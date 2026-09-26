#!/bin/bash
# RBT-107, the extra seeds (PREREGISTRATION Amendment 1): one new founding population, base + C4 shift + cull20, to 1200.
#
#   WORKERS=2 runs/RBT-107/new_seed.sh SEED start      session A of the seed (launch as a harness background task):
#       1. base from season 0 to 340 on RBT-90 part 2's command, byte for byte (runs/RBT-90/part2_run.sh; RBT-92 run_arm.sh)
#       2. T by RBT-92's rule on seasons [0, 340) (new_onset.py -> runs/RBT-107/onset-new-SEED.txt)
#       3. base on to the end of season T - 1; fork.py -> shift-SEED (terrain=flat at T) and cull20-SEED (20/20 at T)
#       4. cull20-SEED saved to ckpt/rbt-107-cull20-SEED, untouched, for session B
#       5. base and shift resumed to 1200 side by side, durable.sh every 20 beside each (rbt-107-base-SEED, -shift-SEED)
#       6. post-run on each: RBT-92 tables.py, RBT-101 wiring.py, and the V0 gate: prefix_check.py ARM base-SEED T
#   WORKERS=2 runs/RBT-107/new_seed.sh SEED cull20     session B: restore ckpt/rbt-107-cull20-SEED, resume to 1200,
#                                                      post-run as above (its V0 against the committed base-SEED tables)
# SEASONS overrides 1200 for a smoke test only; NO_DURABLE=1 skips the checkpoints.  Commit per arm: config.json,
# seasons.txt, lineage-last.txt, bodysig.txt, events.txt, groups.txt, wiring.txt, prefix.txt; and onset-new-SEED.txt.
set -e
SEED=$1; STEP=$2
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
cd "$REPO"
ROOT=${OUTROOT:-runs/RBT-107}
SEASONS=${SEASONS:-1200}
W=${WORKERS:-1}
durable_every() { [ -n "${NO_DURABLE:-}" ] && return 0; DURABLE_WATCH_PID=$2 scripts/durable.sh every 20 "$1" "rbt-107-$(basename "$1")" > "$1/durable.log" 2>&1 & }
durable_save()  { [ -n "${NO_DURABLE:-}" ] && return 0; scripts/durable.sh save "$1" "rbt-107-$(basename "$1")"; }
post() {  # ARM_DIR T
  python runs/RBT-92/tables.py "$1" >> "$1/run.log" 2>&1
  python runs/RBT-101/wiring.py "$1" >> "$1/run.log" 2>&1
  if [ "$(basename "$1")" = "base-$SEED" ]; then echo "base: no prefix gate (it is the reference)" > "$1/prefix.txt"
  else python "$HERE/prefix_check.py" "$1" "$ROOT/base-$SEED" "$2" > "$1/prefix.txt" 2>&1 || true; fi
  durable_save "$1"
  tail -1 "$1/prefix.txt"
}
case "$STEP" in
start)
  B=$ROOT/base-$SEED
  [ -e "$B/state.json" ] && { echo "$B exists" >&2; exit 2; }
  mkdir -p "$B"
  python -m rabbitstew.cli ecology --seasons 340 --capacity 60 --challenge foraging --group-size 4 --workers "$W" \
    --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
    --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
    --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
    --score food --seed "$SEED" --out "$B" > "$B/run.log" 2>&1
  python runs/RBT-92/tables.py "$B" >> "$B/run.log" 2>&1
  python "$HERE/new_onset.py" "$B" "$SEED" > "$ROOT/onset-new-$SEED.txt"
  T=$(cut -f2 "$ROOT/onset-new-$SEED.txt")
  echo "seed $SEED: T = $T"
  python -m rabbitstew.cli ecology --resume --seasons "$T" --workers "$W" --out "$B" >> "$B/run.log" 2>&1
  python "$HERE/fork.py" "$B" "$ROOT/shift-$SEED" shift
  python "$HERE/fork.py" "$B" "$ROOT/cull20-$SEED" cull20
  echo "RBT-107 new seed $SEED arm cull20: forked from base-$SEED at T = $T" > "$ROOT/cull20-$SEED/event.txt"
  echo "RBT-107 new seed $SEED arm shift: forked from base-$SEED at T = $T; --shift-at $T --shift terrain=flat" > "$ROOT/shift-$SEED/event.txt"
  durable_save "$ROOT/cull20-$SEED"
  python -m rabbitstew.cli ecology --resume --seasons "$SEASONS" --workers "$W" --out "$B" >> "$B/run.log" 2>&1 & PB=$!
  durable_every "$B" $PB
  python -m rabbitstew.cli ecology --resume --seasons "$SEASONS" --workers "$W" --out "$ROOT/shift-$SEED" >> "$ROOT/shift-$SEED/run.log" 2>&1 & PS=$!
  durable_every "$ROOT/shift-$SEED" $PS
  st=0; wait $PB || st=1; wait $PS || st=1
  wait || true
  [ $st = 0 ] || { echo "a run failed; see run.log (no post-run step)" >&2; exit 1; }
  post "$B" "$T"; post "$ROOT/shift-$SEED" "$T" ;;
cull20)
  C=$ROOT/cull20-$SEED
  T=$(cut -f2 "$ROOT/onset-new-$SEED.txt")
  [ -e "$C/state.json" ] || scripts/durable.sh restore "$C" "rbt-107-cull20-$SEED"
  python -m rabbitstew.cli ecology --resume --seasons "$SEASONS" --workers "$W" --out "$C" >> "$C/run.log" 2>&1 & PC=$!
  durable_every "$C" $PC
  wait $PC
  wait || true
  [ -e "$ROOT/base-$SEED/seasons.txt" ] || { echo "the V0 gate needs the committed $ROOT/base-$SEED tables on this checkout" >&2; exit 2; }
  post "$C" "$T" ;;
*) sed -n 2,16p "$0"; exit 2 ;;
esac
