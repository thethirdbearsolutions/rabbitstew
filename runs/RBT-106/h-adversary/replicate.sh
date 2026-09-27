#!/bin/bash
# RBT-106 H readout adversary: what was run, from a scratch worktree of a7cf94c with rabbitstew/ checked out at
# c872e80 (tree 9cc84cde), a clean `pip install -e '.[dev]'` venv without scipy, x86_64, MuJoCo 3.14.0, numpy 2.4.6.
# BULK holds the 20 H arms restored by scripts/durable.sh restore from ckpt/rbt-106-ARM-SEED.  RE is a directory whose
# runs/RBT-106/ARM-SEED are symlinks to BULK and everything else symlinks to the worktree, so each script's ROOT (and
# the modules that chdir to it) sees runs/RBT-106/ARM-SEED as the bulk, exactly as postrun.sh did.
set -e
S=${S:?scratch}; P=$S/venv/bin/python; RE=$S/re; BULK=$S/bulk
SEEDS="801 4 804 805 806 807 1 2 3 7"
# founders (digests checked against founders-digests.txt)
for s in $SEEDS; do $P runs/RBT-106/founders.py $s 32 $S/founders-w32-$s; done
# attack 1: the design adversary's null_xover.py, unchanged, on each arm's OWN lineage.jsonl, 100 reps
for a in HP HU; do for s in $SEEDS; do
  $P runs/RBT-106/adversary/null_xover.py $BULK/$a-$s $s 32 $S/founders-w32-$s --reps 100 --procs 4 > runs/RBT-106/h-adversary/ownnull/ownnull-$a-$s.txt
done; done
python runs/RBT-106/h-adversary/ownnull_pool.py runs/RBT-106/h-adversary/ownnull > runs/RBT-106/h-adversary/ownnull_pool.txt
# attack 7: held.py at 300 and 599 on all 20 arms, and function readouts on HP-806 (F12-flagged), HP-4, HU-4
cd $RE
for a in HU HP; do for s in $SEEDS; do for ss in 300 599; do
  $P runs/RBT-106/held.py runs/RBT-106/$a-$s $s 32 --season $ss > $S/out/held/$a-$s-held-$ss.txt; done; done; done
for a in HP-806 HP-4; do $P $RE/runs/RBT-104/function.py --run runs/RBT-106/$a > $S/out/fn/$a-function-patchy.txt; done
$P $RE/runs/RBT-106/cross_world.py --world runs/RBT-106/world-patchy --run runs/RBT-106/HU-4 > $S/out/fn/HU-4-function-patchy.txt
# attack 2: split attribution on two flagged and two unflagged HP arms
for a in HP-806 HP-805 HP-4 HP-3; do $P $RE/runs/RBT-106/h-adversary/attrib.py --run runs/RBT-106/$a > $S/out/attrib/attrib-$a.txt; done
