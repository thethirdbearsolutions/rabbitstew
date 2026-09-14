#!/usr/bin/env bash
# RBT-74: one arena run, protected or unprotected, resumable.
#   scripts/rbt74_run.sh SEED prot|base [WORKERS]
# The configuration is docs/followup-paper.md section 7's command with the rich brain; the
# protected arm adds --protect-morphology 4 (pre-registered on RBT-74). If the run's state.json
# exists the run resumes from it, so a relaunch after a container recycle continues where it
# stopped and produces the same run (the RNG state is checkpointed with the populations).
set -euo pipefail
SEED=$1; ARM=$2; WORKERS=${3:-1}
OUT=runs/RBT-74/$ARM-$SEED
case $ARM in
  prot) EXTRA="--protect-morphology 4" ;;
  base) EXTRA="" ;;
  *) echo "arm must be prot or base" >&2; exit 2 ;;
esac
if [ -f "$OUT/state.json" ]; then
  exec rabbitstew evolve --resume --workers "$WORKERS" --out "$OUT"
fi
exec rabbitstew evolve --generations 250 --population 20 --duration 15 --mass-budget 15.34 \
  --conventional-topology --brain-model rich --terrain random \
  --champion-interval 5 --champions 5 --champion-mode roundrobin \
  --seed "$SEED" --workers "$WORKERS" $EXTRA --out "$OUT"
