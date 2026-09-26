#!/bin/bash
# RBT-106: one arm (PREREGISTRATION.md §7).  RBT-90 part 2's command, taken from RBT-104's seed_founders.PART2
# by command.py, plus the arm's founders and at most one flag:
#
#   HU  founders w = 32                         H pair, uniform world
#   HP  founders w = 32, --food-patches 3       H pair, patchy world   (the one flag)
#   P1  founders w = 1,  --food-patches 3       P pair, patchy world; its uniform twin is RBT-104's S1
#   S1  founders w = 1                          RBT-104's S1, run here only under §7.3's contingency
#
#   runs/RBT-106/run_arm.sh ARM SEED      ->  runs/RBT-106/ARM-SEED/
#
# Launched as a harness background task, never with nohup, beside
#   DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-106/ARM-SEED rbt-106-ARM-SEED
# (README rules 1, 3 and 6).  House packing: two arms per session side by side at WORKERS=2 (waves.txt).
set -e
ARM=$1; SEED=$2
cd "$(dirname "$0")/../.."
OUT=runs/RBT-106/$ARM-$SEED
case "$ARM" in HU|HP) W=32 ;; P1|S1) W=1 ;; *) echo "unknown arm $ARM" >&2; exit 2 ;; esac
[ "$(uname -m)" = x86_64 ] || { echo "RBT-106 arms run on the cloud x86_64 image only (RBT-96)" >&2; exit 3; }
F=runs/RBT-106/founders-w$W-$SEED
# founders.py regenerates them and exits non-zero unless the digest is the committed one
# (w = 1: RBT-104's founders-digests.txt; w = 32: runs/RBT-106/founders-digests.txt)
if [ ! -f "$F/SHA256SUMS" ]; then python runs/RBT-106/founders.py "$SEED" "$W" "$F"; fi
(cd "$F" && sha256sum -c --quiet SHA256SUMS)
python - "$SEED" "$W" "$F" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("fd", "runs/RBT-106/founders.py"); fd = importlib.util.module_from_spec(spec); spec.loader.exec_module(fd)
seed, w, f = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
assert fd.digest_of(f) == fd.committed(w)[seed], f"founders {f} are not the pre-registered ones"
PY
if [ -f "$OUT/state.json" ]; then echo "$OUT exists: resume it with rabbitstew ecology --resume --out $OUT, never relaunch" >&2; exit 4; fi
mkdir -p "$OUT"
python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$OUT/platform.txt"
mapfile -d '' CMD < <(python runs/RBT-106/command.py "$ARM" "$SEED" "$OUT")
echo "${CMD[*]}" > "$OUT/command.txt"
exec "${CMD[@]}" > "$OUT/run.log" 2>&1
