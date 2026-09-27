#!/bin/bash
# RBT-112: the matched held-null with crossover (null_xover_s0.py) on RBT-106's ten seeds, at the default (must
# reproduce the RBT-106 adversary's committed xnull-w32-SEED.txt below the header) and at --global-bias-sigma 0.
# Part 2's genealogies are restored from ckpt/rbt-90-SEED outside the checkout (P2_ROOT, default /tmp/rbt-112-p2).
set -e
cd "$(dirname "$0")/../.."
P2=${P2_ROOT:-/tmp/rbt-112-p2}
for SEED in 801 804 805 806 807 1 2 3 4 7; do
  [ -f "$P2/$SEED/lineage.jsonl" ] || scripts/durable.sh restore "$P2/$SEED" "rbt-90-$SEED"
  F=runs/RBT-106/founders-w32-$SEED
  [ -f "$F/SHA256SUMS" ] || python runs/RBT-106/founders.py "$SEED" 32 "$F"
  python runs/RBT-112/null_xover_s0.py "$P2/$SEED" "$SEED" "$F" > runs/RBT-112/null/xnull-w32-$SEED.txt
  python runs/RBT-112/null_xover_s0.py "$P2/$SEED" "$SEED" "$F" --global-bias-sigma 0 > runs/RBT-112/null/xnull-w32-S0-$SEED.txt
done
