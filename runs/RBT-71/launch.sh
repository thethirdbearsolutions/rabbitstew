#!/bin/bash
# RBT-71 Deliverable A: the forage-801 baseline (RBT-60's command) with ONE flag changed, the seed,
# plus the paired neutral control of the same world and seed.
#   usage: launch.sh SEED [neutral]
# Writes runs/RBT-71/forage-SEED (or neutral-SEED) and a .log beside it.
#
# Code version. Every run in this package executes the package at integration head f3aa69d.
# forage-804, neutral-804 and forage-805 ran the editable install while the working tree was at
# f3aa69d (their processes, and their forked workers, started before the tree moved to 64e5004 at
# 04:29:27 UTC on 2026-09-14). The tree then merged PR #12 (RBT-27/30), which changes the economy
# (an exploded body forfeits its season), so the remaining runs are pinned to a worktree checked out
# at f3aa69d through PYTHONPATH rather than allowed to pick up whatever the tree holds. Set CODE to
# that worktree; empty CODE runs the installed package.
cd "$(git rev-parse --show-toplevel)"
seed=$1; kind=${2:-forage}
extra=""; [ "$kind" = "neutral" ] && extra="--neutral"
out=runs/RBT-71/$kind-$seed
CODE=${CODE-/tmp/claude-0/-home-user-rabbitstew/6bff9532-bc79-571b-a3ff-e00c4a4b3616/scratchpad/rbt71-f3aa69d}
if [ -n "$CODE" ]; then
  export PYTHONPATH=$CODE
  echo "code: $(git -C $CODE rev-parse HEAD) via PYTHONPATH=$CODE" > $out.code.txt
else
  echo "code: installed package, tree at $(git rev-parse HEAD)" > $out.code.txt
fi
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --max-age 60 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random \
  --random-start --score food --seed $seed $extra --out $out > $out.log 2>&1
