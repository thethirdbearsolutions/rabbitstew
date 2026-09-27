#!/bin/bash
# RBT-104 readout adversary: POST HOC install-control probes. Every line runs runs/RBT-104/function.py
# UNCHANGED on a restored checkpoint (SCR/ck/ARM-SEED, from `scripts/durable.sh restore`) or on a
# synthetic host made by make_host.py (SCR/hosts/...). Output goes to readout-adversary/probes/, never
# into an arm directory.
#   runs/RBT-104/readout-adversary/probes.sh SCR [GROUP ...]
set -u
SCR=$1; shift
PY=${PY:-python}
O=runs/RBT-104/readout-adversary/probes
mkdir -p $O
fn() { # label run install
  [ -s "$O/$1.txt" ] && { echo "skip $1"; return; }
  $PY runs/RBT-104/function.py --run "$2" --install "$3" > "$O/$1.tmp" 2> "$O/$1.err" && mv "$O/$1.tmp" "$O/$1.txt"
  grep -h '^LINE' "$O/$1.txt" | sed "s/^/$1: /"; rm -f "$O/$1.err"
}
for grp in ${*:-R B C D E G}; do case $grp in
  R) # reproduce the committed install control from the checkpoint (fidelity)
     for a in S8-801 S1-801 S1-805; do fn R-$a-pc32 $SCR/ck/$a 32; done ;;
  B) # the registered control on SYNTHETIC S8 hosts: passing S1 hosts with every link x 8
     for a in S1-801 S1-4 S1-806; do fn B-$a-x8-pc32 $SCR/hosts/$a-x8 32; done ;;
  C) # the registered control on DESATURATED S8 hosts: failing S8 hosts with every link / 8
     for a in S8-801 S8-3 S8-806 S8-805 S8-1; do fn C-$a-d8-pc32 $SCR/hosts/$a-d8 32; done ;;
  D) # the control at the ARM'S reach on real failing S8 hosts: the a = 64 motif's links x 8 (input +-8, output 256)
     for a in S8-801 S8-3 S8-806 S8-805 S8-1; do fn D-$a-pc256x8 $SCR/ck/$a 256,8; done ;;
  E) # the arm-reach control on the synthetic S8 hosts
     for a in S1-801 S1-4 S1-806; do fn E-$a-x8-pc256x8 $SCR/hosts/$a-x8 256,8; done ;;
  G) # the planted geometry at founding (input +-8, output 8; a = 128) on real failing S8 hosts
     for a in S8-801 S8-3 S8-806; do fn G-$a-pc8x8 $SCR/ck/$a 8,8; done ;;
  H) # RBT-106 option H's risk: passing S1 hosts carrying a planted w = 32 compass (signed as the control),
     # its bias at 0, 0.1, 0.3 (the bias walk), then the registered control on top (make_host.py --plant)
     for a in S1-801 S1-806; do for b in 0 0.1 0.3; do fn H-$a-H32b$b-pc32 $SCR/hosts/$a-H32b$b 32; done; done ;;
esac; done
