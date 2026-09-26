# Regression audit: acceptance rejected

The large ASCII-class speedup is real on eligible searches. It does **not** make
the experimental binary a generally faster replacement for ripgrep. The broader
audit finds slowdowns in ordinary searches, even after separating the class
scanner from the older experiments. Keep upstream for general use.

The experiment remains behind explicit, non-default Cargo features. No installed
`rg` is replaced, no experiment is promoted, and no upstream PR is opened.

## What this audit changes

- Adds `experimental-class`, enabling only the class-scanner integration. The
  literal/count assembly, fused scanning and parallel CLI path are excluded.
  Isolation alone did not eliminate regressions. This is a diagnostic build,
  not an approved replacement.
- Freezes [81 workloads and input hashes](manifest.json) before collecting
  measurements, under a [predeclared protocol](PLAN.md). Ordinary commands,
  output options, directory searches, Unicode, binary input, tiny files, long
  lines, and unfavorable class patterns are included. No slow case is removed.
- Uses two identical upstream controls, randomized paired rounds, and the same
  compiler settings for both sides. No PGO is used in the primary comparison.
- Adds a [machine-readable acceptance gate](../../../scripts/assembly/audit_gate.py).
  Measured regressions return exit status 1; incomplete or inconclusive evidence
  returns 2. Only two complete passing sessions can return 0. A large gain never
  compensates for a failing case.
- Marks earlier benchmark reports as experimental evidence, not acceptance.

## Results

See [every workload, median change and confidence interval](RESULTS.md), including
small median slowdowns below the practical margin. Raw observations are in
[discovery](discovery.json), [session A](session-a.json) and [session B](session-b.json).
Discovery uses 9 rounds; A and B each use 15, with distinct seeds and reversed
case order. The candidate binary is unchanged across all three runs.

**Gate result: REJECT (exit status 1).** Session A: 57 PASS, 2 FAIL,
22 INCONCLUSIVE. Session B: 53 PASS, 5 FAIL, 23 INCONCLUSIVE.

| Workload | Session A upstream → candidate | A change | Session B upstream → candidate | B change |
| --- | ---: | ---: | ---: | ---: |
| literal-count | 13.884 → 14.940 ms | +7.61% | 14.530 → 15.511 ms | +6.75% |
| literal-only-offset | 40.077 → 43.959 ms | +9.69% | 41.707 → 46.535 ms | +11.57% |
| subtitles-alpha30 | 159.647 → 14.015 ms | -91.22% | 160.468 → 13.354 ms | -91.68% |
| subtitles-hex17 | 159.806 → 14.658 ms | -90.83% | 161.198 → 15.345 ms | -90.48% |

Both ordinary-search losses fail independently in both sessions. The letter-run
case remains 11.39× and 12.02× faster, respectively. That narrow win cannot
offset those regressions. Session B additionally fails dense literal output,
anchored regex counting and Unicode literal counting; those cases are
inconclusive in A and are not described as failing in both.

Across discovery and the two confirmation sessions, 10,206 timed batches cover
64,692 process invocations. Every sample is retained. One candidate batch in
`subtitles-digits8` in B has 1 major fault and 24 input blocks, so that case is
inconclusive despite its faster median. All other timed warm-cache batches have
zero major faults and input blocks. Neither session has a failing baseline
control comparison; both have cases whose candidate intervals remain too wide
to establish the chosen bound. All three scopes record zero memory-limit hits
and zero OOM kills.

The earlier all-experiment native binary is also measured during discovery.
Its whole-word literal case fails the preset margin, about 4.9% slower. Its other
selected wins do not cancel that regression. Parallel and PGO modes are excluded
from the primary audit, so it makes no acceptance claim for them. The earlier
parallel prototype's measured Sherlock regression remains documented in the
[previous report](../machine/README.md).

Slowdowns also occur on expressions that do not use the class shortcut. The
audit measures the complete executable, including integration and generated-code
effects. It does not establish which branch, layout change or instruction causes
each loss. No speculative fix is presented as verified.

## Fairness and limits

Upstream is `3fce3b5bb0236da2df6d99672afb8a719642eca7` (15.2.0), rechecked with
`git fetch upstream master` before the audit. The existing native control is
reused by recorded hash. Both builds use rustc 1.98.1 / LLVM 22.1.8,
`--profile release-lto` and `-C target-cpu=znver4`, without PGO or PCRE2. The host
is the owner's Ryzen 5 7600X, kernel 7.2.5-3-omarchy. This is a comparison on this
machine, not against another computer's published timings.

Single-file tests use CPU 4. Parallel directory searches get physical-core
threads 0–5 in both builds; the sorted directory case uses CPU 4. Output is
redirected to `/dev/null` during timing. Startup and formatting are included;
terminal rendering is not. Short-command batching is chosen from upstream only.

The practical tolerance is **3% AND 0.10 ms per invocation**, chosen before
measurement. A per-case paired-bootstrap 95% interval wholly beyond both
margins fails; an upper bound within either margin passes; other cases are
inconclusive. These are per-case intervals, not familywise confidence across
81 tests. Repeat sessions help distinguish repeatable losses from noise. Raw
baseline-control comparisons and all samples remain available. No averaging
across workloads or deletion of outliers turns a failure into a pass.

Warm-cache I/O and materially unstable controls prevent a pass. Cold-I/O cases
evict only a dedicated disk file via `posix_fadvise`; the global cache is not
dropped. All runs use bounded 8 GiB scopes, no swap, and disk-backed corpora.
There are no shared-memory corpus copies. Compilation and correctness suites
run separately from timed measurements.

Synthetic data is explicitly identified in the generator. The real-text case
uses a new 128 MiB line-aligned subtitle section near offset 6 GiB, excluded
from prior training and held-out performance slices. Source-tree and kernel
searches use the existing prepared trees; their source revisions are recorded
in the manifest. No finite suite guarantees that every possible input avoids
regression, even if it passes this gate. This candidate does not pass it.

## Correctness

Benchmark verification compares exit status, stdout and stderr before timing.
Directory lines are sorted for comparison because traversal order is unspecified.
JSON output excludes only nondeterministic elapsed-time fields.

The class-only build passes **1,235 workspace/unit/doc tests**, with 3 ignored,
and **4,416 additional CLI comparisons** (3,204 original suite + 1,212 expanded
suite). Some environment modes are equivalent in a class-only build, so these
comparison counts are not distinct workloads. Broken-pipe behavior also agrees.

[Test summary](test-summary.json), [original differential checks](original-correctness.json),
and [expanded differential checks](machine-correctness.json).

Default workspace compilation, compilation with both experimental features,
formatting, whitespace checks and Python script compilation pass.

Correctness passing cannot override a performance failure.

## Reproduction

Prepare the existing disk corpora using the earlier
[README-workload instructions](../README-benchmarks.md), then run
`python3 scripts/assembly/audit_prepare.py`. Compare the generated manifest to
the recorded one before reusing these results. The committed paths target this
owner's checkout; other paths produce a different manifest and a new audit.

Use `git worktree list` and reuse a clean upstream worktree when available.
If creation is needed, use `~/Worktrees/ripgrep/<branch-slug>`. Build upstream
without experimental features and the candidate with `experimental-class`,
using identical native flags and `release-lto`, two build jobs, and separate
target directories. The recorded candidate was built from parent `e9937cb523`
plus this commit's feature-isolation changes; a later rebuild can have a
different hash because the revision is embedded in the executable.

Example candidate build from the fork root:

```sh
systemd-run --user --scope --collect -p MemoryMax=8G -p MemorySwapMax=0 -p OOMPolicy=kill env -u CARGO_ENCODED_RUSTFLAGS CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR=target/audit-candidate RUSTFLAGS='-C target-cpu=znver4' cargo build --locked --profile release-lto --features experimental-class
cp target/audit-candidate/release-lto/rg target/regression-audit/rg-class-initial
```

Run the sessions sequentially, with builds and other benchmarks stopped:

```sh
systemd-run --user --scope --collect -p MemoryMax=8G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/audit_bench.py --candidate target/regression-audit/rg-class-initial --output target/regression-audit/session-a.json --samples 15 --seed 417225
systemd-run --user --scope --collect -p MemoryMax=8G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/audit_bench.py --candidate target/regression-audit/rg-class-initial --output target/regression-audit/session-b.json --samples 15 --seed 931607 --reverse
python3 scripts/assembly/audit_gate.py target/regression-audit/session-a.json target/regression-audit/session-b.json
python3 scripts/assembly/audit_report.py target/regression-audit/session-a.json target/regression-audit/session-b.json --output target/regression-audit/RESULTS.md
```

The runner preserves failed results and exits normally after collecting them;
the separate **gate's exit status** decides acceptance. Do not promote a binary
merely because benchmark collection completed successfully.

The scripts, protocol, inputs and binaries have recorded hashes. Retain failed
sessions when testing a future fix; rerun the entire matrix for the new binary.
