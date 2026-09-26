# my-grep: making everyday folder searches faster

Finding a name in a codebase. Searching a project for TODOs. Listing files.
Those are the jobs this round of the personal ripgrep experiment focuses on.

On my Ryzen 5 7600X, a new prototype made a small-repository word search take
**40–41% less time**, a TODO search in Linux tools take **about 20% less time**,
and a whole Linux source-tree file listing take **about 12% less time**.
These gains repeated in two complete measurement sessions.

**This is a separate, uninstalled prototype.** It has useful folder-search
gains, but a remaining regression means it has not passed the requirement for
replacing the installed `my-grep`. The system `rg` is also unchanged.

[![Watch the everyday-search comparison](benchmarks/assembly/everyday-video/poster.png)](https://github.com/gardnmi/ripgrep/raw/refs/heads/experiment/assembly-hotpaths/benchmarks/assembly/everyday-video/my-grep-everyday.mp4)

[Watch the revised 52-second video](https://github.com/gardnmi/ripgrep/raw/refs/heads/experiment/assembly-hotpaths/benchmarks/assembly/everyday-video/my-grep-everyday.mp4)
· [Animation, offline player and rendering instructions](benchmarks/assembly/everyday-video/README.md)
· [Complete benchmark report][report]

## What changes in everyday use?

The benefit is shorter waits for the tested folder searches. Here are selected
ordinary tasks, compared with installed **ripgrep 15.2.0**. Times include
starting the program; lower is better.

| Task | Session A: system → prototype | Less time | Session B: system → prototype | Less time |
| --- | ---: | ---: | ---: | ---: |
| Find `Searcher` in the ripgrep source tree | 4.363 → 2.615 ms | 40.07% | 4.602 → 2.697 ms | 41.39% |
| Search that tree for an absent word | 4.160 → 2.580 ms | 37.98% | 4.330 → 2.700 ms | 37.64% |
| Find files containing `error`, ignoring case | 4.725 → 2.750 ms | 41.79% | 4.816 → 2.854 ms | 40.73% |
| List the small repository's files | 3.413 → 2.149 ms | 37.03% | 4.076 → 2.363 ms | 42.03% |
| Find `TODO` in Linux tools | 11.594 → 9.329 ms | 19.53% | 11.600 → 9.260 ms | 20.17% |
| List the whole Linux source tree | 26.535 → 23.475 ms | 11.53% | 26.199 → 23.021 ms | 12.13% |

For the small word search, that is **roughly two milliseconds saved per
invocation**. The Linux file listing saves roughly three milliseconds. These
are real but small absolute differences; this does not establish a noticeable
change in editor responsiveness. Editor integration and drawing results in a
terminal were not measured.

Across the original everyday-directory set, **15 of 19 tasks** took at least
5% less time in both sessions, with each per-case 95% interval below parity
and quality checks passing. Sorted output, explicit single-thread searches
and the two other whole-tree searches did not meet that repeated target.
That gives us evidence for a useful class of everyday improvements, not a
promise that every command is faster. [Every result, including uncertainty][results].

## How it works, in plain English

A search does more than read text. It finds files, applies ignore rules and
hands work to other CPU threads. For short searches, that coordination can
take a meaningful part of the total time.

- **Wake workers sooner.** When another worker finds more work, notify a
  waiting thread instead of routinely waiting for its next one-millisecond
  check. Timed waiting remains as a fallback.
- **Reuse temporary space.** Each thread keeps a scratch list for checking
  ignore rules, avoiding repeated trips to a shared storage pool. That list
  is working space; it does not cache search answers.
- **Avoid irrelevant checks.** Remember whether parent folders have applicable
  ignore rules, so empty or inapplicable rule sets do not cause extra path work.
- **Do less setup.** When no file-type filter needs matching storage, do not
  prepare it. Explicit type filters retain their normal matching behavior.

This prototype changes **four Rust files** on clean upstream ripgrep. Normal
matching, flags and ignore rules are retained, and PCRE2 is included. The
[source patch][patch] is public. The earlier assembly and vector-scanning
specialist is a different experiment; its narrow 10× results do not describe
ordinary folder searches or this prototype. [That earlier story is preserved here](MY-GREP-SPECIALIST.md).

## The tradeoffs

The full test covers **117 workloads**, not just the examples above. Each
session finished with **97 PASS, 19 INCONCLUSIVE and 1 FAIL**. PASS allows the
predeclared practical margin; it does not mean exactly zero slowdown.

The repeated failure was a general-regex count on one file. Against unchanged
upstream built with the same compiler, features and profile, the prototype was
**4.31% slower** in A (19.458 → 20.297 ms) and **4.55% slower** in B
(19.558 → 20.447 ms). Against the packaged system `rg`, that same case was
about 1% faster. Both comparisons matter: the remaining loss cannot be
explained away by selecting the more favorable baseline. Its cause has not
been isolated. **The overall no-regression gate failed.**

Short parallel searches can use more CPU while finishing sooner. The small
word search used **17–27% more CPU time**; the Linux tools word search used
about 2–3% less. This is a latency result, not an energy-saving claim.
Tiny absent-word searches also had slightly slower medians, around
0.04–0.05 ms. [All CPU measurements][cpu].

Ripgrep supports many machines and workloads. These results show a tradeoff
worth exploring on this machine; they do not show that its maintainers missed
a universally better setting.

## Was the test honest?

There is no index, saved answer, hardcoded match count, benchmark-filename
dispatch or reduced search scope. Each invocation searches its supplied input.
The candidate passed **1,233 workspace tests** and **3,556 CLI comparisons**.
Those are useful correctness checks, not proof for every possible input.

Two sessions used 15 randomized paired rounds each, including two identical
system controls and a separately built upstream reference. Output, errors and
exit status were checked before timing. Parallel directory output was sorted
for comparison, and JSON timing fields were excluded. Separate sorted-output
checks compare bytes exactly. No unfavorable case or measured outlier was
discarded.

The featured tasks use real source trees already in the filesystem cache,
with output sent to `/dev/null` for both programs. The broader suite includes
single files, synthetic edge cases and targeted cold-file cases. The corpora
were used in earlier experiments, so they are not an entirely unseen test set.

The source comparison uses upstream `3fce3b5`, Rust 1.98.1, `release-lto`,
PCRE2 and the default CPU target for both builds. That source revision is newer
than packaged 15.2.0. A forced Zen 4 compiler target did not consistently win.
The regression rule was set before confirmation: more than 3% **and** more
than 0.10 ms. Per-case intervals do not establish simultaneous confidence
across the entire suite.

Forcing fewer threads, changing the allocator and more aggressive polling
did not produce a consistent overall win; polling also raised CPU costs.
[Failed approaches and complete provenance remain documented][report].

The video animates these saved medians slowly so the differences are visible.
It is not a live race, and its longer animation time does not represent seconds
saved by a search. Its offline player includes every workload and both sessions.

AI-assisted work in a personal fork. No upstream contribution or endorsement.

[report]: https://github.com/gardnmi/ripgrep/tree/55279a6c2e16c5bf8b441518d0f4d4f91c493060/benchmarks/assembly/everyday
[results]: https://github.com/gardnmi/ripgrep/blob/55279a6c2e16c5bf8b441518d0f4d4f91c493060/benchmarks/assembly/everyday/FINAL-RESULTS.md
[cpu]: https://github.com/gardnmi/ripgrep/blob/55279a6c2e16c5bf8b441518d0f4d4f91c493060/benchmarks/assembly/everyday/FINAL-CPU.md
[patch]: https://github.com/gardnmi/ripgrep/blob/55279a6c2e16c5bf8b441518d0f4d4f91c493060/benchmarks/assembly/everyday/isolated.patch
