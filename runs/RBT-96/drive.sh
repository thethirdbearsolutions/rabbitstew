#!/usr/bin/env bash
# RBT-96: run the eight A/A arms on a four-core cloud session, one seed's pair at a time, each arm at
# --workers 2 with its own durable.sh snapshot loop (label rbt-96-SEED-ARM), then a final snapshot
# after the toolkit has written analysis.json.  Resumable: rerun it after a restore and every arm
# continues from its state.json (scripts/rbt96_run.sh resumes or analyses only as appropriate).
#   runs/RBT-96/drive.sh [SEEDS...]      (default 201 202 203 204)
set -uo pipefail
cd "$(dirname "$0")/../.."
. ./v/bin/activate
SEEDS=${*:-201 202 203 204}
for SEED in $SEEDS; do
  pids=(); loops=()
  for ARM in s0 s1; do
    OUT=runs/RBT-96/$ARM-$SEED
    if [ -f "$OUT/analysis.json" ]; then echo "$(date -u +%FT%TZ) $ARM-$SEED complete, skipping"; continue; fi
    mkdir -p "$OUT"
    scripts/rbt96_run.sh "$SEED" "$ARM" 2 &
    pid=$!; pids+=("$pid")
    DURABLE_WATCH_PID=$pid scripts/durable.sh every 20 "$OUT" "rbt-96-$SEED-$ARM" >> "runs/RBT-96/durable-$SEED-$ARM.log" 2>&1 &
    loops+=("$!")
    echo "$(date -u +%FT%TZ) launched $ARM-$SEED pid $pid"
  done
  for p in "${pids[@]}"; do wait "$p"; rc=$?; echo "$(date -u +%FT%TZ) pid $p exited $rc"; done
  # the loops sleep 20 min between saves; stop them now and take the final save (after analysis.json) here
  for l in "${loops[@]}"; do kill "$l" 2>/dev/null; done; wait 2>/dev/null
  for ARM in s0 s1; do scripts/durable.sh save "runs/RBT-96/$ARM-$SEED" "rbt-96-$SEED-$ARM" >> "runs/RBT-96/durable-$SEED-$ARM.log" 2>&1; done
  echo "$(date -u +%FT%TZ) seed $SEED done"
done
echo "$(date -u +%FT%TZ) all done"
