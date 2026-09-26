#!/usr/bin/env bash
# RBT-107 item 2: does every checkpoint an extension would resume from hold all 600 seasons, and is it consistent?
#   runs/RBT-107/ckpt_check.sh > runs/RBT-107/ckpt_check.txt
# Reads each ckpt/LABEL's MANIFEST (name, seasons done/target, time, consistency note) and its commit. No bulk is read;
# restorability is shown separately by extend_check.sh on real checkpoints.
set -uo pipefail
SEEDS="801 804 805 806 807 1 2 3 4 7"
labels=""
for s in $SEEDS; do labels+=" rbt-90-$s rbt-101-shift-$s"; done
for s in $SEEDS; do labels+=" rbt-101-cull-$s"; done
for s in $SEEDS; do labels+=" rbt-92-cull20-$s"; done
printf 'label\tcommit\tdir\tseasons\tsaved\tnote\n'
for l in $labels; do
    if ! git fetch -q origin "+refs/heads/ckpt/$l:refs/remotes/origin/ckpt/$l" 2>/dev/null; then
        printf '%s\t-\t-\tABSENT\t-\t-\n' "$l"; continue
    fi
    m="$(git show "origin/ckpt/$l:MANIFEST")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$l" "$(git rev-parse --short origin/ckpt/$l)" \
        "$(sed -n 1p <<<"$m")" "$(sed -n 2p <<<"$m")" "$(sed -n 3p <<<"$m")" "$(sed -n 4p <<<"$m" | sed 's/^$/consistent (pre-note format)/')"
done
