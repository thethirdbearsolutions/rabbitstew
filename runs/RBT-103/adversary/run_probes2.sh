#!/usr/bin/env bash
# Second batch: seed-match the W4b world move (the committed pair used 9000+ at home, 7000+ moved).
set -u
cd "$(dirname "$0")/../../.."
H=runs/RBT-103/routed_populations.py
O=runs/RBT-103/adversary
W=docs/artifacts/RBT-23-W4b-801
G=90,190,290,390,490,550,590
until [ -f $O/.done ]; do sleep 10; done
r() { out=$1; shift; [ -s "$O/$out.txt" ] && grep -q '^ROW' "$O/$out.txt" && return; python3 $H "$@" > "$O/$out.txt" 2>"$O/$out.err"; }
r w4b-home-s7000  --run $W --gens $G --seed0 7000 --label w4b-own-world-s7000
r w4b-rbt90-s9000 --run $W --gens $G --config-from runs/RBT-90/forage-805 --seed0 9000 --label w4b-in-rbt90-world-s9000
r w4b-in-p801-world --run $W --gens $G --config-from runs/RBT-19/P-801 --label w4b-in-p801-world
echo ALLDONE > $O/.done2
