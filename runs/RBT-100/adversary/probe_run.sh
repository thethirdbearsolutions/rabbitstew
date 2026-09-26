#!/bin/bash
# RBT-100 adversary probe P1: the C3 shift on a seed outside RBT-92's ten (901), onset at season 100
# (not the registered T of 340-400), run to T+60. Arms: plain and shift. Same ecology command as
# runs/RBT-100/run_arm.sh except --seasons 160. A probe of the design's timing claims (sections 3.3, 4),
# not a C3 result, and read for nothing about the registered arms' class.
#   WORKERS=2 runs/RBT-100/adversary/probe_run.sh 901 {plain|shift}
set -e
SEED=$1; ARM=$2; T=${T:-100}
case "$ARM" in plain) EVENT="" ;; shift) EVENT="--shift-at $T --shift food-items=6" ;; *) exit 2 ;; esac
OUT=runs/RBT-100/data/probe-$ARM-$SEED
mkdir -p "$OUT"
exec python -m rabbitstew.cli ecology --seasons 160 --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" $EVENT --out "$OUT" >> "$OUT/run.log" 2>&1
