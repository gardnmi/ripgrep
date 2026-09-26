#!/usr/bin/env python3
"""Build the everyday-search film from recorded measurements. Never runs rg."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from statistics import median

FEATURED = [
    ('source-literal', 'Find a name in your code', 'Small source repository', 'ripgrep-source'),
    ('tools-literal', 'Find TODOs across a project', 'Linux tools directory', 'linux/tools'),
    ('kernel-files', 'List a large source tree', 'Whole Linux source tree', 'linux'),
]
PIN = '55279a6c2e16c5bf8b441518d0f4d4f91c493060'
REPORT = f'https://github.com/gardnmi/ripgrep/tree/{PIN}/benchmarks/assembly/everyday'


def build(source, out):
    sessions, sources, cases = {}, {}, {}
    first = None
    for label, filename in [('A', 'final-session-a.json'), ('B', 'final-session-b.json')]:
        raw = (source / filename).read_bytes()
        d = json.loads(raw)
        sources[filename] = hashlib.sha256(raw).hexdigest()
        assert d['status'] == 'complete' and d['samples'] == 15
        assert len(d['cases']) == 117 and not d['external_interference']
        if first is None:
            first = d
        else:
            assert d['binaries'] == first['binaries']
            assert d['manifest_sha256'] == first['manifest_sha256']
        counts = dict(Counter(c['verdict'] for c in d['cases']))
        assert counts == {'PASS': 97, 'INCONCLUSIVE': 19, 'FAIL': 1}
        sessions[label] = dict(rounds=d['samples'], seed=d['seed'], reverse=d['reverse'],
                               counts=counts, verdict=d['verdict'])
        for c in d['cases']:
            assert len({json.dumps(v, sort_keys=True) for v in c['verification'].values()}) == 1
            system = c['comparisons']['candidate']
            reference = c['reference_comparison']
            timings = c['timings_ms']
            base = median((a+b)/2 for a, b in zip(timings['baseline-a'], timings['baseline-b']))
            mine = median(timings['candidate'])
            assert abs(base - system['baseline_ms']) < 1e-9
            assert abs(mine - system['candidate_ms']) < 1e-9
            assert abs(median(timings['reference']) - reference['baseline_ms']) < 1e-9
            cpu = {}
            for binary, observations in c['resources'].items():
                cpu[binary] = [(r['user_seconds'] + r['system_seconds']) * 1000 / c['repetitions']
                               for r in observations]
            base_cpu = median((a+b)/2 for a,b in zip(cpu['baseline-a'],cpu['baseline-b']))
            mine_cpu = median(cpu['candidate'])
            row = cases.setdefault(c['name'], dict(id=c['name'], arguments=c['arguments'],
                cache=c['cache'], directory=c['directory'], group=c['group']))
            row[label] = dict(system=system, reference=reference, verdict=c['verdict'],
                             warm_io=c['warm_io'], unstable_controls=c['unstable_controls'],
                             cpu=dict(system=base_cpu, candidate=mine_cpu,
                                      change_percent=100*(mine_cpu/base_cpu-1)))
    directory = [c for c in cases.values() if c['directory'] and c['group'] == 'everyday']
    wins = [c['id'] for c in directory if all(
        c[s]['verdict'] == 'PASS' and c[s]['system']['elapsed_ratio'] <= .95
        and c[s]['system']['ratio_ci95'][1] < 1 for s in sessions)]
    assert len(directory) == 19 and len(wins) == 15
    featured = []
    for name, title, subtitle, path_label in FEATURED:
        c = cases[name]
        assert name in wins and c['cache'] == 'warm'
        args = c['arguments']
        # Only abbreviate the recorded final path. No command flags or patterns change.
        assert args[-1].startswith('/')
        featured.append(dict(id=name, title=title, subtitle=subtitle,
                             command=' '.join(args[:-1] + [path_label])))
    data = dict(title='my-grep / Everyday searches', duration=52, width=1600, height=900,
                cpu=first['cpu'], date='2026-09-26', report=REPORT, sourceCommit=PIN,
                upstream=first['candidate_parent'], sources=sources, binaries=first['binaries'],
                sessions=sessions, cases=list(cases.values()), featured=featured,
                directoryCount=len(directory), repeatedWins=wins,
                disclaimer='Recorded medians; animation slowed down. Prototype is not installed.')
    out.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    (out/'data.json').write_text(encoded)
    template = Path(__file__).with_suffix('.html').read_text()
    assert template.count('__BENCHMARK_DATA__') == 1
    (out/'index.html').write_text(template.replace('__BENCHMARK_DATA__', encoded.replace('</', '<\\/')))
    print(f'Validated all 234 case/session records; built {out}/index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report_dir', type=Path)
    parser.add_argument('output_dir', type=Path)
    a = parser.parse_args()
    build(a.report_dir, a.output_dir)
