#!/bin/bash
# RBT-113 design-adversary probe (throwaway): paths are the adversary session's scratch (#377 checked out at /tmp/claude-0/d113).
# U, D, C at seed 1, the arms' world and N, 8 generations
cd /tmp/claude-0/d113
for L in U D C; do
  mapfile -d '' CMD < <(WORKERS=4 /tmp/claude-0/venv/bin/python -c "
import sys; sys.path.insert(0,'runs/RBT-113'); import world
sys.stdout.write('\0'.join(world.command('$L','',1,'/tmp/claude-0/probe/$L',workers='4',generations=8)))")
  CMD[0]=/tmp/claude-0/venv/bin/python
  SECONDS=0; "${CMD[@]}" > /tmp/claude-0/probe/$L.log 2>&1; echo "$L $SECONDS s"
done
echo done
