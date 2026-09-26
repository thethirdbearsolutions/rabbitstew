#!/bin/bash
# RBT-101, epoch C4 (the furniture removed): one arm of one seed, by RBT-92's launcher itself (runs/RBT-92/run_arm.sh),
# which a sibling challenge reuses unchanged but for SHIFT and OUTROOT (RBT-92 amendment 2, on integration via PR #87):
#
#   shift   --shift-at T --shift terrain=flat                C4 of RBT-89: the fourteen random obstacles removed
#   cull    --cull-at  T --cull holistic=K1,conventional=K2  the null, K from runs/RBT-101/cull-k-SEED.txt, written by
#                                                            python runs/RBT-92/cull_k.py SEED runs/RBT-101/shift-SEED
#                                                            > runs/RBT-101/cull-k-SEED.txt;  k = 0/0: RBT-92's launcher
#                                                            exits 0 and runs nothing, the null is the baseline itself
#
# cull20 is not run for C4: it carries no challenge flag, so it is RBT-92's arm, cited (PREREGISTRATION.md section 7).
# T is the seed's onset from runs/RBT-92/onset.txt.  The exec'd command is RBT-92's, byte for byte.
#
#   WORKERS=4 runs/RBT-101/run_arm.sh SEED ARM        ->  runs/RBT-101/ARM-SEED/
#
# Launch as a harness background task, never nohup, with scripts/durable.sh every 20 beside it
# (label rbt-101-ARM-SEED).  Afterwards: python runs/RBT-92/tables.py runs/RBT-101/ARM-SEED
#                                        python runs/RBT-101/wiring.py runs/RBT-101/ARM-SEED
set -e
case "$2" in shift|cull) ;; *) echo "usage: run_arm.sh SEED {shift|cull}  (cull20 is RBT-92's, cited)" >&2; exit 2 ;; esac
HERE=$(cd "$(dirname "$0")" && pwd)
SHIFT=terrain=flat OUTROOT=runs/RBT-101 exec "$HERE/../RBT-92/run_arm.sh" "$@"
