#!/bin/bash
# RBT-107: the common-garden populations, as registered in Amendment 2 (J = 32 worlds, two halves, merged).
#
#   WORKERS=4 runs/RBT-107/garden_run.sh hrep SEED           H-REP (fresh seeds 11-30 only): the fresh base, shift AND
#                                                            cull20 at T + 110 = 470, both faunas, in one pass, from restored
#                                                            snapshots of the running arms (tables.py is run on the COPY,
#                                                            never on a live directory); plus Z10 (z10.py).  Run it only
#                                                            when ALL 60 fresh arms (waves A, B and C) have a checkpoint at
#                                                            >= 472 (A2.8, coordinator's A8-1 ruling, option 2): the
#                                                            IUT's net-of-null half needs cull20, and nothing is gardened
#                                                            for H-REP before then
#   WORKERS=4 runs/RBT-107/garden_run.sh readout SEED        after the seed's arms have ended, bulk on disk (restored if
#                                                            needed): c0 at T - 1 from the base, and each arm (base, shift,
#                                                            cull20, and RBT-101's k-cull where it ran) at T + 110, 400,
#                                                            600, 800 (and 200, printed, for the old seeds), both faunas
#   WORKERS=4 runs/RBT-107/garden_run.sh aa105 SEED K DIR    see design_j32.sh (the deep A/A is measured before any arm)
#
# Old seeds (RBT-90 part 2's ten): arms in runs/RBT-107/ARM-SEED, T from runs/RBT-92/onset.txt.
# Fresh seeds (11-30): arms in runs/RBT-107/fresh/ARM-SEED, T = 360.
# Every population is run on worlds 0..15 and 16..31 (garden/readout/parts/LABEL.w00-15.txt, .w16-31.txt), then merged
# into garden/readout/LABEL.txt (garden_merge.py); the parts stay committed for the split-half.  A finished part is
# skipped, so a lost container resumes where it stopped.  NO-PEEK: run every read point of a wave in one pass; post no
# number before the readout.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
cd "$REPO"
OUTD=${GARDEN_OUT:-$HERE/garden/readout}
mkdir -p "$OUTD/parts"
W=${WORKERS:-1}
MODE=$1; SEED=$2
if [ "$SEED" -ge 11 ] && [ "$SEED" -le 30 ] 2>/dev/null; then FRESH=1; T=360; ROOT=runs/RBT-107/fresh
else FRESH=; ROOT=runs/RBT-107; T=$(awk -v s="$SEED" '$1 == s && $2 ~ /^[0-9]+$/ {print $2}' runs/RBT-92/onset.txt); fi
[ -n "$T" ] || { echo "no onset for seed $SEED" >&2; exit 2; }
unit() {  # RUN KIND SEASON LABEL [garden.py options]: both halves, then the merge
  local lab=$4
  [ -s "$OUTD/$lab.txt" ] && { echo "have $lab"; return 0; }
  for w0 in 0 16; do
    local p; p=$(printf '%s/parts/%s.w%02d-%02d.txt' "$OUTD" "$lab" $w0 $((w0 + 15)))
    [ -s "$p" ] || { python "$HERE/garden.py" "$1" "$2" "$3" "$lab" --draws 16 --world-start $w0 --workers "$W" "${@:5}" > "$p.part" && mv "$p.part" "$p"; }
  done
  python "$HERE/garden_merge.py" "$OUTD/$lab.txt" "$OUTD/parts/$lab.w00-15.txt" "$OUTD/parts/$lab.w16-31.txt"
}
case "$MODE" in
  hrep)
    [ -n "$FRESH" ] || { echo "H-REP is on the fresh seeds only" >&2; exit 2; }
    SCR=${SCRATCH:-/tmp/rbt107-hrep}
    for A in base shift cull20; do
      D=$SCR/$A-$SEED
      if [ ! -e "$D/.ready" ]; then
        rm -rf "$D"; scripts/durable.sh restore "$D" "rbt-107-fresh-$A-$SEED"
        at=$(python -c "import json;print(json.load(open('$D/state.json'))['season'])")
        [ "$at" -ge 472 ] || { echo "$A-$SEED snapshot at $at < 472: wait for the next save" >&2; exit 3; }
        python runs/RBT-92/tables.py "$D" > /dev/null; touch "$D/.ready"
      fi
    done
    for K in conventional holistic; do
      for A in shift base cull20; do unit "$SCR/$A-$SEED" $K $((T + 110)) "fresh-$A-$SEED-$K-d110"; done
    done
    python "$HERE/z10.py" "$SCR/base-$SEED" "$SCR/shift-$SEED" "$SEED" $T > "$OUTD/z10-fresh-$SEED.txt" ;;
  readout)
    if [ -n "$FRESH" ]; then PFX=fresh-; DS="800 110 400 600"; else PFX=; DS="800 110 400 600 200"; fi
    for K in conventional holistic; do
      unit "$ROOT/base-$SEED" $K $((T - 1)) "${PFX}c0-$SEED-$K"
      for D in $DS; do
        for A in shift base cull20 cull; do
          [ -d "$ROOT/$A-$SEED" ] && unit "$ROOT/$A-$SEED" $K $((T + D)) "${PFX}$A-$SEED-$K-d$D"
        done
      done
    done
    [ -n "$FRESH" ] && python "$HERE/z10.py" "$ROOT/base-$SEED" "$ROOT/shift-$SEED" "$SEED" $T > "$OUTD/z10-fresh-$SEED.txt" || true ;;
  aa105)
    echo "the deep A/A is measured before any arm by design_j32.sh (garden/j32/aa105-*)" ;;
  *) sed -n 2,20p "$0"; exit 2 ;;
esac
