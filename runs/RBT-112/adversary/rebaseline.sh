#!/bin/bash
# RBT-112 design adversary §2: the design's baseline.sh re-run unchanged into $SCRATCH/baseline, timed, and cmp'd
set -e
HERE=$(cd "$(dirname "$0")" && pwd); cd "$HERE/../../.."
O=${SCRATCH:-/tmp/rbt-112-adv}/baseline; mkdir -p "$O"
for SEED in 801 804 805 806 807 1 2 3 4 7; do
  F=runs/RBT-106/founders-w32-$SEED
  [ -f "$F/SHA256SUMS" ] || python runs/RBT-106/founders.py "$SEED" 32 "$F" > /dev/null
  s=$(date +%s); python runs/RBT-112/baseline.py "$SEED" "$F" > $O/baseline-w32-$SEED.txt; echo "default $SEED $(( $(date +%s)-s ))s"
  s=$(date +%s); python runs/RBT-112/baseline.py "$SEED" "$F" --global-bias-sigma 0 > $O/baseline-w32-S0-$SEED.txt; echo "S0 $SEED $(( $(date +%s)-s ))s"
done
for f in $O/*.txt; do cmp -s "$f" runs/RBT-112/baseline/$(basename $f) && echo "BYTE-IDENTICAL $(basename $f)" || echo "DIFFERS $(basename $f)"; done
for s in 801 804 805 806 807 1 2 3 4 7; do
  diff <(tail -n +2 $O/baseline-w32-$s.txt) <(tail -n +2 runs/RBT-106/baseline/baseline-w32-$s.txt) > /dev/null && echo "default $s = RBT-106 below the header" || echo "default $s differs from RBT-106"
done
