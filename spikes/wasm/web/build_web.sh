#!/bin/bash
# RBT-133: link the harness for a browser (after toolchain/build.sh has built the WASM MuJoCo library), with the packs
# preloaded into MEMFS, then run it in headless Chromium and print each state stream's sha256.
#   spikes/wasm/web/build_web.sh OUTDIR
set -euo pipefail
OUT=${1:?usage: build_web.sh OUTDIR}
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
W=${WASMBUILD_DIR:-/opt/rbt133-wasm}
B=$W/build-wasm
source "$W/emsdk/emsdk_env.sh" > /dev/null 2>&1
mkdir -p "$OUT/packs"
cp -r "$ROOT"/spikes/wasm/packs/* "$OUT/packs/"
cp "$ROOT/spikes/wasm/web/index.html" "$ROOT/spikes/wasm/web/drive.mjs" "$OUT/"
cd "$OUT"
emcc -O3 -ffp-contract=off -fno-fast-math -I"$W/src/include" "$ROOT/spikes/wasm/harness/rbt_wasm.c" \
  -Wl,--whole-archive "$B/lib/libmujoco.a" -Wl,--no-whole-archive $(find "$B/lib" -name '*.a' ! -name libmujoco.a | sort) \
  -sENVIRONMENT=web -sALLOW_MEMORY_GROWTH=1 -sSTACK_SIZE=4MB -sINVOKE_RUN=0 -sEXIT_RUNTIME=0 \
  -sEXPORTED_RUNTIME_METHODS=callMain,FS --preload-file packs@/packs -o rbt_web.js
"$EMSDK/upstream/bin/wasm-dis" rbt_web.wasm -o rbt_web.wat
NSIMD=$(grep -c -E "v128|f64x2|f32x4|i8x16|i16x8|i32x4|i64x2" rbt_web.wat || true)
NRELAX=$(grep -c -i "relaxed" rbt_web.wat || true)
[ "$NSIMD" = 0 ] && [ "$NRELAX" = 0 ] || { echo "build_web.sh: SIMD $NSIMD relaxed $NRELAX" >&2; exit 1; }
echo "rbt_web.wasm sha256 $(sha256sum < rbt_web.wasm | cut -c1-64) (SIMD instructions 0, relaxed 0)"
python3 -m http.server 8765 --bind 127.0.0.1 > /dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER' EXIT
sleep 1
node drive.mjs
