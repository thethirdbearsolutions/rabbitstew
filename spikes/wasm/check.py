"""RBT-133: read a harness run (states.bin, result.txt) against a recorded reference, or against another harness run.

    python spikes/wasm/check.py PACK_DIR RUN_DIR [REC_DIR | RUN_DIR2]

Prints the sha256 of the whole state stream (the cross-platform fingerprint of a run), and, given a second argument,
the first mj_step whose state row differs: against a probe recording (REC_DIR, steps.txt; the native reference) the
rows are hashed exactly as probe.py hashes them, against another harness run the rows are compared byte for byte.
"""

from __future__ import annotations

import hashlib
import os
import sys

import mujoco
import numpy as np


def rows(pack: str, run: str) -> np.ndarray:
    m = mujoco.MjModel.from_binary_path(os.path.join(pack, "model.mjb"))
    w = 1 + m.nq + 2 * m.nv + m.na
    a = np.fromfile(os.path.join(run, "states.bin"), dtype="<f8")
    if a.size % w:
        raise SystemExit(f"{run}/states.bin is not a whole number of {w}-wide rows")
    return a.reshape(-1, w)


def main() -> None:
    pack, run = sys.argv[1], sys.argv[2]
    R = rows(pack, run)
    with open(os.path.join(run, "states.bin"), "rb") as f:
        print(f"{run}: {len(R)} state rows, stream sha256 {hashlib.sha256(f.read()).hexdigest()[:16]}")
    tk = os.path.join(run, "ticks.bin")
    if os.path.exists(tk):  # closed loop: every tick's sensors, activations and ctrl (adversary F2)
        with open(tk, "rb") as f:
            b = f.read()
        print(f"{run}: ticks.bin {len(b)} bytes, sha256 {hashlib.sha256(b).hexdigest()[:16]}")
    res = os.path.join(run, "result.txt")
    if os.path.exists(res):
        print(open(res).read().rstrip())
    if len(sys.argv) < 4:
        return
    other = sys.argv[3]
    if os.path.exists(os.path.join(other, "steps.txt")):
        with open(os.path.join(other, "steps.txt")) as f:
            head = f.readline().split()
            settle = int(head[2])
            ref = [ln.strip() for ln in f if ln.strip()]
        mine = [hashlib.sha256(r.tobytes()).hexdigest()[:16] for r in R]
        off = 0 if len(mine) == len(ref) else settle  # an open-loop run starts after the settle
        first = next((k for k in range(min(len(mine), len(ref) - off)) if mine[k] != ref[off + k]), None)
        print(f"vs native recording {other}: {min(len(mine), len(ref) - off)} rows compared (offset {off}); first differing row: {first}")
    else:
        O = rows(pack, other)
        n = min(len(R), len(O))
        diff = np.nonzero(np.any(R[:n].view(np.int64) != O[:n].view(np.int64), axis=1))[0]
        first = int(diff[0]) if diff.size else None
        print(f"vs harness run {other}: {n} rows compared; first differing row: {first}; differing rows {diff.size}")
        if first is not None:
            k = int(np.nonzero(R[first].view(np.int64) != O[first].view(np.int64))[0][0])
            print(f"  row {first} column {k}: {R[first][k]!r} vs {O[first][k]!r}; max |diff| at the end {np.max(np.abs(R[n-1]-O[n-1])):.3e}")


if __name__ == "__main__":
    main()
