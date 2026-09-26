#!/usr/bin/env python3
"""Freeze ordinary-search cases using immutable public source and existing data."""
import argparse
import io
import json
from pathlib import Path
import subprocess
import tarfile

from bench import BASE, ROOT, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--existing-data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / 'manifest.json'
    assert not manifest.exists(), 'Refusing to change a frozen workload matrix'
    source = out / 'source-ripgrep'
    source.mkdir()
    archive = subprocess.check_output(['git', 'archive', BASE], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(source, filter='data')
    subprocess.run(['git', 'init', '-q', str(source)], check=True)
    target = args.existing_data.resolve()
    data = target / 'regression-audit/data'
    kernel = target / 'assembly-readme/linux'
    rows = []

    def add(name, path, flags, category='directory', json_output=False):
        rows.append(dict(name=name, category=category, path=str(path),
                         arguments=['--no-config', *flags, str(path)],
                         directory=path.is_dir(), affinity=list(range(12)),
                         cache='warm', json_output=json_output))

    for name, flags in [
        ('literal', ['-n', 'Searcher']),
        ('absent', ['NOT_PRESENT_XYZ_84921']),
        ('regex', ['-n', r'fn\s+\w+']),
        ('ignore-case', ['-i', '-l', 'error']),
        ('glob', ['-g', '*.rs', '-n', 'TODO']),
        ('files', ['--files']),
        ('files-hidden', ['--hidden', '-g', '!.git', '--files']),
        ('multi', ['-n', '-e', 'TODO', '-e', 'FIXME']),
        ('context', ['-C', '2', 'Searcher']),
        ('sorted', ['--sort', 'path', '-n', 'Searcher']),
        ('explicit-one-thread', ['-j1', '-n', 'Searcher']),
    ]:
        add('source-' + name, source, flags)
    for name, flags in [
        ('literal', ['-n', 'TODO']),
        ('files-with-match', ['-l', 'pthread_create']),
        ('glob', ['-g', '*.c', '-n', 'epoll_ctl']),
        ('regex', ['-n', r'pthread_(create|join)']),
        ('files', ['--files']),
    ]:
        add('tools-' + name, kernel / 'tools', flags)
    for name, flags in [
        ('literal', ['pattern']),
        ('regex', ['-n', '-w', '[A-Z]+_SUSPEND']),
        ('files', ['--files']),
    ]:
        add('kernel-' + name, kernel, flags)
    for name, file, flags in [
        ('tiny-hit', 'tiny.txt', ['abc']),
        ('tiny-miss', 'tiny.txt', ['absent']),
        ('small-regex', 'small.txt', [r'user=\d+']),
        ('log-lines', 'mixed.txt', ['-n', 'RARE_MARK']),
        ('log-context', 'mixed.txt', ['-C', '2', 'RARE_MARK']),
        ('log-count', 'mixed.txt', ['-c', 'status=500']),
        ('log-multi', 'mixed.txt', ['-c', '-e', 'RARE_MARK', '-e', 'status=500']),
        ('log-ignore-case', 'mixed.txt', ['-i', '-c', 'NORMAL']),
        ('log-json', 'json.txt', ['--json', 'RARE_MARK']),
        ('prose-absent', 'subtitles.txt', ['NOT_PRESENT_XYZ_84921']),
        ('prose-count', 'subtitles.txt', ['-c', 'the']),
        ('prose-regex', 'subtitles.txt', ['-n', '-w', r'Sherlock [A-Z]\w+']),
        ('unicode-fold', 'unicode.txt', ['-i', '-c', 'café']),
    ]:
        add(name, data / file, flags, 'single-file', name == 'log-json')
    inputs = sorted({Path(r['path']) for r in rows if not r['directory']})
    result = dict(cases=rows,
                  inputs={str(p): dict(bytes=p.stat().st_size, sha256=digest(p))
                          for p in inputs},
                  source_revision=BASE,
                  source_archive_sha256=__import__('hashlib').sha256(archive).hexdigest(),
                  kernel_revision=subprocess.check_output(
                      ['git', '-C', str(kernel), 'rev-parse', 'HEAD'], text=True).strip(),
                  notes='Logs and tiny inputs are synthetic; source and prose are real. '
                        'Corpora were used in previous experiments, not newly held out.')
    manifest.write_text(json.dumps(result, indent=2) + '\n')
    print(len(rows), 'cases; manifest SHA256', digest(manifest))


if __name__ == '__main__':
    main()
