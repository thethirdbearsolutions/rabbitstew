#!/bin/bash
# Pull one run's config and the champions named, from the branch that holds it, into runs/RBT-38/data/.
set -e
branch=$1; runpath=$2; label=$3; kind=$4; shift 4
dest="runs/RBT-38/data/$label"
mkdir -p "$dest/$kind"
git show "$branch:$runpath/config.json" > "$dest/config.json"
for g in "$@"; do
  git show "$branch:$runpath/$kind/best_gen$(printf %04d "$g").json" > "$dest/$kind/best_gen$(printf %04d "$g").json"
done
echo "$label: config + $# champion(s) of $kind"
