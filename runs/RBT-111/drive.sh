#!/usr/bin/env bash
# RBT-111: one runner session's arms, two at a time (a "pair-slot"), each at --workers 2 with its own
# durable.sh snapshot loop (label rbt-111-SEED-ARM), then a final snapshot after the toolkit has written
# analysis.json, then that slot's summaries.  Arms run in the fixed order SEED s0, s1, s2 for each seed given,
# paired consecutively: four seeds make six pair-slots (waves.txt).  Resumable: rerun it after a restore and
# every arm continues from its state.json (scripts/rbt111_run.sh resumes or analyses only as appropriate).
#   runs/RBT-111/drive.sh SEED...          (one session's four seeds, from waves.txt)
set -uo pipefail
cd "$(dirname "$0")/../.."
. ./v/bin/activate
[ $# -ge 1 ] || { echo "usage: runs/RBT-111/drive.sh SEED..." >&2; exit 2; }
PLAT="runs/RBT-111/platform-$1-${!#}.txt"
{ uname -m; grep -m1 'model name' /proc/cpuinfo; nproc; python --version
  python -c 'import mujoco, numpy; print("mujoco", mujoco.__version__); print("numpy", numpy.__version__)'; } > "$PLAT"
ARMS=()
for SEED in "$@"; do for ARM in s0 s1 s2; do ARMS+=("$ARM-$SEED"); done; done
for ((i = 0; i < ${#ARMS[@]}; i += 2)); do
  SLOT=("${ARMS[@]:i:2}")
  pids=(); loops=()
  for AS in "${SLOT[@]}"; do
    ARM=${AS%-*}; SEED=${AS#*-}; OUT=runs/RBT-111/$AS
    if [ -f "$OUT/analysis.json" ]; then echo "$(date -u +%FT%TZ) $AS complete, skipping"; continue; fi
    mkdir -p "$OUT"
    scripts/rbt111_run.sh "$SEED" "$ARM" 2 &
    pid=$!; pids+=("$pid")
    DURABLE_WATCH_PID=$pid scripts/durable.sh every 20 "$OUT" "rbt-111-$AS" >> "runs/RBT-111/durable-$AS.log" 2>&1 &
    loops+=("$!")
    echo "$(date -u +%FT%TZ) slot $((i / 2 + 1)): launched $AS pid $pid"
  done
  for p in "${pids[@]}"; do wait "$p"; rc=$?; echo "$(date -u +%FT%TZ) pid $p exited $rc"; done
  for l in "${loops[@]}"; do kill "$l" 2>/dev/null; done; wait 2>/dev/null
  for AS in "${SLOT[@]}"; do scripts/durable.sh save "runs/RBT-111/$AS" "rbt-111-$AS" >> "runs/RBT-111/durable-$AS.log" 2>&1; done
  SEEDS_IN_SLOT=$(for AS in "${SLOT[@]}"; do echo "${AS#*-}"; done | sort -u | paste -sd, -)
  python runs/RBT-111/readout.py --write-summaries --seeds "$SEEDS_IN_SLOT" > /dev/null
  echo "$(date -u +%FT%TZ) slot $((i / 2 + 1)) done (${SLOT[*]})"
done
echo "$(date -u +%FT%TZ) all done"
