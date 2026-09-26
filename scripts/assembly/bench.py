#!/usr/bin/env python3
"""Reproducible, warm-cache, end-to-end assembly experiment (stdlib only)."""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import tarfile
import time

BASE = '3fce3b5bb0236da2df6d99672afb8a719642eca7'
ROOT = Path(__file__).resolve().parents[2]
MODES = ('baseline', 'assembly', 'rust-control', 'disabled')


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def environment(mode):
    env = dict(os.environ)
    for key in ('RIPGREP_CONFIG_PATH', 'RG_ASM', 'RUST_LOG'):
        env.pop(key, None)
    env['LC_ALL'] = 'C.UTF-8'
    if mode == 'rust-control':
        env['RG_ASM'] = 'rust'
    elif mode == 'disabled':
        env['RG_ASM'] = '0'
    return env


def generate(directory):
    directory.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(100_000):
        level = 'ERROR' if i % 997 == 0 else 'WARN' if i % 13 == 0 else 'INFO'
        rows.append(
            f'2026-09-26T00:{i % 60:02}:{i * 7 % 60:02}Z {level} '
            f'request={i:08x} method=GET path=/api/items/{i * 7919 % 100003} '
            f'status={500 if i % 997 == 0 else 200} '
            f'latency={i * 37 % 10000:04}us user={i * 31 % 65536:05} '
            'agent=ripgrep-benchmark\n'
        )
    block = ''.join(rows).encode()
    with (directory / 'logs.txt').open('wb') as f:
        for _ in range(16):
            f.write(block)
    (directory / 'cached-logs.txt').write_bytes((block * 2)[:16 * 1024**2])
    (directory / 'small.txt').write_bytes(block[:4096])
    # Read an immutable upstream snapshot, not the changing experimental files.
    archive = subprocess.check_output(
        ['git', 'archive', BASE, 'crates', 'tests'], cwd=ROOT
    )
    chunks = []
    tree = directory / 'source-tree'
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in sorted(tar.getmembers(), key=lambda m: m.name):
            if not member.isfile() or not member.name.endswith('.rs'):
                continue
            data = tar.extractfile(member).read()
            target = tree / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            chunks.append(data)
    source = b'\n'.join(chunks)
    (directory / 'source.txt').write_bytes(
        (source * (64 * 1024**2 // len(source) + 1))[:64 * 1024**2]
    )
    (directory / 'long-line.txt').write_bytes(b'a' * (16 * 1024**2) + b'TOKEN\n')
    (directory / 'adversarial.txt').write_bytes((b'a' * 63 + b'b') * 16384)
    ordinary = 'café 東京 hello κόσμος café 東京 hello κόσμος\n'.encode()
    special = 'καλημέρα from the test corpus\n'.encode()
    unicode_block = ordinary * 1000 + special
    (directory / 'unicode.txt').write_bytes(unicode_block * 256)
    paths = sorted(p for p in directory.rglob('*') if p.is_file())
    manifest = {
        str(p.relative_to(directory)): {'bytes': p.stat().st_size, 'sha256': digest(p)}
        for p in paths
    }
    return manifest


def cases(directory):
    specs = [
        ('logs-sparse-lines', ['-n', 'ERROR'], 'logs.txt'),
        ('logs-sparse-count', ['-c', 'ERROR'], 'logs.txt'),
        ('logs-dense-count', ['-c', 'INFO'], 'logs.txt'),
        ('logs-short-count', ['-c', 'us'], 'logs.txt'),
        ('logs-absent', ['-c', 'notpresentneedle'], 'logs.txt'),
        ('logs-regex', ['-c', 'status=[45][0-9]{2}'], 'logs.txt'),
        ('cached-sparse-lines', ['-n', 'ERROR'], 'cached-logs.txt'),
        ('source-literal', ['-n', 'Searcher'], 'source.txt'),
        ('source-regex', ['-c', r'fn [a-z_]+\('], 'source.txt'),
        ('source-absent', ['-c', 'notpresentneedle'], 'source.txt'),
        ('source-tree', ['-l', '--sort', 'path', 'Searcher'], 'source-tree'),
        ('small-file', ['-n', 'ERROR'], 'small.txt'),
        ('long-line', ['-o', 'TOKEN'], 'long-line.txt'),
        ('adversarial', ['-c', 'a' * 64], 'adversarial.txt'),
        ('unicode', ['-n', 'καλημέρα'], 'unicode.txt'),
    ]
    return [(name, ['--no-config', '-j1', *args, str(directory / file)])
            for name, args, file in specs]


def summarize(values):
    return {
        'median_ms': statistics.median(values),
        'min_ms': min(values),
        'p10_ms': sorted(values)[int((len(values) - 1) * .1)],
        'p90_ms': sorted(values)[int((len(values) - 1) * .9)],
        'samples_ms': values,
    }


def ratio_interval(baseline, candidate):
    # Resample paired rounds; this measures sampling uncertainty, not systematic
    # bias, CPU variation across hosts or generalization to other workloads.
    rng = random.Random(9821)
    ratios = []
    for _ in range(2000):
        indices = rng.choices(range(len(baseline)), k=len(baseline))
        ratios.append(statistics.median(baseline[i] for i in indices)
                      / statistics.median(candidate[i] for i in indices))
    ratios.sort()
    return [ratios[50], ratios[1949]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'target/assembly-data')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=4)
    parser.add_argument('--samples', type=int, default=30)
    parser.add_argument('--seed', type=int, default=7351)
    parser.add_argument('--reverse-case-order', action='store_true')
    args = parser.parse_args()
    if args.samples < 5:
        parser.error('use at least 5 samples')
    baseline, candidate = args.baseline.resolve(), args.candidate.resolve()
    directory = args.data_dir.resolve()
    manifest = generate(directory)
    os.sched_setaffinity(0, {args.cpu})  # Children inherit affinity: no taskset cost.
    rng = random.Random(args.seed)
    commands = {'baseline': baseline, **{m: candidate for m in MODES[1:]}}
    envs = {mode: environment(mode) for mode in MODES}
    cpu_info = Path('/proc/cpuinfo').read_text()
    results = {
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'base_commit': BASE,
        'platform': platform.platform(),
        'cpu': next(line.split(':', 1)[1].strip() for line in cpu_info.splitlines()
                    if line.startswith('model name')),
        'cpu_flags': next(line.split(':', 1)[1].strip() for line in cpu_info.splitlines()
                          if line.startswith('flags')),
        'affinity_cpu': args.cpu, 'seed': args.seed, 'samples': args.samples,
        'reverse_case_order': args.reverse_case_order,
        'profile': 'release-lto, no RUSTFLAGS; baseline unmodified upstream',
        'rustc': subprocess.check_output(['rustc', '-Vv'], text=True).strip(),
        'method': 'warm cache; 2 warmups/mode; randomized paired rounds; wall time '
                  'includes startup; stdout=/dev/null; mmap/IO chosen by rg defaults',
        'binaries': {mode: {'path': str(path), 'sha256': digest(path),
                           'bytes': path.stat().st_size,
                           'RG_ASM': envs[mode].get('RG_ASM')}
                     for mode, path in commands.items()},
        'input_manifest': manifest,
        'cases': [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    suite = cases(directory)
    if args.reverse_case_order:
        suite.reverse()
    for name, options in suite:
        reference = None
        for mode in MODES:
            output = subprocess.run([str(commands[mode]), *options], env=envs[mode],
                                    capture_output=True, check=False)
            result = (output.returncode, output.stdout, output.stderr)
            if reference is None:
                reference = result
                assert output.returncode in (0, 1), result
            else:
                assert result == reference, (name, mode, 'output mismatch')
            subprocess.run([str(commands[mode]), *options], env=envs[mode],
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
        timings = {mode: [] for mode in MODES}
        for _ in range(args.samples):
            order = list(MODES)
            rng.shuffle(order)
            for mode in order:
                start = time.perf_counter_ns()
                process = subprocess.run([str(commands[mode]), *options], env=envs[mode],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                elapsed = (time.perf_counter_ns() - start) / 1e6
                assert process.returncode == reference[0] and process.stderr == reference[2]
                timings[mode].append(elapsed)
        stats = {mode: summarize(values) for mode, values in timings.items()}
        ratio = stats['baseline']['median_ms'] / stats['assembly']['median_ms']
        interval = ratio_interval(timings['baseline'], timings['assembly'])
        results['cases'].append({
            'name': name, 'arguments': options, 'returncode': reference[0],
            'stdout_sha256': hashlib.sha256(reference[1]).hexdigest(),
            'stats': stats, 'speedup': ratio, 'speedup_ci95': interval,
        })
        args.output.write_text(json.dumps(results, indent=2) + '\n')
        print(f'{name:24} ' + ' '.join(f'{m}={stats[m]["median_ms"]:.3f}' for m in MODES)
              + f' speedup={ratio:.3f} [{interval[0]:.3f}, {interval[1]:.3f}]', flush=True)


if __name__ == '__main__':
    main()
