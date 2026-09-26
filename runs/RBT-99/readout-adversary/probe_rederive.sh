#!/usr/bin/env bash
# RBT-99 readout adversary: the round trip of readout.sh and score.py from a worktree that never held bulk
# (runs/README.md), and perturbations of committed cells of every input kind, each in a fresh worktree.
#   bash runs/RBT-99/readout-adversary/probe_rederive.sh [REV] > runs/RBT-99/readout-adversary/probe_rederive.txt
set -u
REPO=$(git rev-parse --show-toplevel)
REV=${1:-b5783ed}
TMP=$(mktemp -d)
trap 'for d in "$TMP"/wt*; do git -C "$REPO" worktree remove --force "$d" >/dev/null 2>&1; done; rm -rf "$TMP"' EXIT

fresh() {  # a new worktree of REV; it holds only tracked files, so no bulk
  local d="$TMP/wt$1"
  git -C "$REPO" worktree add -q --detach "$d" "$REV"
  echo "$d"
}

echo "RBT-99 readout adversary: round trip and perturbations at $(git -C "$REPO" rev-parse --short "$REV")"
echo

W=$(fresh 0)
echo "0. round trip"
echo "   untracked or ignored files in the worktree: $(git -C "$W" status --porcelain --ignored | wc -l)"
echo "   bulk-shaped files under runs/RBT-99, runs/RBT-92 and runs/RBT-90 (history.json, *.jsonl, ckpt, genomes): $(find "$W/runs/RBT-99" "$W/runs/RBT-92" "$W/runs/RBT-90" \( -name 'history.json' -o -name '*.jsonl' -o -name '*ckpt*' -o -name 'gen*.json' -o -name 'best_gen*' \) | wc -l)"
(cd "$W" && runs/RBT-99/readout.sh > "$TMP/r0.txt" 2>&1); echo "   readout.sh exit $?"
(cd "$W" && python3 runs/RBT-99/score.py > "$TMP/s0.txt" 2>&1); echo "   score.py exit $?"
for p in "r0 readout.txt" "s0 score.txt"; do set -- $p
  if cmp -s "$TMP/$1.txt" "$W/runs/RBT-99/$2"; then echo "   $2: byte-identical ($(sha256sum < "$TMP/$1.txt" | cut -c1-16))"; else echo "   $2: DIFFERS"; diff "$TMP/$1.txt" "$W/runs/RBT-99/$2" | head -10; fi
done
echo "   arms the readout reads: seeds read line: $(grep 'seeds read' "$TMP/r0.txt")"
echo

perturb() {  # $1 label  $2 worktree index  $3 python that edits files under cwd  $4 grep for lines to show  $5 how many
  local W; W=$(fresh "$2")
  (cd "$W" && python3 -c "$3")
  (cd "$W" && runs/RBT-99/readout.sh > "$TMP/r$2.txt" 2>&1); local rc=$?
  (cd "$W" && python3 runs/RBT-99/score.py > "$TMP/s$2.txt" 2>&1); local sc=$?
  echo "$1"
  echo "   readout.sh exit $rc; readout lines changed: $(diff "$TMP/r0.txt" "$TMP/r$2.txt" | grep -c '^>');  score.py exit $sc; score lines changed: $(diff "$TMP/s0.txt" "$TMP/s$2.txt" | grep -c '^>')"
  echo "   readout sections touched: $(diff "$TMP/r0.txt" "$TMP/r$2.txt" | grep '^[0-9]' | while read -r h; do n=${h%%[acd]*}; n=${n%%,*}; awk -v n="$n" 'NR<=n && /^[A-Z][A-Z0-9-]+[ :(]/ {s=$1" "$2} END {print s}' "$TMP/r0.txt"; done | sort | uniq -c | tr -s ' ' | tr '\n' ';')"
  diff "$TMP/r0.txt" "$TMP/r$2.txt" | grep '^[<>]' | grep -E "${4:-.}" | head -"${5:-8}" | cut -c1-200 | sed 's/^/     /'
  echo
}

EDIT='
import csv,sys
def edit(p, pred, col, delta):
    rows=list(csv.reader(open(p),delimiter="\t")); h=rows[0]; i=h.index(col); n=0
    for r in rows[1:]:
        if pred(r): r[i]=repr(float(r[i])+delta); n+=1
    csv.writer(open(p,"w",newline=""),delimiter="\t",lineterminator="\n").writerows(rows); print("edited",n,"cells",file=sys.stderr)
'

# 1. a baseline cell: RBT-90/forage-2, season T+100 = 482, designed income +1.0
perturb "1. runs/RBT-90/forage-2/seasons.txt, season 482 conventional mean_lifetime_score +1.0 (base, recovery window)" 1 "$EDIT
edit('runs/RBT-90/forage-2/seasons.txt', lambda r: r[0]=='482' and r[1]=='conventional', 'mean_lifetime_score', 1.0)" \
  "      2  382    base|mean    base   recovery|R-shift  conventional recovery|^. +2: " 8

# 2. a verdict cell: shift-806, every recovery season, holistic -0.5 (seed 806 is the largest paired gap)
perturb "2. runs/RBT-99/shift-806/seasons.txt, seasons 425..524 holistic mean_lifetime_score -0.5 each" 2 "$EDIT
edit('runs/RBT-99/shift-806/seasons.txt', lambda r: 425<=int(r[0])<525 and r[1]=='holistic', 'mean_lifetime_score', -0.5)" \
  "CLASS|R-body recovery, shift arm|mean   shift   recovery|holds up|806: holistic" 8

# 3. a cull cell (the null): cull-805, season 459, designed +0.5
perturb "3. runs/RBT-99/cull-805/seasons.txt, season 459 conventional mean_lifetime_score +0.5 (the null arm)" 3 "$EDIT
edit('runs/RBT-99/cull-805/seasons.txt', lambda r: r[0]=='459' and r[1]=='conventional', 'mean_lifetime_score', 0.5)" \
  "R-null   conventional recovery|R-cull   conventional recovery|  805  359    cull" 6

# 4. a cull20 cell (RBT-92's arm, linked by readout.sh): cull20-7, season 454, holistic +0.5
perturb "4. runs/RBT-92/cull20-7/seasons.txt, season 454 holistic mean_lifetime_score +0.5 (RBT-92's cull20, linked)" 4 "$EDIT
edit('runs/RBT-92/cull20-7/seasons.txt', lambda r: r[0]=='454' and r[1]=='holistic', 'mean_lifetime_score', 0.5)" \
  "cull20" 6

# 5. price.txt: seed 801 designed price +0.1 -> only the C2 block and score.txt may move, never readout.py's part
perturb "5. runs/RBT-99/price.txt, seed 801 conventional price +0.1 (the late file)" 5 "
p='runs/RBT-99/price.txt'; L=open(p).read().split('\n')
for j,l in enumerate(L):
    f=l.split('\t')
    if f[0]=='801' and len(f)>1 and f[1]=='conventional': f[-1]=repr(float(f[-1])+0.1); L[j]='\t'.join(f)
open(p,'w').write('\n'.join(L))" "PRICE|801:|mean net" 6

# 6. a dropped arm: shift-806 removed.  Does anything read 9/10 silently?
perturb "6. runs/RBT-99/shift-806/ removed (a seed silently dropped?)" 6 "
import shutil; shutil.rmtree('runs/RBT-99/shift-806')" "seeds read|806|CLASS" 6
echo "   score.py on the dropped arm: $(tail -2 "$TMP/s6.txt" | tr '\n' ' ' | cut -c1-200)"
echo

# 7. a wrong k: cull-k-3.txt says conventional=40 while the cull arm culled 60 (V1 must catch it)
perturb "7. runs/RBT-99/cull-k-3.txt edited to conventional=40 (the arm culled min(69, 60) = 60)" 7 "
p='runs/RBT-99/cull-k-3.txt'; s=open(p).read().replace('conventional=69','conventional=40'); open(p,'w').write(s)" "V1|V0-V2|INSTRUMENT|FAIL" 6
