# Bundle confirmation schedule

Fixed after the nine-round discovery run and before either confirmation starts:

- Session A: all 81 cases, 45 paired rounds, seed 929711, forward case order.
- Session B: all 81 cases, 45 paired rounds, seed 929719, reverse case order.
- Identical executable, worker and library hashes in both sessions.
- Same frozen manifest, bundle protocol and original regression margins.
- No compilation, profiling or other benchmark jobs during either session.

The extra rounds address the 13 inconclusive discovery cases; there were no
definite discovery failures. This does not change which cases or slowdowns
count. Keep both complete confirmation sessions regardless of their verdict,
and do not retry unchanged binaries until a favorable result appears.

## Correctness repair before completing confirmation

The first candidate's session A was interrupted after a code review identified
that opening a FIFO before checking its type could disturb a producer. Its
partial measurements are preserved as `bundle-v1-session-a-incomplete.json`,
including an inconclusive warm-cache major fault and uncertain offset-output
timings. No result is promoted. The original artifacts are retained in
`target/dispatch-experiment/bundle-v1`, with hashes matching `bundle-v1-build.json`.

The repaired library performs `stat` and rejects non-regular/small inputs before
opening them, and still rechecks the opened descriptor. New FIFO comparisons
pass. The library hash changes; the executable and worker hashes do not. Run
the same schedule above for the repaired candidate as `bundle-v2-session-a.json`
and `bundle-v2-session-b.json`. This is a source correctness fix, not a retry of
an unchanged candidate to discard unfavorable measurements. Keep both v2
sessions regardless of their outcomes.
