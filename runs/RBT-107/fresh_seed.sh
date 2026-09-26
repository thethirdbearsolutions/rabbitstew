#!/bin/bash
# RBT-107 Amendment 2 (F2, F3): one arm of one FRESH seed, from season 0 to 1200, with a fixed onset T = 360.
#
#   WORKERS=2 runs/RBT-107/fresh_seed.sh SEED ARM        ->  runs/RBT-107/fresh/ARM-SEED/   checkpoint ckpt/rbt-107-fresh-ARM-SEED
#
#   ARM      event                                                  (RBT-90 part 2's command otherwise, byte for byte:
#   base     none                                                    runs/RBT-90/part2_run.sh, RBT-92's run_arm.sh)
#   shift    --shift-at 360 --shift terrain=flat                     C4, as RBT-101's arms
#   cull20   --cull-at 360 --cull holistic=20,conventional=20        RBT-92's divergence null
#
# The fresh seeds are 11-30, the next twenty integers after the ten single-digit-and-80x seeds; no committed run uses any
# (checked against every runs/*/config.json).  They were chosen by nothing but order.  T = 360 for every one (the
# adversary's F2: RBT-92's onset rule was built for C1's death waves; 360 is the old seeds' median onset, 359.5).
# Every arm runs from season 0, no fork (the adversary advised against the extra mechanism): the three arms of a seed are
# paired on founders, worlds and streams (RBT-95) and are byte-identical before 360, which the readout's V0 checks.
#
# Launch THIS SCRIPT as a harness background task (runs/README.md rule 1).  It starts the run, durable.sh every 20 beside
# it (DURABLE_WATCH_PID), waits, writes the post-run step, saves once more (README rule 6).  If the container dies BEFORE the
# first 20-minute save, ckpt/rbt-107-fresh-ARM-SEED does not exist: rerun WITHOUT RESUME (delete the directory first).
# After a save exists: RESUME=1 with the same arguments restores it and continues.
# NO-PEEK (Amendment 2, F9): the runner posts progress and platform only; no income, seasons.txt or garden number from
# season 360 on is posted or read until every arm of the wave has ended and V0/V-POST pass.
set -e
SEED=$1; ARM=$2
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
cd "$REPO"
T=360
case "$ARM" in
  base)   EVENT="" ;;
  shift)  EVENT="--shift-at $T --shift terrain=flat" ;;
  cull20) EVENT="--cull-at $T --cull holistic=20,conventional=20" ;;
  *) echo "usage: fresh_seed.sh SEED {base|shift|cull20}" >&2; exit 2 ;;
esac
[ "$SEED" -ge 11 ] && [ "$SEED" -le 30 ] || { echo "fresh seeds are 11-30" >&2; exit 2; }
OUT=${OUTROOT:-runs/RBT-107/fresh}/$ARM-$SEED
LABEL=${LABEL:-rbt-107-fresh-$ARM-$SEED}
SEASONS=${SEASONS:-1200}
if [ -n "${RESUME:-}" ]; then
  [ -e "$OUT/state.json" ] || scripts/durable.sh restore "$OUT" "$LABEL"
  python -m rabbitstew.cli ecology --resume --seasons "$SEASONS" --workers "${WORKERS:-1}" --out "$OUT" >> "$OUT/run.log" 2>&1 &
else
  [ -e "$OUT/state.json" ] && { echo "$OUT exists: RESUME=1, or delete it if no checkpoint was ever saved" >&2; exit 2; }
  mkdir -p "$OUT"
  echo "RBT-107 fresh seed $SEED arm $ARM: T=$T event: ${EVENT:-none}" > "$OUT/event.txt"
  python -m rabbitstew.cli ecology --seasons "$SEASONS" --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
    --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
    --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
    --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
    --score food --seed "$SEED" $EVENT --out "$OUT" > "$OUT/run.log" 2>&1 &
fi
RUN=$!
echo "RBT-107 fresh seed $SEED arm $ARM: pid $RUN, out $OUT, checkpoint ckpt/$LABEL"
DURABLE=""
if [ -z "${NO_DURABLE:-}" ]; then
  DURABLE_WATCH_PID=$RUN scripts/durable.sh every 20 "$OUT" "$LABEL" > "$OUT/durable.log" 2>&1 &
  DURABLE=$!
fi
STATUS=0
wait $RUN || STATUS=$?
[ -n "$DURABLE" ] && { wait $DURABLE || true; }
[ "$STATUS" = 0 ] || { echo "the run exited with status $STATUS; see $OUT/run.log" >&2; exit "$STATUS"; }
python runs/RBT-92/tables.py "$OUT" >> "$OUT/run.log" 2>&1
python runs/RBT-101/wiring.py "$OUT" >> "$OUT/run.log" 2>&1
python "$HERE/vpost.py" "$OUT" "$ARM" "$T" > "$OUT/vpost.txt" 2>&1 || true
[ -z "${NO_DURABLE:-}" ] && scripts/durable.sh save "$OUT" "$LABEL"
cat "$OUT/vpost.txt"
echo "commit: $OUT/{config.json,event.txt,seasons.txt,lineage-last.txt,bodysig.txt,events.txt,groups.txt,wiring.txt,vpost.txt}"
