#!/usr/bin/env python3
"""Summarize complete sessions; the unchanged audit_gate owns acceptance."""
import argparse
import collections
import json
from pathlib import Path
import statistics


def cpu(case, mode):
    return [(r['user_seconds'] + r['system_seconds']) * 1000 / case['repetitions']
            for r in case['resources'][mode]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sessions', type=Path, nargs=2)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runs = [json.loads(p.read_text()) for p in args.sessions]
    assert all(r['status'] == 'complete' for r in runs)
    cases = [{c['name']: c for c in r['cases']} for r in runs]
    manifest = json.loads(args.manifest.read_text())
    names = [c['name'] for c in manifest['cases']]
    assert all(set(c) == set(names) for c in cases)
    directory_names = [c['name'] for c in manifest['cases']
                       if c.get('group') == 'everyday' and c['directory']]
    winners = []
    for name in directory_names:
        if all(c[name]['verdict'] == 'PASS'
               and c[name]['comparisons']['candidate']['elapsed_ratio'] <= 0.95
               and c[name]['comparisons']['candidate']['ratio_ci95'][1] < 1
               for c in cases):
            winners.append(name)
    rows = ['# CPU time per invocation', '',
            'Sum of child user and system CPU time. Two system controls are',
            'averaged within each round; the table gives medians across rounds.',
            'Positive percentages mean more CPU use. This is not an energy measurement.', '',
            '| Workload | A system CPU ms | A candidate CPU ms | A change | B system CPU ms | B candidate CPU ms | B change |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name in names:
        fields = [name]
        for mapping in cases:
            c = mapping[name]
            system = statistics.median((a+b)/2 for a,b in
                                       zip(cpu(c, 'baseline-a'), cpu(c, 'baseline-b')))
            candidate = statistics.median(cpu(c, 'candidate'))
            fields += [f'{system:.3f}', f'{candidate:.3f}',
                       f'{100*(candidate/system-1):+.2f}%']
        rows.append('| ' + ' | '.join(fields) + ' |')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'FINAL-CPU.md').write_text('\n'.join(rows)+'\n')
    summary = dict(directory_cases=len(directory_names), repeatable_directory_wins=winners,
                   improvement_target_met=len(winners) >= (len(directory_names)+1)//2,
                   note='Acceptance additionally requires the unchanged audit_gate to pass every case in both sessions.',
                   sessions=[])
    for path, run in zip(args.sessions, runs):
        summary['sessions'].append(dict(
            file=path.name, verdict=run['verdict'],
            counts=dict(collections.Counter(c['verdict'] for c in run['cases'])),
            nonpassing=[dict(name=c['name'], verdict=c['verdict'],
                             system_comparison=c['comparisons']['candidate'],
                             source_comparison=c['reference_comparison'],
                             warm_io=c['warm_io'], unstable_controls=c['unstable_controls'])
                        for c in run['cases'] if c['verdict'] != 'PASS'],
            memory_peak_bytes=run['memory_peak_bytes'], memory_events=run['memory_events'],
            external_interference=run.get('external_interference', [])))
    (args.output/'final-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='sessions'}, indent=2))
    for s in summary['sessions']:
        print(s['file'], s['verdict'], s['counts'])


if __name__ == '__main__':
    main()
