"""RBT-111 design adversary: the registered readout.py on synthetic summaries, for the three readings, the chance
qualifier, NOT A RESULT (missing and truncated arms), and drive.sh's per-slot summary call.

Each synthetic arm is a copy of RBT-96's committed s0-205 summaries with a constant added to champ_holistic_mean at
every checkpoint at generation >= 200 (so final_fifth moves by exactly that constant; generation 0 untouched):
constant = offset[arm] + N(0, sd) drawn per run from random.Random(111).  No simulation, no arm.

    python runs/RBT-111/adversary/synthetic.py SCRATCH      (writes synthetic roots under SCRATCH; prints synthetic.txt)
"""
import contextlib
import importlib.util
import io
import os
import random
import shutil
import subprocess
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
spec = importlib.util.spec_from_file_location("ro111", os.path.join(ROOT, "runs", "RBT-111", "readout.py"))
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import perm  # noqa: E402

SRC = os.path.join(ROOT, "runs", "RBT-96", "s0-205")


def make(root, offsets, sd, seeds=ro.SEEDS, rng_seed=111):
    rng = random.Random(rng_seed)
    shutil.rmtree(root, ignore_errors=True)
    truth = {}
    for s in seeds:
        for a in ro.ARMS:
            d = os.path.join(root, f"{a}-{s}")
            shutil.copytree(SRC, d)
            k = offsets[a] + rng.gauss(0, sd)
            truth[(a, s)] = k
            lines = open(os.path.join(d, "generations.txt")).read().splitlines()
            head = lines[0].split("\t")
            c = head.index("champ_holistic_mean")
            out = [lines[0]]
            for line in lines[1:]:
                f = line.split("\t")
                if f[c] and int(f[0]) >= 200:
                    f[c] = repr(float(f[c]) + k)
                out.append("\t".join(f))
            open(os.path.join(d, "generations.txt"), "w").write("\n".join(out) + "\n")
    return truth


def run(root, seeds=ro.SEEDS):
    buf = io.StringIO()
    t0 = time.time()
    with contextlib.redirect_stdout(buf):
        r = ro.main(root, seeds, from_summaries=True)
    return r, buf.getvalue(), time.time() - t0


def show(title, r, out, dt, extra=""):
    print(f"\n=== {title}  ({dt:.1f} s)")
    for line in out.splitlines():
        if line.startswith(("c0 ", "c12 ", "3. READING", "   note", "NOT A RESULT", "missing", "4. desc", "   delta", "   qualifier", "   (NOT")):
            print("   " + line)
    if extra:
        print(extra)


def main(scratch):
    os.makedirs(scratch, exist_ok=True)
    cases = [("salt0: s0 -0.082, run sd 0.062", {"s0": -0.082, "s1": 0, "s2": 0}, 0.062, "salt0", 111),
             ("keys: s2 +0.12, run sd 0.062", {"s0": 0, "s1": 0, "s2": 0.12}, 0.062, "keys", 112),
             ("chance: no offset, run sd 0.062", {"s0": 0, "s1": 0, "s2": 0}, 0.062, "chance", 113),
             ("chance with the qualifier: s0 -0.05, run sd 0.12 (the first rng seed tried)", {"s0": -0.05, "s1": 0, "s2": 0}, 0.12, "chance", 111)]
    for i, (title, off, sd, want, rs) in enumerate(cases):
        root = os.path.join(scratch, f"case{i}")
        truth = make(root, off, sd, rng_seed=rs)
        r, out, dt = run(root)
        rows = [(truth[("s0", s)], truth[("s1", s)], truth[("s2", s)]) for s in ro.SEEDS]
        # independent recomputation of the readout's two contrasts from the injected constants
        c0 = [(b + c) / 2 - a for a, b, c in rows]
        assert max(abs(x - y) for x, y in zip(c0, r["c0"])) < 1e-9
        pp = perm.perm_c0_p(rows)
        extra = (f"   check: readout c0 == injected (1e-9); readout sign-flip p(c0) {r['stats']['c0']['p']:.5f},"
                 f" permutation p(c0) {pp[0]:.5f}; complete={r['complete']}; reading={r['reading']}")
        show(title, r, out, dt, extra)
        if want:
            assert r["reading"] == want and r["complete"], (title, r["reading"])
    # NOT A RESULT: a missing arm; a truncated arm (last generation cut)
    root = os.path.join(scratch, "case2")
    shutil.copytree(os.path.join(root, "s1-224"), os.path.join(scratch, "keep"), dirs_exist_ok=True)
    shutil.rmtree(os.path.join(root, "s1-224"))
    r, out, dt = run(root)
    show("NOT A RESULT: s1-224 missing", r, out, dt, f"   check: complete={r['complete']}, seeds read {len(r['c0'])}")
    assert not r["complete"] and "NOT A RESULT" in out
    shutil.copytree(os.path.join(scratch, "keep"), os.path.join(root, "s1-224"))
    g = os.path.join(root, "s2-230", "generations.txt")
    lines = open(g).read().splitlines()
    open(g, "w").write("\n".join(lines[:-1]) + "\n")
    r, out, dt = run(root)
    show("NOT A RESULT: s2-230 truncated at generation 248", r, out, dt, f"   check: complete={r['complete']}, seeds read {len(r['c0'])}")
    assert not r["complete"] and "NOT A RESULT" in out
    # drive.sh's per-slot call: after slot 2 of a session, seed A has all three arms and seed B one
    root = os.path.join(scratch, "slot2")
    make(root, {"s0": 0, "s1": 0, "s2": 0}, 0.062, seeds=(217, 218))
    for a in ("s1", "s2"):
        shutil.rmtree(os.path.join(root, f"{a}-218"))
    cmd = [sys.executable, os.path.join(ROOT, "runs", "RBT-111", "readout.py"), "--from-summaries", "--seeds", "217,218", "--root", root]
    t0 = time.time()
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, timeout=120)
        verdict = f"returned in {time.time() - t0:.1f} s"
    except subprocess.TimeoutExpired:
        verdict = "STILL RUNNING after 120 s (killed): sign_flip_ci on one seed never leaves its while loop"
    print(f"\n=== drive.sh after slot 2 (s0/s1/s2-217 and s0-218 present): readout.py --seeds 217,218\n   {verdict}")


if __name__ == "__main__":
    main(sys.argv[1])
