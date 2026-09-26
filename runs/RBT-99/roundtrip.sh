#!/bin/bash
# RBT-99 round trip: from a clean worktree of a commit (no bulk), readout.sh and score.py must reproduce the
# committed readout.txt and score.txt byte for byte; then one cell is perturbed (shift-3/seasons.txt, season 450,
# holistic mean_lifetime_score + 0.5) and the lines that move are printed.
#   runs/RBT-99/roundtrip.sh COMMIT > runs/RBT-99/roundtrip.txt
set -e
C=${1:-HEAD}
W=$(mktemp -d)/rt
git worktree prune
git worktree add -f "$W" "$C" > /dev/null 2>&1
trap 'git worktree remove --force "$W"' EXIT
cd "$W"
echo "worktree of $(git rev-parse --short HEAD); bulk present: $(ls runs/RBT-99/shift-801 | grep -c -E 'jsonl|history.json') files"
PYTHONPATH="$W" runs/RBT-99/readout.sh > /tmp/rt_readout.txt 2>&1
PYTHONPATH="$W" python runs/RBT-99/score.py > /tmp/rt_score.txt
cmp -s /tmp/rt_readout.txt runs/RBT-99/readout.txt && echo "readout.txt: byte-identical" || { echo "readout.txt: DIFFERS"; diff /tmp/rt_readout.txt runs/RBT-99/readout.txt | head; }
cmp -s /tmp/rt_score.txt runs/RBT-99/score.txt && echo "score.txt: byte-identical" || { echo "score.txt: DIFFERS"; diff /tmp/rt_score.txt runs/RBT-99/score.txt | head; }
python - <<'PY'
p = "runs/RBT-99/shift-3/seasons.txt"
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
PYTHONPATH="$W" runs/RBT-99/readout.sh > /tmp/rt_readout_p.txt 2>&1
echo "lines of readout.txt that move under the perturbation: $(diff /tmp/rt_readout.txt /tmp/rt_readout_p.txt | grep -c '^>')"
diff /tmp/rt_readout.txt /tmp/rt_readout_p.txt | grep -E '^[<>] +(r =|      3  352   shift|  R-body recovery|  mean   shift   recovery|  3: holistic)' | cut -c1-160
