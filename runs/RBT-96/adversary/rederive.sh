#!/usr/bin/env bash
# RBT-96 adversary, item 5: --from-summaries re-derivability in a worktree that never held the bulk,
# then four single-cell perturbations, each of which must move the readout (else it is a replay).
#   runs/RBT-96/adversary/rederive.sh [COMMIT]      (default: the author's head, 3f7ccec)
set -euo pipefail
COMMIT=${1:-3f7ccec}
REPO=$(git rev-parse --show-toplevel)
WT=$(mktemp -d)/wt
git -C "$REPO" worktree add -q --detach "$WT" "$COMMIT"
trap 'git -C "$REPO" worktree remove --force "$WT"' EXIT
cd "$WT"
R=runs/RBT-96
echo "worktree $WT at $(git rev-parse --short HEAD); bulk present: $(ls $R/s1-201/history.json $R/s1-201/lineage.jsonl 2>/dev/null | wc -l) files"
python "$R/readout.py" "$R" --from-summaries > /tmp/rbt96-clean.txt
cmp /tmp/rbt96-clean.txt "$R/readout-from-summaries.txt" && echo "clean: byte-identical to the committed readout-from-summaries.txt"

perturb() {  # LABEL FILE PYTHON-EDIT
  local label=$1 file=$2 edit=$3
  cp "$file" /tmp/rbt96-orig
  python - "$file" <<EOF
import sys; p = sys.argv[1]; s = open(p).read()
$edit
open(p, "w").write(s)
EOF
  python "$R/readout.py" "$R" --from-summaries > /tmp/rbt96-pert.txt 2>&1 || true
  echo "--- perturbation: $label   ($(diff /tmp/rbt96-clean.txt /tmp/rbt96-pert.txt | grep -c '^>') readout lines changed)"
  diff /tmp/rbt96-clean.txt /tmp/rbt96-pert.txt | grep '^>' | head -6 | cut -c1-200 || true
  cp /tmp/rbt96-orig "$file"
}

# 1. one final-fifth checkpoint cell: s1-201 generation 245 champ_holistic_mean + 0.11
perturb "s1-201 gen 245 champ_holistic_mean +0.11" $R/s1-201/generations.txt '
lines = s.split("\n")
for i, l in enumerate(lines):
    f = l.split("\t")
    if f[0] == "245":
        f[13] = f"{float(f[13]) + 0.11:.6f}"; lines[i] = "\t".join(f)
s = "\n".join(lines)'
# 2. one pairing hash: s1-203's conventional digest, first hex digit changed
perturb "s1-203 conventional sha256 one digit" $R/s1-203/conventional-digest.txt '
a, b = s.split("\t", 1); s = a + "\t" + ("0" if b[0] != "0" else "1") + b[1:]'
# 3. the covariate: s0-204 opponent approach -> -5.0
perturb "s0-204 opponent approach -> -5.0" $R/s0-204/opponent.txt '
h, v = s.strip().split("\n"); v = v.split("\t"); v[1] = "-5.000000"; s = h + "\n" + "\t".join(v) + "\n"'
# 4. one terrain seed: s1-202 generation 100
perturb "s1-202 gen 100 terrain_seed + 1" $R/s1-202/generations.txt '
lines = s.split("\n")
for i, l in enumerate(lines):
    f = l.split("\t")
    if f[0] == "100":
        f[1] = str(int(f[1]) + 1); lines[i] = "\t".join(f)
s = "\n".join(lines)'
