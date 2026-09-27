#!/bin/bash
# RBT-112, before any arm (PREREGISTRATION.md §6; the RBT-104 lesson, now a programme rule): run every per-arm control
# on the arm's OWN hosts, as the readout will run it, and show that it can pass.  Throwaway smoke runs, not arms:
# HZ (RBT-106's HU command + --global-bias-sigma 0) for 61 seasons on seeds 801 and 4, outside the checkout.
# On each, with the readout's own instruments and seven bodies (bests 0, 10, ..., 60: the readout's n, t(6)):
#   analyse.py's positive control (window 30-59)          -> controls/prelaunch-rbt102-HZ-SEED.txt
#   the install control, function.py --install 32          -> controls/prelaunch-pc-HZ-SEED.txt
#   F12's resting drive, resting.py --frozen                -> controls/prelaunch-resting-HZ-SEED.txt
# and prelaunch.py adds the HELD call's reachability on the S = 0 tables, then writes controls/prelaunch.txt,
# whose "PRELAUNCH: PASS" line run_arm.sh requires.
set -e
cd "$(dirname "$0")/../.."
SM=${SMOKE_ROOT:-/tmp/rbt-112-smoke}
C=runs/RBT-112/controls
mkdir -p "$C"
GENS=0,10,20,30,40,50,60
pids=()
for SEED in 801 4; do
  F=runs/RBT-106/founders-w32-$SEED
  [ -f "$F/SHA256SUMS" ] || python runs/RBT-106/founders.py "$SEED" 32 "$F"
  R=$SM/HZ-$SEED
  if [ ! -f "$R/state.json" ] || [ "$(python -c "import json; print(json.load(open('$R/state.json'))['season'])")" -lt 61 ]; then
    rm -rf "$R"; mkdir -p "$R"
    mapfile -d '' CMD < <(SEASONS=61 WORKERS=2 python runs/RBT-112/command.py HZ "$SEED" "$R")
    "${CMD[@]}" > "$R/run.log" 2>&1 & pids+=($!)
  fi
done
for p in "${pids[@]}"; do wait "$p"; done
for SEED in 801 4; do
  R=$SM/HZ-$SEED
  python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$R/platform.txt"
  python - "$R" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("measure", "runs/RBT-71/measure.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.summarise(sys.argv[1])
PY
  RBT102_WINDOW=30,59 python runs/RBT-102/analyse.py "$R" > "$C/prelaunch-rbt102-HZ-$SEED.txt"
  python runs/RBT-104/function.py --run "$R" --gens "$GENS" --install 32 > "$C/prelaunch-pc-HZ-$SEED.txt"
  python runs/RBT-112/resting.py --run "$R" --gens "$GENS" --pc "$C/prelaunch-pc-HZ-$SEED.txt" --frozen > "$C/prelaunch-resting-HZ-$SEED.txt" || true
  cp "$R/seasons.txt" "$C/prelaunch-seasons-HZ-$SEED.txt"
  cp "$R/config.json" "$C/prelaunch-config-HZ-$SEED.txt"
done
python runs/RBT-112/prelaunch.py > "$C/prelaunch.txt"
cat "$C/prelaunch.txt" | tail -8
