#!/bin/bash
# RBT-99 adversary probe 5: does the SHIFT/OUTROOT change alter RBT-92's own launcher?
# Runs runs/RBT-92/run_arm.sh as it was before PR #80 (44c4e95) and as merged (HEAD), with `python` stubbed
# to print its argv, in a scratch tree carrying a fixture onset.txt and cull-k file, and compares everything
# each version writes (event.txt, run.log, the output path) for RBT-92's three arms, plus the error paths
# (no onset, no cull-k, bad arm) and RBT-99's wrapper.   runs/RBT-99/adversary/run_arm_identity.sh
set -e
REPO=$(git rev-parse --show-toplevel)
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
mkdir -p "$W/bin"
printf '#!/bin/bash\necho "argv: $*"\n' > "$W/bin/python"; chmod +x "$W/bin/python"
for V in old new; do
  mkdir -p "$W/$V/runs/RBT-92" "$W/$V/runs/RBT-99"
  if [ $V = old ]; then git -C "$REPO" show 44c4e95:runs/RBT-92/run_arm.sh > "$W/$V/runs/RBT-92/run_arm.sh"
  else cp "$REPO/runs/RBT-92/run_arm.sh" "$W/$V/runs/RBT-92/"; cp "$REPO/runs/RBT-99/run_arm.sh" "$W/$V/runs/RBT-99/"; fi
  chmod +x "$W/$V/runs/RBT-92/run_arm.sh"
  printf 'seed\tT\n801\t371\tD=5\n' > "$W/$V/runs/RBT-92/onset.txt"
  printf 'cull\tholistic=3,conventional=35\n' > "$W/$V/runs/RBT-92/cull-k-801.txt"
  ( cd "$W/$V" && for A in shift cull cull20; do PATH="$W/bin:$PATH" runs/RBT-92/run_arm.sh 801 $A; done
    for bad in "802 shift" "801 cull2" ""; do PATH="$W/bin:$PATH" runs/RBT-92/run_arm.sh $bad 2>>errors.txt || echo "exit $?" >> errors.txt; done
    mv runs/RBT-92/cull-k-801.txt k.bak; PATH="$W/bin:$PATH" runs/RBT-92/run_arm.sh 801 cull 2>>errors.txt || echo "exit $?" >> errors.txt; mv k.bak runs/RBT-92/cull-k-801.txt )
  ( cd "$W/$V" && find runs -newer runs/RBT-92/onset.txt -type f ! -name run_arm.sh ! -name 'cull-k-*' | sort | while read f; do echo "== $f"; cat "$f"; done; echo "== errors.txt"; cat errors.txt ) > "$W/$V.out"
done
sed "s#$W/old#ROOT#g" "$W/old.out" > "$W/o"; sed "s#$W/new#ROOT#g" "$W/new.out" > "$W/n"
if cmp -s "$W/o" "$W/n"; then echo "RBT-92 defaults: every file written and every message, old (44c4e95) vs merged: BYTE-IDENTICAL"; else echo "RBT-92 defaults: DIFFER"; diff "$W/o" "$W/n" || true; fi
echo; echo "--- what the old version wrote (the reference) ---"; cat "$W/o"
echo; echo "--- RBT-99 wrapper, merged version, cull-k in runs/RBT-99 ---"
( cd "$W/new" && printf 'cull\tholistic=3,conventional=35\n' > runs/RBT-99/cull-k-801.txt
  for A in shift cull; do PATH="$W/bin:$PATH" runs/RBT-99/run_arm.sh 801 $A; done
  PATH="$W/bin:$PATH" runs/RBT-99/run_arm.sh 801 cull20 || echo "exit $?"
  for A in shift cull; do echo "== runs/RBT-99/$A-801"; cat runs/RBT-99/$A-801/event.txt runs/RBT-99/$A-801/run.log; done ) 2>&1 | sed "s#$W/new#ROOT#g"
echo; echo "--- RBT-99 wrapper launched from outside the repository root (cwd = runs/) ---"
( cd "$W/new/runs" && PATH="$W/bin:$PATH" RBT-99/run_arm.sh 801 cull 2>&1 || echo "exit $?"; ls -d RBT-99/cull-801 runs 2>/dev/null ) | sed "s#$W/new#ROOT#g"
