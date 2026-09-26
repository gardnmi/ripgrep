#!/usr/bin/env python3
"""Exercise real bundle handoffs, fallback and output on disk-backed inputs."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from bench import ROOT, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle', type=Path, default=ROOT/'target/dispatch-experiment/bundle')
    p.add_argument('--baseline', type=Path, default=ROOT/'target/machine/rg-upstream-native')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    env = {k:v for k,v in os.environ.items() if not k.startswith('RG_') and k != 'RIPGREP_CONFIG_PATH'}
    env['LC_ALL'] = 'C.UTF-8'
    routes, comparisons = [], 0
    with tempfile.TemporaryDirectory(dir=ROOT/'target', prefix='bundle-check-') as tmp:
        root = Path(tmp)
        launcher = root/'rg'
        shutil.copy2(args.bundle/'rg', launcher)
        shutil.copy2(args.bundle/'librg_class_dispatch.so', root/'librg_class_dispatch.so')
        # A distinct exit proves execve was reached. This is only a test helper,
        # never the measured worker, and the real worker is restored below.
        source = root/'marker.c'
        source.write_text('int main(void) { return 77; }\n')
        worker = root/'rg-class-worker'
        subprocess.run(['cc', '-o', str(worker), str(source)], check=True)
        text = root/'input with spaces.txt'
        line = b'ordinary text 12345 abcdef 67890\n'
        data = line * (9*1024**2//len(line))
        data += b'A'*129 + b'\n' + b'f'*129 + b'\n' + b'9'*129
        text.write_bytes(data)
        small = root/'small'; small.write_bytes(b'A'*40+b'\n')
        long = root/'long'; long.write_bytes(b'.'*(9*1024**2)+b'A'*40+b'\n')
        binary = root/'binary'; binary.write_bytes(b'\0'+data)
        config = root/'config'; config.write_text('--ignore-case\n')

        def route(name, command, expected, extra=None):
            got = subprocess.run([str(launcher), *command], env=env | (extra or {}),
                                 capture_output=True, timeout=30)
            assert (got.returncode == 77) == expected, (name, got.returncode, got.stderr[:200])
            routes.append({'name':name, 'specialist':expected})

        eligible = ['[A-Za-z]{30}', '[A-Fa-f0-9]{17}', '[0-9]{8}',
                    '[A-Za-z]{2,65}', '[A-Za-z]{2,}', '[A-Za-z]{30}?',
                    '[a-zA-Z_0-9]{30}', '[A-FP-Za-fp-z]{30}']
        for pattern in eligible:
            route(pattern, ['--no-config','-c',pattern,str(text)], True)
        for pattern in ['ordinary','[A-Za-z]+','[A-Za-z]{0,5}','[A-Za-z]{1}',
                        '[ABC]{3}', '[A-Z&&a-z]{3}', '[A-Z~~a-z]{3}',
                        '[A-Z]{3}|foo','[A-Z]{3}x','[^A-Z]{3}',
                        '[A-Z]{42949672960}', '[A-Z]{4,2}', '[A-Z]{',
                        '[A-Z]', '[', '', '[é-ÿ]{3}']:
            route('fallback '+pattern, ['--no-config','-c',pattern,str(text)], False)
        base = ['--no-config','-c','[A-Za-z]{30}',str(text)]
        for extra in [{'RG_BUNDLE':'0'}, {'RG_CLASS':'0'}, {'RG_ASM':'0'}, {'RG_ASM':'rust'}]:
            route('disabled '+str(extra), base, False, extra)
        route('config',base[1:],False,{'RIPGREP_CONFIG_PATH':str(config)})
        route('config explicitly ignored',base,True,{'RIPGREP_CONFIG_PATH':str(config)})
        route('combined short flags',['--no-config','-nc','[A-Za-z]{30}',str(text)],True)
        route('end of options',['--no-config','-c','--','[A-Za-z]{30}',str(text)],True)
        for file in [small,long,binary,root,root/'missing']:
            route('input '+file.name,['--no-config','-c','[A-Za-z]{30}',str(file)],False)
        for flag in ['-i','-o','-v','--mmap','--no-mmap','--stats']:
            route('option '+flag,base[:1]+[flag]+base[1:],False)

        def compare(command, extra=None):
            nonlocal comparisons
            outputs = []
            for executable in [args.baseline, launcher]:
                proc = subprocess.run([str(executable),*command], env=env | (extra or {}),
                                      capture_output=True, timeout=30)
                outputs.append((proc.returncode,proc.stdout,proc.stderr))
            assert outputs[0] == outputs[1], (command, extra, [(x[0],x[1][:100],x[2][:200]) for x in outputs])
            comparisons += 1

        worker.unlink()
        compare(base)  # Missing worker must leave upstream in control.
        worker.write_text('not executable\n'); worker.chmod(0o644)
        compare(base)  # An unusable worker must also leave upstream in control.
        worker.unlink(); shutil.copy2(args.bundle/'rg-class-worker',worker)
        for pattern in eligible + ['[A-Za-z]{64}','[A-Za-z]{65}','[A-Za-z]{129}',
                                   '[A-Z]{4,2}', '[A-Z]{42949672960}']:
            compare(['--no-config','-c',pattern,str(text)])
        for file in [text,small,long,binary]:
            for flags in [[],['-n'],['-c']]:
                compare(['--no-config',*flags,'[A-Za-z]{30}',str(file)])
        for prefix in [b'\xef\xbb\xbf', b'\xff\xfe', b'\xff\x80']:
            text.write_bytes(prefix+data)
            compare(base)
        # NUL after the routing probe must preserve upstream's binary behavior.
        text.write_bytes(data[:8192]+b'\0'+data[8192:]); compare(base)
        text.write_bytes(data)
        compare(base[1:],{'RIPGREP_CONFIG_PATH':str(config)})
        compare(base,{'RIPGREP_CONFIG_PATH':str(config)})
        for extra in [{'RG_BUNDLE':'0'},{'RG_CLASS':'0'},{'RG_ASM':'rust'}]:
            compare(base,extra)
    result = {'result':'PASS','route_checks':routes,'exact_comparisons':comparisons,
              'baseline_sha256':digest(args.baseline),
              'artifacts':{name:digest(args.bundle/name) for name in ['rg','librg_class_dispatch.so','rg-class-worker']}}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(routes)} routing assertions, {comparisons} exact CLI comparisons')


if __name__ == '__main__':
    main()
