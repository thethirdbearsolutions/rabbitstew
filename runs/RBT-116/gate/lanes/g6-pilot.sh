#!/bin/bash
# RBT-116 W1 gate lane g6-pilot (wave 4): G6's choice, the SHOULD 11 pilot (24 generations) and its probe
# EMITTED by runs/RBT-116/gate/lanes.py; NOT LAUNCHED.  Launch only after the hooks PR has merged and the coordinator
# has given the GO: RBT116_GATE_GO=1 WORKERS=4 bash runs/RBT-116/gate/lanes/g6-pilot.sh  (a harness background task)
# Re-running this script resumes the lane.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
[ "${RBT116_GATE_GO:-}" = 1 ] || { echo "REFUSED: no GO (set RBT116_GATE_GO=1 only on the coordinator's GO)" >&2; exit 4; }
[ "$(uname -m)" = x86_64 ] || { echo "REFUSED: x86_64 only (RBT-96)" >&2; exit 3; }
if [ -n "$(git status --porcelain -- rabbitstew runs/RBT-116/*.py runs/RBT-116/gate/*.py scripts/durable.sh)" ]; then
  echo "REFUSED: rabbitstew/ or the RBT-116 scripts have uncommitted changes" >&2; exit 5
fi
[ "$(git rev-parse HEAD:rabbitstew)" = "fff2360078cef154f9fb03a573b361dfc071fd05" ] || { echo "REFUSED: rabbitstew/ is not the tree these lanes were emitted on (fff2360078cef154f9fb03a573b361dfc071fd05)" >&2; exit 6; }
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
  python runs/RBT-116/gate/gate.py "$@" --out "$OUT" --base "$BASE" --workers "$WORKERS" >> "$OUT/lane-g6-pilot.log" 2>&1 &
  local pid=$!
  saver "$OUT" "$label" "$pid" &
  local sp=$!
  local rc=0; wait "$pid" || rc=$?
  wait "$sp" || true
  return $rc
}
restore_units() { for j in $(seq 1 24); do restore "$BASE/unit$(printf %02d $j)/B" "rbt-116-w1-unit$(printf %02d $j)-b"; done; }
restore_gate() { restore "$OUT" rbt-116-w1-gate-a; }

evolve_run() {  # evolve_run DIR LABEL CMD...: launch, or resume, one evolve run with its durable loop (as RBT-113's run_arm.sh)
  local R=$1 L=$2; shift 2
  local G; G=$(python - "$@" <<'PY'
import sys
a = sys.argv[1:]
print(a[a.index("--generations") + 1])
PY
)
  if [ -f "$R/history.json" ] && [ -d "$R/holistic/final" ] && [ "$(python -c "import json,sys; print(sum(e['population']=='holistic' for e in json.load(open(sys.argv[1]))['history']))" "$R/history.json")" = "$G" ]; then
    echo "$R complete; skipped"; return 0
  fi
  restore "$R" "$L" || true
  if [ -f "$R/state.json" ]; then
    echo "resumed $(date -u +%FT%TZ)" >> "$R/resumes.txt"
    python -m rabbitstew.cli evolve --resume --out "$R" --workers "$WORKERS" >> "$R/run.log" 2>&1 &
  else
    [ -d "$R" ] && rm -rf "$R"
    mkdir -p "$R"; echo "$*" > "$R/command.txt"
    "$@" > "$R/run.log" 2>&1 &
  fi
  local pid=$!
  DURABLE_WATCH_PID=$pid scripts/durable.sh every 20 "$R" "$L" &
  local dp=$!
  local rc=0; wait "$pid" || rc=$?
  kill "$dp" 2>/dev/null || true; wait "$dp" 2>/dev/null || true  # its next check could be 20 minutes away
  scripts/durable.sh save "$R" "$L"
  return $rc
}

merge() { scripts/durable.sh restore "$OUT" "$1"; }
restore_units
restore_gate
merge rbt-116-w1-gate-noise
merge rbt-116-w1-gate-g5
merge rbt-116-w1-gate-g7
merge rbt-116-w1-gate-g8-s0
merge rbt-116-w1-gate-g8-s1
merge rbt-116-w1-gate-g8-s2
merge rbt-116-w1-gate-g8-s3
merge rbt-116-w1-gate-g8-s4
merge rbt-116-w1-gate-g8-s5
merge rbt-116-w1-gate-g4-s0
merge rbt-116-w1-gate-g4-s1
merge rbt-116-w1-gate-g4-s2
merge rbt-116-w1-gate-g4-s3
merge rbt-116-w1-gate-g9-s0
merge rbt-116-w1-gate-g9-s1
merge rbt-116-w1-gate-g6u-s0
merge rbt-116-w1-gate-g6u-s1
merge rbt-116-w1-gate-g6u-s2
merge rbt-116-w1-gate-g6u-s3
merge rbt-116-w1-gate-g6u-s4
merge rbt-116-w1-gate-g6u-s5
merge rbt-116-w1-gate-g6u-s6
merge rbt-116-w1-gate-g6u-s7
cell rbt-116-w1-gate-pilot g6-pick
cell rbt-116-w1-gate-pilot pilot-prep
OPT=$(python -c "import json; print(json.load(open('$OUT/g6.json'))['chosen'])")
mapfile -t PCMD < <(python - "$OPT" <<'PY'
import sys; sys.path.insert(0, 'runs/RBT-116/gate'); import gate
print('\n'.join(gate.pilot_command(gate.os.path.join('runs', 'RBT-116', 'gate', 'W1'), sys.argv[1])))
PY
)
evolve_run "$OUT/pilot/run" rbt-116-w1-gate-pilot-run "${PCMD[@]}"
cell rbt-116-w1-gate-pilot pilot-probe
echo 'lane g6-pilot done'
