#!/bin/bash
# RBT-99 smoke run, read for nothing: two short runs of the dense foraging baseline (RBT-90 part 2's
# command, runs/RBT-90/part2_run.sh, with --seasons 20) at one seed: plain, and C2's shift at 10
# (--shift-at 10 --shift work-cost=0.08).  Compared by smoke_check.py, which confirms the manipulation
# (pre-10 identity with plain; from 10 on, each lineage row's gain is priced at 0.08 per kJ) and reads
# no income contrast.  The bulk goes to runs/RBT-99/data/ (ignored) and is deleted after the check.
#   runs/RBT-99/smoke_runs.sh [SEED]   ->  runs/RBT-99/data/smoke-{plain,shift}-SEED/
set -e
SEED=${1:-801}
BASE="--seasons 20 --capacity 60 --challenge foraging --group-size 4 --workers 2 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed $SEED"
D=runs/RBT-99/data
mkdir -p $D/smoke-plain-$SEED $D/smoke-shift-$SEED
python -m rabbitstew.cli ecology $BASE --out $D/smoke-plain-$SEED > $D/smoke-plain-$SEED/run.log 2>&1 &
python -m rabbitstew.cli ecology $BASE --shift-at 10 --shift work-cost=0.08 --out $D/smoke-shift-$SEED > $D/smoke-shift-$SEED/run.log 2>&1 &
wait
echo done
