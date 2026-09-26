#!/bin/bash
# RBT-104: one arm (PREREGISTRATION.md section 5).  RBT-90 part 2's command (part2_run.sh), unchanged,
# plus what the arm names and nothing else:
#
#   S1  seeded founders (seed_founders.py), --link-scale absent (1.0)   primary control
#   S8  seeded founders,                    --link-scale 8              primary treatment
#   U8  part 2's own founders,              --link-scale 8              secondary: literal arm, side effects
#
# The control for U8 is RBT-90 part 2 itself (runs/RBT-90/forage-SEED), cited: the flag at its default
# is byte-identical to it (byte_identity.txt).  S1 and S8 load the same founder files; S8's flag
# multiplies their link weights by 8 at founding and every link-weight draw after.
#
#   runs/RBT-104/run_arm.sh ARM SEED      ->  runs/RBT-104/ARM-SEED/
#
# Launched as a harness background task, never with nohup, beside scripts/durable.sh (README rule 1
# and rule 6).  WORKERS=4 on a four-core cloud session; workers do not change the run (RBT-90 ruling).
set -e
ARM=$1; SEED=$2
OUT=runs/RBT-104/$ARM-$SEED
case "$ARM" in
  S1) EXTRA=(--from-conventional "runs/RBT-104/founders-$SEED") ;;
  S8) EXTRA=(--from-conventional "runs/RBT-104/founders-$SEED" --link-scale 8) ;;
  U8) EXTRA=(--link-scale 8) ;;
  *) echo "unknown arm $ARM" >&2; exit 2 ;;
esac
if [ "$ARM" != U8 ] && [ ! -d "runs/RBT-104/founders-$SEED" ]; then
  python runs/RBT-104/seed_founders.py "$SEED" "runs/RBT-104/founders-$SEED"
fi
if [ "$ARM" != U8 ]; then  # the founders must be the pre-registered ones, byte for byte
  (cd "runs/RBT-104/founders-$SEED" && sha256sum -c --quiet SHA256SUMS)
  grep -q "^$SEED $(sha256sum < "runs/RBT-104/founders-$SEED/SHA256SUMS" | cut -c1-64)$" runs/RBT-104/founders-digests.txt
fi
mkdir -p "$OUT"
exec python -m rabbitstew.cli ecology --seasons "${SEASONS:-600}" --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-1}" \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" --out "$OUT" "${EXTRA[@]}" > "$OUT/run.log" 2>&1
