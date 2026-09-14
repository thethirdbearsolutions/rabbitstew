#!/bin/bash
# RBT-28: the forage-shaped lab on all five champions. Run runs/RBT-28/extract.sh first.
D=runs/RBT-28/data
N=${1:-12}; DRAWS=${2:-120}
run() { echo; echo "##### $1 $2 g$3 #####"; python3 scripts/forage_lab.py "$D/$1" "$2" "$3" "$N" "$DRAWS" 2>&1 | grep -v WARNING; }
run RBT-13       holistic 390   # 3.12 items on 1.2 kJ, the strongest mower of the series
run RBT-16       holistic 590   # two food sensors on separated segments: the exact compass wiring
run RBT-17       holistic 590   # the crowded arena's best; nosed and inert
run RBT-22       holistic 590   # the first inert nose with a readable gradient to ignore
run baseline-801 holistic 300   # the contrast: a nose that cancels a harmful joint-angle input
echo; echo "##### SWEEP COMPLETE #####"
