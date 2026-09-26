#!/bin/bash
# RBT-101, epoch C4 (the furniture removed): one arm of one seed.  RBT-92's launcher (runs/RBT-92/run_arm.sh)
# with the challenge flag changed and nothing else: the dense foraging baseline exactly as RBT-90 part 2 runs
# it (runs/RBT-90/part2_run.sh; docs/held-out-challenges.md section 1), plus ONE event flag pair:
#
#   shift   --shift-at T --shift terrain=flat                C4 of RBT-89: the fourteen random obstacles removed
#   cull    --cull-at  T --cull holistic=K1,conventional=K2  the null: K by RBT-89 section 8's rule, read from
#                                                            runs/RBT-101/cull-k-SEED.txt (RBT-92's cull_k.py
#                                                            on this ticket's shift arm)
#
# cull20 is not run here: it carries no challenge flag, so it is the same arm for every challenge at the same
# seed and T, and RBT-92's runs/RBT-92/cull20-SEED is cited (PREREGISTRATION.md section 7).
# T is the seed's onset from runs/RBT-92/onset.txt (same seeds, same baselines, same rule).  The seed's RBT-90
# part 2 arm is the no-event baseline: byte-identical before T (runs/RBT-92/shared_baseline_check.txt), and a
# terrain shift keeps its start seeds after T (runs/RBT-101/start_seed_check.txt).
#
#   WORKERS=4 runs/RBT-101/run_arm.sh SEED ARM        ->  runs/RBT-101/ARM-SEED/
#
# Launch as a harness background task, never nohup, with scripts/durable.sh every 20 beside it
# (label rbt-101-ARM-SEED).  Afterwards: python runs/RBT-92/tables.py runs/RBT-101/ARM-SEED
#                                        python runs/RBT-101/wiring.py runs/RBT-101/ARM-SEED
set -e
SEED=$1
ARM=$2
HERE=$(cd "$(dirname "$0")" && pwd)
ONSET="$HERE/../RBT-92/onset.txt"
[ -n "$SEED" ] && [ -n "$ARM" ] || { echo "usage: run_arm.sh SEED {shift|cull}" >&2; exit 2; }
T=$(awk -v s="$SEED" '$1 == s && $2 ~ /^[0-9]+$/ {print $2}' "$ONSET" 2>/dev/null)
[ -n "$T" ] || { echo "no onset for seed $SEED in $ONSET (python runs/RBT-92/onset.py after the seed's RBT-90 arm has finished)" >&2; exit 2; }
case "$ARM" in
  shift)  EVENT="--shift-at $T --shift terrain=flat" ;;
  cull)
    KF="$HERE/cull-k-$SEED.txt"
    K=$(awk '$1 == "cull" {print $2}' "$KF" 2>/dev/null)
    [ -n "$K" ] || { echo "no $KF: python runs/RBT-92/cull_k.py $SEED runs/RBT-101/shift-$SEED > $KF once the shift arm has run T+10 seasons" >&2; exit 2; }
    EVENT="--cull-at $T --cull $K" ;;
  *) echo "ARM must be shift or cull" >&2; exit 2 ;;
esac
OUT=runs/RBT-101/$ARM-$SEED
mkdir -p "$OUT"
echo "RBT-101 seed $SEED arm $ARM: T=$T event: $EVENT" > "$OUT/event.txt"
exec python -m rabbitstew.cli ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" $EVENT --out "$OUT" >> "$OUT/run.log" 2>&1
