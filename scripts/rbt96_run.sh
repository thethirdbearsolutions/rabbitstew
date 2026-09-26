#!/usr/bin/env bash
# RBT-96: one arm of the arena's A/A pair, resumable, then the analysis toolkit on it (the opponent
# covariate is read from analysis.json).
#   scripts/rbt96_run.sh SEED s0|s1 [WORKERS]
# The configuration is RBT-85's unprotected arm exactly (scripts/rbt85_run.sh, no --protect-morphology);
# the two arms differ in --holistic-stream-salt alone (0 or 1), so they meet the same wheeled population
# on the same terrains with an independently drawn holistic population, and no manipulation.
# Arm s0 is RBT-85's base-SEED configuration byte for byte (salt 0 is the unsalted stream).
# Output goes to runs/RBT-96/ARM-SEED/, the log to run.log there.
set -euo pipefail
SEED=$1; ARM=$2; WORKERS=${3:-1}
OUT=runs/RBT-96/$ARM-$SEED
case $ARM in
  s0) SALT=0 ;;
  s1) SALT=1 ;;
  *) echo "arm must be s0 or s1" >&2; exit 2 ;;
esac
mkdir -p "$OUT"
if [ -d "$OUT/holistic/final" ]; then
  echo "$OUT already ran to its last generation; analysing only" >> "$OUT/run.log"
elif [ -f "$OUT/state.json" ]; then
  rabbitstew evolve --resume --workers "$WORKERS" --out "$OUT" >> "$OUT/run.log" 2>&1
else
  rabbitstew evolve --generations 250 --population 20 --duration 15 --mass-budget 15.34 \
    --conventional-topology --brain-model rich --terrain random \
    --champion-interval 5 --champions 5 --champion-mode roundrobin \
    --seed "$SEED" --workers "$WORKERS" --holistic-stream-salt "$SALT" --out "$OUT" >> "$OUT/run.log" 2>&1
fi
if [ ! -f "$OUT/analysis.json" ]; then
  rabbitstew analyze "$OUT" --every 5 --lesions final --workers "$WORKERS" >> "$OUT/analyze.log" 2>&1
fi
echo "done $ARM-$SEED"
