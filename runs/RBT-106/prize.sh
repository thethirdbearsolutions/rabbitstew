#!/bin/bash
# RBT-106 section 2: the prize in the ONE-FIELD patchy world, measured, not borrowed.
#
# RBT-103's adversary measured +2.489 for "12 items, 3 patches" on P-801's bodies only, and that world also had
# regrow_delay 45 (a second field, and one that switches the ecology to persistent arenas). The ten part-2
# populations were measured only in P-801's world (26 items, 3 patches, regrow 45): +2.267. So the prize in the
# world this ticket's arms would run in (part 2's config with sim.food.patches = 3 and nothing else) is unmeasured.
# This runs RBT-103's harness, unchanged, on each part-2 population's committed-rule bodies (bests 0..590) with the
# world taken from runs/RBT-106/world-patchy/config.json (--config-from, RBT-103's own world control), a = 32 and
# 64 (w = 16, 32), and the rotated decoy at a = 64. Same seeds as RBT-103 (64 paired from 7000).
#
# Bodies are bulk: restored from ckpt/rbt-90-SEED into a scratch directory (never over runs/RBT-90).
#   runs/RBT-106/prize.sh BODIES_ROOT      (BODIES_ROOT/forage-SEED/conventional/best_gen*.json)
set -e
ROOT=$1
cd "$(dirname "$0")/../.."
mkdir -p runs/RBT-106/prize
# harness check: the restored bodies in their own world must reproduce RBT-103's committed row for 801 to the digit
h=runs/RBT-106/prize/harness-801-uniform.txt
[ -s "$h" ] && grep -q '^ROW' "$h" || python runs/RBT-103/routed_populations.py --run "$ROOT/forage-801" --label 801 \
  --w 16,32 --procs "${PROCS:-4}" > "$h" 2> "$h.err"
for s in 801 804 805 806 807 1 2 3 4 7; do
  out=runs/RBT-106/prize/patchy-$s.txt
  [ -s "$out" ] && grep -q '^ROW' "$out" && continue
  python runs/RBT-103/routed_populations.py --run "$ROOT/forage-$s" --config-from runs/RBT-106/world-patchy \
    --label "$s-in-one-field-patchy" --w 16,32 --decoy 32 --procs "${PROCS:-4}" > "$out.tmp" 2> "$out.err"
  mv "$out.tmp" "$out"
done
python runs/RBT-106/prize.py > runs/RBT-106/prize.txt
