#!/bin/bash
# RBT-107: extend one committed arm from its checkpoint to 1200 seasons.  No arm is run from season 0.
#
#   WORKERS=2 runs/RBT-107/extend_arm.sh SEED ARM        ->  runs/RBT-107/ARM-SEED/    checkpoint ckpt/rbt-107-ARM-SEED
#
#   ARM      source checkpoint           committed source arm (its tables are the prefix gate)
#   base     ckpt/rbt-90-SEED            runs/RBT-90/forage-SEED       RBT-90 part 2, the no-event baseline
#   shift    ckpt/rbt-101-shift-SEED     runs/RBT-101/shift-SEED       C4, --shift-at T --shift terrain=flat
#   cull20   ckpt/rbt-92-cull20-SEED     runs/RBT-92/cull20-SEED       the divergence null: --cull-at T 20/20, no terrain change
#   cull     ckpt/rbt-101-cull-SEED      runs/RBT-101/cull-SEED        RBT-101's k-cull (801, 1, 2, 4 only; k = 0/0 elsewhere)
#
# The ecology resumes byte for byte (RBT-93/95) and --resume takes a larger --seasons (extend_check.txt: the extension
# of a finished run is byte-identical to the longer uninterrupted run).  A checkpoint that stopped short of 600
# (ckpt_check.txt: shift-804 at 548, shift-805 at 599, cull20-806 at 565) simply replays its missing seasons first; the
# replay is gated against the committed tables by prefix_check.py after the run.  Every flag of the original command,
# the shift and the cull included, is in the restored config.json and state.json; nothing is re-typed here.
#
# Launch THIS SCRIPT as a harness background task, never nohup (runs/README.md rule 1).  It restores, starts the run,
# starts scripts/durable.sh every 20 beside it with DURABLE_WATCH_PID on the run, waits, runs the post-run step
# (RBT-92's tables.py, RBT-101's wiring.py, prefix_check.py), then saves once more (README rule 6).  Commit the .txt
# files it lists and push.  A container lost mid-run: RESUME=1 with the same arguments (it restores ckpt/rbt-107-...).
# SEASONS and OUTROOT override 1200 and runs/RBT-107 for a smoke test only.
set -e
SEED=$1
ARM=$2
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
cd "$REPO"
case "$ARM" in
  base)   SRC_LABEL=rbt-90-$SEED;          SRC_DIR=runs/RBT-90/forage-$SEED ;;
  shift)  SRC_LABEL=rbt-101-shift-$SEED;   SRC_DIR=runs/RBT-101/shift-$SEED ;;
  cull20) SRC_LABEL=rbt-92-cull20-$SEED;   SRC_DIR=runs/RBT-92/cull20-$SEED ;;
  cull)   SRC_LABEL=rbt-101-cull-$SEED;    SRC_DIR=runs/RBT-101/cull-$SEED ;;
  *) echo "usage: extend_arm.sh SEED {base|shift|cull20|cull}" >&2; exit 2 ;;
esac
ROOT=${OUTROOT:-runs/RBT-107}
OUT=$ROOT/$ARM-$SEED
LABEL=${LABEL:-rbt-107-$ARM-$SEED}
SEASONS=${SEASONS:-1200}
[ -e "$OUT/state.json" ] && [ -z "${RESUME:-}" ] && { echo "$OUT already holds a run; RESUME=1 to continue it" >&2; exit 2; }
if [ -n "${RESUME:-}" ] && [ ! -e "$OUT/state.json" ]; then
  scripts/durable.sh restore "$OUT" "$LABEL"
elif [ -z "${RESUME:-}" ]; then
  [ -e "$SRC_DIR/seasons.txt" ] || { echo "no committed $SRC_DIR/seasons.txt: the source arm's tables must be on this checkout (the prefix gate reads them)" >&2; exit 2; }
  scripts/durable.sh restore "$OUT" "$SRC_LABEL"
  git fetch -q origin "+refs/heads/ckpt/$SRC_LABEL:refs/remotes/origin/ckpt/$SRC_LABEL"
  FROM=$(python -c "import json;print(json.load(open('$OUT/state.json'))['season'])")
  printf 'RBT-107 extension of %s (ckpt/%s %s, restored at season %s) to %s seasons\n' "$SRC_DIR" "$SRC_LABEL" \
    "$(git rev-parse --short "origin/ckpt/$SRC_LABEL")" "$FROM" "$SEASONS" > "$OUT/extension.txt"
  cat "$OUT/event.txt" >> "$OUT/extension.txt" 2>/dev/null || true
fi
python -m rabbitstew.cli ecology --resume --seasons "$SEASONS" --workers "${WORKERS:-1}" --out "$OUT" >> "$OUT/run.log" 2>&1 &
RUN=$!
echo "RBT-107 seed $SEED arm $ARM: pid $RUN, out $OUT, checkpoint ckpt/$LABEL"
DURABLE=""
if [ -z "${NO_DURABLE:-}" ]; then
  DURABLE_WATCH_PID=$RUN scripts/durable.sh every 20 "$OUT" "$LABEL" > "$OUT/durable.log" 2>&1 &
  DURABLE=$!
fi
STATUS=0
wait $RUN || STATUS=$?
[ -n "$DURABLE" ] && { wait $DURABLE || true; }
[ "$STATUS" = 0 ] || { echo "the run exited with status $STATUS; see $OUT/run.log (no post-run step)" >&2; exit "$STATUS"; }
# Post-run step, from the bulk while it is here: RBT-92's tables (seasons.txt, lineage-last.txt, bodysig.txt, events.txt,
# groups.txt), RBT-101's posture-wiring digest (wiring.txt), and the prefix gate against the committed source arm.
python runs/RBT-92/tables.py "$OUT" >> "$OUT/run.log" 2>&1
python runs/RBT-101/wiring.py "$OUT" >> "$OUT/run.log" 2>&1
python "$HERE/prefix_check.py" "$OUT" "$SRC_DIR" > "$OUT/prefix.txt" 2>&1 || true
[ -z "${NO_DURABLE:-}" ] && scripts/durable.sh save "$OUT" "$LABEL"
cat "$OUT/prefix.txt"
echo "commit: $OUT/{config.json,extension.txt,seasons.txt,lineage-last.txt,bodysig.txt,events.txt,groups.txt,wiring.txt,prefix.txt}"
