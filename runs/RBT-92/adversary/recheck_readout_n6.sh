#!/bin/bash
# RBT-92 adversary re-check: run readout.py through its VERDICT section at n = 6, which smoke.sh (n = 2) never
# reaches.  Six throwaway "seeds" are staged by copying the shared_baseline_runs.sh short runs of 801 and 9901
# three times each under new seed numbers (read for nothing; only whether the code runs and what type r has).
#   runs/RBT-92/adversary/recheck_readout_n6.sh [READOUT_PY]   (default runs/RBT-92/readout.py)
set -e
RO=${1:-runs/RBT-92/readout.py}
S=$(mktemp -d); trap 'rm -rf "$S"' EXIT
mkdir -p "$S/data"
SEEDS=""
for i in 1 2 3; do for B in 801 9901; do
  N=$((B * 10 + i)); SEEDS="$SEEDS $N"
  for A in plain shift cull; do cp -r runs/RBT-92/data/sbc-$A-$B "$S/data/sbc-$A-$N"; done
done; done
# smoke.sh reads runs/RBT-92/data; point it at the staged copies through a scratch tree
mkdir -p "$S/tree/runs/RBT-92" && cp runs/RBT-92/*.py runs/RBT-92/smoke.sh "$S/tree/runs/RBT-92/" && cp "$RO" "$S/tree/runs/RBT-92/readout.py"
ln -s "$S/data" "$S/tree/runs/RBT-92/data"; ln -s "$(pwd)/runs/RBT-71" "$S/tree/runs/RBT-71"
cd "$S/tree" && sed -i 's/^\[ -s "\$S\/err.txt" \] && tail -5/[ -s "$S\/err.txt" ] \&\& tail -3/' runs/RBT-92/smoke.sh
bash runs/RBT-92/smoke.sh $SEEDS 2>&1 | grep -E "exit status|Error|Traceback|CLASS|equivalence|turnover guard" | sed -E 's/[-+]?[0-9]+\.[0-9]+/#/g'
