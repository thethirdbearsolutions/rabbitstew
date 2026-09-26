#!/bin/bash
# RBT-105: smoke test of readout.py's rule on synthetic arms, before any arm.  Each "replicate" is a copy of its
# seed's committed RBT-90 part 2 files with a fabricated pairing.txt; then single files are swapped in to force
# each branch of the rule.  Nothing here is a result.
#
#   runs/RBT-105/smoke.sh SCRATCH  > runs/RBT-105/smoke.txt
set -e
S=$1/smoke-arms
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
mk() {  # mk SEED K SOURCE_SEED: an arm of SEED at K whose oscillator/lineage files are SOURCE_SEED's
  local d=$S/forage-$1-b$2; mkdir -p "$d"
  cp "$REPO/runs/RBT-90/forage-$3/"{oscillator.txt,lineage-last.txt,seasons.txt} "$d/"
  { echo "founders (genomes and ages at season 0) identical to the RBT-90 arm: True"
    echo "designed-body seasons.txt rows identical over the arm's 600 seasons: True"
    [ "$2" = 0 ] && { echo "positive control: seasons.txt byte-identical to the RBT-90 arm's committed file: True"
                      echo "positive control: lineage-last.txt byte-identical to the RBT-90 arm's committed file: True"; }
    true; } > "$d/pairing.txt"
}
base() { rm -rf "$S"; mk 7 0 7; for s in 7 805 4 807; do mk $s 1 $s; mk $s 2 $s; done; }
run() { echo "== case: $1"; RBT105_ARMS=$S python "$HERE/readout.py" | tail -1; }
base; run "every replicate equals its original (expect FOUNDING POPULATION)"
base; mk 7 1 4; run "seed 7 K=1 carries seed 4's acquired count (expect HISTORY on 1 of 4)"
base; mk 7 1 7; sed -i 's/"distinct": 2,/"distinct": 5,/' "$S/forage-7-b1/oscillator.txt"; run "seed 7 K=1 at 5, undecided (expect NOT DECIDED, wave 2 due)"
base; rm -rf "$S/forage-805-b2"; run "an arm missing (expect incomplete)"
base; sed -i 's/True/False/' "$S/forage-7-b0/pairing.txt"; run "positive control failed (expect INVALID)"
base; mk 7 1 4; echo "no holistic best at season 590" > "$S/forage-805-b1/EXTINCT.txt"; run "a flip and an extinct arm (expect HISTORY on 1 of 4)"
base; for s in 806 2 1 804; do mk $s 1 $s; mk $s 2 $s; done; run "wave 2 run, all replicate (expect FOUNDING POPULATION on 8)"
echo "== full readout, the all-replicate case"; base; RBT105_ARMS=$S python "$HERE/readout.py"
