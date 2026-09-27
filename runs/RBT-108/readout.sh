#!/bin/sh
# RBT-108: write runs/RBT-108/readout.txt from the committed summaries alone (no bulk, no simulation).
# Part A is RBT-96's unchanged readout over all sixteen seeds; part B is this ticket's extra statistics.
set -e
cd "$(dirname "$0")/../.."
{
  echo "=== A. python runs/RBT-96/readout.py runs/RBT-96 --seeds 201,...,216 --from-summaries (RBT-96's instrument, unchanged) ==="
  echo "NB: its sections 3-4 print RBT-96's n = 4 labels ('3 df', '4 df', 'a 4-seed mean') beside figures computed at n = 16;"
  echo "    the registered n = 16 figures are part B's. Its section 5 compares with RBT-85's base-201..204 only."
  echo
  python runs/RBT-96/readout.py runs/RBT-96 --seeds 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216 --from-summaries
  echo
  echo "=== B. python runs/RBT-108/readout.py ==="
  echo
  python runs/RBT-108/readout.py
} > runs/RBT-108/readout.txt
