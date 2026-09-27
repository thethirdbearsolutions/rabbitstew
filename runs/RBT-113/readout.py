"""RBT-113 readout (PREREGISTRATION.md §4-§6), fixed before any arm runs.

    readout.py ARM_DIR [ARM_DIR ...]  > readout.txt

An ARM_DIR is `runs/RBT-113/<OP><SEED>` (OP "" = default operator, holistic salt 0; "Z" = --global-bias-sigma 0,
holistic salt 1) holding the three line runs `U/`, `D/`, `C/` of one seed, each an `evolve` output directory
(config.json, lineage.jsonl, history.json).  Nothing here simulates; every number comes from lineage.jsonl.

Per run, fauna and generation t = 0..G-1:
  m(t)  mean fitness (the trait: mean solo net yield over the generation's shared draws);
  S(t)  the realised selection differential: the mean over generation t+1's children of the mean fitness of
        their parents, minus m(t) (so each parent is weighted by the offspring it actually had).
Per arm (one seed: three lines sharing founders and every generation's worlds), fauna, in units of sigma0, ONE
scale per fauna: the median over that fauna's arms of the SD of generation-0 fitness (identical on an arm's three
lines).  Not each arm's own SD: the holistic trait is heavy-tailed (one lucky founder can multiply an arm's SD thirty
times; controls/smoke-readout.txt), and a per-arm scale would weight the seeds by their founders' luck.  h2 is
scale-free.
  div(t) = m_U(t) - m_D(t)                                  the divergence (0 at t = 0 by construction)
  CS(t)  = sum_{tau<t} (S_U(tau) - S_D(tau))                 the cumulative divergent selection differential
  h2     = sum_t div(t) CS(t) / sum_t CS(t)^2                realised heritability, regression through the origin
  b_div  = OLS slope of div(t) on t                          divergence per generation (sigma0 / generation)
  b_up   = OLS slope of m_U(t) - m_C(t) on t                 upward response per generation, against the control
  b_down = OLS slope of m_C(t) - m_D(t) on t                 downward response per generation (positive = responded)
  h2_up, h2_down: as h2, for U - C on cum (S_U - S_C) and C - D on cum (S_C - S_D)
  b_C    = OLS slope of m_C(t) - m_C(0) on t                 the control's own trend (mutational bias plus worlds)
Across arms: mean, t-based 95% CI, and an exact (or 20000-draw) sign-flip p-value on the per-arm values.
Holistic units: the default-operator arm and the Z arm at one seed are two independent holistic replicates
(salt 0, salt 1) and are averaged into one unit per seed; the designed body's unit is the (seed, operator) arm.
"""
import itertools
import json
import os
import sys

import numpy as np

LINES = ("U", "D", "C")
FAUNAE = ("holistic", "conventional")
ALPHA = 0.05
# two-sided 97.5% Student-t quantiles, df 1..40 (no scipy in the house venv)
T975 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131,
        2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042,
        2.040, 2.037, 2.035, 2.032, 2.030, 2.028, 2.026, 2.024, 2.023, 2.021]
# §5 pre-registered thresholds (sigma0 units)
MDE_DIV = 0.05        # the divergence rate the verdict must be able to exclude to call NO RESPONSE (per generation)
EQUIV_OP = 0.05       # the operator comparison's equivalence margin on b_div (per generation)
# the manipulation-reached-the-trait check is scale-free: every arm's cumulative divergent differential sum_t (S_U - S_D)(t) > 0


# --------------------------------------------------------------------------- statistics (shared with power.py)

def ols_slope(y):
    t = np.arange(len(y), dtype=float)
    return float(np.polyfit(t, np.asarray(y, float), 1)[0])


def through_origin(y, x):
    x, y = np.asarray(x, float), np.asarray(y, float)
    sxx = float(np.sum(x * x))
    return float(np.sum(x * y) / sxx) if sxx > 0 else float("nan")


def t_ci(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    n = len(v)
    if n < 2:
        return float(np.mean(v)) if n else float("nan"), float("nan"), float("nan"), n
    m, se = float(v.mean()), float(v.std(ddof=1) / np.sqrt(n))
    q = T975[min(n - 1, len(T975)) - 1]
    return m, m - q * se, m + q * se, n


def sign_flip_p(v, draws=20000, seed=113):
    """Two-sided sign-flip p-value for mean(v) = 0: exact up to 2^16 patterns, else Monte Carlo."""
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    n = len(v)
    if n == 0:
        return float("nan")
    obs = abs(v.mean())
    if n <= 16:
        signs = np.array(list(itertools.product((1, -1), repeat=n)), float)
    else:
        signs = np.random.default_rng(seed).choice((1.0, -1.0), size=(draws, n))
    return float(np.mean(np.abs(signs @ v / n) >= obs - 1e-12))


def line_series(rows):
    """rows: lineage rows of one run and fauna.  -> (m[t], S[t] for t < G-1, sd0, gen0 rows)."""
    by = {}
    for r in rows:
        by.setdefault(r["generation"], []).append(r)
    G = max(by) + 1
    assert sorted(by) == list(range(G)), "missing generations"
    fit = {r["name"]: r["fitness"] for r in rows}
    m = np.array([np.mean([r["fitness"] for r in by[t]]) for t in range(G)])
    S = []
    for t in range(G - 1):
        pm = [np.mean([fit[p] for p in r["parents"]]) for r in by[t + 1]]
        S.append(float(np.mean(pm) - m[t]))
    return m, np.array(S), float(np.std([r["fitness"] for r in by[0]], ddof=1)), by[0]


def arm_stats(series, sd0=None):
    """series: {line: (m, S)} for U, D, C of one arm and fauna.  All in raw units unless sd0 is given."""
    k = 1.0 / sd0 if sd0 else 1.0
    m = {L: series[L][0] * k for L in LINES}
    S = {L: series[L][1] * k for L in LINES}
    cum = lambda s: np.concatenate([[0.0], np.cumsum(s)])  # noqa: E731  CS(t) for t = 0..G-1
    div = m["U"] - m["D"]
    up, down = m["U"] - m["C"], m["C"] - m["D"]
    return {
        "b_div": ols_slope(div), "h2": through_origin(div[1:], cum(S["U"] - S["D"])[1:]),
        "b_up": ols_slope(up), "h2_up": through_origin(up[1:], cum(S["U"] - S["C"])[1:]),
        "b_down": ols_slope(down), "h2_down": through_origin(down[1:], cum(S["C"] - S["D"])[1:]),
        "b_C": ols_slope(m["C"] - m["C"][0]),
        "S_U": float(np.mean(S["U"])), "S_D": float(np.mean(S["D"])), "S_C": float(np.mean(S["C"])),
        "div0": float(div[0]), "div_end": float(div[-1]),
    }


# --------------------------------------------------------------------------- reading the arms

def read_run(d):
    rows = {f: [] for f in FAUNAE}
    with open(os.path.join(d, "lineage.jsonl")) as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                rows[r["population"]].append(r)
    return json.load(open(os.path.join(d, "config.json"))), rows


def controls(arm, cfgs, runs, G):
    """The per-arm controls (§6).  Returns a list of failure strings (empty = pass)."""
    bad = []
    op = "Z" if os.path.basename(arm.rstrip("/")).startswith("Z") else ""
    for L, want in zip(LINES, ("up", "down", "control")):
        c = cfgs[L]
        if c.get("line") != want or not c.get("truncation"):
            bad.append(f"{L}: config line {c.get('line')} truncation {c.get('truncation')}")
        if c["generations"] != G or c["locomotion_phase"] < G or c["elites"] != 0:
            bad.append(f"{L}: generations/locomotion/elites {c['generations']}/{c['locomotion_phase']}/{c['elites']}")
        gbs = c["mutation"].get("global_bias_sigma")
        if (op == "Z") != (gbs == 0.0) or c.get("holistic_stream_salt", 0) != (1 if op == "Z" else 0):
            bad.append(f"{L}: operator/salt {gbs}/{c.get('holistic_stream_salt', 0)} do not match arm {op or 'default'}")
    base = {k: v for k, v in cfgs["U"].items() if k != "line"}
    for L in ("D", "C"):
        if {k: v for k, v in cfgs[L].items() if k != "line"} != base:
            bad.append(f"{L}: config differs from U beyond the line")
    for f in FAUNAE:
        g0 = {L: [(r["name"], r["fitness"]) for r in runs[L][f] if r["generation"] == 0] for L in LINES}
        if not (g0["U"] == g0["D"] == g0["C"]):
            bad.append(f"{f}: generation 0 differs between lines (the pairing is broken)")
        for L in LINES:
            rows = runs[L][f]
            gens = sorted({r["generation"] for r in rows})
            if gens != list(range(G)):
                bad.append(f"{f} {L}: generations {gens[:1]}..{gens[-1:]} of {G}")
                continue
            n = sum(1 for r in rows if r["generation"] == 0)
            k = max(1, int(round(cfgs[L]["truncation"] * n)))
            for t in range(G - 1):
                gen = sorted((r["fitness"] for r in rows if r["generation"] == t))
                fit = {r["name"]: r["fitness"] for r in rows if r["generation"] == t}
                used = {p for r in rows if r["generation"] == t + 1 for p in r["parents"]}
                if not used <= set(fit) or len(used) > k:
                    bad.append(f"{f} {L} gen {t}: {len(used)} parents, k = {k}, or a parent outside generation {t}")
                    break
                pf = [fit[p] for p in used]
                if L == "U" and min(pf) < gen[-k] - 1e-9:
                    bad.append(f"{f} U gen {t}: a parent below the top {k}")
                    break
                if L == "D" and max(pf) > gen[k - 1] + 1e-9:
                    bad.append(f"{f} D gen {t}: a parent above the bottom {k}")
                    break
    return bad


def main(arms):
    print("# RBT-113 readout (runs/RBT-113/readout.py, fixed before any arm ran)")
    per = {f: [] for f in FAUNAE}  # (seed, op, stats in sigma0 units, raw sd0)
    failures = []
    G = None
    for arm in arms:
        name = os.path.basename(arm.rstrip("/"))
        op = "Z" if name.startswith("Z") else ""
        seed = int(name[len(op):])
        cfgs, runs = {}, {}
        for L in LINES:
            cfgs[L], runs[L] = read_run(os.path.join(arm, L))
        G = G or cfgs["U"]["generations"]
        bad = controls(arm, cfgs, runs, G)
        for f in FAUNAE:
            ser = {}
            for L in LINES:
                m, S, sd0, _ = line_series(runs[L][f])
                ser[L] = (m, S)
            st = arm_stats(ser)  # raw units; scaled by the fauna's pooled sigma0 below
            if not st["S_U"] - st["S_D"] > 0:
                bad.append(f"{f}: manipulation check, cumulative divergent differential {(st['S_U'] - st['S_D']) * (G - 1):+.4g} is not positive")
            per[f].append((seed, op, st, sd0))
        failures += [f"{name}: {b}" for b in bad]
        print(f"arm {name:6s} controls {'PASS' if not bad else 'FAIL'}" + "".join(f"\n    {b}" for b in bad))

    # cross-arm pairing control: the default and Z arms at one seed share the designed body's founders and worlds
    for seed in sorted({s for s, op, _, _ in per["conventional"] if op == "Z"} & {s for s, op, _, _ in per["conventional"] if op == ""}):
        g0 = {}
        for arm in arms:
            name = os.path.basename(arm.rstrip("/"))
            if name in (str(seed), f"Z{seed}"):
                g0[name] = [(r["name"], r["fitness"]) for r in read_run(os.path.join(arm, "U"))[1]["conventional"] if r["generation"] == 0]
        if len(set(map(tuple, g0.values()))) != 1:
            failures.append(f"seed {seed}: the designed body's generation 0 differs between the default and Z arms (operator pairing broken)")
            print(f"seed {seed}: operator pairing FAIL")

    keys = ("b_div", "h2", "b_up", "h2_up", "b_down", "h2_down", "b_C", "S_U", "S_D", "S_C", "div_end")
    scaled = ("b_div", "b_up", "b_down", "b_C", "S_U", "S_D", "S_C", "div_end", "div0")
    sigma0 = {f: float(np.median([sd0 for _, _, _, sd0 in per[f]])) for f in FAUNAE}
    for f in FAUNAE:
        per[f] = [(s, op, {k: (v / sigma0[f] if k in scaled else v) for k, v in st.items()}, sd0) for s, op, st, sd0 in per[f]]
    print("\n## per-arm statistics (in sigma0 units, sigma0 = the fauna's median generation-0 SD; each arm's own generation-0 SD, raw, in the last column)")
    print("   " + "  ".join(f"{f} sigma0 {sigma0[f]:.4f}" for f in FAUNAE))
    for f in FAUNAE:
        print(f"\n{f}\n  arm    " + " ".join(f"{k:>8s}" for k in keys) + "   sigma0")
        for seed, op, st, sd0 in per[f]:
            print(f"  {op or '-'}{seed:<5d} " + " ".join(f"{st[k]:+8.3f}" for k in keys) + f"   {sd0:.4f}")

    def units(f, op_filter=None):
        if f == "holistic":  # one unit per seed: the salt-0 and salt-1 replicates averaged
            seeds = sorted({s for s, _, _, _ in per[f]})
            return [{k: float(np.mean([st[k] for s, _, st, _ in per[f] if s == sd])) for k in keys} for sd in seeds]
        return [st for s, op, st, _ in per[f] if op == op_filter]

    verdicts = {}
    print("\n## across arms: mean [95% t CI] (n), sign-flip p")
    for f, opf, label in (("holistic", None, "holistic (both operators; the operator does not reach it), per seed"),
                          ("conventional", "", "designed body, default operator"),
                          ("conventional", "Z", "designed body, --global-bias-sigma 0")):
        u = units(f, opf)
        print(f"\n{label}: {len(u)} units")
        for k in keys:
            m, lo, hi, n = t_ci([x[k] for x in u])
            print(f"  {k:8s} {m:+.4f} [{lo:+.4f}, {hi:+.4f}] ({n})  p = {sign_flip_p([x[k] for x in u]):.4f}")
        m, lo, hi, n = t_ci([x["b_div"] for x in u])
        p = sign_flip_p([x["b_div"] for x in u])
        if failures:
            v = "VOID (a per-arm control failed; see above)"
        elif lo > 0 and p < ALPHA:
            h, hl, hh, _ = t_ci([x["h2"] for x in u])
            v = f"RESPONDS: divergence {m:+.3f} sigma0/generation [{lo:+.3f}, {hi:+.3f}], realised h2 {h:.3f} [{hl:.3f}, {hh:.3f}]"
        elif hi < MDE_DIV:
            v = f"NO RESPONSE at the powered effect: divergence {m:+.3f} [{lo:+.3f}, {hi:+.3f}] excludes {MDE_DIV}"
        else:
            v = f"INCONCLUSIVE: divergence {m:+.3f} [{lo:+.3f}, {hi:+.3f}]"
        verdicts[label] = v
        print(f"  VERDICT: {v}")

    # the operator comparison, designed body: paired by seed
    d0 = {s: st for s, op, st, _ in per["conventional"] if op == ""}
    dz = {s: st for s, op, st, _ in per["conventional"] if op == "Z"}
    pairs = sorted(set(d0) & set(dz))
    print(f"\n## operator comparison, designed body: Z minus default, paired by seed ({len(pairs)} pairs)")
    for k in ("b_div", "h2", "b_up", "b_down", "b_C"):
        diff = [dz[s][k] - d0[s][k] for s in pairs]
        m, lo, hi, n = t_ci(diff)
        print(f"  {k:8s} {m:+.4f} [{lo:+.4f}, {hi:+.4f}] ({n})  p = {sign_flip_p(diff):.4f}")
    diff = [dz[s]["b_div"] - d0[s]["b_div"] for s in pairs]
    m, lo, hi, n = t_ci(diff)
    if failures:
        v = "VOID"
    elif n < 2:
        v = "NOT RUN"
    elif lo > 0 and sign_flip_p(diff) < ALPHA:
        v = f"Z RAISES the divergence rate by {m:+.3f} [{lo:+.3f}, {hi:+.3f}] sigma0/generation"
    elif hi < 0 and sign_flip_p(diff) < ALPHA:
        v = f"Z LOWERS the divergence rate by {m:+.3f} [{lo:+.3f}, {hi:+.3f}] sigma0/generation"
    elif -EQUIV_OP < lo and hi < EQUIV_OP:
        v = f"NO CHANGE within +-{EQUIV_OP}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]"
    else:
        v = f"INCONCLUSIVE: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]"
    opv = v
    print(f"  VERDICT: {v}")

    print("\n## correlated responses (descriptive only): U - D divergence slope per generation, in the founders' SD of each descriptor")
    desc = ("distance", "nodes", "parts", "units", "links", "mass")
    for f in FAUNAE:
        out = {k: [] for k in desc}
        for arm in arms:
            runs = {L: read_run(os.path.join(arm, L))[1][f] for L in ("U", "D")}
            for k in desc:
                sd = np.std([r[k] for r in runs["U"] if r["generation"] == 0], ddof=1)
                if not sd > 0:
                    continue
                mU = [np.mean([r[k] for r in runs["U"] if r["generation"] == t]) for t in range(G)]
                mD = [np.mean([r[k] for r in runs["D"] if r["generation"] == t]) for t in range(G)]
                out[k].append(ols_slope((np.array(mU) - np.array(mD)) / sd))
        print(f"  {f}: " + "  ".join(f"{k} {t_ci(v)[0]:+.3f} [{t_ci(v)[1]:+.3f}, {t_ci(v)[2]:+.3f}]" for k, v in out.items() if v))
    print("\n## verdicts")
    for label, v in verdicts.items():
        print(f"  {label}: {v}")
    print(f"  operator comparison (designed body): {opv}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
