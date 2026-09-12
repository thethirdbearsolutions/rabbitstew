#!/bin/bash
# Pull every champion RBT-38 re-reads out of the branch that holds it, into runs/RBT-38/data/.
# The extracted genotypes are NOT committed: they are byte-identical copies of files already in
# the repo on the branches named below, and this script regenerates them exactly. Run it before
# sweep.sh. Needs the listed branches fetched (git fetch origin <branch>).
set -e
cd "$(git rev-parse --show-toplevel)"

pull() {  # branch runpath label kind gen...
  local branch=$1 runpath=$2 label=$3 kind=$4; shift 4
  local dest="runs/RBT-38/data/$label"
  mkdir -p "$dest/$kind"
  git show "$branch:$runpath/config.json" > "$dest/config.json"
  for g in "$@"; do
    git show "$branch:$runpath/$kind/best_gen$(printf %04d "$g").json" > "$dest/$kind/best_gen$(printf %04d "$g").json"
  done
  echo "$label/$kind: $# champion(s)"
}

B=origin
pull $B/results/RBT-21                            runs/RBT-21/W6b-801        RBT-21       conventional 0 10
pull $B/results/RBT-13                            runs/RBT-13/W1-801         RBT-13       conventional 590
pull $B/results/RBT-13                            runs/RBT-13/W1-801         RBT-13       holistic     390
pull $B/claude/wizardly-johnson-4c9hvn            runs/RBT-17/W5-801         RBT-17       conventional 500 590
pull $B/results/RBT-18                            runs/RBT-18/W6-801         RBT-18       conventional 0
pull $B/claude/rbt-20-mtqdsp                      runs/RBT-20/W3b-801        RBT-20       conventional 0
pull $B/results/baseline-801                      runs/baseline-801/forage-801 baseline-801 conventional 20 30 500
pull $B/results/RBT-16                            runs/RBT-16/W4-801         RBT-16       conventional 100 590
pull $B/claude/rbt-lowest-unclaimed-ticket-55orfd runs/RBT-23/W4b-801        RBT-23       conventional 590
pull $B/results/RBT-22                            runs/RBT-22/W1b-801        RBT-22       conventional 300
echo "done: runs/RBT-38/data"
