#!/bin/bash
# RBT-101: smoke test of wiring.py, rewire.py and readout.sh on the throwaway start-seed runs (start_seed_runs.sh:
# 20 seasons, --shift terrain=flat at 10), read for nothing and deleted.  plain stands in for the baseline,
# flat for the shift arm and, again, for the cull arm; read points shrunk to T + 3, 6, 9; a stand-in
# control.txt line lets the verdict code run.  readout.sh (RBT-92's readout.py on staged links) is run on the
# k = 0/0 path (cull-k says 0/0, no cull arm, the null is the baseline), with flat standing in for RBT-92's cull20,
# windows shrunk as RBT-92's smoke test shrinks them.  Only structural lines are kept, numbers withheld.
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
printf "CONTROL-FAUNA n=%s holistic PASS smoke-stand-in\nCONTROL-FAUNA n=%s conventional PASS smoke-stand-in\n" $# $# > "$S/control.txt"
set +e
RBT101_SEEDS="$*" RBT101_BASE_DIR="$S/base" RBT101_ARM_DIR="$S/arms" RBT101_BASE_WIRING_DIR="$S/arms" RBT101_ONSET="$S/onset.txt" \
  RBT101_READ=3,6,9 RBT101_CONTROL="$S/control.txt" python runs/RBT-101/rewire.py > "$S/rewire.txt" 2> "$S/err.txt"
status=$?
echo "rewire.py exit status: $status; $(wc -l < "$S/rewire.txt") lines; stderr lines: $(wc -l < "$S/err.txt")"
[ -s "$S/err.txt" ] && tail -5 "$S/err.txt"
echo "sections, gates and verdict lines printed (numbers withheld: throwaway runs, read for nothing):"
grep -E '^[A-Z=]|^  (PASS|FAIL|C0|RE-WIRING)|VERDICT' "$S/rewire.txt" | sed -E 's/[-+]?[0-9]+\.[0-9]+/#/g; s/\[[^]]*\]/[...]/g; s/(VERDICT[^:]*:).*/\1 <withheld>/'
# readout.sh, k = 0/0 path: RBT-101's arms (shift, cull-k 0/0, no cull arm) and RBT-92's (cull20 stand-in, base digests)
mkdir -p "$S/r101" "$S/r92"
for SEED in "$@"; do
  cp -r "$S/arms/shift-$SEED" "$S/r101/shift-$SEED"
  printf "cull\tholistic=0,conventional=0\n" > "$S/r101/cull-k-$SEED.txt"
  cp -r "$S/arms/shift-$SEED" "$S/r92/cull20-$SEED"
  python runs/RBT-92/tables.py "$S/base/forage-$SEED" --bodysig-only --to "$S/r92/base-$SEED" > /dev/null
done
RBT101_ARM_DIR="$S/r101" RBT101_RBT92_DIR="$S/r92" RBT92_WINDOWS=5,3,4,3,2 RBT92_SEEDS="$*" RBT92_BASE_DIR="$S/base" \
  RBT92_ONSET="$S/onset.txt" runs/RBT-101/readout.sh > "$S/readout.txt" 2> "$S/err2.txt"
status=$?
echo "readout.sh exit status: $status; $(wc -l < "$S/readout.txt") lines; stderr lines: $(wc -l < "$S/err2.txt")"
[ -s "$S/err2.txt" ] && tail -5 "$S/err2.txt"
echo "k = 0/0 lines and section heads printed by RBT-92's readout.py (numbers withheld):"
grep -E '0/0|^[A-Z][A-Z -]+$|^[A-Z][A-Z ,-]+\(' "$S/readout.txt" | sed -E 's/[-+]?[0-9]+\.[0-9]+/#/g; s/\[[^]]*\]/[...]/g' | head -20
echo "validation failures (expected ONLY for the cull20 stand-in, which carries no cull; exit 1 is then expected):"
grep -E '^  (V[0-3]|FAIL)' "$S/readout.txt" | grep -vE '^  V[0-3] (pre-onset|manipulation|round|sensitivity)|^     ' | sed -E 's/[-+]?[0-9]+\.[0-9]+/#/g'
