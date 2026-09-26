# Isolated directory candidate

After the generic and packed-relocation variants failed to establish the
no-material-regression bound, build only the three modified ignore-crate files
on unchanged upstream 3fce3b5bb0236da2df6d99672afb8a719642eca7. This excludes all
supporting source changes from the older assembly experiment, including matcher
builder factoring and the optional fused-line-count trait method. Their effect
is a hypothesis, not an established cause of the earlier regressions.

Use release-lto, default CPU target, PCRE2, and no packed-relocation flag. Compare
against the existing identically configured unchanged upstream reference and
installed /usr/bin/rg. Keep all prior results. First collect nine-round discovery
on the unchanged 32-case everyday matrix (seed 269351) and 81-case broad matrix
(seed 269353), with the existing runner, guard and memory limits. Do not overlap
compilation/testing with timing. Record exact release output equivalence.

Any confirmation requires its own prewritten schedule, the same margins and
all cases. No installation until the no-material-regression gates pass.

Before building or timing this candidate, source inspection found that
Types::empty and unselected TypesBuilder sets create scratch pools and thereby
trigger the available-parallelism query. Also change types.rs to omit that pool
only when its GlobSet is empty; matching already returns before using it in
that case. Selected file types retain the original pool and semantics. This is
a fourth production file. The experiment thus tests the isolated directory
changes plus empty-type setup removal, not isolation alone. Trace startup to
check the mechanism; do not infer a precise causal speedup without an ablation.
