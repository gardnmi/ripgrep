# Entry-stub audit with an explicit interference guard

This protocol adds process monitoring to the [entry experiment](ENTRY-PLAN.md).
The candidate, complete 81-case manifest, native baseline, timing calculations,
3% AND 0.10 ms margin, correctness checks and artifact hashes stay unchanged.

A separate TTFX validation driver (PID/process group 515771) began at
2026-09-26 06:26:44.92 UTC, during the first library-bundle confirmation session.
Its four concurrent oracle jobs and builds were later observed using substantial
CPU resources. It overlapped the second library session and entry discovery.
The first entry confirmation was stopped when this was identified. Its partial
samples and all previous full runs are retained. Their raw classifications
must not be presented as an isolated measurement of the code changes.

The new runs are justified by independent evidence of external interference,
not by selecting favorable timing outcomes. The previous no-retry rule still
prohibits discarding an unfavorable otherwise valid run. This addendum was
written before collecting the new guarded sessions.

Before starting, at every paired-round boundary and at completion, check for
competing compiler/profiler jobs outside the audit cgroup, and scripted jobs or
repository executables in `/home/gardnmi/Projects/ttfx` and
`/home/gardnmi/Worktrees/ttfx`. Suspended and exited processes do not count as
active work; idle interactive shells are ignored. Stop and preserve the run
if competing work appears. The guard records process identities, not command
arguments. It detects the known source of interference; it cannot prove the
entire desktop is perfectly idle or catch every brief event between checks.
Paired controls, resource counters and conservative uncertainty rules remain.

Only begin when this check is clear. No task outside this ripgrep work is
stopped without user authorization. No CPU/OS configuration is changed.

- Session A: all 81 cases, 15 paired rounds, seed 942111, forward order.
- Session B: all 81 cases, 15 paired rounds, seed 942119, reverse order.
- Both must pass every case, with the same two artifact hashes and required
  isolation watchers, for bounded acceptance. Otherwise reject or report
  inconclusive as dictated by the same gate. No wins cancel a regression.
- Keep both valid sessions regardless of their verdict. An interrupted session
  is not valid confirmation; retain it before resuming under a distinct name.
