#!/bin/bash
# RBT-105: smoke test of readout.py's rules (R1 primary, R2 secondary, R0 reported) on synthetic arms, before any arm.
# Each "replicate" is a copy of a seed's committed RBT-90 part 2 files, with its osc_births.txt taken from
# osc-births-rbt90.txt and a fabricated pairing.txt; single arms are then swapped for another seed's files to force
# each branch.  Nothing here is a result.  aa_spread.py is run on the all-replicate case (every spread 0 by construction).
#
#   runs/RBT-105/smoke.sh SCRATCH  > runs/RBT-105/smoke.txt
set -e
S=$1/smoke-arms
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
SEEDS="7 805 4 807 806 2 1 804"
mk() {  # mk SEED K SOURCE_SEED: an arm of SEED at K whose files are SOURCE_SEED's
  local d=$S/forage-$1-b$2; rm -rf "$d"; mkdir -p "$d"
  cp "$REPO/runs/RBT-90/forage-$3/"{oscillator.txt,lineage-last.txt,seasons.txt} "$d/"
  awk -v s="forage-$3 " 'index($0, s) == 1 {on = 1} on && /^\{/ {print; exit}' "$HERE/osc-births-rbt90.txt" > "$d/osc_births.txt"
  { echo "founders (genomes and ages at season 0) identical to the RBT-90 arm: True"
    echo "designed-body seasons.txt rows identical over the arm's 600 seasons: True"
    [ "$2" = 0 ] && { echo "positive control: seasons.txt byte-identical to the RBT-90 arm's committed file: True"
                      echo "positive control: lineage-last.txt byte-identical to the RBT-90 arm's committed file: True"; }
    true; } > "$d/pairing.txt"
}
base() { rm -rf "$S"; mk 7 0 7; for s in $SEEDS; do mk $s 1 $s; mk $s 2 $s; done; }
run() { echo "== case: $1"; RBT105_ARMS=$S python "$HERE/readout.py" | grep -E "^(flips|verdict|R1|R2|R0)"; echo; }
base; run "every replicate equals its original (expect R1 FOUNDERS DOMINANT, F = 0 of 16, q >= 0.17 excluded; R2 fires; R0 FOUNDING)"
base; mk 7 1 4; run "one flip: seed 7 K=1 carries seed 4's files (expect R1 FOUNDERS DOMINANT at F = 1; R0 HISTORY, q > 0 only)"
base; mk 7 1 4; mk 805 1 807; mk 4 1 7; run "three flips in 16 (expect R1 FOUNDERS DOMINANT: at n = 16 the bars meet, F <= 4 or F >= 5)"
base; mk 7 1 4; mk 805 1 807; mk 4 1 7; for a in 806-b1 806-b2 2-b1 2-b2; do sed -i 's/"distinct": [0-9]*,/"distinct": 5,/' "$S/forage-$a/oscillator.txt"; done
run "three flips, four replicates undecided (n = 12: expect R1 NOT DECIDED, between F <= 2 and F >= 4)"
base; mk 7 1 4; mk 805 1 807; mk 4 1 7; mk 807 2 805; mk 1 1 2; run "five flips (expect R1 SUBSTANTIAL HISTORY)"
base; for s in $SEEDS; do mk $s 1 7; mk $s 2 4; done; run "every seed's replicates are one discarded and one acquired (expect R1 SUBSTANTIAL HISTORY, F = 8; R2 not shown)"
base; sed -i 's/"distinct": 2,/"distinct": 5,/' "$S/forage-7-b1/oscillator.txt"; run "seed 7 K=1 at 5, undecided (expect n = 15)"
base; rm -rf "$S/forage-805-b2"; run "an arm missing (expect incomplete)"
base; sed -i 's/True/False/' "$S/forage-7-b0/pairing.txt"; run "positive control failed (expect INVALID)"
echo "== full readout, the all-replicate case"; base; RBT105_ARMS=$S python "$HERE/readout.py"
echo; echo "== aa_spread.py on the all-replicate case (every spread 0: the replicates are the originals' files)"; python "$HERE/aa_spread.py" "$S" | tail -14
