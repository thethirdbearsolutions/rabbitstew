#!/bin/bash
# Pull every completed arm's lineage.jsonl and config.json into runs/RBT-59/data/.
# Not committed: byte-identical copies of files on the branches named here.
set -e; cd "$(git rev-parse --show-toplevel)"
pull() { local branch=$1 runpath=$2 label=$3
  mkdir -p "runs/RBT-59/data/$label"
  git show "$branch:$runpath/lineage.jsonl" > "runs/RBT-59/data/$label/lineage.jsonl"
  git show "$branch:$runpath/config.json"  > "runs/RBT-59/data/$label/config.json"
  git show "$branch:$runpath/history.json" > "runs/RBT-59/data/$label/history.json" 2>/dev/null || true
  echo "$label"; }
B=origin
pull $B/results/RBT-13                            runs/RBT-13/W1-801           RBT-13
pull $B/results/RBT-16                            runs/RBT-16/W4-801           RBT-16
pull $B/claude/wizardly-johnson-4c9hvn            runs/RBT-17/W5-801           RBT-17
pull $B/results/RBT-18                            runs/RBT-18/W6-801           RBT-18
pull $B/claude/rbt-20-mtqdsp                      runs/RBT-20/W3b-801          RBT-20
pull $B/results/RBT-21                            runs/RBT-21/W6b-801          RBT-21
pull $B/results/RBT-22                            runs/RBT-22/W1b-801          RBT-22
pull $B/claude/rbt-lowest-unclaimed-ticket-55orfd runs/RBT-23/W4b-801          RBT-23
pull $B/results/baseline-801                      runs/baseline-801/forage-801 baseline-801
pull $B/results/baseline-801                      runs/RBT-19/P-801            RBT-19
