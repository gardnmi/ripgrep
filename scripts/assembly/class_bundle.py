#!/usr/bin/env python3
"""Build a local glibc dispatcher while preserving upstream's executable code."""
import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess

from bench import ROOT, digest


def code_sections(path):
    data = path.read_bytes()
    assert data[:6] == b'\x7fELF\x02\x01'
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', data)
    offset, size, count, names_index = header[6], header[11], header[12], header[13]
    sections = [struct.unpack_from('<IIQQQQIIQQ',data,offset+i*size) for i in range(count)]
    names = sections[names_index]
    strings = data[names[4]:names[4]+names[5]]
    return {strings[s[0]:].split(b'\0',1)[0].decode():
            {'address':s[3], 'data':data[s[4]:s[4]+s[5]]} for s in sections if s[2] & 4}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, default=ROOT/'target/machine/rg-upstream-native')
    p.add_argument('--worker', type=Path, default=ROOT/'target/dispatch-experiment/rg-specialized-native')
    p.add_argument('--output', type=Path, default=ROOT/'target/dispatch-experiment/bundle')
    args = p.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    source = ROOT/'scripts/assembly/class_dispatch.c'
    library, launcher, worker = out/'librg_class_dispatch.so',out/'rg',out/'rg-class-worker'
    compile_command = ['cc','-O3','-march=znver4','-fPIC','-shared','-Wall','-Wextra','-Werror',
                       '-Wl,-z,relro,-z,now','-o',str(library),str(source)]
    subprocess.run(compile_command,check=True)
    shutil.copy2(args.baseline,launcher); shutil.copy2(args.worker,worker)
    patcher = ROOT/'target/dispatch-experiment/local-tools/usr/bin/patchelf'
    subprocess.run([str(patcher),'--set-rpath','$ORIGIN','--add-needed',library.name,str(launcher)],check=True)
    before,after = code_sections(args.baseline),code_sections(launcher)
    assert before == after, 'An executable section changed; do not benchmark as preserved upstream.'
    import hashlib
    result = {'baseline_sha256':digest(args.baseline),'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
              'compile_command':compile_command,'dispatcher_source_sha256':digest(source),
              'artifacts':{p.name:digest(p) for p in [launcher,library,worker]},
              'preserved_executable_sections':{name:{'address':s['address'],'bytes':len(s['data']),
                                                       'sha256':hashlib.sha256(s['data']).hexdigest()} for name,s in before.items()}}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'benchmarks/assembly/dispatch/bundle-build.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
