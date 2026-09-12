#!/bin/bash
# Re-read every claim in RBT-38's table at 64 paired seeds.
PY=/tmp/claude-0/venv/bin/python
run() { echo; echo "##### $1 $2 g$3 #####"; $PY scripts/paired_lesion.py "runs/RBT-38/data/$1" "$2" "$3" 64 2>&1 | grep -v WARNING; }
run RBT-13 conventional 590
run RBT-13 holistic 390
run RBT-17 conventional 590
run RBT-17 conventional 500
run RBT-18 conventional 0
run RBT-20 conventional 0
run baseline-801 conventional 500
run baseline-801 conventional 20
run baseline-801 conventional 30
run RBT-16 conventional 590
run RBT-16 conventional 100
run RBT-23 conventional 590
run RBT-22 conventional 300
echo; echo "##### SWEEP COMPLETE #####"
