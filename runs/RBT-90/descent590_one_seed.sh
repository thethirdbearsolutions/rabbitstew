#!/usr/bin/env bash
# One seed of the RBT-90 supplementary descent pass (coordinator's 14:25 ruling on the descent.py seam):
# restore the arm from ckpt/rbt-90-SEED, identify the individual saved as holistic/best_gen0590.json and
# check it against the season-590 best-fitness holistic row of lineage.jsonl and history.json's best_name,
# trace its DAG with RBT-84's descent.py (unmodified) into forage-SEED/descent-590.txt, then delete the bulk.
#
#   SCRATCH=/some/scratch runs/RBT-90/descent590_one_seed.sh SEED
#
# The arm is restored under SCRATCH/root/runs/RBT-90/forage-SEED and descent.py is run from SCRATCH/root, so
# the readout's header names runs/RBT-90/forage-SEED exactly as the pre-registered descent.txt does. As a check
# on the restore, the unnamed call is re-run and compared byte for byte with the committed descent.txt.
set -euo pipefail
SEED=$1
REPO=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
SP=${SCRATCH:?set SCRATCH to a scratch directory}
ROOTX=$SP/root
RUN=runs/RBT-90/forage-$SEED
rm -rf "$ROOTX/$RUN"; mkdir -p "$ROOTX/runs/RBT-90"
(cd $REPO && scripts/durable.sh restore "$ROOTX/$RUN" rbt-90-$SEED)
cd "$ROOTX"
python - "$RUN" > "$SP/identify-$SEED.txt" <<'PY'
import json, sys
run = sys.argv[1]
name = json.load(open(f"{run}/holistic/best_gen0590.json"))["name"]
rows = [json.loads(l) for l in open(f"{run}/lineage.jsonl") if l.strip()]
s590 = [r for r in rows if r["population"] == "holistic" and r["generation"] == 590]
top = max(r["fitness"] for r in s590)
tops = [r["name"] for r in s590 if r["fitness"] == top]
hist = json.load(open(f"{run}/history.json"))["history"]
hb = [e["best_name"] for e in hist if e["season"] == 590 and e["population"] == "holistic"]
last = max(r["generation"] for r in rows if r["population"] == "holistic")
s599 = [r for r in rows if r["population"] == "holistic" and r["generation"] == last]
b599 = max(s599, key=lambda r: r["fitness"])["name"]
agree = tops == [name]
print(json.dumps({"best_gen0590": name, "lineage_590_top": tops, "lineage_590_top_fitness": top,
                  "history_590_best": hb, "agree": agree and hb == [name], "season_last": last,
                  "best_last": b599}))
PY
cat "$SP/identify-$SEED.txt"
{ printf "%s\t" "$SEED"; cat "$SP/identify-$SEED.txt"; } >> "$REPO/runs/RBT-90/descent-590-identify.txt"
NAME=$(python -c "import json,sys;print(json.load(open('$SP/identify-$SEED.txt'))['best_gen0590'])")
python $REPO/runs/RBT-84/descent.py $RUN holistic "$NAME" > "$REPO/$RUN/descent-590.txt"
# sanity: the unnamed call on the restored bulk must reproduce the committed descent.txt
python $REPO/runs/RBT-84/descent.py $RUN holistic > "$SP/descent-unnamed-$SEED.txt"
if cmp -s "$SP/descent-unnamed-$SEED.txt" "$REPO/$RUN/descent.txt"; then r="identical"; else r="DIFFERS"; fi
echo "unnamed re-run vs committed descent.txt: $r"
printf "%s\tunnamed re-run vs committed descent.txt: %s\n" "$SEED" "$r" >> "$REPO/runs/RBT-90/descent-590-identify.txt"
tail -2 "$REPO/$RUN/descent-590.txt"
rm -rf "$ROOTX/$RUN"
