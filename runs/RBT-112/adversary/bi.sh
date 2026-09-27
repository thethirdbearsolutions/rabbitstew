#!/bin/bash
# RBT-112 design adversary §1: throwaway byte-identity and freezing runs (not arms), into $SCRATCH/bi.
# NEW = this checkout (PR #277's head with adversary/ merged); OLD = a worktree of c872e80 (made if missing).
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../.." && pwd)
S=${SCRATCH:-/tmp/rbt-112-adv}; O=$S/bi; mkdir -p "$O"
R=$HERE/run_code.sh; NEW=$ROOT; OLD=${OLD_ROOT:-$S/wt-c872e80}
[ -d "$OLD" ] || git -C "$ROOT" worktree add -q "$OLD" c872e80
for SEED in 801 4; do
  F=$ROOT/runs/RBT-106/founders-w32-$SEED; [ -f "$F/SHA256SUMS" ] || (cd "$ROOT" && python runs/RBT-106/founders.py $SEED 32 "$F")
done
for SEED in 801 4; do
  $R $NEW $SEED $O/new-HU-$SEED 20 &
  $R $OLD $SEED $O/old-HU-$SEED 20
  wait
done
$R $NEW 801 $O/sig04-HU-801 20 --global-bias-sigma 0.4 &
$R $NEW 4 $O/s0-HU-4 40 --global-bias-sigma 0
wait
$R $NEW 801 $O/s0-HU-801 40 --global-bias-sigma 0 &
$R $NEW 4 $O/new40-HU-4 40
wait
$R $NEW 801 $O/new40-HU-801 40
python "$HERE/bi_compare.py" "$O" > "$HERE/bi_compare.txt"
tail -1 "$HERE/bi_compare.txt"
