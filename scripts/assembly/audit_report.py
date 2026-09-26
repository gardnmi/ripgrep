#!/usr/bin/env python3
"""Render every workload's results, without hiding small median slowdowns."""
import argparse
import collections
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('sessions', type=Path, nargs=2)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    runs = [json.loads(path.read_text()) for path in args.sessions]
    assert all(r['status'] == 'complete' for r in runs)
    rows = ['# Complete performance results', '',
            'Elapsed time per invocation, including startup; lower is better. ',
            'Positive percentages are slowdowns. Intervals are paired bootstrap ',
            '95% intervals for elapsed-time change. They are per-case intervals, ',
            'not simultaneous confidence across the whole suite. All observations ',
            'remain in the linked JSON files. PASS permits the predeclared practical ',
            'margin; it does not mean exactly zero slowdown.', '']
    for label, path, run in zip(['A','B'], args.sessions, runs):
        count = collections.Counter(c['verdict'] for c in run['cases'])
        rows += [f"Session {label}: [{path.name}]({path.name}); seed {run['seed']}; "
                 f"{run['samples']} paired rounds; reverse order {run['reverse']}. "
                 f"{count['PASS']} PASS, {count['FAIL']} FAIL, {count['INCONCLUSIVE']} INCONCLUSIVE.", '']
    rows += ['| Workload | A upstream ms | A candidate ms | A change %, 95% interval | A verdict | B upstream ms | B candidate ms | B change %, 95% interval | B verdict |',
             '| --- | ---: | ---: | --- | --- | ---: | ---: | --- | --- |']
    maps = [{c['name']:c for c in r['cases']} for r in runs]
    assert maps[0].keys() == maps[1].keys()
    for name in maps[0]:
        fields = [name]
        for cases in maps:
            case = cases[name]
            c = case['comparisons']['candidate']
            low,high = [(r-1)*100 for r in c['ratio_ci95']]
            fields += [f"{c['baseline_ms']:.3f}", f"{c['candidate_ms']:.3f}",
                       f"{(c['elapsed_ratio']-1)*100:+.2f} [{low:+.2f}, {high:+.2f}]", case['verdict']]
        rows.append('| ' + ' | '.join(fields) + ' |')
    if any('reference_comparison' in c for r in runs for c in r['cases']):
        rows += ['', '## Additional native reference', '',
                 'The candidate must also pass against this unmodified reference. ',
                 'These comparisons use the same paired rounds.', '',
                 '| Workload | A reference ms | A candidate change %, 95% interval | A verdict | B reference ms | B candidate change %, 95% interval | B verdict |',
                 '| --- | ---: | --- | --- | ---: | --- | --- |']
        for name in maps[0]:
            fields = [name]
            for cases in maps:
                c = cases[name]['reference_comparison']
                low,high = [(r-1)*100 for r in c['ratio_ci95']]
                fields += [f"{c['baseline_ms']:.3f}",
                           f"{(c['elapsed_ratio']-1)*100:+.2f} [{low:+.2f}, {high:+.2f}]", c['verdict']]
            rows.append('| ' + ' | '.join(fields) + ' |')
    rows += ['', '## Measurement checks', '']
    for label, run in zip(['A','B'], runs):
        samples = sum(len(v) for c in run['cases'] for v in c['timings_ms'].values())
        invocations = sum(len(v)*c['repetitions'] for c in run['cases'] for v in c['timings_ms'].values())
        io_cases = [c['name'] for c in run['cases'] if c['warm_io']]
        noisy = [c['name'] for c in run['cases'] if c['unstable_controls']]
        rows += [f"Session {label}: {samples:,} timed batches / {invocations:,} timed invocations. "
                 f"Warm-I/O cases: {io_cases or 'none'}. Unstable-control cases: {noisy or 'none'}. "
                 f"Cgroup peak: {run['memory_peak_bytes']/1024**3:.2f} GiB.", '',
                 '```text', run['memory_events'].strip(), '```', '']
    args.output.write_text('\n'.join(row.rstrip() for row in rows).rstrip()+'\n')


if __name__ == '__main__':
    main()
