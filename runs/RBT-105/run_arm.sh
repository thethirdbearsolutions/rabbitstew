#!/bin/bash
# RBT-105: one replicate arm.  The dense foraging baseline exactly as RBT-90 part 2 runs it
# (runs/RBT-90/part2_run.sh, byte for byte in every flag), plus ONE flag: --breed-stream K.
#
#   K = 0     the original holistic stream: the positive control, which must reproduce the seed's RBT-90
#             part 2 arm byte for byte (seasons.txt and lineage-last.txt against the committed files)
#   K >= 1    the same founders (genomes and ages, byte-identical at season 0: founders-rbt90.txt), a new
#             holistic history (groupings, breeding order, mate choice, crossover, mutation), the same
#             designed-body fauna and the same worlds
#
#   WORKERS=4 runs/RBT-105/run_arm.sh SEED K        ->  runs/RBT-105/forage-SEED-bK/   checkpoint ckpt/rbt-105-SEED-bK
#
# Launch THIS SCRIPT as a harness background task, never with nohup (runs/README.md rule 1).  It starts the run,
# starts scripts/durable.sh every 20 beside it with DURABLE_WATCH_PID on the run, waits, writes the post-run
# tables (post_run.py: seasons.txt, lineage-last.txt, oscillator.txt, pairing.txt), and then takes one more
# durable.sh save, after the tables exist (README rule 6).  Commit the four .txt files and push.
# A resumed arm: scripts/durable.sh restore DIR LABEL; RESUME=1 runs/RBT-105/run_arm.sh SEED K.
# SEASONS and OUTROOT override 600 and runs/RBT-105 for the 20-season throwaway check only (throwaway.sh).
set -e
SEED=$1
K=$2
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
cd "$REPO"
[ -n "$SEED" ] && [[ "$K" =~ ^[0-9]+$ ]] || { echo "usage: run_arm.sh SEED K   (K = 0 the positive control, K >= 1 a replicate history)" >&2; exit 2; }
ROOT=${OUTROOT:-runs/RBT-105}
OUT=$ROOT/forage-$SEED-b$K
LABEL=${LABEL:-rbt-105-$SEED-b$K}
mkdir -p "$OUT"
if [ -n "${RESUME:-}" ]; then
  python -m rabbitstew.cli ecology --resume --out "$OUT" --workers "${WORKERS:-1}" >> "$OUT/run.log" 2>&1 &
else
  python -m rabbitstew.cli ecology --seasons "${SEASONS:-600}" --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
    --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
    --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
    --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
    --score food --seed "$SEED" --breed-stream "$K" --out "$OUT" > "$OUT/run.log" 2>&1 &
fi
RUN=$!
echo "RBT-105 seed $SEED breed_stream $K: pid $RUN, out $OUT, checkpoint ckpt/$LABEL"
DURABLE=""
if [ -z "${NO_DURABLE:-}" ]; then
  DURABLE_WATCH_PID=$RUN scripts/durable.sh every 20 "$OUT" "$LABEL" > "$OUT/durable.log" 2>&1 &
  DURABLE=$!
fi
STATUS=0
wait $RUN || STATUS=$?
[ -n "$DURABLE" ] && { wait $DURABLE || true; }
[ "$STATUS" = 0 ] || { echo "the run exited with status $STATUS; see $OUT/run.log (no post-run step)" >&2; exit "$STATUS"; }
# Post-run step: the committed tables, from the bulk, while it is here.
python "$HERE/post_run.py" "$OUT" "$SEED" "$K" >> "$OUT/run.log" 2>&1
# README rule 6: the every loop's last snapshot fired as the run ended, while the tables did not yet exist.
[ -z "${NO_DURABLE:-}" ] && scripts/durable.sh save "$OUT" "$LABEL"
cat "$OUT/pairing.txt"
tail -1 "$OUT/oscillator.txt"
