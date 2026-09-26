#!/usr/bin/env python3
"""Run ripgrep's seven README workloads against the same upstream/candidate builds."""
import argparse
import ctypes
import datetime
import hashlib
import json
import mmap
import os
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import tempfile
import time

from bench import BASE, ROOT, digest, environment, ratio_interval, summarize

URL = 'https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/mono/en.txt.gz'
KERNEL = '84e57d292203a45c96dbcb2e6be9dd80961d981a'
MODES = ('baseline', 'assembly', 'rust-control')


def residency(path):
    """Read mincore residency without faulting in the file's pages (Linux only)."""
    size = path.stat().st_size
    pages = (size + mmap.PAGESIZE - 1) // mmap.PAGESIZE
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                          ctypes.c_int, ctypes.c_int, ctypes.c_long]
    libc.mmap.restype = ctypes.c_void_p
    libc.mincore.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p]
    libc.munmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    with path.open('rb') as f:
        ptr = libc.mmap(None, size, mmap.PROT_READ, mmap.MAP_PRIVATE, f.fileno(), 0)
        if ptr == ctypes.c_void_p(-1).value:
            raise OSError(ctypes.get_errno(), 'mmap failed')
        try:
            vec = (ctypes.c_ubyte * pages)()
            if libc.mincore(ptr, size, vec):
                raise OSError(ctypes.get_errno(), 'mincore failed')
            resident = sum(value & 1 for value in bytes(vec))
            return {'resident_pages': resident, 'total_pages': pages,
                    'fraction': resident / pages}
        finally:
            libc.munmap(ptr, size)


def verify(command, cwd, env, unordered):
    # The `the` case prints gigabytes. Stream it; never capture it all in RAM.
    with tempfile.TemporaryFile() as err:
        proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=err)
        sha = hashlib.sha256()
        lines = size = 0
        if unordered:
            # Kernel directory output is small, but parallel traversal order varies.
            data = proc.stdout.read()
            lines, size = data.count(b'\n'), len(data)
            sha.update(b''.join(sorted(data.splitlines(keepends=True))))
        else:
            while chunk := proc.stdout.read(1024**2):
                lines += chunk.count(b'\n')
                size += len(chunk)
                sha.update(chunk)
        code = proc.wait()
        err.seek(0)
        stderr = err.read()
    assert code == 0 and not stderr, (command, code, stderr)
    return {'exit_code': code, 'lines': lines, 'output_bytes': size,
            'stdout_sha256': sha.hexdigest(), 'order_normalized': unordered}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--corpus', type=Path, default=ROOT / 'target/assembly-readme')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=7)
    parser.add_argument('--slow-samples', type=int, default=5)
    parser.add_argument('--cpu', type=int, default=4)
    parser.add_argument('--seed', type=int, default=62184)
    parser.add_argument('--allow-disk-io', action='store_true',
                        help='Diagnostic runs only: do not require cached subtitle data')
    parser.add_argument('--resume', action='store_true', help='Keep every recorded sample and complete an interrupted output file')
    parser.add_argument('--case', action='append', help='Optional named case filter')
    args = parser.parse_args()
    if min(args.samples, args.slow_samples) < 5:
        parser.error('use at least five samples')
    corpus = args.corpus.resolve()
    linux, subtitles = corpus / 'linux', corpus / 'en.txt'
    group = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split(':')[-1].lstrip('/')
    limits = {name: (group / name).read_text().strip()
              for name in ('memory.max', 'memory.swap.max', 'memory.oom.group')}
    if (limits['memory.max'] == 'max' or int(limits['memory.max']) > 16 * 1024**3
            or limits['memory.swap.max'] != '0' or limits['memory.oom.group'] != '1'):
        raise RuntimeError('Use a dedicated systemd scope with MemoryMax=16G, MemorySwapMax=0, OOMPolicy=kill')
    fs_type = subprocess.check_output(['findmnt', '-n', '-o', 'FSTYPE', '-T', str(subtitles)], text=True).strip()
    if fs_type in ('tmpfs', 'ramfs'):
        raise RuntimeError('Keep the corpus on disk; do not fill desktop shared-memory storage')
    meminfo = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    available = int(meminfo['MemAvailable'].split()[0]) * 1024
    if available < subtitles.stat().st_size + 4 * 1024**3:
        raise RuntimeError('Insufficient memory headroom for this full cached-file benchmark')
    assert (linux / 'vmlinux').is_file(), 'build the kernel first'
    assert subtitles.is_file(), 'download and decompress the complete v2018 corpus first'
    kernel_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=linux, text=True).strip()
    assert kernel_sha == KERNEL, ('unexpected kernel revision', kernel_sha)
    assert not subprocess.check_output(['git', 'diff', 'HEAD'], cwd=linux)
    bins = {'baseline': args.baseline.resolve(),
            **{mode: args.candidate.resolve() for mode in MODES[1:]}}
    envs = {mode: environment(mode) for mode in MODES}
    rng = random.Random(args.seed)
    original_affinity = os.sched_getaffinity(0)
    specs = [
        ('linux-default', linux, ['-n', '-w', '[A-Z]+_SUSPEND'], 536, False),
        ('linux-c-types', linux, ['-uuu', '-tc', '-n', '-w', '[A-Z]+_SUSPEND'], 447, False),
        ('subtitles-sherlock', subtitles.parent, ['-w', r'Sherlock [A-Z]\w+', subtitles.name], 7882, False),
        ('subtitles-sherlock-lines', subtitles.parent, ['-n', '-w', r'Sherlock [A-Z]\w+', subtitles.name], 7882, False),
        ('subtitles-surrounding', subtitles.parent, ['-w', r'[A-Z]\w+ Sherlock [A-Z]\w+', subtitles.name], 485, False),
        ('subtitles-no-literal', subtitles.parent, ['[A-Za-z]{30}', subtitles.name], 6749, True),
        ('subtitles-frequent', subtitles.parent, ['the', subtitles.name], 83499915, True),
    ]
    cpu_info = Path('/proc/cpuinfo').read_text()
    results = {
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'base_commit': BASE,
        'fetched_upstream_master': subprocess.check_output(
            ['git', 'rev-parse', 'upstream/master'], cwd=ROOT, text=True).strip(),
        'upstream_verification': json.loads((corpus / 'provenance.json').read_text())
            if (corpus / 'provenance.json').exists() else None,
        'candidate_source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'readme': f'https://github.com/BurntSushi/ripgrep/blob/{BASE}/README.md#quick-examples-comparing-tools',
        'platform': platform.platform(),
        'cpu': next(line.split(':', 1)[1].strip() for line in cpu_info.splitlines()
                    if line.startswith('model name')),
        'single_file_affinity': [args.cpu], 'directory_affinity': sorted(original_affinity),
        'seed': args.seed,
        'cgroup': str(group), 'memory_limits': limits, 'corpus_filesystem': fs_type,
        'require_cached_subtitles': not args.allow_disk_io,
        'method': 'README arguments plus --no-config; default thread selection; warm cache; '
                  'one explicit warmup after output verification; randomized paired rounds; '
                  'wall time includes startup and IO; timed output=/dev/null; '
                  'directory output sorted only for untimed correctness comparison; '
                  'subtitle source mmap held open and pages touched before every timed process; '
                  'MADV_DONTFORK avoids inheriting the warmup mapping into child processes',
        'kernel': {'revision': kernel_sha, 'config_sha256': digest(linux / '.config'),
                   'vmlinux_bytes': (linux / 'vmlinux').stat().st_size,
                   'build': "make defconfig; make -j8 CC='gcc -std=gnu11' HOSTCC='gcc -std=gnu11' KCFLAGS=-Wno-error",
                   'compiler': subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0]},
        'subtitles': {'url': URL, 'path': str(subtitles),
                      'bytes': subtitles.stat().st_size, 'sha256': digest(subtitles)},
        'binaries': {mode: {'path': str(path), 'sha256': digest(path),
                           'bytes': path.stat().st_size, 'RG_ASM': envs[mode].get('RG_ASM')}
                     for mode, path in bins.items()},
        'meminfo_before': Path('/proc/meminfo').read_text(),
        'cases': [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    prior_cases = {}
    if args.resume:
        previous = json.loads(args.output.read_text())
        assert previous['subtitles']['sha256'] == results['subtitles']['sha256']
        assert previous['kernel'] == results['kernel']
        assert previous['seed'] == args.seed
        assert previous['single_file_affinity'] == results['single_file_affinity']
        for mode in MODES:
            assert previous['binaries'][mode]['sha256'] == results['binaries'][mode]['sha256']
        prior_cases = {c['name']: c for c in previous['cases']}
        if args.case and not set(prior_cases).issubset(args.case):
            parser.error('--resume must retain every previously recorded case')
        if any(name.startswith('linux-') for name in prior_cases):
            assert previous['directory_affinity'] == results['directory_affinity']
        if not args.allow_disk_io:
            for name, case in prior_cases.items():
                if name.startswith('subtitles-') and any(
                    sample['major_faults'] or sample['input_blocks']
                    for samples in case['resources'].values() for sample in samples
                ):
                    parser.error('recorded storage IO requires --allow-disk-io to resume')
        results['resumed_from_utc'] = previous['recorded_utc']
        results['resume_note'] = 'All prior samples retained, including IO-affected samples; output verification reused after rechecking input and binary hashes.'

    def save():
        args.output.write_text(json.dumps(results, indent=2) + '\n')

    cache_mapping = None
    for name, cwd, options, expected_lines, slow in specs:
        if args.case and name not in args.case:
            continue
        directory = name.startswith('linux-')
        os.sched_setaffinity(0, original_affinity if directory else {args.cpu})
        if not directory and cache_mapping is None:
            # Keep a mapping of the original disk file open. These are shared
            # page-cache pages, not another 13 GB allocation or tmpfs copy.
            with subtitles.open('rb') as source:
                cache_mapping = mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ)
            cache_mapping.madvise(mmap.MADV_RANDOM)
            cache_mapping.madvise(mmap.MADV_DONTFORK)
            cache_mapping[::mmap.PAGESIZE]
        commands = {m: [str(bins[m]), '--no-config', *options] for m in MODES}
        prior = prior_cases.get(name)
        if prior is None:
            print(f'{name}: verifying output', flush=True)
            verification = {m: verify(commands[m], cwd, envs[m], directory) for m in MODES}
            assert all(v == verification['baseline'] for v in verification.values()), verification
        else:
            assert prior['arguments'] == ['--no-config', *options]
            verification = prior['verification']
            print(f'{name}: resuming recorded samples', flush=True)
        print(f'{name}: {verification["baseline"]["lines"]:,} lines '
              f'(README {expected_lines:,})', flush=True)
        if prior is None:
            for mode in MODES:
                proc = subprocess.run(commands[mode], cwd=cwd, env=envs[mode], stdin=subprocess.DEVNULL,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                assert proc.returncode == 0 and not proc.stderr
        if not directory:
            cache_mapping[::mmap.PAGESIZE]
        samples = args.slow_samples if slow else args.samples
        timings = {mode: [] for mode in MODES}
        resources = {mode: [] for mode in MODES}
        entry = {'name': name, 'cwd': str(cwd), 'arguments': ['--no-config', *options],
                 'expected_readme_lines': expected_lines, 'verification': verification,
                 'matches_readme_count': verification['baseline']['lines'] == expected_lines,
                 'affinity': sorted(os.sched_getaffinity(0)), 'samples': samples,
                 'residency_before': None if directory else residency(subtitles),
                 'resources': resources}
        if prior is not None:
            assert prior['samples'] == samples
            entry = prior
            timings = {m: list(prior['stats'].get(m, {}).get('samples_ms', [])) for m in MODES}
            resources = entry['resources']
            entry['residency_at_resume'] = None if directory else residency(subtitles)
        results['cases'].append(entry)
        if not directory and not args.allow_disk_io:
            save()
            current_residency = entry.get('residency_at_resume', entry['residency_before'])
            if current_residency['fraction'] < 0.999:
                raise RuntimeError('Subtitle data is not cached; cached-file benchmarking cannot proceed')
        for round_number in range(samples):
            order = list(MODES)
            rng.shuffle(order)
            for mode in order:
                if len(timings[mode]) > round_number:
                    continue
                if not directory:
                    # A strided slice touches every source page but allocates
                    # only one byte per page (~3.2 MB for this full corpus).
                    cache_mapping[::mmap.PAGESIZE]
                usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
                start = time.perf_counter_ns()
                proc = subprocess.run(commands[mode], cwd=cwd, env=envs[mode], stdin=subprocess.DEVNULL,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                elapsed = (time.perf_counter_ns() - start) / 1e6
                usage = resource.getrusage(resource.RUSAGE_CHILDREN)
                assert proc.returncode == 0 and not proc.stderr
                timings[mode].append(elapsed)
                resources[mode].append({
                    'major_faults': usage.ru_majflt - usage_before.ru_majflt,
                    'user_seconds': usage.ru_utime - usage_before.ru_utime,
                    'system_seconds': usage.ru_stime - usage_before.ru_stime,
                    'input_blocks': usage.ru_inblock - usage_before.ru_inblock,
                    'involuntary_context_switches': usage.ru_nivcsw - usage_before.ru_nivcsw,
                })
                if not directory and not args.allow_disk_io:
                    if resources[mode][-1]['major_faults'] or resources[mode][-1]['input_blocks']:
                        entry['stats'] = {m: summarize(v) for m, v in timings.items() if v}
                        save()
                        raise RuntimeError('Storage IO or major faults invalidated cached-file timing')
            entry['stats'] = {m: summarize(v) for m, v in timings.items()}
            save()
            print(f'{name}: round {round_number+1}/{samples} ' +
                  ', '.join(f'{m}={timings[m][round_number]/1000:.3f}s' for m in MODES), flush=True)
        entry['residency_after'] = None if directory else residency(subtitles)
        # Pages can be reclaimed after their last read. Record end residency,
        # but judge cached timing by the measured processes' faults and IO.
        entry['speedup'] = statistics.median(timings['baseline']) / statistics.median(timings['assembly'])
        entry['speedup_ci95'] = ratio_interval(timings['baseline'], timings['assembly'])
        save()
        print(f'{name}: speedup {entry["speedup"]:.3f}x', flush=True)
    results['meminfo_after'] = Path('/proc/meminfo').read_text()
    results['memory_peak_bytes'] = int((group / 'memory.peak').read_text())
    results['memory_events'] = (group / 'memory.events').read_text()
    results['memory_swap_bytes_after'] = int((group / 'memory.swap.current').read_text())
    results['status'] = 'complete'
    save()
    if cache_mapping is not None:
        cache_mapping.close()


if __name__ == '__main__':
    main()
