#!/bin/bash
# RBT-134 lane A: the Pioneer assay (DESIGN.md 3, 4, 13), its readout, and re-signing.  See runs/RBT-134/LAUNCH.md.
#
#   RBT134_GO=<GO sha> bash runs/RBT-134/lanes/laneA.sh
#
# Order (DESIGN.md 13, S4): the controls B0, C+, A0, then THE CONTROL GATE (step 3: I1-I7 must pass before step 4):
# the registered readout over the controls alone, and the lane stops (exit 8, outputs committed, RELAY printed) unless
# its VOID list is "none" -- decided by relay.py from that one token, no value is read.  Then the checks P1, P4, P5;
# P2 FIRST (a determinate computation from committed data) and P3; the readout; re-signing (capped at 400 per
# condition by lineage index).  Restart-safe: a JSON complete at this head is skipped, a text output marked with this
# head (FILE.head) is skipped, and anything from another head refuses (exit 5).  At the end it commits out/ to
# claude/rbt134-runs-A and prints the RELAY block, which is all that may be relayed (LAUNCH.md).
LANE=A
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

N=100000      # lineages per pool (200,000 per condition; DESIGN.md 3)
N_BG=20000    # background lineages per pool (40,000; DESIGN.md 3.5)
CONTROLS=(B0 C+ A0)
REST=(P1 P4 P5 P2 P3)
CONDS=("${CONTROLS[@]}" "${REST[@]}")
BRANCH=claude/rbt134-runs-A

assay() {
  if check_json assay "$OUT/$1.json" "$N" "$N_BG"; then skip "$1"; else
    step "$1" $PY runs/RBT-134/assay.py run "$1" --go --n "$N" --n-bg "$N_BG" --workers "$WORKERS"
  fi
}

files() {  # the lane's outputs so far (for the commit), given the conditions run
  echo readout-controls.txt readout-controls.txt.head lane-A.log
  local c
  for c in "$@"; do echo "$c.json"; done
}

stage controls
for c in "${CONTROLS[@]}"; do assay "$c"; done

stage gate
to_file control-gate "$OUT/readout-controls.txt" $PY runs/RBT-134/assay.py readout
if [ "$DRY" = "1" ]; then
  echo "PLAN control gate: stop (exit 8) unless the VOID list of readout-controls.txt is none"
elif [ "$($RELAY gate "$OUT/readout-controls.txt")" != "PASS" ]; then
  echo "STOPPED at the control gate (DESIGN.md 13 step 3): a control VOIDs; the checks and the family do not run"
  stage ""
  commit_outputs "$BRANCH" $(files "${CONTROLS[@]}")
  relay stopped-at-control-gate
  echo "output branch: $BRANCH"
  exit 8
fi

stage checks-and-family
for c in "${REST[@]}"; do assay "$c"; done

stage readout
to_file readout "$OUT/readout.txt" $PY runs/RBT-134/assay.py readout

stage resign
for c in "${CONDS[@]}"; do
  f="$OUT/$c-resign.txt"
  if have_text "$f"; then skip "$c-resign"; else
    step "$c-resign" $PY runs/RBT-134/assay.py resign "$c" --go --cap 400 --workers "$WORKERS"  # writes f atomically
    mark "$f"
  fi
done
stage ""

[ "$DRY" = "1" ] && { echo "PLAN end (dry run: no commit, no RELAY)"; exit 0; }

FILES=($(files "${CONDS[@]}") readout.txt readout.txt.head)
for c in "${CONDS[@]}"; do FILES+=("$c-resign.txt" "$c-resign.txt.head"); done
commit_outputs "$BRANCH" "${FILES[@]}"
relay done
echo "output branch: $BRANCH"
