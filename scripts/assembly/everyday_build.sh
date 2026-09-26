#!/usr/bin/env bash
# Build a matching-feature baseline/candidate pair in separate Cargo directories.
set -euo pipefail
everyday_root=$(cd -- "$(dirname -- "$0")/../.." && pwd)
everyday_upstream=$(realpath -- "${1:?Pass a clean upstream checkout}")
everyday_output=$(realpath -m -- "${2:?Pass a new artifact directory}")
test -z "$(git -C "$everyday_upstream" status --porcelain)"
test "$(git -C "$everyday_upstream" rev-parse HEAD)" = 3fce3b5bb0236da2df6d99672afb8a719642eca7
test ! -e "$everyday_output"
mkdir -p -- "$everyday_output"

for everyday_label in baseline candidate; do
    everyday_source=$everyday_upstream
    if [[ $everyday_label == candidate ]]; then
        everyday_source=$everyday_root
    fi
    systemd-run --user --scope --collect -p MemoryMax=4G \
        -p MemorySwapMax=0 -p OOMPolicy=kill \
        env -u CARGO_ENCODED_RUSTFLAGS CARGO_BUILD_JOBS=2 \
        CARGO_TARGET_DIR="$everyday_output/build-$everyday_label" RUSTFLAGS='' \
        cargo build --manifest-path "$everyday_source/Cargo.toml" \
        --locked --profile release-lto --features pcre2 \
        > "$everyday_output/build-$everyday_label.log" 2>&1
    cp -- "$everyday_output/build-$everyday_label/release-lto/rg" \
        "$everyday_output/rg-$everyday_label"
done
sha256sum "$everyday_output/rg-baseline" "$everyday_output/rg-candidate" \
    > "$everyday_output/SHA256SUMS"
