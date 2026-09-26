#!/usr/bin/env python3
"""Add a syscall-only startup router in an unused upstream ELF address gap."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

from bench import ROOT, digest
from class_bundle import code_sections


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,default=ROOT/'target/machine/rg-upstream-native')
    p.add_argument('--worker',type=Path,default=ROOT/'target/dispatch-experiment/rg-specialized-native')
    p.add_argument('--output',type=Path,default=ROOT/'target/entry-experiment/bundle')
    p.add_argument('--metadata',type=Path,default=ROOT/'benchmarks/assembly/dispatch/entry-build.json')
    args = p.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    original=args.baseline.read_bytes(); data=bytearray(original)
    assert data[:6] == b'\x7fELF\x02\x01'
    header=struct.unpack_from('<16sHHIQQQIHHHHHH',data)
    assert header[1] == 3 and header[2] == 62  # PIE, x86-64
    entry,phoff,phsize,phnum=header[4],header[5],header[9],header[10]
    assert phsize == 56
    ph=[struct.unpack_from('<IIQQQQQQ',data,phoff+i*phsize) for i in range(phnum)]
    loads=[s for s in ph if s[0]==1]
    assert loads==sorted(loads,key=lambda s:s[3])
    gaps=[((a[3]+a[6]+4095)&~4095,b[3]&~4095) for a,b in zip(loads,loads[1:])]
    address,end=next((a,b) for a,b in gaps if b-a>=4096)
    notes=[s for s in ph if s[0]==4]
    assert len(notes)==1, 'This experimental patcher requires one replaceable NOTE header.'
    # Only GNU ABI-tag/build-id notes may lose their program-header reference.
    note=notes[0]; cursor=note[2]; limit=cursor+note[5]
    while cursor<limit:
        namesz,descsz,kind=struct.unpack_from('<III',data,cursor);cursor+=12
        name=bytes(data[cursor:cursor+namesz]);cursor+=(namesz+3)&~3
        assert name==b'GNU\0' and kind in (1,3), (name,kind)
        cursor+=(descsz+3)&~3
    assert cursor==limit
    sources=[ROOT/'scripts/assembly/entry_start.S',ROOT/'scripts/assembly/entry_dispatch.c']
    commands=[];objects=[]
    for source in sources:
        obj=out/(source.stem+'.o'); objects.append(obj)
        cmd=['cc','-Os','-march=znver4','-fpie','-ffreestanding','-fno-builtin',
             '-fno-stack-protector','-fno-asynchronous-unwind-tables','-fno-unwind-tables',
             '-fno-ident','-mno-red-zone','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)]
        subprocess.run(cmd,check=True);commands.append(cmd)
    script=out/'payload.ld'
    script.write_text(f'ENTRY(rg_entry)\nrg_upstream_entry = {entry};\nSECTIONS {{\n'
                      f' . = {address};\n .payload : {{ KEEP(*(.text.rg_entry)) *(.text*) *(.rodata*) }}\n'
                      ' /DISCARD/ : { *(.eh_frame*) *(.comment) *(.note*) }\n}\n')
    payload_elf=out/'payload.elf';payload_bin=out/'payload.bin'
    cmd=['ld','--no-undefined','-T',str(script),'-o',str(payload_elf),*[str(o) for o in objects]]
    subprocess.run(cmd,check=True);commands.append(cmd)
    assert not subprocess.check_output(['nm','-u',str(payload_elf)]).strip()
    cmd=['objcopy','-O','binary','--only-section=.payload',str(payload_elf),str(payload_bin)]
    subprocess.run(cmd,check=True);commands.append(cmd)
    payload=payload_bin.read_bytes()
    assert 0<len(payload)<=end-address
    assert struct.unpack_from('<Q',payload_elf.read_bytes(),24)[0]==address
    offset=(len(data)+4095)&~4095
    new=(1,5,offset,address,address,len(payload),len(payload),4096)
    rewritten=[];inserted=False
    for s in ph:
        if s==note: continue
        if not inserted and s[0]==1 and s[3]>address:
            rewritten.append(new);inserted=True
        rewritten.append(s)
    assert inserted and len(rewritten)==phnum
    assert [s for s in rewritten if s[0]==1 and s!=new]==loads
    # Existing highest mapping (and consequently the normal program break)
    # is unchanged. No loader dependency, GOT, TLS, or existing section moves.
    assert max(s[3]+s[6] for s in rewritten if s[0]==1)==max(s[3]+s[6] for s in loads)
    struct.pack_into('<Q',data,24,address)
    for i,s in enumerate(rewritten):struct.pack_into('<IIQQQQQQ',data,phoff+i*phsize,*s)
    data.extend(b'\0'*(offset-len(data)));data.extend(payload)
    launcher=out/'rg';launcher.write_bytes(data);launcher.chmod(0o755)
    worker=out/'rg-class-worker';shutil.copy2(args.worker,worker)
    assert code_sections(args.baseline)==code_sections(launcher)
    # Only the entry field and program header table may differ in old bytes.
    restored=bytearray(data[:len(original)])
    restored[24:32]=original[24:32]
    restored[phoff:phoff+phnum*phsize]=original[phoff:phoff+phnum*phsize]
    assert bytes(restored)==original
    result={'baseline_sha256':digest(args.baseline),'artifacts':{p.name:digest(p) for p in [launcher,worker]},
            'tool_versions':{tool:subprocess.check_output([tool,'--version'],text=True).splitlines()[0] for tool in ['cc','ld','objcopy']},
            'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sources},
            'commands':commands,'original_entry':entry,'new_entry':address,'payload_bytes':len(payload),
            'payload_sha256':hashlib.sha256(payload).hexdigest(),'payload_file_offset':offset,
            'preserved':'Every original byte except e_entry and program-header table; all original LOAD mappings unchanged.',
            'note_header':'GNU ABI-tag/build-id remain as section data; their NOTE program-header slot becomes the extra RX LOAD.'}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    args.metadata.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
