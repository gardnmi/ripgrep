#!/usr/bin/env python3
"""Reject a candidate unless two complete, comparable audit sessions pass."""
import argparse
import collections
import json
from pathlib import Path
import sys

from bench import ROOT, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('sessions', type=Path, nargs=2)
    p.add_argument('--manifest', type=Path, default=ROOT/'benchmarks/assembly/audit/manifest.json')
    p.add_argument('--protocol', type=Path, default=ROOT/'benchmarks/assembly/audit/PLAN.md')
    p.add_argument('--require-isolation-watch',type=Path,action='append',default=[])
    args = p.parse_args()
    expected_names = {c['name'] for c in json.loads(args.manifest.read_text())['cases']}
    runs = [json.loads(path.read_text()) for path in args.sessions]
    problems = []
    for path, run in zip(args.sessions, runs):
        required = {str(p.resolve()) for p in args.require_isolation_watch}
        if not required <= set(run.get('isolation_watch',[])):
            problems.append(f'{path}: required interference guards missing')
        if required and run.get('isolation_checks',0) < len(expected_names)*run['samples']+2:
            problems.append(f'{path}: incomplete interference checks')
        if run.get('external_interference'):
            problems.append(f'{path}: competing work observed')
        if run['status'] != 'complete' or run['subset'] or run['samples'] < 15:
            problems.append(f'{path}: incomplete audit or too few rounds')
        names = [c['name'] for c in run['cases']]
        if set(names) != expected_names or len(names) != len(expected_names):
            problems.append(f'{path}: workload set differs')
        if run['manifest_sha256'] != digest(args.manifest):
            problems.append(f'{path}: input manifest differs')
        if run['protocol_sha256'] != digest(args.protocol):
            problems.append(f'{path}: protocol differs')
        for case in run['cases']:
            for mode in run['binaries']:
                if len(case['timings_ms'][mode]) != run['samples'] or len(case['resources'][mode]) != run['samples']:
                    problems.append(f"{path}: {case['name']} has missing samples")
    if runs[0]['binaries'].keys() != runs[1]['binaries'].keys():
        problems.append('Binary comparison sets differ between sessions')
    for mode in runs[0]['binaries'].keys() & runs[1]['binaries'].keys():
        if runs[0]['binaries'][mode]['sha256'] != runs[1]['binaries'][mode]['sha256']:
            problems.append(f'{mode}: binaries differ between sessions')
    for run in runs:
        if run['binaries']['baseline-a']['sha256'] != run['binaries']['baseline-b']['sha256']:
            problems.append('Baseline controls are not identical')
    if runs[0]['seed'] == runs[1]['seed'] or runs[0]['reverse'] == runs[1]['reverse']:
        problems.append('Sessions must use distinct seeds and opposite case order')
    if runs[0].get('artifacts', {}) != runs[1].get('artifacts', {}):
        problems.append('Companion artifacts differ between sessions')
    if runs[0].get('isolation_watch',[]) != runs[1].get('isolation_watch',[]):
        problems.append('Interference guards differ between sessions')
    print(json.dumps({'validation_errors': problems,
                      'sessions': {str(path):dict(collections.Counter(c.get('verdict', 'INCOMPLETE') for c in run['cases']))
                                   for path,run in zip(args.sessions,runs)}}, indent=2))
    if problems:
        return 2
    if any(c['verdict'] == 'FAIL' for run in runs for c in run['cases']):
        print('REJECT: measured regressions; do not promote this binary.')
        return 1
    if any(c['verdict'] != 'PASS' or c['warm_io'] or c['unstable_controls'] for run in runs for c in run['cases']):
        print('INCONCLUSIVE: the evidence does not establish the required bound.')
        return 2
    print('PASS within the recorded workload matrix and practical margin only.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
