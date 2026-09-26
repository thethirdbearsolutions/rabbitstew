#!/bin/bash
# Resume probe C's two runs from state.json with two workers each (workers do not change a run; RBT-90
# coordinator ruling), after the shared-baseline re-runs freed the cores.
set -e
D=runs/RBT-92/data
python -m rabbitstew.cli ecology --resume --out $D/probe-plain-9902 --workers 2 >> $D/probe-plain-9902/run.log 2>&1 &
python -m rabbitstew.cli ecology --resume --out $D/probe-shift-9902 --workers 2 >> $D/probe-shift-9902/run.log 2>&1 &
wait
echo done
