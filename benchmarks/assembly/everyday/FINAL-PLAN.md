# Isolated candidate confirmation

Written before confirmation. Candidate: rg-isolated, SHA-256
0d5f756bb912cda19c98c744effaea4fcc7ed9e7ce0b08b2896be44d451bd9f8.
It is upstream 3fce3b5 plus exactly the four ignore-crate changes in
isolated.patch: notifications, per-thread ignore scratch, parent-rule flags,
and no scratch pool for an empty file-type set. Build: release-lto, default CPU
target, PCRE2, Rust 1.98.1. No old assembly experiment scaffolding or packed
relocations. System baseline and equally built clean source reference retain
their recorded hashes in the result files.

Use combined-manifest.json: all 32 original everyday cases, all 81 broad cases
(with a name prefix only), and all four supplemental file-type cases. Keep the
arguments, affinities, cache modes and input hashes unchanged. No unfavorable
case is removed. The 19 original everyday directory cases alone determine the
improvement target: at least half must take at least 5% less time in both
sessions, with per-case 95% elapsed-ratio intervals entirely below parity.

Two sessions of 15 randomized paired rounds each, the existing gate's minimum:
- A: seed 269361, forward case order.
- B: seed 269367, reverse case order.

The broader confirmation now covers 117 cases per session, rather than the
first candidate's 32. Use the same runner, system baseline controls, clean
source reference, per-case 3% AND 0.10 ms regression margin, and noise/I/O rules.
Every case must pass both sessions before promotion. No averaging, discarded
outliers, or repeating completed sessions to seek a pass. If precision or
interference prevents a pass, report INCONCLUSIVE and leave the installation
unchanged. Record CPU time and memory, not just elapsed gains.

Use the external-work guard for both TTFX roots, 4 GiB MemoryMax, zero swap,
OOMPolicy=kill, disk-backed corpora, and no changes to CPU settings. Complete
compilation, correctness checks, packaging and provenance work before timing.
Do not stop another job. Retain every interrupted attempt under its own name.
No simultaneous build, test or profiling work. No upstream contribution.

The earlier 45-round confirmations are measurements of a different candidate;
they remain INCONCLUSIVE. All discovery failures and quality flags stay public.
