#!/bin/bash
# RBT-134b registered run at MASTER_SEED 20260912 (DESIGN-134b.md 7, 9 step 5; REGISTRATION-134b.md): the 134b assay,
# its readout, and re-signing.  The 134b counterpart of laneA.sh, on the same conventions (common.sh).
#
#   RBT134B_GO=<the owner's GO sha for the registered run> bash runs/RBT-134/lanes/lane134b.sh
#
# Run it from a clean checkout of the GO sha, in a venv made as REGISTRATION-134b.md says (".[dev]" with
# mujoco==3.14.0 pinned in the venv only); the lane refuses any other mujoco (exit 10), and refuses while the held-out
# validation's spend (assay.VALIDATION_SPENT_H) is not registered (exit 11).
#
# Order (DESIGN.md 13): the controls B0, C+L1 (the registered rung), A0 and A0's I5-S swap; then THE CONTROL GATE: the
# 134b readout over the controls alone, and the lane stops (exit 8, outputs committed, RELAY printed) unless its VOID
# list is "none" -- decided by relay134b.py from that one token, no value is read.  Then the checks P1 (+ swap),
# P4 (+ swap), P5; P2 FIRST (+ swap), then P3 (+ swap); the readout; re-signing (capped at 400 per condition; all
# conditions but A0, OWNER-DECISIONS item 8), each condition priced at its actual eligible count first.  I5-S B0 at MASTER_SEED is the RBT-134 diagnosis's EXACT,
# cited, not re-run (DESIGN-134b.md 6.1, trim iv).
#
# The cost stop rule (DESIGN-134b.md 8) runs inside every run134b and resign134b: a STOP-COST exits 9, and the lane
# then commits what it has, prints the RELAY block with status stopped-cost and exits 9; the owner decides.
#
# Restart-safe as lane A: a JSON complete at this head is skipped, a text output marked with this head (FILE.head) is
# skipped, and anything from another head refuses (exit 5).  At the end it commits out/134b-20260912/ to
# claude/rbt134b-runs and prints the RELAY block, which is all that may be relayed (LAUNCH.md).
if [ -z "${RBT134B_GO:-}" ]; then
  echo "refused: the RBT-134b registered run runs only after the owner's GO (set RBT134B_GO=<the GO sha>)" >&2
  exit 3
fi
export RBT134_GO=$RBT134B_GO
LANE=134b
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

SEED=20260912
N=100000      # lineages per pool (200,000 per condition; DESIGN.md 3, unchanged in 134b)
N_BG=20000    # background lineages per pool (40,000)
CPLUS=C+L1    # the registered rung (assay.CPLUS_REGISTERED; REGISTRATION-134b.md)
CONTROLS=(B0 "$CPLUS" A0)
CHECKS=(P1 P4 P5)
FAMILY=(P2 P3)  # P2 first (DESIGN.md 13 step 4)
SWAPS_OF=" A0 P1 P2 P3 P4 "  # I5-S at MASTER_SEED (B0's is cited)
CONDS=("${CONTROLS[@]}" "${CHECKS[@]}" "${FAMILY[@]}")
RESIGNED=(B0 "$CPLUS" "${CHECKS[@]}" "${FAMILY[@]}")  # all but A0: bounded at 0 at a16 (OWNER-DECISIONS item 8)
BRANCH=claude/rbt134b-runs
OUT=runs/RBT-134/out/134b-$SEED
LOG=$OUT/lane-134b.log
RELAY="$PY runs/RBT-134/lanes/relay134b.py"
mkdir -p "$OUT"

mj=$(ask mujoco mujoco-ok) || exit 6
if [ "$mj" != "ok" ]; then
  echo "refused: this interpreter's mujoco is not the lane's pin (3.14.0); make the venv as REGISTRATION-134b.md says" >&2
  exit 10
fi

# the cost stop rule counts everything 134b has spent (DESIGN-134b.md 8): this checkout has no validation ledgers, so
# the validation's spend must be registered (assay.VALIDATION_SPENT_H, REGISTRATION-134b.md 1) or the rule undercounts
vs=$(ask validation-spent validation-spent-ok) || exit 6
if [ "$vs" != "ok" ]; then
  echo "refused: the held-out validation's spend (assay.VALIDATION_SPENT_H) is not registered; see REGISTRATION-134b.md" >&2
  exit 11
fi

relay() {  # the RELAY block (all that may be relayed)
  $RELAY relay "$OUT" "$HEAD" --committed "$COMMITTED" --status "$1" "${STAGES[@]}" || {
    echo "FAILED: the RELAY block" >&2; exit 6; }
}

present() {  # every output in OUT so far (for a commit after a stop)
  local f
  for f in "$OUT"/*; do [ -f "$f" ] && [[ "$f" != *.tmp ]] && echo "${f#"$OUT"/}"; done
}

stop_cost() {
  echo "STOPPED: STOP-COST at $1 (DESIGN-134b.md 8): 30 CPU-h would be passed; nothing further runs, the owner decides"
  stage ""
  commit_outputs "$BRANCH" $(present)
  relay stopped-cost
  echo "output branch: $BRANCH"
  exit 9
}

# run_or_stop NAME CMD... : as common.sh's step, but exit status 9 (a STOP-COST) stops the lane cleanly
run_or_stop() {
  local name=$1 rc; shift
  if [ "$DRY" = "1" ]; then echo "PLAN run $name: $*"; return 0; fi
  echo "run $name"
  echo "=== run $name: $*" >> "$LOG"
  "$@" >> "$LOG" 2>&1
  rc=$?
  [ "$rc" -eq 0 ] && return 0
  [ "$rc" -eq 9 ] && stop_cost "$name"
  fail "$name"
}

assay() {  # COND, then its I5-S swap where one runs at MASTER_SEED
  if check_json run "$OUT/$1.json" "$N" "$N_BG"; then skip "$1"; else
    run_or_stop "$1" $PY runs/RBT-134/assay.py run134b "$1" --seed "$SEED" --go --n "$N" --n-bg "$N_BG" --workers "$WORKERS"
  fi
  if [[ "$SWAPS_OF" == *" $1 "* ]]; then
    if check_json swap "$OUT/$1-swap.json" "$N" "$N_BG"; then skip "$1-swap"; else
      run_or_stop "$1-swap" $PY runs/RBT-134/assay.py run134b "$1" --seed "$SEED" --go --swap --n "$N" --n-bg "$N_BG" --workers "$WORKERS"
    fi
  fi
}

files() {  # the lane's outputs (for the commit), given the conditions run
  echo readout-controls.txt readout-controls.txt.head lane-134b.log cpu-ledger.jsonl
  local c
  for c in "$@"; do
    echo "$c.json"
    [[ "$SWAPS_OF" == *" $c "* ]] && echo "$c-swap.json"
  done
}

stage controls
for c in "${CONTROLS[@]}"; do assay "$c"; done

stage gate
to_file control-gate "$OUT/readout-controls.txt" $PY runs/RBT-134/assay.py readout134b --seed "$SEED"
if [ "$DRY" = "1" ]; then
  echo "PLAN control gate: stop (exit 8) unless the VOID list of readout-controls.txt is none"
elif ! gate=$(ask control-gate gate "$OUT/readout-controls.txt"); then
  exit 6
elif [ "$gate" != "PASS" ]; then
  echo "STOPPED at the control gate (DESIGN.md 13 step 3): a control VOIDs; the checks and the family do not run"
  stage ""
  commit_outputs "$BRANCH" $(files "${CONTROLS[@]}")
  relay stopped-at-control-gate
  echo "output branch: $BRANCH"
  exit 8
fi

stage checks-and-family
for c in "${CHECKS[@]}" "${FAMILY[@]}"; do assay "$c"; done

stage readout
to_file readout "$OUT/readout.txt" $PY runs/RBT-134/assay.py readout134b --seed "$SEED"

# re-signing is deliberately untimed, as in lane A: its CPU tracks the number of re-signed arrivals
stage ""
for c in "${RESIGNED[@]}"; do
  f="$OUT/$c-resign.txt"
  if have_text "$f"; then skip "$c-resign"; else
    run_or_stop "$c-resign" $PY runs/RBT-134/assay.py resign134b "$c" --go --cap 400 --workers "$WORKERS"
    mark "$f"
  fi
done

[ "$DRY" = "1" ] && { echo "PLAN end (dry run: no commit, no RELAY)"; exit 0; }

FILES=($(files "${CONDS[@]}") readout.txt readout.txt.head)
for c in "${RESIGNED[@]}"; do FILES+=("$c-resign.txt" "$c-resign.txt.head"); done
commit_outputs "$BRANCH" "${FILES[@]}"
relay done
echo "output branch: $BRANCH"
