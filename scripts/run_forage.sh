#!/bin/bash
# Foraging ecology.  usage: run_forage.sh SEED SEASONS BASAL WORKCOST [EXTRA...]   (env NAME overrides the run name, default "forage")
seed=$1; seasons=$2; basal=$3; work=$4; shift 4; extra="$@"
name=${NAME:-forage}
mkdir -p eco
./v/bin/rabbitstew ecology --seasons $seasons --capacity 60 --challenge foraging --group-size 4 --workers 1 \
  --brain-model foraging --food-items ${ITEMS:-12} --food-radius 3 --eat-radius 0.35 --food-decay 1.0 --work-cost $work \
  --living-cost $basal --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start --score food \
  --seed $seed $extra --out eco/$name-$seed > eco/$name-$seed.log 2>&1
