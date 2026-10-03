#!/bin/bash
# RBT-129 crash diagnosis: is a run byte-identical under (a) the pip libmujoco 3.14.0, (b) the source-built
# instrumented 3.14.0 with the guard OFF, (c) the same build with the guard ON?  One unit's M fork, NSEAS seasons
# from its ckpt60.  Prints only sha256 of each output file (never contents) and the exit codes; deletes the runs.
#   identity.sh PIP_VENV INSTR_VENV NSEAS POINT/SEED
set -u
PIP=$1; INS=$2; NSEAS=$3; u=$4
ROOT=$(git rev-parse --show-toplevel); point=${u%/*}; seed=${u#*/}; L=rbt-129-stage1-$point-$seed-ckpt60
git -C "$ROOT" fetch -q origin "+refs/heads/ckpt/$L:refs/remotes/origin/ckpt/$L"
W=$(mktemp -d); mkdir -p "$W/src"
for p in $(git -C "$ROOT" ls-tree --name-only "origin/ckpt/$L" | grep '^run.tar.gz.part' | sort); do
  git -C "$ROOT" cat-file blob "origin/ckpt/$L:$p" >> "$W/run.tgz"; done
tar -C "$W/src" -xzf "$W/run.tgz"; rm -f "$W/src/ckpt60"/.rbt129-done-*
"$PIP/bin/python" - "$W/src/ckpt60/config.json" <<'PY'
import json, sys
c = json.load(open(sys.argv[1])); c["ecology"].update({"merge_after": 60, "pooled_capacity": 120}); json.dump(c, open(sys.argv[1], "w"), indent=2)
PY
run() {  # name venv guard
  cp -a "$W/src/ckpt60" "$W/$1"
  ( cd "$ROOT" && RBT_HZN_GUARD=$3 RBT_HZN_STATS=$W/$1.hz NO_DURABLE=1 "$2/bin/python" -m rabbitstew.cli ecology --resume \
      --seasons $((60 + NSEAS)) --workers 1 --out "$W/$1" > /dev/null 2>&1 ); echo "$1 exit $? $(cat $W/$1.hz 2>/dev/null)"
  (cd "$W/$1" && find . -type f ! -name run.log ! -name command.txt ! -name platform.json -print0 | sort -z | xargs -0 sha256sum) > "$W/$1.sha"
}
run pip "$PIP" 0; run off "$INS" 0; run on "$INS" 1
for x in off on; do
  if cmp -s "$W/pip.sha" "$W/$x.sha"; then echo "pip vs $x: IDENTICAL ($(wc -l < $W/pip.sha) files)"; else echo "pip vs $x: DIFFER in $(diff "$W/pip.sha" "$W/$x.sha" | grep -c '^<') files"; fi
done
cmp -s "$W/off.sha" "$W/on.sha" && echo "off vs on: IDENTICAL" || echo "off vs on: DIFFER"
rm -rf "$W"
