"""RBT-66 adversary, the one thing the report and I both left untested: does the positive
control hold on more than one body?

`axis_lesion.py control` installs its four circuits of known axis and sign on ONE Pioneer,
RBT-19's P-801 gen 590. The report names this limitation itself, and RBT-45's calibration is
the reason it matters: the same circuit installed on seven robots delivered the nominal gain
on five, DOUBLE on one, and SIGN-REVERSED on one. My attenuation measurement adds a second
reason -- the four bodies here pass between 0.007 and 0.98 of a perturbation to the Effector
output, a spread of 20x, so a control that passes where the gate is open says little about a
body where it is shut.

If the frozen probe recovers all four installed axes on every champion body, the verdicts'
instrument is validated where it was actually used. If it fails on one, the verdict scored on
that body is withdrawn by the pre-registration's own clause ("or the positive control fails").

Same four circuits, same installer, same seeds, same scoring quantity as `axis_lesion.py` --
imported from it rather than reimplemented, so this cannot drift from what it audits.

Usage: control_bodies.py [N_SEEDS]
"""
import importlib.util, os, sys

_d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "RBT-66", "axis_lesion.py")
_s = importlib.util.spec_from_file_location("axis_lesion", os.path.abspath(_d))
ax = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ax)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 16
BODIES = [
    ("brake  (baseline-801 g500)", "runs/RBT-66/data/baseline-801", "conventional", 500),
    ("throttle (RBT-19 g300)", "runs/RBT-66/data/RBT-19", "conventional", 300),
    ("sweep  (RBT-10-802free g590)", "runs/RBT-66/data/RBT-10-802free", "conventional", 590),
    ("control body (RBT-19 g590)", "runs/RBT-66/data/RBT-19", "conventional", 590),
]
CIRCUITS = [("STEERING +", 1.0, 0.0), ("STEERING -", -1.0, 0.0),
            ("THROTTLE +", 0.0, 1.0), ("THROTTLE -", 0.0, -1.0)]

print("# RBT-66 adversary: the positive control on every champion body, not just one")
print(f"n={N} paired seeds from {ax.SEED0}; circuits from fixed.drive_commands at k=1.0;")
print("native nose pathways zeroed in both arms, so each delta is the installed circuit alone.")
print("Scored on the frozen peak-over-8 column, the one the verdicts use.\n")
print("| body | circuit | steer | throttle | probe says | correct? | free-running says | correct? |")
print("|---|---|---|---|---|---|---|---|")
score = {"probe": 0, "free": 0, "n": 0}
for label, run, kind, gen in BODIES:
    g, cfg, ph = ax.load(run, kind, gen)
    for name, s, t in CIRCUITS:
        rows = ax.paired(g, cfg, ph, N, ax.installer(1.0, s, t))
        want = "steer" if s else "throttle"
        wsign = "+" if (s or t) > 0 else "-"
        import numpy as np
        pk_s = float(np.mean([r["dk_steer"] for r in rows]))
        pk_t = float(np.mean([r["dk_throttle"] for r in rows]))
        fr_s = float(np.mean([r["steer"] for r in rows]))
        fr_t = float(np.mean([r["throttle"] for r in rows]))

        def verdict(vs, vt):
            w = "steer" if abs(vs) > abs(vt) else "throttle"
            v = vs if w == "steer" else vt
            return f"{w} {'+' if v > 0 else '-'}", (w == want and ('+' if v > 0 else '-') == wsign)

        pv, pok = verdict(pk_s, pk_t)
        fv, fok = verdict(fr_s, fr_t)
        score["probe"] += pok; score["free"] += fok; score["n"] += 1
        print(f"| {label} | {name} | {pk_s:+.4f} | {pk_t:+.4f} | {pv} | "
              f"{'YES' if pok else '**NO**'} | {fv} | {'YES' if fok else '**NO**'} |")
print(f"\n**Frozen peak-over-8: {score['probe']} of {score['n']}. "
      f"Free-running lesion: {score['free']} of {score['n']}.**")
