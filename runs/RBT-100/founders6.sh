#!/bin/bash
# RBT-100 (C3), adversary round 1 F5(a): random founders at six items from season 0, per seed of the seed
# rule, on the head's generator: the "bootstrap line" endpoint that C3's question ("whether an established
# population holds where random founders could not") is read against, seed by seed.  The ecology command of
# runs/RBT-100/run_arm.sh with --food-items 6 from season 0 and --seasons 60 (one max_age; the doc's six-item
# designed population went extinct at 51), no event.  The adversary's P2 (runs/RBT-100/adversary/
# founders6_run.sh) is this command at 40 seasons.
#   WORKERS=4 runs/RBT-100/founders6.sh SEED   ->  runs/RBT-100/founders6-SEED/
# tables.py runs as a post-run step (seasons.txt is what the readout reads).
set -e
SEED=$1
[ -n "$SEED" ] || { echo "usage: founders6.sh SEED" >&2; exit 2; }
OUT=runs/RBT-100/founders6-$SEED
mkdir -p "$OUT"
echo "RBT-100 seed $SEED arm founders6: --food-items 6 from season 0, 60 seasons, no event" > "$OUT/event.txt"
python -m rabbitstew.cli ecology --seasons 60 --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
  --brain-model foraging --food-items 6 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" --out "$OUT" >> "$OUT/run.log" 2>&1
python "$(cd "$(dirname "$0")" && pwd)/../RBT-92/tables.py" "$OUT" >> "$OUT/run.log" 2>&1
