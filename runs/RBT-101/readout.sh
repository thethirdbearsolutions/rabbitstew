#!/bin/bash
# RBT-101, epoch C4: the income, recovery, carriage and class readout is RBT-92's readout.py, run unchanged on
# this ticket's arms.  It reads ARM_DIR/{shift,cull,cull20,base}-SEED; this stages a directory of links:
#   shift-SEED, cull-SEED   -> runs/RBT-101/          (this ticket's arms)
#   cull20-SEED, base-SEED  -> runs/RBT-92/           (the validation cull and the baseline body digests are
#                                                       challenge-free, so they are RBT-92's, cited)
# then runs readout.py with RBT92_ARM_DIR pointing at it.  The re-wiring readout is separate: rewire.py.
#   runs/RBT-101/readout.sh > runs/RBT-101/readout.txt
set -e
S=$(mktemp -d)
trap 'rm -rf "$S"' EXIT
R=$(pwd)
for SEED in 801 804 805 806 807 1 2 3 4 7; do
  for A in shift cull; do [ -e "runs/RBT-101/$A-$SEED" ] && ln -s "$R/runs/RBT-101/$A-$SEED" "$S/$A-$SEED"; done
  # k = 0 for both faunas: no cull arm exists and the null is the baseline itself (PREREGISTRATION.md section 7)
  if [ ! -e "runs/RBT-101/cull-$SEED" ] && grep -q $'^cull\tholistic=0,conventional=0$' "runs/RBT-101/cull-k-$SEED.txt" 2>/dev/null; then
    mkdir "$S/cull-$SEED"
    for F in seasons.txt lineage-last.txt; do ln -s "$R/runs/RBT-90/forage-$SEED/$F" "$S/cull-$SEED/$F"; done
    ln -s "$R/runs/RBT-92/base-$SEED/bodysig.txt" "$S/cull-$SEED/bodysig.txt"
    printf "kind\tpopulation\tseason\tcount\tnames\n" > "$S/cull-$SEED/events.txt"
    echo "# seed $SEED: k = 0 for both faunas; the cull arm is the baseline itself (no event), so R-null = R-shift"
  fi
  for A in cull20 base; do [ -e "runs/RBT-92/$A-$SEED" ] && ln -s "$R/runs/RBT-92/$A-$SEED" "$S/$A-$SEED"; done
done
echo "# RBT-101 (C4, --shift terrain=flat): RBT-92's readout.py on runs/RBT-101/{shift,cull}-SEED with RBT-92's cull20 and base digests"
RBT92_ARM_DIR="$S" python runs/RBT-92/readout.py
