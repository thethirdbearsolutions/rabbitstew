#!/bin/bash
# Wait for the max_age 15 arm, then run the middle point at 30. Two points fit a line; three test it.
cd "$(git rev-parse --show-toplevel)"
while ! grep -q "results in\|everyone died" runs/RBT-60/A15-801.log 2>/dev/null; do sleep 30; done
/tmp/claude-0/venv/bin/rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --max-age 30 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random \
  --random-start --score food --seed 801 --out runs/RBT-60/A30-801 > runs/RBT-60/A30-801.log 2>&1
