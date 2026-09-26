# Regression audit protocol

This protocol and the workload generator are written before collecting audit
timings. The earlier selective wins are hypotheses, not a regression verdict.

## Scope and controls

- Same upstream revision, compiler, `release-lto` and `target-cpu=znver4` for
  baseline and candidate. No PGO in the primary comparison. No CPU/OS changes.
- A separate `experimental-class` build excludes the earlier literal scanner,
  byte counter, fused scanning and parallel CLI path. Earlier binaries remain
  available as diagnostic comparisons, not recommended by this audit.
- Workloads include ordinary literals, regexes, options, Unicode, dense output,
  tiny/empty inputs, long lines, binary input, eligible and ineligible character
  classes, real source trees, and a new subtitle slice. Synthetic stress cases
  are explicitly labeled. Cold-I/O cases are evaluated separately.
- Freeze the generated manifest and its hash. Do not remove slow cases after
  seeing results. Fixes may narrow the optimization's applicability, but the
  same complete workload matrix must still be run against the final candidate.
- Two identical baseline labels expose scheduling/measurement noise. All modes
  use the same per-case CPU affinity, flags, inputs and output destinations.
- Verify output and status before timing. Directory results are compared as
  unordered lines; JSON elapsed-time fields are normalized. Timed output goes
  to `/dev/null`; interactive-terminal speed is outside the claim.

## Timing and predeclared interpretation

- Randomized paired rounds; at least 9 rounds in discovery and 15 rounds in
  each of two final sessions, with distinct seeds and reversed case order.
- For short commands, time batches with a repetition count chosen only from
  baseline warmup (target at least 50 ms, at most 25 invocations per batch).
  Report wall time per invocation, including startup.
- Record all samples, child CPU time, major faults and input blocks. Warm-cache
  I/O or unstable baseline controls makes a case inconclusive, not a pass.
  Cold cases evict only the dedicated benchmark copy with `posix_fadvise`; no
  global cache dropping or shared-memory corpus copies.
- Report every median slowdown, including small ones. The practical regression
  margin is **3% AND 0.10 ms per invocation**, fixed before measurement. This
  is an explicit tolerance, not a claim of mathematically zero regressions.
- Resample paired rounds to obtain a 95% bootstrap interval for candidate
  elapsed time divided by the baseline controls' mean time. A lower bound
  above both margins fails. An upper bound within either margin passes that
  case. A result spanning the margin is inconclusive and is not called safe.
- A repeated baseline-control difference exceeding the same margin, timed
  warm-cache I/O, or failures in either final session prevents a clean verdict.
- No geometric mean or large win may offset a regressed case. Both final
  sessions must pass every in-scope case for a bounded no-material-regressions
  statement. Remaining failures or uncertainty must be reported explicitly.

No finite suite establishes that no possible input regresses. This audit can
only establish a result for its recorded workload matrix, machine and margin.
