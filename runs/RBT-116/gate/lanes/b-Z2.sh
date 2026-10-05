#!/bin/bash
# RBT-116 W1 gate lane b-Z2 (wave 0): the burn-in B (D16, 13 generations) of units [16, 17, 18]
# EMITTED by runs/RBT-116/gate/lanes.py; NOT LAUNCHED.  Launch only after the hooks PR has merged and the coordinator
# has given the GO: RBT116_GATE_GO=1 WORKERS=4 bash runs/RBT-116/gate/lanes/b-Z2.sh  (a harness background task)
# Re-running this script resumes the lane.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
[ "${RBT116_GATE_GO:-}" = 1 ] || { echo "REFUSED: no GO (set RBT116_GATE_GO=1 only on the coordinator's GO)" >&2; exit 4; }
[ "$(uname -m)" = x86_64 ] || { echo "REFUSED: x86_64 only (RBT-96)" >&2; exit 3; }
if [ -n "$(git status --porcelain -- rabbitstew scripts/durable.sh docs/artifacts/RBT-67/compass_dose_response.py runs/RBT-113/world.py runs/RBT-116/gate/gate.py runs/RBT-116/gate/lanes.py runs/RBT-116/planters.py runs/RBT-116/power.py runs/RBT-116/steer.py runs/RBT-116/world.py runs/RBT-97/g500_direction.py runs/RBT-97/mechanism.py runs/RBT-97/resign_rbt67.py runs/RBT-97/routed_p801.py scripts/compass_mechanism.py scripts/compass_replication.py scripts/travel_direction.py)" ]; then
  echo "REFUSED: rabbitstew/ or a script the gate loads has uncommitted changes" >&2; exit 5
fi
[ "$(git rev-parse HEAD:rabbitstew)" = "e033c1938408aa7f3ccc66753c34d25222978da5" ] || { echo "REFUSED: rabbitstew/ is not the tree these lanes were emitted on (e033c1938408aa7f3ccc66753c34d25222978da5)" >&2; exit 6; }
# F7a: every script outside rabbitstew/ that gate.py loads, pinned by blob (re-emit with lanes.py on the final tree)
while read -r blob path; do
  [ "$(git rev-parse "HEAD:$path" 2>/dev/null)" = "$blob" ] || { echo "REFUSED: $path is not the blob these lanes were emitted on ($blob)" >&2; exit 6; }
done <<'PINS'
f854537ef31eaf51bab3176d30534dc97e84d101 docs/artifacts/RBT-67/compass_dose_response.py
3e3305ca885ac7585c309cabe5b8dfcb5c5d650b runs/RBT-113/world.py
2096a8eaad94625d51fbe384c2f6ca5c279d22f5 runs/RBT-116/gate/gate.py
7e45c738c8567fe8b45a458fac1f3dcb940e9eee runs/RBT-116/gate/lanes.py
433ee5790fd155448288173dcad1d4111574c9f2 runs/RBT-116/planters.py
d3ea864734e7680cc6aabddc3230a4543a5dcc77 runs/RBT-116/power.py
863fa6c742ca1e2b8444579be781e1cb9ff9b7df runs/RBT-116/steer.py
76ccd464190bcbc2fe3902fa8340f3eae2aeb3a2 runs/RBT-116/world.py
d9080daaf19dfdba82f1222f3f28a5b228ec9b1c runs/RBT-97/g500_direction.py
6eb642b7b84bb9e6f8d9c691f2586ff76d553165 runs/RBT-97/mechanism.py
08ac98256539caad3193947c6aae569410c2df31 runs/RBT-97/resign_rbt67.py
1dd946c35cf6f4d1679b8047b2d6240b91cfbe64 runs/RBT-97/routed_p801.py
b41e49838f0287cb3aa9e25ff96cac3d7fa11f9b scripts/compass_mechanism.py
ed60adbd5bdb31564129e58a6d036c8d34a1a226 scripts/compass_replication.py
37b98b2fb0f50b3b1b525661f32d6d92711d5520 scripts/travel_direction.py
PINS
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
  python runs/RBT-116/gate/gate.py "$@" --out "$OUT" --base "$BASE" --workers "$WORKERS" >> "$OUT/lane-b-Z2.log" 2>&1 &
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
  local rr=0; restore "$R" "$L" || rr=$?  # F4: exit 3 is "no checkpoint yet" (a fresh run); anything else is a failure
  [ "$rr" = 0 ] || [ "$rr" = 3 ] || { echo "REFUSED: restoring $R from ckpt/$L failed (exit $rr)" >&2; exit 7; }
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
  if [ "$rc" != 0 ] && grep -q DecoyRefused "$R/run.log"; then  # H16 as ruled: the stop is reported for a ruling
    echo "STOPPED FOR A RULING (H16): $R: a decoy season found no clear theta (DecoyRefused); see $R/run.log" >&2; exit 8
  fi
  return $rc
}

restore runs/RBT-113/Z2 rbt-113-Z2
evolve_run runs/RBT-116/W1/unit16/B rbt-116-w1-unit16-b python -m rabbitstew.cli evolve --population 40 --generations 13 --locomotion-phase 13 --elites 0 --champion-interval 0 --truncation 0.25 --line up --crossover-rate 0 --save-every 12 --workers "$WORKERS" --draws 16 --brain-model foraging --conventional-topology --food-items 12 --food-patches 2 --patch-radius 0.4 --food-radius 4.0 --regrow-delay 60 --smell log --food-decay 1.5 --smell-contrast 2.5 --smell-tau 1.0 --eat-radius 0.35 --eat-from root --eat-rule surface --clear-from root --work-cost 0.03 --terrain random --random-start --duration 15 --score food --fair --from-population holistic=runs/RBT-113/Z2/Z4/U/holistic/final --from-population conventional=runs/RBT-113/Z2/Z4/U/conventional/final --seed 116016 --smell-decoy zero --out runs/RBT-116/W1/unit16/B
evolve_run runs/RBT-116/W1/unit17/B rbt-116-w1-unit17-b python -m rabbitstew.cli evolve --population 40 --generations 13 --locomotion-phase 13 --elites 0 --champion-interval 0 --truncation 0.25 --line up --crossover-rate 0 --save-every 12 --workers "$WORKERS" --draws 16 --brain-model foraging --conventional-topology --food-items 12 --food-patches 2 --patch-radius 0.4 --food-radius 4.0 --regrow-delay 60 --smell log --food-decay 1.5 --smell-contrast 2.5 --smell-tau 1.0 --eat-radius 0.35 --eat-from root --eat-rule surface --clear-from root --work-cost 0.03 --terrain random --random-start --duration 15 --score food --fair --from-population holistic=runs/RBT-113/Z2/Z5/U/holistic/final --from-population conventional=runs/RBT-113/Z2/Z5/U/conventional/final --seed 116017 --smell-decoy zero --out runs/RBT-116/W1/unit17/B
evolve_run runs/RBT-116/W1/unit18/B rbt-116-w1-unit18-b python -m rabbitstew.cli evolve --population 40 --generations 13 --locomotion-phase 13 --elites 0 --champion-interval 0 --truncation 0.25 --line up --crossover-rate 0 --save-every 12 --workers "$WORKERS" --draws 16 --brain-model foraging --conventional-topology --food-items 12 --food-patches 2 --patch-radius 0.4 --food-radius 4.0 --regrow-delay 60 --smell log --food-decay 1.5 --smell-contrast 2.5 --smell-tau 1.0 --eat-radius 0.35 --eat-from root --eat-rule surface --clear-from root --work-cost 0.03 --terrain random --random-start --duration 15 --score food --fair --from-population holistic=runs/RBT-113/Z2/Z6/U/holistic/final --from-population conventional=runs/RBT-113/Z2/Z6/U/conventional/final --seed 116018 --smell-decoy zero --out runs/RBT-116/W1/unit18/B
echo 'lane b-Z2 done'
