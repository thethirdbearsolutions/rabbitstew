#!/bin/bash
# RBT-101: why the re-wiring readout scores `new` (PREREGISTRATION.md section 6.3).  The positive control
# (control.py analyse) on the same committed tables, runs/RBT-101/control/SEED.txt, once per candidate
# statistic and sign-guard setting; the summary and the n = 10 rows of each are kept.
#   runs/RBT-101/control_stats.sh > runs/RBT-101/control_stats.txt
set -e
for cfg in "g2 1" "g2 0" "lg2 1" "g1 1" "g1 0" "new 1" "new 0"; do
  set -- $cfg
  echo "######## statistic $1, sign guard $([ "$2" = 1 ] && echo on || echo off)"
  RBT101_STAT=$1 RBT101_SIGN_GUARD=$2 python runs/RBT-101/control.py analyse \
    | grep -E '^== |no install|n=10 |^ +w=1\.0|^CONTROL n=10' | awk '/n=10 /{show=2} /^ +w=1\.0/{if(show>0){print; show--}; next} {print}'
  echo
done
