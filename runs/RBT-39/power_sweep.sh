#!/bin/bash
# RBT-39, after the adversary: the MEASURED detection threshold on every champion, in whole items.
# Replaces the extrapolated "~7% of the crop" in the report's §6. Run runs/RBT-38/extract.sh first.
D=runs/RBT-38/data
N=${1:-16}; DRAWS=${2:-200}; MAXK=${3:-6}
run() { echo; echo "##### $1 $2 g$3 #####"; python3 runs/RBT-39/power_ladder.py "$1" "$2" "$3" "$N" "$DRAWS" "$MAXK" 2>&1 | grep -v WARNING; }
run $D/RBT-13       conventional 590
run $D/RBT-13       holistic     390
run $D/RBT-17       conventional 590
run $D/RBT-17       conventional 500
run $D/baseline-801 conventional 500
run $D/RBT-22       conventional 300
run $D/RBT-22       holistic     590
run $D/RBT-16       conventional 590
run runs/RBT-19/P-801 conventional 590
run runs/RBT-19/P-801 holistic     590
echo; echo "##### POWER SWEEP COMPLETE #####"
