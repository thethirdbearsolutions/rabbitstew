#!/bin/bash
# RBT-101, epoch C4: the income, recovery, carriage and class readout is RBT-92's readout.py, run unchanged on this
# ticket's arms.  It reads ARM_DIR/{shift,cull,cull20,base}-SEED and ARM_DIR/cull-k-SEED.txt; this stages a directory
# of links and runs it with RBT92_ARM_DIR pointing there:
#   shift-SEED, cull-SEED, cull-k-SEED.txt  -> runs/RBT-101/   (this ticket's arms and null sizes)
#   cull20-SEED, base-SEED                  -> runs/RBT-92/    (challenge-free: RBT-92's, cited)
# k = 0/0 needs nothing here: readout.py reads the cull-k file and uses the baseline as the null (RBT-92 amendment 2).
# The re-wiring readout is separate: rewire.py.  Every other RBT92_* setting passes through (the smoke test uses them).
#   runs/RBT-101/readout.sh > runs/RBT-101/readout.txt
set -e
ARMS=${RBT101_ARM_DIR:-runs/RBT-101}
R92=${RBT101_RBT92_DIR:-runs/RBT-92}
S=$(mktemp -d)
trap 'rm -rf "$S"' EXIT
for SEED in ${RBT92_SEEDS:-801 804 805 806 807 1 2 3 4 7}; do
  for A in shift-$SEED cull-$SEED cull-k-$SEED.txt; do [ -e "$ARMS/$A" ] && ln -s "$(cd "$(dirname "$ARMS/$A")" && pwd)/$A" "$S/$A"; done
  for A in cull20-$SEED base-$SEED; do [ -e "$R92/$A" ] && ln -s "$(cd "$R92" && pwd)/$A" "$S/$A"; done
done
echo "# RBT-101 (C4, --shift terrain=flat): RBT-92's readout.py on $ARMS/{shift,cull}-SEED with RBT-92's cull20 and base digests"
RBT92_ARM_DIR="$S" python runs/RBT-92/readout.py
