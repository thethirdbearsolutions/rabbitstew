"""RBT-107 H1 adversary: the post-data depth.py change (#376, 9f8237a), with and without.  Print only.

    python runs/RBT-107/h1-adversary/depth_ab.py         (from a checkout of #376's head)

(1) Seed 29's co-evolved fauna: who is alive at T - 1 = 359, and when it was last alive, in each fresh arm.
(2) readout.py's full output three ways, compared line by line:
    A  as committed (depth.py with the early return);
    B  depth.py as at the pre-data commit 2f92005 (no early return), with only the empty-C0 StatisticsError caught at
       the call (so the rest of the readout can run at all; uncaught, it stops the readout in the DEPTH section);
    C  the DEPTH section skipped entirely.
    Every line outside the DEPTH section must be identical in A, B and C; the DEPTH lines of A and B must be identical.
"""
import contextlib
import importlib.util
import io
import os
import statistics
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(BASE))
PRE = "2f92005"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(mode):
    ro = _load(f"rbt107_readout_ab_{mode}", os.path.join(BASE, "readout.py"))
    if mode == "B":
        src = subprocess.run(["git", "show", f"{PRE}:runs/RBT-107/depth.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        p = os.path.join(os.environ.get("TMPDIR", "/tmp"), "rbt107_depth_pre.py")
        with open(p, "w") as f:
            f.write(src.replace('HERE = os.path.dirname(os.path.abspath(__file__))', f'HERE = {BASE!r}'))
        old = _load("rbt107_depth_pre", p)
        assert "if not c0" not in src

        def measures(arm, kind, T, reads):
            try:
                return old.measures(arm, kind, T, reads)
            except statistics.StatisticsError:
                assert not arm.alive_at(kind, T - 1)
                return {}
        ro.DEPTH.measures = measures
    if mode == "C":
        ro.depth_line = lambda sm, arms: {}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ro.main()
    return buf.getvalue().splitlines(), ro


def split(lines):
    i, j = lines.index("== DEPTH"), next(k for k, l in enumerate(lines) if l.startswith("== 0."))
    return lines[:i] + lines[j:], lines[i:j]


def main():
    A, ro = run("A")
    sm = ro.Sample("FRESH", ro.FRESH_SEEDS, True)
    print("== (1) seed 29, co-evolved (holistic)")
    for arm in ("base", "shift", "cull20"):
        a = ro.R92.Arm(sm.dir(arm, 29))
        alive = [t for t in range(0, a.last + 1) if a.alive_at("holistic", t)]
        print(f"  {arm:7s} alive at T-1=359: {len(a.alive_at('holistic', 359))}; last season with anyone alive: "
              f"{max(alive) if alive else 'none'}; designed alive at 359: {len(a.alive_at('conventional', 359))}")
    B, _ = run("B")
    C, _ = run("C")
    committed = open(os.path.join(BASE, "h1", "readout.txt")).read().splitlines()
    (a_rest, a_dep), (b_rest, b_dep), (c_rest, c_dep) = split(A), split(B), split(C)
    print("\n== (2) readout.py three ways")
    print(f"  A (as committed) equals h1/readout.txt: {A == committed} ({len(A)} lines)")
    print(f"  outside DEPTH: A == B {a_rest == b_rest}; A == C {a_rest == c_rest} ({len(a_rest)} lines)")
    print(f"  DEPTH section: A == B {a_dep == b_dep}")
    for l in a_dep:
        print(f"    A| {l}")
    for l in c_dep:
        print(f"    C| {l}")
    print("  (the DEPTH line names no seed: seed 29's co-evolved absence shows only as n=19; no 'UNREAD' is printed)")


if __name__ == "__main__":
    main()
