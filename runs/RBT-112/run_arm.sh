#!/bin/bash
# RBT-112: one arm (PREREGISTRATION.md §3, §7).  RBT-106's HU command (RBT-106's command.py, imported by
# runs/RBT-112/command.py) plus exactly one flag:
#
#   HZ  founders w = 32 (RBT-106's), --global-bias-sigma 0      the arm; paired control RBT-106's HU-SEED
#
#   runs/RBT-112/run_arm.sh HZ SEED      ->  runs/RBT-112/HZ-SEED/
#
# Launched as a harness background task, never with nohup, beside
#   DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-112/HZ-SEED rbt-112-HZ-SEED
# (README rules 1, 3 and 6).  Two arms per session at WORKERS=2 (waves.txt).
#
# Refuses to launch (the RBT-104 lesson and RBT-106's F2, made mechanical):
#   exit 2  unknown arm;  exit 3  not x86_64 (RBT-96);  exit 4  the run exists (resume it)
#   exit 5  rabbitstew/ has uncommitted changes
#   exit 6  no runs/RBT-112/cross-ticket-<commit12>.txt recording SAME RUN against RBT-106's HU-801 and HU-4 at THIS
#           commit (certify.sh): the pair must be one flag apart on the code that actually runs
#   exit 7  no runs/RBT-112/controls/prelaunch.txt reading "PRELAUNCH: PASS" on THIS rabbitstew/ tree (prelaunch.sh): the
#           per-arm install control, analyse.py's control and the HELD call shown able to pass on the arm's own S = 0 hosts
set -e
ARM=$1; SEED=$2
cd "$(dirname "$0")/../.."
OUT=runs/RBT-112/$ARM-$SEED
[ "$ARM" = HZ ] || { echo "unknown arm $ARM" >&2; exit 2; }
[ "$(uname -m)" = x86_64 ] || { echo "RBT-112 arms run on the cloud x86_64 image only (RBT-96)" >&2; exit 3; }
if ! git diff --quiet HEAD -- rabbitstew || [ -n "$(git status --porcelain -- rabbitstew)" ]; then
  echo "REFUSED: rabbitstew/ has uncommitted changes; launch from a clean checkout" >&2; exit 5
fi
HEADC=$(git rev-parse HEAD)
CT=runs/RBT-112/cross-ticket-${HEADC:0:12}.txt
if ! { [ -f "$CT" ] && grep -q "^CROSS-TICKET HU-801: SAME RUN (prefix)" "$CT" && grep -q "^CROSS-TICKET HU-4: SAME RUN (prefix)" "$CT"; }; then
  echo "REFUSED: $CT does not record SAME RUN against RBT-106's HU-801 and HU-4 at this commit (run certify.sh)" >&2; exit 6
fi
grep -q "^PRELAUNCH: PASS" runs/RBT-112/controls/prelaunch.txt 2>/dev/null || { echo "REFUSED: the pre-launch controls have not passed (prelaunch.sh)" >&2; exit 7; }
grep -q "^rabbitstew_tree $(git rev-parse HEAD:rabbitstew)$" runs/RBT-112/controls/prelaunch.txt || { echo "REFUSED: controls/prelaunch.txt was made on another rabbitstew/ tree; re-run prelaunch.sh" >&2; exit 7; }
F=runs/RBT-106/founders-w32-$SEED
if [ ! -f "$F/SHA256SUMS" ]; then python runs/RBT-106/founders.py "$SEED" 32 "$F"; fi
(cd "$F" && sha256sum -c --quiet SHA256SUMS)
python - "$SEED" "$F" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("fd", "runs/RBT-106/founders.py"); fd = importlib.util.module_from_spec(spec); spec.loader.exec_module(fd)
seed, f = int(sys.argv[1]), sys.argv[2]
assert fd.digest_of(f) == fd.committed(32.0)[seed], f"founders {f} are not the pre-registered ones"
PY
if [ -f "$OUT/state.json" ]; then echo "$OUT exists: resume it with rabbitstew ecology --resume --out $OUT, never relaunch" >&2; exit 4; fi
mkdir -p "$OUT"
python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$OUT/platform.txt"
printf '# RBT-112 launch record\ncommit %s\nrabbitstew_tree %s\ncertified %s\n' "$HEADC" "$(git rev-parse HEAD:rabbitstew)" "$CT" > "$OUT/commit.txt"
mapfile -d '' CMD < <(python runs/RBT-112/command.py "$ARM" "$SEED" "$OUT")
echo "${CMD[*]}" > "$OUT/command.txt"
exec "${CMD[@]}" > "$OUT/run.log" 2>&1
