# Packed-relocation experiment

The generic candidate's two complete everyday confirmation sessions remain
INCONCLUSIVE. The additional 81-case diagnostic FAILed on literal-only-offset
against the unchanged source reference and regex-anchored against system rg.
No promotion follows from those observations.

Try GNU ld's `-z pack-relative-relocs` on both candidate and unchanged upstream,
keeping the compiler, source changes, release-lto profile, CPU target and PCRE2
feature the same. This compresses the executable's relative-relocation table;
it neither changes search scope nor removes PIE/BIND_NOW hardening. This is a
machine-local build choice, not a portable-binary claim.

Save distinct binaries and retain all prior results. Run the unchanged everyday
32-case and broader 81-case matrices as nine-round discovery, seeds 269341 and
269343 respectively, against system rg and the equally rebuilt source reference.
Include the prior generic candidate as a diagnostic in everyday discovery.
Do not run builds, tests or profiling during timing. Existing isolation and
memory safeguards apply. Validate actual release-binary output equivalence.

Only a changed candidate is eligible for new confirmation. If this variant
remains unpromotable, document that result; do not silently route unfavorable
workloads elsewhere or remove cases. Any later confirmation schedule must be
written before collecting it, retaining the same regression margin.
