#!/usr/bin/env bash
# Build equal-tuning baseline/candidate pairs; train PGO on disjoint input.
set -euo pipefail
machine_root=$(cd -- "$(dirname -- "$0")/../.." && pwd)
machine_baseline=$(realpath -- "${1:?Pass the clean upstream checkout path}")
machine_data="$machine_root/target/machine"
mkdir -p "$machine_data"
test -f "$machine_data/train.txt"
test -z "$(git -C "$machine_baseline" status --porcelain)"

machine_build() {
    local label=$1 source=$2 flags=$3
    shift 3
    (
        cd "$source"
        systemd-run --user --scope --collect -p MemoryMax=8G \
            -p MemorySwapMax=0 -p OOMPolicy=kill \
            env -u CARGO_ENCODED_RUSTFLAGS CARGO_BUILD_JOBS=2 \
            CARGO_TARGET_DIR="$machine_root/target/machine-$label" \
            RUSTFLAGS="$flags" \
            cargo build --locked --profile release-lto "$@"
    )
}

for label in upstream candidate; do
    source=$machine_baseline
    features=()
    target_label=baseline
    if [[ $label == candidate ]]; then
        source=$machine_root
        features=(--features experimental-asm)
        target_label=candidate
    fi
    machine_build "$target_label" "$source" '-C target-cpu=znver4' "${features[@]}"
    cp "$machine_root/target/machine-$target_label/release-lto/rg" "$machine_data/rg-$label-native"
    profile="$machine_data/pgo-$label"
    mkdir -p "$profile"
    python3 - "$profile" <<'PY'
from pathlib import Path
import sys
for p in Path(sys.argv[1]).glob('*.profraw'):
    p.unlink()
PY
    machine_build "$target_label" "$source" "-C target-cpu=znver4 -C profile-generate=$profile" "${features[@]}"
    systemd-run --user --scope --collect -p MemoryMax=4G \
        -p MemorySwapMax=0 -p OOMPolicy=kill python3 \
        "$machine_root/scripts/assembly/machine_train.py" \
        "$machine_root/target/machine-$target_label/release-lto/rg"
    llvm-profdata merge -o "$machine_data/$label.profdata" "$profile"
    machine_build "$target_label" "$source" "-C target-cpu=znver4 -C profile-use=$machine_data/$label.profdata" "${features[@]}"
    cp "$machine_root/target/machine-$target_label/release-lto/rg" "$machine_data/rg-$label-pgo"
done
