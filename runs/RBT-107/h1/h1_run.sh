#!/bin/bash
# RBT-107 H1 (T + 800), as registered (A2.1, A2.2, A2.8, A2.9, the post-H-REP note; garden_run.sh readout), for one fresh seed:
#   WORKERS=4 runs/RBT-107/h1/h1_run.sh SEED
# 1. restore COPIES of the seed's three fresh arms from ckpt/rbt-107-fresh-{base,shift,cull20}-SEED (each at 1200/1200)
#    into SCRATCH; never a live run directory
# 2. cut each copy to season T + 800 = 1160, the last registered read season (hrep/hrep_cut.py; the coordinator's 08:45
#    cut discipline) and write its tables (RBT-92 tables.py); the population alive at a season <= 1160 is the same cut or
#    uncut
# 3. garden_run.sh readout's units and labels, into its registered output garden/readout/: c0 at T - 1 from the base, and
#    base, shift, cull20 at T + 800, 400, 600, both faunas, J = 32 as halves 0..15 and 16..31, merged
# 4. T + 110 and Z10 are H-REP's committed files (hrep/garden/, the same labels), copied, not re-run: H-ALT's increment and
#    the trajectory then use exactly the T + 110 numbers H-REP was scored on (byte-identity checked on a re-run, REPORT.md)
# Outputs (committed): runs/RBT-107/garden/readout/[parts/]fresh-*-SEED-*.txt, z10-fresh-SEED.txt; h1/source/ARM-SEED.txt
set -e
SEED=$1
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../../.." && pwd)
cd "$REPO"
T=360; CUT=$((T + 800))
SCR=${SCRATCH:-/tmp/rbt107-h1}
OUTD=$HERE/../garden/readout
HREP=$HERE/../hrep/garden
mkdir -p "$OUTD/parts" "$HERE/source"
W=${WORKERS:-1}
for A in base shift cull20; do
  D=$SCR/$A-$SEED
  if [ ! -e "$D/.ready" ]; then
    rm -rf "$D"; scripts/durable.sh restore "$D" "rbt-107-fresh-$A-$SEED" > /dev/null
    at=$(python -c "import json;print(json.load(open('$D/state.json'))['season'])")
    [ "$at" -ge "$CUT" ] || { echo "$A-$SEED checkpoint at $at < $CUT" >&2; exit 3; }
    python "$HERE/../hrep/hrep_cut.py" "$D" $CUT
    python runs/RBT-92/tables.py "$D" > /dev/null  # the garden reads the population from the cut copy's lineage-last.txt
    echo "checkpoint ckpt/rbt-107-fresh-$A-$SEED $(git rev-parse --short "origin/ckpt/rbt-107-fresh-$A-$SEED") restored at season $at; cut to $CUT" > "$D/source.txt"
    touch "$D/.ready"
  fi
  cp "$D/source.txt" "$HERE/source/$A-$SEED.txt"
done
unit() {  # RUN KIND SEASON LABEL: both halves, then the merge (garden_run.sh's unit, verbatim)
  local lab=$4
  [ -s "$OUTD/$lab.txt" ] && { echo "have $lab"; return 0; }
  for w0 in 0 16; do
    local p; p=$(printf '%s/parts/%s.w%02d-%02d.txt' "$OUTD" "$lab" $w0 $((w0 + 15)))
    [ -s "$p" ] || { python runs/RBT-107/garden.py "$1" "$2" "$3" "$lab" --draws 16 --world-start $w0 --workers "$W" > "$p.part" && mv "$p.part" "$p"; }
  done
  python runs/RBT-107/garden_merge.py "$OUTD/$lab.txt" "$OUTD/parts/$lab.w00-15.txt" "$OUTD/parts/$lab.w16-31.txt"
}
for K in conventional holistic; do
  for A in shift base cull20; do  # T + 110: H-REP's files
    lab=fresh-$A-$SEED-$K-d110
    cp "$HREP/$lab.txt" "$OUTD/$lab.txt"
    cp "$HREP/parts/$lab.w00-15.txt" "$HREP/parts/$lab.w16-31.txt" "$OUTD/parts/"
  done
done
cp "$HREP/z10-fresh-$SEED.txt" "$OUTD/z10-fresh-$SEED.txt"
for K in conventional holistic; do
  unit "$SCR/base-$SEED" $K $((T - 1)) "fresh-c0-$SEED-$K"
  for D in 800 400 600; do
    for A in shift base cull20; do unit "$SCR/$A-$SEED" $K $((T + D)) "fresh-$A-$SEED-$K-d$D"; done
  done
done
echo "H1-SEED-DONE $SEED"
