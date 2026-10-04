#!/bin/bash
# RBT-116 W1 gate lane g4-s2 (wave 2): G4 shard 2/4
# EMITTED by runs/RBT-116/gate/lanes.py; NOT LAUNCHED.  Launch only after the hooks PR has merged and the coordinator
# has given the GO: RBT116_GATE_GO=1 WORKERS=4 bash runs/RBT-116/gate/lanes/g4-s2.sh  (a harness background task)
# Re-running this script resumes the lane.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
[ "${RBT116_GATE_GO:-}" = 1 ] || { echo "REFUSED: no GO (set RBT116_GATE_GO=1 only on the coordinator's GO)" >&2; exit 4; }
[ "$(uname -m)" = x86_64 ] || { echo "REFUSED: x86_64 only (RBT-96)" >&2; exit 3; }
if [ -n "$(git status --porcelain -- rabbitstew runs/RBT-116/*.py runs/RBT-116/gate/*.py scripts/durable.sh)" ]; then
  echo "REFUSED: rabbitstew/ or the RBT-116 scripts have uncommitted changes" >&2; exit 5
fi
[ "$(git rev-parse HEAD:rabbitstew)" = "e033c1938408aa7f3ccc66753c34d25222978da5" ] || { echo "REFUSED: rabbitstew/ is not the tree these lanes were emitted on (e033c1938408aa7f3ccc66753c34d25222978da5)" >&2; exit 6; }
WORKERS=${WORKERS:-4}
OUT=runs/RBT-116/gate/W1
BASE=runs/RBT-116/W1
mkdir -p "$OUT"
restore() {  # restore DIR LABEL unless DIR is already there (durable.sh refuses a directory holding a state.json)
  if [ ! -e "$1/.restored" ] && [ ! -e "$1/state.json" ]; then scripts/durable.sh restore "$1" "$2" && touch "$1/.restored"; fi
}
saver() {  # snapshot DIR to LABEL every 20 minutes while PID runs (polling every 10 s), then once more
  local dir=$1 label=$2 pid=$3 t=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 10; t=$((t + 10))
    if [ "$t" -ge 1200 ]; then scripts/durable.sh save "$dir" "$label" || true; t=0; fi
  done
  scripts/durable.sh save "$dir" "$label"
}
cell() {  # run one gate.py cell in the background with its saver, and wait
  local label=$1; shift
  python runs/RBT-116/gate/gate.py "$@" --out "$OUT" --base "$BASE" --workers "$WORKERS" >> "$OUT/lane-g4-s2.log" 2>&1 &
  local pid=$!
  saver "$OUT" "$label" "$pid" &
  local sp=$!
  local rc=0; wait "$pid" || rc=$?
  wait "$sp" || true
  return $rc
}
restore_units() { for j in $(seq 1 24); do restore "$BASE/unit$(printf %02d $j)/B" "rbt-116-w1-unit$(printf %02d $j)-b"; done; }
restore_gate() { restore "$OUT" rbt-116-w1-gate-a; }

restore_units
restore_gate
for arm in O1 O2 O3 O4 Z1 Z2 Z3 Z4; do restore runs/RBT-113/$arm rbt-113-$arm; done
cell rbt-116-w1-gate-g4-s2 g4 --shard 2/4
echo 'lane g4-s2 done'
