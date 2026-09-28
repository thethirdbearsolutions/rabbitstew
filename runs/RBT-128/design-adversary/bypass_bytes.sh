#!/bin/sh
# RBT-128 design adversary: does --unfair-i-know write nothing?  The same tiny evolve and ecology command lines, run on
# integration (626ca4c, before RBT-128, no flag) and on the PR tree (with --unfair-i-know); every output file is compared
# by sha256 (timing fields excluded by comparing only files that carry no wall-clock).
#   sh runs/RBT-128/design-adversary/bypass_bytes.sh <integration tree> <PR tree> <python> > .../bypass_bytes.txt
set -e
INTEG=$1; PR=$2; PY=$3; T=$(mktemp -d)
EVO="evolve --generations 2 --population 4 --champion-interval 1 --champions 1 --duration 0.2 --seed 5 --mass-budget 15.34 --work-cost 0.03"
ECO="ecology --seasons 2 --capacity 4 --group-size 2 --duration 0.2 --seed 5 --food-items 4 --brain-model foraging --challenge foraging"
(cd "$INTEG" && $PY -m rabbitstew.cli $EVO --workers 1 --out "$T/evo_old" >/dev/null && $PY -m rabbitstew.cli $ECO --workers 1 --out "$T/eco_old" >/dev/null)
(cd "$PR" && $PY -m rabbitstew.cli $EVO --workers 1 --unfair-i-know --out "$T/evo_new" >/dev/null && $PY -m rabbitstew.cli $ECO --workers 1 --unfair-i-know --out "$T/eco_new" >/dev/null)
for k in evo eco; do
  echo "## $k: files in old / new: $(ls "$T/${k}_old" | wc -l) / $(ls "$T/${k}_new" | wc -l)"
  for f in $(cd "$T/${k}_old" && find . -type f | sort); do
    a=$(sha256sum "$T/${k}_old/$f" | cut -c1-16); b=$(sha256sum "$T/${k}_new/$f" 2>/dev/null | cut -c1-16 || echo missing)
    if [ "$a" = "$b" ]; then echo "  same  $f"; else echo "  DIFF  $f"; fi
  done
done
rm -rf "$T"
