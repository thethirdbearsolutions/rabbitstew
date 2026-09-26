#!/bin/bash
# RBT-107, the extra-seed option: can a new seed's shift and cull20 arms FORK from its base at T - 1 instead of re-running
# the shared prefix?  The fork is the base's directory at the end of season T - 1, copied, with ecology.shift_at/shift
# (or cull_at/cull) written into config.json, then --resume.  Ecology.resume builds the ecology from config.json, so the
# event is resolved there; before T nothing differs.  Checked here against a fresh run with the flag, at seed 801:
#   runs/RBT-107/fork_check.sh run DIR       fresh shift-at 12 and cull-at 12 (20/20) runs to 20 seasons; a base to 12,
#                                            forked twice and resumed to 20
#   runs/RBT-107/fork_check.sh compare DIR   sha256 of every file that matters, fresh vs fork
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
BASE="--capacity 60 --challenge foraging --group-size 4 --workers ${WORKERS:-1} \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed 801"
case "$1" in
run)
  D=$2; mkdir -p "$D"
  ( python -m rabbitstew.cli ecology --seasons 20 $BASE --shift-at 12 --shift terrain=flat --out "$D/shift-fresh" > "$D/shift-fresh.log" 2>&1 ) &
  ( python -m rabbitstew.cli ecology --seasons 20 $BASE --cull-at 12 --cull holistic=20,conventional=20 --out "$D/cull20-fresh" > "$D/cull20-fresh.log" 2>&1 ) &
  python -m rabbitstew.cli ecology --seasons 12 $BASE --out "$D/base" > "$D/base.log" 2>&1
  python "$HERE/fork.py" "$D/base" "$D/shift-fork" shift
  python "$HERE/fork.py" "$D/base" "$D/cull20-fork" cull20
  ( python -m rabbitstew.cli ecology --resume --seasons 20 --out "$D/shift-fork" >> "$D/shift-fork.log" 2>&1 ) &
  ( python -m rabbitstew.cli ecology --resume --seasons 20 --out "$D/cull20-fork" >> "$D/cull20-fork.log" 2>&1 ) &
  wait ;;
compare)
  D=$2; st=0
  for a in shift cull20; do
    for r in fresh fork; do python "$ROOT/runs/RBT-92/tables.py" "$D/$a-$r" > /dev/null; done
    for f in lineage.jsonl cohorts.jsonl history.json state.json seasons.txt lineage-last.txt events.txt; do
      x=$(sha256sum < "$D/$a-fresh/$f" | cut -c1-16); y=$(sha256sum < "$D/$a-fork/$f" | cut -c1-16)
      [ "$x" = "$y" ] && v=IDENTICAL || { v=DIFFER; st=1; }
      echo "$a $f fresh $x fork $y $v"
    done
    x=$(cd "$D/$a-fresh" && find holistic conventional -name '*.json' -not -path '*/final/*' | sort | xargs cat | sha256sum | cut -c1-16)
    y=$(cd "$D/$a-fork" && find holistic conventional -name '*.json' -not -path '*/final/*' | sort | xargs cat | sha256sum | cut -c1-16)
    [ "$x" = "$y" ] && v=IDENTICAL || { v=DIFFER; st=1; }
    echo "$a genomes/ + best_gen*.json fresh $x fork $y $v"
    python - "$D/$a-fresh/config.json" "$D/$a-fork/config.json" <<'PY' || st=1
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:])
diff = sorted(k for k in set(a["ecology"]) | set(b["ecology"]) if a["ecology"].get(k) != b["ecology"].get(k))
rest = sorted(k for k in set(a) | set(b) if k not in ("ecology", "generations") and a.get(k) != b.get(k))
# "generations" is the CLI's copy of the first --seasons (cli.py: generations=args.seasons); --resume never rewrites it,
# the ecology never reads it (it runs to ecology.seasons), and only durable.sh's ARENA branch does.  Same in extend_check.
print(f"config.json: ecology fields differing {diff or 'none'}; other fields differing {rest or 'none'} "
      f"(generations, metadata: fresh {a.get('generations')} fork {b.get('generations')})")
sys.exit(1 if diff or rest else 0)
PY
  done
  [ $st = 0 ] && echo "FORK-CHECK PASS: a fork of the base at T - 1 is byte-identical to a fresh run with the event" || echo "FORK-CHECK FAIL"
  exit $st ;;
*) sed -n 2,9p "$0"; exit 2 ;;
esac
