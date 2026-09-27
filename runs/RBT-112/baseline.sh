#!/bin/bash
# RBT-112 step 3 (DECISION.md): the w = 32, K = 1 operator-alone baseline on RBT-106's ten seeds, at the
# default (must reproduce RBT-106's committed tables) and at --global-bias-sigma 0.
set -e
cd "$(dirname "$0")/../.."
for SEED in 801 804 805 806 807 1 2 3 4 7; do
  F=runs/RBT-106/founders-w32-$SEED
  [ -f "$F/SHA256SUMS" ] || python runs/RBT-106/founders.py "$SEED" 32 "$F"
  python runs/RBT-112/baseline.py "$SEED" "$F" > runs/RBT-112/baseline/baseline-w32-$SEED.txt
  python runs/RBT-112/baseline.py "$SEED" "$F" --global-bias-sigma 0 > runs/RBT-112/baseline/baseline-w32-S0-$SEED.txt
done
