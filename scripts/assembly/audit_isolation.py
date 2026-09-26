#!/usr/bin/env python3
"""Read-only detection of competing builds and jobs in explicitly watched repos."""
import os
from pathlib import Path


def external_work(watch_roots):
    roots = [str(Path(p).resolve()).rstrip('/')+'/' for p in watch_roots]
    own_group = Path('/proc/self/cgroup').read_text()
    found = []
    compilers = {'cargo','rustc','cc','gcc','g++','cc1','cc1plus','clang','clang++',
                 'ld','ld.lld','lld','lto1','collect2','ninja','make','perf','hyperfine'}
    interpreters = {'python','python3','python3.14','bash','sh','zsh','fish','node','ruby'}
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            if (proc/'cgroup').read_text() == own_group:
                continue
            stat = (proc/'stat').read_text().rsplit(')',1)[1].split()
            if stat[0] in ('T','t','Z','X'):
                continue
            name = (proc/'comm').read_text().strip()
            cwd, executable = str((proc/'cwd').resolve()),str((proc/'exe').resolve())
            watched_cwd = any(cwd+'/' == root or cwd.startswith(root) for root in roots)
            watched_exe = any(executable.startswith(root) for root in roots)
            driver = False
            if watched_cwd and name in interpreters:
                argv = (proc/'cmdline').read_bytes().split(b'\0')
                argv = [a for a in argv if a]
                # An idle interactive shell is not a competing job. Never
                # record argument strings: they could contain credentials.
                driver = len(argv)>1 and not (len(argv)==2 and argv[1] in (b'-l',b'--login',b'-i'))
            if name in compilers or watched_exe or driver:
                found.append({'pid':int(proc.name),'name':name,'cwd':cwd,'exe':executable,
                              'state':stat[0],'process_group':int(stat[2]),'start_ticks':int(stat[19])})
        except (OSError,ValueError):
            continue  # A process may exit during this read-only snapshot.
    return sorted(found,key=lambda p:p['pid'])
