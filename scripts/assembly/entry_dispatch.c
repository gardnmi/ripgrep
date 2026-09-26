/* Linux x86-64 experimental startup router. No libc, allocation or globals.
 * It applies the same conservative rule as class_dispatch.c, before upstream's
 * entry point, and uses raw syscalls only after a command might qualify.
 * Licensed under the same terms as this fork.
 */
#include <fcntl.h>
#include <asm/unistd.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/stat.h>

_Static_assert(sizeof(void *) == 8 && sizeof(struct stat) == 144
               && offsetof(struct stat, st_mode) == 24
               && offsetof(struct stat, st_size) == 48, "Requires Linux x86-64 stat ABI");

static long syscall4(long number, long a, long b, long c, long d) {
    register long fourth __asm__("r10") = d;
    long result;
    __asm__ volatile("syscall" : "=a"(result)
                     : "a"(number), "D"(a), "S"(b), "d"(c), "r"(fourth)
                     : "rcx", "r11", "memory", "cc");
    return result;
}

static int equal(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return *a == *b;
}

static const char *environment(char **env, const char *name) {
    for (; *env; env++) {
        const char *a = *env, *b = name;
        while (*b && *a == *b) { a++; b++; }
        if (!*b && *a == '=') return a + 1;
    }
    return 0;
}

static int disabled(char **env, const char *name) {
    const char *value = environment(env, name);
    return value && equal(value, "0");
}

static int endpoint(unsigned char c) {
    return c >= 33 && c < 127 && c != '[' && c != ']' && c != '\\'
        && c != '^' && c != '-' && c != '&' && c != '~';
}

static int number(const unsigned char **cursor, uint32_t *value) {
    const unsigned char *p = *cursor;
    uint64_t n = 0;
    if (*p < '0' || *p > '9') return 0;
    do {
        n = n * 10 + (*p++ - '0');
        if (n > UINT32_MAX) return 0;
    } while (*p >= '0' && *p <= '9');
    *cursor = p;
    *value = (uint32_t)n;
    return 1;
}

static int eligible(const char *pattern) {
    const unsigned char *p = (const unsigned char *)pattern;
    uint64_t members[2] = {0, 0};
    unsigned ranges = 0, cardinality = 0;
    if (*p++ != '[') return 0;
    while (*p && *p != ']') {
        unsigned lo = *p;
        if (!endpoint((unsigned char)lo)) return 0;
        p++;
        unsigned hi = lo;
        if (*p == '-') {
            p++;
            hi = *p;
            if (!endpoint((unsigned char)hi) || hi < lo) return 0;
            p++;
        }
        if (++ranges > 4) return 0;
        for (unsigned c = lo; c <= hi; c++) {
            uint64_t bit = UINT64_C(1) << (c & 63);
            cardinality += !(members[c >> 6] & bit);
            members[c >> 6] |= bit;
        }
    }
    if (*p != ']' || cardinality < 8) return 0;
    p++;
    if (*p++ != '{') return 0;
    uint32_t minimum, maximum;
    if (!number(&p, &minimum) || minimum < 2) return 0;
    if (*p == ',') {
        p++;
        if (*p != '}' && (!number(&p, &maximum) || maximum < minimum)) return 0;
    }
    if (*p != '}') return 0;
    p++;
    if (*p == '?') p++;
    return *p == 0;
}

/* Keep the large stack buffer out of the ordinary fallback path. */
__attribute__((noinline))
static void try_file(const char *path, char **argv, char **envp) {
    struct stat info;
    if (syscall4(__NR_stat, (long)path, (long)&info, 0, 0) != 0
        || !S_ISREG(info.st_mode) || info.st_size < 8 * 1024 * 1024) return;
    long fd = syscall4(__NR_open, (long)path, O_RDONLY | O_CLOEXEC | O_NONBLOCK, 0, 0);
    if (fd < 0) return;
    char buffer[4096];
    long got = -1;
    if (syscall4(__NR_fstat, fd, (long)&info, 0, 0) == 0
        && S_ISREG(info.st_mode) && info.st_size >= 8 * 1024 * 1024) {
        got = syscall4(__NR_pread64, fd, (long)buffer, sizeof(buffer), 0);
    }
    syscall4(__NR_close, fd, 0, 0, 0);
    if (got <= 0) return;
    int newline = 0;
    for (long i = 0; i < got; i++) {
        if (!buffer[i]) return;
        newline |= buffer[i] == '\n';
    }
    if (!newline) return;
    long length = syscall4(__NR_readlink, (long)"/proc/self/exe", (long)buffer, sizeof(buffer)-1, 0);
    if (length <= 0 || length >= (long)sizeof(buffer)-1) return;
    buffer[length] = 0;
    long slash = length;
    while (slash >= 0 && buffer[slash] != '/') slash--;
    static const char name[] = "/rg-class-worker";
    if (slash < 0 || slash + sizeof(name) > sizeof(buffer)) return;
    for (unsigned i = 0; i < sizeof(name); i++) buffer[slash+i] = name[i];
    syscall4(__NR_execve, (long)buffer, (long)argv, (long)envp, 0);
    /* Failure falls through with the original startup stack unchanged. */
}

void rg_route(int argc, char **argv, char **envp) {
    if (argc < 3) return;
    const char *pattern = 0, *path = 0;
    int no_config = 0, options = 1;
    for (int i = 1; i < argc; i++) {
        const char *arg = argv[i];
        if (options && equal(arg, "--")) { options = 0; continue; }
        if (options && equal(arg, "--no-config")) { no_config = 1; continue; }
        if (options && arg[0] == '-') {
            if (!arg[1] || arg[1] == '-') return;
            for (const char *p = arg+1; *p; p++) if (*p != 'n' && *p != 'c') return;
            continue;
        }
        if (!pattern) pattern = arg;
        else if (!path) path = arg;
        else return;
    }
    if (!pattern || !path || !eligible(pattern)) return;
    /* An extra exec must not duplicate loader diagnostics or constructor side
     * effects. Keep loader-injected processes in their original executable. */
    if (environment(envp,"LD_PRELOAD") || environment(envp,"LD_AUDIT")) return;
    if (disabled(envp,"RG_BUNDLE") || disabled(envp,"RG_CLASS")
        || disabled(envp,"RG_ASM")) return;
    if (!no_config && environment(envp,"RIPGREP_CONFIG_PATH")) return;
    const char *mode = environment(envp,"RG_ASM");
    if (mode && equal(mode,"rust")) return;
    try_file(path,argv,envp);
}
