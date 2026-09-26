#!/usr/bin/env python3
"""Diagnostic thread/allocator/build comparison; not an acceptance run."""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import random
import resource
import statistics
import subprocess
import time

from audit_bench import comparison, verify
from audit_isolation import external_work
from bench import ROOT, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    env = {k: v for k, v in os.environ.items()
           if not k.startswith('RG_') and k not in ('RIPGREP_CONFIG_PATH', 'RUST_LOG', 'LD_PRELOAD')}
    env['LC_ALL'] = 'C.UTF-8'
    modes = {
        'baseline-a': ('/usr/bin/rg', [], {}),
        'baseline-b': ('/usr/bin/rg', [], {}),
        'six-threads': ('/usr/bin/rg', ['-j6'], {}),
        'one-thread': ('/usr/bin/rg', ['-j1'], {}),
        'jemalloc': ('/usr/bin/rg', [], {'LD_PRELOAD': '/usr/lib/libjemalloc.so.2'}),
        'native-existing': (str(args.native), [], {}),
    }
    selected = {'source-literal', 'source-absent', 'source-files',
                'tools-literal', 'tools-files', 'kernel-literal', 'kernel-files',
                'tiny-hit', 'log-lines', 'prose-absent'}
    manifest = json.loads(args.manifest.read_text())
    cases = [c for c in manifest['cases'] if c['name'] in selected]
    result = dict(purpose='Discovery only; native-existing also differs in PCRE2 support.',
                  recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  manifest_sha256=digest(args.manifest), modes=modes, samples=9, seed=260928,
                  hashes={p: digest(Path(p)) for p in [*{m[0] for m in modes.values()},
                                                     '/usr/lib/libjemalloc.so.2']},
                  cases=[], status='running')
    rng = random.Random(result['seed'])

    def save():
        args.output.write_text(json.dumps(result, indent=2) + '\n')

    def quiet():
        jobs = external_work([Path.home() / 'Projects/ttfx', Path.home() / 'Worktrees/ttfx'])
        if jobs:
            result.update(status='interrupted-external-work', interference=jobs)
            save()
            raise SystemExit('Competing work detected; partial samples retained.')

    quiet()
    for case in cases:
        os.sched_setaffinity(0, set(case['affinity']))
        commands = {m: [binary, *flags, *case['arguments']]
                    for m, (binary, flags, _) in modes.items()}
        environments = {m: {**env, **changes} for m, (_, _, changes) in modes.items()}
        verified = {m: verify(cmd, environments[m], case) for m, cmd in commands.items()}
        assert all(v == verified['baseline-a'] for v in verified.values()), case['name']
        entry = dict(name=case['name'], verification=verified, commands=commands,
                     timings_ms={m: [] for m in modes}, resources={m: [] for m in modes}, order=[])
        result['cases'].append(entry)

        def batch(mode, repeats):
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            total = 0
            for _ in range(repeats):
                start = time.perf_counter_ns()
                cp = subprocess.run(commands[mode], env=environments[mode], cwd=ROOT,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120)
                total += (time.perf_counter_ns() - start) / 1e6
                assert cp.returncode == verified[mode]['exit'] and cp.stderr.hex() == verified[mode]['stderr_hex']
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            return total / repeats, dict(major_faults=after.ru_majflt-before.ru_majflt,
                                         input_blocks=after.ru_inblock-before.ru_inblock,
                                         cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime)

        for mode in modes:
            batch(mode, 1)
        pilot = statistics.median(batch('baseline-a', 1)[0] for _ in range(3))
        repeats = min(25, max(1, math.ceil(50 / pilot)))
        entry['repetitions'] = repeats
        for _ in range(result['samples']):
            quiet()
            order = list(modes)
            rng.shuffle(order)
            entry['order'].append(order)
            for mode in order:
                elapsed, counters = batch(mode, repeats)
                entry['timings_ms'][mode].append(elapsed)
                entry['resources'][mode].append(counters)
            save()
        t = entry['timings_ms']
        baseline = [(a + b) / 2 for a, b in zip(t['baseline-a'], t['baseline-b'])]
        entry['comparisons'] = {m: comparison(baseline, t[m]) for m in modes if not m.startswith('baseline')}
        entry['controls'] = comparison(t['baseline-a'], t['baseline-b'])
        save()
        print(case['name'], {m: round(c['elapsed_ratio'], 3) for m, c in entry['comparisons'].items()}, flush=True)
    result['status'] = 'complete'
    save()


if __name__ == '__main__':
    main()
