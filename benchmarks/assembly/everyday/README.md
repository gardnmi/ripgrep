# Everyday-search experiment

The first candidate delivered repeatable directory-search gains, but **did not
pass the overall regression gate and was not installed**. In both 45-round
confirmation sessions, 16 of 19 directory cases took at least 5% less time and
had per-case 95% intervals entirely below parity. All 19 directory cases passed
the practical regression bound. The complete 32-case verdict was INCONCLUSIVE
in both sessions, and an additional broader diagnostic found regressions.

This candidate targets ordinary source-tree searches: literals, regular
expressions, case-insensitive searches, globs, context and file listing.
It is a separate experiment from the installed `my-grep` class specialist.
All new implementation changes are Rust code in the `ignore` crate.

## What changed

- **Wake workers when work arrives.** The original parallel walker can wait
  one millisecond between checks for work. Workers now advertise that they are
  waiting and receive a notification when another worker adds work. The queue
  and termination accounting stay in place, with timed waits as a fallback.
  The [implementation](../../../crates/ignore/src/walk.rs) follows Rust's
  [park/unpark token protocol](https://doc.rust-lang.org/std/thread/fn.park.html).
- **Give each thread a scratch list.** Ignore matching previously borrowed a
  vector from a shared pool on each call. A thread-local vector now serves
  successive matchers, with a private temporary vector if thread cleanup or
  reentrancy makes that storage unavailable. This stores temporary match
  indices, never search answers. [Implementation](../../../crates/ignore/src/gitignore.rs).
- **Avoid unnecessary parent-path work.** Each ignore matcher records whether
  its absolute parents contain applicable kinds of rules. If none can apply,
  matching avoids rebuilding an absolute path and walking those empty or
  inapplicable matchers. Git repository boundaries, `.ignore`, custom ignore
  files, overrides and global rules retain their existing semantics.
  [Implementation](../../../crates/ignore/src/dir.rs).

No index, saved answers, corpus-name checks or reduced search scope are used.
All files and matching rules are still considered according to ripgrep's flags.
The results do not establish a speedup for every possible command.

## Measurements

The [protocol](PLAN.md) freezes 32 everyday cases before testing: 19 directory
cases and 13 single-file cases. Sources are an immutable upstream ripgrep
snapshot and the existing Linux source checkout. Logs/tiny inputs are synthetic;
the subtitle slice is real prose. These corpora were used in prior experiments,
so this is not a claim of validation on completely unseen data.

The practical baseline is installed `/usr/bin/rg` 15.2.0. An additional reference
is unchanged upstream at `3fce3b5bb0236da2df6d99672afb8a719642eca7`, compiled with
the same Rust compiler, `release-lto` profile, default CPU target and PCRE2
feature as the candidate. The CPU is the owner's Ryzen 5 7600X (Zen 4).
Runtime SIMD detection remains enabled. This build does not enable the previous
experimental character-class scanner or parallel-within-one-file prototype.

Both final sessions use 45 randomized paired rounds, distinct seeds and opposite
case order. Each round includes two installed-rg controls. Output, stderr and
exit status are compared before timing; directory lines are sorted and JSON
elapsed fields normalized. Timings include startup and output processing to
`/dev/null`, with warm caches and all 12 logical CPUs available. No caches are
globally flushed and no CPU settings are changed. Builds and tests finish before
timing. The external-work guard, 4 GiB memory limit and zero-swap limit apply.

See [every result and interval](RESULTS.md), [the gate](gate.txt),
[CPU costs](CPU.md), [session A](session-a.json), [session B](session-b.json),
[the manifest](manifest.json) and [build hashes](builds.json).
The no-material-regression bound remains **3% AND 0.10 ms**, not exactly zero
overhead. A faster average cannot compensate for a failing or uncertain case.
Per-case intervals are not simultaneous confidence across the whole suite.

The first session had 31 PASS and one INCONCLUSIVE case (`prose-absent`). The
repeat had 29 PASS and three INCONCLUSIVE cases: `tiny-hit`, `tiny-miss` and
`log-json`. Those three had measured median slowdowns of 6.58%, 7.77% and 6.92%
against system rg. Their time-difference intervals crossed the 0.10 ms practical
bound; INCONCLUSIVE does not mean they were equally fast. Their medians were
within about 0.01 ms of the unchanged source build, so this is not evidence
that the directory changes alone caused the startup difference. It remains a
real cost relative to the installed package.

The separate [81-case diagnostic](broad-discovery.json), collected after those
sessions, had 52 PASS, 27 INCONCLUSIVE and two FAIL cases. `literal-only-offset`
was 4.34% slower than the unchanged source reference (1.08% slower than system
rg); `regex-anchored` was 8.33% slower than system rg. Nine-round discovery is
not confirmation, but these failures are additional reasons not to promote
this binary. These results are retained rather than averaged into faster cases.

Correctness checks passed: 1,239 workspace tests, with three ignored and none
failed; [288 directory CLI comparisons](directory-correctness.json); and
[3,204 general CLI comparisons](cli-correctness.json) across 1,068 cases and
three legacy environment modes. Those modes are repetitions for this build,
whose old experimental scanners are disabled. The exact tested release binary
hash is recorded in each comparison file.

## What did not work, and tradeoffs

- Forcing six threads hurt some large-tree searches; one thread was much worse
  on those cases. The default thread count is retained.
- Preloading jemalloc slowed several ordinary cases, particularly small
  commands. That diagnostic does not establish how every allocator/build
  combination would behave.
- Thread-local scratch alone was insufficient. The native build still lost
  substantially to system rg on several small-repository searches.
- Polling every 50 microseconds improved elapsed time, but increased CPU use
  on small searches. Notifications avoid relying on that short polling interval,
  but small searches still use more CPU time: more workers become active sooner.
  This is a latency tradeoff, not a promise of reduced CPU or energy use.
  For example, the source literal search used 24–26% more CPU time across the
  two sessions; source file listing used about 28–29% more. Larger directory
  cases generally used less CPU time in these measurements.
- Forced `target-cpu=znver4` compilation was not consistently best. The final
  candidate uses the default compiler target; the measured machine is still
  Zen 4. Do not attribute all differences from the system package to source code.
  The default-target candidate also added a scratch-storage teardown safeguard;
  its difference from the native candidate is not a pure CPU-flag ablation.
- The old assembly-entry packager rejected the new executable because it has
  no sufficiently large unused address gap. Its layout checks were not bypassed;
  the existing installed bundle is unchanged.
- Packing relative relocations with `-z pack-relative-relocs` reduced executable
  size but did not remove the startup penalty. That variant's everyday
  diagnostic had 26 PASS, five INCONCLUSIVE and one FAIL (`log-json`). Its broad
  diagnostic had 63 PASS, 16 INCONCLUSIVE and two FAIL cases (the same offset
  and anchored searches). It was rejected. See [the prewritten plan](RELR-PLAN.md),
  [everyday data](relr-discovery.json), [broad data](relr-broad-discovery.json) and
  [matching build settings and ELF tables](relr-builds.json). PIE and BIND_NOW
  were retained; no loader checks were bypassed.

All discovery records are retained: [configuration](config-discovery.json),
[scratch only](tls-discovery.json), [short polling](poll50-discovery.json),
[notifications with native compilation](wakeup-discovery.json), and
[default-target compilation](generic-discovery.json).
Their original [protocol](DISCOVERY-PLAN.md) is retained as well. Discovery is
used to choose candidates, not to establish acceptance. During the final part
of generic discovery, a provenance helper also read the binaries and invoked
`--version`; that run is diagnostic only. Confirmation excludes that work.

## Reproducing and checking

Use [everyday_build.sh](../../../scripts/assembly/everyday_build.sh) with a clean
checkout of the pinned upstream revision and a new output directory. It builds
baseline and candidate with matching features/settings in separate Cargo
directories. Reusing one Cargo directory across checkouts initially reused an
incompatible matcher artifact; that build failed, and all measured candidates
were rebuilt in their own directory.

The [preparer](../../../scripts/assembly/everyday_prepare.py) records all commands
and input hashes. The [audit runner](../../../scripts/assembly/audit_bench.py)
and [gate](../../../scripts/assembly/audit_gate.py) are unchanged. The added
[directory comparison script](../../../scripts/assembly/everyday_check.py)
checks nested repositories, ignore rules, globs, symlinks, hidden files, context,
JSON, quiet termination and 1/2/12/65 worker configurations against upstream.

This is AI-assisted work in a personal fork, with no upstream PR or endorsement.

## Follow-up

The next [isolated experiment](ISOLATED-PLAN.md) applies the directory changes
to clean upstream, excluding supporting source changes from the earlier
assembly experiment. It also omits file-type scratch storage when there are no
globs to match. Results for that different candidate belong to its own report;
the confirmation and rejection results above remain unchanged.
