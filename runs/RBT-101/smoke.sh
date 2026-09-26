#!/bin/bash
# RBT-101: smoke test of wiring.py and rewire.py on the throwaway start-seed runs (start_seed_runs.sh:
# 20 seasons, --shift terrain=flat at 10), read for nothing and deleted.  plain stands in for the baseline,
# flat for the shift arm and, again, for the cull arm; read points shrunk to T + 3, 6, 9; a stand-in
# control.txt line lets the verdict code run.  Only structural lines are kept, numbers withheld.
#   runs/RBT-101/smoke.sh SEED [SEED ...]  > runs/RBT-101/smoke.txt
set -e
S=$(mktemp -d)
trap 'rm -rf "$S"' EXIT
mkdir -p "$S/base" "$S/arms"
printf "seed\tT\n" > "$S/onset.txt"
for SEED in "$@"; do
  D=runs/RBT-101/data
  cp -r "$D/ssc-plain-$SEED" "$S/base/forage-$SEED"
  cp -r "$D/ssc-flat-$SEED" "$S/arms/shift-$SEED"
  cp -r "$D/ssc-flat-$SEED" "$S/arms/cull-$SEED"
  printf "%s\t10\n" "$SEED" >> "$S/onset.txt"
  python runs/RBT-92/tables.py "$S/base/forage-$SEED" > /dev/null
  python runs/RBT-101/wiring.py "$S/base/forage-$SEED" --to "$S/arms/base-$SEED" > /dev/null
  for A in shift cull; do python runs/RBT-92/tables.py "$S/arms/$A-$SEED" > /dev/null; python runs/RBT-101/wiring.py "$S/arms/$A-$SEED" > /dev/null; done
  echo "wiring.py, seed $SEED: $(($(wc -l < "$S/arms/shift-$SEED/wiring.txt") - 1)) rows in the shift arm's table; missing genomes: $(grep -c $'\t-\t' "$S/arms/shift-$SEED/wiring.txt" || true)"
done
echo "CONTROL n=$# PASS smoke-stand-in" > "$S/control.txt"
set +e
RBT101_SEEDS="$*" RBT101_BASE_DIR="$S/base" RBT101_ARM_DIR="$S/arms" RBT101_BASE_WIRING_DIR="$S/arms" RBT101_ONSET="$S/onset.txt" \
  RBT101_READ=3,6,9 RBT101_CONTROL="$S/control.txt" python runs/RBT-101/rewire.py > "$S/rewire.txt" 2> "$S/err.txt"
status=$?
echo "rewire.py exit status: $status; $(wc -l < "$S/rewire.txt") lines; stderr lines: $(wc -l < "$S/err.txt")"
[ -s "$S/err.txt" ] && tail -5 "$S/err.txt"
echo "sections, gates and verdict lines printed (numbers withheld: throwaway runs, read for nothing):"
grep -E '^[A-Z=]|^  (PASS|FAIL|C0|RE-WIRING)|VERDICT' "$S/rewire.txt" | sed -E 's/[-+]?[0-9]+\.[0-9]+/#/g; s/\[[^]]*\]/[...]/g; s/(VERDICT[^:]*:).*/\1 <withheld>/'
