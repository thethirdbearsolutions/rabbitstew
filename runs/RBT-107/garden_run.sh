#!/bin/bash
# RBT-107: the common-garden populations, one file per population, into runs/RBT-107/garden/ (kilobytes each; committed).
#
#   WORKERS=4 runs/RBT-107/garden_run.sh readout SEED     after the seed's extended arms have ended, their bulk on disk
#                                                         (restore ckpt/rbt-107-ARM-SEED if the container is new):
#                                                           c0-SEED-KIND              C0 (alive at T-1), from the base arm
#                                                           ARM-SEED-KIND-dD          ARM in base shift cull20 (and cull where
#                                                                                     it ran), D in 110 200 400 600 800
#                                                         into garden/readout/, on 16 worlds (Amendment 1); the design stage's
#                                                         8-world files stay in garden/ and are never read by readout.py
#   WORKERS=4 runs/RBT-107/garden_run.sh design SEED DIR  the design-stage measurement (PREREGISTRATION section 4), from
#                                                         restored 600-season checkpoints in DIR (base-SEED, cull20-SEED):
#                                                           c0-SEED-KIND, base-SEED-KIND-s599, cull20-SEED-KIND-s599
#                                                         No shift arm is read.
#   WORKERS=4 runs/RBT-107/garden_run.sh c2control SEED DIR   the positive control (PREREGISTRATION section 6): RBT-90 base
#                                                         (DIR/base-SEED) and RBT-99's C2 shift arm (DIR/c2shift-SEED,
#                                                         from ckpt/rbt-99-shift-SEED) at 599, both at work_cost 0.08
#   WORKERS=4 runs/RBT-107/garden_run.sh aa105 SEED K DIR RBT-105's replicate forage-SEED-bK in DIR, holistic, season 599:
#                                                           aa105-SEED-bK-holistic-s599  (report-only depth-matched A/A)
# A population file that already exists is skipped, so a lost container resumes where it stopped.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
cd "$REPO"
case "$1" in readout|aa105) OUTD=${GARDEN_OUT:-$HERE/garden/readout} ;; *) OUTD=${GARDEN_OUT:-$HERE/garden} ;; esac
mkdir -p "$OUTD"
W=${WORKERS:-1}
MODE=$1; SEED=$2
T=$(cat runs/RBT-92/onset.txt runs/RBT-107/onset-new-*.txt 2>/dev/null | awk -v s="$SEED" '$1 == s && $2 ~ /^[0-9]+$/ {print $2; exit}')
[ -n "$T" ] || { echo "no onset for seed $SEED" >&2; exit 2; }
unit() {  # RUN KIND SEASON LABEL [garden.py options]
  local f="$OUTD/$4.txt"
  [ -s "$f" ] && { echo "have $4"; return 0; }
  python "$HERE/garden.py" "$1" "$2" "$3" "$4" --workers "$W" "${@:5}" > "$f.part" && mv "$f.part" "$f"
  echo "wrote $4 ($(head -1 "$f" | grep -o '([0-9]* s'))"
}
case "$MODE" in
  readout)
    for K in holistic conventional; do
      unit "runs/RBT-107/base-$SEED" $K $((T - 1)) "c0-$SEED-$K" --draws 16
      for D in 800 110 400 600 200; do
        for A in shift base cull20 cull; do
          [ -d "runs/RBT-107/$A-$SEED" ] && unit "runs/RBT-107/$A-$SEED" $K $((T + D)) "$A-$SEED-$K-d$D" --draws 16
        done
      done
    done ;;
  design)
    DIR=$3
    for K in holistic conventional; do
      unit "$DIR/base-$SEED" $K $((T - 1)) "c0-$SEED-$K"
      unit "$DIR/base-$SEED" $K 599 "base-$SEED-$K-s599"
      unit "$DIR/cull20-$SEED" $K 599 "cull20-$SEED-$K-s599"
    done ;;
  c2control)
    DIR=$3
    for K in holistic conventional; do
      unit "$DIR/base-$SEED" $K 599 "c2base-$SEED-$K-s599" --work-cost 0.08
      unit "$DIR/c2shift-$SEED" $K 599 "c2shift-$SEED-$K-s599" --work-cost 0.08
    done ;;
  aa105)
    K=$3; DIR=$4
    unit "$DIR/forage-$SEED-b$K" holistic 599 "aa105-$SEED-b$K-holistic-s599" --draws 16
    unit "runs/RBT-107/base-$SEED" holistic 599 "base-$SEED-holistic-s599" --draws 16 ;;  # the original, same 16 worlds
  *) sed -n 2,17p "$0"; exit 2 ;;
esac
