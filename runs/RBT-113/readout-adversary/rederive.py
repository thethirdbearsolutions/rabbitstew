"""RBT-113/117 readout adversary: the key numbers re-derived from lineage.jsonl and decompose.json with independent
code (no import of readout.py or compare.py), plus RBT-117 robustness splits that are NOT registered (descriptive).

    rederive.py > rederive.txt        (run from the repository root; needs only the committed evidence)
"""
import glob
import itertools
import json
import os

import numpy as np

R = "runs/RBT-113"
T975 = {11: 2.201, 23: 2.069}


def ci(v):
    v = np.asarray(v, float)
    m, se = v.mean(), v.std(ddof=1) / np.sqrt(len(v))
    q = T975[len(v) - 1]
    return f"{m:+.4f} [{m - q * se:+.4f}, {m + q * se:+.4f}]"


def pflip(v):
    v = np.asarray(v, float)
    obs = abs(v.mean())
    tot = hit = 0
    for s in itertools.product((1, -1), repeat=len(v)):
        tot += 1
        hit += abs(np.dot(s, v) / len(v)) >= obs - 1e-12
    return hit / tot


def slope(y):
    t = np.arange(len(y))
    t = t - t.mean()
    return float(np.sum(t * (y - np.mean(y))) / np.sum(t * t))


def series(path, fauna):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    rows = [r for r in rows if r["population"] == fauna]
    G = max(r["generation"] for r in rows) + 1
    fit = {r["name"]: r["fitness"] for r in rows}
    by = [[r for r in rows if r["generation"] == t] for t in range(G)]
    m = np.array([np.mean([r["fitness"] for r in g]) for g in by])
    S = np.array([np.mean([np.mean([fit[p] for p in r["parents"]]) for r in by[t + 1]]) - m[t] for t in range(G - 1)])
    return m, S, float(np.std([r["fitness"] for r in by[0]], ddof=1))


def seed_dirs():
    out = []
    for d in sorted(glob.glob(f"{R}/O[1-4]/[0-9]*") + glob.glob(f"{R}/Z[1-4]/Z*")):
        n = os.path.basename(d)
        out.append((d, "Z" if n.startswith("Z") else "", int(n.lstrip("Z"))))
    return out


def stats(d, fauna):
    s = {L: series(f"{d}/{L}/lineage.jsonl", fauna) for L in "UDC"}
    m = {L: s[L][0] for L in "UDC"}
    S = {L: s[L][1] for L in "UDC"}
    div = m["U"] - m["D"]
    cs = np.cumsum(S["U"] - S["D"])
    return {"b_div": slope(div), "h2": float(np.dot(div[1:], cs) / np.dot(cs, cs)), "b_up": slope(m["U"] - m["C"]),
            "b_down": slope(m["C"] - m["D"]), "D": float(div[-1]), "up": float(m["U"][-1] - m["C"][-1]),
            "down": float(m["C"][-1] - m["D"][-1]), "Cdrift": float(m["C"][-1] - m["C"][0]), "sd0": s["U"][2]}


def main():
    SD = seed_dirs()
    st = {(op, seed, f): stats(d, f) for d, op, seed in SD for f in ("holistic", "conventional")}
    dec = {(op, seed): json.load(open(f"{d}/decompose.json")) for d, op, seed in SD}
    seeds = sorted({s for _, _, s in SD})
    sig = {f: float(np.median([st[(op, s, f)]["sd0"] for _, op, s in SD])) for f in ("holistic", "conventional")}
    print(f"# independent re-derivation; sigma0 holistic {sig['holistic']:.6f} conventional {sig['conventional']:.6f}")
    hol = lambda k: [np.mean([st[(op, s, "holistic")][k] for op in ("", "Z")]) for s in seeds]  # noqa: E731
    con = lambda k, op="": [st[(op, s, "conventional")][k] for s in seeds]  # noqa: E731
    print("\n## RBT-113")
    for lab, get, sg in (("holistic (per seed, 2 replicates)", hol, sig["holistic"]),
                         ("designed default", con, sig["conventional"]),
                         ("designed Z", lambda k: con(k, "Z"), sig["conventional"])):
        b = np.array(get("b_div"))
        print(f"{lab}: b_div raw {ci(b)} p {pflip(b):.4f};  sigma0 {ci(b / sg)};  h2 {ci(get('h2'))} p {pflip(get('h2')):.4f};"
              f"  b_up {ci(np.array(get('b_up')) / sg)} p {pflip(get('b_up')):.4f};  b_down {ci(np.array(get('b_down')) / sg)} p {pflip(get('b_down')):.4f}")
    dz = np.array(con("b_div", "Z")) - np.array(con("b_div"))
    print(f"operator Z - default, b_div sigma0: {ci(dz / sig['conventional'])}  (NO CHANGE iff the CI lies inside +-0.05)")

    print("\n## RBT-113 D1 checks (decompose.json)")
    for f in ("holistic", "conventional"):
        for g in ("founders", "U", "D", "C"):
            if f == "holistic":
                fo = [np.mean([dec[(op, s)]["faunae"][f][g]["food"] for op in ("", "Z")]) for s in seeds]
                wo = [np.mean([dec[(op, s)]["faunae"][f][g]["work"] for op in ("", "Z")]) for s in seeds]
            else:
                fo = [dec[("", s)]["faunae"][f][g]["food"] for s in seeds]
                wo = [dec[("", s)]["faunae"][f][g]["work"] for s in seeds]
            print(f"  {f:12s} {g:8s} food {np.mean(fo):.3f}  work {np.mean(wo):.3f}  (seeds with food up/down vs founders listed below)")
    fh = lambda g, q: np.array([np.mean([dec[(op, s)]["faunae"]["holistic"][g][q] for op in ("", "Z")]) for s in seeds])  # noqa: E731
    print(f"  holistic U/founders food ratio {fh('U', 'food').mean() / fh('founders', 'food').mean():.1f}x;  D/founders work ratio"
          f" {fh('D', 'work').mean() / fh('founders', 'work').mean():.1f}x;  D/C work ratio {fh('D', 'work').mean() / fh('C', 'work').mean():.1f}x")
    print(f"  seeds where holistic U food > founders food: {int(np.sum(fh('U', 'food') > fh('founders', 'food')))}/12;"
          f"  where U food > C food: {int(np.sum(fh('U', 'food') > fh('C', 'food')))}/12;  min U food {fh('U', 'food').min():.3f}")
    fr = [dec[(op, s)]["faunae"]["holistic"]["U"]["food"] for op in ("", "Z") for s in seeds]
    print(f"  holistic U food per seed DIRECTORY (24): min {min(fr):.3f}, below 0.3: {sum(x < 0.3 for x in fr)}")
    pr = [dec[(op, s)]["faunae"]["holistic"]["U"]["p_food"] for op in ("", "Z") for s in seeds]
    print(f"  holistic U P(member ate anything on the 4 draws): mean {np.mean(pr):.2f}, min {min(pr):.2f}")
    ps = [dec[(op, s)]["faunae"]["holistic"]["D"]["p_still"] for op in ("", "Z") for s in seeds]
    print(f"  holistic D P(member does no work): mean {np.mean(ps):.2f}")

    print("\n## RBT-117 (12 default seeds)")
    Dh = np.array([st[("", s, "holistic")]["D"] for s in seeds])
    Dd = np.array([st[("", s, "conventional")]["D"] for s in seeds])
    d = Dh - Dd
    c = np.array([st[("", s, "holistic")]["Cdrift"] - st[("", s, "conventional")]["Cdrift"] for s in seeds])
    print(f"primary d {ci(d)}  exact sign-flip p {pflip(d):.4f}  positive {int(np.sum(d > 0))}/12")
    print(f"control c {ci(c)}  p {pflip(c):.4f}  |mean c| {abs(c.mean()):.3f} vs C_BOUND 0.8 -> VOID {pflip(c) < 0.05 and abs(c.mean()) >= 0.8}")
    for k, lab in (("up", "up half U - C"), ("down", "down half C - D")):
        x = np.array([st[("", s, "holistic")][k] - st[("", s, "conventional")][k] for s in seeds])
        print(f"  NOT REGISTERED, descriptive: {lab}, holistic - designed: {ci(x)}  p {pflip(x):.4f}  positive {int(np.sum(x > 0))}/12")
    fd = lambda f, a, b, q: np.array([dec[("", s)]["faunae"][f][a][q] - dec[("", s)]["faunae"][f][b][q] for s in seeds])  # noqa: E731
    for q, sgn in (("food", 1), ("net", 1)):
        x = fd("holistic", "U", "D", q) - fd("conventional", "U", "D", q)
        print(f"  NOT REGISTERED, descriptive: U - D in {q} (decompose, 4 fixed draws), holistic - designed: {ci(x)}  p {pflip(x):.4f}  positive {int(np.sum(x > 0))}/12")
    # counterfactual: the down line may not waste more work than the designed body's D line at that seed
    cap = np.array([dec[("", s)]["faunae"]["conventional"]["D"]["work"] for s in seeds])
    hDw = np.array([dec[("", s)]["faunae"]["holistic"]["D"]["work"] for s in seeds])
    x = fd("holistic", "U", "D", "net") - np.maximum(0, hDw - cap) - fd("conventional", "U", "D", "net")
    print(f"  NOT REGISTERED, counterfactual: holistic D-line work capped at the designed D line's work: d {ci(x)}  p {pflip(x):.4f}")
    loo = [np.delete(d, i).mean() for i in range(12)]
    print(f"  leave-one-seed-out mean d: min {min(loo):+.3f} max {max(loo):+.3f}")


if __name__ == "__main__":
    main()
