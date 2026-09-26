# System rg versus my-grep

The command is now `my-grep`. It is the same tested binary previously named `rg-zen4`; the original JSON and video retain their historical names.

[Specialist summary](../../../MY-GREP-SPECIALIST.md) · [Newer everyday-search article](../../../MY-GREP.md) · [CSV](results.csv) · [Benchmark runner](../../../scripts/assembly/audit_bench.py)

Controlled measurements of the installed executables on this machine. The VHS video is a replay of saved measurements, not a live timing run. Encoding starts after all measurements finish.

The eight workloads were selected before timing: four specialized examples and four ordinary controls. Every result is shown. This does not reproduce a search of `/` and does not establish a general-purpose speedup.

## Method

- CPU: AMD Ryzen 5 7600X 6-Core Processor.
- Both binaries: ripgrep 15.2.0; system package versus the installed experimental build.
- Two sessions, 15 paired rounds each, warmups and reproducibly randomized command order.
- Searches run sequentially; video shows their results side by side.
- Two system-rg controls per round detect baseline instability.
- Fast commands use repeated invocations per batch; reported times are medians of per-invocation batch means. The baseline averages its two controls within each round.
- Identical stdout (directory lines sorted), stderr and exit status checked before timing.
- Timed stdout goes to `/dev/null`; time includes process startup and output processing.
- The text corpus is 128 MiB; all twelve logical CPUs are available.
- No system caches flushed, CPU settings changed, or installed executables modified.
- Interference guard checks every round. Interrupted attempts remain available.
- Directory metadata is compared before and after each completed session; binary and corpus hashes are also recorded.
- A numerical PASS permits the declared margin: a loss must exceed both 3% and 0.10 ms.
- Small measured losses remain visible even when within that margin.
- Per-case 95% bootstrap intervals are not a simultaneous guarantee across all workloads.

## Session A

Raw data: [session-a.json](session-a.json).

| Workload | System rg | my-grep | Time change | Median ratio | 95% elapsed ratio | Interpretation |
|---|---:|---:|---:|---|---|---|
| 30 consecutive letters | 162.898 ms | 15.485 ms | -90.49% | 10.52x faster | 0.0930–0.0984 | Measured improvement (95% interval below parity) |
| Letters + line numbers | 166.532 ms | 18.023 ms | -89.18% | 9.24x faster | 0.1042–0.1096 | Measured improvement (95% interval below parity) |
| 17 hexadecimal digits | 162.912 ms | 15.374 ms | -90.56% | 10.60x faster | 0.0904–0.0987 | Measured improvement (95% interval below parity) |
| 8 consecutive digits | 15.852 ms | 13.966 ms | -11.90% | 1.135x faster | 0.8326–0.9013 | Measured improvement (95% interval below parity) |
| Headers: literal search | 32.378 ms | 31.976 ms | -1.24% | 1.013x faster | 0.9579–1.0019 | INCONCLUSIVE: measurement check flagged this case |
| Kernel: literal search | 90.780 ms | 87.295 ms | -3.84% | 1.040x faster | 0.9337–1.0130 | No clear difference at the 95% interval |
| Text: literal search | 12.515 ms | 12.696 ms | +1.45% | 1.014x slower | 0.9776–1.0802 | No clear difference at the 95% interval |
| Text: count common word | 51.512 ms | 49.043 ms | -4.79% | 1.050x faster | 0.9261–0.9632 | Measured improvement (95% interval below parity) |

Overall audit status: **INCONCLUSIVE**. Interference checks: 122; detections: 0.

## Session B

Raw data: [session-b.json](session-b.json).

| Workload | System rg | my-grep | Time change | Median ratio | 95% elapsed ratio | Interpretation |
|---|---:|---:|---:|---|---|---|
| 30 consecutive letters | 162.414 ms | 15.268 ms | -90.60% | 10.64x faster | 0.0900–0.0976 | Measured improvement (95% interval below parity) |
| Letters + line numbers | 165.885 ms | 17.353 ms | -89.54% | 9.56x faster | 0.1022–0.1064 | Measured improvement (95% interval below parity) |
| 17 hexadecimal digits | 162.922 ms | 14.594 ms | -91.04% | 11.16x faster | 0.0877–0.0979 | Measured improvement (95% interval below parity) |
| 8 consecutive digits | 16.350 ms | 14.339 ms | -12.30% | 1.140x faster | 0.8137–0.9140 | Measured improvement (95% interval below parity) |
| Headers: literal search | 31.108 ms | 31.680 ms | +1.84% | 1.018x slower | 0.9972–1.0284 | No clear difference at the 95% interval |
| Kernel: literal search | 87.053 ms | 85.933 ms | -1.29% | 1.013x faster | 0.9761–1.0109 | No clear difference at the 95% interval |
| Text: literal search | 11.506 ms | 12.087 ms | +5.05% | 1.051x slower | 1.0118–1.0938 | Measured slowdown (95% interval above parity) |
| Text: count common word | 51.085 ms | 48.087 ms | -5.87% | 1.062x faster | 0.9335–0.9638 | Measured improvement (95% interval below parity) |

Overall audit status: **INCONCLUSIVE**. Interference checks: 122; detections: 0.

## Commands using the current name

The measurements used the old `rg-zen4` command name. The commands below use
`my-grep`, which resolves to the same executable; see the [rename receipt](rename.json).
The original invocations remain unchanged in [run-log.json](run-log.json).

### 30 consecutive letters

```bash
/usr/bin/rg --no-config '[A-Za-z]{30}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
/home/gardnmi/.local/bin/my-grep --no-config '[A-Za-z]{30}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
```

### Letters + line numbers

```bash
/usr/bin/rg --no-config -n '[A-Za-z]{30}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
/home/gardnmi/.local/bin/my-grep --no-config -n '[A-Za-z]{30}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
```

### 17 hexadecimal digits

```bash
/usr/bin/rg --no-config -c '[A-Fa-f0-9]{17}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
/home/gardnmi/.local/bin/my-grep --no-config -c '[A-Fa-f0-9]{17}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
```

### 8 consecutive digits

```bash
/usr/bin/rg --no-config -c '[0-9]{8}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
/home/gardnmi/.local/bin/my-grep --no-config -c '[0-9]{8}' /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
```

### Headers: literal search

```bash
/usr/bin/rg --no-config pattern /usr/include
/home/gardnmi/.local/bin/my-grep --no-config pattern /usr/include
```

### Kernel: literal search

```bash
/usr/bin/rg --no-config pattern /home/gardnmi/Projects/ripgrep/target/assembly-readme/linux
/home/gardnmi/.local/bin/my-grep --no-config pattern /home/gardnmi/Projects/ripgrep/target/assembly-readme/linux
```

### Text: literal search

```bash
/usr/bin/rg --no-config pattern /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
/home/gardnmi/.local/bin/my-grep --no-config pattern /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
```

### Text: count common word

```bash
/usr/bin/rg --no-config -c the /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
/home/gardnmi/.local/bin/my-grep --no-config -c the /home/gardnmi/Projects/ripgrep/target/regression-audit/data/subtitles.txt
```

## Provenance

```json
{
  "binaries": {
    "baseline-a": {
      "path": "/usr/bin/rg",
      "sha256": "d006acfe51619144af4709e85945fe3b5a6f05038d356c4d8f752a33b4ecae42"
    },
    "baseline-b": {
      "path": "/usr/bin/rg",
      "sha256": "d006acfe51619144af4709e85945fe3b5a6f05038d356c4d8f752a33b4ecae42"
    },
    "candidate": {
      "path": "/home/gardnmi/.local/lib/ripgrep-zen4/a7be65f27f71/rg",
      "sha256": "a7be65f27f713b0db1761a780a0ac15d92dc2cba39a3555f0d57c12ec6e43422"
    }
  },
  "artifacts": {
    "/home/gardnmi/.local/lib/ripgrep-zen4/a7be65f27f71/rg-class-worker": "03101117059e0e6ec11d5252d931a1164a84aced617392a1508bf7a2dc9dc3f6"
  },
  "manifest_sha256": "3cac837d98cfd527a3777f5fd6d363837252bba962f8481c0b524a4c37e22741"
}
```

Attempt history and directory snapshots: [run-log.json](run-log.json).

The original 112.373 s versus 81.151 s search of `/` remains unexplained by this fixed-corpus experiment. Keep that observation separate from these results.

## Reading the records

Attempts 1 and 3 were interrupted when the guard detected other work; their
samples are retained in [attempt-01.json](attempt-01.json) and
[attempt-03.json](attempt-03.json). Completed attempts 2 and 4 are byte-identical
to session A and B respectively. Logs for all four attempts are included.
No completed unfavorable session was dropped.

The exact commands, random seeds, directory snapshots and executable hashes
are in `run-log.json`. The [manifest](manifest.json) supplies the eight workloads,
input hash and CPU affinity. Paths describe the original machine and must be
adapted to reproduce the experiment elsewhere. The existing
[runner](../../../scripts/assembly/audit_bench.py) and
[protocol](../audit/PLAN.md) document timing and classification.

Both binaries report version 15.2.0, but their build configurations differ:
the system package includes PCRE2; the experimental build does not. None of
these cases requests PCRE2. Ordinary-path timing differences cannot be assigned
solely to the specialized scanner. The earlier
[equally CPU-tuned comparison](../dispatch/README.md) uses a different baseline;
its roughly 11.5–11.7× results should not be substituted into this table.

The locally generated videos are illustrations/replays of these records,
not independent benchmark evidence. No timing work was performed for this
Markdown publication.

## Measurement checks

Session A: 675 timed invocations; 122 interference checks; 0 detections; 414.4 MiB peak memory.

- `directory-headers`: warm-I/O flag=True, unstable-control flag=False.

  Resource counters: `{"baseline-a": {"input_blocks": 0, "major_faults": 0}, "baseline-b": {"input_blocks": 0, "major_faults": 1}, "candidate": {"input_blocks": 0, "major_faults": 0}}`.


Session B: 675 timed invocations; 122 interference checks; 0 detections; 414.4 MiB peak memory.
