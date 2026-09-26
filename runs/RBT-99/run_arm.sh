#!/bin/bash
# RBT-99, epoch C2 (dearer work): one arm of one seed, on RBT-92's instrument.  RBT-92's launcher
# (runs/RBT-92/run_arm.sh) run unchanged but for its two sibling variables:
#
#   shift   --shift-at T --shift work-cost=0.08               C2 of RBT-89 (docs/held-out-challenges.md section 2)
#   cull    --cull-at  T --cull holistic=K1,conventional=K2    the null; K from runs/RBT-99/cull-k-SEED.txt,
#                                                             written by RBT-92's cull_k.py on THIS ticket's shift arm
#
# T is the seed's onset from runs/RBT-92/onset.txt (the shared baseline's; the same T as RBT-92's arms).
# No cull20 arm here: RBT-92's cull20-SEED is the same command at the same seed and T, so it is the same run
# byte for byte, and RBT-99 cites it (PREREGISTRATION.md section 6).
#
#   WORKERS=4 runs/RBT-99/run_arm.sh SEED {shift|cull}     ->  runs/RBT-99/ARM-SEED/
#
# Launch as a harness background task with DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20
# runs/RBT-99/ARM-SEED rbt-99-ARM-SEED beside it.  Afterwards: python runs/RBT-92/tables.py runs/RBT-99/ARM-SEED
set -e
case "$2" in
  shift|cull) ;;
  *) echo "usage: run_arm.sh SEED {shift|cull}  (cull20 is RBT-92's arm, cited)" >&2; exit 2 ;;
esac
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE/../.."   # OUTROOT is relative to the repository root, so launch from anywhere (adversary nit)
SHIFT=work-cost=0.08 OUTROOT=runs/RBT-99 exec "$HERE/../RBT-92/run_arm.sh" "$1" "$2"
