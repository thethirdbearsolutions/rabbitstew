#!/bin/bash
# RBT-112: the post-run steps (PREREGISTRATION.md §7.2), after season 599, before the final save.
#
#   runs/RBT-112/postrun.sh HZ SEED     the arm: into runs/RBT-112/HZ-SEED/
#   runs/RBT-112/postrun.sh HU SEED     the F12 print on RBT-106's paired control, restored from ckpt/rbt-106-HU-SEED
#                                       into $BULK_ROOT/HU-SEED (outside the checkout); writes runs/RBT-112/HU-SEED/resting.txt only
#
# HZ writes, with RBT-106's instruments unchanged: seasons.txt + lineage-last.txt (RBT-71 measure.summarise), rbt102.txt
# (RBT-102 analyse.py), held-300.txt + held-599.txt (runs/RBT-112/held.py: RBT-106's held.py against the S = 0 operator's
# table), function-uniform.txt (RBT-104 function.py) + function-patchy.txt (RBT-106 cross_world.py), function-pc.txt
# (function.py --install 32), and resting.txt (resting.py --frozen: F12's resting drive per champion, beside the control).
# Then: scripts/durable.sh save runs/RBT-112/HZ-SEED rbt-112-HZ-SEED   (README rule 6).
# Smoke tests only: RBT112_WINDOW=A,B (held seasons, readout window) and GENS=g1,g2,.. (function.py bodies).
set -e
ARM=$1; SEED=$2
cd "$(dirname "$0")/../.."
IFS=, read -r W0 W1 <<< "${RBT112_WINDOW:-300,599}"
GENSARG=(); [ -n "$GENS" ] && GENSARG=(--gens "$GENS")
D=runs/RBT-112/$ARM-$SEED
case "$ARM" in
  HU)
    RUN=${BULK_ROOT:-/tmp/rbt-112-bulk}/HU-$SEED
    [ -f "$RUN/state.json" ] || scripts/durable.sh restore "$RUN" "rbt-106-HU-$SEED"
    mkdir -p "$D"
    [ -f runs/RBT-106/HU-$SEED/function-pc.txt ] && PC=(--pc runs/RBT-106/HU-$SEED/function-pc.txt) || PC=()
    python runs/RBT-112/resting.py --run "$RUN" "${GENSARG[@]}" "${PC[@]}" > "$D/resting.txt"
    echo "F12 print done for RBT-106's HU-$SEED: $D/resting.txt"; exit 0 ;;
  HZ) RUN=$D ;;
  *) echo "unknown arm $ARM" >&2; exit 2 ;;
esac
[ -f "$D/platform.txt" ] || { echo "no platform.txt in $D" >&2; exit 3; }
python - "$RUN" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("measure", "runs/RBT-71/measure.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.summarise(sys.argv[1])
PY
[ -f "$D/rbt102.txt" ] || RBT102_WINDOW="$W0,$W1" python runs/RBT-102/analyse.py "$RUN" > "$D/rbt102.txt"
for s in "$W0" "$W1"; do python runs/RBT-112/held.py "$RUN" "$SEED" 32 --season "$s" > "$D/held-$s.txt"; done
[ -f "$D/function-uniform.txt" ] || python runs/RBT-104/function.py --run "$RUN" "${GENSARG[@]}" > "$D/function-uniform.txt"
python runs/RBT-106/cross_world.py --world runs/RBT-106/world-patchy --run "$RUN" "${GENSARG[@]}" > "$D/function-patchy.txt"
[ -f "$D/function-pc.txt" ] || python runs/RBT-104/function.py --run "$RUN" "${GENSARG[@]}" --install 32 > "$D/function-pc.txt"
python runs/RBT-112/resting.py --run "$RUN" "${GENSARG[@]}" --pc "$D/function-pc.txt" --frozen > "$D/resting.txt"
echo "post-run done for $D; now: scripts/durable.sh save $D rbt-112-$ARM-$SEED"
