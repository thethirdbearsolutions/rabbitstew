#!/bin/bash
# The three champions the taxonomy names, at n=64 paired seeds each.
set -e
cd "$(git rev-parse --show-toplevel)"
D=runs/RBT-66/data
run() { python runs/RBT-66/axis_lesion.py champion "$1" conventional "$2" 64 > "docs/artifacts/RBT-66-$3.txt" 2>&1; echo "done $3"; }
run $D/baseline-801   500 brake        &
run $D/RBT-19         300 throttle     &
run $D/RBT-10-802free 590 sweep        &
run $D/RBT-19         590 throttle590  &
wait
echo "all champions done"
