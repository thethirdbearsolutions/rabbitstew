#!/usr/bin/env bash
# RBT-85: one arena run of RBT-74's rerun under per-population RNG streams, resumable, then the
# analysis toolkit on it (the opponent covariate is read from analysis.json).
#   scripts/rbt85_run.sh SEED prot|base [WORKERS]
# The configuration is RBT-74's exactly (scripts/rbt74_run.sh); only the output root differs.
# Output goes to runs/RBT-85/ARM-SEED/, the log to run.log there; watch it with tail, not
# through a pipe.  On macOS the run holds an idle-sleep assertion for as long as it lives.
set -euo pipefail
SEED=$1; ARM=$2; WORKERS=${3:-1}
OUT=runs/RBT-85/$ARM-$SEED
case $ARM in
  prot) EXTRA="--protect-morphology 4" ;;
  base) EXTRA="" ;;
  *) echo "arm must be prot or base" >&2; exit 2 ;;
esac
mkdir -p "$OUT"
KEEP=""; command -v caffeinate >/dev/null 2>&1 && KEEP="caffeinate -i"
if [ -d "$OUT/holistic/final" ]; then
  echo "$OUT already ran to its last generation; analysing only" >> "$OUT/run.log"
elif [ -f "$OUT/state.json" ]; then
  $KEEP rabbitstew evolve --resume --workers "$WORKERS" --out "$OUT" >> "$OUT/run.log" 2>&1
else
  $KEEP rabbitstew evolve --generations 250 --population 20 --duration 15 --mass-budget 15.34 \
    --conventional-topology --brain-model rich --terrain random \
    --champion-interval 5 --champions 5 --champion-mode roundrobin \
    --seed "$SEED" --workers "$WORKERS" $EXTRA --out "$OUT" >> "$OUT/run.log" 2>&1
fi
$KEEP rabbitstew analyze "$OUT" --every 5 --lesions final --workers "$WORKERS" >> "$OUT/analyze.log" 2>&1
echo "done $ARM-$SEED"
