#!/bin/bash
# RBT-101 readout adversary: round trip and perturbations of my own choosing, each in its own fresh worktree of COMMIT
# (default HEAD of the designer's branch, 880ce66), which holds no bulk.  The designer's files are never edited in the
# main checkout; every perturbation is made inside a throwaway worktree.
#   runs/RBT-101/readout-adversary/probe_rederive.sh [COMMIT] > runs/RBT-101/readout-adversary/probe_rederive.txt
set -e
C=${1:-880ce66}
ROOT=$(git rev-parse --show-toplevel)
TMP=$(mktemp -d)
fresh() {  # a new worktree of $C at $TMP/$1, printed with its bulk count
  git -C "$ROOT" worktree add -f "$TMP/$1" "$C" > /dev/null 2>&1
  echo "  worktree $1 of $(git -C "$TMP/$1" rev-parse --short HEAD): untracked+ignored files $(git -C "$TMP/$1" status --porcelain --ignored | wc -l); bulk-shaped files under runs/RBT-101 runs/RBT-92 runs/RBT-90: $(find "$TMP/$1/runs/RBT-101" "$TMP/$1/runs/RBT-92" "$TMP/$1/runs/RBT-90" \( -name lineage.jsonl -o -name history.json -o -name state.json -o -name cohorts.jsonl \) | wc -l)"
}
run_all() {  # the four readouts, into $2
  ( cd "$1" && PYTHONPATH="$1" runs/RBT-101/readout.sh > "$2/readout.txt" 2>&1; echo "readout.sh exit $?" > "$2/exit.txt"
    PYTHONPATH="$1" python runs/RBT-101/rewire.py > "$2/rewire.txt" 2>&1; echo "rewire.py exit $?" >> "$2/exit.txt"
    PYTHONPATH="$1" python runs/RBT-101/placebo.py > "$2/placebo.txt" 2>&1; echo "placebo.py exit $?" >> "$2/exit.txt"
    PYTHONPATH="$1" python runs/RBT-101/arith.py > "$2/arith.txt" 2>&1; echo "arith.py exit $?" >> "$2/exit.txt" ) || true
}
moved() {  # lines of each readout that move between $1 and $2
  for f in readout rewire placebo arith; do
    echo "    $f.txt: $(diff "$1/$f.txt" "$2/$f.txt" | grep -c '^>') lines move"
  done
}
trap 'for d in $TMP/*/; do git -C "$ROOT" worktree remove --force "$d" > /dev/null 2>&1 || true; done' EXIT

echo "0 ROUND TRIP (fresh worktree, no bulk)"
fresh rt
mkdir -p "$TMP/o0"; run_all "$TMP/rt" "$TMP/o0"; sed 's/^/    /' "$TMP/o0/exit.txt"
for f in readout rewire placebo arith; do
  cmp -s "$TMP/o0/$f.txt" "$TMP/rt/runs/RBT-101/$f.txt" && echo "    $f.txt byte-identical, sha256 $(sha256sum < "$TMP/o0/$f.txt" | cut -c1-12)" || echo "    $f.txt DIFFERS"
done

echo
echo "1 A BASELINE CELL (not the designer's): runs/RBT-90/forage-805/seasons.txt, season 420 (T+61), conventional mean_lifetime_score + 1.0"
fresh p1
python - "$TMP/p1/runs/RBT-90/forage-805/seasons.txt" <<'PY'
import sys
p = sys.argv[1]; L = open(p).read().split("\n"); h = L[0].split("\t"); i = h.index("mean_lifetime_score")
for j, l in enumerate(L):
    f = l.split("\t")
    if len(f) > i and f[0] == "420" and f[1] == "conventional":
        print(f"    {f[i]} -> {float(f[i]) + 1.0}"); f[i] = repr(float(f[i]) + 1.0); L[j] = "\t".join(f)
open(p, "w").write("\n".join(L))
PY
mkdir -p "$TMP/o1"; run_all "$TMP/p1" "$TMP/o1"; moved "$TMP/o0" "$TMP/o1"
diff "$TMP/o0/readout.txt" "$TMP/o1/readout.txt" | grep -E '^[<>] +(805  359    base|  mean    base   recovery|  R-shift  conventional recovery|  R-body recovery|  CLASS)' | cut -c1-150 | sed 's/^/    /'
diff "$TMP/o0/placebo.txt" "$TMP/o1/placebo.txt" | grep -E '^[<>] +(event - base|   base   recovery)' | cut -c1-130 | sed 's/^/    /'
diff "$TMP/o0/arith.txt" "$TMP/o1/arith.txt" | grep -E '^[<>] (paired: residual|designed: observed R-shift)' | cut -c1-130 | sed 's/^/    /'

echo
echo "2 A WIRING CELL THAT REACHES THE SCORED STATISTIC: runs/RBT-101/shift-1/wiring.txt, the first designed individual alive at"
echo "  T+160 that is not already a new_existing hit, g1 -> its largest C0 ancestor's g1 + 5 (a new direct posture link)"
fresh p2
( cd "$TMP/p2" && python - <<'PY'
import sys
sys.path.insert(0, "runs/RBT-92")
import readout as R
T = R.onsets()[1]
a = R.Arm("runs/RBT-101/shift-1")
p = "runs/RBT-101/shift-1/wiring.txt"
L = open(p).read().split("\n"); h = L[0].split("\t")
rows = {(l.split("\t")[0], l.split("\t")[1]): l.split("\t") for l in L[1:] if l}
c0 = a.alive_at("conventional", T - 1)
for name in sorted(a.alive_at("conventional", T + 160)):
    anc = a.anc0("conventional", name, c0)
    f = rows[("conventional", name)]
    mx = max(float(rows[("conventional", x)][h.index("g1")]) for x in anc)
    if float(f[h.index("g1")]) < mx + 0.5:
        print(f"    conventional {name}: g1 {f[h.index('g1')]} -> {mx + 5:.6f} (largest C0-ancestor g1 {mx:.6f})")
        f[h.index("g1")] = f"{mx + 5:.6f}"
        break
open(p, "w").write("\n".join([L[0]] + ["\t".join(rows[(l.split("\t")[0], l.split("\t")[1])]) for l in L[1:] if l]) + "\n")
PY
)
mkdir -p "$TMP/o2"; run_all "$TMP/p2" "$TMP/o2"; moved "$TMP/o0" "$TMP/o2"
diff "$TMP/o0/rewire.txt" "$TMP/o2/rewire.txt" | grep -E '^[<>] +(new_existing +shift - base|    1  base)' | head -4 | cut -c1-150 | sed 's/^/    /'

echo
echo "3 THE PROBE THE ARITHMETIC RESTS ON: runs/RBT-101/flat_probe.txt, seed 806 designed flat-random +0.891 -> +0.391"
fresh p3
sed -i 's/^\(806\tconventional.*flat-random \)+0\.891/\1+0.391/' "$TMP/p3/runs/RBT-101/flat_probe.txt"
grep -P '^806\tconventional' "$TMP/p3/runs/RBT-101/flat_probe.txt" | grep -o 'flat-random [^ ]*' | sed 's/^/    now /'
mkdir -p "$TMP/o3"; run_all "$TMP/p3" "$TMP/o3"; moved "$TMP/o0" "$TMP/o3"
diff "$TMP/o0/arith.txt" "$TMP/o3/arith.txt" | grep -E '^[<>] paired: residual' | cut -c1-130 | sed 's/^/    /'

echo
echo "4 A REMOVED ARM: runs/RBT-101/shift-805 deleted"
fresh p4
rm -rf "$TMP/p4/runs/RBT-101/shift-805"
mkdir -p "$TMP/o4"; run_all "$TMP/p4" "$TMP/o4"; sed 's/^/    /' "$TMP/o4/exit.txt"
grep -E 'seeds read|805: ' "$TMP/o4/readout.txt" | head -3 | cut -c1-140 | sed 's/^/    readout: /'
tail -1 "$TMP/o4/placebo.txt" | cut -c1-140 | sed 's/^/    placebo: /'
tail -1 "$TMP/o4/arith.txt" | cut -c1-140 | sed 's/^/    arith: /'

echo
echo "5 A SUBSTITUTED SEED: runs/RBT-101/shift-806/seasons.txt replaced by shift-807's"
fresh p5
cp "$TMP/p5/runs/RBT-101/shift-807/seasons.txt" "$TMP/p5/runs/RBT-101/shift-806/seasons.txt"
mkdir -p "$TMP/o5"; run_all "$TMP/p5" "$TMP/o5"; sed 's/^/    /' "$TMP/o5/exit.txt"
grep -E 'V0|806' "$TMP/o5/readout.txt" | grep -iE 'fail|differ|not read' | head -3 | cut -c1-160 | sed 's/^/    readout: /'
diff "$TMP/o0/placebo.txt" "$TMP/o5/placebo.txt" | grep -c '^>' | sed 's/^/    placebo.txt lines that move (it has no V0 of its own): /'
