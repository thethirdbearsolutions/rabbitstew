#!/bin/bash
# RBT-113: one arm (PREREGISTRATION.md §3, §8).  An arm is one operator on a block of three seeds, each seed's three
# line runs (U, D, C) in turn, sequentially:
#
#   arm   operator                                                seeds       seed directories
#   O1    default                                                 1 2 3       runs/RBT-113/O1/1 .. /3
#   O2    default                                                 4 5 6
#   O3    default                                                 7 8 9
#   O4    default                                                 10 11 12
#   Z1    --global-bias-sigma 0 --holistic-stream-salt 1         1 2 3       runs/RBT-113/Z1/Z1 .. /Z3
#   Z2..Z4 likewise on 4-6, 7-9, 10-12
#
#   runs/RBT-113/run_arm.sh ARM      ->  runs/RBT-113/ARM/<OP><SEED>/{U,D,C}/   (each an `evolve` output directory)
#
# Launched as a harness background task, never with nohup, beside
#   DURABLE_WATCH_PID=<this script's pid> scripts/durable.sh every 20 runs/RBT-113/ARM rbt-113-ARM
# Two arms per session at WORKERS=2 (RUNNER.md).  The arm directory carries a progress manifest for durable.sh
# (config.json {"generations": 9 x G} and state.json {"populations": {"arm": {"generation": done}}}), updated as
# each line run completes; it is bookkeeping, not evidence.
#
# RE-RUNNING THIS SCRIPT IS HOW AN ARM IS RESUMED: a complete line run (its history.json has G generations and it
# exited) is skipped, a started one is continued with `evolve --resume` (byte for byte, RBT-93), and a missing one is
# launched.  So after a container restart: `scripts/durable.sh restore runs/RBT-113/ARM rbt-113-ARM`, then this.
#
# Refuses (exit codes): 2 unknown arm; 3 not x86_64 (RBT-96); 5 rabbitstew/ has uncommitted changes;
#   7 controls/prelaunch.txt does not read PRELAUNCH: PASS on this rabbitstew/ tree (prelaunch.sh)
set -e
ARM=$1
cd "$(dirname "$0")/../.."
case "$ARM" in
  O1|Z1) SEEDS="1 2 3";; O2|Z2) SEEDS="4 5 6";; O3|Z3) SEEDS="7 8 9";; O4|Z4) SEEDS="10 11 12";;
  *) echo "unknown arm $ARM (O1-O4, Z1-Z4)" >&2; exit 2;;
esac
OP=${ARM:0:1}; [ "$OP" = O ] && OP=""
[ "$(uname -m)" = x86_64 ] || { echo "RBT-113 arms run on the cloud x86_64 image only (RBT-96)" >&2; exit 3; }
if ! git diff --quiet HEAD -- rabbitstew || [ -n "$(git status --porcelain -- rabbitstew)" ]; then
  echo "REFUSED: rabbitstew/ has uncommitted changes; launch from a clean checkout" >&2; exit 5
fi
grep -q "^PRELAUNCH: PASS" runs/RBT-113/controls/prelaunch.txt 2>/dev/null || { echo "REFUSED: the pre-launch controls have not passed (prelaunch.sh)" >&2; exit 7; }
grep -q "^rabbitstew_tree $(git rev-parse HEAD:rabbitstew)$" runs/RBT-113/controls/prelaunch.txt || { echo "REFUSED: controls/prelaunch.txt was made on another rabbitstew/ tree; re-run prelaunch.sh" >&2; exit 7; }
G=$(python -c "import sys; sys.path.insert(0, 'runs/RBT-113'); import world; print(world.GENERATIONS)")
A=runs/RBT-113/$ARM
mkdir -p "$A"
if [ ! -f "$A/commit.txt" ]; then
  python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$A/platform.txt"
  printf '# RBT-113 launch record\ncommit %s\nrabbitstew_tree %s\nworkers %s\n' "$(git rev-parse HEAD)" "$(git rev-parse HEAD:rabbitstew)" "${WORKERS:-2}" > "$A/commit.txt"
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
      mapfile -d '' CMD < <(python runs/RBT-113/world.py "$L" "${OP:--}" "$s" "$R")
      echo "${CMD[*]}" > "$R/command.txt"
      "${CMD[@]}" > "$R/run.log" 2>&1
    fi
    manifest
  done
done
manifest
echo "arm $ARM complete: $(cat $A/state.json)"
