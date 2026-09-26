# Reproducing the upstream README workloads

For the acceptance decision, see the later [broader regression audit](audit/README.md).
This historical benchmark subset does not establish regression-free behavior.

This follow-up runs the seven ripgrep commands in upstream's
[README comparison](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/README.md#quick-examples-comparing-tools):
two Linux kernel tree searches and five OpenSubtitles searches, including the
line-number variant described in the prose.

The baseline is the **latest upstream source verified on 2026-09-26 UTC**:
`3fce3b5bb0236da2df6d99672afb8a719642eca7`. A fresh `git fetch upstream master`
confirmed that no newer upstream commit was available. GitHub's latest published
release was also checked: **15.2.0**, published 2026-07-15. The baseline uses the
current development tip rather than an older release binary.

The assembly implementation is unchanged from `051d70ab91153bb961cceb4ecea547b890248d75`.
Both binaries use the same `release-lto` profile and compiler. Their hashes match
the earlier [experiment report](README.md). This is a comparison between two
builds of current ripgrep on the same machine, not a comparison of our times
with the README's historical Intel i9-12900K timings. Other grep tools from the
README tables are not included in this experiment.

## Results

The clearest assembly-specific benefit is the line-number case: **1.063×
throughput**, or about **6.0% less elapsed time**, compared with latest upstream.
The high-match-count case is **1.041×** by median, but its Rust control performs
almost identically, so that improvement primarily comes from the Rust literal
shortcut. The general regex cases are effectively tied.

Median wall times below include the full input and normal output formatting.
A ratio above 1 favors the assembly build.

| Workload | Matching lines | Upstream seconds | Assembly seconds | Rust control seconds | Speedup |
| --- | ---: | ---: | ---: | ---: | ---: |
| Linux tree, default filtering | 538 | 0.0799 | 0.0768 | 0.0797 | 1.040× |
| Linux tree, all C/header files | 451 | 0.0583 | 0.0562 | 0.0556 | 1.037× |
| `Sherlock [A-Z]\w+` | 7,882 | 0.6544 | 0.6534 | 0.6558 | 1.002× |
| Same search with `-n` | 7,882 | 0.9340 | 0.8783 | 0.9377 | 1.063× |
| `[A-Z]\w+ Sherlock [A-Z]\w+` | 485 | 0.6527 | 0.6526 | 0.6550 | 1.000× |
| `[A-Za-z]{30}` † | 6,749 | 15.2898 | 15.2885 | 15.2996 | 1.000× |
| `the` † | 83,499,915 | 6.0732 | 5.8366 | 5.8442 | 1.041× |

† The two slow cases include occasional storage reads and are **not a strict
zero-I/O reproduction** of the README's cached-file setup. Every retained sample
is included, including outliers. The no-literal case had one assembly sample at
16.558 seconds with 137 major faults and 298,640 input blocks; its other assembly
samples were around 15.2–15.3 seconds. In the frequent-match case, round four had
storage reads in all three modes. The other four rounds had zero major faults
and input blocks. Treat fine percentage differences in these rows cautiously.
All other table rows had zero timed major faults and storage input blocks.

The line-number case's paired-bootstrap 95% interval is 1.056–1.071×. The two
Sherlock regex cases without line numbers have intervals spanning 1.0. Kernel
searches show small median differences of about 4%; default-filtering uncertainty
also spans 1.0, and the C/header Rust control is slightly faster than assembly.
These measurements do not establish a broad assembly advantage for directory
searches. There is no universal average speedup or cross-CPU claim.

All seven workloads produce identical output across the baseline, assembly and
Rust-control modes. All five subtitle line counts also match the published
README exactly. The kernel counts are **538 and 451**, versus the README's
**536 and 447**. We used the linked kernel repository's pinned revision and a
fresh build, but cannot claim to have reproduced the historical kernel counts.
Compiler-generated files and ripgrep versions differ from the historical setup;
the precise source of the count difference was not established.

Raw samples, output hashes, binary/input hashes, bootstrap intervals, cache
residency and resource counters are in [the first five cases](readme-zen4.json)
and [the final two cases](readme-zen4-slow.json). The slow-case run was resumed
with `--allow-disk-io`; all previously recorded samples were retained after
rechecking binary and input hashes. Its recorded memory events show no limit
hits, OOM kills or swap use. Page residency was 100% at the slow-case boundaries,
which illustrates why boundary snapshots alone cannot prove absence of disk I/O
inside a timed search.

## Corpus and preparation

The kernel corpus is a shallow clone of
[`BurntSushi/linux`](https://github.com/BurntSushi/linux) at
`84e57d292203a45c96dbcb2e6be9dd80961d981a`. The README calls for a `defconfig`
build so that directory traversal encounters generated and ignored build files.
No tracked kernel source files were changed and no kernel was installed.

The host's GCC 16 defaults differ from the compiler used with this 2022 snapshot.
The initial build failed because real-mode code treated `bool` and `false` as
C keywords. Explicit GNU C11 fixed that. New compiler warnings then failed the
snapshot's warnings-as-errors setting; `KCFLAGS=-Wno-error` allowed those warnings.
The final command was:

```sh
make defconfig
make -j8 CC='gcc -std=gnu11' HOSTCC='gcc -std=gnu11' KCFLAGS=-Wno-error
```

The missing `bc` build dependency was extracted into the ignored local corpus
tools directory from the distribution package; no system package was installed.
Generated files can differ from those produced by the original compiler, so the
kernel snapshot and matching output counts are recorded separately from build
configuration and artifacts.

The subtitle source is the README's full
[OpenSubtitles v2018 English monolingual download](https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/mono/en.txt.gz),
provided by [OPUS](https://opus.nlpl.eu/) from
[OpenSubtitles.org](https://www.opensubtitles.org/). The compressed download is
3,663,376,519 bytes, decompressing to **13,113,340,782 bytes**. It was
decompressed in full with gzip integrity checks.
The repository's older `benchsuite` script points at v2016, so that download
setting was not used for these README workloads. The corpus is not committed
or redistributed by this fork.

## Method

The host is the same AMD Ryzen 5 7600X (Zen 4), Linux 7.2.3, and rustc 1.98.1
used in the earlier report. Each case uses the README's search options, plus
`--no-config`. The default thread selection is preserved for directory searches,
with all 12 logical CPUs available. Single-file searches are pinned to logical
CPU 4. No `-j1`, count-only replacement, shortened input, or new optimization
is substituted for the README commands.

Three modes are interleaved in randomized rounds: untouched upstream, the
assembly build, and `RG_ASM=rust` in the assembly build. The Rust control keeps
the literal shortcut but uses memchr kernels, allowing assembly gains to be
distinguished from integration gains.

Before timing, output bytes, line counts, exit status and stderr are compared.
Directory output is sorted only for this untimed comparison, because parallel
traversal can change result order. Subtitle output is hashed as a stream to avoid
holding the frequent-match case's gigabytes of output in RAM. Timed stdout goes
to `/dev/null`, while matching and formatting work still occur.

Each mode has an output-verification pass and one explicit untimed warmup. There
are seven timed rounds per case, except five for the two slowest patterns.
For subtitle timing, the runner holds a read-only mapping of the original disk
file and touches one byte per page before each timed process. The touched-byte
slice is only about 3.2 MB; the underlying pages are shared with the file cache.
The mapping is marked `MADV_DONTFORK`, so child processes do not inherit it.
Page touching is outside the timer and is identical for all three modes.
Wall time includes startup and file handling. Linux `mincore` records subtitle
page-cache residency before and after each case; per-process resource deltas
record major faults and storage reads. The user closed other applications before
the final run. Compilation and downloading finished before timing began.

The benchmark runs in its own temporary systemd scope with `MemoryMax=16G`,
`MemorySwapMax=0`, and `OOMPolicy=kill`. The runner verifies the limits, requires
memory headroom, and refuses a RAM-backed corpus. By default, cached subtitle cases must
start with at least 99.9% page residency and have zero major faults/storage reads
in the timed processes, otherwise the run stops. End residency is recorded;
pages reclaimed after their last read do not imply disk I/O during timing.

### Failed preparation attempt

The first on-disk attempt retained only about 12.2% of the subtitle file in
cache and read substantial data from storage. It was stopped and is preserved
separately as [an incomplete disk-I/O diagnostic](readme-disk-diagnostic.json),
not used for the cached-file comparison.

An attempted copy of the complete file into `/dev/shm` then hit the desktop's
per-user shared-memory quota. Chromium and Hyprland crashed during that copy;
Hyprland's core records `SIGBUS` while updating a keyboard map. The quota
failure, timing, and stack strongly implicate this benchmark setup. The copy
was removed, and the user restarted the desktop. No cached timings were taken
from that incomplete copy. No shared-memory copy or quota adjustment is used
in the final approach: the original disk file is warmed and checked, within
the dedicated memory-limited scope. The initial free-space check missed the
per-user quota; this was a setup mistake, not an assembly performance result.

A subsequent bounded run was stopped by the cache guard after 55 major faults
in one slow-case process; its raw data is kept in
[the cache-guard diagnostic](readme-cache-guard-diagnostic.json). This motivated
the explicit page touch before every trial. The first five cases of the final
measurement then completed with zero timed storage reads. An overly strict
post-run check stopped that session when residency fell to 99.6822% after the
last search. Those completed timings remain valid: their measured processes had
zero major faults and zero input blocks. The final two cases were run
separately using the same per-trial warmup, then resumed in diagnostic mode when
transient reads occurred. Both sessions and every sample are retained; the slow
rows explicitly disclose those reads.

## Reproduce

Build the baseline and candidate binaries using the instructions in the
[original experiment report](README.md#build-and-reproduce), after fetching and
checking the current upstream tip. If upstream has advanced, update both source
bases and record the new revision before comparing them.

Prepare the corpus under the ignored `target/` directory:

```sh
mkdir -p target/assembly-readme
git clone --depth 1 https://github.com/BurntSushi/linux target/assembly-readme/linux
git -C target/assembly-readme/linux rev-parse HEAD
# Expected: 84e57d292203a45c96dbcb2e6be9dd80961d981a
make -C target/assembly-readme/linux defconfig
make -C target/assembly-readme/linux -j8 CC='gcc -std=gnu11' HOSTCC='gcc -std=gnu11' KCFLAGS=-Wno-error
curl -4 --fail --location --retry 3 -o target/assembly-readme/en.txt.gz https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/mono/en.txt.gz
gzip -dc target/assembly-readme/en.txt.gz > target/assembly-readme/en.txt
sha256sum target/assembly-readme/en.txt.gz target/assembly-readme/en.txt

systemd-run --user --scope --collect -p MemoryMax=16G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/readme_bench.py --baseline target/rg-original-lto --candidate target/rg-assembly-lto --output target/readme-results.json
```

The script requires Linux and Python 3.11+, plus the kernel's build dependencies
for corpus preparation. `bc` must be on the build command's `PATH`. Use `--cpu`
to choose an allowed logical CPU for the single-file tests, and `--samples` or
`--slow-samples` to increase repetitions. Repeated `--case NAME` options select
specific cases. Prepare the corpus fully before running the benchmark. The
script streams large outputs and verifies residency instead of assuming the
entire input fits in RAM. It requires a dedicated cgroup with the limits above,
and at least the input size plus 4 GiB of available memory before beginning.
If those conditions cannot be met, it stops; do not fill `/dev/shm` to work
around a failed cache check. `--allow-disk-io` permits explicitly labeled
diagnostic timing, while retaining the memory limits and on-disk requirement.

An interrupted run can be continued with `--resume` and the same output path.
The runner checks input/binary hashes, preserves existing samples, and fills
only missing repetitions. `--allow-disk-io` must be stated explicitly to retain
IO-affected diagnostic runs; their resource counters remain in the output.
