#!/bin/bash
# RBT-133 adversary: re-run every probe in this directory and rewrite its readout.
#   spikes/wasm/adversary/rederive.sh DIST NATIVE_BIN_DIR SCRATCH     (run from the repository root)
#   e.g. spikes/wasm/adversary/rederive.sh /opt/wasmspike/dist /opt/wasmspike/native /tmp/claude-0/adv
# DIST holds rbt_wasm.js/.wasm (toolchain/build.sh) and rbt_native (NATIVE=1); NATIVE_BIN_DIR holds build_native.sh's
# rbt_native.  semcheck.py also needs the native MuJoCo build under ${WASMBUILD_DIR:-/opt/rbt133-wasm}.
set -euo pipefail
DIST=${1:?usage}; NB=${2:?usage}; S=${3:?usage}
A=spikes/wasm/adversary
mkdir -p "$S"
# harness runs: WASM and native-scalar, both packs, both modes
for kind in wasm native; do
  for b in conventional-0 holistic-0; do for m in openloop bout; do
    R="$S/$kind/$b-$m"; mkdir -p "$R"
    if [ $kind = wasm ]; then node "$DIST/rbt_wasm.js" $m spikes/wasm/packs/$b "$R" > /dev/null; else "$NB/rbt_native" $m spikes/wasm/packs/$b "$R" > /dev/null; fi
  done; done
done
{
  echo "# WASM fingerprints here vs the committed x86 ones (ref-wasm-x86/)"
  for b in conventional-0 holistic-0; do for m in openloop bout; do
    python spikes/wasm/check.py spikes/wasm/packs/$b "$S/wasm/$b-$m" | sed "s#$S/wasm/##" > "$S/fp.txt"
    diff -q "$S/fp.txt" spikes/wasm/ref-wasm-x86/$b-$m.txt > /dev/null && echo "$b $m IDENTICAL" || echo "$b $m DIFFERS"
  done; done
  echo "# the harness's states against the Python (pip-wheel) recordings in locate/ref-x86/ (check.py), and the WASM compile"
  for b in conventional-0 holistic-0; do
    node "$DIST/rbt_wasm.js" compile spikes/wasm/packs/$b "$S/$b-wasm.mjb" > /dev/null
    echo "$b: WASM-compiled MJB sha $(sha256sum < "$S/$b-wasm.mjb" | cut -c1-16), x86 wheel's $(sha256sum < spikes/wasm/packs/$b/model.mjb | cut -c1-16)"
    for kind in wasm native; do for m in bout openloop; do
      echo "  $kind $m: $(python spikes/wasm/check.py spikes/wasm/packs/$b "$S/$kind/$b-$m" spikes/wasm/locate/ref-x86/$b | tail -1 | sed "s#.*: \([0-9]* rows\)#\1#")"
    done; done
  done
  echo "# probe.py's own same-platform positive control (x86 here against the x86 references)"
  for b in conventional-0 holistic-0; do
    python spikes/wasm/locate/probe.py replay-physics spikes/wasm/locate/ref-x86/$b --scratch "$S" | grep -v '^ref:\|^here:' | sed "s/^/$b /"
    python spikes/wasm/locate/probe.py replay-brain spikes/wasm/locate/ref-x86/$b | grep -v '^ref:\|^here:' | sed "s/^/$b /"
  done
} > $A/rederive.txt
{ echo "######## WASM (this container's build of rbt_wasm.wasm, sha d48ef3e9...)"; python $A/faithful.py "$S/wasm";
  echo "######## native-scalar (build_native.sh)"; python $A/faithful.py "$S/native"; } | sed "s#$S/#SCRATCH/#g" > $A/faithful.txt
python $A/semcheck.py "$S/wasm" > $A/semcheck.txt
python $A/perturb.py "$DIST" "$S/perturb" | sed "s#$S/#SCRATCH/#g" > $A/perturb.txt
python $A/perturb.py "$DIST" "$S/perturb" --sweep > $A/perturb_sweep.txt
python $A/evidence.py > $A/evidence.txt
python spikes/wasm/bench.py "$DIST" 10 > $A/bench_rerun.txt
python $A/bench_adv.py 10 > $A/bench_adv.txt
