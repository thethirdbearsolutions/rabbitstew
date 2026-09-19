#!/bin/bash
# Adversary re-derivations for RBT-85, run from a clean checkout of the integration head.
#
# 1. readout.py --from-summaries regenerated and diffed against the committed readout-from-summaries.txt.
# 2. The pinning test made to fail on the broken code: spawn_streams' three generators replaced by
#    one generator handed out three times, the named test run, then the file restored with git.
# 3. adversary_stats.py: the resolution triple and the t(3) figures recomputed from generations.txt.
#
# usage: bash runs/RBT-85/adversary_rederive.sh    (writes docs/runs/RBT-85-adversary-rederive.txt)
set -u
OUT=docs/runs/RBT-85-adversary-rederive.txt
mkdir -p docs/runs
{
  echo "head: $(git rev-parse --short HEAD)   $(date -u +%Y-%m-%dT%H:%MZ)"
  echo
  echo "=== 1. readout.py --from-summaries against the committed readout ==="
  python runs/RBT-85/readout.py runs/RBT-85 --from-summaries > /tmp/rbt85-rederived.txt 2>/dev/null
  if diff -q /tmp/rbt85-rederived.txt runs/RBT-85/readout-from-summaries.txt > /dev/null; then
    echo "IDENTICAL: the four differences, mean, SE, verdict, paired/unpaired SEs, correlation and the resolution triple regenerate byte for byte from generations.txt"
  else
    echo "DIFFERS:"; diff /tmp/rbt85-rederived.txt runs/RBT-85/readout-from-summaries.txt | head -20
  fi
  echo
  echo "=== 2. the pinning test on the broken code (one generator handed out three times) ==="
  python - <<'EOF'
p = "rabbitstew/evolution.py"
s = open(p).read()
old = "    return {name: np.random.default_rng(ss) for name, ss in zip(STREAMS, np.random.SeedSequence(seed).spawn(len(STREAMS)))}"
assert old in s, "spawn_streams body not found; the breakage no longer applies"
open(p, "w").write(s.replace(old, "    _one = np.random.default_rng(seed)  # BROKEN ON PURPOSE\n    return {name: _one for name in STREAMS}"))
EOF
  T="tests/test_rng_streams.py::test_arms_differing_in_holistic_reproduction_share_the_opponent_and_the_terrain"
  python -m pytest -q -x "$T" 2>&1 | grep -E "^>|^E |passed|failed" | head -6
  echo "--- all five stream tests on the broken code:"
  python -m pytest -q tests/test_rng_streams.py 2>&1 | tail -3
  git checkout -q rabbitstew/evolution.py
  echo "--- restored ($(git status --short rabbitstew/evolution.py | wc -l) modified files under rabbitstew/); the named test again:"
  python -m pytest -q "$T" 2>&1 | tail -1
  echo
  echo "=== 3. the statistics, recomputed independently of readout.py ==="
  python runs/RBT-85/adversary_stats.py runs/RBT-85
} 2>&1 | tee "$OUT"
