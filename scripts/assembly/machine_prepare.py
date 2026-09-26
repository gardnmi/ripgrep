#!/usr/bin/env python3
"""Create disjoint, line-aligned PGO/evaluation slices on disk, 8 MiB at a time."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
base = ROOT/'target/machine'
base.mkdir(parents=True, exist_ok=True)
source = ROOT/'target/assembly-readme/en.txt'
records = []
with source.open('rb') as src:
    for name, offset, size in [('train', 0, 256*1024**2),
                               ('heldout', 4*1024**3, 512*1024**2),
                               ('heldout2', 8*1024**3, 256*1024**2)]:
        src.seek(offset)
        if offset: src.readline()
        begin = src.tell()
        remaining = size
        sha = hashlib.sha256()
        with (base/(name+'.txt')).open('wb') as dst:
            while remaining:
                block = src.read(min(8*1024**2, remaining))
                if not block: raise RuntimeError('incomplete subtitle corpus')
                dst.write(block); sha.update(block); remaining -= len(block)
            block = src.readline()
            dst.write(block); sha.update(block)
        records.append({'name': name, 'source_start': begin, 'bytes': src.tell()-begin, 'sha256': sha.hexdigest()})
(base/'slices.json').write_text(json.dumps(records, indent=2)+'\n')
print(json.dumps(records, indent=2))
