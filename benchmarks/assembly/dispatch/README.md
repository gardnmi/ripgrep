# Zen 4 follow-up: specialization, BOLT and a preserved-upstream bundle

Experimental follow-up to the [failed acceptance audit](../audit/README.md).
Native and BOLT attempts below are rejected or inconclusive. Later unguarded
bundle timings overlapped another task and cannot establish isolated performance.
The assembly-entry candidate achieves roughly **11.5–11.7×** speedups on two
targeted class searches in the guarded runs. The strict overall gate remains
**INCONCLUSIVE**, not approved: one baseline major fault disqualifies one case.
Small measured slowdowns also remain within the declared tolerance, as shown
below. The installed ripgrep is unchanged; this work stays in the personal fork.

**Measurement correction:** a separate TTFX validation/build job began at
06:26:44.92 UTC and overlapped much of library session A, all of B, and entry
discovery. Its CPU load was found only afterward. I should have checked for it
before timing. Original samples and gate classifications remain recorded, but
neither apparent wins nor losses in those runs are clean causal evidence about
the executable changes. [Process evidence](external-load-processes.json),
[driver/group evidence](external-load-groups.json), and a
[between-session snapshot](between-sessions-machine.json) document the discovery.
The first entry confirmation was [stopped with its samples retained](entry-session-a-external-load-incomplete.json).
No external job was stopped. Fresh runs require the
[explicit interference guard](ENTRY-QUIET-PLAN.md); thresholds and workloads
remain unchanged. This is a correction for independently observed concurrent
work, not discarding an unfavorable valid result.

## Guarded confirmation results

Session A: **80 PASS, 0 FAIL, 1 INCONCLUSIVE**. Session B: **81 PASS, 0 FAIL, 0 INCONCLUSIVE**.
Both use all 81 frozen workloads and 15 randomized paired rounds. All **162
numerical performance comparisons** meet the predeclared **3% AND 0.10 ms**
margin. Each run records 1,217 interference checks, with zero competing-work
observations. This is evidence for the measured cases and tolerance, not a
claim of universally zero regression. No averages cancel losses.

The remaining exception is `long-line-literal` in A: one major fault in
baseline control A, round 12, with zero recorded input blocks. Its timing
comparison passes (candidate elapsed time 3.96% lower), but the unchanged resource
rule marks it inconclusive. The same case passes completely in B. The
original fault remains recorded; B does not erase it or turn the combined
gate green. No unchanged-candidate rerun was added just to obtain a pass.

[All 81 cases and intervals](ENTRY-RESULTS.md), [strict gate output](entry-gate.txt),
[session A](entry-quiet-session-a.json), [session B](entry-quiet-session-b.json).

Selected real-text cases use a **128 MiB held-out subtitle slice**. Wall time
includes startup, file probing, worker exec and output formatting to `/dev/null`.

| Pattern | A upstream ms | A candidate ms | A speedup | B upstream ms | B candidate ms | B speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `[A-Za-z]{30}` | 162.030 | 13.794 | 11.75× | 162.029 | 14.100 | 11.49× |
| `[A-Fa-f0-9]{17}` | 162.177 | 13.887 | 11.68× | 161.910 | 13.954 | 11.60× |
| `[0-9]{8}` | 15.022 | 12.507 | 1.20× | 15.174 | 12.435 | 1.22× |

**Small losses are still losses.** Replacement output is approximately
0.60% slower in A and 0.46% slower in B; offset output is +0.70% and
+0.16%. These are below the declared 3% relative margin, not claimed wins
or mathematically zero overhead. The earlier multi-percent regressions
are not reproduced in the guarded entry-candidate sessions.

| Ordinary workload | A elapsed change | B elapsed change |
| --- | ---: | ---: |
| `literal-count` | -1.67% | -1.18% |
| `literal-only-offset` | +0.70% | +0.16% |
| `regex-captures` | -0.33% | -0.80% |
| `regex-replace` | +0.60% | +0.46% |
| `multiline` | -0.87% | -0.55% |

Correctness: **1,236 workspace tests** passed (3 ignored), **4,457 CLI
comparisons** passed (including JSON elapsed-field normalization where
applicable), and **46 routing assertions** passed. Comparison counts include
repeated environment modes and fallback paths; they are not 4,457 distinct
specialized workloads. Default and combined-feature compilation checks pass.

The tested local candidate is `target/entry-experiment/bundle/rg`, with
its adjacent `rg-class-worker`. Its [manifest](entry-build.json) records
the two hashes. It is kept as an experimental artifact; the strict
two-session gate has not approved it as a general replacement.

## What changed and why

The earlier class scanner made two ordinary output workloads slower. Removing
its check from the ordinary search loop was the first repair. `RegexMatcher`
again has no class field/branch with `experimental-class` alone. The CLI selects
a separate `ClassMatcher` before entering the generic file/reader search.
Full spans and captures retain the normal regex engine. The specialized matcher
is boxed so that its data does not enlarge the ordinary matcher enum.

[Counters before](counters-before.json) and [after](counters-after.json) show
ordinary literal/count instruction and branch counts returning approximately to
upstream. A fork with the experiments disabled closely matches upstream. But
separating types changes generated code elsewhere: [residual counters](counters-residual.json)
still show differences for replacement and multiline searches. Removing the
runtime branch alone did not meet the performance acceptance criterion.

The class kernel now selects a function once per pattern, with the range count,
case-folding mask and run-intersection depth fixed at compile time. AVX-512
compares 64 input bytes at once, then integer bit operations find sufficiently
long runs. It is written using Rust SIMD intrinsics, which the compiler lowers
to vector instructions. Paired upper/lower ASCII intervals can share a comparison after
OR-ing bit 0x20. Unpaired intervals still use original bytes; folding digits
would incorrectly accept some control characters. There are 56 specialized
kernel variants, with scalar differential tests covering boundary lengths,
overlap, mixed digits/letters and paired ranges in different orders.

On the eleven-case [specialized-kernel diagnostic](specialized-subset.json),
the alpha/hex/digit workloads took approximately 16%, 21% and 18% less time
than the preceding class implementation measured in the same rounds. Those
are improvements to an already specialized experiment, not a general ripgrep
speedup. These three cases use a fixed **128 MiB subtitle holdout**, not the
entire 13 GB README corpus. The integrated binary still did not establish the
regression bound.

## Attempts that did not meet the gate

All discovery results use at least nine randomized paired rounds. Subsets are
diagnostic only, never acceptance. Complete raw observations are retained.

| Candidate / experiment | Workloads | PASS / FAIL / INCONCLUSIVE | Finding |
| --- | ---: | --- | --- |
| [Separate matcher types](native-discovery.json) | 81 | 67 / 1 / 13 | Multiline +5.14%, 95% interval +3.86% to +6.47%; count regression repaired but candidate rejected. |
| [BOLT full recipe](bolt-discovery.json) | 81 | 68 / 2 / 11 | Multiline improved; replacement +7.41% and optional class +12.61% versus native upstream. Rejected. |
| [New specialized kernels](specialized-subset.json) | 11 | 6 / 0 / 5 | Faster targeted class scans; unrelated output cases still uncertain. |
| [BOLT block order only](bolt-blocks-subset.json) | 9 | 6 / 0 / 3 | No clean verdict; replacement median +3.65% versus native upstream. |
| [BOLT blocks and functions](bolt-layout-subset.json) | 9 | 5 / 1 / 3 | Replacement failed versus native upstream. |
| [BOLT lite](bolt-lite-subset.json) | 9 | 4 / 1 / 4 | Optional class failed versus equally optimized upstream. |

The [BOLT protocol](BOLT-PLAN.md) gave upstream and candidate the same training
commands, input slices and post-link optimization treatment. Each candidate also
had to pass against original native upstream, so making the control slower
could not manufacture a win. Profiles used two disk-backed 32 MiB prefixes of
older training data; the frozen audit inputs were not training data. The tested
BOLT code predates the new kernel specialization. None of these observations
establishes that every possible BOLT configuration would fail.

See [tool provenance](bolt-tools.json), [upstream training](bolt-upstream.json),
[candidate training](bolt-dispatch.json), and [alternative recipes](bolt-recipes.json).
Both initial BOLT binaries passed 1,212 CLI comparisons each:
[candidate](bolt-correctness.json), [upstream control](bolt-baseline-correctness.json).
The initial [native](dispatch-subset.json) and [BOLT](bolt-subset.json) subsets
are retained even though later, broader tests exposed problems.

## Bundle experiment

The bundle keeps upstream's executable instructions byte for byte at their
original virtual addresses, then adds a tiny dynamic library that chooses
whether to start the specialized worker. This avoids recompiling ordinary
upstream search code. The copy has changed ELF metadata and extra startup work;
equal code bytes are not proof of equal performance.

The constructor routes one explicitly named regular file of at least 8 MiB
when the pattern is a supported positive ASCII class repetition and the first
4096 input bytes contain a newline and no NUL. Only optional `-n`/`-c` and
`--no-config` are accepted. Config files otherwise disable routing. Small files,
directories, complex flags, long-line prefixes, small alphabets and unsupported
patterns retain upstream. The [complete rule and protocol](BUNDLE-PLAN.md) were
written before bundle timings. There are no corpus-name checks, saved answers
or benchmark-specific filenames in the router.

The helper is another complete ripgrep executable, so its existing parser,
matching semantics and output machinery still run. The router's file-prefix
probe only determines which executable runs. All opening, probing and `execve`
costs are included in timings. `RG_BUNDLE=0` disables routing. If the worker is
missing or cannot execute, the constructor returns to upstream. The library
itself must stay beside `rg`; removing it prevents the dynamic loader starting
the package. This is a Linux/glibc, Zen 4 experiment with three companion files,
not a standalone assembly rewrite or a supported replacement release.

[Build metadata](bundle-build.json) records every artifact hash and the
preserved ELF sections. The native upstream `.text` is 2,466,640 bytes and its
SHA-256 remains `5f73dafba383ea7b0886e51e5200ead7dc0d10835df162a8852de2e0dcb505e7`.
[Patchelf provenance](patchelf-tool.json) records the locally extracted tool;
no system package installation was needed.

## Correctness and measurement limits

- [Workspace tests](workspace-tests.json): 1,236 passed, zero failed, three
  ignored. Both experimental features together also pass `cargo check`.
- Bundle [general CLI comparisons](bundle-cli-correctness-v2.json): 3,204 passed;
  [machine experiment comparisons](bundle-machine-correctness-v2.json): 1,212
  passed, including matching broken-pipe behavior. These include many fallback
  paths, so their count is not a count of specialized executions.
- [Bundle-specific tests](bundle-correctness.json): 44 routing assertions using
  an isolated marker worker, plus 39 exact output/status/stderr comparisons
  with the real worker. Covers configuration, disable switches, missing or
  unusable worker, binary data beyond the prefix, BOMs, long lines and malformed
  patterns and FIFO producers. [Specialized worker checks](specialized-correctness.json) also
  passed 1,212 comparisons independently of the router.

The first bundle's [discovery](bundle-discovery.json) had 68 PASS, zero FAIL and
13 INCONCLUSIVE cases. Its [first confirmation was interrupted](bundle-v1-session-a-incomplete.json)
for a correctness repair: the router now checks path type before opening it,
preventing a transient FIFO open from disturbing a writer. Both the original
artifacts and observations remain available; see the [confirmation schedule](CONFIRMATION.md).
The broader CLI comparisons were repeated after this library change. V1's
[general](bundle-cli-correctness.json), [machine](bundle-machine-correctness.json)
and [routing](bundle-v1-correctness.json) check results are also retained.

The repaired library bundle **fails the raw acceptance gate**, and the external
load above independently disqualifies the runs as clean confirmation. Two complete 45-round sessions
produced 64 PASS / 1 FAIL / 16 INCONCLUSIVE and 61 PASS / 0 FAIL / 20 INCONCLUSIVE.
The captures/output case is +4.85% in session A, with its whole 95% interval
above the margin (+4.39% to +5.27%). This occurred during competing work, so it
cannot establish an isolated code regression. Session B's +3.83% median has an inconclusive
interval. An offset-output case also has a +7.30% median in A, but its warm-cache
major fault prevents attributing that result cleanly. These observations are
retained, not discarded as outliers. See the [full two-session table](BUNDLE-RESULTS.md)
and [gate output](bundle-gate.txt). Isolated major faults occurred even without
recorded input blocks; the predeclared rule still marks them inconclusive.

## Assembly entry prototype

The next experiment is a 1,553-byte startup payload, including a small handwritten
x86-64 entry routine and a freestanding C router. It needs no extra dynamic
library or allocator calls. A build-time patch places it in an unused virtual
address page before upstream's code. If the command is eligible, it probes the
file with direct Linux syscalls and execs the same specialized worker. Otherwise
it restores the original stack, flags and loader finalizer register, then jumps
to upstream's original entry point. Loader-injected processes (`LD_PRELOAD` or
`LD_AUDIT`) stay with upstream to avoid duplicated loader effects.

The previous library patch changed dynamic metadata and added mappings beyond
upstream's highest mapping. Those are plausible performance influences, not a
proven explanation of the mixed-load observations. The entry prototype preserves
every original LOAD mapping, dynamic dependency, TLS/GOT/data location and
highest mapped address. It asserts that every old file byte is unchanged except
the ELF entry field and program-header table. This adds a stronger control over
layout; timing still determines whether it works.

The patch reuses a NOTE program-header slot for the added RX mapping. GNU ABI
and build-id note bytes remain in their original sections. This is specific to
the inspected ELF layout; the builder rejects incompatible layouts. Version
and build-id strings still identify the embedded upstream executable, so use
the [manifest and artifact hashes](entry-build.json) to identify this experiment.
The startup payload's linked ELF, raw bytes and object files remain in
`target/entry-experiment/bundle` for inspection.

[Routing and output checks](entry-correctness.json) pass 46 routing assertions
and 41 exact comparisons, including FIFO producers and loader-environment
fallback. The [general](entry-cli-correctness.json) and
[expanded](entry-machine-correctness.json) CLI suites pass 3,204 and 1,212
comparisons. There are no unresolved symbols or relocations in the linked
startup payload. The [entry experiment protocol](ENTRY-PLAN.md) fixes the
discovery and confirmation schedule before its first timing.

The frozen audit compares the same latest upstream revision used in the prior
audit (`3fce3b5bb0236da2df6d99672afb8a719642eca7`) with the same Rust compiler,
`release-lto` and `-C target-cpu=znver4`. The machine is a Ryzen 5 7600X, not
Zen 5. Two identical baseline labels expose control noise. Timings include
startup and send output to `/dev/null`; terminal-rendering performance is not
claimed. CPU affinity is recorded per case. Warm-I/O contamination and materially
unstable controls make a case inconclusive. All data remains disk-backed,
with memory-limited scopes and no global cache dropping.

The margin remains **3% AND 0.10 ms**, not mathematically zero slowdown. Every
case must pass in two complete confirmation sessions. Large gains do not offset
a failed or inconclusive case. Per-case 95% intervals are not simultaneous
confidence across all workloads. This finite suite cannot prove that no other
input ever regresses. The routing probe can also change behavior if a file is
concurrently replaced while the command starts; concurrent modification is
outside the audit's fixed-input scope.

## Reproduction

The [original audit instructions](../audit/README.md#reproduction) describe input
preparation and the identical native upstream build. The final
[upstream recheck](upstream-recheck.json) still resolves master to the measured
`3fce3b5bb0236da2df6d99672afb8a719642eca7`. Reuse a registered clean upstream
worktree if one exists, or create one only under `~/Worktrees/ripgrep/`. The
completed clean worktree used here is removed after testing. Do not use
`/dev/shm` for the corpora. Keep earlier artifacts/results and use new paths.

For a fresh entry bundle, build upstream and the specialized worker with the
same compiler and native release profile. From this fork, after preparing the
baseline and corpora:

```sh
systemd-run --user --scope --collect -p MemoryMax=8G -p MemorySwapMax=0 -p OOMPolicy=kill env -u CARGO_ENCODED_RUSTFLAGS CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR=target/entry-repeat/build RUSTFLAGS='-C target-cpu=znver4' cargo build --locked --profile release-lto --features experimental-class
python3 scripts/assembly/entry_bundle.py --worker target/entry-repeat/build/release-lto/rg --output target/entry-repeat/bundle --metadata target/entry-repeat/build-metadata.json
systemd-run --user --scope --collect -p MemoryMax=4G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/bundle_check.py --bundle target/entry-repeat/bundle --without-library --output target/entry-repeat/correctness.json
systemd-run --user --scope --collect -p MemoryMax=4G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/machine_check.py --baseline target/machine/rg-upstream-native --candidate target/entry-repeat/bundle/rg --output target/entry-repeat/machine-correctness.json
systemd-run --user --scope --collect -p MemoryMax=4G -p MemorySwapMax=0 -p OOMPolicy=kill env TMPDIR=/home/gardnmi/Projects/ripgrep/target python3 scripts/assembly/check.py --baseline target/machine/rg-upstream-native --candidate target/entry-repeat/bundle/rg --output target/entry-repeat/cli-correctness.json
```

The entry builder uses `cc`, `ld` and `objcopy`; tool versions and commands are
in its manifest. It does not require patchelf. The old library experiment can
still be built using `class_bundle.py` and the recorded local patchelf tool.
The recorded worker was compiled at parent `6f693c9` plus the Rust changes
committed as `5de483b`. A fresh build can differ because ripgrep embeds its Git
revision; every new artifact needs a new audit rather than reusing these claims.

Once builds, tests and competing jobs have finished, run the complete sessions
sequentially. The watchers include the other repository and its worktree root.
Collection aborts if a competing build or watched job appears, preserving the
partial observations. Keep interrupted results under distinct names.

```sh
systemd-run --user --scope --collect -p MemoryMax=8G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/audit_bench.py --protocol benchmarks/assembly/dispatch/ENTRY-QUIET-PLAN.md --watch-cwd /home/gardnmi/Projects/ttfx --watch-cwd /home/gardnmi/Worktrees/ttfx --candidate target/entry-repeat/bundle/rg --artifact target/entry-repeat/bundle/rg-class-worker --output target/entry-repeat/session-a.json --samples 15 --seed 942111
systemd-run --user --scope --collect -p MemoryMax=8G -p MemorySwapMax=0 -p OOMPolicy=kill python3 scripts/assembly/audit_bench.py --protocol benchmarks/assembly/dispatch/ENTRY-QUIET-PLAN.md --watch-cwd /home/gardnmi/Projects/ttfx --watch-cwd /home/gardnmi/Worktrees/ttfx --candidate target/entry-repeat/bundle/rg --artifact target/entry-repeat/bundle/rg-class-worker --output target/entry-repeat/session-b.json --samples 15 --seed 942119 --reverse
python3 scripts/assembly/audit_gate.py --protocol benchmarks/assembly/dispatch/ENTRY-QUIET-PLAN.md --require-isolation-watch /home/gardnmi/Projects/ttfx --require-isolation-watch /home/gardnmi/Worktrees/ttfx --require-artifact target/entry-repeat/bundle/rg-class-worker target/entry-repeat/session-a.json target/entry-repeat/session-b.json
python3 scripts/assembly/audit_report.py target/entry-repeat/session-a.json target/entry-repeat/session-b.json --output target/entry-repeat/RESULTS.md
```

Completed benchmark collection returns normally even if performance fails. The
separate gate's exit status decides acceptance: 0 PASS, 1 REJECT, 2 INCONCLUSIVE
or invalid/incomplete evidence. Include the required watcher and artifact flags;
a launcher hash alone does not identify the worker. The interference guard's
[integration test](isolation-test.json) uses an owned sleeping fixture in another
cgroup and confirms the collector stops before recording any timing samples.

## Research references

- [Rust monomorphization](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html)
  explains why concrete matcher types produce separate generated search code.
- [LLVM BOLT](https://github.com/llvm/llvm-project/blob/main/bolt/README.md)
  documents instrumentation, retained relocations and post-link layout options.
- [AMD Ryzen optimization guidance](https://gpuopen.com/gdc-presentations/2024/GDC2024_AMD_Ryzen_Processor_Software_Optimization.pdf)
  informed exploration of SIMD and instruction layout; measured results, not
  architectural claims alone, determine the verdict here.
- [glibc loader source](https://github.com/bminor/glibc/blob/master/elf/dl-init.c)
  supplies the Linux/glibc constructor calling convention; routing tests confirm
  it on this machine.
- [Patchelf manual](https://github.com/NixOS/patchelf/blob/master/patchelf.1)
  documents the added dependency and `$ORIGIN` library lookup used by the bundle.
