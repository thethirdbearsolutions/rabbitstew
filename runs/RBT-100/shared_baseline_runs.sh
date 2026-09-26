#!/bin/bash
# RBT-100 (C3) shared-baseline and smoke runs: RBT-92's shared_baseline_runs.sh with the one C3 change,
# three short runs of the dense foraging baseline (runs/RBT-90/part2_run.sh's command with --seasons 20)
# at one seed: plain; shift at 10 (food-items=6, C3); cull at 10 (holistic=20,conventional=20).
# Throwaway: compared by shared_baseline_check.py and used by smoke.sh, read for nothing, never committed.
#   runs/RBT-100/shared_baseline_runs.sh [SEED]   ->  runs/RBT-100/data/sbc-{plain,shift,cull}-SEED/
set -e
SEED=${1:-801}
BASE="--seasons 20 --capacity 60 --challenge foraging --group-size 4 --workers ${WORKERS:-1} \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed $SEED"
D=runs/RBT-100/data
mkdir -p $D/sbc-plain-$SEED $D/sbc-shift-$SEED $D/sbc-cull-$SEED
python -m rabbitstew.cli ecology $BASE --out $D/sbc-plain-$SEED > $D/sbc-plain-$SEED/run.log 2>&1 &
python -m rabbitstew.cli ecology $BASE --shift-at 10 --shift food-items=6 --out $D/sbc-shift-$SEED > $D/sbc-shift-$SEED/run.log 2>&1 &
python -m rabbitstew.cli ecology $BASE --cull-at 10 --cull holistic=20,conventional=20 --out $D/sbc-cull-$SEED > $D/sbc-cull-$SEED/run.log 2>&1 &
wait
echo done
