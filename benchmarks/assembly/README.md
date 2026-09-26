# ripgrep assembly experiment

**Acceptance status: experimental; not a validated replacement for upstream.**
The later [regression audit](audit/README.md) tests a frozen, broader workload
matrix and rejects builds with material slowdowns. Selected wins below do not
establish that ordinary searches avoid regressions.

The latest [Zen 4 machine-specific experiments](machine/README.md) add a SIMD
character-class scanner, bounded single-file parallelism, fused scanning and
PGO comparisons. That report records substantially larger gains on selected
workloads and the cases where these approaches regress.

This fork adds two handwritten Linux x86-64 AVX-512 kernels behind the
`experimental-asm` feature. It is a hybrid Rust/assembly experiment, not a full
assembly port. On the tested Ryzen 5 7600X, sparse log searches with line numbers
ran at **1.136–1.167× upstream throughput** across two benchmark sessions.
Frequent-match counts improved **1.104–1.161×**, but the Rust-only control explains
most of those gains. General regex and no-match workloads showed no consistent
improvement.

The [upstream README benchmark follow-up](README-benchmarks.md) uses the full
13 GB OpenSubtitles corpus and a built Linux kernel tree, against the latest
upstream source verified for that run. It reports a separate workload set and
documents the resource-management problems encountered during preparation.

The implementation, tests, and this report were produced with Codex at the fork
owner's request. This work stays in `gardnmi/ripgrep`; it is not an upstream
contribution or a claim of endorsement. Upstream's [contribution guidelines](../../CONTRIBUTING.md)
and [AI policy](../../AI_POLICY.md) were read before proceeding.

## What changed

- [New assembly crate](../../crates/asm/src/lib.rs), unpublished and optional.
  Runtime checks require Linux x86-64, AVX-512F, AVX-512BW, and POPCNT, including
  OS support through Rust's feature detection. Unsupported hosts keep upstream's
  implementation. The default build does not enable the experiment.
- [Byte-count kernel](../../crates/asm/src/x86_64.s): compare 64 bytes at a time,
  turn equality masks into counts with POPCNT, and process four vectors per main
  loop. This accelerates counting skipped line terminators for line numbers.
  Slices shorter than 256 bytes keep the existing counter.
- [Literal candidate kernel](../../crates/asm/src/x86_64.s): check two selected
  byte positions in 64 potential matches at once. Selection reuses memchr's
  frequency heuristic. A four-vector loop amortizes branches on long scans.
  Rust checks the complete literal before accepting a match. After 16 rejected
  candidates, the existing memmem finder handles the remainder.
- [Matcher integration](../../crates/regex/src/matcher.rs): only use the shortcut
  when the final parsed expression, after flags and word/line transformations,
  is exactly one literal of 2–64 bytes. General regexes and capture operations
  use the existing engine. Search the first 256 bytes with memmem, then enter
  the assembly scanner; retain an overlap of `needle length - 1` bytes.

In plain terms, the kernels examine a large group of characters together and
quickly count or reject possibilities. The Rust shortcut also avoids some regex
engine dispatch when the pattern is just a string. Those are separate sources
of improvement.

The assembly uses only SysV caller-saved registers. Full-width loads are issued
only when they fit the supplied slice; masked loads handle tails. Candidate
positions account for the full needle length. Zero bytes outside the valid
mask cannot count as matches. Full-literal verification and the bounded fallback
protect correctness on repetitive input.

Rust's [`global_asm!`](https://doc.rust-lang.org/reference/inline-assembly.html)
embeds the `.s` file; no NASM dependency is needed. The baseline already has
optimized SIMD searching through [memchr 2.8.3](https://docs.rs/memchr/2.8.3/memchr/),
including runtime AVX2 support. This is not a comparison with scalar Rust.

## Measurements

Both binaries use the same upstream `release-lto` profile: optimization level 3,
fat LTO, one codegen unit, stripped symbols, and abort-on-panic. No `RUSTFLAGS` or
`target-cpu=native` were used. The baseline is untouched upstream commit
`3fce3b5bb0236da2df6d99672afb8a719642eca7` (ripgrep 15.2.0).

Hardware and conditions:

- AMD Ryzen 5 7600X, **Zen 4**; Linux 7.2.3-arch1-3, glibc 2.44.
- rustc 1.98.1, LLVM 22.1.8, x86_64-unknown-linux-gnu.
- Warm page cache; process and inherited children pinned to logical CPU 4;
  `--no-config -j1`; output directed to `/dev/null` during timing.
- Wall time includes process startup and file handling. Two warmups per mode,
  then 30 randomized, interleaved rounds per case. A second session reverses
  case order and uses a different random seed. No compilation or test jobs ran
  during either timing session. Normal desktop processes remained active.
- Before timing, all four modes must produce identical stdout, stderr and exit
  status on each benchmark case.

The table contains **run 1 median milliseconds** and throughput ratios for both
runs. A ratio above 1 is faster. For example, 1.136× means 13.6% more throughput,
or approximately 12% less elapsed time. The Rust control is the same candidate
binary with the same literal shortcut and prefix strategy, but memchr kernels.

| Workload | Upstream ms | Assembly ms | Rust control ms | Run 1 ratio | Run 2 ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `logs-sparse-lines` | 13.889 | 12.230 | 13.985 | 1.136× | 1.167× |
| `logs-sparse-count` | 10.056 | 9.903 | 9.740 | 1.015× | 0.990× |
| `logs-dense-count` | 46.871 | 42.335 | 42.199 | 1.107× | 1.104× |
| `logs-short-count` | 50.393 | 43.400 | 43.398 | 1.161× | 1.134× |
| `logs-absent` | 9.388 | 8.925 | 8.816 | 1.052× | 0.968× |
| `logs-regex` | 24.146 | 24.012 | 24.031 | 1.006× | 0.997× |
| `cached-sparse-lines` | 1.947 | 1.777 | 1.918 | 1.095× | 1.132× |
| `source-literal` | 5.340 | 4.703 | 5.346 | 1.136× | 1.112× |
| `source-regex` | 9.135 | 9.172 | 9.194 | 0.996× | 0.998× |
| `source-absent` | 3.346 | 3.258 | 3.285 | 1.027× | 1.027× |
| `source-tree` | 2.498 | 2.461 | 2.457 | 1.015× | 1.051× |
| `small-file` | 1.245 | 1.185 | 1.173 | 1.051× | 1.048× |
| `long-line` | 2.352 | 2.359 | 2.263 | 0.997× | 0.998× |
| `adversarial` | 1.267 | 1.220 | 1.209 | 1.038× | 1.019× |
| `unicode` | 2.106 | 1.944 | 2.067 | 1.083× | 1.162× |

Inputs are deterministic and generated by [bench.py](../../scripts/assembly/bench.py).
The log file is 219,023,904 bytes (about 209 MiB), with rare `ERROR` records,
frequent `INFO` records, and a fixed field layout. The cached subset is 16 MiB.
The source-text file is 64 MiB made by repeating the **unmodified upstream Rust
sources**, while `source-tree` searches the original 108 individual `.rs` files.
Additional inputs cover a 4 KiB file, a 16 MiB line, 1 MiB of repetitive false
candidates, and about 15.6 MiB of UTF-8 text. Exact arguments, input hashes,
binary hashes, all samples, disabled-mode results, and bootstrap intervals are
in [run 1](zen4-run1.json) and [run 2](zen4-run2.json).

Interpretation:

- Sparse log searches with line numbers improved in both sessions. Run 1's
  95% paired-bootstrap interval was 1.105–1.172×; run 2's was 1.131–1.205×.
  The Rust control stays much closer to upstream here, supporting an assembly
  benefit. The much smaller change without line numbers suggests the line
  counter is a substantial contributor; this is an inference, not a separate
  isolation of the two assembly kernels.
- Frequent-match counts improved consistently, but the Rust control is equally
  fast. Credit the literal matcher shortcut and memmem prefix here, rather
  than claiming AVX-512 caused the entire improvement.
- Source-text searches with line numbers improved by median estimates of
  11–14%. The second session was noisy: its interval spans 0.962–1.276×, so the
  exact size of this benefit is less certain. The ordinary source-tree search
  changed much less; a repeated 64 MiB source file is a distinct workload.
- No-match log searches changed from 1.052× to **0.968×** across sessions: no
  repeatable win, with a regression in the second median. General regex and
  the long-line case were essentially unchanged. Tiny-file differences also
  appear in disabled mode and should not be credited to assembly.
- There is no representative-workload weighting or universal average speedup.
  Bootstrap intervals describe sampling uncertainty on this host, not other
  machines or workloads. These are not Zen 5, Intel, cold-cache, disk-throughput,
  or multicore measurements. No hardware performance counters were available.

The LTO binary grew from 3,865,768 to 3,879,928 bytes: **14,160 bytes (0.37%)**.
The measured binary hashes are recorded in the JSON files. Measurements were
made before the experiment commit, so their embedded `--version` revision is
still the upstream base; rebuilding a later commit changes that version string
and can change the binary hash.

## What did not work, and what was retained

1. **Using the AVX-512 candidate scanner for every literal lookup.** In an
   exploratory LTO comparison, dense `INFO` counting took 38.745 ms with the
   assembly scanner versus 36.596 ms with the Rust control. Short `us` matching
   took 45.467 versus 40.943 ms. The existing finder has lower overhead for close
   matches. The retained implementation searches a 256-byte prefix with memmem
   before entering the assembly streaming scan. Those exploratory figures are
   notes, not part of the final raw-sample dataset.
2. **Widening and unrolling alone as a guaranteed speedup.** Moving the candidate
   loop from 64 to 256 positions per iteration produced mixed exploratory
   results. The unrolled version is retained, but no independent speedup is
   claimed for it. Final end-to-end results measure the complete implementation.
3. **Claiming a faster no-match scanner from one run.** The apparent gain did
   not reproduce in the second session. The existing AVX2 implementation is
   already strong; these results do not establish why the no-match case is
   limited, or show that assembly removes that limit.
4. **Treating integration gains as assembly gains.** `RG_ASM=rust` exposed this
   mistake early. The control remains available so future changes can be
   evaluated against it as well as against untouched upstream.

Only the two hot paths above were ported. A replacement regex engine, filesystem
walker, output layer, and full assembly executable were not implemented.

## Correctness and checks

[validation.json](validation.json) records the test commands and totals:

| Configuration | Passed | Failed | Ignored |
| --- | ---: | ---: | ---: |
| Default workspace | 1,233 | 0 | 3 |
| Assembly + PCRE2 workspace | 1,233 | 0 | 3 |
| Assembly + experimental indexing workspace | 1,249 | 0 | 3 |

These counts overlap between configurations; they are not distinct test totals.
Formatting, `git diff --check`, and workspace documentation with warnings treated
as errors also passed.

The four new [kernel tests](../../crates/asm/src/tests.rs) cover 262,144 byte-count
combinations, 12,000 randomized literal cases against a scalar oracle,
adversarial fallback behavior, and input placed against inaccessible guard
pages. Guard-page cases exercise every length from 0 through 512 at both ends
of a readable page. The native host supports the required instructions, so these
checks executed the assembly instead of being skipped.

[check.py](../../scripts/assembly/check.py) additionally compares **1,068 CLI
cases in three modes: 3,204 exact comparisons**, all passing; see
[correctness.json](correctness.json). Cases include vector/prefix boundaries,
needle lengths through 66, invalid UTF-8, Unicode, NUL, CRLF, binary data,
repetitive candidates, long lines, match offsets, context, inversion,
replacement, case flags, multiline options, and errors. The benchmark harness
also checks output parity for each of its 15 cases.

An initial test invocation combined PCRE2 and experimental indexing and had
15 failures: indexing tests tried `--x-crud` while the PCRE2 test mode added
`--pcre2`. The separate feature configurations used by upstream CI both pass.
The combined configuration is **not** reported as passing, and no unrelated
indexing behavior was changed. Other operating systems, non-AVX-512 CPUs,
cross compilation, and the minimum Rust version were not tested here. Runtime
`RG_ASM=0` was tested as a fallback control on the current machine.

## Build and reproduce

To try this branch locally:

```sh
cargo build --profile release-lto --locked --features experimental-asm
./target/release-lto/rg -n ERROR example.log
```

The feature is off unless explicitly requested. In an enabled build, the default
mode uses assembly only on a supported host. `RG_ASM=0` disables the experimental
paths; `RG_ASM=rust` retains the integration but uses memchr. The environment mode
is read once per process. No existing installed `rg` is replaced.

For a fresh, isolated reproduction checkout:

```sh
git clone --branch experiment/assembly-hotpaths https://github.com/gardnmi/ripgrep ripgrep-assembly
cd ripgrep-assembly
git switch --detach 3fce3b5bb0236da2df6d99672afb8a719642eca7
env -u RUSTFLAGS -u CARGO_ENCODED_RUSTFLAGS CARGO_BUILD_JOBS=2 cargo build --profile release-lto --locked
cp target/release-lto/rg target/rg-original-lto
git switch experiment/assembly-hotpaths
env -u RUSTFLAGS -u CARGO_ENCODED_RUSTFLAGS CARGO_BUILD_JOBS=2 cargo build --profile release-lto --locked --features experimental-asm
cp target/release-lto/rg target/rg-assembly-lto

python3 scripts/assembly/check.py --baseline target/rg-original-lto --candidate target/rg-assembly-lto --output target/assembly-check.json
python3 scripts/assembly/bench.py --baseline target/rg-original-lto --candidate target/rg-assembly-lto --cpu 4 --samples 30 --output target/assembly-run1.json
python3 scripts/assembly/bench.py --baseline target/rg-original-lto --candidate target/rg-assembly-lto --cpu 4 --samples 30 --seed 8419 --reverse-case-order --output target/assembly-run2.json
```

Python 3.11+ and Linux are required by the measurement scripts. Choose an allowed
CPU with `--cpu` if logical CPU 4 is unavailable. The harness needs several
hundred MiB of disk space for generated input. It assumes the two supplied
binaries were built with the flags above; it records their hashes but does not
independently infer compiler flags. Run compilation and tests before timing,
not alongside it. The generated input and binaries stay under ignored `target/`.

Future work should first establish whether a change beats the Rust control,
then repeat on other CPUs and realistic directory trees. The current evidence
supports selected hot-path improvements, not replacing ripgrep with assembly.
