#!/bin/bash
# RBT-39: every items-per-metre claim in the family, re-read against its own gait's expectation.
# Champions come from runs/RBT-38/extract.sh (plus RBT-22's holistic g590 and RBT-19's own run dir).
D=runs/RBT-38/data
N=${1:-16}; DRAWS=${2:-200}
run() { echo; echo "##### $1 $2 g$3 #####"; python3 runs/RBT-39/trajectory_null.py "$1" "$2" "$3" "$N" "$DRAWS" 2>&1 | grep -v WARNING; }
run $D/RBT-13       conventional 590   # the load-bearing claim: 0.276 items/m against 0.297
run $D/RBT-13       holistic     390   # the mower with a nose it never reads
run $D/RBT-17       conventional 590   # brake, survives RBT-38 at 35%
run $D/RBT-17       conventional 500
run $D/baseline-801 conventional 500   # the baseline's brake, survives RBT-38 at 83%
run $D/RBT-22       conventional 300   # 0.247, below the floor; effect died at 64 paired seeds
run $D/RBT-22       holistic     590   # noseless, "clears the floor at 0.48-0.52 on body width alone"
run $D/RBT-16       conventional 590   # ce861, the strongest effect in the family; RBT-58's subject
run runs/RBT-19/P-801 conventional 590 # the persistent world's nose-dependent Pioneer
run runs/RBT-19/P-801 holistic     590 # the persistent world's blind forager, paper 5's subject
echo; echo "##### SWEEP COMPLETE #####"
