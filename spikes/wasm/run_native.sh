#!/bin/bash
# RBT-133 control: run the native-scalar harness (toolchain/build_native.sh) on both packs and print each state stream's
# sha256, against the x86 native-scalar fingerprints in spikes/wasm/ref-native-x86/.
#   spikes/wasm/run_native.sh BIN_DIR OUTDIR [--write-ref]
set -uo pipefail
BIN=${1:?usage: run_native.sh BIN_DIR OUTDIR}
OUT=${2:?usage: run_native.sh BIN_DIR OUTDIR}
REF=spikes/wasm/ref-native-x86
mkdir -p "$OUT"
fail=0
cat "$BIN/BUILD-native.txt"
for b in $(grep -v "^#" spikes/wasm/bouts.txt | cut -d" " -f1); do
  for mode in openloop bout; do
    R="$OUT/$b-$mode"; mkdir -p "$R"
    "$BIN/rbt_native" $mode "spikes/wasm/packs/$b" "$R" > /dev/null || { echo "rbt_native failed: $b $mode"; fail=1; continue; }
    python spikes/wasm/check.py "spikes/wasm/packs/$b" "$R" | sed "s#$OUT/##" > "$R/fingerprint.txt"
    grep -q "stream sha256 [0-9a-f]" "$R/fingerprint.txt" || { echo "NO FINGERPRINT: $b $mode (the run or check.py failed)"; fail=1; continue; }
    if [ "${3:-}" = --write-ref ]; then mkdir -p "$REF"; cp "$R/fingerprint.txt" "$REF/$b-$mode.txt"; fi
    if diff -q "$REF/$b-$mode.txt" "$R/fingerprint.txt" > /dev/null; then echo "IDENTICAL to x86 native-scalar: $b $mode"; else echo "DIFFERS from x86 native-scalar: $b $mode ($(head -1 "$R/fingerprint.txt" | grep -o 'sha256 [0-9a-f]*'))"; fi
  done
done
exit $fail
