#!/bin/bash
# RBT-100 round trip (RBT-99's roundtrip.sh, C3's files): from a clean worktree of a commit (no bulk), readout.py,
# placebo.py and score.py must reproduce the committed readout.txt, placebo.txt and score.txt byte for byte; then one
# cell is perturbed (shift-3/seasons.txt, season 450, holistic mean_lifetime_score + 0.5) and the lines that move are
# counted and the key ones printed.
#   runs/RBT-100/roundtrip.sh COMMIT > runs/RBT-100/roundtrip.txt
set -e
C=${1:-HEAD}
W=$(mktemp -d)/rt
O=$(mktemp -d)
git worktree prune
git worktree add -f "$W" "$C" > /dev/null 2>&1
trap 'git worktree remove --force "$W"; rm -rf "$O"' EXIT
cd "$W"
echo "worktree of $(git rev-parse --short HEAD); bulk files present under runs/RBT-100 and runs/RBT-90: $(find runs/RBT-100 runs/RBT-90 -name 'lineage.jsonl' -o -name 'history.json' | wc -l)"
PYTHONPATH="$W" python runs/RBT-100/readout.py > "$O/readout.txt" 2>&1
PYTHONPATH="$W" python runs/RBT-100/placebo.py > "$O/placebo.txt"
PYTHONPATH="$W" python runs/RBT-100/score.py > "$O/score.txt"
for f in readout placebo score; do
  cmp -s "$O/$f.txt" "runs/RBT-100/$f.txt" && echo "$f.txt: byte-identical" || { echo "$f.txt: DIFFERS"; diff "$O/$f.txt" "runs/RBT-100/$f.txt" | head; }
done
python - <<'PY'
p = "runs/RBT-100/shift-3/seasons.txt"
L = open(p).read().split("\n")
i = L[0].split("\t").index("mean_lifetime_score")
for j, l in enumerate(L):
    f = l.split("\t")
    if len(f) > i and f[0] == "450" and f[1] == "holistic":
        print(f"perturbed {p} season 450 holistic mean_lifetime_score {f[i]} -> {float(f[i]) + 0.5}")
        f[i] = repr(float(f[i]) + 0.5)
        L[j] = "\t".join(f)
open(p, "w").write("\n".join(L))
PY
PYTHONPATH="$W" python runs/RBT-100/readout.py > "$O/readout_p.txt" 2>&1
PYTHONPATH="$W" python runs/RBT-100/score.py > "$O/score_p.txt"
echo "lines of readout.txt that move under the perturbation: $(diff "$O/readout.txt" "$O/readout_p.txt" | grep -c '^>')"
echo "lines of score.txt that move under the perturbation: $(diff "$O/score.txt" "$O/score_p.txt" | grep -c '^>')"
diff "$O/readout.txt" "$O/readout_p.txt" | grep -E '^[<>] +(r =|      3  352   shift|  R-body recovery|  mean   shift   recovery)' | cut -c1-160
git checkout -q -- runs/RBT-100/shift-3/seasons.txt
