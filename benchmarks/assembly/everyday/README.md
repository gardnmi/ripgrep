# Everyday search on this machine

**Not promoted: both complete final sessions FAIL the regression gate.**

The everyday-directory improvement target was met: **15 of 19 cases** took
at least 5% less time in both sessions, with per-case 95% intervals below
parity and no quality flags in those cases. Each complete session had
**97 PASS, 19 INCONCLUSIVE and one FAIL** across all 117 cases.

| Ordinary workload | A system → candidate | A time saved | B system → candidate | B time saved |
| --- | ---: | ---: | ---: | ---: |
| Word search, small source repository | 4.363 → 2.615 ms | 40.07% | 4.602 → 2.697 ms | 41.39% |
| Regex search, small source repository | 7.970 → 5.763 ms | 27.69% | 8.269 → 5.985 ms | 27.62% |
| File listing, small source repository | 3.413 → 2.149 ms | 37.03% | 4.076 → 2.363 ms | 42.03% |
| Word search, Linux tools | 11.594 → 9.329 ms | 19.53% | 11.600 → 9.260 ms | 20.17% |
| File listing, Linux tools | 7.427 → 5.448 ms | 26.64% | 7.419 → 5.567 ms | 24.96% |
| File listing, whole Linux tree | 26.535 → 23.475 ms | 11.53% | 26.199 → 23.021 ms | 12.13% |

These are selected examples; [all 117 cases and intervals](FINAL-RESULTS.md)
include every slower and uncertain result. A 40% improvement on a tiny
repository saves roughly two milliseconds here, not seconds.

**The blocker repeated.** `broad-regex-general` took 20.297 ms versus
19.458 ms for the unchanged source build in A (**4.31% slower**), and
20.447 ms versus 19.558 ms in B (**4.55% slower**). Both intervals exceed
the predeclared regression bound. It was about 1% faster than system rg
in those same rounds; that does not erase the regression against an
equally configured build. The cause of this single-file difference has
not been isolated. The remaining uncertain cases also prevent acceptance.

Tiny searches still had small slower medians against system rg: for
example, `tiny-miss` cost about 0.046 ms more in A and 0.039 ms more in B.
Those passed the practical bound, which allows limited overhead.

Short parallel searches used more CPU. The small-repository word search
used about **17–27% more CPU time** while finishing sooner; Linux tools
word searches used about 2–3% less. [Every CPU measurement](FINAL-CPU.md)
is shown separately from wall time.

See [the unchanged gate output](final-gate.txt), [summary data](final-summary.json),
[session A](final-session-a.json), [session B](final-session-b.json),
[exact build details](isolated-build.json), and [source patch](isolated.patch).
The gate found no missing/incompatible-session errors. Warm-I/O flags
occurred for `broad-literal-insensitive` in A and `type-negated` in B;
those observations remain in the results. Neither session recorded
unstable controls, detected external build/TTFX interference, or OOM events.

**The installed `my-grep` and system `rg` remain unchanged.**

This experiment targets normal folder searches, not selected character-class
patterns. The candidate is clean upstream plus four Rust changes in the
`ignore` crate. It contains no assembly router or experimental regex scanner.
The earlier installed `my-grep` specialist is a separate binary.

## What changed, in plain English

- Wake a waiting worker when another worker has found more work, instead of
  routinely waiting for its next one-millisecond check. Work ownership and
  termination accounting stay the same, with timed waiting as a fallback.
- Reuse one temporary ignore-matching list per thread. This avoids repeatedly
  borrowing storage from a shared pool. It stores temporary match indices,
  never previous search answers. A private temporary list handles reentrant
  calls or thread-local teardown.
- Record whether parent folders have applicable ignore rules. When none can
  apply, skip rebuilding a path solely to check empty or inapplicable matchers.
  Git boundaries, global rules, `.ignore`, custom rules and overrides still apply.
- Do not prepare file-type matching storage when its glob set is empty.
  Searches with selected types retain the normal matching pool; definitions
  and `--type-list` remain available.

The production diff is limited to [walking](../../../crates/ignore/src/walk.rs),
[ignore matching](../../../crates/ignore/src/gitignore.rs),
[parent rules](../../../crates/ignore/src/dir.rs) and
[file types](../../../crates/ignore/src/types.rs).
There is no index, saved answer, benchmark-filename check, or reduced search
scope. Files and matching rules are considered according to the original flags.

## How the comparison works

The practical baseline is installed `/usr/bin/rg` 15.2.0. A second baseline is
unchanged upstream `3fce3b5bb0236da2df6d99672afb8a719642eca7`, built with the same
Rust compiler, default CPU target, `release-lto` profile and PCRE2 feature.
That source revision contains changes after the packaged 15.2.0 release; equal
version numbers do not mean identical source or compiler settings. The machine
is the owner's Ryzen 5 7600X. No CPU settings are changed.

The [final protocol](FINAL-PLAN.md) includes all 32 original everyday cases,
all 81 broader regression cases, and four added file-type cases. No unfavorable
case was removed. [The manifest](combined-manifest.json) records commands,
inputs, affinity and cache mode. Most cases use warm caches; the broader suite
also contains targeted cold-file cases. Source trees and subtitle text are
real; logs and boundary inputs are synthetic. These corpora were used in prior
experiments and are not wholly unseen holdout data.

Each round randomizes the candidate, unchanged reference and two identical
system controls. Timings include process startup and output to `/dev/null`.
Actual stdout, stderr and exit status are compared before timing. Directory
lines are normalized for unordered parallel output; JSON timing fields are
excluded. Separate correctness checks compare sorted output byte for byte.
The predeclared material-regression threshold is more than 3% AND more than
0.10 ms; PASS does not mean exactly zero overhead. Intervals are per case,
not simultaneous confidence across all cases. A faster average cannot hide a
regression in a different command.

Builds, tests and profiling finish before timing. The runner checks for
competing builds and TTFX jobs, uses a 4 GiB memory limit and zero swap, and keeps
all observations. Ordinary desktop activity is not eliminated by that guard.
Warm-I/O and noisy-control flags make a result inconclusive. Other jobs are not
stopped, global caches are not flushed, and the system executable is untouched.

## Validation and earlier attempts

The isolated candidate passed 1,233 workspace tests, with three ignored and no
failures. It also passed [352 directory CLI comparisons](isolated-directory-correctness.json)
covering nested repositories, ignore files, symlinks, binary files, type filters,
quiet termination, JSON and 1/2/12/65 workers, plus
[3,204 general CLI comparisons](isolated-cli-correctness.json) across 1,068 cases
and three legacy environment modes. Those modes repeat the same standard
engine here; no old assembly feature is enabled. These checks provide evidence,
not proof for every possible input.

The [first candidate and rejected variants](INITIAL.md) remain documented with
all data. Its two complete 45-round sessions were INCONCLUSIVE. A broader check
found offset-output and anchored-regex regressions. Packing ELF relocation
entries did not fix them. The new isolated candidate excludes the previous
assembly experiment's supporting source changes and skips unused type setup;
this is not a pure ablation of either change alone. A planned syscall trace
could not run because `strace` was unavailable; no claim rests on that trace.

Notifications trade latency for CPU use on short folder searches: more workers
become active sooner. Lower wall time is not a claim of lower energy use. Larger
trees and single files may behave differently. These changes do not promise a
speedup for every command or machine.

Use [the build script](../../../scripts/assembly/everyday_build.sh) with a clean
checkout of the pinned upstream revision and a new artifact directory. Baseline
and candidate use separate Cargo target directories. The
[preparer](../../../scripts/assembly/everyday_prepare.py) records public source
and existing corpus provenance. The [runner](../../../scripts/assembly/audit_bench.py)
and [gate](../../../scripts/assembly/audit_gate.py) preserve the original rules.
Exact source patches, compiler details and binary hashes accompany the results.

AI-assisted work in a personal fork. No upstream PR, merge request, or upstream
endorsement. The installed `my-grep` is changed only after the stated gate passes.
