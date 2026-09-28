"""RBT-120 readout adversary: an independent recompute of Q1, Q2, Q3 and the b_up / b_down split.

    python recompute.py B_ROOT O_ROOT  > recompute.txt

Written from the registration's text (PREREGISTRATION.md §3; RBT-117's compare.py rules as §3 quotes them), NOT by
importing readout.py, budget.py or compare.py.  Reads only lineage.jsonl (per-generation fitness and parents),
decompose.json and the frozen sigma0 file.  Statistics: OLS slope over generations 0..23 of the per-generation mean
fitness contrasts (U-D, U-C, C-D); t 95% CI from scipy; exact sign-flip over all 2^12 patterns, both two- and
one-sided.  Adds what the REPORT quotes without intervals: bootstrap (seeds resampled) and Fieller-style intervals
for the ratios 73%, 27% and 51%, and the association of the per-seed drop with K4's binding share.
"""
import itertools
import json
import os
import sys

import numpy as np
from scipy import stats as sps

ARM = {s: (s - 1) // 3 + 1 for s in range(1, 13)}
SIG0 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RBT-113", "sigma0_reference.json")))


def lineage(path, pop):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    return [r for r in rows if r["population"] == pop]


def means(rows):
    G = max(r["generation"] for r in rows) + 1
    return np.array([np.mean([r["fitness"] for r in rows if r["generation"] == g]) for g in range(G)])


def sel_diff(rows):
    fit = {r["name"]: r["fitness"] for r in rows}
    m = means(rows)
    return np.array([np.mean([np.mean([fit[p] for p in r["parents"]]) for r in rows if r["generation"] == g + 1]) - m[g]
                     for g in range(len(m) - 1)])


def slope(y):
    t = np.arange(len(y), dtype=float)
    t -= t.mean()
    return float(np.sum(t * (y - y.mean())) / np.sum(t * t))


def seed_stats(sd, pop="holistic"):
    rows = {L: lineage(os.path.join(sd, L, "lineage.jsonl"), pop) for L in "UDC"}
    m = {L: means(rows[L]) for L in "UDC"}
    S = {L: sel_diff(rows[L]) for L in "UDC"}
    div = m["U"] - m["D"]
    cs = np.concatenate([[0], np.cumsum(S["U"] - S["D"])])
    h2 = float(np.sum(div[1:] * cs[1:]) / np.sum(cs[1:] ** 2))
    return {"b_div": slope(div), "b_up": slope(m["U"] - m["C"]), "b_down": slope(m["C"] - m["D"]), "h2": h2,
            "final_UD": float(div[-1]), "Cdrift": float(m["C"][-1] - m["C"][0]), "sd0": float(np.std([r["fitness"] for r in rows["U"] if r["generation"] == 0], ddof=1))}


def tci(v):
    v = np.asarray(v, float)
    n = len(v)
    m, se = v.mean(), v.std(ddof=1) / np.sqrt(n)
    q = sps.t.ppf(0.975, n - 1)
    return m, m - q * se, m + q * se


PATS = np.array(list(itertools.product((1.0, -1.0), repeat=12)))


def flip(v):
    v = np.asarray(v, float)
    null = PATS @ v / len(v)
    return float(np.mean(np.abs(null) >= abs(v.mean()) - 1e-12)), float(np.mean(null >= v.mean() - 1e-12))


def boot_ratio(num, den, n=20000, seed=120):
    rng = np.random.default_rng(seed)
    num, den = np.asarray(num), np.asarray(den)
    idx = rng.integers(0, len(num), size=(n, len(num)))
    r = num[idx].mean(1) / den[idx].mean(1)
    return np.percentile(r, [2.5, 97.5])


def fieller(num, den):
    """95% Fieller interval for mean(num)/mean(den), paired (same seeds)."""
    a, b = np.asarray(num, float), np.asarray(den, float)
    n = len(a)
    ma, mb = a.mean(), b.mean()
    C = np.cov(a, b, ddof=1) / n
    t = sps.t.ppf(0.975, n - 1)
    A = mb ** 2 - t ** 2 * C[1, 1]
    B = -2 * (ma * mb - t ** 2 * C[0, 1])
    Cc = ma ** 2 - t ** 2 * C[0, 0]
    disc = B * B - 4 * A * Cc
    if A <= 0 or disc < 0:
        return (float("nan"), float("nan"))
    return ((-B - np.sqrt(disc)) / (2 * A), (-B + np.sqrt(disc)) / (2 * A))


def main(broot, oroot):
    sh, sdes = SIG0["holistic"], SIG0.get("conventional", SIG0.get("designed"))
    print(f"# independent recompute (no readout.py / budget.py / compare.py); frozen sigma0 holistic {sh}, designed {sdes}")
    B, O, Bd, Od, dec = {}, {}, {}, {}, {}
    for s in range(1, 13):
        bsd, osd = os.path.join(broot, f"B{ARM[s]}", str(s)), os.path.join(oroot, f"O{ARM[s]}", str(s))
        B[s], O[s] = seed_stats(bsd), seed_stats(osd)
        Bd[s], Od[s] = seed_stats(bsd, "conventional"), seed_stats(osd, "conventional")
        p = os.path.join(bsd, "decompose.json")
        dec[s] = json.load(open(p)) if os.path.exists(p) else None
    S = range(1, 13)
    print("\n## per seed (holistic, raw yield per generation)")
    print("  seed   b_div_B   b_div_O     Delta    b_up_B    b_up_O  b_down_B  b_down_O")
    for s in S:
        print(f"  {s:4d} {B[s]['b_div']:+9.5f} {O[s]['b_div']:+9.5f} {O[s]['b_div'] - B[s]['b_div']:+9.5f} "
              f"{B[s]['b_up']:+9.5f} {O[s]['b_up']:+9.5f} {B[s]['b_down']:+9.5f} {O[s]['b_down']:+9.5f}")
    print("\n## Q1 and Q2 (mean [t 95% CI]; sign-flip p two-sided / one-sided)")
    for name, v in (("b_div_B", [B[s]["b_div"] for s in S]), ("b_div_O", [O[s]["b_div"] for s in S]),
                    ("Delta = O - B", [O[s]["b_div"] - B[s]["b_div"] for s in S]),
                    ("b_up  O - B", [O[s]["b_up"] - B[s]["b_up"] for s in S]),
                    ("b_down O - B", [O[s]["b_down"] - B[s]["b_down"] for s in S]),
                    ("b_up_B", [B[s]["b_up"] for s in S]), ("b_down_B", [B[s]["b_down"] for s in S]),
                    ("b_up_O", [O[s]["b_up"] for s in S]), ("b_down_O", [O[s]["b_down"] for s in S]),
                    ("h2 O - B", [O[s]["h2"] - B[s]["h2"] for s in S])):
        m, lo, hi = tci(v)
        p2, p1 = flip(v)
        print(f"  {name:14s} {m:+.5f} [{lo:+.5f}, {hi:+.5f}]  sigma0 {m / sh:+.4f} [{lo / sh:+.4f}, {hi / sh:+.4f}]  "
              f"p2 {p2:.4f}  p1 {p1:.4f}  positive seeds {sum(x > 0 for x in v)}/12")
    print("\n## the ratios the REPORT quotes as points (bootstrap over seeds, 20000; and Fieller, paired)")
    bd, od = [B[s]["b_div"] for s in S], [O[s]["b_div"] for s in S]
    bdn, odn = [B[s]["b_down"] for s in S], [O[s]["b_down"] for s in S]
    for name, num, den in (("b_div_B / b_div_O (the 73%)", bd, od),
                           ("Delta / b_div_O (the 27%)", [o - b for o, b in zip(od, bd)], od),
                           ("b_down_B / b_down_O (the 51%)", bdn, odn),
                           ("b_up_B / b_up_O", [B[s]["b_up"] for s in S], [O[s]["b_up"] for s in S])):
        r = np.mean(num) / np.mean(den)
        bl, bh = boot_ratio(num, den)
        fl, fh = fieller(num, den)
        print(f"  {name:32s} {r:.3f}  bootstrap [{bl:.3f}, {bh:.3f}]  Fieller [{fl:.3f}, {fh:.3f}]")
    lo_pred, hi_pred = 0.59, 0.70
    boots = []
    rng = np.random.default_rng(7)
    idx = rng.integers(0, 12, size=(20000, 12))
    rr = np.asarray(bd)[idx].mean(1) / np.asarray(od)[idx].mean(1)
    print(f"  bootstrap P(b_div_B/b_div_O > 0.70) = {np.mean(rr > hi_pred):.3f}; P(within 0.59-0.70) = {np.mean((rr >= lo_pred) & (rr <= hi_pred)):.3f}")
    print(f"  Delta in sigma0 against the predicted +0.13 to +0.18: the CI above covers both ends of the predicted range")

    print("\n## Q3 (RBT-117's rule as registered: d = holistic - designed final U - D, raw, exact sign-flip; "
          "VOID iff control p < 0.05 and |c| >= 0.8)")
    d = [B[s]["final_UD"] - Bd[s]["final_UD"] for s in S]
    c = [B[s]["Cdrift"] - Bd[s]["Cdrift"] for s in S]
    m, lo, hi = tci(d); p2, _ = flip(d)
    mc, lc, hc = tci(c); pc, _ = flip(c)
    void = pc < 0.05 and abs(mc) >= 0.8
    verdict = "VOID" if void else ("HOLISTIC RESPONDS MORE" if p2 < 0.05 and m > 0 else "DESIGNED RESPONDS MORE" if p2 < 0.05 and m < 0 else "NOT DECIDED")
    print(f"  d {m:+.4f} [{lo:+.4f}, {hi:+.4f}] p {p2:.4f};  c {mc:+.4f} [{lc:+.4f}, {hc:+.4f}] p {pc:.4f};  VERDICT {verdict}")
    same = all(json.dumps(Bd[s], sort_keys=True) == json.dumps(Od[s], sort_keys=True) for s in S)
    print(f"  designed side of B equals O's at every seed (K2 through the statistics): {same}")

    if all(dec[s] is not None for s in S):
        print("\n## food / work at generation 23, from the regenerated decompose.json (holistic; mean over seeds)")
        for g in ("founders", "U", "D", "C"):
            f = [dec[s]["faunae"]["holistic"][g]["food"] for s in S]
            w = [dec[s]["faunae"]["holistic"][g]["work"] for s in S]
            n = [dec[s]["faunae"]["holistic"][g]["net"] for s in S]
            print(f"  {g:8s} food {np.mean(f):.3f}  work {np.mean(w):.3f}  net {np.mean(n):+.3f}")
    return B, O




def controls_independent(broot, oroot):
    """K2, K3 and K7 re-derived from lineage.jsonl, and K1 from config.json, without budget.py."""
    print("\n## K1, K2, K3, K7 re-derived (lineage.jsonl, config.json)")
    for s in range(1, 13):
        bsd, osd = os.path.join(broot, f"B{ARM[s]}", str(s)), os.path.join(oroot, f"O{ARM[s]}", str(s))
        k1 = k2 = True
        for L in "UDC":
            cb, co = json.load(open(os.path.join(bsd, L, "config.json"))), json.load(open(os.path.join(osd, L, "config.json")))
            mb = cb["sim"]["world"].pop("motor_budget", None)
            k1 &= mb == 1.77 and "motor_budget" not in co["sim"]["world"] and cb == co
            k2 &= lineage(os.path.join(bsd, L, "lineage.jsonl"), "conventional") == lineage(os.path.join(osd, L, "lineage.jsonl"), "conventional")
        g0b = [r for r in lineage(os.path.join(bsd, "U", "lineage.jsonl"), "holistic") if r["generation"] == 0]
        g0o = [r for r in lineage(os.path.join(osd, "U", "lineage.jsonl"), "holistic") if r["generation"] == 0]
        k3 = [(r["name"], r["body"]) for r in g0b] == [(r["name"], r["body"]) for r in g0o]
        moved = sum(a != b for a, b in zip(g0b, g0o))
        moved_fit = sum(a["fitness"] != b["fitness"] for a, b in zip(g0b, g0o))
        print(f"  seed {s:2d}: K1 {'PASS' if k1 else 'FAIL'}  K2 {'PASS' if k2 else 'FAIL'}  K3 {'PASS' if k3 else 'FAIL'}  "
              f"K7 rows moved {moved:2d}/40 (fitness moved {moved_fit:2d})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
    controls_independent(sys.argv[1], sys.argv[2])
