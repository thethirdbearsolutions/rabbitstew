#!/bin/bash
# RBT-129 crash diagnosis: the build recipe for a patched libmujoco 3.14.0 (adversary MINOR 6).
#
#   build.sh PATCH WORKDIR PIP_VENV OUT_VENV
#
# - source: google-deepmind/mujoco tag 3.14.0 (commit 9ecbb9d7b5ee623f54745638d36799ff90e6f7cd), shallow clone
# - PATCH applied with `patch -p1` (or "none" for an unpatched source build)
# - toolchain used here: Ubuntu 24.04, clang/clang++ 18.1.3 (1ubuntu1), LLD 18.1.3, cmake 3.28.3, ninja 1.11.1
# - cmake: -G Ninja -DCMAKE_BUILD_TYPE=Release (-O3 -DNDEBUG) with MuJoCo's defaults (AVX + AVX intrinsics ON,
#   its own LTO setting), examples/simulate/tests/USD OFF; target `mujoco` only
# - -ffile-prefix-map=<src>=mujoco-3.14.0: the .so embeds __FILE__ source paths (29 of them, in error strings).
# - WORKDIR's ABSOLUTE PATH is part of the recipe: MuJoCo builds with ThinLTO, whose promoted local symbols are named
#   `.str.1.llvm.<hash>` with the hash taken from each object's path, so the same patch built under a different
#   directory gives a different .so (checked: 6N in $S/bA -> 358e9608..., in $S/other/dir/bB -> c4f8c0c4...; the nm
#   tables differ in 1218 lines, all inspected ones `.llvm.<hash>` names; the code was not diffed beyond that) while a rebuild in the SAME directory reproduces 358e9608... exactly.
#   Paths, plus the compiler (adversary: clang 18.1.3 elsewhere; the round-1 ad-hoc build had no prefix map) are why
#   the hosts' sha256s differed.  To pin a build across hosts, fix WORKDIR (e.g. /opt/mjbuild) and the toolchain image.
# - OUT_VENV is a copy of PIP_VENV (pip mujoco==3.14.0, numpy 2.4.6) with the wheel's libmujoco.so.3.14.0 replaced by
#   the built one; the Python bindings are the wheel's, unchanged.
# The pip wheel itself is clang 20.1.8 + LLD 20.1.8 (its .comment section).  Byte identity of results with the wheel
# is an empirical check (identity.sh), not a consequence of this recipe: neither build has FMA instructions or
# fast-math, so IEEE results should not depend on the compiler version, but that is argued, then tested, not proven.
set -eu
PATCH=$1; W=$2; PIP=$3; OUT=$4
mkdir -p "$W"
[ -d "$W/src" ] || git clone -q --depth 1 --branch 3.14.0 https://github.com/google-deepmind/mujoco.git "$W/src"
[ "$(git -C "$W/src" rev-parse HEAD)" = 9ecbb9d7b5ee623f54745638d36799ff90e6f7cd ]
git -C "$W/src" checkout -q -- .
[ "$PATCH" = none ] || patch -s -d "$W/src" -p1 < "$PATCH"
SRC=$(cd "$W/src" && pwd)
cmake -S "$SRC" -B "$W/build" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_C_FLAGS="-ffile-prefix-map=$SRC=mujoco-3.14.0" -DCMAKE_CXX_FLAGS="-ffile-prefix-map=$SRC=mujoco-3.14.0" \
  -DMUJOCO_BUILD_EXAMPLES=OFF -DMUJOCO_BUILD_SIMULATE=OFF -DMUJOCO_BUILD_TESTS=OFF -DMUJOCO_TEST_PYTHON_UTIL=OFF \
  -DMUJOCO_WITH_USD=OFF > "$W/cmake.log"
ninja -C "$W/build" -j2 mujoco > "$W/build.log"
rm -rf "$OUT"; cp -a "$PIP" "$OUT"
cp "$W/build/lib/libmujoco.so.3.14.0" "$OUT/lib/python3.11/site-packages/mujoco/libmujoco.so.3.14.0"
"$OUT/bin/python" -c 'import mujoco; assert mujoco.__version__ == "3.14.0"'
echo "patch $(basename "$PATCH") sha256 $(sha256sum < "$W/build/lib/libmujoco.so.3.14.0" | cut -c1-64)"
echo "compiler $(clang --version | head -1); vfmadd count $(objdump -d "$W/build/lib/libmujoco.so.3.14.0" | grep -c vfmadd)"
