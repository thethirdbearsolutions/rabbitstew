#!/usr/bin/env bash
# RBT-103 adversary probes. Every row goes through the author's committed harness unchanged.
set -u
cd "$(dirname "$0")/../../.."
H=runs/RBT-103/routed_populations.py
O=runs/RBT-103/adversary
r() { out=$1; shift; [ -s "$O/$out.txt" ] && grep -q '^ROW' "$O/$out.txt" && return; python3 $H "$@" > "$O/$out.txt" 2>"$O/$out.err"; }
# 1. reproductions from scratch
r repro-P801-control --run runs/RBT-19/P-801 --label P-801-control
r repro-seed-805 --run runs/RBT-90/forage-805 --label 805
r repro-seed-1   --run runs/RBT-90/forage-1 --label 1
# 2. the missing cell: RBT-90 bodies in P-801's world
for s in 805 1 4 807 3 7 801 804 806 2; do
  r xworld-seed-$s-in-p801 --run runs/RBT-90/forage-$s --config-from runs/RBT-19/P-801 --label $s-in-p801-world
done
# 3. draw noise: a fresh seed block for both halves of the P-801 world move
r seedblock9000-P801-home   --run runs/RBT-19/P-801 --seed0 9000 --label P801-home-s9000
r seedblock9000-P801-rbt90  --run runs/RBT-19/P-801 --config-from runs/RBT-90/forage-805 --seed0 9000 --label P801-rbt90-s9000
# 4. which part of the world: P-801 bodies in one-factor-changed worlds
for w in dense-uniform sparse-patchy p801-instant-regrow; do
  r world-P801-in-$w --run runs/RBT-19/P-801 --config-from $O/worlds/$w --label P801-in-$w
done
echo ALLDONE > $O/.done
