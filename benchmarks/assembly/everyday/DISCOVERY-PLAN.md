# Everyday search experiment

Written before collecting candidate timings. The goal is useful ordinary-search
gains on the Ryzen 5 7600X, with unchanged search scope and output semantics.
No indexing, cached answers, reduced ignore checking, or corpus-name dispatch.

The fixed manifest covers a small source repository, the Linux tools subtree,
the whole Linux tree, synthetic application logs, real prose, tiny files,
Unicode, case folding, globs, context, counts, multiple patterns and file lists.
The previous character-class showcase is not part of the improvement target.
Existing broad correctness and regression checks remain additional safeguards.

Discovery may compare thread counts, allocators and builds on a labeled subset.
All observations and rejected variants are retained. Discovery cannot establish
acceptance. Freeze the manifest and input hashes before discovery; do not remove
unfavorable cases from confirmation.

Use the existing paired audit runner and its 3% AND 0.10 ms regression margin.
The main practical comparison is against the installed `/usr/bin/rg`; code
changes also need an unchanged source build with the same compiler, CPU flags,
features and build profile. Build-only gains are labeled as such. Compile PCRE2
support into new builds so this is not a reduced-feature replacement.

For a candidate to be described as a useful everyday improvement, require both:

- In two independent 15-round confirmation sessions, every case passes the
  existing no-material-regression gate, including its noise/resource checks.
- At least half the directory cases improve by at least 5% in both sessions,
  with their per-case 95% elapsed-ratio intervals below parity. Single-file
  results are shown separately; directory wins cannot be called universal wins.

No finite suite proves universal gains. Report all slower medians, uncertain
cases, CPU time and memory. No averaging away regressions. Interrupted runs
remain available. Benchmark only after builds/profiling finish, using the
existing external-work guard. Do not stop another job. Use a 4 GiB memory limit
with no swap, disk-backed data, and no global cache flushing or CPU changes.

Do not replace the installed `my-grep` with an unvalidated candidate.
