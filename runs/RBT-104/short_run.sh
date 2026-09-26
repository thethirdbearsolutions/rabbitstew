#!/bin/bash
# RBT-104 throwaway checks: RBT-90 part 2's command (runs/RBT-90/part2_run.sh), unchanged, for a
# short run, with any extra flags appended.  Used for the byte-identity check of --link-scale at
# its default and for the side-by-side at a raised value.  Not an arm: arms use run_arm.sh.
#
#   runs/RBT-104/short_run.sh SEED SEASONS OUT [extra flags...]
set -e
SEED=$1; SEASONS=$2; OUT=$3; shift 3
mkdir -p "$OUT"
exec python -m rabbitstew.cli ecology --seasons "$SEASONS" --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-4}" \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" --out "$OUT" "$@" > "$OUT/run.log" 2>&1
