#!/bin/bash
# RBT-105: the 20-season throwaway check of --breed-stream on a real seed, before any arm.  Three arms of seed
# SEED (default 7) at K = 0, 1, 2 through run_arm.sh itself (SEASONS=20, OUTROOT scratch, NO_DURABLE), then
# throwaway_check.py against the seed's RBT-90 part 2 arm restored from its checkpoint.
#
#   runs/RBT-105/throwaway.sh SCRATCH [SEED]  > runs/RBT-105/throwaway.txt
set -e
SCRATCH=$1
SEED=${2:-7}
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE/../.."
[ -d "$SCRATCH/rbt90-forage-$SEED" ] || scripts/durable.sh restore "$SCRATCH/rbt90-forage-$SEED" "rbt-90-$SEED" >&2
for K in 0 1 2; do
  rm -rf "$SCRATCH/throwaway/forage-$SEED-b$K"
  SEASONS=20 OUTROOT="$SCRATCH/throwaway" NO_DURABLE=1 WORKERS=1 "$HERE/run_arm.sh" "$SEED" "$K" > "$SCRATCH/throwaway-b$K.out" 2>&1 &
done
wait
python "$HERE/throwaway_check.py" "$SCRATCH/rbt90-forage-$SEED" "$SEED" "$SCRATCH"/throwaway/forage-$SEED-b{0,1,2}
