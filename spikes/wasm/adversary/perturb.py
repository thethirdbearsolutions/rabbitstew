"""RBT-133 adversary: positive controls for the WASM fingerprint (can the instrument see a one-ULP change?).

    python spikes/wasm/adversary/perturb.py DIST SCRATCH            (one-input cases)  -> perturb.txt
    python spikes/wasm/adversary/perturb.py DIST SCRATCH --sweep    (every non-zero W entry, one at a time) -> perturb_sweep.txt

Copies a pack, changes ONE input by one ULP (or one digit), runs the WASM module, and reports whether the committed
fingerprint (check.py: sha256 of states.bin, plus result.txt) moves, at which state row the stream first differs from
the unperturbed run, and whether ticks.bin (sensors, activations, ctrl: NOT part of the fingerprint) moves.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PACKS = os.path.join(ROOT, "spikes", "wasm", "packs")


def run(dist: str, pack: str, out: str, mode: str) -> dict:
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    subprocess.run(["node", os.path.join(dist, "rbt_wasm.js"), mode, pack, out], check=True, capture_output=True)
    fp = subprocess.run([sys.executable, os.path.join(ROOT, "spikes", "wasm", "check.py"), pack, out], check=True, capture_output=True, text=True).stdout
    r = {"fp": fp.split(":", 1)[1].strip(), "states": np.fromfile(os.path.join(out, "states.bin"), dtype="<f8")}
    tk = os.path.join(out, "ticks.bin")
    r["ticks_sha"] = hashlib.sha256(open(tk, "rb").read()).hexdigest()[:16] if os.path.exists(tk) else None
    return r


def first_row(a: np.ndarray, b: np.ndarray, w: int):
    A, B = a.reshape(-1, w), b.reshape(-1, w)
    n = min(len(A), len(B))
    d = np.nonzero(np.any(A[:n].view(np.int64) != B[:n].view(np.int64), axis=1))[0]
    return (int(d[0]) if d.size else None), n


def bump_hex(tok: str) -> str:
    x = float.fromhex(tok)
    return float(np.nextafter(x, np.inf)).hex()


def edit_pack_line(pack: str, robot: int, key: str, index: int) -> str:
    """Bump entry `index` of line `key` of robot `robot` in pack.txt by one ULP; returns a description."""
    L = open(os.path.join(pack, "pack.txt")).read().split("\n")
    r = -1
    for i, ln in enumerate(L):
        t = ln.split()
        if t and t[0] == "robot":
            r = int(t[1])
        if r == robot and t and t[0] == key:
            old = t[1 + index]
            t[1 + index] = bump_hex(old)
            L[i] = " ".join(t)
            open(os.path.join(pack, "pack.txt"), "w").write("\n".join(L))
            return f"robot {robot} {key}[{index}] {old} -> {t[1 + index]}"
    raise SystemExit(f"no {key} for robot {robot}")


def first_nonzero_W(pack: str, robot: int) -> int:
    r = -1
    for ln in open(os.path.join(pack, "pack.txt")):
        t = ln.split()
        if t and t[0] == "robot":
            r = int(t[1])
        if r == robot and t and t[0] == "W":
            vals = [float.fromhex(v) for v in t[1:]]
            return next(i for i, v in enumerate(vals) if v != 0.0)
    raise SystemExit("no W")


def effector_row_W(pack: str, robot: int) -> int:
    """First non-zero W entry in the row of a unit that drives an actuator (so the change reaches ctrl directly)."""
    r, n, W, eff = -1, 0, None, []
    for ln in open(os.path.join(pack, "pack.txt")):
        t = ln.split()
        if t and t[0] == "robot":
            r = int(t[1])
        if r != robot or not t:
            continue
        if t[0] == "units":
            n = int(t[1])
        if t[0] == "W":
            W = [float.fromhex(v) for v in t[1:]]
        if t[0] == "a":
            eff += [int(u) for u in t[3:]]
    for u in eff:
        for j in range(n):
            if W[u * n + j] != 0.0:
                return u * n + j
    raise SystemExit("no effector row with a non-zero weight")


def first_unsaturated_ctrl(path: str, nu: int, after: int) -> int:
    a = np.fromfile(path, dtype="<f8")
    return next(i for i in range(after * nu, a.size) if abs(a[i]) < 0.99)


def bump_bin(path: str, index: int) -> str:
    a = np.fromfile(path, dtype="<f8")
    old = a[index]
    a[index] = np.nextafter(a[index], np.inf)
    a.tofile(path)
    return f"{os.path.basename(path)}[{index}] {old!r} -> {a[index]!r}"


def main() -> None:
    dist, scratch = sys.argv[1], sys.argv[2]
    import mujoco

    print(f"# module {dist}/rbt_wasm.wasm; each case = one input changed, everything else the committed pack")
    for bout in ("conventional-0", "holistic-0"):
        src = os.path.join(PACKS, bout)
        m = mujoco.MjModel.from_binary_path(os.path.join(src, "model.mjb"))
        w = 1 + m.nq + 2 * m.nv + m.na
        base = {mode: run(dist, src, os.path.join(scratch, bout, "base-" + mode), mode) for mode in ("bout", "openloop")}
        print(f"=== {bout}: unperturbed bout {base['bout']['fp'].splitlines()[0]}; ticks.bin {base['bout']['ticks_sha']}")
        cases = []
        cases.append(("bout", "W, robot 0, first non-zero entry", lambda p: edit_pack_line(p, 0, "W", first_nonzero_W(p, 0))))
        cases.append(("bout", "W, robot 1, first non-zero entry", lambda p: edit_pack_line(p, 1, "W", first_nonzero_W(p, 1))))
        cases.append(("bout", "W, robot 0, effector unit's row", lambda p: edit_pack_line(p, 0, "W", effector_row_W(p, 0))))
        cases.append(("bout", "bias, robot 1, first entry", lambda p: edit_pack_line(p, 1, "bias", 0)))
        cases.append(("openloop", "init_state qpos[2] (robot 0 root z)", lambda p: bump_bin(os.path.join(p, "init_state.bin"), 1 + 2)))
        cases.append(("openloop", "ctrl tick 100, actuator 0", lambda p: bump_bin(os.path.join(p, "ctrl.bin"), 100 * m.nu)))
        cases.append(("openloop", "ctrl, first |ctrl| < 0.99 from tick 100", lambda p: bump_bin(os.path.join(p, "ctrl.bin"), first_unsaturated_ctrl(os.path.join(p, "ctrl.bin"), m.nu, 100))))

        def xml_digit(p):
            x = open(os.path.join(p, "model.xml")).read()
            k = x.index('mass="') + len('mass="')
            j = k
            while x[j] not in '" ':
                j += 1
            old = x[k:j]
            new = old[:-1] + str((int(old[-1]) + 1) % 10)
            open(os.path.join(p, "model.xml"), "w").write(x[:k] + new + x[j:])
            return f"model.xml first mass {old} -> {new}"

        if 'mass="' in open(os.path.join(src, "model.xml")).read():
            cases.append(("bout", "model.xml last digit of one mass", xml_digit))
        for k, (mode, label, fn) in enumerate(cases):
            p = os.path.join(scratch, bout, f"pack{k}")
            shutil.rmtree(p, ignore_errors=True)
            shutil.copytree(src, p)
            what = fn(p)
            r = run(dist, p, os.path.join(scratch, bout, f"run{k}"), mode)
            fr, n = first_row(base[mode]["states"], r["states"], w)
            moved = r["fp"] != base[mode]["fp"]
            tk = "" if mode == "openloop" else f"; ticks.bin {'MOVES' if r['ticks_sha'] != base[mode]['ticks_sha'] else 'same'}"
            print(f"  {mode:8s} {label:38s} fingerprint {'MOVES' if moved else 'DOES NOT MOVE'}; first differing state row {fr} of {n}{tk}   ({what})")
    # the runner's guard against a missing/empty run
    e = os.path.join(scratch, "empty")
    os.makedirs(e, exist_ok=True)
    open(os.path.join(e, "states.bin"), "wb").close()
    fp = subprocess.run([sys.executable, os.path.join(ROOT, "spikes", "wasm", "check.py"), os.path.join(PACKS, "holistic-0"), e], capture_output=True, text=True).stdout.strip()
    print(f"empty states.bin -> check.py prints: {fp!r} (passes run_wasm.sh's 'stream sha256 [0-9a-f]' guard; fails only the diff against the reference)")


if __name__ == "__main__" and len(sys.argv) == 3:
    main()


def sweep(dist: str, scratch: str) -> None:
    """Every non-zero W entry of every robot, one at a time, +1 ULP: does the state fingerprint see it?"""
    for bout in ("conventional-0", "holistic-0"):
        src = os.path.join(PACKS, bout)
        base = run(dist, src, os.path.join(scratch, bout, "sweep-base"), "bout")
        L = open(os.path.join(src, "pack.txt")).read().split("\n")
        r, entries = -1, []
        for ln in L:
            t = ln.split()
            if t and t[0] == "robot":
                r = int(t[1])
            if t and t[0] == "W":
                entries += [(r, i) for i, v in enumerate(t[1:]) if float.fromhex(v) != 0.0]
        for robot in sorted({e[0] for e in entries}):
            mine = [e for e in entries if e[0] == robot]
            moved_states = moved_ticks = 0
            for _, i in mine:
                p = os.path.join(scratch, bout, "sweep-pack")
                shutil.rmtree(p, ignore_errors=True)
                shutil.copytree(src, p)
                edit_pack_line(p, robot, "W", i)
                res = run(dist, p, os.path.join(scratch, bout, "sweep-run"), "bout")
                moved_states += res["fp"] != base["fp"]
                moved_ticks += res["ticks_sha"] != base["ticks_sha"]
            print(f"sweep {bout} robot {robot}: {len(mine)} non-zero W entries, each +1 ULP alone: state fingerprint moves for "
                  f"{moved_states}, ticks.bin moves for {moved_ticks}")


if __name__ == "__main__" and len(sys.argv) > 3 and sys.argv[3] == "--sweep":
    sweep(sys.argv[1], sys.argv[2])
