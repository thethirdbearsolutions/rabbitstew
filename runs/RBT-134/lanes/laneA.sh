#!/bin/bash
# RBT-134 lane A: the Pioneer assay (DESIGN.md 3, 4, 13), its readout, and re-signing.  See runs/RBT-134/LAUNCH.md.
#
#   RBT134_GO=1 bash runs/RBT-134/lanes/laneA.sh
#
# Order (DESIGN.md 13, S4): the controls B0, C+, A0; the checks P1, P4, P5; then P2 FIRST (a determinate computation
# from committed data) and P3.  Then the readout and re-signing (capped at 400 per condition by lineage index).
# Restart-safe: a condition whose out JSON is complete at this head is skipped; one written at another head refuses
# (exit 5).  At the end it commits out/ to claude/rbt134-runs-A and prints the RELAY block, which is all that may be
# relayed (LAUNCH.md).
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

N=100000      # lineages per pool (200,000 per condition; DESIGN.md 3)
N_BG=20000    # background lineages per pool (40,000; DESIGN.md 3.5)
CONDS=(B0 C+ A0 P1 P4 P5 P2 P3)
BRANCH=claude/rbt134-runs-A

for c in "${CONDS[@]}"; do
  if check_json assay "$OUT/$c.json" "$N"; then
    skip "$c"
  else
    step "$c" $PY runs/RBT-134/assay.py run "$c" --go --n "$N" --n-bg "$N_BG" --workers "$WORKERS"
  fi
done

to_file readout "$OUT/readout.txt" $PY runs/RBT-134/assay.py readout

for c in "${CONDS[@]}"; do
  if [ -f "$OUT/$c-resign.txt" ]; then
    skip "$c-resign"
  else
    step "$c-resign" $PY runs/RBT-134/assay.py resign "$c" --go --cap 400 --workers "$WORKERS"
  fi
done

[ "${RBT134_DRY:-0}" = "1" ] && { echo "PLAN end (dry run: no commit, no RELAY)"; exit 0; }

FILES=(readout.txt)
for c in "${CONDS[@]}"; do FILES+=("$c.json" "$c-resign.txt"); done
commit_outputs "$BRANCH" "${FILES[@]}"

$RELAY relay-a "$OUT" "$HEAD" "$((SECONDS - T0))" $(cpu_times)
echo "output branch: $BRANCH"
