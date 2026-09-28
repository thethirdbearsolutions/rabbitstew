#!/bin/bash
# Launch-adversary probe L3: is PR #435's cli.py refactor byte-identical?  The same tiny non-sweep ecology command
# lines on the base tree (integration 626ca4c) and on PR #435 (4464a4e); every output file compared byte for byte
# (run.log/command lines aside).  Three cases: a fresh run, a run with a merge, and a resume.
# usage: probe_launch_cli.sh BASE_TREE PR_TREE OUTDIR
set -u
BASE=$1; PR=$2; OUT=$3; mkdir -p $OUT
TINY="--capacity 4 --challenge foraging --group-size 2 --brain-model foraging --food-items 4 --duration 0.4 --terrain flat --conventional-topology --score food --living-cost 0.05 --initial-energy 2 --birth-threshold 0.5 --birth-cost 0.2 --max-age 6"
for tree in base pr; do
  T=$BASE; [ $tree = pr ] && T=$PR
  (cd $T && PYTHONPATH=$T python -m rabbitstew.cli ecology $TINY --seed 5 --seasons 4 --workers 1 --out $OUT/$tree-fresh >/dev/null 2>&1; echo "$tree fresh exit $?")
  (cd $T && PYTHONPATH=$T python -m rabbitstew.cli ecology $TINY --merge-after 2 --seed 6 --seasons 4 --workers 1 --out $OUT/$tree-merge >/dev/null 2>&1; echo "$tree merge exit $?")
  (cd $T && PYTHONPATH=$T python -m rabbitstew.cli ecology $TINY --sweep-log --seed 7 --seasons 2 --workers 1 --out $OUT/$tree-res >/dev/null 2>&1 && PYTHONPATH=$T python -m rabbitstew.cli ecology --resume --seasons 4 --out $OUT/$tree-res >/dev/null 2>&1; echo "$tree resume exit $?")
done
for c in fresh merge res; do
  n=0; bad=0
  for f in $(cd $OUT/base-$c && find . -type f | sort); do
    n=$((n+1)); cmp -s $OUT/base-$c/$f $OUT/pr-$c/$f || { bad=$((bad+1)); echo "   DIFFERS: $c $f"; }
  done
  extra=$(cd $OUT/pr-$c && find . -type f | sort | wc -l)
  echo "$c: $n files in base, $extra in PR, $bad differ"
done
