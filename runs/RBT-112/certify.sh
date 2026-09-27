#!/bin/bash
# RBT-112, at launch only (PREREGISTRATION.md §7.2): certify that the launch commit's code, with the flag unset,
# is the code RBT-106's HU arms ran, so that HZ and HU are exactly one flag apart.  For each of HU-801 and HU-4
# (finished arms: this runs only after RBT-106's H has read), RBT-106's HU command is re-run for 20 seasons at
# the launch commit and compared with the first 20 seasons of RBT-106's arm, restored from ckpt/rbt-106-HU-SEED,
# by RBT-106's adversary's cross_ticket.py (seasons.txt rows, lineage.jsonl records, config, platform).
#
#   runs/RBT-112/certify.sh      ->  runs/RBT-112/cross-ticket-<commit12>.txt   (run_arm.sh requires SAME RUN on both)
set -e
cd "$(dirname "$0")/../.."
B=${BULK_ROOT:-/tmp/rbt-112-bulk}
HEADC=$(git rev-parse HEAD)
OUT=runs/RBT-112/cross-ticket-${HEADC:0:12}.txt
git diff --quiet HEAD -- rabbitstew && [ -z "$(git status --porcelain -- rabbitstew)" ] || { echo "certify from a clean rabbitstew/" >&2; exit 5; }
printf '# RBT-112 certification at commit %s (rabbitstew tree %s): RBT-106 HU command, 20 seasons, against RBT-106 HU-SEED\n' "$HEADC" "$(git rev-parse HEAD:rabbitstew)" > "$OUT"
for SEED in 801 4; do
  REF=$B/HU-$SEED
  [ -f "$REF/state.json" ] || scripts/durable.sh restore "$REF" "rbt-106-HU-$SEED"
  CT=$B/ct-HU-$SEED; rm -rf "$CT"; mkdir -p "$CT"
  [ -f "runs/RBT-106/founders-w32-$SEED/SHA256SUMS" ] || python runs/RBT-106/founders.py "$SEED" 32 "runs/RBT-106/founders-w32-$SEED"
  mapfile -d '' CMD < <(SEASONS=20 WORKERS=${WORKERS:-2} python runs/RBT-106/command.py HU "$SEED" "$CT")
  "${CMD[@]}" > "$CT/run.log" 2>&1
  python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$CT/platform.txt"
  python runs/RBT-106/adversary/cross_ticket.py "$CT" "$REF" >> "$OUT"
done
grep "^CROSS-TICKET" "$OUT"
