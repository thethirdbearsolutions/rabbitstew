# The instrumented MuJoCo 3.14.0: provenance, reproduction, byte identity

*RBT-129 continuations tooling, owner decision 2 (option (c)). Built and tested 2026-10-03 on Linux 6.18 x86_64,
Ubuntu 24.04, Intel Xeon @ 2.10GHz, 4 cores, CPython 3.11.15.*

## Build

| item | value |
|---|---|
| source | google-deepmind/mujoco tag 3.14.0, `9ecbb9d7b5ee623f54745638d36799ff90e6f7cd` |
| patch | `build/mujoco-3.14.0-rbt129-epa-log.patch`, sha256 `c5dba64d56773e22fe7a728f790a1e5ffe28324913ad2d97b260487f7c2b1a9a`; additions only, no guard |
| third-party deps (fetched by MuJoCo's own cmake at its pinned versions) | ccd `7931e764`, lodepng `17d08dd2`, MarchingCubeCpp `f03a1b3e`, miniz `d10b03cc`, qhull `d1c2fc0c`, tinyobjloader `2945a967`, tinyxml2 `e6caeae8` |
| WORKDIR | `/opt/rbt129-mjbuild` (fixed: ThinLTO's promoted-symbol names hash object paths) |
| toolchain | Ubuntu clang 18.1.3 (1ubuntu1), Ubuntu LLD 18.1.3, cmake 3.28.3, ninja 1.11.1 |
| flags | MuJoCo's Release defaults: `-O3 -DNDEBUG -flto=thin -fPIC -fvisibility=hidden -fdata-sections -ffunction-sections -mavx` (+ `-std=c11` / `-std=c++20`, warnings), plus `-ffile-prefix-map=<src>=mujoco-3.14.0`; examples, simulate, tests, USD off; target `mujoco` |
| **output** | `libmujoco.so.3.14.0`, 5,525,136 bytes, sha256 **`1d138916760a1226e1882a578851bfd6da88c2ab9532949bdfdcfd25f0e94aa0`** |
| reproduction | `rm -rf /opt/rbt129-mjbuild`, then the script again (fresh clone, fresh dependency fetches): **the same sha256** |
| installed as | a venv of the pip wheel (`mujoco==3.14.0`, `numpy==2.4.6`) with `mujoco/libmujoco.so.3.14.0` replaced; the bindings are the wheel's |
| identity marker | `rbt_hzn_build_id()` = `rbt129-epa-instr/2 mujoco 3.14.0 9ecbb9d7… guard-off count-and-log` |

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
`command.txt`, `platform.json`, `epa_overflow.jsonl`). Raw lines: `records/identity-a.txt`, `records/identity-b.txt`.

| arm | point / seed | files | stock vs instrumented | EPA log (instrumented) |
|---|---|---|---|---|
| S | c2-p080-HP-G / 129004 | 899 | **IDENTICAL** | 10 near misses, max horizon **23**, 0 overflows, 4.8e8 EPA iterations |
| M | c2-p030-U-G / 129005 | 772 | **IDENTICAL** | 0 near misses, max 16, 0 overflows, 3.8e8 |
| N | c0-p030-PW-G / 129001 | 1121 | **IDENTICAL** | 0 near misses, max 13, 0 overflows, 7.7e7 |
| S | c1-p080-U-L / 129004 | 917 | **IDENTICAL** | 2 near misses, max 18, 0 overflows, 6.5e8 |

**4/4 units, 3709/3709 files identical**, over 3 arms, 4 points, 3 terrains (HP, U, PW) and both layouts (G, L), 120
unit-seasons and 1.6e9 EPA iterations. Two units exercised the near-miss path (horizons 17–23) and stayed identical.
No run overflowed, so, as FC-2 requires, nothing is claimed about the overflow path. Every instrumented run's
`platform.json` `resumes` entry carried `mujoco_build` with `libmujoco_sha256` `1d138916…`.

The scan's smoke test (`SMOKE.md`) adds full-length replays (240 seasons) on the instrumented build compared with the
Stage-1 branches that stock produced on other hosts.

---
_Generated by [Claude Code](https://claude.ai/code)_
