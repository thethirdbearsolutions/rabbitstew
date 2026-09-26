#!/bin/bash
# RBT-101 start-seed check: two short runs of the dense foraging baseline (RBT-90 part 2's command,
# runs/RBT-90/part2_run.sh, with --seasons 20) at one seed: plain, and C4's event at season 10
# (--shift-at 10 --shift terrain=flat). Compared by start_seed_check.py.
#   runs/RBT-101/start_seed_runs.sh [SEED]   ->  runs/RBT-101/data/ssc-{plain,flat}-SEED/
set -e
SEED=${1:-801}
BASE="--seasons 20 --capacity 60 --challenge foraging --group-size 4 --workers 1 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed $SEED"
D=runs/RBT-101/data
mkdir -p $D/ssc-plain-$SEED $D/ssc-flat-$SEED
python -m rabbitstew.cli ecology $BASE --out $D/ssc-plain-$SEED > $D/ssc-plain-$SEED/run.log 2>&1 &
python -m rabbitstew.cli ecology $BASE --shift-at 10 --shift terrain=flat --out $D/ssc-flat-$SEED > $D/ssc-flat-$SEED/run.log 2>&1 &
wait
echo done
