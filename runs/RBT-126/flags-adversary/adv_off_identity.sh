#!/bin/bash
# RBT-126 flags adversary, probe 1: off is byte-identical beyond the PR's goldens.
# Runs the same small CLI ecologies on two trees (the code before the flags, 3503cc2, and the flags head or a trial
# merge) and compares every file each run writes.  Configs the PR's goldens do not cover: a merge, a cull, a shift,
# a replicate breed stream, a neutral arm with a merge, persistent food; each with the flags absent and named at
# their defaults.
# Usage: adv_off_identity.sh PY_BASE PY_NEW OUT_DIR    (PY_*: the python of a venv with that tree installed -e)
set -u
PYB=$1; PYN=$2; OUT=$3
C="ecology --seasons 6 --max-age 4 --capacity 6 --challenge foraging --group-size 2 --duration 0.5 --seed 7 --living-cost 0.25 --initial-energy 3 --birth-threshold 2"
declare -A CFG=(
  [merge]="$C --merge-after 2"
  [cull]="$C --cull-at 3 --cull 1"
  [shift]="$C --shift-at 3 --shift group_size=3"
  [stream]="$C --breed-stream 2"
  [neutral_merge]="ecology --seasons 6 --max-age 4 --capacity 6 --challenge foraging --group-size 2 --duration 0.5 --seed 7 --neutral --initial-energy 3 --merge-after 3"
  [regrow]="$C --regrow-delay 2"
)
fail=0
for k in "${!CFG[@]}"; do
  $PYB -m rabbitstew.cli ${CFG[$k]} --out $OUT/base/$k >/dev/null 2>&1 || echo "base $k failed"
  $PYN -m rabbitstew.cli ${CFG[$k]} --out $OUT/new/$k >/dev/null 2>&1 || echo "new $k failed"
  $PYN -m rabbitstew.cli ${CFG[$k]} --breed-rule shuffle --breed-gate energy --out $OUT/newx/$k >/dev/null 2>&1 || echo "newx $k failed"
  for v in new newx; do
    for f in $(cd $OUT/base/$k && find . -type f | sort); do
      if ! cmp -s $OUT/base/$k/$f $OUT/$v/$k/$f; then echo "DIFF $v $k $f"; fail=1; fi
    done
    extra=$(cd $OUT/$v/$k && find . -type f | sort | while read f; do [ -f $OUT/base/$k/$f ] || echo $f; done)
    [ -n "$extra" ] && { echo "EXTRA FILES $v $k: $extra"; fail=1; }
  done
  echo "$k: $(cd $OUT/base/$k && find . -type f | wc -l) files compared ($(cd $OUT/base/$k && ls | tr '\n' ' '))"
done
[ $fail = 0 ] && echo "ALL IDENTICAL" || echo "DIFFERENCES FOUND"
