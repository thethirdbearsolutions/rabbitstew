#!/bin/bash
# RBT-107 Amendment 2 (F3, F4): the design-stage garden at J = 32 worlds, and RBT-105's deep A/A, before any arm.
#
#   WORKERS=4 runs/RBT-107/design_j32.sh SHARD NSHARD SCRATCH     run the units with index = SHARD (mod NSHARD)
#   runs/RBT-107/design_j32.sh merge                              merge parts into runs/RBT-107/garden/j32/ (all shards in)
#
# Units (population x world range), all no-event populations; no C4 shift arm is read:
#   c0-SEED-KIND, base-SEED-KIND-s599, cull20-SEED-KIND-s599   (the ten old seeds, both faunas) on worlds 8..15 and 16..31;
#       worlds 0..7 are the committed design-stage files in garden/ (garden.py is deterministic: re-running c0-801-holistic
#       reproduced its committed rows exactly), so 0..7 + 8..15 + 16..31 = 32 worlds, split-half 0..15 against 16..31
#   aa105-SEED-bK-holistic-s599   RBT-105's founder-sharing replicates (K = 1, 2; 8 seeds), holistic, season 599, on
#       worlds 0..15 and 16..31; their original is base-SEED-holistic-s599 above
# Bulk comes from the checkpoints (restored under SCRATCH); tables are always the committed ones (README rule 6), copied
# over the restored ones.  ckpt/rbt-92-cull20-806 stops at 565: it is replayed to 600 first (ckpt_replay.txt: byte-identical).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
cd "$REPO"
PARTS=$HERE/garden/parts
OLD="801 804 805 806 807 1 2 3 4 7"
AA="1 2 4 7 804 805 806 807"
units() {  # one line per unit: LABEL ARM SEED KIND SEASON W0 J
  for s in $OLD; do
    T=$(awk -v s="$s" '$1 == s && $2 ~ /^[0-9]+$/ {print $2}' runs/RBT-92/onset.txt)
    for k in holistic conventional; do
      for r in "8 8" "16 16"; do
        echo "c0-$s-$k base $s $k $((T - 1)) $r"
        echo "base-$s-$k-s599 base $s $k 599 $r"
        echo "cull20-$s-$k-s599 cull20 $s $k 599 $r"
      done
    done
  done
  for s in $AA; do for K in 1 2; do for r in "0 16" "16 16"; do
    echo "aa105-$s-b$K-holistic-s599 aa$K $s holistic 599 $r"
  done; done; done
}
prep() {  # ARM SEED SCRATCH -> echo the run dir
  local arm=$1 s=$2 d label src
  case "$arm" in
    base)   d=$3/base-$s;     label=rbt-90-$s;        src=runs/RBT-90/forage-$s ;;
    cull20) d=$3/cull20-$s;   label=rbt-92-cull20-$s; src=runs/RBT-92/cull20-$s ;;
    aa*)    d=$3/aa-$s-b${arm#aa}; label=rbt-105-$s-b${arm#aa}; src=runs/RBT-105/forage-$s-b${arm#aa} ;;
  esac
  if [ ! -e "$d/.ready" ]; then
    scripts/durable.sh restore "$d" "$label" >&2
    local at; at=$(python -c "import json;print(json.load(open('$d/state.json'))['season'])")
    if [ "$at" -lt 600 ]; then python -m rabbitstew.cli ecology --resume --seasons 600 --workers "${WORKERS:-1}" --out "$d" > "$d/replay.log" 2>&1; fi
    for f in seasons.txt lineage-last.txt events.txt; do [ -e "$src/$f" ] && cp "$src/$f" "$d/$f"; done
    touch "$d/.ready"
  fi
  echo "$d"
}
if [ "$1" = merge ]; then
  mkdir -p "$HERE/garden/j32"
  for lab in $(units | awk '{print $1}' | sort -u); do
    p=$(ls "$PARTS/$lab".w*.txt 2>/dev/null | sort)
    case "$lab" in aa105-*) base="" ;; *) base="$HERE/garden/$lab.txt" ;; esac
    python "$HERE/garden_merge.py" "$HERE/garden/j32/$lab.txt" $base $p
  done
  exit 0
fi
SHARD=$1; N=$2; SCR=$3
mkdir -p "$PARTS" "$SCR"
i=0
units | while read -r lab arm s k season w0 J; do
  if [ $((i % N)) -eq "$SHARD" ]; then
    out=$(printf '%s/%s.w%02d-%02d.txt' "$PARTS" "$lab" "$w0" $((w0 + J - 1)))
    if [ ! -s "$out" ]; then
      d=$(prep "$arm" "$s" "$SCR")
      python "$HERE/garden.py" "$d" "$k" "$season" "$lab" --draws "$J" --world-start "$w0" --workers "${WORKERS:-1}" > "$out.part"
      mv "$out.part" "$out"
      echo "wrote $(basename "$out") ($(head -1 "$out" | grep -o '([0-9]* s'))"
    fi
  fi
  i=$((i + 1))
done
