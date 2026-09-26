#!/usr/bin/env bash
# RBT-92 readout adversary: the round trip, from a worktree that never held bulk (runs/README.md), and four
# perturbations of committed cells, each in a fresh worktree so nothing leaks between them.
#   bash runs/RBT-92/readout-adversary/probe_rederive.sh > runs/RBT-92/readout-adversary/probe_rederive.txt
set -u
REPO=$(git rev-parse --show-toplevel)
REV=${1:-HEAD}
TMP=$(mktemp -d)
trap 'for d in "$TMP"/wt*; do git -C "$REPO" worktree remove --force "$d" >/dev/null 2>&1; done; rm -rf "$TMP"' EXIT

fresh() {  # a new worktree of REV; it holds only tracked files, so no bulk
  local d="$TMP/wt$1"
  git -C "$REPO" worktree add -q --detach "$d" "$REV"
  echo "$d"
}

echo "RBT-92 readout adversary: round trip and perturbations at $(git -C "$REPO" rev-parse --short "$REV")"
echo

W=$(fresh 0)
echo "0. round trip"
echo "   untracked or ignored files in the worktree: $(git -C "$W" status --porcelain --ignored | wc -l)"
echo "   bulk-shaped files under runs/RBT-92 and runs/RBT-90 (history.json, lineage.jsonl, cohorts.jsonl, ckpt, genomes): $(find "$W/runs/RBT-92" "$W/runs/RBT-90" \( -name 'history.json' -o -name '*.jsonl' -o -name '*ckpt*' -o -name 'gen*.json' \) | wc -l)"
(cd "$W" && python3 runs/RBT-92/readout.py > "$TMP/r0.txt"); echo "   readout.py exit $?"
if cmp -s "$TMP/r0.txt" "$W/runs/RBT-92/readout.txt"; then echo "   output is byte-identical to the committed readout.txt ($(sha256sum < "$TMP/r0.txt" | cut -c1-16))"; else echo "   OUTPUT DIFFERS from readout.txt:"; diff "$TMP/r0.txt" "$W/runs/RBT-92/readout.txt" | head -20; fi
echo

perturb() {  # $1 label  $2 worktree index  $3 python that edits files under cwd
  local W; W=$(fresh "$2")
  (cd "$W" && python3 -c "$3")
  (cd "$W" && python3 runs/RBT-92/readout.py > "$TMP/r$2.txt" 2>&1); local rc=$?
  echo "$1"
  echo "   readout.py exit $rc; lines changed: $(diff "$TMP/r0.txt" "$TMP/r$2.txt" | grep -c '^>')"
  echo "   sections touched: $(diff "$TMP/r0.txt" "$TMP/r$2.txt" | grep '^[0-9]' | while read -r h; do n=${h%%[acd]*}; n=${n%%,*}; awk -v n="$n" 'NR<=n && /^[A-Z][A-Z-]+[ :(]/ {s=$1} END {print s}' "$TMP/r0.txt"; done | sort | uniq -c | tr '\n' ' ')"
  diff "$TMP/r0.txt" "$TMP/r$2.txt" | grep '^[<>]' | grep -E "${4:-.}" | head -"${5:-8}" | sed 's/^/     /'
  echo
}

# 1. a baseline cell (RBT-90's table, not an RBT-92 arm): seed 2, season T+100 = 482, designed income +1.0
perturb "1. runs/RBT-90/forage-2/seasons.txt, season 482 conventional mean_lifetime_score +1.0 (base, recovery window)" 1 '
import csv
p="runs/RBT-90/forage-2/seasons.txt"; rows=list(csv.reader(open(p),delimiter="\t")); h=rows[0]; i=h.index("mean_lifetime_score")
for r in rows[1:]:
    if r[0]=="482" and r[1]=="conventional": r[i]=repr(float(r[i])+1.0)
csv.writer(open(p,"w",newline=""),delimiter="\t",lineterminator="\n").writerows(rows)' "base +recovery|mean +base +recovery|R-shift +conventional recovery|seed 2|^.  +2 " 10

# 2. a verdict-carrying cell: seed 806 shift arm, every recovery season, holistic -0.2: does the verdict move?
perturb "2. runs/RBT-92/shift-806/seasons.txt, seasons 425..524 holistic mean_lifetime_score -0.2 each (seed 806's recovery R-body -0.2)" 2 '
import csv
p="runs/RBT-92/shift-806/seasons.txt"; rows=list(csv.reader(open(p),delimiter="\t")); h=rows[0]; i=h.index("mean_lifetime_score")
for r in rows[1:]:
    if 425<=int(r[0])<525 and r[1]=="holistic": r[i]=repr(float(r[i])-0.2)
csv.writer(open(p,"w",newline=""),delimiter="\t",lineterminator="\n").writerows(rows)' "CLASS|R-body recovery, shift arm|mean +shift +recovery" 6

# 3. V3 containment: rewire the parents of every post-onset holistic birth in shift-7's lineage-last.txt to the
#    first founder.  Alive counts are untouched (V2 still passes); only the descent DAG changes.
perturb "3. runs/RBT-92/shift-7/lineage-last.txt: every holistic individual born after T=354 re-parented to h0-0 (DAG only)" 3 '
import csv
p="runs/RBT-92/shift-7/lineage-last.txt"; rows=list(csv.reader(open(p),delimiter="\t")); h=rows[0]
g,a,pa,po=h.index("generation"),h.index("age"),h.index("parents"),h.index("population")
for r in rows[1:]:
    if r[po]=="holistic" and int(r[g])-int(r[a])>354: r[pa]="h0-0"
csv.writer(open(p,"w",newline=""),delimiter="\t",lineterminator="\n").writerows(rows)' "V0-V2|CLASS|    7   shift  T|L  shift" 8

# 4. a dropped arm: remove shift-806 entirely.  Does the readout refuse, or read 9/10 silently?
perturb "4. runs/RBT-92/shift-806/ removed (a seed silently dropped?)" 4 '
import shutil; shutil.rmtree("runs/RBT-92/shift-806")' "seeds read|CLASS|R-body recovery, shift arm" 8

# 5. a substituted arm: shift-806 replaced by shift-805's tables (same shape, wrong seed)
perturb "5. runs/RBT-92/shift-806/seasons.txt replaced by shift-805/seasons.txt (a substituted seed)" 5 '
import shutil; shutil.copy("runs/RBT-92/shift-805/seasons.txt","runs/RBT-92/shift-806/seasons.txt")' "V0|FAIL|INSTRUMENT" 6
