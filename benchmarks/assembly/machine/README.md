# Zen 4 machine-specific experiments

This follow-up targets the owner’s AMD Ryzen 5 7600X only. Both the unchanged
upstream baseline and the candidate are compiled with `-C target-cpu=znver4`,
using the same `release-lto` profile. Upstream was fetched again and remained at
`3fce3b5bb0236da2df6d99672afb8a719642eca7` (15.2.0). This is work in the fork only.

## Held-out results

The largest improvement comes from recognizing runs of ASCII character classes
with SIMD. It is a general optimization for eligible parsed expressions, not a
check for the benchmark’s literal pattern text. The full output is checked in
every mode before timing. Times include startup, matching and output formatting;
output is sent to `/dev/null` during timing.

The main subtitle input is a 512 MiB section starting near the 4 GiB offset.
A second 256 MiB section starts near 8 GiB. Neither subtitle section was used
for PGO training. Log inputs are the earlier deterministic corpus and **were**
used for PGO training, so their PGO results are in-sample.

| Workload | Upstream native ms | Upstream + PGO ms | SIMD candidate ms | Candidate + PGO ms | Four workers ms | Six workers ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `[A-Za-z]{30}` | 620.18 | 622.20 | 35.87 | 30.96 | 177.13 | 126.25 |
| `[A-Fa-f0-9]{17}` | 621.60 | 625.19 | 40.16 | 34.82 | 178.39 | 126.53 |
| `[0-9]{8}` | 34.66 | 33.22 | 32.16 | 27.32 | 35.19 | 36.36 |
| sherlock | 23.98 | 23.78 | 24.04 | 24.37 | 34.74 | 34.80 |
| sherlock-lines | 34.45 | 34.40 | 33.05 | 32.48 | 35.58 | 36.54 |
| `the` | 229.96 | 189.54 | 214.79 | 180.29 | 54.85 | 59.81 |
| literal-lines | 34.33 | 32.14 | 33.82 | 32.78 | 37.01 | 36.03 |
| logs-lines | 19.40 | 20.11 | 18.80 | 17.47 | 22.29 | 21.35 |
| logs-dense | 119.06 | 105.40 | 120.84 | 92.22 | 44.15 | 47.63 |
| `[A-Za-z]{30}`, second slice | 315.50 | 315.76 | 22.20 | 19.34 | 93.23 | 67.70 |

Each cell is the median of seven randomized, interleaved trials. Every mode
gets the **same CPU affinity: logical CPUs 0–5**, one hardware thread per physical
core on this machine. The single-threaded builds can run on any of these CPUs;
the parallel modes use 2, 4 or 6 workers. All 700 timed trials had zero major
faults and zero storage input blocks. The 8 GiB benchmark scope recorded no
memory-limit hits or OOM kills.

The four/six-worker columns disable the new class scanner (`RG_CLASS=0`) to
isolate parallel execution. They still use the previous literal/line-count
experiment and a specialized plain-output path. Therefore the frequent-match
gain includes changes to output handling; it is not a pure thread-scaling claim.
The raw results also include the previous assembly control, two-worker mode,
fused scanning, and SIMD plus six workers.

On `alpha30`, the SIMD candidate is 17.288× upstream native throughput; PGO
raises that to 20.034×. Relative to **upstream with PGO**, the latter is about
20.10×. `hex17` improves 15.478× without PGO and 17.849× with it. The second
held-out letter-run slice also improves substantially; see the table and raw
confidence intervals. These are workload-specific gains, not an average for rg.

## Full-file confirmation

The same full **13,113,340,782-byte** OpenSubtitles file was tested with three
randomized timed trials per mode, after output verification and warmup. Both
workloads matched upstream output exactly: **6,749** lines for `[A-Za-z]{30}`
and **83,499,915** lines for `the`. These also match the original README counts.

| Full-file workload | Upstream native s | Upstream + PGO s | Candidate + PGO s | Four workers s | Six workers s |
| --- | ---: | ---: | ---: | ---: | ---: |
| `[A-Za-z]{30}` | 15.689 | 15.655 | 1.164 | 4.724 | 3.542 |
| `the` | 5.849 | 4.953 | 4.709 | 1.696 | 1.772 |

The class scanner with PGO improves full-file letter-run throughput **13.476×**
over upstream native and **13.447×** over upstream with PGO. Four-worker
frequent-match search improves **3.448×** over upstream native and about
**2.920×** over upstream with PGO. The single-threaded PGO candidate takes
about **92.6% less elapsed time** on the letter-run search.

All samples are retained. One upstream-PGO letter-run trial had **1 major fault
and 40 input blocks**; the other 29 timed trials had zero major faults and
input blocks. This is disclosed rather than calling the entire session a strict
zero-I/O benchmark. The primary letter-run comparison (upstream native versus
candidate PGO) has no timed I/O in either mode. The 16 GiB scope had no limit
hits or OOM kills. With only three trials per mode, the full-file run confirms
the large effect rather than estimating small percentage differences precisely.

[Raw full-file samples and resource counters](full-results.json).

## CPU-counter diagnostic

A separate one-core diagnostic on the 512 MiB letter-run input recorded:

| Build | Instructions | CPU cycles |
| --- | ---: | ---: |
| Upstream native | 4,165,539,022 | 3,297,820,833 |
| SIMD candidate native | 810,092,824 | 141,748,912 |
| SIMD candidate + PGO | 650,568,473 | 116,849,928 |

The native scanner executes about **80.6% fewer instructions**, and removes
much of the serial dependency work in the regex state machine. It processes
byte classifications together using SIMD and masks. These are single diagnostic
samples pinned to CPU 4, not replacements for the randomized timing trials.
[Counter data and binary hashes](perf.json) link the measurements to these builds.

## What changed

### SIMD character-class runs

[`ClassRun`](../../../crates/asm/src/class.rs) recognizes a minimum-length run
from up to four ASCII byte ranges. Each AVX-512 load classifies 64 bytes. Bit
intersections find consecutive matching bytes using logarithmically many
shifts, while a carry tracks runs crossing vector boundaries. A scalar tail
handles the final partial vector without reading beyond the slice.

Integration inspects the final regex HIR after flags and word/line transforms.
Only a positive repetition directly over an ASCII class qualifies. Unsupported
patterns keep the existing engine. The optimization supplies a shortest match
for finding matching lines; full match spans and captures still use the normal
engine. Non-ASCII Unicode classes, captures around the repetition, anchors and more
complicated expressions conservatively fall back. The code uses Rust AVX-512
intrinsics, compiled into machine instructions, alongside the earlier handwritten
assembly kernels.

### Parallel search within a file

[`machine.rs`](../../../crates/core/machine.rs) partitions an immutable mapped
file into roughly 1 MiB chunks, ending at newlines. Workers search those chunks
with ripgrep’s matcher/searcher. Bounded channels return line ranges, and the
main thread writes results in original file order. Line-number offsets are
carried between chunks. Output contents are not accumulated for the whole file.

This is an explicit prototype (`RG_PARALLEL=2`, `4` or `6`), not an automatic
default. It requires `--no-config`, one regular file of at least 8 MiB, redirected
output, and a narrow set of ordinary search options. Context, JSON, replacements,
counts, multiline, PCRE2, unsupported flags, binary data, UTF-16 and text-anchored
patterns use the ordinary implementation. A whole-file NUL check occurs before
emitting any output. Chunk boundaries, BOM handling, partial final lines and
broken pipes are covered by differential checks. The same mapped-file mutation
assumption as ripgrep’s mmap path applies.

### Fused literal search and line counting

`RG_FUSED=1` enables one scan that produces literal candidates and counts line
terminators together. It only applies to exact literals with line numbers,
without context or inverted matching. Full literal verification and a bounded
false-candidate fallback remain. A new optional matcher method conveys the
confirmed position and count; ordinary matchers decline it.

### Profile-guided optimization

Both upstream and candidate were separately instrumented, trained and rebuilt
with LLVM 22.1.8 profiles. Both use the fixed workload recipe in
[`machine_train.py`](../../../scripts/assembly/machine_train.py): a 256 MiB
subtitle section, deterministic logs, and source searches. Source training used
the local `crates/` tree during development; that tree had minor edits between
the initial upstream and final candidate profile collections. Subtitle and log
training inputs were unchanged. The held-out subtitle slices are disjoint from
the training slice; the full-file confirmation naturally includes that first
256 MiB. PGO training and compilation are outside measured search time.

PGO adds about 16% throughput to the class scanner on `alpha30` but does not
improve upstream’s same regex case. It also improves dense-output workloads.
That is why the tables show both an optimized upstream baseline and candidate,
rather than attributing compiler improvements to the new scanner.

## What did not work as a broad optimization

- Parallelism makes the already-fast Sherlock search take about 45% longer.
  Chunk setup, the extra binary check and ordered output coordination have a
  cost. It remains an explicit option. Four workers beat six for frequent
  matches on the held-out input.
- Combining SIMD with six workers does not beat the best single-threaded PGO
  scanner on the held-out letter-run workload. The gains cannot simply be
  multiplied together.
- Fused scanning is a small improvement: about 7% over upstream on sparse log
  line-number searches, and about 4.5% over the prior assembly control. It does
  not help the dense-line case. It stays disabled unless requested.
- PGO is workload-dependent. It leaves upstream’s slow letter/hex regexes
  essentially unchanged and slightly regresses some other rows.
- An initial parallel prototype returned exit code 0 on a broken pipe where
  the ordinary single-file path returned 1. The final implementation preserves
  upstream’s behavior and has a differential check for it.

## Validation and artifacts

- Workspace with `experimental-asm`: **1,235 passed, 0 failed, 3 ignored**.
- Six kernel tests include scalar-oracle comparisons for ASCII runs, carries
  through 64/128-byte boundaries, fused counting, false candidates and
  guard-page tests for all four kernels.
- Expanded CLI suite: **1,212 comparisons per build**, run against both native
  and PGO builds, including large files that exercise
  parallelism, chunk boundaries, flags, invalid UTF-8, BOMs, fallback cases and
  fused line numbers. JSON elapsed-time fields are excluded; other output,
  status and stderr must agree. Broken-pipe status is checked separately.
- Original CLI suite: **3,204 comparisons**, including Rust-control and disabled
  modes. Default-feature compilation, formatting and whitespace checks pass.

[Raw held-out samples](heldout-results.json), [new correctness checks](correctness.json),
[PGO correctness checks](correctness-pgo.json),
[original correctness checks](original-correctness.json), [test summary](test-summary.json),
[slice hashes](slices.json), and [build/profile provenance](builds.json).

## Reproduce on this machine

Use the existing full corpus preparation from the
[README workload report](../README-benchmarks.md). Then create the smaller
line-aligned training/evaluation slices and build both source trees:

```sh
python3 scripts/assembly/machine_prepare.py
# Inspect git worktree list first; reuse this worktree if it exists.
git worktree add -b experiment/upstream-control ~/Worktrees/ripgrep/experiment-upstream-control 3fce3b5bb0236da2df6d99672afb8a719642eca7
bash scripts/assembly/machine_build.sh ~/Worktrees/ripgrep/experiment-upstream-control
systemd-run --user --scope --collect -p MemoryMax=8G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/machine_bench.py --samples 7 --output target/machine/heldout-results.json
```

To repeat the full-file confirmation:

```sh
systemd-run --user --scope --collect -p MemoryMax=16G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/machine_bench.py --full --samples 3 --case alpha30 --case frequent --mode upstream-native --mode upstream-pgo --mode class-pgo --mode parallel4 --mode parallel6 --output target/machine/full-results.json
```

The build helper requires `llvm-profdata` matching rustc’s LLVM version and the
earlier deterministic `target/assembly-data` inputs. It uses two build jobs and
8 GiB build scopes. Benchmarks require disk-backed inputs, memory headroom,
no swap in their scope, and the same six physical cores for every mode. The
runner records per-trial I/O and retains any affected samples rather than
selectively removing outliers. No shared-memory corpus copy is used.

Try the optimized binary directly:

```sh
target/machine/rg-candidate-pgo --no-config '[A-Za-z]{30}' FILE
RG_PARALLEL=4 target/machine/rg-candidate-native --no-config the FILE
RG_FUSED=1 target/machine/rg-candidate-native --no-config -n ERROR FILE
```

The feature remains opt-in at build time (`experimental-asm`). Within that
build, the class scanner defaults on (`RG_CLASS=0` disables it); parallelism
and fused scanning require their environment switches. No installed system
`rg` is replaced. Binaries/profiles/corpora stay under ignored `target/`; only
source, scripts and measurements are committed. No upstream PR is opened.
Measurements precede this experiment’s commit, so embedded version revisions
refer to the parent; rebuilding a later commit can change binary hashes.
