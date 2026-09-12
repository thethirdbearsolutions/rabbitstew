#!/bin/bash
# Foraging ecology.  usage: run_forage.sh SEED SEASONS BASAL WORKCOST [EXTRA...]
seed=$1; seasons=$2; basal=$3; work=$4; shift 4; extra="$@"
mkdir -p eco
./v/bin/rabbitstew ecology --seasons $seasons --capacity 60 --challenge foraging --group-size 4 --workers 1 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 --work-cost $work \
  --living-cost $basal --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start --score food \
  --seed $seed $extra --out eco/${NAME:-forage}-$seed > eco/${NAME:-forage}-$seed.log 2>--seed $seed $extra --out eco/forage-$seed > eco/forage-$seed.log 2>&11
