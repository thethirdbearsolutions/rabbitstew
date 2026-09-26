#!/bin/bash
# RBT-92: smoke test of tables.py, cull_k.py and readout.py on throwaway runs, read for nothing and deleted.
# Uses the short runs of shared_baseline_runs.sh (20 seasons, event at 10) at the given seeds: plain as
# the baseline, shift as the shift arm, the k = 20 cull as both the cull20 arm and the cull arm (with a
# cull-k file stating 20/20). Windows are shrunk to fit 20 seasons (RBT92_WINDOWS). Everything is
# copied to a scratch directory and removed at the end; only the structural lines are kept.
#   runs/RBT-92/smoke.sh SEED [SEED ...]  > runs/RBT-92/smoke.txt
set -e
S=$(mktemp -d)
trap 'rm -rf "$S"' EXIT
mkdir -p "$S/base" "$S/arms"
printf "seed\tT\n" > "$S/onset.txt"
for SEED in "$@"; do
  D=runs/RBT-92/data
  cp -r "$D/sbc-plain-$SEED" "$S/base/forage-$SEED"
  cp -r "$D/sbc-shift-$SEED" "$S/arms/shift-$SEED"
  cp -r "$D/sbc-cull-$SEED" "$S/arms/cull20-$SEED"
  cp -r "$D/sbc-cull-$SEED" "$S/arms/cull-$SEED"
  printf "%s\t10\n" "$SEED" >> "$S/onset.txt"
  python runs/RBT-92/tables.py "$S/base/forage-$SEED" > /dev/null
  python runs/RBT-92/tables.py "$S/base/forage-$SEED" --bodysig-only --to "$S/arms/base-$SEED" > /dev/null
  rm "$S/base/forage-$SEED/bodysig.txt"
  for A in shift cull20 cull; do python runs/RBT-92/tables.py "$S/arms/$A-$SEED" > /dev/null; done
  cp "$S/onset.txt" "$S/arms/onset.txt"
  RBT92_BASELINE_DIR="$S/base" python - "$SEED" "$S" <<'PY' > "$S/arms/cull-k-$SEED.txt"
import sys, importlib.util
spec = importlib.util.spec_from_file_location("ck", "runs/RBT-92/cull_k.py"); ck = importlib.util.module_from_spec(spec); spec.loader.exec_module(ck)
ck.main(int(sys.argv[1]), f"{sys.argv[2]}/arms/shift-{sys.argv[1]}", T=10)
PY
  echo "cull_k.py on the throwaway shift arm, seed $SEED: $(grep -c . "$S/arms/cull-k-$SEED.txt") lines, rule line present: $(grep -c '^cull' "$S/arms/cull-k-$SEED.txt")"
  printf "cull\tholistic=20,conventional=20\n" > "$S/arms/cull-k-$SEED.txt"
done
set +e
RBT92_WINDOWS=5,3,4,3,2 RBT92_SEEDS="$*" RBT92_BASE_DIR="$S/base" RBT92_ARM_DIR="$S/arms" RBT92_ONSET="$S/onset.txt" \
  python runs/RBT-92/readout.py > "$S/readout.txt" 2> "$S/err.txt"
status=$?
echo "readout.py exit status: $status; $(wc -l < "$S/readout.txt") lines; stderr lines: $(wc -l < "$S/err.txt")"
[ -s "$S/err.txt" ] && tail -5 "$S/err.txt"
echo "sections and gates printed (numbers withheld: throwaway runs, read for nothing):"
grep -E '^[A-Z][A-Z -]+|^  V[0-3]|FAIL|CLASS' "$S/readout.txt" | sed -E 's/[-+]?[0-9]+\.[0-9]+/#/g; s/\[[^]]*\]/[...]/g'
