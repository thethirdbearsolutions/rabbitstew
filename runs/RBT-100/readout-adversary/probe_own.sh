#!/bin/bash
# RBT-100 readout adversary: were the committed baseline own tables (runs/RBT-100/base-SEED/own.txt) written from
# 600/600 bulk?  README rule 6: tables are never read from a checkpoint, but they may be regenerated from its bulk.
# For each seed: restore ckpt/rbt-90-SEED into a scratch directory (never into runs/), print the MANIFEST's progress
# and consistency lines, re-run the designer's own_table.py on it, and cmp against the committed own.txt.
#   runs/RBT-100/readout-adversary/probe_own.sh SCRATCH > runs/RBT-100/readout-adversary/probe_own.txt
set -u
S=${1:?scratch dir}
echo "RBT-100 readout adversary: base-SEED/own.txt regenerated from the restored RBT-90 part 2 bulk (README rule 6)"
for seed in 801 804 805 806 807 1 2 3 4 7; do
  D="$S/forage-$seed"; rm -rf "$D" "$S/own-$seed"; mkdir -p "$S/own-$seed"
  scripts/durable.sh restore "$D" "rbt-90-$seed" > "$S/restore-$seed.log" 2>&1
  m=$(git show "origin/ckpt/rbt-90-$seed:MANIFEST" | sed -n '2p;4p' | tr '\n' ' ')
  chk=$(python runs/RBT-100/own_table.py "$D" --to "$S/own-$seed" 2>&1 | tail -1)
  if cmp -s "$S/own-$seed/own.txt" "runs/RBT-100/base-$seed/own.txt"; then r="byte-identical"; else r="DIFFERS ($(diff "$S/own-$seed/own.txt" "runs/RBT-100/base-$seed/own.txt" | grep -c '^>') lines)"; fi
  rows=$(tail -n +2 "runs/RBT-100/base-$seed/own.txt" | wc -l); last=$(tail -1 "runs/RBT-100/base-$seed/own.txt" | cut -f1)
  echo "  $seed: ckpt MANIFEST [$m] ($(tail -1 "$S/restore-$seed.log" | cut -c1-60)); committed own.txt $rows rows, last season $last; regenerated: $r; own_table check: $chk"
  rm -rf "$D"
done | sed "s|$S|SCRATCH|g"
