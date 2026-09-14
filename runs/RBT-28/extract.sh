#!/bin/bash
# Pull every champion RBT-28 autopsies out of the branch that holds it, into runs/RBT-28/data/.
# The extracted genotypes are NOT committed: they are byte-identical copies of files already in the
# repo on the branches named below, and this script regenerates them exactly.  Same pattern as
# runs/RBT-38/extract.sh, which is where it came from.  Needs the branches fetched.
set -e
cd "$(git rev-parse --show-toplevel)"

pull() {  # branch runpath label kind gen...
  local branch=$1 runpath=$2 label=$3 kind=$4; shift 4
  local dest="runs/RBT-28/data/$label"
  mkdir -p "$dest/$kind"
  git show "$branch:$runpath/config.json" > "$dest/config.json"
  for g in "$@"; do
    git show "$branch:$runpath/$kind/best_gen$(printf %04d "$g").json" > "$dest/$kind/best_gen$(printf %04d "$g").json"
  done
  echo "$label/$kind: $# champion(s)"
}

B=origin
# The four inert-nose mowers the ticket names.
pull $B/results/RBT-13                 runs/RBT-13/W1-801           RBT-13       holistic 390
pull $B/results/RBT-16                 runs/RBT-16/W4-801           RBT-16       holistic 590
pull $B/claude/wizardly-johnson-4c9hvn runs/RBT-17/W5-801           RBT-17       holistic 590
pull $B/results/RBT-22                 runs/RBT-22/W1b-801          RBT-22       holistic 590
# The optional contrast: the one nose in the family known to do real work for a non-smelling
# reason (it cancels a harmful joint-angle input).  The ticket points at
# runs/RBT-10/check-801/forage-w0.03-801, which holds only gens 0 and 10 -- it is a short
# replication check, not a 600-season run.  The season-300 lump docs/foraging-world.md describes
# is the baseline dense arm's, so that is what is pulled.
pull $B/results/baseline-801           runs/baseline-801/forage-801 baseline-801 holistic 300
echo "done: runs/RBT-28/data"
# The Pioneer of the same arm and season, for the items-per-kJ contrast RBT-28's Q3 asks about.
pull $B/results/RBT-13 runs/RBT-13/W1-801 RBT-13 conventional 390
