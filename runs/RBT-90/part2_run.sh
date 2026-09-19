#!/bin/bash
# RBT-90 part 2: one arm of the ten-seed baseline sweep.  The dense foraging baseline exactly as
# docs/held-out-challenges.md section 1 quotes it (forage-801's command; RBT-10's own config is not on
# the head, and this command builds a config equal to runs/RBT-28/data/baseline-801/config.json in
# every field that config has, checked before launch).  One flag changes between arms: --seed.
# --workers 1 because ten arms run side by side on ten cores; save_genomes is the default (on).
#
#   runs/RBT-90/part2_run.sh SEED        ->  runs/RBT-90/forage-SEED/
#
# Launched as a harness background task, never with nohup; the log is read directly, not through grep.
set -e
SEED=$1
OUT=runs/RBT-90/forage-$SEED
mkdir -p "$OUT"
exec python -m rabbitstew.cli ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 1 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" --out "$OUT" > "$OUT/run.log" 2>&1
