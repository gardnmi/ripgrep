# Zen 4 follow-up: specialization, BOLT and a preserved-upstream bundle

Experimental follow-up to the [failed acceptance audit](../audit/README.md).
Native and BOLT integration attempts below are not approved as replacements.
Bundle performance verification is in progress. The installed ripgrep is
unchanged; this work remains in the personal fork, with no upstream PR.

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
long runs. Paired upper/lower ASCII intervals can share a comparison after
OR-ing bit 0x20. Unpaired intervals still use original bytes; folding digits
would incorrectly accept some control characters. There are 56 specialized
kernel variants, with scalar differential tests covering boundary lengths,
overlap, mixed digits/letters and paired ranges in different orders.

On the eleven-case [specialized-kernel diagnostic](specialized-subset.json),
the alpha/hex/digit workloads took approximately 16%, 21% and 18% less time
than the preceding class implementation measured in the same rounds. Those
are improvements to an already specialized experiment, not a general ripgrep
speedup. The integrated binary still did not establish the regression bound.

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
