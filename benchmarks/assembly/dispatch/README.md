# Selecting the class matcher before the search loop

Experimental follow-up to the [failed acceptance audit](../audit/README.md).
No candidate in this directory is approved as a general upstream replacement.

The ordinary `RegexMatcher` again has no class field or class branch when built
with `experimental-class` alone. A separate `ClassMatcher` handles eligible
parsed expressions. The CLI chooses the matcher before each file/reader search;
Rust generates a separate concrete search loop for each type. Full spans and
captures retain the existing regex engine. The older `experimental-asm` feature
remains a historical, separately enabled experiment.

CPU counters compare upstream, the prior class build, a fork build with both
experiments disabled, and the new dispatch implementation. On ordinary commands,
the previous class integration adds instructions/branches; the new implementation
returns those counts approximately to upstream. Cycles and wall time still need
measurement: removing branches alone does not establish acceptance.

- [Counters before](counters-before.json) and [after](counters-after.json).
- [Initial eight-case diagnostic](dispatch-subset.json): six PASS, two
  INCONCLUSIVE, zero FAIL. A subset is not a full acceptance result.
- [Post-link experiment protocol](BOLT-PLAN.md), fixed before its timings.
- BOLT [tool provenance](bolt-tools.json), [upstream training](bolt-upstream.json)
  and [candidate training](bolt-dispatch.json). Both get the same training
  inputs, commands and optimization flags. There is no compiler PGO here.
- Initial BOLT correctness: [candidate](bolt-correctness.json) and
  [upstream control](bolt-baseline-correctness.json), 1,212 comparisons each.
  This does not establish performance acceptance.

The primary native comparison retains the frozen 81-case audit and original
3% AND 0.10 ms tolerance. BOLT is evaluated separately against both optimized
upstream and the original native upstream reference. No slowdown may be offset
by a win elsewhere. All timing observations, failures and uncertainty are kept.

Research references:
[Rust monomorphization](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html),
[LLVM BOLT](https://github.com/llvm/llvm-project/blob/main/bolt/README.md),
[AMD Ryzen optimization guidance](https://gpuopen.com/gdc-presentations/2024/GDC2024_AMD_Ryzen_Processor_Software_Optimization.pdf).
