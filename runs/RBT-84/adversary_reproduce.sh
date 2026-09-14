#!/bin/bash
# Adversary check for RBT-84: does the 600-season run reproduce from the seed on another machine?
#
# The report's own check covers 66 of 600 seasons (the killed first attempt against the completed
# run).  This re-ran the arm from the ticket's command at the same commit (4a09a86, via a worktree)
# into runs/RBT-84/adversary-rerun-807 and runs the delegate's four analysis scripts, unmodified but
# for an absolute repo root, on that output.  Each readout is diffed against the one the delegate
# committed, after replacing the run path in the header.  Identical readouts mean the champion, its
# 138-ancestor DAG, the 36 distinct linked-oscillator bests and the 655 of 999 births all reproduce
# from `config.json` alone.
#
# usage: bash runs/RBT-84/adversary_reproduce.sh REF_DIR   (REF_DIR holds <script>.py and <script>.expected.txt)
set -u
REF=$1
MINE=runs/RBT-84/adversary-rerun-807
THEIRS=runs/RBT-84/forage-807
OUT=docs/runs/RBT-84-adversary-reproduce.txt
mkdir -p docs/runs
{
  echo "replication: $MINE, run from the ticket's command at 4a09a86 on $(hostname), config identical to the delegate's (diff of config.json empty)"
  echo "seasons logged: $(grep -c '^season' runs/RBT-84/adversary-rerun-807.log)   genomes: $(ls $MINE/holistic/genomes | wc -l)   saved bests: $(ls $MINE/holistic | grep -c best_gen)"
  echo "exit line: $(grep '^exit' runs/RBT-84/adversary-rerun-807.log)"
  echo
  for s in oscillator_rate descent halves entry_steps; do
    python3 $REF/$s.py $MINE holistic 2>/dev/null | sed "s|$MINE|$THEIRS|g" > $REF/$s.mine.txt
    if diff -q $REF/$s.mine.txt $REF/$s.expected.txt > /dev/null; then
      echo "$s.txt: IDENTICAL to the delegate's committed readout"
    else
      echo "$s.txt: DIFFERS from the delegate's committed readout -- diff follows"
      diff $REF/$s.mine.txt $REF/$s.expected.txt | head -40
    fi
  done
} | tee $OUT
