#!/bin/bash
# RBT-107 H-REP (T + 110), as registered (A2.2, A2.8, A2.9; garden_run.sh hrep), for one fresh seed:
#   WORKERS=4 runs/RBT-107/hrep/hrep_run.sh SEED
# 1. restore COPIES of the seed's three fresh arms from ckpt/rbt-107-fresh-{base,shift,cull20}-SEED (every one at >= 472:
#    the coordinator's gate, 03:17) into SCRATCH; never a live run directory
# 2. cut each copy back to season 470 (hrep_cut.py) and write its tables (RBT-92 tables.py): no table read past 470
# 3. the J = 32 garden at T + 110 = 470 on base, shift and cull20, both faunas, two halves 0..15 and 16..31, merged
#    (garden.py, garden_merge.py; exactly garden_run.sh hrep's units and labels)
# 4. Z10 (z10.py; reads seasons 359..369 only)
# Outputs (committed): runs/RBT-107/hrep/garden/[parts/]fresh-ARM-SEED-KIND-d110*.txt, z10-fresh-SEED.txt, and the cut tables
# runs/RBT-107/hrep/tables/ARM-SEED/{seasons.txt,lineage-last.txt,events.txt} (seasons 0..470 only).
set -e
SEED=$1
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../../.." && pwd)
cd "$REPO"
T=360; S=$((T + 110))
SCR=${SCRATCH:-/tmp/rbt107-hrep}
OUTD=$HERE/garden
mkdir -p "$OUTD/parts" "$HERE/tables"
W=${WORKERS:-1}
for A in base shift cull20; do
  D=$SCR/$A-$SEED
  if [ ! -e "$D/.ready" ]; then
    rm -rf "$D"; scripts/durable.sh restore "$D" "rbt-107-fresh-$A-$SEED" > /dev/null
    at=$(python -c "import json;print(json.load(open('$D/state.json'))['season'])")
    [ "$at" -ge 472 ] || { echo "$A-$SEED checkpoint at $at < 472" >&2; exit 3; }
    python "$HERE/hrep_cut.py" "$D" $S
    python runs/RBT-92/tables.py "$D" > /dev/null
    touch "$D/.ready"
  fi
  if [ ! -e "$HERE/tables/$A-$SEED/source.txt" ]; then  # also when a cut scratch copy is reused (.ready)
    at=$(python -c "import json;print(json.load(open('$D/state.json'))['season'])")
    mkdir -p "$HERE/tables/$A-$SEED"
    cp "$D/seasons.txt" "$D/lineage-last.txt" "$D/events.txt" "$HERE/tables/$A-$SEED/"
    echo "checkpoint ckpt/rbt-107-fresh-$A-$SEED $(git rev-parse --short "origin/ckpt/rbt-107-fresh-$A-$SEED") restored at season $at; cut to $S" > "$HERE/tables/$A-$SEED/source.txt"
  fi
done
unit() {  # RUN KIND LABEL
  local lab=$3
  [ -s "$OUTD/$lab.txt" ] && return 0
  for w0 in 0 16; do
    local p; p=$(printf '%s/parts/%s.w%02d-%02d.txt' "$OUTD" "$lab" $w0 $((w0 + 15)))
    [ -s "$p" ] || { python runs/RBT-107/garden.py "$1" "$2" $S "$lab" --draws 16 --world-start $w0 --workers "$W" > "$p.part" && mv "$p.part" "$p"; }
  done
  python runs/RBT-107/garden_merge.py "$OUTD/$lab.txt" "$OUTD/parts/$lab.w00-15.txt" "$OUTD/parts/$lab.w16-31.txt" > /dev/null
  echo "garden $lab"
}
for K in conventional holistic; do
  for A in shift base cull20; do unit "$SCR/$A-$SEED" $K "fresh-$A-$SEED-$K-d110"; done
done
python runs/RBT-107/z10.py "$SCR/base-$SEED" "$SCR/shift-$SEED" "$SEED" $T > "$OUTD/z10-fresh-$SEED.txt"
echo "HREP-SEED-DONE $SEED"
