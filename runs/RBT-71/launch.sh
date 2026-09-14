#!/bin/bash
# RBT-71 Deliverable A: the forage-801 baseline (RBT-60's command) with ONE flag changed, the seed,
# plus the paired neutral control of the same world and seed.
#   usage: launch.sh SEED [neutral]
# Writes runs/RBT-71/forage-SEED (or neutral-SEED) and a .log beside it.
cd "$(git rev-parse --show-toplevel)"
seed=$1; kind=${2:-forage}
extra=""; [ "$kind" = "neutral" ] && extra="--neutral"
out=runs/RBT-71/$kind-$seed
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --max-age 60 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random \
  --random-start --score food --seed $seed $extra --out $out > $out.log 2>&1
