"""RBT-125 readout adversary: recompute §A from the committed harness outputs, independently of prize_readout.py.

Parses each runs/RBT-125/gate/prize/<cell>-<seed>.txt (the RBT-103 harness's own printout) line by line: the direction
table's sign column, the income table's per-body base and delta, and the mechanism block's motif / rotated-decoy means.
Recomputes, with scipy's t quantile:
  * the prize per population (mean over signed bodies of the delta) and its t(9) interval, all 10 counted;
  * (motif - decoy) per population and its t(9) interval;
  * the channel contrast (cell - PW-G0) paired by population, on all bodies and on bodies signed the same in both;
  * NOT registered, added here: the contrast in ABSOLUTE motif income (base + delta), i.e. without crediting the
    channel for lowering the bodies' own base; and the base change itself.

    python recompute_A.py <gate dir>
"""
import os, re, sys
import numpy as np
from scipy import stats

D = os.path.join(sys.argv[1], "prize")
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def parse(path):
    txt = open(path).read().splitlines()
    sign, body, mot, dec, zeros = {}, {}, None, None, None
    sec = None
    for ln in txt:
        if ln.startswith("## Direction"): sec = "dir"
        elif ln.startswith("## Install"): sec = "inst"
        elif ln.startswith("## Income"): sec = "inc"
        elif ln.startswith("## Mechanism"): sec = "mech"
        if sec == "dir" and ln.startswith("g"):
            parts = [p.strip() for p in ln.split("|")]
            g = int(parts[0][1:]); s = parts[3]
            if s in ("+1", "-1"): sign[g] = int(s)
        if sec == "inc" and ln.startswith("g"):
            f = ln.replace("|", " ").split()
            body[int(f[0][1:])] = (float(f[2]), float(f[3]))  # base, delta
        if sec == "inc" and re.match(r"^\s+3\s+6 \|", ln):
            zeros = tuple(int(x) for x in re.search(r"(\d+)/(\d+) \|", ln).groups())
        if sec == "mech":
            m = re.match(r"^\s+motif\s+([+-][\d.]+)", ln)
            if m: mot = float(m.group(1))
            m = re.match(r"^\s+rotated decoy\s+([+-][\d.]+)", ln)
            if m: dec = float(m.group(1))
    assert set(body) == set(sign), (path, body.keys(), sign.keys())
    return sign, body, mot, dec, zeros


def t(x):
    x = np.asarray(x, float); n = len(x)
    h = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)
    return f"{x.mean():+.3f} [{x.mean() - h:+.3f}, {x.mean() + h:+.3f}]  (n {n})"


R = {c: {s: parse(os.path.join(D, f"{c}-{s}.txt")) for s in SEEDS} for c in ("PW-G2.5", "PW-G10", "PW-G0")}
for c, rows in R.items():
    prize = [np.mean([d for _, d in r[1].values()]) for r in rows.values()]
    base = [np.mean([b for b, _ in r[1].values()]) for r in rows.values()]
    md = [r[2] - r[3] for r in rows.values()]
    z = np.sum([r[4] for r in rows.values()], axis=0)
    chk = [abs(np.mean([d for _, d in r[1].values()]) - r[2]) < 6e-4 for r in rows.values()]
    print(f"{c:8s} signed {sum(len(r[0]) for r in rows.values())}/70  prize {t(prize)}  motif-decoy {t(md)}  base {np.mean(base):.3f}  "
          f"zeros {z[0]}/{z[1]}  per-pop prize == harness motif line: {all(chk)}")
    print("   per pop prize: " + " ".join(f"{s}:{p:+.3f}" for s, p in zip(SEEDS, prize)))
print()
for c in ("PW-G2.5", "PW-G10"):
    A, B = R[c], R["PW-G0"]
    d_all = [np.mean([v[1] for v in A[s][1].values()]) - np.mean([v[1] for v in B[s][1].values()]) for s in SEEDS]
    same, dropped = [], 0
    for s in SEEDS:
        gs = [g for g in A[s][0] if g in B[s][0] and A[s][0][g] == B[s][0][g]]
        dropped += 7 - len(gs)
        if gs:
            same.append(np.mean([A[s][1][g][1] for g in gs]) - np.mean([B[s][1][g][1] for g in gs]))
    absm = [np.mean([sum(v) for v in A[s][1].values()]) - np.mean([sum(v) for v in B[s][1].values()]) for s in SEEDS]
    dbase = [np.mean([v[0] for v in A[s][1].values()]) - np.mean([v[0] for v in B[s][1].values()]) for s in SEEDS]
    print(f"{c} - PW-G0: prize contrast {t(d_all)}")
    print(f"   same-signed bodies {t(same)}; bodies dropped (sign differs) {dropped}/70")
    print(f"   ABSOLUTE motif income (base + delta) {t(absm)}   base change {t(dbase)}")
