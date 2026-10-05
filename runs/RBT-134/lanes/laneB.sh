#!/bin/bash
# RBT-134 lane B: the costs E1 and E2 and the holistic census H1 (DESIGN.md 5.2, 8).  See runs/RBT-134/LAUNCH.md.
#
#   RBT134_GO=1 bash runs/RBT-134/lanes/laneB.sh [FOUNDERS_SCRATCH]
#
# FOUNDERS_SCRATCH (default ${TMPDIR:-/tmp}/rbt134-founders) receives RBT-106's planted w = 32 founders, built by
# runs/RBT-106/founders.py (digest-checked) -- never under runs/RBT-106/.  E2's B0 run must reproduce RBT-112's
# committed baseline tables (relayed as a YES/NO token).  Restart-safe: every text output is written to FILE.tmp and
# renamed on success, so an existing file is complete; an H1 JSON is checked like lane A's.  At the end it commits
# out/ to claude/rbt134-runs-B and prints the RELAY block.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

FOUNDERS=${1:-${TMPDIR:-/tmp}/rbt134-founders}
E2_SEEDS=(801 804 805 806 807 1 2 3 4 7)       # RBT-112's ten (runs/RBT-112/erasure.py)
E2_CONDS=(B0 A0 P1 P2 P3 P4 P5)                # DESIGN.md 8; B0 is the reproduction check
H1_CONDS=(B0 A0 P1 P2 P3 P4)                   # DESIGN.md 5.2 (h1_census.HOL_CONDITIONS)
H1_N=100000
BRANCH=claude/rbt134-runs-B

# E1 (RBT-121 audit B parity, every condition, one pass)
if [ -f "$OUT/e1.txt" ]; then skip e1; else to_file e1 "$OUT/e1.txt" $PY runs/RBT-134/e1_parity.py --go; fi

# E2 (RBT-112's u(8)): founders, then 10 seeds per condition, then the summaries
for s in "${E2_SEEDS[@]}"; do
  if [ -f "$FOUNDERS/founders-w32-$s/SHA256SUMS" ]; then
    skip "founders-$s"
  else
    step "founders-$s" $PY runs/RBT-106/founders.py "$s" 32 "$FOUNDERS/founders-w32-$s"
  fi
done
for c in "${E2_CONDS[@]}"; do
  for s in "${E2_SEEDS[@]}"; do
    f="$OUT/e2-$c-$s.txt"
    if [ -f "$f" ]; then skip "e2-$c-$s"; else
      to_file "e2-$c-$s" "$f" $PY runs/RBT-134/e2_erasure.py run "$c" "$s" "$FOUNDERS/founders-w32-$s" --procs "$WORKERS" --go
    fi
  done
  [ "$c" = "B0" ] && continue
  if [ -f "$OUT/e2-summary-$c.txt" ]; then skip "e2-summary-$c"; else
    to_file "e2-summary-$c" "$OUT/e2-summary-$c.txt" $PY runs/RBT-134/e2_erasure.py summary "$c"
  fi
done

# H1 (the holistic census, both arms), then its readout
for c in "${H1_CONDS[@]}"; do
  if check_json h1 "$OUT/h1-$c.json" "$H1_N"; then skip "h1-$c"; else
    step "h1-$c" $PY runs/RBT-134/h1_census.py run "$c" --go --n "$H1_N" --workers "$WORKERS"
  fi
done
to_file h1-readout "$OUT/h1-readout.txt" $PY runs/RBT-134/h1_census.py readout

[ "${RBT134_DRY:-0}" = "1" ] && { echo "PLAN end (dry run: no commit, no RELAY)"; exit 0; }

FILES=(e1.txt h1-readout.txt)
for c in "${E2_CONDS[@]}"; do
  for s in "${E2_SEEDS[@]}"; do FILES+=("e2-$c-$s.txt"); done
  [ "$c" = "B0" ] || FILES+=("e2-summary-$c.txt")
done
for c in "${H1_CONDS[@]}"; do FILES+=("h1-$c.json"); done
commit_outputs "$BRANCH" "${FILES[@]}"

$RELAY relay-b "$OUT" "$HEAD" "$((SECONDS - T0))" $(cpu_times)
echo "output branch: $BRANCH"
