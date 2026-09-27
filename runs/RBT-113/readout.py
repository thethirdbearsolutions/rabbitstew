"""RBT-113 readout (PREREGISTRATION.md §5-§7), fixed before any arm runs; amended before any arm ran by the design
adversary's ruling (D1-D5, D8, D9; PREREGISTRATION.md §11).

    readout.py [--reference SIGMA0.json] [--write-reference SIGMA0.json] SEED_DIR [SEED_DIR ...]  > readout.txt

Vocabulary (D9): an ARM is one runner job, one operator on a block of three seeds (`runs/RBT-113/O1` .. `Z4`); a SEED
DIRECTORY is one operator at one seed, `runs/RBT-113/<ARM>/<OP><SEED>` (OP "" = default operator, holistic salt 0;
"Z" = --global-bias-sigma 0, holistic salt 1), holding the three line runs `U/`, `D/`, `C/`, each an `evolve` output
directory (config.json, lineage.jsonl, history.json), and, once decompose.py has run on the restored `final/`
populations, `decompose.json`.  Nothing here simulates.

Per line run, fauna and generation t = 0..G-1:
  m(t)  mean fitness (the trait: mean solo net yield over the generation's shared draws);
  S(t)  the realised selection differential: the mean over generation t+1's children of the mean fitness of
        their parents, minus m(t) (so each parent is weighted by the offspring it actually had).
Per seed directory (three lines sharing founders and every generation's worlds) and fauna, in RAW yield units and in
units of sigma0, ONE scale per fauna: the median over that fauna's seed directories of the SD of generation-0 fitness
(identical on a seed directory's three lines).  Not each seed directory's own SD: the holistic trait is heavy-tailed
(one lucky founder can multiply the SD thirty times; controls/smoke-readout.txt).  This benchmark's sigma0 is printed
as the FROZEN REFERENCE for later benchmarks (--write-reference), and a later benchmark given --reference reports its
rates against it as well as against its own (D4).  h2 is scale-free.
  div(t) = m_U(t) - m_D(t)                                  the divergence (0 at t = 0 by construction)
  CS(t)  = sum_{tau<t} (S_U(tau) - S_D(tau))                 the cumulative divergent selection differential
  h2     = sum_t div(t) CS(t) / sum_t CS(t)^2                realised heritability, regression through the origin
  b_div  = OLS slope of div(t) on t                          divergence per generation
  b_up   = OLS slope of m_U(t) - m_C(t) on t                 upward response per generation, against the control
  b_down = OLS slope of m_C(t) - m_D(t) on t                 downward response per generation (positive = responded)
  h2_up, h2_down: as h2, for U - C on cum (S_U - S_C) and C - D on cum (S_C - S_D)
  b_C    = OLS slope of m_C(t) - m_C(0) on t                 the control's own trend (mutational bias plus worlds)
Across units: mean, t-based 95% CI, and an exact (or 20000-draw) sign-flip p-value.  Holistic units: the default and
Z seed directories at one seed are two independent holistic replicates (salt 0, salt 1) averaged into one unit per
seed; the designed body's unit is the seed directory, per operator.
Food/work (D1): from each seed directory's decompose.json, the generation-(G-1) contrasts U - D, U - C, C - D in items
eaten and in work cost (yield units), per unit with t CIs, and the FOOD SHARE of each contrast in net yield (ratio of
the unit means: mean delta food / mean delta net).
VOID is per fauna and per comparison (D8): a failed control voids only the verdicts whose data it touches.
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


# --------------------------------------------------------------------------- reading the seed directories

def read_run(d):
    rows = {f: [] for f in FAUNAE}
    with open(os.path.join(d, "lineage.jsonl")) as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                rows[r["population"]].append(r)
    return json.load(open(os.path.join(d, "config.json"))), rows


def worlds(d):
    """[(generation, terrain_seed, start_seeds)] from a line run's history.json (one per generation)."""
    h = json.load(open(os.path.join(d, "history.json")))["history"]
    return sorted({(e["generation"], e["terrain_seed"], tuple(e["start_seeds"])) for e in h})


def parse_seed_dir(sd):
    name = os.path.basename(sd.rstrip("/"))
    op = "Z" if name.startswith("Z") else ""
    return name, op, int(name[len(op):])


def controls(sd, cfgs, runs, G, wlds=None):
    """The per-seed-directory controls (§7).  Returns [(scope, message)], scope "holistic", "conventional" or None
    (both faunas); empty = pass.  `wlds`: {line: worlds(...)}, the per-generation world check (D3)."""
    bad = []
    op = parse_seed_dir(sd)[1]
    for L, want in zip(LINES, ("up", "down", "control")):
        c = cfgs[L]
        if c.get("line") != want or not c.get("truncation"):
            bad.append((None, f"{L}: config line {c.get('line')} truncation {c.get('truncation')}"))
        if c["generations"] != G or c["locomotion_phase"] < G or c["elites"] != 0:
            bad.append((None, f"{L}: generations/locomotion/elites {c['generations']}/{c['locomotion_phase']}/{c['elites']}"))
        gbs = c["mutation"].get("global_bias_sigma")
        if (op == "Z") != (gbs == 0.0) or c.get("holistic_stream_salt", 0) != (1 if op == "Z" else 0):
            bad.append((None, f"{L}: operator/salt {gbs}/{c.get('holistic_stream_salt', 0)} do not match {op or 'default'}"))
    base = {k: v for k, v in cfgs["U"].items() if k != "line"}
    for L in ("D", "C"):
        if {k: v for k, v in cfgs[L].items() if k != "line"} != base:
            bad.append((None, f"{L}: config differs from U beyond the line"))
    if wlds is not None:
        if not (wlds["U"] == wlds["D"] == wlds["C"]):
            bad.append((None, "the per-generation worlds (terrain and start seeds, history.json) differ between the lines"))
        if [w[0] for w in wlds["U"]] != list(range(G)):
            bad.append((None, "history.json does not hold one world per generation"))
    for f in FAUNAE:
        g0 = {L: [(r["name"], r["fitness"]) for r in runs[L][f] if r["generation"] == 0] for L in LINES}
        if not (g0["U"] == g0["D"] == g0["C"]):
            bad.append((f, "generation 0 differs between lines (the pairing is broken)"))
        for L in LINES:
            rows = runs[L][f]
            gens = sorted({r["generation"] for r in rows})
            if gens != list(range(G)):
                bad.append((f, f"{L}: generations {gens[:1]}..{gens[-1:]} of {G}"))
                continue
            n = sum(1 for r in rows if r["generation"] == 0)
            k = max(1, int(round(cfgs[L]["truncation"] * n)))
            for t in range(G - 1):
                gen = sorted((r["fitness"] for r in rows if r["generation"] == t))
                fit = {r["name"]: r["fitness"] for r in rows if r["generation"] == t}
                used = {p for r in rows if r["generation"] == t + 1 for p in r["parents"]}
                if not used <= set(fit) or len(used) > k:
                    bad.append((f, f"{L} gen {t}: {len(used)} parents, k = {k}, or a parent outside generation {t}"))
                    break
                pf = [fit[p] for p in used]
                if L == "U" and min(pf) < gen[-k] - 1e-9:
                    bad.append((f, f"U gen {t}: a parent below the top {k}"))
                    break
                if L == "D" and max(pf) > gen[k - 1] + 1e-9:
                    bad.append((f, f"D gen {t}: a parent above the bottom {k}"))
                    break
    return bad


def selection_checks(f, S):
    """The manipulation checks on the realised differentials (§7.4, §7.6).  S: {line: per-generation S}.
    Returns [(scope, message)]."""
    bad = []
    div = float(np.sum(S["U"] - S["D"]))
    if not div > 0:
        bad.append((f, f"manipulation check: cumulative divergent differential {div:+.4g} is not positive"))
    # D3: the control must be unselected.  Pass if the t CI over generations of S_C covers 0, OR its mean is under a
    # quarter of the mean divergent differential; fail only if both fail.
    m, lo, hi, _ = t_ci(S["C"])
    if not (lo <= 0 <= hi) and not abs(m) < 0.25 * float(np.mean(S["U"] - S["D"])):
        bad.append((f, f"the control line is selected: mean S_C {m:+.4g} [{lo:+.4g}, {hi:+.4g}] excludes 0 and is not under "
                       f"0.25 x mean(S_U - S_D) = {0.25 * float(np.mean(S['U'] - S['D'])):.4g}"))
    return bad


def food_units(dec, f, units_of):
    """Per-unit generation-(G-1) contrasts from decompose.json.  units_of: list of lists of seed-dir names per unit."""
    out = []
    for names in units_of:
        rows = [dec[n]["faunae"][f] for n in names]
        u = {}
        for c, (a, b) in (("U-D", ("U", "D")), ("U-C", ("U", "C")), ("C-D", ("C", "D"))):
            for q in ("food", "work", "net"):
                u[f"{c} {q}"] = float(np.mean([r[a][q] - r[b][q] for r in rows]))
        for g in ("founders", "U", "D", "C"):
            for q in ("food", "work", "net"):
                u[f"{g} {q}"] = float(np.mean([r[g][q] for r in rows]))
        out.append(u)
    return out


def ci_text(v, fmt="+.3f"):
    m, lo, hi, n = t_ci(v)
    return f"{m:{fmt}} [{lo:{fmt}}, {hi:{fmt}}]"


DISCLAIMER_1 = "this is the response to imposed selection in this design; it is not a measurement of natural selection in the ecology (paper 5 §2–§4)"
DISCLAIMER_2 = "realised h2 of this design only; not comparable with paper 5's parent–offspring r"
DESIGN = ("Under imposed truncation selection (top / bottom / random {k} of {n}, discrete generations, solo scoring, "
          "{G} generations from random founders, paper 5's world)")  # the arms' values: 10 of 40, 24 generations


def food_share(df, dw):
    """The food share of a contrast in net yield: |mean delta food| / (|mean delta food| + |mean delta work|), in [0, 1]
    whatever the signs (a ratio to delta net explodes when food and work move the same way and cancel); the signs are
    printed beside it."""
    a, b = abs(float(np.mean(df))), abs(float(np.mean(dw)))
    return a / (a + b) if a + b > 0 else float("nan")


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", default=None, help="a frozen sigma0 reference (JSON {fauna: sigma0}) to report against as well")
    ap.add_argument("--write-reference", default=None, help="write this benchmark's sigma0 per fauna here (the frozen reference)")
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    sdirs = a.seed_dirs
    print("# RBT-113 readout (runs/RBT-113/readout.py, fixed before any arm ran)")
    per = {f: [] for f in FAUNAE}  # (name, seed, op, raw stats, own generation-0 SD)
    fails = []  # (seed dir name, op, scope, message)
    G = N = K = None
    wl, g0c, dec = {}, {}, {}
    for sd in sdirs:
        name, op, seed = parse_seed_dir(sd)
        cfgs, runs = {}, {}
        for L in LINES:
            cfgs[L], runs[L] = read_run(os.path.join(sd, L))
        G = G or cfgs["U"]["generations"]
        N = N or cfgs["U"]["population_size"]
        K = K or max(1, int(round(cfgs["U"]["truncation"] * N)))
        wlds = {L: worlds(os.path.join(sd, L)) for L in LINES}
        wl[name] = wlds["U"]
        g0c[name] = [(r["name"], r["fitness"]) for r in runs["U"]["conventional"] if r["generation"] == 0]
        bad = controls(sd, cfgs, runs, G, wlds)
        for f in FAUNAE:
            ser, S = {}, {}
            for L in LINES:
                m, s_, sd0, _ = line_series(runs[L][f])
                ser[L], S[L] = (m, s_), s_
            bad += selection_checks(f, S)
            per[f].append((name, seed, op, arm_stats(ser), sd0))
        if os.path.exists(os.path.join(sd, "decompose.json")):
            dec[name] = json.load(open(os.path.join(sd, "decompose.json")))
        fails += [(name, op, sc, msg) for sc, msg in bad]
        print(f"seed dir {name:6s} controls {'PASS' if not bad else 'FAIL'}" + "".join(f"\n    [{sc or 'both faunae'}] {msg}" for sc, msg in bad))

    # cross-directory pairing controls: the default and Z seed directories at one seed share the designed body's
    # founders and every generation's worlds (the operator comparison's pairing)
    seeds = sorted({s for _, s, _, _, _ in per["conventional"]})
    for seed in seeds:
        a0, az = str(seed), f"Z{seed}"
        if a0 in wl and az in wl:
            if g0c[a0] != g0c[az]:
                fails.append((f"seed {seed}", "", "operator", "the designed body's generation 0 differs between the default and Z seed directories"))
                print(f"seed {seed}: operator pairing FAIL (generation 0)")
            if wl[a0] != wl[az]:
                fails.append((f"seed {seed}", "", "operator", "the per-generation worlds differ between the default and Z seed directories"))
                print(f"seed {seed}: operator pairing FAIL (worlds)")

    def void(scope_fauna, op_filter):
        """True if a failure touches this fauna (and operator, None = any)."""
        return any((sc in (None, scope_fauna)) and (op_filter is None or o == op_filter) for _, o, sc, _ in fails)

    keys = ("b_div", "h2", "b_up", "h2_up", "b_down", "h2_down", "b_C", "S_U", "S_D", "S_C", "div_end")
    scaled = ("b_div", "b_up", "b_down", "b_C", "S_U", "S_D", "S_C", "div_end", "div0")
    sigma0 = {f: float(np.median([s0 for *_, s0 in per[f]])) for f in FAUNAE}
    ref = json.load(open(a.reference)) if a.reference else None
    print(f"\n## sigma0 (median over seed directories of the generation-0 SD, raw yield units): "
          + "  ".join(f"{f} {sigma0[f]:.4f}" for f in FAUNAE))
    print("SIGMA0 REFERENCE " + json.dumps({f: round(sigma0[f], 6) for f in FAUNAE}) + "   (frozen for later benchmarks; D4)")
    if a.write_reference:
        with open(a.write_reference, "w") as fh:
            json.dump({f: sigma0[f] for f in FAUNAE}, fh, indent=1)
    if ref:
        print("   reported against a frozen reference as well: " + "  ".join(f"{f} {ref[f]:.4f}" for f in FAUNAE))
    raw = {f: [(n, s, o, st, s0) for n, s, o, st, s0 in per[f]] for f in FAUNAE}
    sig = {f: [(n, s, o, {k: (v / sigma0[f] if k in scaled else v) for k, v in st.items()}, s0) for n, s, o, st, s0 in per[f]] for f in FAUNAE}
    print("\n## per-seed-directory statistics, in sigma0 units (each directory's own generation-0 SD, raw, in the last column)")
    for f in FAUNAE:
        print(f"\n{f}\n  seed dir " + " ".join(f"{k:>8s}" for k in keys) + "   own SD")
        for n, s, o, st, s0 in sig[f]:
            print(f"  {n:8s} " + " ".join(f"{st[k]:+8.3f}" for k in keys) + f"   {s0:.4f}")

    def units(table, f, op_filter=None):
        """(unit stats, [seed-dir names per unit])"""
        if f == "holistic":  # one unit per seed: the salt-0 and salt-1 replicates averaged
            ss = sorted({s for _, s, _, _, _ in table[f]})
            return ([{k: float(np.mean([st[k] for _, s, _, st, _ in table[f] if s == sd])) for k in keys} for sd in ss],
                    [[n for n, s, _, _, _ in table[f] if s == sd] for sd in ss])
        rows = [(n, st) for n, s, o, st, _ in table[f] if o == op_filter]
        return [st for _, st in rows], [[n] for n, _ in rows]

    groups = (("holistic", None, "holistic, per seed (both operators: the operator does not reach it)", "holistic"),
              ("conventional", "", "designed body, default operator", "conventional"),
              ("conventional", "Z", "designed body, --global-bias-sigma 0", "conventional"))
    verdicts, headlines = {}, {}
    print("\n## across units: mean [95% t CI] (n), sign-flip p; sigma0 units, then raw yield units for the rates")
    for f, opf, label, _ in groups:
        u, names = units(sig, f, opf)
        ur, _ = units(raw, f, opf)
        print(f"\n{label}: {len(u)} units")
        for k in keys:
            m, lo, hi, n = t_ci([x[k] for x in u])
            print(f"  {k:8s} {m:+.4f} [{lo:+.4f}, {hi:+.4f}] ({n})  p = {sign_flip_p([x[k] for x in u]):.4f}")
        for k in ("b_div", "b_up", "b_down", "b_C"):
            print(f"  {k:8s} raw {ci_text([x[k] for x in ur], '+.5f')} yield per generation"
                  + (f";  reference sigma0 units {ci_text([x[k] / ref[f] for x in ur], '+.4f')}" if ref else ""))
        m, lo, hi, n = t_ci([x["b_div"] for x in u])
        p = sign_flip_p([x["b_div"] for x in u])
        if void(f, opf):
            v = "VOID (a control on this fauna's data failed; see above)"
        elif lo > 0 and p < ALPHA:
            v = "RESPONDS"
        elif hi < MDE_DIV:
            v = f"NO RESPONSE at the powered effect (the CI excludes {MDE_DIV} sigma0 per generation)"
        else:
            v = "INCONCLUSIVE"
        verdicts[label] = v
        print(f"  VERDICT: {v}")

        # D1: the endpoint food/work split
        have = [ns for ns in names if all(nm in dec for nm in ns)]
        if len(have) == len(names) and names:
            fu = food_units(dec, f, names)
            print(f"  food/work at generation {G - 1} (decompose.json; items eaten, work cost in yield units; t CI over {len(fu)} units)")
            for g in ("founders", "U", "D", "C"):
                print(f"    {g:8s} food {ci_text([x[g + ' food'] for x in fu], '.3f')}  work {ci_text([x[g + ' work'] for x in fu], '.3f')}  net {ci_text([x[g + ' net'] for x in fu])}")
            shares = {}
            for c in ("U-D", "U-C", "C-D"):
                df, dw, dn = ([x[f"{c} {q}"] for x in fu] for q in ("food", "work", "net"))
                shares[c] = food_share(df, dw)
                sg = f"food {'+' if np.mean(df) >= 0 else '-'}, work {'+' if np.mean(dw) >= 0 else '-'}"
                shares[c + " signs"] = sg
                print(f"    {c:4s} delta food {ci_text(df)}  delta work {ci_text(dw)}  delta net {ci_text(dn)}  food share {shares[c]:.0%} ({sg})")
            split = (f"At generation {G - 1}, food was {shares['U-D']:.0%} of the U − D change in net yield "
                     f"({shares['U-C']:.0%} of U − C, {shares['C-D']:.0%} of C − D), and work the rest "
                     f"(food share = |delta food| / (|delta food| + |delta work|); signs U − D {shares['U-D signs']}, "
                     f"U − C {shares['U-C signs']}, C − D {shares['C-D signs']}).")
        else:
            missing = sorted({nm for ns in names for nm in ns if nm not in dec})
            split = f"The food/work split is NOT YET RUN (pre-registered: decompose.py on the restored final/ populations; missing for {', '.join(missing)})."
            print(f"  food/work: {split}")

        hr = t_ci([x["b_div"] for x in ur])
        headlines[label] = (
            f"{DESIGN.format(k=K, n=N, G=G)}, over {len(u)} {'seeds (two replicates each)' if f == 'holistic' else 'seeds'}, {label}: "
            f"the up and down lines diverged by {ci_text([x['b_div'] for x in u])} sigma0 per generation "
            f"({hr[0]:+.4f} [{hr[1]:+.4f}, {hr[2]:+.4f}] yield per generation; sigma0 = {sigma0[f]:.4f}), with realised h2 "
            f"{ci_text([x['h2'] for x in u])}; against the control, the up line moved {ci_text([x['b_up'] for x in u])} and "
            f"the down line {ci_text([x['b_down'] for x in u])} sigma0 per generation. {split} Verdict: {v}. RESPONDS is the "
            f"expected verdict, since mutation alone supplies heritable variance; the finding is the magnitude, the asymmetry "
            f"and the food/work split. \"{DISCLAIMER_1}\"; \"{DISCLAIMER_2}\"."
        )

    # the operator comparison, designed body: paired by seed
    d0 = {s: st for _, s, o, st, _ in sig["conventional"] if o == ""}
    dz = {s: st for _, s, o, st, _ in sig["conventional"] if o == "Z"}
    pairs = sorted(set(d0) & set(dz))
    print(f"\n## operator comparison, designed body: Z minus default, paired by seed ({len(pairs)} pairs)")
    for k in ("b_div", "h2", "b_up", "b_down", "b_C"):
        diff = [dz[s][k] - d0[s][k] for s in pairs]
        m, lo, hi, n = t_ci(diff)
        print(f"  {k:8s} {m:+.4f} [{lo:+.4f}, {hi:+.4f}] ({n})  p = {sign_flip_p(diff):.4f}")
    diff = [dz[s]["b_div"] - d0[s]["b_div"] for s in pairs]
    m, lo, hi, n = t_ci(diff)
    if void("conventional", None) or any(sc == "operator" for _, _, sc, _ in fails):
        opv = "VOID (a control on the designed body's data or on the pairing failed; see above)"
    elif n < 2:
        opv = "NOT RUN"
    elif lo > 0 and sign_flip_p(diff) < ALPHA:
        opv = f"Z RAISES the divergence rate by {m:+.3f} [{lo:+.3f}, {hi:+.3f}] sigma0/generation"
    elif hi < 0 and sign_flip_p(diff) < ALPHA:
        opv = f"Z LOWERS the divergence rate by {m:+.3f} [{lo:+.3f}, {hi:+.3f}] sigma0/generation"
    elif -EQUIV_OP < lo and hi < EQUIV_OP:
        opv = f"NO CHANGE within +-{EQUIV_OP}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]"
    else:
        opv = f"INCONCLUSIVE: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]"
    print(f"  VERDICT: {opv}")

    print("\n## correlated responses (descriptive only): U - D divergence slope per generation, in the founders' SD of each "
          "descriptor; holistic averaged per seed as the main table")
    desc = ("distance", "nodes", "parts", "units", "links", "mass")
    for f in FAUNAE:
        by = {}
        for sd in sdirs:
            name, op, seed = parse_seed_dir(sd)
            rr = {L: read_run(os.path.join(sd, L))[1][f] for L in ("U", "D")}
            for k in desc:
                s0 = np.std([r[k] for r in rr["U"] if r["generation"] == 0], ddof=1)
                if not s0 > 0:
                    continue
                mU = [np.mean([r[k] for r in rr["U"] if r["generation"] == t]) for t in range(G)]
                mD = [np.mean([r[k] for r in rr["D"] if r["generation"] == t]) for t in range(G)]
                key = seed if f == "holistic" else (seed, op)
                by.setdefault(k, {}).setdefault(key, []).append(ols_slope((np.array(mU) - np.array(mD)) / s0))
        print(f"  {f}: " + "  ".join(f"{k} {ci_text([np.mean(v) for v in d.values()])}" for k, d in by.items()))

    print("\n## HEADLINES (fixed in code before any data; D2)")
    notes = {
        "holistic": ("h2 is an index of this design (standing and new mutational variance mixed over 24 generations, "
                     "eroded by drift and the Bulmer effect), not an estimate of a heritability. No before-and-after "
                     "operator number exists for the holistic fauna: RBT-112's operator does not reach it."),
        "conventional": ("h2 is an index of this design, not an estimate of a heritability. The operator comparison is "
                         "designed-body only (RBT-112's operator does not reach the holistic fauna) and weakly powered "
                         "(P = 0.53 at a planted change in h2 from 0.2 to 0.4; power.txt)."),
    }
    for f, opf, label, nk in groups:
        print(f"\n* {headlines[label]}\n  ({notes[nk]})")
    print(f"\n* Operator comparison (designed body, Z minus default, paired by seed): {opv}.\n  ({notes['conventional']})")
    print("\n## verdicts")
    for label, v in verdicts.items():
        print(f"  {label}: {v}")
    print(f"  operator comparison (designed body): {opv}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
