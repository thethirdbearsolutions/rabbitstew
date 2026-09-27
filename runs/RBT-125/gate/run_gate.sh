#!/bin/bash
# RBT-125 world gate: every compute job, in the registered order (REGISTRATION.md §D).  Refuses to start before
# 23:01 UTC on 2026-09-27 (the programme's compute window).  Idempotent: a finished output (with its ROW / final
# line) is skipped, so the script can be re-run after an interruption.
#
#   runs/RBT-125/gate/run_gate.sh BODIES_ROOT HOSTS_ROOT
#     BODIES_ROOT/forage-SEED/{config.json,conventional/best_gen*.json,state.json}   (ckpt/rbt-90-SEED)
#     HOSTS_ROOT/O1/{1,2,3}/U/conventional/final/*.json                             (ckpt/rbt-113-O1)
set -e
B=$1; H=$2; P=${PROCS:-4}
cd "$(dirname "$0")/../../.."
G=runs/RBT-125/gate
now=$(date -u +%s); open=$(date -u -d "2026-09-27 23:01:00" +%s)
[ "$now" -ge "$open" ] || { echo "refusing: compute opens at 23:01 UTC ($(date -u))"; exit 2; }
mkdir -p $G/prize $G/steps
{ echo "# RBT-125 gate launch record"; echo "commit $(git rev-parse HEAD)"; echo "rabbitstew_tree $(git rev-parse HEAD:rabbitstew)";
  echo "started $(date -u +%FT%TZ)"; python -c "import platform,mujoco,numpy;print(platform.platform(),platform.machine(),'mujoco',mujoco.__version__,'numpy',numpy.__version__)"; } > $G/launch.txt
python $G/worlds.py > /dev/null
git diff --quiet -- $G/worlds || { echo "worlds/ differ from the registered ones"; exit 3; }

prize() {  # cell seed extra...
  local cell=$1 s=$2; shift 2
  local out=$G/prize/$cell-$s.txt
  [ -s "$out" ] && grep -q '^ROW' "$out" && return 0
  python $G/prize_gate.py --run "$B/forage-$s" --config-from $G/worlds/$cell --label "$s-$cell" --w 3 --procs $P "$@" > "$out.tmp" 2> "$out.err"
  mv "$out.tmp" "$out"
}
SEEDS="801 804 805 806 807 1 2 3 4 7"

# 0. the harness check: this tree reproduces RBT-103's committed seed-801 row in its own world, to the digit
h=$G/prize/harness-801-uniform.txt
[ -s "$h" ] && grep -q '^ROW' "$h" || python $G/prize_gate.py --run "$B/forage-801" --label 801 --w 16,32 --procs $P > "$h" 2> "$h.err"
# 1. the gate: PW at the registered G, the alternative G and the legacy control, with the decoy
for cell in PW-G2.5 PW-G10 PW-G0; do for s in $SEEDS; do prize $cell $s --decoy 3; done; done
python $G/prize_readout.py > $G/prize.txt
# 2. the nose step against the speed step on RBT-113 hosts
for cell in PW-G2.5 PW-G10 PW-G0; do
  out=$G/steps/$cell.txt
  [ -s "$out" ] && grep -q '^STEP' "$out" || { python $G/steps.py "$H" $cell --procs $P > "$out.tmp" 2> "$out.err"; mv "$out.tmp" "$out"; }
done
# 3. the R6 side effects
out=$G/side_effects.txt
[ -s "$out" ] && grep -q 'tumbler' "$out" || { python $G/side_effects.py "$B" --procs $P > "$out.tmp" 2> "$out.err"; mv "$out.tmp" "$out"; }
# 4. the committed layouts at the two G, then their legacy controls
for cell in HP-G2.5 U-G2.5 HP-G10 U-G10 HP-G0 U-G0; do for s in $SEEDS; do prize $cell $s; done; python $G/prize_readout.py > $G/prize.txt; done
echo "finished $(date -u +%FT%TZ)" >> $G/launch.txt
