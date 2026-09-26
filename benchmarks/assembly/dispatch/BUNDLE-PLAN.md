# Preserved-upstream bundle experiment

This addendum is written before any bundle timings. The complete frozen
[81-case matrix](../audit/manifest.json) and [original protocol](../audit/PLAN.md)
remain binding, including every case and the 3% AND 0.10 ms margin. Two complete
confirmation sessions must both pass. No compiler PGO or BOLT is used here.

The candidate consists of three files: a copy of native upstream with a new
dynamic dependency, a small C constructor library, and an adjacent specialized
ripgrep worker. The build asserts that every executable ELF section retains its
original address and bytes. This preserves upstream search code; it does not
establish equal startup time or performance by itself. Hash all three files in
every audit, and assert they remain unchanged. Upstream is the same unmodified
native baseline as before. All invocations, including handoff costs, are timed.

The routing rule is fixed before timing: one explicit regular file at least
8 MiB, a newline and no NUL in its first 4096 bytes, and a single positive ASCII
class of at most four written intervals with at least eight distinct members,
repeated at least twice using braces. Optional `-n` and `-c` are accepted.
Configuration files disable routing unless `--no-config` is explicit. Other
options and input shapes use upstream. Environment overrides `RG_BUNDLE=0`,
`RG_CLASS=0`, and `RG_ASM=0`/`rust` also disable it. An unavailable worker leaves
upstream in control. The companion library itself is a required bundle file.

The rule uses input structure, never benchmark names, expected results, cached
outputs or particular corpus paths. Actual parsing and matching still uses
ripgrep. It may route a search that gains nothing; those costs count. The prefix
probe is solely a performance heuristic and does not decide search results.

The worker has the same native compiler profile as upstream, plus the isolated
experimental class feature. Its class kernel specializes range count and run
length, and merges paired ASCII intervals where bit folding is exact. SIMD
decides candidate lines/shortest matches; normal regex matching supplies spans,
captures and output. This is a hybrid experimental package, not an assembly
rewrite of all ripgrep and not a universal acceleration claim.

Correctness includes exact output/status/stderr comparisons, routing tests using
a temporary marker executable, configuration and disable controls, missing or
unusable worker fallback, BOMs, binary input and long lines. Keep all discovery
and confirmation results, including failures and uncertainty. The installed
system ripgrep is not changed.
