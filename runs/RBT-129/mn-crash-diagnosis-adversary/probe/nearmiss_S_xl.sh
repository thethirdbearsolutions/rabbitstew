#!/bin/bash
# RBT-129 crash diagnosis (d): EPA horizon sizes in other Stage-1 M forks, from their ckpt60, for the first NSEAS
# merged seasons, under the instrumented libmujoco (mujoco-3.14.0-epa-horizon.patch, guard OFF = stock logic).
# Keeps ONLY the horizon histogram line and the exit code; the run directory and its logs are deleted unread.
#   nearmiss.sh VENV OUTFILE NSEAS POINT/SEED [POINT/SEED ...]
set -u
VENV=$1; OUT=$2; NSEAS=$3; shift 3
ROOT=$(git rev-parse --show-toplevel)
"$VENV/bin/python" -c 'import mujoco; assert mujoco.__version__ == "3.14.0"' || exit 2
for u in "$@"; do
  point=${u%/*}; seed=${u#*/}; L=rbt-129-stage1-$point-$seed-ckpt60
  git -C "$ROOT" fetch -q origin "+refs/heads/ckpt/$L:refs/remotes/origin/ckpt/$L" || { echo "$u fetch-failed" >> "$OUT"; continue; }
  W=$(mktemp -d); mkdir -p "$W/x"
  for p in $(git -C "$ROOT" ls-tree --name-only "origin/ckpt/$L" | grep '^run.tar.gz.part' | sort); do
    git -C "$ROOT" cat-file blob "origin/ckpt/$L:$p" >> "$W/run.tgz"; done
  tar -C "$W/x" -xzf "$W/run.tgz"; D=$W/x/ckpt60; rm -f "$D"/.rbt129-done-*
  ( cd "$ROOT" && RBT_HZN_STATS=$W/hz NO_DURABLE=1 timeout -k 30 14000 "$VENV/bin/python" -m rabbitstew.cli ecology --resume \
      --seasons $((60 + NSEAS)) --workers 1 --out "$D" > /dev/null 2> "$W/err" ); code=$?
  over=$(grep -c '^RBT_HZN overflow' "$W/err")
  echo "$u S exit $code overflow_lines $over $(cat "$W/hz" 2>/dev/null)" >> "$OUT"
  rm -rf "$W"
done
