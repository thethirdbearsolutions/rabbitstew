#!/bin/bash
# RBT-92 adversary probe C: one throwaway seed (9902, not in the ten), the RBT-92 baseline command
# (run_arm.sh's, 230 seasons) twice: plain, and --shift-at 150 --shift group-size=8.  Read by
# probe_shift_dynamics.py for demography, energy, remainder groups and the body digest only; the
# income columns are not read.  Bulk under runs/RBT-92/data/ (ignored); only the readout is committed.
#   runs/RBT-92/adversary/probe_runs.sh   ->  runs/RBT-92/data/probe-{plain,shift}-9902/
set -e
SEED=9902
BASE="--seasons 230 --capacity 60 --challenge foraging --group-size 4 --workers ${WORKERS:-2} \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed $SEED"
D=runs/RBT-92/data
mkdir -p $D/probe-plain-$SEED $D/probe-shift-$SEED
python -m rabbitstew.cli ecology $BASE --out $D/probe-plain-$SEED > $D/probe-plain-$SEED/run.log 2>&1 &
python -m rabbitstew.cli ecology $BASE --shift-at 150 --shift group-size=8 --out $D/probe-shift-$SEED > $D/probe-shift-$SEED/run.log 2>&1 &
wait
echo done
