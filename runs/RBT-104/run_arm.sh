#!/bin/bash
# RBT-104: one arm (PREREGISTRATION.md section 5).  RBT-90 part 2's command (part2_run.sh), unchanged,
# plus what the arm names and nothing else:
#
#   S1  seeded founders (seed_founders.py), --link-scale absent (1.0)   primary control
#   S8  seeded founders,                    --link-scale 8              primary treatment
#
# (U8, the unseeded K = 8 arm, was dropped by the coordinator's 18:40 ruling: it carries no verdict.)
# S1 and S8 load the same founder files; S8's flag multiplies their link weights by 8 at founding
# and every link-weight draw after.
#
#   runs/RBT-104/run_arm.sh ARM SEED      ->  runs/RBT-104/ARM-SEED/
#
# Launched as a harness background task, never with nohup, beside scripts/durable.sh (README rule 1
# and rule 6).  House packing (coordinator, 17:02): two arms per four-core session, each at the default
# WORKERS=2 (waves.txt).  Workers do not change the run (RBT-90 ruling: workers 1 and 4 byte-identical).
set -e
ARM=$1; SEED=$2
OUT=runs/RBT-104/$ARM-$SEED
case "$ARM" in
  S1) EXTRA=(--from-conventional "runs/RBT-104/founders-$SEED") ;;
  S8) EXTRA=(--from-conventional "runs/RBT-104/founders-$SEED" --link-scale 8) ;;
  *) echo "unknown arm $ARM" >&2; exit 2 ;;
esac
if [ ! -d "runs/RBT-104/founders-$SEED" ]; then
  python runs/RBT-104/seed_founders.py "$SEED" "runs/RBT-104/founders-$SEED"
fi
# the founders must be the pre-registered ones, byte for byte
(cd "runs/RBT-104/founders-$SEED" && sha256sum -c --quiet SHA256SUMS)
grep -q "^$SEED $(sha256sum < "runs/RBT-104/founders-$SEED/SHA256SUMS" | cut -c1-64)$" runs/RBT-104/founders-digests.txt
mkdir -p "$OUT"
# one platform throughout (coordinator's condition 3, RBT-96): recorded beside the run, committed as evidence
python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$OUT/platform.txt"
[ "$(uname -m)" = x86_64 ] || { echo "RBT-104 arms run on the cloud x86_64 image only (RBT-96)" >&2; exit 3; }
exec python -m rabbitstew.cli ecology --seasons "${SEASONS:-600}" --capacity 60 --challenge foraging --group-size 4 --workers "${WORKERS:-2}" \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed "$SEED" --out "$OUT" "${EXTRA[@]}" > "$OUT/run.log" 2>&1
