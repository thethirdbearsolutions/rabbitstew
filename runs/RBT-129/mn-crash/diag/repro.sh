#!/bin/bash
# RBT-129 crash diagnosis: rebuild the faulting physics state of 1/c2-p030-U-G/129001/M from its ckpt60 (never from the
# quarantined ckpt/rbt-129-stage1-c2-p030-U-G-129001-M).  Crash-only: stdout/stderr of the ecology go to files that are
# only grepped for the faulthandler block; the scratch run is the caller's to delete unread.
#   repro.sh VENV SCRATCH        (VENV: pip mujoco==3.14.0, numpy 2.4.6; SCRATCH: an empty dir outside runs/)
# Steps: 1 fork M from ckpt60 (fork_config's merge settings), run it with NO_DURABLE=1 WORKERS=1 until it exits 139,
# keeping a copy of the run dir at each new state.json; 2 the last copy (state before the faulting season) -> pre/;
# 3 trace.py count on a copy of pre/ -> [sim, step, total]; 4 trace.py dump at that (sim, step) -> dump/;
# 5 replay.py dump/ <step> step  faults in one mj_step.
set -eu
VENV=$1; S=$2; ROOT=$(git rev-parse --show-toplevel); L=rbt-129-stage1-c2-p030-U-G-129001-ckpt60
"$VENV/bin/python" -c 'import mujoco; assert mujoco.__version__ == "3.14.0", mujoco.__version__'
mkdir -p "$S/ck"; git -C "$ROOT" fetch -q origin "+refs/heads/ckpt/$L:refs/remotes/origin/ckpt/$L"
for p in $(git -C "$ROOT" ls-tree --name-only "origin/ckpt/$L" | grep '^run.tar.gz.part' | sort); do
  git -C "$ROOT" cat-file blob "origin/ckpt/$L:$p" >> "$S/ck/run.tgz"; done
tar -C "$S/ck" -xzf "$S/ck/run.tgz"; cp -a "$S/ck/ckpt60" "$S/fork"; rm -f "$S/fork"/.rbt129-done-*
"$VENV/bin/python" - "$S/fork/config.json" <<'PY'
import json, sys
c = json.load(open(sys.argv[1])); c["ecology"].update({"merge_after": 60, "pooled_capacity": 120}); json.dump(c, open(sys.argv[1], "w"), indent=2)
PY
code=0
( cd "$ROOT" && PYTHONFAULTHANDLER=1 NO_DURABLE=1 "$VENV/bin/python" -m rabbitstew.cli ecology --resume --seasons 300 \
    --workers 1 --out "$S/fork" > "$S/fork.out" 2>&1 ) &
pid=$!; last=""
while kill -0 $pid 2>/dev/null; do  # copy the dir whenever state.json changes (the copy before the fault is kept)
  m=$(stat -c %Y.%N "$S/fork/state.json" 2>/dev/null || true)
  if [ "$m" != "$last" ]; then last=$m; sleep 1; rm -rf "$S/pre.new"; cp -a "$S/fork" "$S/pre.new" && rm -rf "$S/pre" && mv "$S/pre.new" "$S/pre"; fi
  sleep 2
done
wait $pid || code=$?
echo "ecology exit $code"; sed -n '/Fatal Python error/,/^$/p' "$S/fork.out" | grep -E 'Fatal|File' || true
D=$(dirname "$0"); cp -a "$S/pre" "$S/t1"
PYTHONPATH=$ROOT "$VENV/bin/python" "$D/trace.py" count "$S/t1" "$S/cnt" || true
read -r SIM STEP < <("$VENV/bin/python" -c "import numpy as n; c=n.memmap('$S/cnt',dtype=n.int64,mode='r',shape=(3,)); print(c[0], c[1])")
echo "fault at simulation $SIM, mj_step $STEP"; cp -a "$S/pre" "$S/t2"
PYTHONPATH=$ROOT "$VENV/bin/python" "$D/trace.py" dump "$S/t2" "$S/cnt2" "$SIM" "$STEP" "$S/dump" || true
"$VENV/bin/python" "$D/replay.py" "$S/dump" "$STEP" step || echo "replay exit $? (139 = reproduced)"
