#!/bin/bash
# RBT-129 continuations: build the guard-off INSTRUMENTED MuJoCo 3.14.0 (owner decision 2, option (c),
# runs/RBT-129/coordinator/OWNER-DECISIONS-2026-10-03.md), reproducibly, and install it into a venv.
#
#   scripts/build_mujoco_instrumented.sh instr OUT_VENV    build the patched libmujoco, check its sha256, and make a
#                                                          venv of the pip wheel with the wheel's libmujoco replaced
#   scripts/build_mujoco_instrumented.sh stock OUT_VENV    the same venv with the pip wheel untouched (the identity
#                                                          runs' reference; its libmujoco sha256 is checked too)
#
# The recipe (every item is part of it: change one and the sha256 changes):
# - source: google-deepmind/mujoco tag 3.14.0, commit 9ecbb9d7b5ee623f54745638d36799ff90e6f7cd (shallow clone);
# - patch: runs/RBT-129/continuations/build/mujoco-3.14.0-rbt129-epa-log.patch (sha256 PATCH_SHA below), `patch -p1`.
#   It ONLY counts and logs EPA horizon sizes: no guard, so stock behaviour, overflow included, is kept;
# - WORKDIR: /opt/rbt129-mjbuild, an ABSOLUTE path that is part of the recipe.  MuJoCo builds with ThinLTO, which names
#   promoted local symbols `.str.N.llvm.<hash>` from each object's path, so the same patch built in another directory
#   gives another .so (runs/RBT-129/mn-crash/DIAGNOSIS.md, "Builds", on #520).  Override with MJBUILD_DIR only to test
#   the script; the sha256 check then fails, as it should;
# - toolchain: Ubuntu 24.04's clang/clang++ 18.1.3 (1ubuntu1), LLD 18.1.3, cmake 3.28.3, ninja 1.11.1 (refused
#   otherwise; MJBUILD_ANY_TOOLCHAIN=1 skips that check for a test build only);
# - cmake: -G Ninja -DCMAKE_BUILD_TYPE=Release (-O3 -DNDEBUG) with MuJoCo's own defaults (AVX and AVX intrinsics ON, its
#   LTO), C and C++ flags `-ffile-prefix-map=<src>=mujoco-3.14.0` (the .so embeds __FILE__ strings); examples, simulate,
#   tests, python-util tests and USD OFF; target `mujoco` only;
# - the venv: python3.11 -m venv, pip install mujoco==3.14.0 numpy==2.4.6 (binary wheels), then the wheel's
#   mujoco/libmujoco.so.3.14.0 is replaced by the built one.  The Python bindings are the wheel's, unchanged.
#
# The pip wheel is clang 20.1.8 + LLD 20.1.8 (its .comment section), so the two libraries differ as binaries.  Neither
# has an FMA instruction (vfmadd count 0, printed below) or fast-math, so IEEE results should not depend on the
# compiler; that is an argument, and byte identity of whole runs is the empirical check
# (runs/RBT-129/continuations/identity.sh; IDENTITY.md).
set -euo pipefail

MODE=${1:?usage: build_mujoco_instrumented.sh instr|stock OUT_VENV}
OUT=${2:?usage: build_mujoco_instrumented.sh instr|stock OUT_VENV}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
W=${MJBUILD_DIR:-/opt/rbt129-mjbuild}
TAG=3.14.0
COMMIT=9ecbb9d7b5ee623f54745638d36799ff90e6f7cd
PATCH=$ROOT/runs/RBT-129/continuations/build/mujoco-3.14.0-rbt129-epa-log.patch
# keep these three in step with runs/RBT-129/launch/mjbuild.py (tests/test_rbt129_continuations.py checks it)
PATCH_SHA=2821425a0b2c80d1fe9791611fa04828f023ae4976e9f9e564463b62642e0cc4
STOCK_SO_SHA=5e7623e30f55bf324d4c9648379ebeba5bcd153ee0304c52eac74bf8d441000b
INSTR_SO_SHA=2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4
PY=${PYTHON:-python3.11}

die() { echo "build_mujoco_instrumented: $*" >&2; exit 1; }
sha() { sha256sum < "$1" | cut -c1-64; }

venv() {  # the pip wheel's venv at $OUT, its libmujoco checked against the stock sha256
  rm -rf "$OUT"
  "$PY" -m venv "$OUT"
  "$OUT/bin/pip" install -q --only-binary=:all: mujoco==$TAG numpy==2.4.6
  SO=$("$OUT/bin/python" -c 'import mujoco, os; print(os.path.join(os.path.dirname(mujoco.__file__), "libmujoco.so.3.14.0"))')
  [ "$(sha "$SO")" = "$STOCK_SO_SHA" ] || die "the pip wheel's libmujoco is $(sha "$SO"), not $STOCK_SO_SHA"
}

case "$MODE" in
  stock)
    venv
    echo "stock venv $OUT: libmujoco.so.3.14.0 sha256 $STOCK_SO_SHA (pip wheel)"
    exit 0 ;;
  instr) ;;
  *) die "mode must be instr or stock" ;;
esac

if [ -z "${MJBUILD_ANY_TOOLCHAIN:-}" ]; then
  clang --version | head -1 | grep -qx 'Ubuntu clang version 18.1.3 (1ubuntu1)' || die "clang is not 18.1.3 (1ubuntu1): $(clang --version | head -1)"
  ld.lld --version | grep -q '^Ubuntu LLD 18.1.3' || die "ld.lld is not 18.1.3: $(ld.lld --version)"
  cmake --version | head -1 | grep -qx 'cmake version 3.28.3' || die "cmake is not 3.28.3"
  [ "$(ninja --version)" = 1.11.1 ] || die "ninja is not 1.11.1"
fi
[ "$(sha "$PATCH")" = "$PATCH_SHA" ] || die "the patch is $(sha "$PATCH"), not $PATCH_SHA"

mkdir -p "$W"
[ -d "$W/src/.git" ] || git clone -q --depth 1 --branch $TAG https://github.com/google-deepmind/mujoco.git "$W/src"
[ "$(git -C "$W/src" rev-parse HEAD)" = $COMMIT ] || die "$W/src is not $COMMIT"
git -C "$W/src" checkout -q -- . && git -C "$W/src" clean -fdq
patch -s -d "$W/src" -p1 < "$PATCH"
SRC=$(cd "$W/src" && pwd)
rm -rf "$W/build"
cmake -S "$SRC" -B "$W/build" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_C_FLAGS="-ffile-prefix-map=$SRC=mujoco-$TAG" -DCMAKE_CXX_FLAGS="-ffile-prefix-map=$SRC=mujoco-$TAG" \
  -DMUJOCO_BUILD_EXAMPLES=OFF -DMUJOCO_BUILD_SIMULATE=OFF -DMUJOCO_BUILD_TESTS=OFF -DMUJOCO_TEST_PYTHON_UTIL=OFF \
  -DMUJOCO_WITH_USD=OFF > "$W/cmake.log"
ninja -C "$W/build" -j"$(nproc)" mujoco > "$W/build.log"
LIB=$W/build/lib/libmujoco.so.$TAG
GOT=$(sha "$LIB")
echo "built $LIB sha256 $GOT"
echo "compiler $(clang --version | head -1); linker $(ld.lld --version); vfmadd count $(objdump -d "$LIB" | grep -c vfmadd || true)"
if [ "$INSTR_SO_SHA" != "__INSTR_SO_SHA__" ] && [ "$GOT" != "$INSTR_SO_SHA" ]; then
  die "the built libmujoco is $GOT, not the recipe's $INSTR_SO_SHA (WORKDIR, toolchain or patch differ)"
fi
venv
cp "$LIB" "$SO"
"$OUT/bin/python" - "$ROOT" <<'EOF'
import sys
sys.path.insert(0, sys.argv[1] + "/runs/RBT-129/launch")
import mjbuild
print("installed:", mjbuild.check_instrumented())
EOF
