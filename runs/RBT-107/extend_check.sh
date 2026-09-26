#!/bin/bash
# RBT-107 item 2: is "resume a finished arm with a larger --seasons" byte-identical to having run it longer?
#
#   runs/RBT-107/extend_check.sh throwaway DIR   three 20-season pairs at seed 801 on RBT-92's command
#                                                (plain = RBT-90 part 2, C4 shift at 5, cull 5/5 at 5):
#                                                  long  = --seasons 20, uninterrupted;
#                                                  ext   = --seasons 10 to its natural end, then --resume --seasons 20.
#   runs/RBT-107/extend_check.sh compare DIR     sha256 of lineage.jsonl, cohorts.jsonl, history.json, state.json,
#                                                seasons.txt/lineage-last.txt (tables.py) and every genome, long vs ext.
#   runs/RBT-107/extend_check.sh ckpt LABEL DIR  a real short checkpoint: restore ckpt/LABEL, resume to 600, write its
#                                                tables, and diff them against the committed arm's (the replayed seasons
#                                                must reproduce the committed tables byte for byte).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
BASE="--capacity 60 --challenge foraging --group-size 4 --workers ${WORKERS:-1} \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed 801"
declare -A EV=([plain]="" [shift]="--shift-at 5 --shift terrain=flat" [cull]="--cull-at 5 --cull holistic=5,conventional=5")
case "$1" in
throwaway)
  D=$2; mkdir -p "$D"
  for a in plain shift cull; do
    ( python -m rabbitstew.cli ecology --seasons 20 $BASE ${EV[$a]} --out "$D/$a-long" > "$D/$a-long.log" 2>&1 ) &
    ( python -m rabbitstew.cli ecology --seasons 10 $BASE ${EV[$a]} --out "$D/$a-ext" > "$D/$a-ext.log" 2>&1 &&
      python -m rabbitstew.cli ecology --resume --seasons 20 --out "$D/$a-ext" >> "$D/$a-ext.log" 2>&1 ) &
  done
  wait ;;
compare)
  D=$2; st=0
  for a in plain shift cull; do
    for r in long ext; do python "$ROOT/runs/RBT-92/tables.py" "$D/$a-$r" > /dev/null; done
    for f in lineage.jsonl cohorts.jsonl history.json state.json seasons.txt lineage-last.txt; do
      x=$(sha256sum < "$D/$a-long/$f" | cut -c1-16); y=$(sha256sum < "$D/$a-ext/$f" | cut -c1-16)
      [ "$x" = "$y" ] && v=IDENTICAL || { v=DIFFER; st=1; }
      echo "$a $f long $x ext $y $v"
    done
    # genomes at birth (what the garden reads) and the champions: the same set, byte for byte
    x=$(cd "$D/$a-long" && find holistic conventional -name '*.json' -not -path '*/final/*' | sort | xargs cat | sha256sum | cut -c1-16)
    y=$(cd "$D/$a-ext" && find holistic conventional -name '*.json' -not -path '*/final/*' | sort | xargs cat | sha256sum | cut -c1-16)
    nx=$(cd "$D/$a-long" && find holistic conventional -name '*.json' -not -path '*/final/*' | wc -l); ny=$(cd "$D/$a-ext" && find holistic conventional -name '*.json' -not -path '*/final/*' | wc -l)
    [ "$x" = "$y" ] && [ "$nx" = "$ny" ] && v=IDENTICAL || { v=DIFFER; st=1; }
    echo "$a genomes/ + best_gen*.json ($nx/$ny files) long $x ext $y $v"
    # final/: the end-of-run population dump, one file per living member (Ecology._save_populations).  The first end
    # (season 10) wrote more members than the second overwrites, so its higher-numbered files remain: stale, never
    # read by --resume (state.json carries the population), and not read by anything in RBT-107.
    bad=0; extra=0
    for f in $(cd "$D/$a-ext" && find holistic conventional -path '*/final/*' -name '*.json' | sort); do
      if [ -e "$D/$a-long/$f" ]; then cmp -s "$D/$a-long/$f" "$D/$a-ext/$f" || bad=$((bad + 1)); else extra=$((extra + 1)); fi
    done
    missing=$(cd "$D/$a-long" && for f in $(find holistic conventional -path '*/final/*' -name '*.json'); do [ -e "$D/$a-ext/$f" ] || echo x; done | wc -l)
    [ $bad = 0 ] && [ "$missing" = 0 ] && v=IDENTICAL || { v=DIFFER; st=1; }
    echo "$a final/ dump: every file of the longer run's dump identical in ext ($bad differ, $missing missing) $v; $extra stale extra files in ext from its first end"
    echo "$a seasons.txt rows: long $(($(wc -l < "$D/$a-long/seasons.txt") - 1)) ext $(($(wc -l < "$D/$a-ext/seasons.txt") - 1))"
  done
  [ $st = 0 ] && echo "EXTEND-CHECK PASS: resume-and-extend is byte-identical to the longer uninterrupted run on all three arms" \
              || echo "EXTEND-CHECK FAIL"
  exit $st ;;
ckpt)
  L=$2; D=$3; ARMDIR=$4
  "$ROOT/scripts/durable.sh" restore "$D" "$L"
  echo "restored $L at $(python -c "import json;print(json.load(open('$D/state.json'))['season'])")"
  python -m rabbitstew.cli ecology --resume --seasons 600 --workers "${WORKERS:-1}" --out "$D" > "$D/resume.log" 2>&1
  python "$ROOT/runs/RBT-92/tables.py" "$D" > /dev/null
  st=0
  for f in seasons.txt lineage-last.txt bodysig.txt events.txt groups.txt; do
    if cmp -s "$D/$f" "$ROOT/$ARMDIR/$f"; then echo "$L $f: IDENTICAL to committed $ARMDIR/$f"; else echo "$L $f: DIFFERS from committed $ARMDIR/$f"; st=1; fi
  done
  [ $st = 0 ] && echo "CKPT-CHECK PASS $L" || echo "CKPT-CHECK FAIL $L"
  exit $st ;;
*) sed -n 2,14p "$0"; exit 2 ;;
esac
