#!/usr/bin/env bash
# RBT-96 adversary, item 4: the build.  Salt 0 against the pre-salt code, a mutant the PR's tests
# miss, the golden test that catches it, and the full suite on the PR head and a trial merge.
#   runs/RBT-96/adversary/item4.sh [--suites]        (output: item4.txt beside this file)
# Needs a venv with the package's dependencies active.  Worktrees go in a temp directory.
set -uo pipefail
REPO=$(git rev-parse --show-toplevel)
HERE=$REPO/runs/RBT-96/adversary
BASE=852dcac   # merge-base of results/RBT-96 with claude/new-session-4cao7d: the code before the salt
HEAD_=3f7ccec  # the author's head
T=$(mktemp -d)
for w in base:$BASE head:$HEAD_ mut:$HEAD_; do git -C "$REPO" worktree add -q --detach "$T/${w%%:*}" "${w#*:}"; done
cleanup() { for w in base head mut merge; do git -C "$REPO" worktree remove --force "$T/$w" 2>/dev/null; done; }
trap cleanup EXIT
ARGS="--generations 6 --population 8 --duration 15 --mass-budget 15.34 --conventional-topology --brain-model rich --terrain random --champion-interval 5 --champions 2 --champion-mode roundrobin --seed 201 --workers 1"
run() { (cd "$T/$1" && PYTHONPATH=$PWD python -m rabbitstew.cli evolve $ARGS --out "$T/run-$1" > "$T/run-$1.log" 2>&1); }

echo "1. salt 0 (the default) on the PR head against the pre-salt code $BASE: seed 201, 6 generations, population 8"
run base; run head
for f in lineage.jsonl history.json; do cmp -s "$T/run-base/$f" "$T/run-head/$f" && echo "   $f byte-identical" || echo "   $f DIFFERS"; done
echo "   config.json differs only by: $(diff <(python -m json.tool "$T/run-base/config.json") <(python -m json.tool "$T/run-head/config.json") | grep '^>' | tr -s ' ' | tr '\n' ' ')"

echo "2. an old config.json (no holistic_stream_salt field) resumes on the PR head"
(cd "$T/head" && PYTHONPATH=$PWD python -m rabbitstew.cli evolve --resume --generations 8 --workers 1 --out "$T/run-base" > "$T/resume.log" 2>&1) && echo "   resume exit 0; $(tail -1 "$T/resume.log")"

echo "3. mutant: 'if holistic_salt:' -> 'if True:' (salt 0 re-spawned at spawn key (i, 0))"
sed -i 's/^    if holistic_salt:$/    if True:  # MUTANT/' "$T/mut/rabbitstew/evolution.py"
echo "   mutant diff: $(git -C "$T/mut" diff --stat | tail -1)"
run mut
cmp -s "$T/run-base/lineage.jsonl" "$T/run-mut/lineage.jsonl" && echo "   mutant salt-0 lineage identical to pre-salt (mutant is benign?)" || echo "   mutant salt-0 lineage DIFFERS from the pre-salt code: the mutant breaks every earlier run's reproducibility"
echo "   the PR's tests/test_rng_streams.py on the mutant: $(cd "$T/mut" && PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_rng_streams.py 2>&1 | tail -1)"

echo "4. the golden test ($HERE/test_salt0_golden.py)"
for w in head mut; do echo "   on $w: $(cd "$T/$w" && PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider "$HERE/test_salt0_golden.py" 2>&1 | tail -1)"; done
echo "   recorded draws on the pre-salt code: $(cd "$T/base" && PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider "$HERE/test_salt0_golden.py" -k recorded 2>&1 | tail -1)"

if [ "${1:-}" = "--suites" ]; then
  echo "5. full suite"
  echo "   PR head $HEAD_: $(cd "$T/head" && PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider 2>&1 | tail -1)"
  git -C "$REPO" worktree add -q --detach "$T/merge" "$HEAD_"
  (cd "$T/merge" && git -c user.email=adversary@example.invalid -c user.name=adversary merge -q --no-edit origin/claude/new-session-4cao7d >/dev/null 2>&1) && echo "   trial merge with origin/claude/new-session-4cao7d ($(git -C "$REPO" rev-parse --short origin/claude/new-session-4cao7d)): clean"
  echo "   trial merge: $(cd "$T/merge" && PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider 2>&1 | tail -1)"
  echo "   mutant, full suite: $(cd "$T/mut" && PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider 2>&1 | tail -1)"
fi
