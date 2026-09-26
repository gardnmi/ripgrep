#!/usr/bin/env python3
"""Paired regression audit. Keep every observation, including bad/noisy ones."""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import random
import resource
import statistics as stats
import subprocess
import time

from bench import ROOT, digest
from machine_check import normalize_json


def interval(xs):
    xs = sorted(xs)
    return [xs[int(len(xs)*0.025)], xs[int(len(xs)*0.975)]]


def comparison(reference, candidate):
    """Resample round indices jointly, retaining the paired experiment."""
    rng = random.Random(81631)
    ratios, deltas = [], []
    for _ in range(4000):
        ix = rng.choices(range(len(reference)), k=len(reference))
        b = stats.median(reference[i] for i in ix)
        c = stats.median(candidate[i] for i in ix)
        ratios.append(c/b)
        deltas.append(c-b)
    ratio_ci, delta_ci = interval(ratios), interval(deltas)
    verdict = ('FAIL' if ratio_ci[0] > 1.03 and delta_ci[0] > 0.10 else
               'PASS' if ratio_ci[1] <= 1.03 or delta_ci[1] <= 0.10 else
               'INCONCLUSIVE')
    return {'baseline_ms': stats.median(reference),
            'candidate_ms': stats.median(candidate),
            'elapsed_ratio': stats.median(candidate)/stats.median(reference),
            'delta_ms': stats.median(candidate)-stats.median(reference),
            'ratio_ci95': ratio_ci, 'delta_ci95_ms': delta_ci,
            'verdict': verdict}


def verify(command, env, case):
    with subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as proc:
        hasher = hashlib.sha256()
        count = 0
        if case['directory'] or case['json_output']:
            output, errors = proc.communicate(timeout=120)
            if case['json_output']:
                output = json.dumps(normalize_json(output), sort_keys=True).encode()
            else:
                output = b'\n'.join(sorted(output.splitlines()))
            hasher.update(output)
            count = len(output)
        else:
            while block := proc.stdout.read(1024*1024):
                hasher.update(block)
                count += len(block)
            errors = proc.stderr.read()
            proc.wait(timeout=120)
        assert proc.returncode in (0, 1), (command, proc.returncode, errors[:500])
        return {'exit': proc.returncode, 'stdout_sha256': hasher.hexdigest(),
                'normalized_bytes': count, 'stderr_hex': errors.hex()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, default=ROOT/'benchmarks/assembly/audit/manifest.json')
    p.add_argument('--protocol', type=Path, default=ROOT/'benchmarks/assembly/audit/PLAN.md')
    p.add_argument('--baseline', type=Path, default=ROOT/'target/machine/rg-upstream-native')
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--diagnostic', type=Path)
    p.add_argument('--reference', type=Path, help='Additional baseline the candidate must also pass.')
    p.add_argument('--artifact', type=Path, action='append', default=[], help='Hash and freeze companion binaries/libraries.')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--samples', type=int, default=9)
    p.add_argument('--seed', type=int, default=916253)
    p.add_argument('--reverse', action='store_true')
    p.add_argument('--case', action='append', help='Diagnostic subset only; never a full audit.')
    args = p.parse_args()
    assert args.samples >= 9
    group = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split(':')[-1].lstrip('/')
    limits = {k: (group/k).read_text().strip() for k in ('memory.max', 'memory.swap.max', 'memory.oom.group')}
    assert limits['memory.max'] != 'max' and int(limits['memory.max']) <= 8*1024**3
    assert limits['memory.swap.max'] == '0' and limits['memory.oom.group'] == '1'
    env = {k: v for k, v in os.environ.items()
           if not k.startswith('RG_') and k not in ('RIPGREP_CONFIG_PATH', 'RUST_LOG')}
    env['LC_ALL'] = 'C.UTF-8'
    modes = {'baseline-a': args.baseline.resolve(), 'baseline-b': args.baseline.resolve(),
             'candidate': args.candidate.resolve()}
    if args.diagnostic:
        modes['diagnostic'] = args.diagnostic.resolve()
    if args.reference:
        modes['reference'] = args.reference.resolve()
    manifest = json.loads(args.manifest.read_text())
    for file, expected in manifest['inputs'].items():
        assert digest(Path(file)) == expected['sha256'], file
        fs = subprocess.check_output(['findmnt', '-n', '-o', 'FSTYPE', '-T', file], text=True).strip()
        assert fs not in ('tmpfs', 'ramfs'), file
    cases = manifest['cases']
    if args.case:
        assert set(args.case) <= {c['name'] for c in cases}
        cases = [c for c in cases if c['name'] in args.case]
    if args.reverse:
        cases = list(reversed(cases))
    result = {
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'manifest_sha256': digest(args.manifest),
        'protocol_sha256': digest(args.protocol),
        'runner_sha256': digest(Path(__file__)),
        'candidate_parent': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'working_diff_sha256': hashlib.sha256(subprocess.check_output(['git','diff'],cwd=ROOT)).hexdigest(),
        'compiler': subprocess.check_output(['rustc','-Vv'],text=True),
        'cpu': next(l.split(':',1)[1].strip() for l in Path('/proc/cpuinfo').read_text().splitlines() if l.startswith('model name')),
        'kernel': os.uname().release, 'seed': args.seed, 'reverse': args.reverse,
        'samples': args.samples, 'subset': args.case, 'memory_limits': limits,
        'binaries': {m: {'path':str(binary), 'sha256':digest(binary)} for m,binary in modes.items()},
        'artifacts': {str(path.resolve()):digest(path) for path in args.artifact},
        'control_rule': 'Inconclusive when either paired baseline-versus-baseline comparison FAILs; all intervals retained.',
        'cases': [], 'status': 'running',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    def save():
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    rng = random.Random(args.seed)
    for index, case in enumerate(cases):
        print(f"{index+1}/{len(cases)} {case['name']} verifying", flush=True)
        os.sched_setaffinity(0, set(case['affinity']))
        commands = {m: [str(binary), *case['arguments']] for m,binary in modes.items()}
        correctness = {m: verify(cmd, env, case) for m,cmd in commands.items()}
        assert all(v == correctness['baseline-a'] for v in correctness.values()), (case, correctness)
        path = Path(case['path'])

        def warm():
            if not case['directory']:
                with path.open('rb') as f:
                    while f.read(1024*1024):
                        pass

        def evict():
            assert path.name == 'cold.txt' and not case['directory']
            with path.open('rb') as f:
                os.fsync(f.fileno())
                os.posix_fadvise(f.fileno(), 0, 0, os.POSIX_FADV_DONTNEED)

        def batch(mode, repeats):
            if case['cache'] == 'warm':
                warm()
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            elapsed = 0
            for _ in range(repeats):
                if case['cache'] == 'cold':
                    evict()
                start = time.perf_counter_ns()
                cp = subprocess.run(commands[mode], cwd=ROOT, env=env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120)
                elapsed += (time.perf_counter_ns()-start)/1e6
                assert cp.returncode == correctness[mode]['exit'] and cp.stderr.hex() == correctness[mode]['stderr_hex']
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            counters = {'major_faults':after.ru_majflt-before.ru_majflt,
                        'input_blocks':after.ru_inblock-before.ru_inblock,
                        'user_seconds':after.ru_utime-before.ru_utime,
                        'system_seconds':after.ru_stime-before.ru_stime}
            return elapsed/repeats, counters

        for mode in modes:
            batch(mode, 1)
        pilot = stats.median(batch('baseline-a', 1)[0] for _ in range(3))
        repeats = min(25, max(1, math.ceil(50/pilot)))
        entry = {**case, 'verification':correctness, 'pilot_ms':pilot, 'repetitions':repeats,
                 'timings_ms':{m:[] for m in modes}, 'resources':{m:[] for m in modes}, 'order':[]}
        result['cases'].append(entry)
        for _ in range(args.samples):
            order = list(modes); rng.shuffle(order); entry['order'].append(order)
            for mode in order:
                elapsed, counters = batch(mode, repeats)
                entry['timings_ms'][mode].append(elapsed)
                entry['resources'][mode].append(counters)
            save()
        times = entry['timings_ms']
        baseline = [(a+b)/2 for a,b in zip(times['baseline-a'],times['baseline-b'])]
        entry['comparisons'] = {m:comparison(baseline,times[m]) for m in modes if not m.startswith('baseline')}
        entry['controls'] = [comparison(times['baseline-a'],times['baseline-b']), comparison(times['baseline-b'],times['baseline-a'])]
        entry['warm_io'] = case['cache'] == 'warm' and any(c['input_blocks'] or c['major_faults'] for rows in entry['resources'].values() for c in rows)
        entry['unstable_controls'] = any(c['verdict'] == 'FAIL' for c in entry['controls'])
        entry['verdict'] = entry['comparisons']['candidate']['verdict']
        if 'reference' in times:
            entry['reference_comparison'] = comparison(times['reference'], times['candidate'])
            verdicts = [entry['verdict'], entry['reference_comparison']['verdict']]
            entry['verdict'] = ('FAIL' if 'FAIL' in verdicts else
                                'INCONCLUSIVE' if 'INCONCLUSIVE' in verdicts else 'PASS')
        # Contamination prevents attributing even an apparent loss to the build.
        if entry['warm_io'] or entry['unstable_controls']:
            entry['verdict'] = 'INCONCLUSIVE'
        save()
        print(case['name'], entry['verdict'], {m:round(c['elapsed_ratio'],4) for m,c in entry['comparisons'].items()},
              'warm_io='+str(entry['warm_io']), 'control_noise='+str(entry['unstable_controls']), flush=True)
    assert all(digest(Path(path)) == sha for path,sha in result['artifacts'].items()), 'A companion artifact changed during timing'
    result['memory_events'] = (group/'memory.events').read_text()
    result['memory_peak_bytes'] = int((group/'memory.peak').read_text())
    result['status'] = 'complete'
    result['verdict'] = ('FAIL' if any(c['verdict']=='FAIL' for c in result['cases']) else
                         'INCONCLUSIVE' if any(c['verdict']=='INCONCLUSIVE' for c in result['cases']) else 'PASS')
    save()
    print('AUDIT', result['verdict'], flush=True)


if __name__ == '__main__':
    main()
