#!/bin/bash
# RBT-120: one arm of the budgeted rerun (PREREGISTRATION.md §3, §8): RBT-113's run_arm.sh with the arm map and the
# world swapped.  An arm is the default operator plus --motor-budget 1.77 on one of RBT-113's seed blocks:
#
#   arm   seeds       seed directories
#   B1    1 2 3       runs/RBT-120/B1/1 .. /3
#   B2    4 5 6
#   B3    7 8 9
#   B4    10 11 12
#
#   runs/RBT-120/run_arm.sh ARM      ->  runs/RBT-120/ARM/<SEED>/{U,D,C}/   (each an `evolve` output directory)
#
# Launched as a harness background task, never with nohup, beside
#   DURABLE_WATCH_PID=<this script's pid> scripts/durable.sh every 20 runs/RBT-120/ARM rbt-120-ARM
# RE-RUNNING THIS SCRIPT IS HOW AN ARM IS RESUMED, exactly as RBT-113's (RUNNER.md §3).
#
# Refuses (exit codes): 2 unknown arm; 3 not x86_64 (RBT-96); 5 rabbitstew/ has uncommitted changes;
#   7 controls/prelaunch.txt does not read PRELAUNCH: PASS on this rabbitstew/ tree (prelaunch.sh)
set -e
ARM=$1
cd "$(dirname "$0")/../.."
case "$ARM" in
  B1) SEEDS="1 2 3";; B2) SEEDS="4 5 6";; B3) SEEDS="7 8 9";; B4) SEEDS="10 11 12";;
  *) echo "unknown arm $ARM (B1-B4)" >&2; exit 2;;
esac
OP=""
[ "$(uname -m)" = x86_64 ] || { echo "RBT-120 arms run on the cloud x86_64 image only (RBT-96)" >&2; exit 3; }
if ! git diff --quiet HEAD -- rabbitstew || [ -n "$(git status --porcelain -- rabbitstew)" ]; then
  echo "REFUSED: rabbitstew/ has uncommitted changes; launch from a clean checkout" >&2; exit 5
fi
grep -q "^PRELAUNCH: PASS" runs/RBT-120/controls/prelaunch.txt 2>/dev/null || { echo "REFUSED: the pre-launch controls have not passed (prelaunch.sh)" >&2; exit 7; }
grep -q "^rabbitstew_tree $(git rev-parse HEAD:rabbitstew)$" runs/RBT-120/controls/prelaunch.txt || { echo "REFUSED: controls/prelaunch.txt was made on another rabbitstew/ tree; re-run prelaunch.sh" >&2; exit 7; }
G=$(python -c "import sys; sys.path.insert(0, 'runs/RBT-120'); import world; print(world.GENERATIONS)")
A=runs/RBT-120/$ARM
mkdir -p "$A"
if [ ! -f "$A/commit.txt" ]; then
  python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$A/platform.txt"
  printf '# RBT-120 launch record\ncommit %s\nrabbitstew_tree %s\nworkers %s\n' "$(git rev-parse HEAD)" "$(git rev-parse HEAD:rabbitstew)" "${WORKERS:-2}" > "$A/commit.txt"
fi
manifest() {  # durable.sh's progress: completed generations over 9 x G
  local done=0 s L h n
  for s in $SEEDS; do for L in U D C; do
    h="$A/$OP$s/$L/history.json"
    if [ -f "$h" ]; then n=$(python -c "import json,sys; print(sum(e['population']=='holistic' for e in json.load(open(sys.argv[1]))['history']))" "$h"); done=$((done + n)); fi
  done; done
  printf '{"generations": %d}\n' $((9 * G)) > "$A/config.json.tmp" && mv "$A/config.json.tmp" "$A/config.json"
  printf '{"populations": {"arm": {"generation": %d}}}\n' "$done" > "$A/state.json.tmp" && mv "$A/state.json.tmp" "$A/state.json"
}
manifest
for s in $SEEDS; do
  for L in U D C; do
    R=$A/$OP$s/$L
    if [ -f "$R/history.json" ] && [ "$(python -c "import json,sys; print(sum(e['population']=='holistic' for e in json.load(open(sys.argv[1]))['history']))" "$R/history.json")" = "$G" ] && [ -d "$R/holistic/final" ]; then
      echo "$R complete; skipped"; continue
    fi
    if [ -f "$R/state.json" ]; then
      echo "$R resumed"; echo "resumed $(date -u +%FT%TZ)" >> "$R/resumes.txt"
      python -m rabbitstew.cli evolve --resume --out "$R" --workers "${WORKERS:-2}" >> "$R/run.log" 2>&1
    else
      # no state.json: the run never finished its generation 0, so nothing of it is kept (lineage.jsonl appends)
      [ -d "$R" ] && { echo "$R restarted from scratch (no state.json)"; rm -rf "$R"; }
      mkdir -p "$R"
      mapfile -d '' CMD < <(python runs/RBT-120/world.py "$L" "${OP:--}" "$s" "$R")
      echo "${CMD[*]}" > "$R/command.txt"
      "${CMD[@]}" > "$R/run.log" 2>&1
    fi
    manifest
  done
done
manifest
echo "arm $ARM complete: $(cat $A/state.json)"
