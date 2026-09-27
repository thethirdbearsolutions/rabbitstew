#!/usr/bin/env bash
# RBT-111: one arm of the arena's three-salt A/A (salts 0, 1, 2), resumable, then the analysis toolkit on it.
#   scripts/rbt111_run.sh SEED s0|s1|s2 [WORKERS]
# The configuration is RBT-96's (scripts/rbt96_run.sh) exactly, which is RBT-85's unprotected arm; the three arms
# differ in --holistic-stream-salt alone (0, 1 or 2), so each meets the same wheeled population on the same
# terrains with an independently drawn holistic population.  RBT-96's scripts are left byte-identical, so
# RBT-96 and RBT-108 still re-derive from them; tests/test_rbt111.py pins this file's evolve arguments to
# rbt96_run.sh's.  Output goes to runs/RBT-111/ARM-SEED/, the log to run.log there.
set -euo pipefail
SEED=$1; ARM=$2; WORKERS=${3:-1}
OUT=runs/RBT-111/$ARM-$SEED
case $ARM in
  s0) SALT=0 ;;
  s1) SALT=1 ;;
  s2) SALT=2 ;;
  *) echo "arm must be s0, s1 or s2" >&2; exit 2 ;;
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
