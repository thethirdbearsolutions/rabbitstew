#!/bin/bash
# RBT-112 design adversary §3: the S = 0 matched null (null_xover_s0.py, unchanged) re-run on the ten seeds from part 2's
# genealogies restored from ckpt/rbt-90-SEED (RBT-90 part 2, finished) into $SCRATCH, and cmp'd with the committed tables
HERE=$(cd "$(dirname "$0")" && pwd); cd "$HERE/../../.."
S=${SCRATCH:-/tmp/rbt-112-adv}; mkdir -p $S/null
for SEED in 801 804 805 806 807 1 2 3 4 7; do
  P=$S/p2/$SEED
  [ -f "$P/lineage.jsonl" ] || scripts/durable.sh restore "$P" "rbt-90-$SEED" > /dev/null 2>&1
  F=runs/RBT-106/founders-w32-$SEED
  [ -f "$F/SHA256SUMS" ] || python runs/RBT-106/founders.py "$SEED" 32 "$F" > /dev/null
  O=$S/null/xnull-w32-S0-$SEED.txt
  [ -f "$O" ] || python runs/RBT-112/null_xover_s0.py "$P" "$SEED" "$F" --global-bias-sigma 0 > "$O"
  cmp -s "$O" runs/RBT-112/null/xnull-w32-S0-$SEED.txt && echo "S0 null $SEED: BYTE-IDENTICAL" || echo "S0 null $SEED: DIFFERS"
done
