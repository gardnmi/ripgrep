#!/usr/bin/env python3
"""Interleaved hardware-counter diagnostics; not an acceptance benchmark."""
import argparse
import json
import os
from pathlib import Path
import random
import statistics
import subprocess

from bench import ROOT, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', action='append', required=True, help='label=path')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--rounds', type=int, default=5)
    args = p.parse_args()
    binaries = {label:Path(path).resolve() for label,path in (x.split('=',1) for x in args.binary)}
    env = {k:v for k,v in os.environ.items() if not k.startswith('RG_') and k != 'RIPGREP_CONFIG_PATH'}
    env['LC_ALL'] = 'C'
    env['LD_LIBRARY_PATH'] = str(ROOT/'target/machine/tools/usr/lib')
    os.sched_setaffinity(0, {4})
    perf = ROOT/'target/machine/tools/usr/bin/perf'
    manifest = json.loads((ROOT/'benchmarks/assembly/audit/manifest.json').read_text())
    names = ['literal-count', 'literal-only-offset', 'literal-dense', 'unicode-literal', 'subtitles-alpha30']
    cases = [c for c in manifest['cases'] if c['name'] in names]
    result = {'purpose':'Counter diagnostic, not wall-time acceptance', 'cpu_affinity':[4],
              'seed':187421, 'rounds':args.rounds,
              'binaries':{k:{'path':str(v), 'sha256':digest(v)} for k,v in binaries.items()}, 'cases':[]}
    rng = random.Random(result['seed'])
    for case in cases:
        entry = {'name':case['name'], 'samples':{m:[] for m in binaries}}
        for binary in binaries.values():
            cp = subprocess.run([str(binary),*case['arguments']],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            assert cp.returncode in (0,1) and not cp.stderr
        for _ in range(args.rounds):
            order = list(binaries); rng.shuffle(order)
            for mode in order:
                command = [str(perf),'stat','--no-big-num','-x',';', '-e',
                           'cycles:u,instructions:u,branches:u,branch-misses:u', '--',
                           str(binaries[mode]),*case['arguments']]
                cp = subprocess.run(command,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
                assert cp.returncode in (0,1),cp.stderr
                counts = {}
                for line in cp.stderr.splitlines():
                    fields = line.split(';')
                    if len(fields) >= 5 and fields[2] in ('cycles:u','instructions:u','branches:u','branch-misses:u'):
                        counts[fields[2]] = {'count':float(fields[0]), 'running_percent':float(fields[4])}
                assert len(counts) == 4, cp.stderr
                entry['samples'][mode].append(counts)
        entry['medians'] = {mode:{event:statistics.median(row[event]['count'] for row in rows)
                                 for event in rows[0]} for mode,rows in entry['samples'].items()}
        result['cases'].append(entry)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print(case['name'],entry['medians'],flush=True)


if __name__ == '__main__':
    main()
