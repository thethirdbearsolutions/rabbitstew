#!/bin/bash
# RBT-106: the post-run steps of one arm (PREREGISTRATION.md §7.2), after season 599, before the final save.
#
#   runs/RBT-106/postrun.sh ARM SEED
#
# Writes into runs/RBT-106/ARM-SEED/: seasons.txt + lineage-last.txt (RBT-71's measure.summarise), rbt102.txt
# (RBT-102's analyse.py), held-300.txt + held-599.txt (held.py), function-uniform.txt + function-patchy.txt
# (RBT-104's function.py in the arm's own world, cross_world.py in the other), function-pc.txt (function.py
# --install 32, own world).  Then run `scripts/durable.sh save runs/RBT-106/ARM-SEED rbt-106-ARM-SEED` (rule 6).
#
# ARM S1 is RBT-104's arm: its bulk is restored from ckpt/rbt-104-S1-SEED into runs/RBT-106/S1-SEED/bulk (§7.3)
# unless RBT-106 ran it itself, and RBT-104's committed readouts are reused where they are the same file.
#
# Smoke tests only: RBT106_WINDOW=A,B (held seasons, readout window) and GENS=g1,g2,.. (function.py bodies).
set -e
ARM=$1; SEED=$2
cd "$(dirname "$0")/../.."
D=runs/RBT-106/$ARM-$SEED
case "$ARM" in HU|HP) W=32 ;; P1|S1) W=1 ;; *) echo "unknown arm $ARM" >&2; exit 2 ;; esac
IFS=, read -r W0 W1 <<< "${RBT106_WINDOW:-300,599}"
GENSARG=(); [ -n "$GENS" ] && GENSARG=(--gens "$GENS")
RUN=$D
if [ "$ARM" = S1 ] && [ ! -f "$D/state.json" ]; then
  RUN=$D/bulk
  [ -f "$RUN/state.json" ] || scripts/durable.sh restore "$RUN" "rbt-104-S1-$SEED"
  for f in platform.txt rbt102.txt function-pc.txt; do
    [ -f "runs/RBT-104/S1-$SEED/$f" ] && cp "runs/RBT-104/S1-$SEED/$f" "$D/$f"
  done
  [ -f "runs/RBT-104/S1-$SEED/function.txt" ] && cp "runs/RBT-104/S1-$SEED/function.txt" "$D/function-uniform.txt"
fi
python - "$RUN" "$D" <<'PY'
import importlib.util, shutil, sys, os
spec = importlib.util.spec_from_file_location("measure", "runs/RBT-71/measure.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
run, d = sys.argv[1], sys.argv[2]
m.summarise(run)
if run != d:
    for f in ("seasons.txt", "lineage-last.txt"):
        shutil.copy(os.path.join(run, f), os.path.join(d, f))
PY
PATCHES=$(python -c "import json,sys; print(json.load(open('$RUN/config.json'))['sim']['food']['patches'])")
if [ "$PATCHES" = 0 ]; then OWN=uniform; OTHER=patchy; OTHERW=runs/RBT-106/world-patchy
else OWN=patchy; OTHER=uniform; OTHERW=runs/RBT-90/forage-$SEED; fi
[ -f "$D/platform.txt" ] || { echo "no platform.txt in $D" >&2; exit 3; }
[ -f "$D/rbt102.txt" ] || RBT102_WINDOW="$W0,$W1" python runs/RBT-102/analyse.py "$RUN" > "$D/rbt102.txt"
for s in "$W0" "$W1"; do python runs/RBT-106/held.py "$RUN" "$SEED" "$W" --season "$s" > "$D/held-$s.txt"; done
[ -f "$D/function-$OWN.txt" ] || python runs/RBT-104/function.py --run "$RUN" "${GENSARG[@]}" > "$D/function-$OWN.txt"
python runs/RBT-106/cross_world.py --world "$OTHERW" --run "$RUN" "${GENSARG[@]}" > "$D/function-$OTHER.txt"
[ -f "$D/function-pc.txt" ] || python runs/RBT-104/function.py --run "$RUN" "${GENSARG[@]}" --install 32 > "$D/function-pc.txt"
echo "post-run done for $D; now: scripts/durable.sh save $D rbt-106-$ARM-$SEED"
