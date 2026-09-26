#!/bin/bash
# RBT-100: smoke test of the C3 pipeline (RBT-92's tables.py and cull_k.py, runs/RBT-100/own_table.py and readout.py) on the
# throwaway runs of shared_baseline_runs.sh (20 seasons, event at 10), read for nothing and deleted.  As
# RBT-92's smoke.sh: plain is the baseline, the C3 shift run is the shift arm, the k = 20 cull run serves as
# RBT-92's cull20 arm and as C3's cull arm (with a cull-k file stating 20/20).  Windows are shrunk to fit 20
# seasons (RBT92_WINDOWS).  Scratch only; the structural lines are kept, every number is withheld.
#   runs/RBT-100/smoke.sh SEED [SEED ...]  > runs/RBT-100/smoke.txt
set -e
S=$(mktemp -d)
trap 'rm -rf "$S"' EXIT
mkdir -p "$S/base" "$S/c1" "$S/c3"
printf "seed\tT\n" > "$S/c1/onset.txt"
for SEED in "$@"; do
  D=runs/RBT-100/data
  cp -r "$D/sbc-plain-$SEED" "$S/base/forage-$SEED"
  cp -r "$D/sbc-shift-$SEED" "$S/c3/shift-$SEED"
  cp -r "$D/sbc-cull-$SEED" "$S/c1/cull20-$SEED"
  cp -r "$D/sbc-cull-$SEED" "$S/c3/cull-$SEED"
  printf "%s\t10\n" "$SEED" >> "$S/c1/onset.txt"
  python runs/RBT-92/tables.py "$S/base/forage-$SEED" > /dev/null
  python runs/RBT-92/tables.py "$S/base/forage-$SEED" --bodysig-only --to "$S/c1/base-$SEED" > /dev/null
  rm "$S/base/forage-$SEED/bodysig.txt"
  python runs/RBT-92/tables.py "$S/c3/shift-$SEED" > /dev/null
  python runs/RBT-92/tables.py "$S/c3/cull-$SEED" > /dev/null
  python runs/RBT-92/tables.py "$S/c1/cull20-$SEED" > /dev/null
  # Amendment 2: the own-net tables (F3) for the shift arm and the baseline, and a founders6 stand-in (F5; the plain
  # run serves, only to exercise the path)
  python runs/RBT-100/own_table.py "$S/c3/shift-$SEED" | sed "s#$S#<scratch>#"
  python runs/RBT-100/own_table.py "$S/base/forage-$SEED" --to "$S/c3/base-$SEED" | sed "s#$S#<scratch>#"
  rm -f "$S/base/forage-$SEED/own.txt"
  cp -r "$D/sbc-plain-$SEED" "$S/c3/founders6-$SEED"
  python runs/RBT-92/tables.py "$S/c3/founders6-$SEED" > /dev/null
  RBT92_BASELINE_DIR="$S/base" python - "$SEED" "$S" <<'PY' > "$S/c3/cull-k-$SEED.txt"
import sys, importlib.util
spec = importlib.util.spec_from_file_location("ck", "runs/RBT-92/cull_k.py"); ck = importlib.util.module_from_spec(spec); spec.loader.exec_module(ck)
ck.main(int(sys.argv[1]), f"{sys.argv[2]}/c3/shift-{sys.argv[1]}", T=10)
PY
  echo "RBT-92's cull_k.py on the throwaway C3 shift arm, seed $SEED: $(grep -c . "$S/c3/cull-k-$SEED.txt") lines, rule line present: $(grep -c '^cull' "$S/c3/cull-k-$SEED.txt")"
  printf "cull\tholistic=20,conventional=20\n" > "$S/c3/cull-k-$SEED.txt"
  LAST=$SEED
done
# the last seed exercises RBT-92 amendment 2's k = 0/0 path: no cull arm on disk, the null read as the baseline itself
rm -rf "$S/c3/cull-$LAST"
printf "cull\tholistic=0,conventional=0\n" > "$S/c3/cull-k-$LAST.txt"
echo "k = 0/0 path on seed $LAST: C3 cull arm removed"
set +e
RBT92_WINDOWS=5,3,4,3,2 RBT92_SEEDS="$*" RBT92_BASE_DIR="$S/base" RBT100_C1_DIR="$S/c1" RBT100_ARM_DIR="$S/c3" \
  python runs/RBT-100/readout.py > "$S/readout.txt" 2> "$S/err.txt"
status=$?
echo "runs/RBT-100/readout.py exit status: $status; $(wc -l < "$S/readout.txt") lines; stderr lines: $(wc -l < "$S/err.txt")"
[ -s "$S/err.txt" ] && tail -5 "$S/err.txt"
grep -c "the null is the baseline itself" "$S/readout.txt" | sed 's/^/readout lines naming the 0\/0 null: /'
echo "sections and gates printed (numbers withheld: throwaway runs, read for nothing):"
grep -E '^[A-Z][A-Z0-9 -]+|^  V[0-3]|^  C3-V1|FAIL|CLASS|CLAIM 3:|contrast sentence|below basal|echo|sentence:' "$S/readout.txt" | grep -vE '^ +[0-9]+[: ]' | sed -E 's/(^|[^A-Za-z0-9-])[-+]?[0-9]+(\.[0-9]+)?/\1#/g; s/\[[^]]*\]/[...]/g; s/HOLDS|FALSIFIED/<withheld>/'
