#!/bin/bash
# RBT-92, the first epoch: one arm of one seed.  The dense foraging baseline exactly as RBT-90 part 2
# runs it (runs/RBT-90/part2_run.sh; docs/held-out-challenges.md section 1), plus ONE event flag pair:
#
#   shift   --shift-at T --shift group-size=8               crowding, C1 of RBT-89
#   cull    --cull-at  T --cull holistic=K1,conventional=K2  the null: K by RBT-89 section 8's rule, read
#                                                            from runs/RBT-92/cull-k-SEED.txt (cull_k.py)
#   cull20  --cull-at  T --cull holistic=20,conventional=20  the instrument's validation cull (RBT-89 section 8,
#                                                            "validation before use", k = 20)
#
# T is the seed's onset from runs/RBT-92/onset.txt (onset.py, the committed rule, applied to the seed's
# finished RBT-90 part 2 arm).  The seed's RBT-90 part 2 arm is the no-event baseline: the arms share it
# byte for byte before T (runs/RBT-92/shared_baseline_check.txt).  WORKERS as in part2_run.sh (default 1;
# 4 on a four-core cloud session; workers do not change a run).
#
#   WORKERS=4 runs/RBT-92/run_arm.sh SEED ARM        ->  runs/RBT-92/ARM-SEED/
#
# Launch as a harness background task, never nohup, with scripts/durable.sh every 20 beside it
# (label rbt-92-ARM-SEED).  Afterwards: python runs/RBT-92/tables.py runs/RBT-92/ARM-SEED
set -e
SEED=$1
ARM=$2
HERE=$(cd "$(dirname "$0")" && pwd)
[ -n "$SEED" ] && [ -n "$ARM" ] || { echo "usage: run_arm.sh SEED {shift|cull|cull20}" >&2; exit 2; }
T=$(awk -v s="$SEED" '$1 == s && $2 ~ /^[0-9]+$/ {print $2}' "$HERE/onset.txt" 2>/dev/null)
[ -n "$T" ] || { echo "no onset for seed $SEED in $HERE/onset.txt (python runs/RBT-92/onset.py after the seed's RBT-90 arm has finished)" >&2; exit 2; }
case "$ARM" in
  shift)  EVENT="--shift-at $T --shift group-size=8" ;;
  cull20) EVENT="--cull-at $T --cull holistic=20,conventional=20" ;;
  cull)
    KF="$HERE/cull-k-$SEED.txt"
    K=$(awk '$1 == "cull" {print $2}' "$KF" 2>/dev/null)
    [ -n "$K" ] || { echo "no $KF: python runs/RBT-92/cull_k.py $SEED once the shift arm has run T+10 seasons" >&2; exit 2; }
    EVENT="--cull-at $T --cull $K" ;;
  *) echo "ARM must be shift, cull or cull20" >&2; exit 2 ;;
esac
OUT=runs/RBT-92/$ARM-$SEED
mkdir -p "$OUT"
echo "RBT-92 seed $SEED arm $ARM: T=$T event: $EVENT" > "$OUT/event.txt"
exec python -m rabbitstew.cli ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" $EVENT --out "$OUT" >> "$OUT/run.log" 2>&1
