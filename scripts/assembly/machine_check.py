#!/usr/bin/env python3
"""Check the machine-specific experiments against unchanged upstream output."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def normalize_json(output):
    def clean(value):
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items() if k not in ('elapsed', 'elapsed_total')}
        if isinstance(value, list):
            return [clean(v) for v in value]
        return value
    return [clean(json.loads(line)) for line in output.splitlines()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rng = random.Random(41928)
    env = {k: v for k, v in os.environ.items() if not k.startswith('RG_') and k != 'RIPGREP_CONFIG_PATH'}
    env['LC_ALL'] = 'C.UTF-8'
    modes = [{}, {'RG_FUSED': '1'}, {'RG_PARALLEL': '6'}, {'RG_PARALLEL': '2', 'RG_FUSED': '1'}]
    count = 0
    digest = hashlib.sha256()
    with tempfile.TemporaryDirectory(dir=ROOT / 'target', prefix='machine-check-') as tmp:
        path = Path(tmp) / 'input'

        def check(data, pattern, flags):
            nonlocal count
            path.write_bytes(data)
            command = ['--no-config', *flags, pattern, str(path)]
            ref = subprocess.run([str(args.baseline.resolve()), *command], env=env, capture_output=True, timeout=30)
            for mode in modes:
                got = subprocess.run([str(args.candidate.resolve()), *command], env=env | mode, capture_output=True, timeout=30)
                expected = normalize_json(ref.stdout) if '--json' in flags else ref.stdout
                actual = normalize_json(got.stdout) if '--json' in flags else got.stdout
                assert (ref.returncode, expected, ref.stderr) == (got.returncode, actual, got.stderr), (pattern, flags, mode, ref.returncode, got.returncode, ref.stdout[:200], got.stdout[:200], got.stderr[:200])
                count += 1
            digest.update(data); digest.update(json.dumps([pattern, flags]).encode())

        flags = [[], ['-n'], ['-c'], ['-o', '-b', '-n'], ['-v'], ['-w'], ['-x'], ['-i'], ['--crlf'], ['--null-data'], ['-U'], ['-C', '2'], ['--replace', 'X'], ['--json']]
        for pattern in ['[A-Za-z]{30}', '[A-Z]{2,65}', '[A-Z]{2,65}?', '[0-9]+', '[0-9]{65}', '[A-Fa-f0-9]{17}', '(?-u:[a-z]{3})', '[a-z]{0,5}', '[a-z]{3}|foo', '([a-z]{3})', '[a-z]{129}', r'\w{30}', r'(?i:[a-z]{30})']:
            for trial in range(18):
                data = bytes(rng.randrange(256) for _ in range(129))
                data += b'\n' + b'A' * trial + b'1234567890'*15 + b'\n'
                data += b'x'*trial + b'a' * 129 + b'\r\n' + b'A'*30
                check(data, pattern, flags[trial % len(flags)])
        # Large text forces the parallel path. Matches straddle proposed chunk
        # boundaries, the last line is unterminated, and BOMs occur inside data.
        data = bytearray((b'ordinary line 0123\n' * 600000)[:9*1024**2])
        for boundary in range(1024*1024, len(data), 1024*1024):
            data[boundary-15:boundary+20] = b'\n' + b'A'*30 + b'\nXYZ'
        data += b'\n\xef\xbb\xbfembedded BOM\n' + b'A'*129
        for pattern in ['[A-Za-z]{30}', '[0-9]{3}', 'ordinary', 'XYZ', r'^A+$', r'\AA', r'(?-m:^ordinary)', r'A\z', '', 'absent', r'\bXYZ\b']:
            for opts in [[], ['-n']]:
                check(data, pattern, opts)
        for prefix in [b'\xef\xbb\xbf', b'\xff\xfe', b'\x00', b'\xff\x80']:
            check(prefix + data, '[A-Za-z]{30}', ['-n'])
        for opts in [['-C', '2'], ['--json'], ['--crlf'], ['-o'], ['-c'], ['-v'], ['-m', '2'], ['-U']]:
            check(data, 'XYZ', opts)
        # Fused literal search: counts before/after matches and context fallback.
        for length in [2, 3, 31, 63, 64]:
            needle = ('abcDEF' * 11)[:length]
            for offset in [0, 63, 64, 255, 256, 257, 4095]:
                text = b'\n.' * offset + needle.encode() + b'\n' + needle.encode()
                check(text, needle, ['-n'])
    pipe_results = []
    for binary in [args.baseline, args.candidate]:
        proc = subprocess.Popen([str(binary.resolve()), '--no-config', 'the', str(ROOT/'target/machine/heldout.txt')],
                                env=env | {'RG_PARALLEL': '6'}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdout.read(64); proc.stdout.close()
        pipe_results.append((proc.wait(timeout=15), proc.stderr.read()))
    assert pipe_results[0] == pipe_results[1], pipe_results
    result = {'result': 'PASS', 'comparisons': count, 'case_sha256': digest.hexdigest(),
              'broken_pipe_exit': pipe_results[0][0],
              'comparison': 'Exact exit status, stderr and stdout; JSON elapsed/elapsed_total fields excluded.',
              'baseline_sha256': hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
              'candidate_sha256': hashlib.sha256(args.candidate.read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
