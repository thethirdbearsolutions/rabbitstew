#!/bin/bash
# RBT-107 H1 adversary: re-garden a few #376 units from the checkpoints and compare data rows with the committed parts.
# Print only: writes to SCRATCH, never to garden/readout/.  Run from a checkout of #376's head:
#   SCRATCH=/some/tmp WORKERS=4 runs/RBT-107/h1-adversary/spot_garden.sh
# Units: ARM SEED KIND SEASON LABEL-SUFFIX HALF(0|16).  Each restores a fresh copy, cuts it to 1160 (hrep_cut.py, as
# h1_run.sh), writes its tables, gardens one half, and compares md5 of the non-'#' rows with the committed part.
set -e
SCR=${SCRATCH:-/tmp/rbt107-h1-adv}
W=${WORKERS:-4}
mkdir -p "$SCR/out"
OUTD=runs/RBT-107/garden/readout
while read -r A SEED K SEASON LAB W0; do
  D=$SCR/$A-$SEED
  if [ ! -e "$D/.ready" ]; then
    rm -rf "$D"; scripts/durable.sh restore "$D" "rbt-107-fresh-$A-$SEED" > /dev/null
    python runs/RBT-107/hrep/hrep_cut.py "$D" 1160 > /dev/null
    python runs/RBT-92/tables.py "$D" > /dev/null
    touch "$D/.ready"
  fi
  part=$(printf '%s.w%02d-%02d.txt' "$LAB" "$W0" $((W0 + 15)))
  python runs/RBT-107/garden.py "$D" "$K" "$SEASON" "$LAB" --draws 16 --world-start "$W0" --workers "$W" > "$SCR/out/$part"
  a=$(grep -v '^#' "$SCR/out/$part" | md5sum | cut -c1-32); b=$(grep -v '^#' "$OUTD/parts/$part" | md5sum | cut -c1-32)
  n=$(grep -vc '^#' "$SCR/out/$part" || true)
  echo "$part rows $n re-run $a committed $b $([ "$a" = "$b" ] && echo IDENTICAL || echo DIFFERENT)"
done <<'UNITS'
shift 11 conventional 1160 fresh-shift-11-conventional-d800 0
cull20 20 holistic 1160 fresh-cull20-20-holistic-d800 16
base 27 conventional 760 fresh-base-27-conventional-d400 0
shift 24 holistic 960 fresh-shift-24-holistic-d600 16
base 15 holistic 359 fresh-c0-15-holistic 0
UNITS
