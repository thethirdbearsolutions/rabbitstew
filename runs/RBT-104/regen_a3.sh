#!/bin/bash
# RBT-104 readout, step 2 (coordinator 23:15 and 00:25): regenerate the Amendment 3 window readings.
# For each S8 arm: restore ckpt/rbt-104-S8-SEED (600/600) into a scratch directory, run integration's
# peek.py (Amendment 3) at the pre-registered windows, and write runs/RBT-104/S8-SEED/peek-a3-{300,599}.txt.
# A reading that does not end in a WINDOW verdict line is not written (A4: the readout then reads NOT
# READ for the FALSIFIED branch, never F-b). The launch-commit peek-{300,599}.txt are left untouched.
#
#   runs/RBT-104/regen_a3.sh SCRATCH_DIR [SEED ...]
set -u
SCR=$1; shift
SEEDS=${*:-801 804 805 806 807 1 2 3 4 7}
for s in $SEEDS; do
  d="$SCR/S8-$s"
  rm -rf "$d"
  if ! scripts/durable.sh restore "$d" "rbt-104-S8-$s" > "$SCR/restore-$s.log" 2>&1; then
    echo "seed $s: restore FAILED (see $SCR/restore-$s.log); nothing written"; continue
  fi
  grep -h "WARNING" "$SCR/restore-$s.log" | sed "s/^/seed $s restore: /"
  for w in 300 599; do
    out="runs/RBT-104/S8-$s/peek-a3-$w.txt"
    tmp="$SCR/peek-a3-$s-$w.txt"
    python runs/RBT-104/peek.py "$d" "$s" --season "$w" > "$tmp" 2> "$SCR/peek-$s-$w.err"
    if grep -q "^WINDOW seed $s season $w: .* k_bare = " "$tmp"; then
      sed "s#$d#ckpt/rbt-104-S8-$s (restored)#" "$tmp" > "$out"
      echo "seed $s season $w: $(grep '^WINDOW' "$out")"
    else
      echo "seed $s season $w: NO VALID READING (not written); $(tail -1 "$SCR/peek-$s-$w.err")"
      rm -f "$out"
    fi
  done
  rm -rf "$d"
done
