#!/bin/bash
# adversary: run RBT-106's HU command (built by the design checkout's RBT-106 command.py) for SEASONS seasons
# on the rabbitstew/ package at CODE (a checkout root), asserting in the same process which package ran.
#   run_code.sh CODE SEED OUT SEASONS [extra flags]
set -e
CODE=$1; SEED=$2; OUT=$3; SEASONS=$4; shift 4
D=${DESIGN_ROOT:-$(cd "$(dirname "$0")/../../.." && pwd)}
rm -rf "$OUT"; mkdir -p "$OUT"
mapfile -d '' CMD < <(cd $D && SEASONS=$SEASONS WORKERS=2 python runs/RBT-106/command.py HU "$SEED" "$OUT")
# make the founders path absolute; drop "python -m rabbitstew.cli ecology" prefix handling below
ARGS=()
for a in "${CMD[@]}"; do case "$a" in runs/*) ARGS+=("$D/$a");; *) ARGS+=("$a");; esac; done
ARGS+=("$@")
printf '%s\n' "${ARGS[@]}" > "$OUT/argv.txt"
cd "$CODE"
PYTHONPATH="$CODE" python - "${ARGS[@]}" > "$OUT/run.log" 2>&1 <<'PY'
import sys, os
argv = sys.argv[1:]
i = argv.index("ecology")
import rabbitstew, rabbitstew.genetics as g
open(os.path.join(argv[argv.index("--out") + 1], "code.txt"), "w").write(
    f"rabbitstew {os.path.dirname(rabbitstew.__file__)} has_flag {hasattr(g.MutationConfig(), 'global_bias_sigma')}\n")
from rabbitstew.cli import main
sys.exit(main(argv[i:]))
PY
