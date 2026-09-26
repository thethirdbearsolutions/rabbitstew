#!/bin/bash
# RBT-99, epoch C2: the readout, which is RBT-92's readout.py run unchanged on C2's arms.
# readout.py reads four arms per seed under one directory; this wrapper assembles that directory from
# committed files only, by symlink, in a scratch directory it removes:
#
#   shift-SEED, cull-SEED     runs/RBT-99/  (this ticket's arms)
#   cull20-SEED, base-SEED    runs/RBT-92/  (RBT-92's validation cull, the same run as C2's would be; and
#                                            RBT-92's body digests of the RBT-90 baseline)
#   baseline                  runs/RBT-90/forage-SEED (readout.py's default), onset runs/RBT-92/onset.txt
#
#   runs/RBT-99/readout.sh > runs/RBT-99/readout.txt
set -e
S=$(mktemp -d)
trap 'rm -rf "$S"' EXIT
R=$(pwd)
for SEED in ${RBT92_SEEDS:-801 804 805 806 807 1 2 3 4 7}; do
  for A in shift cull; do [ -e "$R/runs/RBT-99/$A-$SEED" ] && ln -s "$R/runs/RBT-99/$A-$SEED" "$S/$A-$SEED"; done
  for A in cull20 base; do [ -e "$R/runs/RBT-92/$A-$SEED" ] && ln -s "$R/runs/RBT-92/$A-$SEED" "$S/$A-$SEED"; done
done
echo "RBT-99, epoch C2 (dearer work: --shift-at T --shift work-cost=0.08), on RBT-92's readout; shift and cull"
echo "arms from runs/RBT-99, cull20 and the baseline's body digests from runs/RBT-92 (runs/RBT-99/readout.sh)"
echo
RBT92_ARM_DIR="$S" RBT92_ONSET="${RBT92_ONSET:-$R/runs/RBT-92/onset.txt}" python "$R/runs/RBT-92/readout.py"
