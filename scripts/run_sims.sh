#!/bin/bash
# Sims-budget run: population 300, (mu+lambda) survival, epsilon-lexicase, neighbour
# links, mirrored connections; random terrain resampled every generation, bouts from
# rest, equal mass, the fixed body's controller topology free to evolve.
#
# usage: run_sims.sh SEED [GENERATIONS] [EXTRA...]
#   env: NAME POP DURATION WORKERS DRAWS CURRICULUM BRAIN CHAMPION_INTERVAL override the defaults
#   defaults match the RBT-11 / RBT-5 package: 2 draws, heading curriculum 100, no champion bouts
#
# The score is closeness (progress integrated over the bout) evaluated SOLO for the
# whole run, which is why --locomotion-phase is pinned to the run's length.  Champion
# bouts still run at the checkpoint interval, but as a measurement only: nothing a
# bout returns feeds selection.  That is deliberate, and it is the one place this
# script departs from the older bout-scored runs.  Paper 3 measured realised
# heritability of 0.05 or less on the holistic side under a zero-sum bout at one, two
# and four bouts per individual, and 0.35 to 0.41 for the same dense score used solo;
# averaging more bout draws does not move it, because the noise is not draw-to-draw
# variance.  Scoring 300 individuals through a format with no heritable signal would
# spend the whole budget on drift.  To score bouts anyway, pass --locomotion-phase 0.
set -eu
seed=$1; generations=${2:-100}; shift $(( $# > 1 ? 2 : 1 )); extra="$@"
name=${NAME:-sims}
pop=${POP:-300}
mkdir -p runs
rabbitstew evolve --population $pop --generations $generations \
  --survival --selection lexicase --mirror --neighbour-links \
  --score closeness --locomotion-phase $generations \
  --terrain random --random-start --mass-budget 15.34 --conventional-topology \
  --brain-model ${BRAIN:-rich} --duration ${DURATION:-15} --draws ${DRAWS:-2} --heading-curriculum ${CURRICULUM:-100} \
  --champion-interval ${CHAMPION_INTERVAL:-0} --workers ${WORKERS:-$(nproc)} \
  --seed $seed $extra --out runs/$name-$seed > runs/$name-$seed.log 2>&1
