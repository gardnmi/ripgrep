#!/usr/bin/env python3
"""Compare traversal/filtering behavior against untouched upstream."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from bench import digest
from machine_check import normalize_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    env = {k: v for k, v in os.environ.items()
           if not k.startswith('RG_') and k not in ('RIPGREP_CONFIG_PATH', 'RUST_LOG')}
    env['LC_ALL'] = 'C.UTF-8'
    checks = []
    with tempfile.TemporaryDirectory(prefix='rg-everyday-check-') as tmp:
        root = Path(tmp)
        (root / '.git').mkdir()
        (root / '.gitignore').write_text('*.tmp\n!keep.tmp\nignored/\n')
        (root / '.ignore').write_text('global-skip.txt\n')
        (root / 'rules').write_text('custom-skip.txt\n')
        for parent in ['src', 'tests', 'nested', 'ignored', '.hidden']:
            for child in ['a', 'b/deep', 'ignored', '東京']:
                directory = root / parent / child
                directory.mkdir(parents=True)
                for name in ['code.rs', 'notes.txt', 'skip.tmp', 'keep.tmp',
                             'global-skip.txt', 'custom-skip.txt', '.secret']:
                    (directory / name).write_text('before\nneedle café 東京\nafter\n')
        (root / 'nested/.git').mkdir()
        (root / 'nested/.gitignore').write_text('notes.txt\n')
        (root / 'tests/.ignore').write_text('!global-skip.txt\n')
        (root / 'src/a/link.rs').symlink_to('code.rs')
        (root / 'src/binary').write_bytes(b'needle\x00tail\n')
        options = [
            ['--files'], ['--files', '--hidden'], ['--files', '-uuu'],
            ['--files', '-g', '*.rs'], ['--files', '-g', '!notes.txt'],
            ['-n', 'needle'], ['-l', 'needle'], ['-i', '-n', 'NEEDLE'],
            ['-C', '1', 'needle'], ['--sort', 'path', 'needle'],
            ['--json', 'needle'], ['--no-ignore-parent', 'needle'],
            ['--no-ignore-vcs', 'needle'], ['-L', '-n', 'needle'],
            ['--ignore-file', str(root / 'rules'), 'needle'],
            ['-q', 'needle'], ['-q', 'absent'], ['-c', 'needle'],
        ]
        for threads in [1, 2, 12, 65]:
            for paths in [[], ['.'], ['nested'], ['src', 'tests']]:
                for flags in options:
                    command = ['--no-config', f'-j{threads}', *flags, *paths]
                    values = []
                    for binary in [args.baseline, args.candidate]:
                        cp = subprocess.run([str(binary.resolve()), *command],
                                            cwd=root, env=env, stdin=subprocess.DEVNULL,
                                            capture_output=True, timeout=20)
                        if '--json' in flags:
                            records = normalize_json(cp.stdout)
                            output = sorted(json.dumps(r, sort_keys=True) for r in records)
                            output = json.dumps(output).encode()
                        else:
                            output = b'\n'.join(sorted(cp.stdout.splitlines()))
                        errors = b'\n'.join(sorted(cp.stderr.splitlines()))
                        values.append((cp.returncode, output, errors))
                    assert values[0] == values[1], (command, [v[:1] for v in values])
                    checks.append(dict(arguments=command, exit=values[0][0],
                                       stdout_sha256=hashlib.sha256(values[0][1]).hexdigest(),
                                       stderr_sha256=hashlib.sha256(values[0][2]).hexdigest()))
    result = dict(result='PASS', comparisons=len(checks),
                  baseline_sha256=digest(args.baseline), candidate_sha256=digest(args.candidate),
                  normalization='Unordered directory output lines/JSON records; JSON elapsed fields removed. Exit and errors compared.',
                  checks=checks)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS:', len(checks), 'directory/flag/thread-count comparisons')


if __name__ == '__main__':
    main()
