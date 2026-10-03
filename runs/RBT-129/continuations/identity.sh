#!/bin/bash
# RBT-129 continuations: is a Stage-1 unit's continuation byte-identical under the stock pip libmujoco 3.14.0 and the
# instrumented build (scripts/build_mujoco_instrumented.sh)?  For each unit: its ckpt60 (a narrow fetch of that one
# branch), forked as ARM (S: as is; M: merge_after 60, pooled_capacity 120; N: the same with merge_null holistic on odd
# seeds, conventional on even, as stages.mn_units), then NSEAS seasons twice:
#   stock:  STOCK_VENV/bin/python -m rabbitstew.cli ecology --resume ...          (exactly what Stage 1 ran)
#   instr:  INSTR_VENV/bin/python runs/RBT-129/launch/epa_ecology.py --resume ...   (what a continuation runs)
# then the sha256 of every output file of the two, compared.  Excluded: run.log and command.txt (logs),
# platform.json (provenance: the instrumented run's carries mujoco_build) and epa_overflow.jsonl (the instrumented
# run's own log).  Prints file counts, IDENTICAL / DIFFER, and the EPA log's summary (near misses, overflows, the
# largest horizon) only: no output file is displayed.  The run directories are deleted at the end.
#
#   identity.sh STOCK_VENV INSTR_VENV NSEAS ARM:POINT/SEED [ARM:POINT/SEED ...]     e.g. M:c2-p030-U-G/129005
#
# Never the quarantined ckpt/rbt-129-stage1-c2-p030-U-G-129001-M (RULING.md item 3): only -ckpt60 branches are read.
set -u
STOCK=$1; INSTR=$2; NSEAS=$3; shift 3
ROOT=$(git rev-parse --show-toplevel)
WORKERS=${WORKERS:-2}
total=0; same=0
for spec in "$@"; do
  arm=${spec%%:*}; u=${spec#*:}; point=${u%/*}; seed=${u#*/}
  L=rbt-129-stage1-$point-$seed-ckpt60
  case "$L" in *129001-M*) echo "REFUSED: $L"; exit 2 ;; esac
  git -C "$ROOT" fetch -q origin "+refs/heads/ckpt/$L:refs/remotes/origin/ckpt/$L" || { echo "$spec fetch-failed"; continue; }
  W=$(mktemp -d); mkdir -p "$W/x"
  for p in $(git -C "$ROOT" ls-tree --name-only "origin/ckpt/$L" | grep '^run.tar.gz.part' | sort); do
    git -C "$ROOT" cat-file blob "origin/ckpt/$L:$p" >> "$W/run.tgz"; done
  tar -C "$W/x" -xzf "$W/run.tgz"; rm -f "$W/x/ckpt60"/.rbt129-done-*
  "$STOCK/bin/python" - "$W/x/ckpt60/config.json" "$arm" "$seed" <<'PY'
import json, sys
path, arm, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
c = json.load(open(path))
if arm in ("M", "N"):
    c["ecology"].update({"merge_after": 60, "pooled_capacity": 120})
if arm == "N":
    c["ecology"]["merge_null"] = "holistic" if (seed - 129000) % 2 else "conventional"
json.dump(c, open(path, "w"), indent=2)
PY
  cp -a "$W/x/ckpt60" "$W/stock"; cp -a "$W/x/ckpt60" "$W/instr"
  ( cd "$ROOT" && "$STOCK/bin/python" -m rabbitstew.cli ecology --resume --seasons $((60 + NSEAS)) --workers "$WORKERS" \
      --out "$W/stock" > /dev/null 2>&1 ); cs=$?
  ( cd "$ROOT" && "$INSTR/bin/python" runs/RBT-129/launch/epa_ecology.py --resume --seasons $((60 + NSEAS)) --workers "$WORKERS" \
      --out "$W/instr" > /dev/null 2>&1 ); ci=$?
  for b in x/ckpt60 stock instr; do
    (cd "$W/$b" && find . -type f ! -name run.log ! -name command.txt ! -name platform.json ! -name 'epa_overflow.jsonl*' \
       -print0 | sort -z | xargs -0 sha256sum) > "$W/$(basename $b).sha"
  done
  n=$(wc -l < "$W/stock.sha")
  # NOTE 15: how many of the compared files the run wrote or changed, and how many it carried unchanged from ckpt60
  carried=$(comm -12 <(sort "$W/ckpt60.sha") <(sort "$W/stock.sha") | wc -l)
  split="$((n - carried)) written or changed by the run + $carried carried unchanged from ckpt60"
  if cmp -s "$W/stock.sha" "$W/instr.sha"; then v=IDENTICAL; else v="DIFFER in $(diff "$W/stock.sha" "$W/instr.sha" | grep -c '^<') files"; fi
  epa=$("$INSTR/bin/python" - "$W/instr/epa_overflow.jsonl" "$ROOT" <<'PY'
import sys
sys.path.insert(0, sys.argv[2] + "/runs/RBT-129/launch")
import epa_ecology
r = epa_ecology.read_log(sys.argv[1])
print(f"epa: near(>=17) {r['near']} overflow {r['overflow']} max_horizon {r['max_nedges']} epa_iterations {r['epa_iterations']}")
PY
)
  b=$("$INSTR/bin/python" -c "import json; print(json.load(open('$W/instr/platform.json'))['resumes'][-1]['mujoco_build']['libmujoco_sha256'][:12])")
  echo "$arm:$point/$seed seasons 60-$((59 + NSEAS)) exit stock $cs instr $ci | $n files ($split) | stock vs instr: $v | instr platform.json mujoco_build $b... | $epa"
  total=$((total + 1)); [ "$v" = IDENTICAL ] && [ "$cs" = 0 ] && [ "$ci" = 0 ] && same=$((same + 1))
  rm -rf "$W"
done
echo "identity: $same/$total units IDENTICAL"
