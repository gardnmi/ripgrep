# Making ordinary searches faster

This branch explores everyday searches through source folders: finding a word,
using a regular expression, filtering file types, and listing files. It is a
separate prototype from the character-class specialist currently installed as
`my-grep`.

The changes are fairly simple:

- **Less waiting:** idle search workers get notified when more work arrives.
- **Less bookkeeping:** each thread reuses a temporary list for ignore rules,
  and the program skips parent-rule work when no applicable rules exist.
- **Less startup work:** an empty file-type filter no longer prepares matching
  storage it will never use.

These are four Rust-file changes on clean upstream ripgrep. Each command still
searches its input and honors the normal flags and ignore rules. There are no
saved search answers, benchmark-filename checks, or restricted search scopes.
PCRE2 support is included.

Across two complete sessions, ordinary word searches through the small source
repository took **40–41% less time** (about 4.4–4.6 ms down to 2.6–2.7 ms).
Word searches through Linux tools took **about 20% less time**. Fifteen of the
19 everyday directory cases cleared the repeated-improvement target.

However, **this prototype has not met the no-regressions requirement**. The final tests found a general-regex slowdown
against an equally built, unchanged upstream reference. Short parallel searches
can also consume more CPU while finishing sooner. Large-file searches and
startup do not automatically benefit from faster folder traversal.

The installed `my-grep` and system `rg` are unchanged. The
[complete report](benchmarks/assembly/everyday/README.md) includes all timings,
slower cases, uncertainty, CPU costs, failed approaches and reproducible inputs.
Correctness checks passed 1,233 workspace tests and 3,556 CLI comparisons;
passing correctness checks does not prove that every command is faster.

AI-assisted personal experiment; no upstream contribution or endorsement.
