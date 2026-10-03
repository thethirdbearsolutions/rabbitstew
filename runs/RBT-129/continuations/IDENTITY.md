# The instrumented MuJoCo 3.14.0: provenance, reproduction, byte identity

*RBT-129 continuations tooling, owner decision 2 (option (c)). Built and tested 2026-10-03 on Linux 6.18 x86_64,
Ubuntu 24.04, Intel Xeon @ 2.10GHz, 4 cores, CPython 3.11.15.*

## Build

| item | value |
|---|---|
| source | google-deepmind/mujoco tag 3.14.0, `9ecbb9d7b5ee623f54745638d36799ff90e6f7cd` |
| patch | `build/mujoco-3.14.0-rbt129-epa-log.patch`, sha256 `2821425a0b2c80d1fe9791611fa04828f023ae4976e9f9e564463b62642e0cc4`; additions only, no guard |
| third-party deps (fetched by MuJoCo's own cmake at its pinned versions) | ccd `7931e764`, lodepng `17d08dd2`, MarchingCubeCpp `f03a1b3e`, miniz `d10b03cc`, qhull `d1c2fc0c`, tinyobjloader `2945a967`, tinyxml2 `e6caeae8` |
| WORKDIR | `/opt/rbt129-mjbuild` (fixed: ThinLTO's promoted-symbol names hash object paths) |
| toolchain | Ubuntu clang 18.1.3 (1ubuntu1), Ubuntu LLD 18.1.3, cmake 3.28.3, ninja 1.11.1 |
| flags | MuJoCo's Release defaults: `-O3 -DNDEBUG -flto=thin -fPIC -fvisibility=hidden -fdata-sections -ffunction-sections -mavx` (+ `-std=c11` / `-std=c++20`, warnings), plus `-ffile-prefix-map=<src>=mujoco-3.14.0`; examples, simulate, tests, USD off; target `mujoco` |
| **output** | `libmujoco.so.3.14.0`, sha256 **`2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4`** (build v3) |
| reproduction | `rm -rf /opt/rbt129-mjbuild`, then the script again (fresh clone, fresh dependency fetches): **the same sha256** |
| installed as | a venv of the pip wheel (`mujoco==3.14.0`, `numpy==2.4.6`) with `mujoco/libmujoco.so.3.14.0` replaced; the bindings are the wheel's |
| identity marker | `rbt_hzn_build_id()` = `rbt129-epa-instr/3 mujoco 3.14.0 9ecbb9d7… guard-off count-and-log` |
| versions | v1 `7ae75f7f…` (first log); v2 `1d138916…` (`unit`/`attempt`/`pid`/`seq` on every line); **v3 `2aea9a94…`** (the overflow line's write fails closed: `abort()` on an unopenable log or a short write; #527 adversary MINOR 9). Only the logging differs between them. |

## How it differs from the pip wheel (sha256 `5e7623e3…441000b`, 6,261,224 bytes)

| | pip wheel | instrumented build |
|---|---|---|
| compiler / linker (`.comment`) | clang 20.1.8 / LLD 20.1.8 (llvm-project `87f0227c`) | clang 18.1.3 / LLD 18.1.3 |
| C++ runtime | LLVM libc++, linked statically (manylinux); `NEEDED` libdl, libm, libpthread, libc, librt | GNU libstdc++, linked dynamically; `NEEDED` libm, libstdc++, libgcc_s, libc |
| libm (sin, cos, exp, …) | the host's glibc libm, at run time | the same host libm |
| vector ISA | AVX (17,799 ymm instructions); no AVX2 integer ops | AVX (15,406 ymm); no AVX2 integer ops |
| FMA (`vf[n]madd/msub`) | **0** | **0** |
| x87 | 242 instructions, all in tinyobjloader's OBJ/MTL readers and libc++'s long-double I/O | 8 (`randomdot`, a non-physics helper) |
| fast-math | none in MuJoCo's flags | none |
| added code | — | `engine_rbt_hzn.c` (hooks); one call in `epa`, one in `mj_step` |

Why this can still be byte-identical: no FMA contraction is possible on either side (no FMA target feature, and none
emitted), neither uses fast-math, so each IEEE double operation in the engine rounds the same way whichever clang
scheduled it; transcendental functions come from the same host libm at run time; decimal→binary conversion of the
model XML is correctly rounded in both runtimes. That is an argument. The evidence is below.

**Scope (COORD-RULING-520 D3, FC-2).** Identity is claimed for trajectories with no EPA overflow only. At an
overflow both builds are in undefined behaviour and build-specific; nothing here, and nothing the build does after an
overflow, is evidence about stock. The logged overflow line is the signal (`OVERFLOW-RULE-DRAFT.md`).

## Byte identity, stock vs instrumented

`identity.sh STOCK INSTR 30 ARM:POINT/SEED …`: each unit's ckpt60, forked as its arm, run **30 whole seasons (60–89)**
twice from the same state: stock pip venv (`-m rabbitstew.cli`, exactly as Stage 1 ran) and instrumented venv (through
`epa_ecology.py`, as a continuation runs), `WORKERS=2`. Every output file compared by sha256 (all but `run.log`,
`command.txt`, `platform.json` and the EPA logs). Raw lines: `records/identity-v3-{a,b}.txt` (the build),
`records/identity-v2-{a,b}.txt` and `records/identity-v1-{a,b}.txt`.

**Which files the comparison is about (NOTE 15).** Many compared files are the ckpt60 state, carried unchanged into the
run, and could not differ. The split below separates the files the 30 seasons **wrote or changed** (the full
`state.json` with populations, RNG streams and arenas; `history.json`; `lineage.jsonl`; `cohorts.jsonl`; `arenas.json`;
`config.json`; every new genotype file) from those **carried unchanged** from ckpt60.

| arm | point / seed | files: written or changed + carried | v3 (`2aea9a94…`, the build) | v2 (`1d138916…`) | v1 (`7ae75f7f…`) | EPA log (v3) |
|---|---|---|---|---|---|---|
| S | c2-p080-HP-G / 129004 | 899: **190** + 709 | **IDENTICAL** | IDENTICAL | IDENTICAL | 10 near misses, max horizon **23**, 0 overflows, 4.8e8 EPA iterations |
| M | c2-p030-U-G / 129005 | 772: **292** + 480 | **IDENTICAL** | IDENTICAL | IDENTICAL | 0 near misses, max 16, 0 overflows, 3.8e8 |
| N | c0-p030-PW-G / 129001 | 1121: **356** + 765 | **IDENTICAL** | IDENTICAL | IDENTICAL | 0 near misses, max 13, 0 overflows, 7.7e7 |
| S | c1-p080-U-L / 129004 | 917: **308** + 609 | **IDENTICAL** | IDENTICAL | IDENTICAL | 2 near misses, max 18, 0 overflows, 6.5e8 |

**Build v3: 4/4 units identical: 1146/1146 files written or changed by the runs, and 3709/3709 files in all** (v1 and
v2 likewise), over 3 arms, 4 points, 3 terrains (HP, U, PW) and both layouts (G, L), 120 unit-seasons and 1.6e9 EPA
iterations a build. The adversary's own re-run of the N unit gave the same split (356 + 765) and the same EPA figures.
Two units exercised the near-miss path (horizons 17–23) and stayed identical. No run overflowed, so, as FC-2 requires,
nothing is claimed about the overflow path. Every instrumented run's `platform.json` `resumes` entry carried
`mujoco_build` with the build's sha256.

**Reproduction of the build.** v1, v2 and v3 were each built twice from scratch (`rm -rf /opt/rbt129-mjbuild`, fresh
clone and dependency fetches); each pair gave the same sha256.

The scan's smoke test (`SMOKE.md`) adds full-length replays (240 seasons) on the instrumented build compared with the
Stage-1 branches that stock produced on other hosts.

---
_Generated by [Claude Code](https://claude.ai/code)_
