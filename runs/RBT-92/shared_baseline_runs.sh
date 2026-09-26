#!/bin/bash
# RBT-92 shared-baseline check: three short runs of the dense foraging baseline (RBT-90 part 2's
# command, runs/RBT-90/part2_run.sh, with --seasons 20) at one seed: plain, shift at 10
# (group-size=8), cull at 10 (holistic=20,conventional=20). Compared by shared_baseline_check.py.
#   runs/RBT-92/shared_baseline_runs.sh [SEED]   ->  runs/RBT-92/data/sbc-{plain,shift,cull}-SEED/
set -e
SEED=${1:-801}
BASE="--seasons 20 --capacity 60 --challenge foraging --group-size 4 --workers 1 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed $SEED"
D=runs/RBT-92/data
mkdir -p $D/sbc-plain-$SEED $D/sbc-shift-$SEED $D/sbc-cull-$SEED
python -m rabbitstew.cli ecology $BASE --out $D/sbc-plain-$SEED > $D/sbc-plain-$SEED/run.log 2>&1 &
python -m rabbitstew.cli ecology $BASE --shift-at 10 --shift group-size=8 --out $D/sbc-shift-$SEED > $D/sbc-shift-$SEED/run.log 2>&1 &
python -m rabbitstew.cli ecology $BASE --cull-at 10 --cull holistic=20,conventional=20 --out $D/sbc-cull-$SEED > $D/sbc-cull-$SEED/run.log 2>&1 &
wait
echo done
