#!/bin/bash
# RBT-100 adversary probe P2: random founders at six items from season 0 on the head's generator (RBT-95
# streams), 40 seasons: the "bootstrap line" endpoint C3's question is framed against, re-measured on seeds
# other than the one docs/foraging-world.md "Six items" ran (801, pre-RBT-95 generator).  Same ecology command
# as runs/RBT-100/run_arm.sh with --food-items 6 and --seasons 40, no event.
#   WORKERS=1 runs/RBT-100/adversary/founders6_run.sh SEED
set -e
SEED=$1
OUT=runs/RBT-100/data/founders6-$SEED
mkdir -p "$OUT"
exec python -m rabbitstew.cli ecology --seasons 40 --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
  --brain-model foraging --food-items 6 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" --out "$OUT" >> "$OUT/run.log" 2>&1
