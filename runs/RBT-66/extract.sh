#!/bin/bash
# Pull the three champions the taxonomy names into runs/RBT-66/data/ (not committed:
# byte-identical copies of files already in the repo on the branches named below).
set -e
cd "$(git rev-parse --show-toplevel)"
pull() {  # branch runpath label kind gen...
  local branch=$1 runpath=$2 label=$3 kind=$4; shift 4
  local dest="runs/RBT-66/data/$label"
  mkdir -p "$dest/$kind"
  git show "$branch:$runpath/config.json" > "$dest/config.json"
  for g in "$@"; do
    git show "$branch:$runpath/$kind/best_gen$(printf %04d "$g").json" > "$dest/$kind/best_gen$(printf %04d "$g").json"
  done
  echo "$label/$kind: $# champion(s)"
}
B=origin
# the brake
pull $B/results/baseline-801 runs/baseline-801/forage-801 baseline-801 conventional 500
# the throttle (gen 300 is the one that survives 64 paired seeds; 590 evaporated -- both pulled)
pull $B/claude/new-session-4cao7d runs/RBT-19/P-801 RBT-19 conventional 300 590
# the sweep modulator -- NOT in runs/RBT-38/extract.sh; located on RBT-10's own delegate branch
pull $B/claude/determined-shannon-2zb8jp runs/RBT-10/forage-w0.0-802 RBT-10-802free conventional 590
echo "done: runs/RBT-66/data"
