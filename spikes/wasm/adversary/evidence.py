"""RBT-133 adversary: re-derivations from the committed evidence only (no simulation).

    python spikes/wasm/adversary/evidence.py

1. What the two packed bouts exercise: sensor kinds and transfer functions per robot, whether the robot drives any
   actuator (only those can reach the state fingerprint), and how often ctrl sits at its clip.
2. gen-0 bout identity per CI platform against the x86 reference (fitness AND distance hex), and the holistic rows
   beside the laptop's (RBT-85 base-201) row.
3. The numpy/libm probe: which primitive agrees with x86 on which platform.
4. What the committed step-1 readouts contain: are the open-loop replay results (replay-physics, replay-brain) in them?
"""

from __future__ import annotations

import glob
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
W = os.path.join(ROOT, "spikes", "wasm")
KINDS = ["contact", "oscillator", "target", "opponent", "target_distance", "opponent_distance", "up", "velocity", "height", "joint_angle", "joint_velocity"]
FUNCS = ["tanh", "sin", "abs", "relu", "sign", "integrate", "differentiate"]


def coverage() -> None:
    print("1. coverage of the packed bouts")
    for b in ("conventional-0", "holistic-0"):
        robots = []
        for ln in open(os.path.join(W, "packs", b, "pack.txt")):
            t = ln.split()
            if not t:
                continue
            if t[0] == "robot":
                robots.append({"sensors": [], "funcs": [], "acts": 0, "ball": 0})
            elif t[0] == "func":
                robots[-1]["funcs"] = [int(x) for x in t[1:]]
            elif t[0] == "s":
                robots[-1]["sensors"].append(KINDS[int(t[2])])
                robots[-1]["ball"] += int(t[7])
            elif t[0] == "actuators":
                robots[-1]["acts"] = int(t[1])
        for k, r in enumerate(robots):
            f = sorted({FUNCS[x] for x in r["funcs"] if x >= 0})
            print(f"  {b} robot {k}: drives {r['acts']} actuators; sensor kinds {sorted(set(r['sensors']))}; ball-joint sensors {r['ball']}; transfer functions {f}")
        used = {s for r in robots if r["acts"] for s in r["sensors"]}
        fused = {FUNCS[x] for r in robots if r["acts"] for x in r["funcs"] if x >= 0}
        print(f"    reaching the state stream (robots that drive actuators): sensors {sorted(used)}; functions {sorted(fused)}")
        c = np.load(os.path.join(W, "locate", "ref-x86", b, "ctrl.npy"))
        print(f"    ctrl at exactly +-1 (clipped): {np.mean(np.abs(c) == 1.0):.0%} of entries; per-actuator std {np.round(c.std(0), 3).tolist()}")
    never = set(KINDS) - {"contact", "target", "opponent", "target_distance", "opponent_distance", "up", "velocity", "joint_velocity"}
    print(f"  never reaching any state stream: sensors {sorted(never)} (oscillator only on holistic robot 1, which drives nothing); functions sin, sign, integrate (abs, relu only on holistic robot 1)")


def gen0() -> None:
    print("2. gen-0 bouts against the x86 reference (fitness hex and distance hex)")
    ref = [ln.split() for ln in open(os.path.join(W, "locate", "ref-x86", "gen0.txt")) if " bout " in ln]
    for p in sorted(glob.glob(os.path.join(W, "locate", "ci-run-37157969294", "*", "gen0.txt"))):
        rows = [ln.split() for ln in open(p) if " bout " in ln]
        same = sum(a[9] == b[9] and a[11] == b[11] for a, b in zip(ref, rows))
        print(f"  {p.split(os.sep)[-2]:18s} {same}/{len(ref)} bouts identical")
    lap = open(os.path.join(ROOT, "runs", "RBT-85", "base-201", "generations.txt")).read().split("\n")
    hdr, g0 = lap[0].split("\t"), lap[1].split("\t")
    row = dict(zip(hdr, g0))
    mac = [ln.split() for ln in open(os.path.join(W, "locate", "ci-run-37157969294", "macos-15", "gen0.txt")) if ln.startswith("h bout")]
    fits = np.array([float(r[8]) for r in mac])
    print(f"  laptop (RBT-85 base-201) gen 0: h_best {row['h_best']} h_mean {row['h_mean']}; M1: h_best {fits.max():.6f} h_mean {fits.mean():.6f}")
    need = (fits.max() - float(row["h_best"])) / len(fits)
    print(f"  if the laptop differed from the M1 in the h_best bout alone, h_mean would differ by >= {need:.6f}; it differs by "
          f"{abs(fits.mean() - float(row['h_mean'])):.6f}: so at least two holistic bouts differ, with deltas cancelling to < 1e-6 in the mean")


def numpy_probe() -> None:
    print("3. numpy/libm probe: agreement with x86 (Intel, this repo's ref) per CI platform")
    def load(p):
        return {ln[:28].strip(): ln.split()[-1] for ln in open(p) if not ln.startswith("#") and ln.strip()}
    ref = load(os.path.join(W, "locate", "ref-x86", "numpy-probe.txt"))
    plats = ["ubuntu-24.04", "ubuntu-24.04-arm", "macos-15"]
    other = {p: load(os.path.join(W, "locate", "ci-run-37157969294", p, "numpy-probe.txt")) for p in plats}
    print(f"  {'primitive':28s} " + " ".join(f"{p:>17s}" for p in plats))
    for k, v in ref.items():
        print(f"  {k:28s} " + " ".join(f"{('same' if other[p][k] == v else 'DIFFERS'):>17s}" for p in plats))
    print(f"  same machine, np.tanh vs math.tanh: {'same' if ref['np.tanh'] == ref['math.tanh'] else 'differ'}")


def readouts() -> None:
    print("4. are the step-1 open-loop replays in the committed readouts?")
    hits = []
    for p in glob.glob(os.path.join(W, "**", "*"), recursive=True):
        if os.path.isfile(p) and not p.endswith((".py", ".npy", ".mjb", ".bin")) and os.sep + "adversary" + os.sep not in p:
            s = open(p, errors="ignore").read()
            if "open-loop physics:" in s or "brain replay on recorded sensors" in s:
                hits.append(os.path.relpath(p, ROOT))
    print(f"  files containing replay-physics / replay-brain output: {hits if hits else 'NONE'}")
    print("  (ci.sh prints them to the job log only: its tee/redirects cover numpy-probe and gen0, not the replays)")
    fp = open(os.path.join(W, "ci-run-37158742068", "wasm-fingerprints.txt")).read()
    print(f"  CI WASM fingerprints mention ticks.bin: {'yes' if 'tick' in fp else 'NO'} (check.py hashes states.bin and prints result.txt)")


def main() -> None:
    coverage()
    gen0()
    numpy_probe()
    readouts()


if __name__ == "__main__":
    main()
