#!/bin/bash
# RBT-133 control: the same patched MuJoCo 3.14.0 and the same harness, built NATIVELY on the host with the same
# floating-point discipline as the WASM build (scalar paths: AVX off; -ffp-contract=off; no fast-math).  If this
# reproduces across x86, linux-arm64 and macOS-arm64, WASM is not what buys determinism; if it does not, what is
# left after the build flags is the platform (its libm, its compiler's code generation).
#   spikes/wasm/toolchain/build_native.sh OUTDIR    -> OUTDIR/rbt_native
set -euo pipefail
OUT=${1:?usage: build_native.sh OUTDIR}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
W=${WASMBUILD_DIR:-/opt/rbt133-wasm}
TAG=3.14.0
COMMIT=9ecbb9d7b5ee623f54745638d36799ff90e6f7cd
PATCH=$ROOT/runs/RBT-129/continuations/build/mujoco-3.14.0-rbt129-epa-log.patch
PATCH_SHA=2821425a0b2c80d1fe9791611fa04828f023ae4976e9f9e564463b62642e0cc4
FPFLAGS="-ffp-contract=off -fno-fast-math"
die() { echo "build_native.sh: $*" >&2; exit 1; }
sha() { if command -v sha256sum > /dev/null; then sha256sum < "$1" | cut -c1-64; else shasum -a 256 < "$1" | cut -c1-64; fi; }
mkdir -p "$W"
[ "$(sha "$PATCH")" = "$PATCH_SHA" ] || die "the patch is $(sha "$PATCH"), not $PATCH_SHA"
[ -d "$W/src/.git" ] || git clone -q --depth 1 --branch $TAG https://github.com/google-deepmind/mujoco.git "$W/src"
[ "$(git -C "$W/src" rev-parse HEAD)" = $COMMIT ] || die "$W/src is not $COMMIT"
git -C "$W/src" checkout -q -- . && git -C "$W/src" clean -fdq
patch -s -d "$W/src" -p1 < "$PATCH"
SRC=$(cd "$W/src" && pwd)
NB=$W/build-native
rm -rf "$NB"
RTLIB=""  # clang on linux-arm64 emits __muloti4, which lives in compiler-rt, not libgcc
if [ "$(uname -s)" = Linux ] && [ "$(uname -m)" = aarch64 ]; then RTLIB="--rtlib=compiler-rt"; fi
cmake -S "$SRC" -B "$NB" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
  -DMUJOCO_ENABLE_AVX=OFF -DMUJOCO_ENABLE_AVX_INTRINSICS=OFF \
  -DMUJOCO_BUILD_EXAMPLES=OFF -DMUJOCO_BUILD_SIMULATE=OFF -DMUJOCO_BUILD_TESTS=OFF -DMUJOCO_TEST_PYTHON_UTIL=OFF \
  -DCMAKE_C_FLAGS="$FPFLAGS" -DCMAKE_CXX_FLAGS="$FPFLAGS" -DCMAKE_SHARED_LINKER_FLAGS="$RTLIB" > "$W/cmake-native.log" 2>&1 || { tail -30 "$W/cmake-native.log"; die "cmake failed"; }
ninja -C "$NB" mujoco > "$W/ninja-native.log" 2>&1 || { tail -40 "$W/ninja-native.log"; die "ninja failed"; }
LIB=$(ls "$NB"/lib/libmujoco.so.$TAG "$NB"/lib/libmujoco.$TAG.dylib "$NB"/lib/libmujoco.dylib 2>/dev/null | head -1 || true)
[ -n "$LIB" ] || die "no native libmujoco in $NB/lib"
clang -O3 $FPFLAGS -I"$SRC/include" "$ROOT/spikes/wasm/harness/rbt_wasm.c" "$LIB" -Wl,-rpath,"$NB/lib" -lm $RTLIB -o "$OUT/rbt_native"
echo "rbt_native: $(uname -sm), $(clang --version | head -1), scalar paths (AVX off), $FPFLAGS, lib $(basename "$LIB")" | tee "$OUT/BUILD-native.txt"
