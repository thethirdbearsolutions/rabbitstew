#!/bin/bash
# pip vs ONE patched venv, run in parallel, NSEAS merged seasons of one unit's M fork from ckpt60; prints sha-compare only.
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
run() {
  cp -a "$W/src/ckpt60" "$W/$1"
  ( cd "$ROOT" && RBT_HZN_STATS=$W/$1.hz NO_DURABLE=1 "$2/bin/python" -m rabbitstew.cli ecology --resume \
      --seasons $((60 + NSEAS)) --workers 1 --out "$W/$1" > /dev/null 2>"$W/$1.err" ); echo "$1 exit $? overflow_lines $(grep -c '^RBT_HZN overflow' $W/$1.err) $(cat $W/$1.hz 2>/dev/null)"
  (cd "$W/$1" && find . -type f ! -name run.log ! -name command.txt ! -name platform.json -print0 | sort -z | xargs -0 sha256sum) > "$W/$1.sha"
}
run pip "$PIP" > $W/pip.res & run log "$INS" > $W/log.res & wait
cat $W/pip.res $W/log.res
if cmp -s "$W/pip.sha" "$W/log.sha"; then echo "pip vs log: IDENTICAL ($(wc -l < $W/pip.sha) files)"; else echo "pip vs log: DIFFER in $(diff "$W/pip.sha" "$W/log.sha" | grep -c '^<') of $(wc -l < $W/pip.sha) files"; fi
rm -rf "$W"
