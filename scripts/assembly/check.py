#!/usr/bin/env python3
"""Compare exact CLI output/status with untouched upstream on adversarial inputs."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile

from bench import MODES, digest, environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    baseline, candidate = args.baseline.resolve(), args.candidate.resolve()
    rng = random.Random(32941)
    checks = []
    datasets = [
        b'', b'ERROR', b'ERROR\r\nINFO\r\n', b'hello\x00ERROR\x00world\x00',
        b'\xff\xfeERROR\xf0\x80\x80\x80\nhello\xffworld\n',
        'hello café 東京 καλημέρα\nHELLO CAFÉ\nStraße STRASSE\n'.encode() * 100,
        (b'a' * 63 + b'b') * 2048 + b'a' * 64,
        b'a' * (1024 * 1024) + b'ERROR',
        b'ERROR' + b'a' * (1024 * 1024),
        b'one\ntwo\nthree\r\n\x00ERROR\nInfo\nINFO hello 123\n' * 200,
        b''.join(bytes([rng.randrange(256)]) for _ in range(8192)),
        ''.join(rng.choice(['ERROR\n', 'INFO\n', 'hello ', 'world\r\n',
                            '東京', 'café\n', 'a' * 63 + '\n', '\x00'])
                for _ in range(4000)).encode(),
    ]
    patterns = [
        '', 'ERROR', 'INFO', 'ER', 'hello', '東京', 'café', 'καλημέρα',
        'a' * 64, 'a' * 65, 'a' * 66, 'a', '(ERROR)', 'ERROR|INFO',
        r'\bERROR\b', '^ERROR$', 'E.ROR', r'\x00', r'(?-u:\xff)',
        'ERROR.*', 'one\ntwo', 'hello.*world', '[A-Z]+', r'\pL+',
        r'(hello) (world)', 'notpresentneedle', 'Straße', 'STRASSE',
    ]
    flags = [
        [], ['-n'], ['-c'], ['-o', '-b', '-n'], ['-F', '-n'], ['-i', '-n'],
        ['-S'], ['-w'], ['-x'], ['-v', '-n'], ['-C', '2', '-n'],
        ['-a', '-n'], ['--crlf', '-n'], ['--null-data', '-n'],
        ['-U', '--multiline-dotall', '-n'], ['--no-unicode', '-a'],
        ['--replace', '$1'], ['--passthru'], ['--count-matches'],
        ['--column', '--color', 'always'], ['-q'], ['-m', '2', '-n'],
    ]
    for i, data in enumerate(datasets):
        for pattern in patterns:
            checks.append((f'matrix-{i}-{len(checks)}', data, pattern, rng.choice(flags)))
    # Deliberately hit vector and prefix transitions, including complete literals
    # that straddle the 256-byte prefix and every possible needle length.
    for length in range(1, 67):
        needle = ('XYZabcdefghijklmnop' * 4)[:length]
        for offset in (0, 31, 63, 64, 127, 255, 256, 257, 511, 512, 1023):
            data = b'\n.' * (offset // 2) + b'.' * (offset % 2) + needle.encode()
            data += b'\n' + needle.encode() + b'\n'
            checks.append((f'boundary-{length}-{offset}', data, needle, ['-F', '-n', '-b', '-o']))
    # Repetitive false positives must fall back without skipping a real match.
    for length in (2, 3, 31, 32, 63, 64):
        needle = 'a' * length
        data = (b'a' * (length - 1) + b'b') * 10000 + needle.encode()
        checks.append((f'adversarial-{length}', data, needle, ['-n', '-o', '-b']))
    aggregate = hashlib.sha256()
    comparisons = 0
    with tempfile.TemporaryDirectory(prefix='rg-assembly-check-') as directory:
        file = Path(directory) / 'input'
        for name, data, pattern, options in checks:
            file.write_bytes(data)
            command = ['--no-config', '-j1', *options, '-e', pattern, str(file)]
            ref = subprocess.run([str(baseline), *command], env=environment('baseline'),
                                 capture_output=True, timeout=15)
            expected = (ref.returncode, ref.stdout, ref.stderr)
            for mode in MODES[1:]:
                got = subprocess.run([str(candidate), *command], env=environment(mode),
                                     capture_output=True, timeout=15)
                actual = (got.returncode, got.stdout, got.stderr)
                if actual != expected:
                    raise AssertionError((name, mode, options, pattern,
                                          'baseline', expected, 'candidate', actual))
                comparisons += 1
            aggregate.update(name.encode())
            aggregate.update(data)
            aggregate.update(json.dumps([pattern, options]).encode())
    report = {
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'seed': 32941, 'cases': len(checks), 'comparisons': comparisons,
        'case_digest_sha256': aggregate.hexdigest(), 'result': 'PASS',
        'checks': 'exact stdout, stderr and exit status; assembly, Rust control and disabled',
        'baseline_sha256': digest(baseline), 'candidate_sha256': digest(candidate),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
