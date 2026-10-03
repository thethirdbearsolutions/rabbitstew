#!/bin/bash
# RBT-133 spike: build MuJoCo 3.14.0 + the RBT-129 EPA log patch, and the rabbitstew harness, to WebAssembly.
#
#   spikes/wasm/toolchain/build.sh OUTDIR          -> OUTDIR/rbt_wasm.js + OUTDIR/rbt_wasm.wasm, and OUTDIR/BUILD.txt
#   NATIVE=1 spikes/wasm/toolchain/build.sh OUTDIR -> also OUTDIR/rbt_native: the same harness and patched source built
#                                                 natively with the host clang (for the WASM-vs-native comparison)
#
# The recipe (each item is part of it):
# - Emscripten SDK 4.0.10 (MuJoCo's wasm/README.md pins it), emsdk checkout EMSDK_COMMIT below; release hash
#   8103ffedfb0c42d231c6af6859a5a1a832260b43;
# - source: google-deepmind/mujoco tag 3.14.0, commit 9ecbb9d7b5ee623f54745638d36799ff90e6f7cd, the same as
#   scripts/build_mujoco_instrumented.sh; patch runs/RBT-129/continuations/build/mujoco-3.14.0-rbt129-epa-log.patch
#   (sha256 checked, the same constant as that script);
# - single-threaded (MUJOCO_WASM_THREADS=OFF), no embind bindings, no tests; target `mujoco` (static) and its deps;
# - floating point: -ffp-contract=off everywhere, no -ffast-math (MuJoCo's CMake adds none), no -msimd128 and no
#   -mrelaxed-simd, so the module has no SIMD and no relaxed instructions (checked below by disassembly).  mjUSEPLATFORMSIMD
#   is never defined for Emscripten (it is set only with MUJOCO_ENABLE_AVX_INTRINSICS), so MuJoCo takes its scalar paths;
# - -ffile-prefix-map so that no host path is embedded; WORKDIR defaults to /opt/rbt133-wasm.
set -euo pipefail

OUT=${1:?usage: build.sh OUTDIR}
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
W=${WASMBUILD_DIR:-/opt/rbt133-wasm}
EMSDK_VERSION=4.0.10
EMSDK_COMMIT=96c657fc60920d2a6a82318aa50e0abf82749604
TAG=3.14.0
COMMIT=9ecbb9d7b5ee623f54745638d36799ff90e6f7cd
PATCH=$ROOT/runs/RBT-129/continuations/build/mujoco-3.14.0-rbt129-epa-log.patch
PATCH_SHA=2821425a0b2c80d1fe9791611fa04828f023ae4976e9f9e564463b62642e0cc4
FPFLAGS="-ffp-contract=off -fno-fast-math"

die() { echo "build.sh: $*" >&2; exit 1; }
sha() { sha256sum < "$1" | cut -c1-64; }

mkdir -p "$W"
# --- emsdk, pinned ---------------------------------------------------------------------------------------------
if [ ! -d "$W/emsdk/.git" ]; then git clone -q https://github.com/emscripten-core/emsdk.git "$W/emsdk"; fi
git -C "$W/emsdk" fetch -q origin "$EMSDK_COMMIT" 2>/dev/null || true
git -C "$W/emsdk" checkout -q "$EMSDK_COMMIT"
(cd "$W/emsdk" && ./emsdk install $EMSDK_VERSION > "$W/emsdk-install.log" 2>&1 && ./emsdk activate $EMSDK_VERSION > /dev/null)
# shellcheck disable=SC1091
source "$W/emsdk/emsdk_env.sh" > /dev/null 2>&1
EMCC_V=$(emcc --version | head -1)
echo "$EMCC_V" | grep -q " $EMSDK_VERSION " || die "emcc is not $EMSDK_VERSION: $EMCC_V"

# --- source + patch --------------------------------------------------------------------------------------------
[ "$(sha "$PATCH")" = "$PATCH_SHA" ] || die "the patch is $(sha "$PATCH"), not $PATCH_SHA"
[ -d "$W/src/.git" ] || git clone -q --depth 1 --branch $TAG https://github.com/google-deepmind/mujoco.git "$W/src"
[ "$(git -C "$W/src" rev-parse HEAD)" = $COMMIT ] || die "$W/src is not $COMMIT"
git -C "$W/src" checkout -q -- . && git -C "$W/src" clean -fdq
patch -s -d "$W/src" -p1 < "$PATCH"
SRC=$(cd "$W/src" && pwd)
PREFIX="-ffile-prefix-map=$SRC=mujoco-$TAG -ffile-prefix-map=$W=rbt133"

# --- MuJoCo static library, WASM -------------------------------------------------------------------------------
B=$W/build-wasm
rm -rf "$B"
emcmake cmake -S "$SRC" -B "$B" -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DMUJOCO_WASM_THREADS=OFF -DMUJOCO_BUILD_TESTS_WASM=OFF -DMUJOCO_BUILD_STUDIO=OFF \
  -DCMAKE_C_FLAGS="$FPFLAGS $PREFIX" -DCMAKE_CXX_FLAGS="$FPFLAGS $PREFIX" > "$W/cmake-wasm.log" 2>&1 \
  || { tail -30 "$W/cmake-wasm.log"; die "cmake failed"; }
ninja -C "$B" mujoco > "$W/ninja-wasm.log" 2>&1 || { tail -40 "$W/ninja-wasm.log"; die "ninja failed"; }
grep -q -- "-ffast-math\|-msimd128\|-mrelaxed-simd\|-ffp-contract=fast" "$B/compile_commands.json" && die "a forbidden FP/SIMD flag is in compile_commands.json"
LIBS=$(find "$B/lib" -name '*.a' ! -name libmujoco.a | sort)  # ccd, miniz, qhull, tinyobjloader, tinyxml2

# --- the harness, WASM -----------------------------------------------------------------------------------------
emcc -O3 $FPFLAGS $PREFIX -ffile-prefix-map=$ROOT=rabbitstew -I"$SRC/include" "$ROOT/spikes/wasm/harness/rbt_wasm.c" \
  -Wl,--whole-archive "$B/lib/libmujoco.a" -Wl,--no-whole-archive $LIBS \
  -sNODERAWFS=1 -sENVIRONMENT=node -sALLOW_MEMORY_GROWTH=1 -sEXIT_RUNTIME=1 -sSTACK_SIZE=4MB \
  -o "$OUT/rbt_wasm.js"

# --- checks: no SIMD, no relaxed instructions, no FMA-like ops -------------------------------------------------
DIS="$W/rbt_wasm.wat"
"$EMSDK/upstream/bin/wasm-dis" "$OUT/rbt_wasm.wasm" -o "$DIS"
NSIMD=$(grep -c -E "v128|f64x2|f32x4|i8x16|i16x8|i32x4|i64x2" "$DIS" || true)
NRELAX=$(grep -c -i "relaxed" "$DIS" || true)
NF64=$(grep -c -E "f64\.(add|sub|mul|div)" "$DIS" || true)
[ "$NSIMD" = 0 ] || die "the module has $NSIMD SIMD instructions"
[ "$NRELAX" = 0 ] || die "the module has $NRELAX relaxed-SIMD instructions"

{
  echo "rbt_wasm build (RBT-133 spike)"
  echo "emcc: $EMCC_V (emsdk $EMSDK_COMMIT)"
  echo "mujoco: $TAG $COMMIT + $(basename "$PATCH") ($PATCH_SHA)"
  echo "flags: -O3 $FPFLAGS, single-threaded, no -msimd128, no relaxed SIMD"
  echo "rbt_wasm.wasm sha256 $(sha "$OUT/rbt_wasm.wasm")"
  echo "rbt_wasm.js   sha256 $(sha "$OUT/rbt_wasm.js")"
  echo "disassembly: SIMD instructions $NSIMD, relaxed instructions $NRELAX, f64 add/sub/mul/div $NF64"
  echo "rbt129 build id: $(grep -a -o 'rbt129-epa-instr/3[ -~]*' "$OUT/rbt_wasm.wasm" | head -1)"
} | tee "$OUT/BUILD.txt"

# --- optional: the same harness and patched source, native (host clang, scalar paths, contraction off) ------------
if [ -n "${NATIVE:-}" ]; then
  NB=$W/build-native
  rm -rf "$NB"
  cmake -S "$SRC" -B "$NB" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
    -DMUJOCO_ENABLE_AVX=OFF -DMUJOCO_ENABLE_AVX_INTRINSICS=OFF -DBUILD_SHARED_LIBS=OFF \
    -DMUJOCO_BUILD_EXAMPLES=OFF -DMUJOCO_BUILD_SIMULATE=OFF -DMUJOCO_BUILD_TESTS=OFF -DMUJOCO_TEST_PYTHON_UTIL=OFF \
    -DCMAKE_C_FLAGS="$FPFLAGS $PREFIX" -DCMAKE_CXX_FLAGS="$FPFLAGS $PREFIX" > "$W/cmake-native.log" 2>&1 \
    || { tail -30 "$W/cmake-native.log"; die "native cmake failed"; }
  ninja -C "$NB" mujoco > "$W/ninja-native.log" 2>&1 || { tail -40 "$W/ninja-native.log"; die "native ninja failed"; }
  clang -O3 $FPFLAGS -I"$SRC/include" "$ROOT/spikes/wasm/harness/rbt_wasm.c" \
    "$NB/lib/libmujoco.so" -Wl,-rpath,"$NB/lib" -lm -o "$OUT/rbt_native"  # MuJoCo's native library is always SHARED
  echo "rbt_native: $(clang --version | head -1), scalar paths (AVX off), $FPFLAGS" | tee -a "$OUT/BUILD.txt"
fi
