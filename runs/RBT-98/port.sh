#!/bin/sh
# RBT-98: port every missing claim-bearing file named in rows.txt onto the current branch,
# byte for byte from the source branch's head, one commit per source branch naming that
# commit. Branches that are the same commit under two names (the table says which) are
# ported once. Run from the repository root after audit.py has written rows.txt.
set -eu
rows=runs/RBT-98/rows.txt
done_heads=""
for br in $(cut -f1 "$rows" | awk '!seen[$0]++'); do
  head=$(git rev-parse "origin/$br")
  case " $done_heads " in *" $head "*) continue;; esac
  done_heads="$done_heads $head"
  n=0
  awk -F'\t' -v b="$br" '$1==b && $7!="-"{print $5"\t"$7}' "$rows" > /tmp/rbt98-port.$$
  while IFS="$(printf '\t')" read -r src dest; do
    mkdir -p "$(dirname "$dest")"
    git cat-file blob "$head:$src" > "$dest"
    git add "$dest"
    n=$((n + 1))
  done < /tmp/rbt98-port.$$
  rm -f /tmp/rbt98-port.$$
  [ "$n" -gt 0 ] || continue
  git commit -q -F - <<MSG
RBT-98: port $n stranded evidence files from $br

Source commit $head ($br), never merged to integration. Reports, readouts, scripts,
configs and per-season summaries only; no bulk. Files the allowlist does not admit under
their own name (.json/.log readouts) are ported byte for byte as NAME.txt.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01UtpjSw8nZcTk2WJHCFxLu4
MSG
  echo "$br $n"
done
