#!/bin/bash
# RBT-133 step 1 on one CI runner: run every probe against the committed x86 references and print the lot.
# Usage: spikes/wasm/locate/ci.sh OUTDIR     (run from the repository root)
set -uo pipefail
OUT=${1:?usage: ci.sh OUTDIR}
P=spikes/wasm/locate/probe.py
REF=spikes/wasm/locate/ref-x86
mkdir -p "$OUT"
python $P numpy-probe | tee "$OUT/numpy-probe.txt"
diff <(grep -v '^#' $REF/numpy-probe.txt) <(grep -v '^#' "$OUT/numpy-probe.txt") > "$OUT/numpy-probe.diff" && echo "numpy-probe: identical to x86 ref" || { echo "numpy-probe differs from x86 ref:"; cat "$OUT/numpy-probe.diff"; }
python $P gen0 > "$OUT/gen0.txt"; grep -E '^(#|ROW)' "$OUT/gen0.txt"
echo "gen0 bouts identical to x86 ref: $(paste <(grep bout $REF/gen0.txt) <(grep bout "$OUT/gen0.txt") | awk '{ if ($10==$22) s++ } END { print s+0 "/" NR }')"
for b in conventional-0 holistic-0; do
  pop=${b%-*}
  echo "=== $b"
  python $P record "$OUT/$b" --population "$pop" --bout 0 > /dev/null
  python $P compare "$REF/$b" "$OUT/$b"
  python $P replay-physics "$REF/$b" --scratch "$OUT"
  python $P replay-brain "$REF/$b"
done
