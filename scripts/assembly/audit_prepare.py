#!/usr/bin/env python3
"""Freeze a broad regression workload matrix before inspecting measurements."""
import hashlib
import json
from pathlib import Path
import random

from bench import ROOT, digest

BASE = ROOT / 'target/regression-audit'
DATA = BASE / 'data'
DATA.mkdir(parents=True, exist_ok=True)
rng = random.Random(23091877)


def repeat(name, block, size):
    path = DATA/name
    with path.open('wb') as out:
        while size:
            part = block[:size]
            out.write(part)
            size -= len(part)
    return path


rows = []
for i in range(10000):
    rows.append(f"record={i:06} {'RARE_MARK' if i % 997 == 0 else 'normal'} user={rng.randrange(100000):05} status={rng.choice([200,201,404,500])} message=alpha beta gamma {rng.randrange(2**32):08x}\n")
mixed = ''.join(rows).encode()
repeat('mixed.txt', mixed, 32*1024**2)
repeat('cold.txt', mixed, 32*1024**2)
repeat('small.txt', mixed, 4096)
(DATA/'empty.txt').write_bytes(b'')
(DATA/'tiny.txt').write_bytes(b'abc 123\n')
repeat('json.txt', mixed, 128*1024)
repeat('dense.txt', b'a'*127+b'\n'+b'0123456789'*13+b'\n'+b'ABCDEFabcdef'*11+b'\n', 32*1024**2)
repeat('absent.txt', b'!.-_ \n'*1000, 32*1024**2)
varied = b''.join(b'a'*n+b' 01234567 '+b'B'*((n*7)%140)+b'\n' for n in [1,2,3,7,8,15,16,24,30,31,63,64,65,129]*300)
repeat('varied.txt', varied, 32*1024**2)
repeat('unicode.txt', 'café CAFÉ Straße STRASSE 東京 κόσμος Καλημέρα 123 abcdef\n'.encode()*1000, 16*1024**2)
repeat('crlf.txt', b'alpha 123\r\nbeta 456\r\nfoo\r\nbar\r\n'*1000, 8*1024**2)
repeat('multiline.txt', b'alpha\nfoo\nbar\nbeta\n'*1000, 8*1024**2)
repeat('binary.bin', b'hello\x00abc\xff\x80\nABCDEF1234\n'*1000, 8*1024**2)
repeat('long.txt', b'a'*65536, 16*1024**2)
with (DATA/'long.txt').open('ab') as f: f.write(b'TOKEN\n')

# Real text from a section not used by any of the previous performance runs.
with (ROOT/'target/assembly-readme/en.txt').open('rb') as src:
    src.seek(6*1024**3); src.readline()
    begin = src.tell(); remaining = 128*1024**2
    with (DATA/'subtitles.txt').open('wb') as dst:
        while remaining:
            block = src.read(min(8*1024**2, remaining))
            assert block
            dst.write(block); remaining -= len(block)
        dst.write(src.readline())

cases = []


def add(name, file, args, *, category='ordinary', directory=False, cpus=None, cache='warm', json_output=False):
    path = file if isinstance(file, Path) else DATA/file
    cases.append({'name': name, 'category': category, 'path': str(path),
                  'arguments': ['--no-config', *args, str(path)], 'directory': directory,
                  'affinity': cpus or [4], 'cache': cache, 'json_output': json_output})


for name, file, args in [
    ('empty', 'empty.txt', ['x']), ('tiny-hit','tiny.txt',['abc']),
    ('tiny-miss','tiny.txt',['absent']), ('tiny-class30','tiny.txt',['[A-Za-z]{30}']),
    ('small-literal','small.txt',['normal']), ('small-regex','small.txt',[r'user=\d+']),
    ('literal-dense','mixed.txt',['normal']), ('literal-sparse-lines','mixed.txt',['-n','RARE_MARK']),
    ('literal-absent','mixed.txt',['NOT_PRESENT_XYZ']), ('literal-fixed','mixed.txt',['-F','status=200']),
    ('literal-insensitive','mixed.txt',['-i','NORMAL']), ('literal-word','mixed.txt',['-w','alpha']),
    ('literal-count','mixed.txt',['-c','normal']), ('literal-count-matches','mixed.txt',['--count-matches','a']),
    ('literal-only-offset','mixed.txt',['-o','-b','user']), ('literal-context','mixed.txt',['-C','2','RARE_MARK']),
    ('literal-invert','mixed.txt',['-v','normal']), ('literal-limit','mixed.txt',['-m','2','normal']),
    ('literal-quiet','mixed.txt',['-q','normal']), ('literal-multi-pattern','mixed.txt',['-e','RARE_MARK','-e','status=500']),
    ('regex-general','mixed.txt',['-c',r'status=[45][0-9]{2}']),
    ('regex-captures','mixed.txt',['-o',r'(user)=([0-9]+)']),
    ('regex-replace','mixed.txt',['--replace','$2:$1',r'(user)=([0-9]+)']),
    ('regex-anchored','mixed.txt',['-c',r'^record=[0-9]+']),
    ('regex-zero-length','mixed.txt',['-c','[A-Z]*']),
    ('regex-word-class','mixed.txt',['-w','[a-z]{8}']),
    ('regex-lazy-class','varied.txt',['-c','[a-z]{2,30}?']),
    ('regex-whole-class','varied.txt',['-x','[a-z]{30}']),
    ('unicode-literal','unicode.txt',['-c','東京']), ('unicode-fold','unicode.txt',['-i','-c','café']),
    ('unicode-word','unicode.txt',['-c',r'\w+']), ('unicode-property','unicode.txt',['-c',r'\pL{3}']),
    ('unicode-class-fallback','unicode.txt',['-c','[a-zα-ω]{3}']),
    ('crlf','crlf.txt',['--crlf','-n',r'^alpha']),
    ('multiline','multiline.txt',['-U',r'foo\nbar']),
    ('binary-default','binary.bin',['ABCDEF']), ('binary-text','binary.bin',['-a','-c','ABCDEF']),
    ('null-lines','binary.bin',['--null-data','-a','-c','abc']),
    ('long-line-literal','long.txt',['-o','TOKEN']), ('long-line-class','long.txt',['-c','[a-z]{65}']),
    ('subtitles-sherlock','subtitles.txt',['-w',r'Sherlock [A-Z]\w+']),
    ('subtitles-sherlock-lines','subtitles.txt',['-n','-w',r'Sherlock [A-Z]\w+']),
    ('subtitles-frequent','subtitles.txt',['the']),
    ('subtitles-alpha30','subtitles.txt',['[A-Za-z]{30}']),
    ('subtitles-hex17','subtitles.txt',['[A-Fa-f0-9]{17}']),
    ('subtitles-digits8','subtitles.txt',['[0-9]{8}']),
    ('json','json.txt',['--json','RARE_MARK']), ('color','json.txt',['--color','always','normal']),
]: add(name, file, args, json_output=(name=='json'))
for minimum in [1,2,3,7,8,15,16,30,64,65,129]:
    add(f'class-dense-{minimum}', 'dense.txt', ['-c', f'[a-z]{{{minimum}}}'], category='class-stress')
for minimum in [1,2,8,16,30,65]:
    add(f'class-absent-{minimum}', 'absent.txt', ['-c', f'[a-z]{{{minimum}}}'], category='class-stress')
for minimum in [2,8,16,30,65]:
    add(f'class-varied-{minimum}', 'varied.txt', ['-n', f'[A-Za-z]{{{minimum}}}'], category='class-stress')
for name, args in [('wide-ascii',['-c','[\x01-\x7f]{30}']),('optional-class',['-c','[a-z]{0,30}']),('captured-class',['-c','([a-z]{30})'])]:
    add(name, 'varied.txt', args, category='class-stress')
tree=ROOT/'target/assembly-data/source-tree'
for name,args,cpus in [('tree-literal',['Searcher'],[0,1,2,3,4,5]),('tree-regex',[r'fn\s+\w+'],[0,1,2,3,4,5]),('tree-files',['-l','Searcher'],[0,1,2,3,4,5]),('tree-sorted',['--sort','path','-n','Searcher'],[4])]:
    add(name,tree,args,category='directory',directory=True,cpus=cpus)
kernel=ROOT/'target/assembly-readme/linux'
add('kernel-default',kernel,['-n','-w','[A-Z]+_SUSPEND'],category='directory',directory=True,cpus=[0,1,2,3,4,5])
add('kernel-c',kernel,['-uuu','-tc','-n','-w','[A-Z]+_SUSPEND'],category='directory',directory=True,cpus=[0,1,2,3,4,5])
add('cold-literal','cold.txt',['-c','NOT_PRESENT_XYZ'],category='cold-io',cache='cold')
add('cold-regex','cold.txt',['-c','status=[45][0-9]{2}'],category='cold-io',cache='cold')

manifest = {'seed': 23091877, 'subtitle_source_start': begin, 'cases': cases,
            'inputs': {str(p): {'bytes':p.stat().st_size, 'sha256':digest(p)} for p in sorted(DATA.iterdir())},
            'source_revision': '3fce3b5bb0236da2df6d99672afb8a719642eca7',
            'kernel_revision': '84e57d292203a45c96dbcb2e6be9dd80961d981a'}
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(len(cases), 'cases; manifest', digest(BASE/'manifest.json'))
