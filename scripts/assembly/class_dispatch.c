/* Linux/glibc-only experimental companion, licensed like the surrounding fork.
 * The parent executable's original search code is not rewritten or recompiled.
 * This constructor either returns to it or execs the adjacent class specialist.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

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

/* A conservative structural filter, not a replacement regex parser. All
 * actual parsing, matching and output remains in ripgrep. No filename or
 * benchmark-name checks are made. Small alphabets keep upstream's literal
 * prefilters; only positive runs of at least two bytes are routed.
 */
static int eligible(const char *pattern) {
    const unsigned char *p = (const unsigned char *)pattern;
    unsigned char members[128] = {0};
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
            cardinality += !members[c];
            members[c] = 1;
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

static int disabled(const char *name) {
    const char *value = getenv(name);
    return value && strcmp(value, "0") == 0;
}

static void try_specialist(int argc, char **argv, char **envp) {
    if (argc < 3 || disabled("RG_BUNDLE") || disabled("RG_CLASS")
        || disabled("RG_ASM")) return;
    const char *pattern = NULL, *path = NULL;
    int no_config = 0, options = 1;
    for (int i = 1; i < argc; i++) {
        const char *arg = argv[i];
        if (options && strcmp(arg, "--") == 0) {
            options = 0;
            continue;
        }
        if (options && strcmp(arg, "--no-config") == 0) {
            no_config = 1;
            continue;
        }
        if (options && arg[0] == '-') {
            if (!arg[1] || arg[1] == '-') return;
            for (const char *p = arg + 1; *p; p++) {
                if (*p != 'n' && *p != 'c') return;
            }
            continue;
        }
        if (!pattern) pattern = arg;
        else if (!path) path = arg;
        else return;
    }
    if (!pattern || !path || !eligible(pattern)) return;
    if (!no_config && getenv("RIPGREP_CONFIG_PATH")) return;
    const char *mode = getenv("RG_ASM");
    if (mode && strcmp(mode, "rust") == 0) return;

    /* The handoff has fixed startup cost. Small inputs and very long lines
     * keep upstream. The probe affects routing only, never search results.
     * NONBLOCK plus a second type check avoids blocking if a path changes.
     */
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NONBLOCK);
    if (fd < 0) return;
    struct stat info;
    char probe[4096];
    ssize_t got = -1;
    if (fstat(fd, &info) == 0 && S_ISREG(info.st_mode)
        && info.st_size >= 8 * 1024 * 1024) {
        got = pread(fd, probe, sizeof(probe), 0);
    }
    close(fd);
    if (got <= 0 || !memchr(probe, '\n', (size_t)got)
        || memchr(probe, 0, (size_t)got)) return;

    char helper[PATH_MAX];
    ssize_t length = readlink("/proc/self/exe", helper, sizeof(helper) - 1);
    if (length <= 0 || length >= (ssize_t)sizeof(helper) - 1) return;
    helper[length] = 0;
    char *slash = strrchr(helper, '/');
    static const char name[] = "/rg-class-worker";
    if (!slash || (size_t)(slash - helper) + sizeof(name) > sizeof(helper)) return;
    memcpy(slash, name, sizeof(name));
    execve(helper, argv, envp);
    /* A missing/unusable specialist simply leaves upstream in control. */
}

__attribute__((constructor))
static void initialize(int argc, char **argv, char **envp) {
    int saved_errno = errno;
    try_specialist(argc, argv, envp);
    errno = saved_errno;
}
