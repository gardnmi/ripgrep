# Assembly entry-stub experiment

Written before building or timing this candidate. The entire frozen 81-case
matrix and original 3% AND 0.10 ms regression margin still apply. There is no
compiler PGO or BOLT. The specialized worker and the core routing rule are unchanged
from the repaired library bundle. `LD_PRELOAD`/`LD_AUDIT` additionally disable
routing to avoid duplicating loader diagnostics or injected constructor side
effects across an exec. The baseline remains native upstream.

The new candidate has two files: upstream with an added startup routine, and
the adjacent class worker. A short handwritten x86-64 assembly entry routine
preserves the initial stack and dynamic loader finalizer register, calls a
freestanding C router, then jumps to upstream's original entry. The router
uses direct Linux syscalls for eligible file probes and helper handoff. It
has no libc calls, heap allocation, global mutable data or new dynamic library.

The builder locates an unused virtual-address page between original LOAD
segments. It appends the payload to the file and maps it into that gap, without
moving any original mapping or increasing the highest mapped address/program
break. It repurposes the GNU ABI-tag/build-id NOTE program-header slot as the
new RX LOAD; note section contents remain, but the runtime NOTE reference is
removed. It must refuse other note kinds, incompatible layouts, oversized
payloads, undefined symbols or architectures other than this x86-64 PIE.

Every old byte outside the ELF entry field and program-header table must remain
identical. All original executable sections, dynamic dependencies, TLS, GOT and
data addresses remain unchanged. These assertions constrain the edit; they do
not establish equal speed or correctness without testing. The linked payload
ELF, raw bytes, object files, sources and manifest remain locally inspectable.

Run the routing/output/FIFO and broader CLI correctness suites first. Then run
all 81 discovery cases for nine rounds (seed 941101). If there is no definite
performance failure, run two full confirmation sessions of 15 rounds each,
seeds 941111 and 941119, with opposite case order. This is the original minimum
confirmation length; report remaining uncertainty and every warm-cache fault
without retrying unchanged binaries until they pass. Reject on any definite
failure, and never call an inconclusive result safe. Preserve all experiments.

No compilation, profiling or other benchmark jobs overlap timed sessions.
Use the existing disk-backed corpora and memory-limited scopes. This remains a
local experimental binary patch, not an installation or upstream contribution.

The design follows the [x86-64 process entry ABI](https://gitlab.com/x86-psABIs/x86-64-ABI/-/blob/master/x86-64-ABI/low-level-sys-info.tex)
and [ELF program-header requirements](https://refspecs.linuxfoundation.org/elf/gabi4%2B/ch5.pheader.html).
Syscall numbers come from this machine's Linux headers, and compilation checks
the required x86-64 `struct stat` layout.
