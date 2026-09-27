#!/bin/bash
# RBT-107 H1 compute shard: WORKERS=4 runs/RBT-107/h1/h1_shard.sh SHARD NSHARD
# runs h1_run.sh for every fresh seed 11..30 whose index (seed - 11) is SHARD mod NSHARD.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
for s in $(seq 11 30); do
  if [ $(( (s - 11) % $2 )) -eq "$1" ]; then "$HERE/h1_run.sh" "$s"; fi
done
echo "H1-SHARD-DONE $1/$2"
