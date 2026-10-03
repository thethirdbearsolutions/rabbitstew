#!/bin/bash
# RBT-133 step 3 on one machine: run the WASM build (DIST/rbt_wasm.js) on both packed bouts, open loop and closed loop,
# and compare each run's state-stream sha256 with the committed x86 fingerprints in spikes/wasm/ref-wasm-x86/.
#   spikes/wasm/run_wasm.sh DIST OUTDIR [--write-ref]
set -uo pipefail
DIST=${1:?usage: run_wasm.sh DIST OUTDIR [--write-ref]}
OUT=${2:?usage: run_wasm.sh DIST OUTDIR [--write-ref]}
REF=spikes/wasm/ref-wasm-x86
mkdir -p "$OUT"
echo "# host: $(uname -sm) | $(python -c 'import sys;sys.path.insert(0,".");from rabbitstew.provenance import _cpu_model;print(_cpu_model())') | node $(node --version)"
cat "$DIST/BUILD.txt" 2>/dev/null | grep sha256
fail=0
for b in $(grep -v "^#" spikes/wasm/bouts.txt | cut -d" " -f1); do
  P=spikes/wasm/packs/$b
  for mode in openloop bout; do
    R="$OUT/$b-$mode"; mkdir -p "$R"
    node "$DIST/rbt_wasm.js" $mode "$P" "$R" > "$R/stdout.txt" || { echo "$b $mode: node failed"; fail=1; continue; }
    python spikes/wasm/check.py "$P" "$R" | sed "s#$OUT/##" > "$R/fingerprint.txt"
    grep -q "stream sha256 [0-9a-f]" "$R/fingerprint.txt" || { echo "NO FINGERPRINT: $b $mode (the run or check.py failed)"; fail=1; continue; }
    if [ "${3:-}" = --write-ref ]; then mkdir -p "$REF"; cp "$R/fingerprint.txt" "$REF/$b-$mode.txt"; fi
    if diff -q "$REF/$b-$mode.txt" "$R/fingerprint.txt" > /dev/null; then
      echo "IDENTICAL to x86 WASM: $b $mode  ($(head -1 "$R/fingerprint.txt" | grep -o 'sha256 [0-9a-f]*'))"
    else
      echo "DIFFERS from x86 WASM: $b $mode"; diff "$REF/$b-$mode.txt" "$R/fingerprint.txt"; fail=1
    fi
  done
done
for b in $(grep -v "^#" spikes/wasm/bouts.txt | cut -d" " -f1); do node "$DIST/rbt_wasm.js" bench spikes/wasm/packs/$b 20 | tail -1 | sed "s/^/$b /"; done
exit $fail
