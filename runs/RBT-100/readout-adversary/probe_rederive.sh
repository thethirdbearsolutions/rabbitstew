#!/bin/bash
# RBT-100 readout adversary: round trip and perturbations, each in its own fresh worktree of COMMIT (no bulk).
#   0  readout.py, placebo.py, score.py reproduce readout.txt, placebo.txt, score.txt byte for byte; plus an open()
#      audit of every file each script reads (which arms, which seeds, any ckpt or bulk)
#   1  base own table (base-3/own.txt, season T-10, conventional food + 1.0): the arithmetic must move, only seed 3
#   2  founders6 (founders6-7/seasons.txt, season 59, holistic alive 8 -> 12): FOUNDERS and the qualifier must move
#   3  C3's cull (cull-805/seasons.txt, season T+100, holistic mean_lifetime_score + 0.5): R-cull / R-null only
#   4  the baseline (RBT-90/forage-806/seasons.txt, season T+100, conventional + 0.5): base lines and the arithmetic
#   5  the shift own table (shift-806/own.txt, recovery rows, conventional net_all_ub + 0.3): OWN lines only
#   6  founders6-4/ deleted: printed or silent?
#   runs/RBT-100/readout-adversary/probe_rederive.sh COMMIT > runs/RBT-100/readout-adversary/probe_rederive.txt
set -u
C=${1:-HEAD}
REPO=$(git rev-parse --show-toplevel)
O=$(mktemp -d)
fresh() {  # a fresh worktree of $C at $1
  git -C "$REPO" worktree add -f "$1" "$C" > /dev/null 2>&1
}
drop() { git -C "$REPO" worktree remove --force "$1"; }
run3() {  # $1 worktree, $2 tag
  (cd "$1" && PYTHONPATH="$1" python runs/RBT-100/readout.py > "$O/readout_$2.txt" 2>&1; echo "readout exit $?" > "$O/exit_$2";
   PYTHONPATH="$1" python runs/RBT-100/placebo.py > "$O/placebo_$2.txt" 2>&1; echo "placebo exit $?" >> "$O/exit_$2";
   PYTHONPATH="$1" python runs/RBT-100/score.py > "$O/score_$2.txt" 2>&1; echo "score exit $?" >> "$O/exit_$2")
}
moved() {  # $1 tag
  for f in readout placebo score; do
    n=$(diff "$O/${f}_0.txt" "$O/${f}_$1.txt" | grep -c '^>')
    echo "   $f.txt: $n lines move; $(tr '\n' ' ' < "$O/exit_$1" | grep -o "$f exit [0-9]*")"
    diff "$O/${f}_0.txt" "$O/${f}_$1.txt" | grep '^[<>]' | cut -c1-200 | head -${2:-6} | sed 's/^/      /'
  done
}
echo "RBT-100 readout adversary: round trip of $(git -C "$REPO" rev-parse --short "$C") and six perturbations, each in a fresh worktree"
W=$(mktemp -d)/w0; W0=$W; fresh "$W"
cd "$W"
echo "0  worktree $(git rev-parse --short HEAD): untracked/ignored files $(git status --porcelain --ignored | wc -l); bulk-shaped files under runs/RBT-100, RBT-92, RBT-90: $(find runs/RBT-100 runs/RBT-92 runs/RBT-90 \( -name lineage.jsonl -o -name history.json -o -name 'cohorts.jsonl' -o -name '*.traj' -o -name analysis.json \) | wc -l)"
run3 "$W" 0
for f in readout placebo score; do
  cmp -s "$O/${f}_0.txt" "runs/RBT-100/$f.txt" && echo "   $f.txt: byte-identical (sha256 $(sha256sum < "$O/${f}_0.txt" | cut -c1-12))" || { echo "   $f.txt: DIFFERS"; diff "$O/${f}_0.txt" "runs/RBT-100/$f.txt" | head; }
done
cat "$O/exit_0" | sed 's/^/   /'
echo "   open() audit: files read under runs/, by script (arm directories grouped)"
for s in readout placebo score; do
  PYTHONPATH="$W" python - "$s" <<'PY'
import collections, os, re, runpy, sys, io, contextlib
name = sys.argv[1]
seen = []
def hook(ev, args):
    if ev == "open" and isinstance(args[0], str):
        seen.append(os.path.relpath(os.path.abspath(args[0]), os.getcwd()))
sys.addaudithook(hook)
sys.argv = [f"runs/RBT-100/{name}.py"]
code = 0
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    try:
        runpy.run_path(f"runs/RBT-100/{name}.py", run_name="__main__")
    except SystemExit as e:
        code = e.code
runs = sorted({p for p in seen if p.startswith("runs/")})
by = collections.defaultdict(set)
for p in runs:
    m = re.match(r"runs/(RBT-\d+)/([a-z0-9]+?)-?(\d+)?/(.+)$", p)
    if m and m.group(3):
        by[(m.group(1), m.group(2))].add(m.group(3))
    else:
        by[("file", p)].add("")
print(f"   {name}.py (exit {code}):")
for (a, b), seeds in sorted(by.items()):
    if a == "file":
        print(f"      {b}")
    else:
        print(f"      runs/{a}/{b}-SEED: {len(seeds)} seeds {sorted(seeds, key=int)}")
bad = [p for p in runs if "ckpt" in p or p.endswith(("lineage.jsonl", "history.json", ".traj"))]
print(f"      ckpt or bulk paths opened: {len(bad)}")
PY
done

pert() {  # $1 tag, $2 description, $3 python edit (run in the worktree)
  W=$(mktemp -d)/w$1; fresh "$W"; cd "$W"
  echo "$1  $2"
  python -c "$3" | sed 's/^/   /'
  run3 "$W" "$1"; moved "$1" "${4:-6}"
  cd "$REPO"; drop "$W"
}
EDIT='
import sys
def edit(p, season, pop, col, fn):
    L = open(p).read().split("\n"); h = L[0].split("\t"); i = h.index(col); n = 0
    for j, l in enumerate(L):
        f = l.split("\t")
        if len(f) > i and f[0].isdigit() and int(f[0]) in season and f[1] == pop:
            old = f[i]; f[i] = fn(f[i]); L[j] = "\t".join(f); n += 1
    open(p, "w").write("\n".join(L)); print(f"edited {p}: {n} cell(s) of {col} ({pop}), e.g. {old} -> {fn(old)}")
T = {int(l.split()[0]): int(l.split()[1]) for l in open("runs/RBT-92/onset.txt") if l.split() and l.split()[0].isdigit() and len(l.split()) > 1 and l.split()[1].isdigit()}
'
cd "$REPO"
pert 1 "base-3/own.txt, season T-10, conventional food + 1.0 (pre-onset: feeds the arithmetic)" "$EDIT
edit('runs/RBT-100/base-3/own.txt', {T[3]-10}, 'conventional', 'food', lambda v: repr(float(v) + 1.0))" 8
pert 2 "founders6-7/seasons.txt, season 59, holistic alive 8 -> 12" "$EDIT
edit('runs/RBT-100/founders6-7/seasons.txt', {59}, 'holistic', 'alive', lambda v: '12')" 8
pert 3 "cull-805/seasons.txt, season T+100, holistic mean_lifetime_score + 0.5" "$EDIT
edit('runs/RBT-100/cull-805/seasons.txt', {T[805]+100}, 'holistic', 'mean_lifetime_score', lambda v: repr(float(v) + 0.5))" 6
pert 4 "RBT-90/forage-806/seasons.txt, season T+100, conventional mean_lifetime_score + 0.5" "$EDIT
edit('runs/RBT-90/forage-806/seasons.txt', {T[806]+100}, 'conventional', 'mean_lifetime_score', lambda v: repr(float(v) + 0.5))" 6
pert 5 "shift-806/own.txt, recovery rows [T+60, T+160), conventional net_all_ub + 0.3" "$EDIT
edit('runs/RBT-100/shift-806/own.txt', set(range(T[806]+60, T[806]+160)), 'conventional', 'net_all_ub', lambda v: v if v == '-' else repr(float(v) + 0.3))" 6
pert 6 "founders6-4/ deleted" "import shutil; shutil.rmtree('runs/RBT-100/founders6-4'); print('deleted runs/RBT-100/founders6-4')" 8
drop "$W0"; git -C "$REPO" worktree prune; rm -rf "$O"
