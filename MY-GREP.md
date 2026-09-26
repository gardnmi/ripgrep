# my-grep: what made it faster?

`my-grep` is an AI-assisted personal ripgrep experiment tuned for one machine:
an AMD Ryzen 5 7600X (Zen 4) running Linux. It makes a narrow group of searches
much faster. **The results do not establish a general speedup or zero regressions.**
It is installed under its own name, leaving the system's `rg` available.

Think of the change as adding a specialist to ripgrep. For a question like
“does this line contain 30 letters in a row?”, the specialist can use a simpler
method than a general regular-expression engine.

- **Check 64 bytes together.** Rust code uses the CPU's AVX-512 vector
  instructions to check a block of text at once. The result is a row of bits:
  `1` for an allowed character, `0` otherwise. A few bit operations find runs
  of consecutive matches. [Scanner source](crates/asm/src/class.rs).
- **Make decisions once.** The pattern selects a specialized scanning routine
  before scanning starts, avoiding repeated decisions inside the busiest loop.
- **Keep ordinary searches on the upstream engine.** A tiny startup router,
  written in assembly and C, sends eligible searches to a separate worker.
  It recognizes supported ASCII character repetitions on one regular file of
  at least 8 MiB, with limited flags. Other commands continue into the preserved
  upstream executable. [Routing rules](scripts/assembly/entry_dispatch.c).

Most of the program remains ripgrep's Rust code. The large gains come from
specializing the matching algorithm; writing something in assembly alone does
not guarantee it will be faster. Ripgrep already has many optimizations and
supports a much wider range of searches and machines.

## What we measured

These are session A medians against the installed **ripgrep 15.2.0** package,
using roughly 128 MiB of real subtitle text already in memory. The examples
were deliberately selected to exercise the specialist; ordinary controls were
also measured. Both sessions and all eight workloads are in the
[full report and raw data](benchmarks/assembly/showcase/README.md).

| Search | System `rg` | `my-grep` | Result |
| --- | ---: | ---: | --- |
| 30 letters in a row | 162.898 ms | 15.485 ms | 10.52× speedup |
| Same, with line numbers | 166.532 ms | 18.023 ms | 9.24× speedup |
| Count lines containing 17 hex digits | 162.912 ms | 15.374 ms | 10.60× speedup |
| Count lines containing 8 digits | 15.852 ms | 13.966 ms | 1.14× speedup |
| Ordinary absent-word search | 12.515 ms | 12.696 ms | **1.45% slower** |

The repeat session's absent-word search was **5.05% slower**, with its 95%
interval entirely on the slower side. Both sessions' overall verdict was
**INCONCLUSIVE**.

## Was anything fudged?

There are no saved answers, hardcoded match counts, or benchmark-filename checks
in the fast path. It searches the supplied input. Output, errors and exit
status were compared before timing; directory output was sorted for comparison.
Two sessions used warmups and 15 randomized paired rounds each. Timings include
startup, routing and output processing, with both programs writing to
`/dev/null`. The larger correctness run passed 1,236 tests and 4,457 CLI
comparisons, including repeated fallback checks. Those checks are evidence,
not a proof that every possible input is correct.

The important caveats are public too:

- Earlier attempts introduced regressions. Some timings overlapped another
  job. The [experiment history](benchmarks/assembly/dispatch/README.md) retains
  failed attempts, corrections and the inconclusive acceptance result.
- The installed-package comparison includes build differences. Earlier
  comparisons against equally CPU-tuned upstream builds are documented
  separately. This experimental build also lacks the system package's PCRE2
  support.
- The promotional animation illustrates recorded medians; it is not a live
  race. The command was renamed from `rg-zen4` to `my-grep` afterward, without
  changing the tested executable.

This work stays in the personal fork. It is not an upstream contribution or
an endorsement by ripgrep's maintainers.
