#!/bin/bash
# RBT-112 readout adversary: the commands behind ownnull/ and the other probes (POST HOC; nothing here is scored).
# BULK (default /tmp/rbt-112-adv) holds the ten HZ arms restored from ckpt/rbt-112-HZ-SEED and the w = 32 founders.
# Run from the repo root in a clean `pip install -e '.[dev]'` venv (no scipy).
set -e
cd "$(dirname "$0")/../../.."
BULK=${BULK:-/tmp/rbt-112-adv}
A=runs/RBT-112/readout-adversary
mkdir -p "$A/ownnull"
for s in 801 4 804 805 806 807 1 2 3 7; do
  [ -f "$BULK/HZ-$s/lineage.jsonl" ] || scripts/durable.sh restore "$BULK/HZ-$s" "rbt-112-HZ-$s"
  [ -f "$BULK/founders-w32-$s/SHA256SUMS" ] || python runs/RBT-106/founders.py "$s" 32 "$BULK/founders-w32-$s"   # digest checked against founders-digests
  python runs/RBT-112/null_xover_s0.py "$BULK/HZ-$s" "$s" "$BULK/founders-w32-$s" --global-bias-sigma 0 --reps 200 --procs 4 \
    > "$A/ownnull/ownnull-HZ-$s.txt"
done
python $A/ownnull_pool.py $A/ownnull > $A/ownnull_pool.txt
python $A/instrument.py > $A/instrument.txt
python $A/function_robust.py > $A/function_robust.txt
python $A/rederive.py > $A/rederive.txt
for s in 4 805 801 804 807 1 7; do python $A/ancestry.py "$BULK/HZ-$s" "$s"; done > $A/ancestry.txt
# held-300/599 byte identity from the checkpoints: run held.py with the arm path spelled runs/RBT-112/HZ-SEED
# (a symlink to $BULK/HZ-SEED under a scratch root), and cmp against the committed files: 20 of 20 identical.
