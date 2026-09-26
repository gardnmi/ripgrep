#!/usr/bin/env python3
"""Fixed PGO training set, disjoint from held-out subtitle benchmark slices."""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('binary', type=Path)
args = parser.parse_args()
env = {k: v for k, v in os.environ.items() if not k.startswith('RG_') and k != 'RIPGREP_CONFIG_PATH'}
env['LC_ALL'] = 'C.UTF-8'
file = ROOT / 'target/machine/train.txt'
jobs = [(['[A-Za-z]{24}'], file), (['[0-9]{6}'], file),
        (['-n', 'Sherlock'], file), (['-w', 'Sherlock [A-Z]\\w+'], file),
        (['the'], file), (['-n', 'INFO'], ROOT / 'target/assembly-data/logs.txt'),
        (['-n', 'ERROR'], ROOT / 'target/assembly-data/logs.txt'),
        (['-n', 'pub fn'], ROOT / 'crates'), (['-n', r'fn\s+\w+'], ROOT / 'crates')]
for options, path in jobs:
    proc = subprocess.run([str(args.binary.resolve()), '--no-config', *options, str(path)],
                          env=env, stdout=subprocess.DEVNULL, check=False)
    assert proc.returncode in (0, 1)
    print(options, 'trained', flush=True)
