#!/usr/bin/env python3
"""Interleaved Zen 4 experiments with equal CPU budgets and bounded memory."""
import argparse
import datetime
import json
import mmap
import os
from pathlib import Path
import random
import resource
import statistics
import subprocess
import time

from bench import ROOT, digest, ratio_interval, summarize
from readme_bench import residency, verify


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--samples', type=int, default=7)
    p.add_argument('--seed', type=int, default=754319)
    p.add_argument('--mode', action='append')
    p.add_argument('--case', action='append')
    p.add_argument('--full', action='store_true')
    a = p.parse_args()
    assert a.samples >= 3
    group = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split(':')[-1].lstrip('/')
    limits = {k: (group/k).read_text().strip() for k in ('memory.max', 'memory.swap.max', 'memory.oom.group')}
    assert limits['memory.max'] != 'max' and int(limits['memory.max']) <= 16*1024**3
    assert limits['memory.swap.max'] == '0' and limits['memory.oom.group'] == '1'
    os.sched_setaffinity(0, {0, 1, 2, 3, 4, 5})
    base = ROOT / 'target/machine'
    env = {k: v for k, v in os.environ.items() if not k.startswith('RG_') and k != 'RIPGREP_CONFIG_PATH'}
    env['LC_ALL'] = 'C.UTF-8'
    spec = {
        'upstream-native': ('rg-upstream-native', {}),
        'upstream-pgo': ('rg-upstream-pgo', {}),
        'asm-control': ('rg-candidate-native', {'RG_CLASS': '0'}),
        'class': ('rg-candidate-native', {}),
        'class-pgo': ('rg-candidate-pgo', {}),
        'fused': ('rg-candidate-native', {'RG_CLASS': '0', 'RG_FUSED': '1'}),
        'parallel2': ('rg-candidate-native', {'RG_CLASS': '0', 'RG_PARALLEL': '2'}),
        'parallel4': ('rg-candidate-native', {'RG_CLASS': '0', 'RG_PARALLEL': '4'}),
        'parallel6': ('rg-candidate-native', {'RG_CLASS': '0', 'RG_PARALLEL': '6'}),
        'combined6': ('rg-candidate-native', {'RG_PARALLEL': '6'}),
    }
    modes = a.mode or list(spec)
    assert 'upstream-native' in modes
    subtitle = ROOT/'target/assembly-readme/en.txt' if a.full else base/'heldout.txt'
    cases = [
        ('alpha30', subtitle, ['[A-Za-z]{30}']),
        ('hex17', subtitle, ['[A-Fa-f0-9]{17}']),
        ('digits8', subtitle, ['[0-9]{8}']),
        ('sherlock', subtitle, ['-w', r'Sherlock [A-Z]\w+']),
        ('sherlock-lines', subtitle, ['-n', '-w', r'Sherlock [A-Z]\w+']),
        ('frequent', subtitle, ['the']),
        ('literal-lines', subtitle, ['-n', 'Sherlock']),
        ('logs-lines', ROOT/'target/assembly-data/logs.txt', ['-n', 'ERROR']),
        ('logs-dense', ROOT/'target/assembly-data/logs.txt', ['-n', 'INFO']),
        ('alpha30-second', base/'heldout2.txt', ['[A-Za-z]{30}']),
    ]
    if a.case:
        assert set(a.case) <= {c[0] for c in cases}
        cases = [c for c in cases if c[0] in a.case]
    inputs = {str(path): path for _, path, _ in cases}
    for path in inputs.values():
        fs = subprocess.check_output(['findmnt', '-n', '-o', 'FSTYPE', '-T', str(path)], text=True).strip()
        assert fs not in ('tmpfs', 'ramfs')
    available = int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))) * 1024
    assert available >= max(p.stat().st_size for p in inputs.values()) + 4*1024**3
    results = {
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'base_commit': subprocess.check_output(['git','rev-parse','upstream/master'],cwd=ROOT,text=True).strip(),
        'candidate_parent': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'cpu': next(l.split(':',1)[1].strip() for l in Path('/proc/cpuinfo').read_text().splitlines() if l.startswith('model name')),
        'affinity_all_modes': sorted(os.sched_getaffinity(0)), 'seed': a.seed,
        'memory_limits': limits, 'full_subtitle_file': a.full,
        'method': 'Exact output verification; one untimed command warmup; disk-backed mmap pages touched before every trial; randomized interleaved rounds; output=/dev/null; per-child resource counters. IO-affected samples are retained and labeled.',
        'inputs': {name: {'bytes': path.stat().st_size, 'sha256': digest(path)} for name,path in inputs.items()},
        'binaries': {m: {'path': str(base/spec[m][0]), 'sha256': digest(base/spec[m][0]), 'environment': spec[m][1]} for m in modes},
        'cases': [],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    def save(): a.output.write_text(json.dumps(results, indent=2)+'\n')
    rng = random.Random(a.seed)
    for name, path, options in cases:
        commands = {m: [str(base/spec[m][0]), '--no-config', *options, str(path)] for m in modes}
        envs = {m: env | spec[m][1] for m in modes}
        print(name, 'verifying', flush=True)
        correctness = {m: verify(commands[m], ROOT, envs[m], False) for m in modes}
        assert all(v == correctness['upstream-native'] for v in correctness.values())
        with path.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mapping:
            mapping.madvise(mmap.MADV_DONTFORK)
            mapping.madvise(mmap.MADV_RANDOM)
            for m in modes:
                cp = subprocess.run(commands[m], env=envs[m], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                assert cp.returncode == 0 and not cp.stderr
            entry = {'name': name, 'arguments': options+[str(path)], 'verification': correctness,
                     'timings_ms': {m: [] for m in modes}, 'resources': {m: [] for m in modes}}
            results['cases'].append(entry)
            for iteration in range(a.samples):
                order = list(modes); rng.shuffle(order)
                for m in order:
                    mapping[::mmap.PAGESIZE]
                    before = resource.getrusage(resource.RUSAGE_CHILDREN)
                    start = time.perf_counter_ns()
                    cp = subprocess.run(commands[m], env=envs[m], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    elapsed = (time.perf_counter_ns()-start)/1e6
                    after = resource.getrusage(resource.RUSAGE_CHILDREN)
                    assert cp.returncode == 0 and not cp.stderr
                    entry['timings_ms'][m].append(elapsed)
                    entry['resources'][m].append({'major_faults': after.ru_majflt-before.ru_majflt,
                        'input_blocks': after.ru_inblock-before.ru_inblock, 'user_seconds': after.ru_utime-before.ru_utime,
                        'system_seconds': after.ru_stime-before.ru_stime})
                save()
            entry['residency_after'] = residency(path)
        entry['stats'] = {m: summarize(t) for m,t in entry['timings_ms'].items()}
        entry['speedups'] = {m: {'ratio': statistics.median(entry['timings_ms']['upstream-native'])/statistics.median(entry['timings_ms'][m]),
                               'ci95': ratio_interval(entry['timings_ms']['upstream-native'],entry['timings_ms'][m])} for m in modes}
        save()
        print(name, {m: round(s['ratio'],3) for m,s in entry['speedups'].items()}, flush=True)
    results['memory_events'] = (group/'memory.events').read_text()
    results['memory_peak_bytes'] = int((group/'memory.peak').read_text())
    results['status'] = 'complete'; save()


if __name__ == '__main__': main()
