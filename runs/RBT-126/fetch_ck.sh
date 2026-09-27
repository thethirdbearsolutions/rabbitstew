#!/bin/bash
# RBT-126: restore lineage.jsonl, seasons.txt, config.json and event.txt from the corpus's checkpoint branches
# (origin ckpt/rbt-<n>-<arm>: MANIFEST + run.tar.gz.part*) into CK_DIR/rbt-<n>-<arm>/<arm>/.
# Usage: bash runs/RBT-126/fetch_ck.sh CK_DIR   (from the repository root; about 3 GB of fetches, resumable)
CK=${1:?usage: fetch_ck.sh CK_DIR}
for b in $(git ls-remote --heads origin 'ckpt/*' | awk '{print $2}' | sed 's|refs/heads/||' | grep -E '^ckpt/rbt-(90|99|100|101|104|105|106|107|112)-'); do
  d=$CK/${b#ckpt/}
  [ -f $d/DONE ] && continue
  mkdir -p $d
  for i in 1 2 3 4; do git fetch -q --depth 1 origin "$b" 2>/dev/null && break; sleep $((2**i)); done
  git show FETCH_HEAD:MANIFEST > $d/MANIFEST
  parts=$(git ls-tree --name-only FETCH_HEAD | grep run.tar.gz.part | sort)
  (for p in $parts; do git show FETCH_HEAD:$p; done) | tar xzf - -C $d --wildcards '*/lineage.jsonl' '*/seasons.txt' '*/config.json' '*/event.txt' 2>$d/tar.err
  touch $d/DONE
  echo "$b $(du -sh $d | cut -f1)"
done
echo ALLDONE
