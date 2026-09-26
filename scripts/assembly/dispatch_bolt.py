#!/usr/bin/env python3
"""Profile and post-link optimize equally built upstream/candidate executables."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from bench import ROOT, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--label', required=True)
    args = p.parse_args()
    assert args.label in ('upstream', 'dispatch')
    base = ROOT/'target/dispatch-experiment'
    tools = base/'bolt-tools/usr/lib/llvm-22'
    bolt = tools/'bin/llvm-bolt'
    env = {k:v for k,v in os.environ.items() if not k.startswith('RG_') and k != 'RIPGREP_CONFIG_PATH'}
    env['LC_ALL'] = 'C.UTF-8'
    env['LD_LIBRARY_PATH'] = str(base/'bolt-tools/usr/lib/x86_64-linux-gnu')
    os.sched_setaffinity(0, {0,1,2,3,4,5})
    training = base/'training'; training.mkdir(exist_ok=True)
    for name, source in [('text', ROOT/'target/machine/train.txt'), ('logs', ROOT/'target/assembly-data/logs.txt')]:
        destination = training/name
        if not destination.exists():
            with source.open('rb') as src, destination.open('wb') as dst:
                remaining = 32*1024**2
                while remaining:
                    block = src.read(min(remaining,1024*1024))
                    assert block
                    dst.write(block); remaining -= len(block)
                dst.write(src.readline())
    jobs = [
        ('text', ['[A-Za-z]{24}']), ('text',['[A-Fa-f0-9]{11}']),
        ('text',['[0-9]{6}']), ('text',['-n','Sherlock']),
        ('text',['-w',r'Sherlock [A-Z]\w+']), ('text',['the']),
        ('text',['-c','the']), ('text',['-o','-b','the']),
        ('text',['-i','Sherlock']), ('text',['-c',r'\w+']),
        ('logs',['-n','INFO']), ('logs',['-n','ERROR']),
        ('logs',['-c','INFO']), ('logs',['-o','-b','INFO']),
        ('logs',['-c',r'^[A-Za-z]+']), ('logs',['-C','2','ERROR']),
    ]
    profile_dir = base/f'bolt-profile-{args.label}'; profile_dir.mkdir(exist_ok=True)
    for old in profile_dir.glob('run.*'):
        old.unlink()
    binary = args.binary.resolve()
    instrumented = base/f'rg-{args.label}-instrumented'
    profile = base/f'{args.label}.fdata'
    optimized = base/f'rg-{args.label}-bolt'
    instrument_command = [str(bolt),str(binary),'-instrument',
                          f'-instrumentation-file={profile_dir}/run',
                          '-instrumentation-file-append-pid',
                          f'-runtime-instrumentation-lib={tools}/lib/libbolt_rt_instr.a',
                          '-o',str(instrumented)]
    with (base/f'{args.label}-instrument.log').open('w') as log:
        subprocess.run(instrument_command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    for name, flags in jobs:
        cp = subprocess.run([str(instrumented),'--no-config',*flags,str(training/name)],
                            env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        assert cp.returncode in (0,1),cp.stderr
        print(args.label, 'trained',name,flags,flush=True)
    pieces = sorted(profile_dir.glob('run.*'))
    assert len(pieces) == len(jobs),(len(pieces),len(jobs))
    with profile.open('w') as out:
        subprocess.run([str(tools/'bin/merge-fdata'),*[str(p) for p in pieces]],
                       env=env,stdout=out,check=True)
    optimize_command = [str(bolt),str(binary),'-o',str(optimized),f'-data={profile}',
                        '-reorder-blocks=ext-tsp','-reorder-functions=cdsort',
                        '-split-functions','-split-all-cold','-split-eh','-dyno-stats']
    with (base/f'{args.label}-optimize.log').open('w') as log:
        subprocess.run(optimize_command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    report = {'label':args.label,'input_sha256':digest(binary),'output_sha256':digest(optimized),
              'profile_sha256':digest(profile), 'training_jobs':jobs,
              'training_inputs':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(training.iterdir())},
              'instrument_command':instrument_command,'optimize_command':optimize_command,
              'bolt_version':subprocess.check_output([str(bolt),'--version'],env=env,text=True)}
    (ROOT/f'benchmarks/assembly/dispatch/bolt-{args.label}.json').write_text(json.dumps(report,indent=2)+'\n')
    print('optimized',optimized,flush=True)


if __name__ == '__main__':
    main()
