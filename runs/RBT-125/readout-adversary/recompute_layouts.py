"""RBT-125 readout adversary, pass 1: recompute §A's committed layouts (HP, U at G 2.5 / 10 / 0) from the committed
harness outputs, independently of prize_readout.py (recompute_A.py's parser), and add the paired contrasts the readout
states but does not test: G10 - G2.5, the base-income change, and the between-layout differences behind the
"HP > PW > U" ranking.

    python recompute_layouts.py GATE_DIR
"""
import os, sys
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], sys.argv[1]] if len(sys.argv) > 1 else sys.argv
import importlib.util
spec = importlib.util.spec_from_file_location("rA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "recompute_A.py"))
src = open(spec.origin).read().split("\nR = {c:")[0]   # take the parser and t() only
ns = {}; exec(compile(src, spec.origin, "exec"), ns)
parse, t, SEEDS = ns["parse"], ns["t"], ns["SEEDS"]
D = os.path.join(sys.argv[1], "prize")
CELLS = ["PW-G2.5", "PW-G10", "PW-G0", "HP-G2.5", "HP-G10", "HP-G0", "U-G2.5", "U-G10", "U-G0"]
R = {c: {s: parse(os.path.join(D, f"{c}-{s}.txt")) for s in SEEDS} for c in CELLS}
prize = {c: np.array([np.mean([d for _, d in R[c][s][1].values()]) for s in SEEDS]) for c in CELLS}
base = {c: np.array([np.mean([b for b, _ in R[c][s][1].values()]) for s in SEEDS]) for c in CELLS}
print("| cell | signed | prize t(9) | base |")
print("|---|---|---|---|")
for c in CELLS:
    print(f"| {c} | {sum(len(R[c][s][0]) for s in SEEDS)}/70 | {t(prize[c])} | {base[c].mean():.3f} |")


def same_signed(a, b):
    out = []
    for s in SEEDS:
        gs = [g for g in R[a][s][0] if g in R[b][s][0] and R[a][s][0][g] == R[b][s][0][g]]
        if gs:
            out.append(np.mean([R[a][s][1][g][1] for g in gs]) - np.mean([R[b][s][1][g][1] for g in gs]))
    return out


print("\n## paired by population, t(9)")
for L in ("PW", "HP", "U"):
    for G in ("G2.5", "G10"):
        a, b = f"{L}-{G}", f"{L}-G0"
        absm = (prize[a] + base[a]) - (prize[b] + base[b])
        print(f"{a} - {b}: {t(prize[a] - prize[b])};  same-signed {t(same_signed(a, b))};  absolute motif income {t(absm)}")
    print(f"{L}-G10 - {L}-G2.5: {t(prize[f'{L}-G10'] - prize[f'{L}-G2.5'])}")
    print(f"base change {L}-G2.5 - {L}-G0: {t(base[f'{L}-G2.5'] - base[f'{L}-G0'])};  {L}-G10 - {L}-G0: {t(base[f'{L}-G10'] - base[f'{L}-G0'])}")
print("\n## the ranking behind 'HP > PW > U' (channel contribution, cell - G0, at G2.5), differences paired by population")
ch = {L: prize[f"{L}-G2.5"] - prize[f"{L}-G0"] for L in ("PW", "HP", "U")}
for a, b in (("HP", "PW"), ("PW", "U"), ("HP", "U")):
    print(f"  {a} - {b}: {t(ch[a] - ch[b])}")
print("## the legacy prizes' ranking (G0 cells), paired")
for a, b in (("HP", "PW"), ("PW", "U"), ("HP", "U")):
    print(f"  {a}-G0 - {b}-G0: {t(prize[f'{a}-G0'] - prize[f'{b}-G0'])}")
print("## ratio (prize G2.5 / prize G0), point estimates only")
for L in ("PW", "HP", "U"):
    print(f"  {L}: {prize[f'{L}-G2.5'].mean() / prize[f'{L}-G0'].mean():.2f}")
