#!/bin/bash
# RBT-107 H-REP readout adversary: independent restore -> cut -> tables -> compare, for a few fresh seeds.
#   runs/RBT-107/hrep/adversary/spotcheck.sh HREP_DIR SCRATCH SEED... [--garden SEED KIND]
# Run from a checkout of #338's head (it needs HREP_DIR = runs/RBT-107/hrep with the committed tables and garden).
# NO-PEEK: nothing read or printed here is from a season after 470.  The restored copy holds later seasons on disk; the
# cut runs before any table is written, restore's own "restored at season X" line is discarded, and the only outputs are
# byte comparisons against the committed cut tables and garden parts plus independent checks that every row is <= 470.
set -e
HREP=$(cd "$1" && pwd); SCR=$2; shift 2
REPO=$(cd "$HREP/../../.." && pwd); cd "$REPO"
mkdir -p "$SCR"
GARDEN=()
SEEDS=()
while [ $# -gt 0 ]; do
  if [ "$1" = "--garden" ]; then GARDEN+=("$2:$3"); shift 3; else SEEDS+=("$1"); shift; fi
done
for SEED in "${SEEDS[@]}"; do
  for A in base shift cull20; do
    D=$SCR/$A-$SEED
    rm -rf "$D"; scripts/durable.sh restore "$D" "rbt-107-fresh-$A-$SEED" > /dev/null 2>&1
    python -c "import json,sys;s=json.load(open('$D/state.json'))['season'];sys.exit(0 if s>=472 else 3)" \
      || { echo "$A-$SEED: checkpoint below 472"; exit 3; }
    python "$HREP/hrep_cut.py" "$D" 470 > /dev/null
    python "$HREP/adversary/cutcheck.py" "$D" 470
    python runs/RBT-92/tables.py "$D" > /dev/null
    for f in seasons.txt lineage-last.txt events.txt; do
      if cmp -s "$D/$f" "$HREP/tables/$A-$SEED/$f"; then r=IDENTICAL; else r=DIFFERS; fi
      echo "$A-$SEED $f: re-cut from the checkpoint vs committed: $r"
    done
  done
done
for GK in "${GARDEN[@]}"; do
  SEED=${GK%%:*}; K=${GK##*:}
  for A in base shift cull20; do
    lab=fresh-$A-$SEED-$K-d110
    for w0 in 0 16; do
      p=$(printf '%s.w%02d-%02d.txt' "$lab" $w0 $((w0 + 15)))
      python runs/RBT-107/garden.py "$SCR/$A-$SEED" "$K" 470 "$lab" --draws 16 --world-start $w0 --workers "${WORKERS:-4}" > "$SCR/$p"
      if diff -q <(grep -v '^#' "$SCR/$p") <(grep -v '^#' "$HREP/garden/parts/$p") > /dev/null; then r=IDENTICAL; else r=DIFFERS; fi
      echo "garden $p: re-run rows vs committed rows: $r ($(grep -vc '^#' "$SCR/$p") rows)"
    done
  done
done
echo SPOTCHECK-DONE
