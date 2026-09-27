#!/bin/bash
# RBT-125 world gate: every compute job, in the registered order (REGISTRATION.md §D, amended per the coordinator's
# ruling of 22:28).  Refuses to start before 23:01 UTC on 2026-09-27: compute opens then.
# Idempotent: an output is promoted from .tmp only when its program exits 0 and the
# output carries its completion marker, so an interruption never leaves a truncated file that a re-run would skip.
#
#   runs/RBT-125/gate/run_gate.sh BODIES_ROOT HOSTS_ROOT
#     BODIES_ROOT/forage-SEED/{config.json,conventional/best_gen*.json,state.json}   (ckpt/rbt-90-SEED)
#     HOSTS_ROOT/O1/{1,2,3}/U/conventional/final/*.json                             (ckpt/rbt-113-O1)
set -e -o pipefail
B=$1; H=$2; P=${PROCS:-4}
cd "$(dirname "$0")/../../.."
G=runs/RBT-125/gate
PIN=0ec395f7  # the tree the adversary checked for parity with #414's head: rabbitstew/ must be identical to it
now=$(date -u +%s); open=$(date -u -d "2026-09-27 23:01:00" +%s)
[ "$now" -ge "$open" ] || { echo "refusing: compute opens at 23:01 UTC ($(date -u))"; exit 2; }
python -c "import scipy" || { echo "refusing: scipy is not installed"; exit 2; }
[ "$(git rev-parse HEAD:rabbitstew)" = "$(git rev-parse $PIN:rabbitstew)" ] || { echo "refusing: rabbitstew/ differs from $PIN"; exit 3; }
git diff --quiet HEAD -- rabbitstew runs/RBT-125 runs/RBT-103 runs/RBT-97 scripts || { echo "refusing: uncommitted changes in the code the gate runs"; exit 3; }
mkdir -p $G/prize $G/steps
{ echo "# RBT-125 gate launch record"; echo "commit $(git rev-parse HEAD)"
  echo "rabbitstew_tree $(git rev-parse HEAD:rabbitstew)"; echo "rabbitstew_tree_at_$PIN $(git rev-parse $PIN:rabbitstew)"
  echo "started $(date -u +%FT%TZ)"
  python -c "import platform,mujoco,numpy,scipy;print(platform.platform(),platform.machine(),'python',platform.python_version(),'mujoco',mujoco.__version__,'numpy',numpy.__version__,'scipy',scipy.__version__)"; } > $G/launch.txt
python $G/worlds.py > /dev/null
[ -z "$(git status --porcelain -- $G/worlds)" ] || { echo "worlds/ differ from the registered ones"; exit 3; }

promote() {  # out marker cmd...  : run cmd > out.tmp; promote only on exit 0 with the marker present
  local out=$1 marker=$2; shift 2
  [ -s "$out" ] && grep -q "$marker" "$out" && return 0
  if "$@" > "$out.tmp" 2> "$out.err" && grep -q "$marker" "$out.tmp"; then mv "$out.tmp" "$out"; else echo "FAILED: $out ($*)"; return 1; fi
}
prize() {  # cell seed extra...
  local cell=$1 s=$2; shift 2
  promote $G/prize/$cell-$s.txt '^ROW' python $G/prize_gate.py --run "$B/forage-$s" --config-from $G/worlds/$cell --label "$s-$cell" --w 3 --procs $P "$@" || true
}
same_row() {  # ours committed
  [ "$(grep -m1 '^ROW' "$1")" = "$(grep -m1 '^ROW' "$2")" ]
}
SEEDS="801 804 805 806 807 1 2 3 4 7"

# 0. the harness checks: this tree reproduces RBT-103's committed seed-801 row in its own world, and RBT-106's
#    committed HP-801 row through --config-from with the legacy decoy, to the digit.  DIFFERENT stops everything.
promote $G/prize/harness-801-uniform.txt '^ROW' python $G/prize_gate.py --run "$B/forage-801" --label 801 --w 16,32 --procs $P
same_row $G/prize/harness-801-uniform.txt docs/artifacts/RBT-103-seed-801.txt || { echo "STOP: harness check (uniform) DIFFERENT"; exit 4; }
promote $G/prize/harness-801-HP.txt '^ROW' python $G/prize_gate.py --run "$B/forage-801" --config-from runs/RBT-106/world-patchy \
  --label 801-in-one-field-patchy --w 16,32 --decoy 32 --procs $P
same_row $G/prize/harness-801-HP.txt runs/RBT-106/prize/patchy-801.txt || { echo "STOP: harness check (HP, --config-from) DIFFERENT"; exit 4; }
# 1. the gate: PW at the registered G, the alternative G and the legacy control, with the decoy
for cell in PW-G2.5 PW-G10 PW-G0; do for s in $SEEDS; do prize $cell $s --decoy 3; done; done
promote $G/prize.txt '^GATE VERDICT' python $G/prize_readout.py || true
echo "section A computed $(date -u +%FT%TZ)" >> $G/launch.txt
# 2. the tau = 1 s sensitivity cell (descriptive)
for s in $SEEDS; do prize PW-G2.5-tau1 $s --decoy 3; done
# 3. section C: saturation, then the R6 side effects
promote $G/saturation.txt 'U-G10' python $G/saturation.py "$B" --procs $P || true
promote $G/side_effects.txt '^# tumbler' python $G/side_effects.py "$B" --procs $P || true
# 4. the committed layouts at the two G, then their legacy controls
for cell in HP-G2.5 U-G2.5 HP-G10 U-G10 HP-G0 U-G0; do for s in $SEEDS; do prize $cell $s; done; done
{ promote $G/prize.txt.final '^GATE VERDICT' python $G/prize_readout.py && mv $G/prize.txt.final $G/prize.txt; } || true
# 5. section B: the nose step against the speed step, 128 seeds per host
for cell in PW-G2.5 PW-G10 PW-G0; do promote $G/steps/$cell.txt '^STEP' python $G/steps.py "$H" $cell --procs $P || true; done
echo "finished $(date -u +%FT%TZ)" >> $G/launch.txt
