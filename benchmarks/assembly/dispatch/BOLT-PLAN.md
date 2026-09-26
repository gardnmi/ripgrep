# Paired post-link optimization protocol

Written before collecting any BOLT performance timings. The earlier
[audit protocol](../audit/PLAN.md) and frozen 81-case manifest remain the native
comparison. This separate experiment permits profile-guided post-link rewriting;
it is not the unprofiled native comparison. It preserves the original tolerance,
correctness requirements, workload set, randomized pairing, noise controls,
minimum round counts, two-session rule, and prohibition on hiding losses.

Both upstream and the candidate are compiled with the same rustc, `znver4`,
`release-lto`, retained symbols and `--emit-relocs`. Both are independently
instrumented by LLVM BOLT 22.1.8, trained on the exact same 16 commands and
two disk-backed inputs, and optimized with the exact same BOLT settings.
Training uses 32 MiB prefixes of the existing training subtitle slice and
original synthetic logs. Neither is an audit input. Compiler PGO is not used.
Training commands, input hashes, profiles, binaries and tool packages are
recorded. Rewriting warnings and stdout/status comparisons must be checked.

The primary baseline controls are two labels of **BOLT-optimized upstream**.
An additional **unmodified upstream native binary** is measured once per paired
round. The candidate must pass against both references: the original paired
bootstrap comparison against the controls' per-round mean, and an additional
paired bootstrap comparison against the native reference. A failure in either
fails the case; uncertainty in either is inconclusive. Baseline control checks
and warm-I/O checks still apply. All modes are interleaved randomly.

This extra reference prevents a slower rewritten baseline from making the
candidate look safe. The 3% AND 0.10 ms tolerance is unchanged. No averaging
across cases compensates for any failure. A diagnostic subset is never an
acceptance result. Final acceptance still requires every case to pass in two
complete sessions of at least 15 rounds, distinct seeds and reversed case order.

No system configuration is changed. Inputs remain on disk; memory scopes have
an 8 GiB limit and no swap. No build or profile collection overlaps timing.

Method references: [BOLT documentation](https://github.com/llvm/llvm-project/blob/main/bolt/README.md),
[LLVM's package repository](https://apt.llvm.org/).
