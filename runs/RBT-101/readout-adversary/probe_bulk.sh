#!/bin/bash
# RBT-101 readout adversary: README rule 6.  Restore every baseline (ckpt/rbt-90-SEED) and shift arm
# (ckpt/rbt-101-shift-SEED) into BULKDIR (outside the repository), say at what season each checkpoint stands, and
# regenerate from that bulk: base-SEED/wiring.txt (wiring.py --to) and each shift arm's seasons.txt, lineage-last.txt,
# bodysig.txt, events.txt (RBT-92's tables.py) and wiring.txt; compare each with the committed file.  Where a checkpoint
# stops short of 600, compare the committed table's prefix.  The bulk read by probe_arena.py and probe_refund.py is this.
#   runs/RBT-101/readout-adversary/probe_bulk.sh BULKDIR > runs/RBT-101/readout-adversary/probe_bulk.txt
set -e
B=$1
mkdir -p "$B/regen"
for s in 801 804 805 806 807 1 2 3 4 7; do
  for pair in "base-$s rbt-90-$s" "shift-$s rbt-101-shift-$s"; do
    set -- $pair
    [ -f "$B/$1/state.json" ] || scripts/durable.sh restore "$B/$1" "$2" > /dev/null 2>&1
    git fetch -q origin "+refs/heads/ckpt/$2:refs/remotes/origin/ckpt/$2"
    echo "$1: $(git log -1 --format='%s (%ci)' origin/ckpt/$2 | sed 's|runs/[^ ]* ||')"
  done
done
echo
for s in 801 804 805 806 807 1 2 3 4 7; do
  mkdir -p "$B/regen/base-$s"
  python runs/RBT-101/wiring.py "$B/base-$s" --to "$B/regen/base-$s" > /dev/null 2>&1
  cmp -s "$B/regen/base-$s/wiring.txt" "runs/RBT-101/base-$s/wiring.txt" && r=identical || r=DIFFERS
  echo "base-$s/wiring.txt regenerated from the 600/600 bulk: $r ($(wc -l < runs/RBT-101/base-$s/wiring.txt) lines)"
done
echo
for s in 801 804 805 806 807 1 2 3 4 7; do
  python runs/RBT-92/tables.py "$B/shift-$s" > /dev/null 2>&1
  python runs/RBT-101/wiring.py "$B/shift-$s" > /dev/null 2>&1
  r="shift-$s:"
  for f in seasons.txt lineage-last.txt bodysig.txt events.txt wiring.txt; do
    if cmp -s "$B/shift-$s/$f" "runs/RBT-101/shift-$s/$f"; then r="$r $f=identical"; else
      n=$(wc -l < "$B/shift-$s/$f")
      if [ "$f" = seasons.txt ] && head -n "$n" "runs/RBT-101/shift-$s/$f" | cmp -s - "$B/shift-$s/$f"; then r="$r $f=prefix-identical($n of $(wc -l < runs/RBT-101/shift-$s/$f) lines)"; else r="$r $f=differs"; fi
    fi
  done
  echo "$r"
done
