#!/bin/bash
# RBT-112 step 2: the throwaway short runs byte_identity.py reads (not arms), into $1 (outside the checkout).
# RBT-104's short_run.sh is RBT-90 part 2's command.  HUold-801 runs the same command on c872e80's code, in a
# git worktree of c872e80 at $1/wt-c872e80 (python -m resolves rabbitstew from the worktree's cwd).
set -e
cd "$(dirname "$0")/../.."
S=$1; mkdir -p "$S"
R=runs/RBT-104/short_run.sh
for SEED in 801; do for W in 1 32; do [ -f runs/RBT-106/founders-w$W-$SEED/SHA256SUMS ] || python runs/RBT-106/founders.py $SEED $W runs/RBT-106/founders-w$W-$SEED; done; done
$R 801 10 "$S/p2-801"
$R 4 10 "$S/p2-4"
$R 801 20 "$S/S1U-801" --from-conventional runs/RBT-106/founders-w1-801
$R 801 20 "$S/HU-801" --from-conventional runs/RBT-106/founders-w32-801
$R 801 20 "$S/HU0-801" --from-conventional runs/RBT-106/founders-w32-801 --global-bias-sigma 0
[ -d "$S/wt-c872e80" ] || git worktree add -q "$S/wt-c872e80" c872e80
F=$PWD/runs/RBT-106/founders-w32-801
(cd "$S/wt-c872e80" && python -c "import rabbitstew.genetics as g; assert not hasattr(g.MutationConfig(), 'global_bias_sigma')" \
  && bash runs/RBT-104/short_run.sh 801 20 "$S/HUold-801" --from-conventional "$F")
python -c "import platform, mujoco, numpy; print(f'platform {platform.machine()} mujoco {mujoco.__version__} numpy {numpy.__version__}')" > "$S/HU-801/platform.txt"
python runs/RBT-112/byte_identity.py "$S" > runs/RBT-112/byte_identity.txt
tail -1 runs/RBT-112/byte_identity.txt
