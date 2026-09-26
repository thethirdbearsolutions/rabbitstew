#!/bin/bash
# RBT-101 round trip: from a clean worktree of a commit (no bulk), readout.sh, rewire.py, placebo.py and arith.py must
# reproduce the committed readout.txt, rewire.txt, placebo.txt and arith.txt byte for byte; then one cell is perturbed
# (shift-3/seasons.txt, season 450, holistic mean_lifetime_score + 0.5) and the lines of readout.txt that move are
# printed; and one wiring cell (shift-3/wiring.txt, the first holistic individual alive at T+160, g1 + 1.0) is perturbed
# and the lines of rewire.txt that move are counted.
#   runs/RBT-101/roundtrip.sh COMMIT > runs/RBT-101/roundtrip.txt
set -e
C=${1:-HEAD}
W=$(mktemp -d)/rt
git worktree prune
git worktree add -f "$W" "$C" > /dev/null 2>&1
trap 'git worktree remove --force "$W"' EXIT
cd "$W"
echo "worktree of $(git rev-parse --short HEAD); bulk present under runs/RBT-101 and runs/RBT-90: $(find runs/RBT-101 runs/RBT-90 -name 'lineage.jsonl' -o -name 'history.json' | wc -l) files"
O=$(mktemp -d)
PYTHONPATH="$W" runs/RBT-101/readout.sh > $O/readout.txt 2>&1
PYTHONPATH="$W" python runs/RBT-101/rewire.py > $O/rewire.txt
PYTHONPATH="$W" python runs/RBT-101/placebo.py > $O/placebo.txt
PYTHONPATH="$W" python runs/RBT-101/arith.py > $O/arith.txt
for f in readout rewire placebo arith; do
  cmp -s $O/$f.txt runs/RBT-101/$f.txt && echo "$f.txt: byte-identical" || { echo "$f.txt: DIFFERS"; diff $O/$f.txt runs/RBT-101/$f.txt | head; }
done
python - <<'PY'
p = "runs/RBT-101/shift-3/seasons.txt"
L = open(p).read().split("\n")
h = L[0].split("\t")
i = h.index("mean_lifetime_score")
for j, l in enumerate(L):
    f = l.split("\t")
    if len(f) > i and f[0] == "450" and f[1] == "holistic":
        print(f"perturbed {p} season 450 holistic mean_lifetime_score {f[i]} -> {float(f[i]) + 0.5}")
        f[i] = repr(float(f[i]) + 0.5)
        L[j] = "\t".join(f)
open(p, "w").write("\n".join(L))
PY
PYTHONPATH="$W" runs/RBT-101/readout.sh > $O/readout_p.txt 2>&1
echo "lines of readout.txt that move under the income perturbation: $(diff $O/readout.txt $O/readout_p.txt | grep -c '^>')"
diff $O/readout.txt $O/readout_p.txt | grep -E '^[<>] +(r =|      3  352   shift|  mean   shift   recovery|  R-body recovery)' | cut -c1-150
git checkout -q -- runs/RBT-101/shift-3/seasons.txt
python - <<'PY'
import sys
sys.path.insert(0, "runs/RBT-92")
import readout as R
a = R.Arm("runs/RBT-101/shift-3")
T = R.onsets()[3]
name = sorted(a.alive_at("holistic", T + 160))[0]
p = "runs/RBT-101/shift-3/wiring.txt"
L = open(p).read().split("\n")
h = L[0].split("\t")
i = h.index("g1")
for j, l in enumerate(L):
    f = l.split("\t")
    if len(f) > i and f[0] == "holistic" and f[1] == name:
        print(f"perturbed {p} holistic {name} (alive at T+160) g1 {f[i]} -> {float(f[i]) + 1.0}")
        f[i] = f"{float(f[i]) + 1.0:.6f}"
        L[j] = "\t".join(f)
open(p, "w").write("\n".join(L))
PY
PYTHONPATH="$W" python runs/RBT-101/rewire.py > $O/rewire_p.txt
echo "lines of rewire.txt that move under the wiring perturbation: $(diff $O/rewire.txt $O/rewire_p.txt | grep -c '^>')"
diff $O/rewire.txt $O/rewire_p.txt | grep -E '^[<>]' | head -6 | cut -c1-170
