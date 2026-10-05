"""RBT-134: the registered proposal-rate assay, Pioneer (runs/RBT-134/DESIGN.md r3, sections 3, 4, 6, 9).

RBT-91's instrument, imported, not reimplemented (`runs/RBT-91/structural_rate.py`): the predicate, the probes,
RBT-78's pools, MASTER_SEED and the lineage seeds.  One pass per condition: 19 `mutate_controller` mutations from
the committed parents, 100,000 lineages per pool (200,000), add 0.15 rem 0.1, the condition's MutationConfig fields,
and the registered auxiliary stream SeedSequence([MASTER_SEED, crc32(label), 19, i, 134]) for every extra draw.

    assay.py run COND --go [--n 100000] [--n-bg 20000] [--workers 4]   -> OUT/COND.json
    assay.py resign COND --go [--cap 400] [--workers 4]                 -> OUT/COND-resign.txt
    assay.py readout                                                    -> stdout (tee OUT/readout.txt)
    assay.py smoke                                                      -> a tiny B0 pass and the self-checks

`run` refuses any condition without --go: nothing registered runs before the PR is merged and the coordinator's
GO (the ruling of 2026-10-04).  `smoke` runs only the default operator (B0, published) at a few hundred lineages.

THE ORDER (DESIGN.md 13 and S4): controls B0, C+, A0, then the checks P1, P4, P5; then P2 FIRST (a determinate
computation from committed data), then P3.  `readout` reads whatever JSONs exist and applies the registered rules.
"""
import argparse
import copy
import importlib.util
import json
import math
import os
import re
import sys
import zlib
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, [path]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


sr = _load("sr91", os.path.join(_ROOT, "runs", "RBT-91", "structural_rate.py"))
dec = _load("dec134", os.path.join(_HERE, "decompose_arrivals.py"))
rbt78 = sr.rbt78

from rabbitstew import genetics  # noqa: E402
from rabbitstew.fixed import drive_effector_units  # noqa: E402
from rabbitstew.genetics import mutate_controller  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

OUT = os.path.join(_HERE, "out")
K, ADD, REM = 19, 0.15, 0.1
AUX_KEY = 134
#: own-link rungs (ERRATA H41; runs/RBT-72-adversary/probe_rung.txt:2-4), and the whole-brain reading
RUNGS = {"a16": 6.2831, "a32": 12.5236, "a64": 24.7145}
PRIMARY = "a32"
WHOLE = 6.8664  #: whole-brain rung: the background clause's (like for like there), and continuity with "0 of 84"
WHOLE_64 = 24.7145
#: registered conditions (DESIGN.md 2.1, 2.2, 6.4).  Each is a set of MutationConfig fields over the pool's config.
CONDITIONS = {
    "B0": {},
    "C+": {"pair_event_rate": 0.005, "pair_event_scale": 16.0, "pair_event_zero_bias": True},
    "A0": {"global_bias_sigma": 0.0, "effector_bias_sigma": 0.0},
    "P1": {"link_sigma": 1.6},
    "P2": {"link_sigma": 4.0},
    "P3": {"link_sigma": 4.0, "bias_reset_rate": 0.2},
    "P4": {"fan_rate": 0.2, "fan_sigma": 0.75},
    "P5": {"pair_event_rate": 0.005},
}
PAIR_CONDITIONS = ("C+", "P5")  #: not sensor-blind: I5 against B0's food rate (DESIGN.md 9, amendment I5-a)
FAMILY = ("P2", "P3")  #: Holm, m = 2 (DESIGN.md 6.1)
CHECK_BOUND = {"A0": 0, "P1": 2, "P2": 29, "P3": 29}  #: k at a = 32 may not exceed these (I3)
CEILING = {"P4": 2.96, "P5": 0.01}  #: priced ceilings; k >= 6 is a ceiling failure (DESIGN.md 2.2)
#: the committed arrival sets these conditions must reproduce (I2): links and structure are those lineages'
TWIN_READOUT = {"B0": "RBT-91-alone-baseline.txt", "A0": "RBT-91-alone-baseline.txt",
                "P1": "RBT-91-alone-1.6.txt", "P2": "RBT-91-alone-4.0.txt", "P3": "RBT-91-alone-4.0.txt"}
FMAX = {"tanh": 1.0, "sin": 1.0, "relu": 1.0, "integrate": 2 * (1 - 0.9 ** 12), "abs": 1.0,
        "differentiate": 0.0, "sign": 0.0}  #: the slope bound's max f' (DESIGN.md 2.2)
B0_BG_PREFIX = {"all": (26, 9_996), "unflagged": (22, 9_990)}  #: first 5,000 per pool (DESIGN.md 9, FC-M1)
MARGIN = 2.0  #: background non-inferiority margin (DESIGN.md 4)


# --------------------------------------------------------------------------- #
# The predicate, generalised to a sensor source only for the sham (I5)
# --------------------------------------------------------------------------- #

def wheel_sensors(ph, source):
    side = {}
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor" or ui.unit.source != source or ui.part is None:
            continue
        part = ph.parts[ui.part]
        if part.parent is None:
            continue
        side.setdefault("left" if part.attach_pos[1] > 0 else "right", []).append(i)
    if "left" not in side or "right" not in side:
        return None
    return side["left"][0], side["right"][0]


def predicate(ph, source="food"):
    """structural_rate.motif_units with the nose source as a parameter; for "food" it must equal it (checked)."""
    noses = wheel_sensors(ph, source)
    if noses is None:
        return []
    n_L, n_R = noses
    left_e, right_e = drive_effector_units(ph)
    if not left_e or not right_e:
        return []
    e_L, e_R = left_e[0], right_e[0]
    w = {}
    for s, d, weight in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + weight
    out = []
    for k, ui in enumerate(ph.units):
        if ui.part is not None or ui.unit.kind == "sensor":
            continue
        in_L, in_R = w.get((n_L, k), 0.0), w.get((n_R, k), 0.0)
        if in_L == 0.0 or in_R == 0.0 or np.sign(in_L) == np.sign(in_R):
            continue
        out_L, out_R = w.get((k, e_L), 0.0), w.get((k, e_R), 0.0)
        if out_L == 0.0 or out_R == 0.0 or np.sign(out_L) != np.sign(out_R):
            continue
        out.append(k)
    return out


#: the counterfactual reads of DESIGN.md 1 / 3.4 (decompose_arrivals.py's columns), per predicate unit of every arrival
CF = {"tanh": {"func": "tanh"}, "bk0": {"bk": 0.0}, "bE0": {"bE": 0.0}, "tk": {"func": "tanh", "bk": 0.0},
      "kE": {"bk": 0.0, "bE": 0.0}, "tE": {"func": "tanh", "bE": 0.0}, "unit": {"func": "tanh", "bk": 0.0, "bE": 0.0}}


def resting_input_a(ph, k):
    """DESIGN.md 11.1 (descriptive): the circuit's links-alone response with each drive Effector held at its
    whole-brain resting input -- its bias replaced by its settled pre-activation under zero sensors, less k's own
    contribution -- instead of at its bare bias."""
    from rabbitstew.brain import RuntimeBrain
    brain = RuntimeBrain(ph)
    zero = np.zeros(len(brain.sensor_idx))
    for _ in range(sr.SETTLE):
        brain.step(zero)
    rest = brain.activation.copy()
    x = brain.W @ rest + brain.bias
    le, re_ = drive_effector_units(ph)
    held = copy.deepcopy(ph)
    for e in le + re_:
        held.units[e].unit.bias = float(x[e] - brain.W[e, k] * rest[k])
    return float(sr.links_alone_a(held, k))


def unit_record(ph, k):
    noses = sr._wheel_noses(ph)
    le, re_ = drive_effector_units(ph)
    w = {}
    for s, d, wt in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + wt
    uL, uR = w.get((noses[0], k), 0.0), w.get((noses[1], k), 0.0)
    vL, vR = w.get((k, le[0]), 0.0), w.get((k, re_[0]), 0.0)
    rec = {"k": k, "func": ph.units[k].unit.func, "bk": float(ph.units[k].unit.bias),
           "bE": float(max(abs(ph.units[e].unit.bias) for e in le + re_)),
           "a": float(sr.links_alone_a(ph, k)), "flip": bool(dec.sign_flip(ph, k)),
           "prod": float((uL - uR) / 2.0 * (vL + vR) / 2.0)}
    rec["cf"] = {name: float(sr.links_alone_a(dec.edited(ph, k, **edit), k)) for name, edit in CF.items()}
    rec["cf_flip"] = {name: bool(dec.sign_flip(dec.edited(ph, k, **edit), k)) for name, edit in CF.items()}
    rec["rest"] = resting_input_a(ph, k)
    return rec


# --------------------------------------------------------------------------- #
# One pass
# --------------------------------------------------------------------------- #

def lineage(label, i, fields, k=K):
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=ADD, remove_link_rate=REM, **fields)
    seed = [rbt78.MASTER_SEED, zlib.crc32(label.encode()), k, i]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    aux = np.random.default_rng(np.random.SeedSequence(seed + [AUX_KEY]))
    g = pool[i % len(pool)]
    for _ in range(k):
        g = mutate_controller(g, rng, mcfg, aux_rng=aux)
    return synthesize(g, cfg.sim.synthesis), i % len(pool)


def chunk(task):
    cond, label, lo, hi, n_bg = task
    fields = CONDITIONS[cond]
    genetics.PAIR_EVENT_COUNTS.update(events=0, refused=0, no_pair=0)
    arrivals, bg, sham, mismatch = [], [], 0, 0
    for i in range(lo, hi):
        ph, parent = lineage(label, i, fields)
        units = predicate(ph, "food")
        mismatch += units != sr.motif_units(ph)
        sham += bool(predicate(ph, "agent"))
        whole = None
        if units:
            whole = float(sr.small_signal_a(ph))
            arrivals.append({"label": label, "i": i, "parent": parent, "whole": whole,
                             "units": [unit_record(ph, k) for k in units]})
        if i < n_bg:
            if whole is None:
                whole = float(sr.small_signal_a(ph))
            bg.append((i, bool(units), abs(whole) if np.isfinite(whole) else 0.0, bool(dec.sign_flip(ph, None))))
    return {"label": label, "n": hi - lo, "arrivals": arrivals, "bg": bg, "sham": sham, "mismatch": mismatch,
            "pair_events": dict(genetics.PAIR_EVENT_COUNTS)}


def run(cond, n, n_bg, workers, go):
    if cond not in CONDITIONS:
        sys.exit(f"unknown condition {cond!r}; registered: {', '.join(CONDITIONS)}")
    if not go:
        sys.exit("refused: registered conditions run only after the merge and the coordinator's GO (pass --go)")
    from concurrent.futures import ProcessPoolExecutor
    step = 2_000
    tasks = [(cond, label, lo, min(lo + step, n), n_bg) for label in rbt78.POOLS for lo in range(0, n, step)]
    res = {"condition": cond, "fields": CONDITIONS[cond], "n_per_pool": n, "n_bg_per_pool": n_bg,
           "aux_key": AUX_KEY, "git": _git_head(), "pools": {}, "arrivals": [], "bg": [], "sham": 0, "mismatch": 0,
           "pair_events": {"events": 0, "refused": 0, "no_pair": 0}}
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(chunk, tasks):
            res["pools"][r["label"]] = res["pools"].get(r["label"], 0) + r["n"]
            res["arrivals"] += r["arrivals"]
            res["bg"] += [[r["label"]] + list(b) for b in r["bg"]]
            res["sham"] += r["sham"]
            res["mismatch"] += r["mismatch"]
            for key in ("events", "refused", "no_pair"):
                res["pair_events"][key] += r["pair_events"][key]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{cond}.json")
    json.dump(res, open(path, "w"))
    print(f"wrote {path}: {len(res['arrivals'])} arrivals over {sum(res['pools'].values())} lineages")


def _git_head():
    try:
        import subprocess
        return subprocess.check_output(["git", "-C", _ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # pragma: no cover
        return "unknown"


# --------------------------------------------------------------------------- #
# Readout: the registered rules
# --------------------------------------------------------------------------- #

def wilson(k, n, z=1.96):
    return sr.wilson(k, n, z)


def arrival_flagged(arr):
    return any(u["flip"] for u in arr["units"])


def arrival_a(arr):
    """max |a| over the lineage's predicate units (S8); None for an arrival with ANY `sign`-flipped unit, which the
    registered wording excludes from k and from I3 whole (F2, ruled option a)."""
    if arrival_flagged(arr):
        return None
    vals = [abs(u["a"]) for u in arr["units"] if np.isfinite(u["a"])]
    return max(vals) if vals else None


def arrival_a_per_unit(arr):
    """DESCRIPTIVE ONLY (F2): max |a| over the arrival's UNFLAGGED units, keeping an arrival that has a flagged unit."""
    vals = [abs(u["a"]) for u in arr["units"] if not u["flip"] and np.isfinite(u["a"])]
    return max(vals) if vals else None


def k_at(res, rung, reader=arrival_a):
    return {(a["label"], a["i"]) for a in res["arrivals"] if (reader(a) or 0.0) >= rung}


def binom_sf(b, n):
    """P(X >= b), X ~ Binomial(n, 1/2): McNemar's exact one-sided p on b of n discordant pairs."""
    return sum(math.comb(n, j) for j in range(b, n + 1)) / 2 ** n


def bg_hits(res, rung=WHOLE, unflagged=True, prefix=None):
    """(hits, denominator) over structureless background lineages."""
    rows = [b for b in res["bg"] if not b[2] and (prefix is None or b[1] < prefix)]
    if unflagged:
        rows = [b for b in rows if not b[4]]
    return sum(1 for b in rows if b[3] >= rung), len(rows)


def katz_upper(x1, n1, x0, n0, z=1.6449):
    if x1 == 0:
        return 0.0
    if x0 == 0:
        return float("inf")
    r = (x1 / n1) / (x0 / n0)
    return r * math.exp(z * math.sqrt(1 / x1 - 1 / n1 + 1 / x0 - 1 / n0))


def committed_arrivals(name):
    txt = open(os.path.join(_ROOT, "docs", "artifacts", name)).read()
    return [(lab, int(i), float(alone), float(whole)) for lab, i, alone, whole in
            re.findall(r"(\S+) lineage (\d+): \d+ unit\(s\), LINKS ALONE ([+-][\d.]+) \([^)]*\); whole brain ([+-][\d.]+)", txt)]


def binom_range(n, p, lo_q=0.005, hi_q=0.995):
    """The central 99% range of Binomial(n, p) (I5, as registered: F7).  The pmf is summed in log space (lgamma)
    over mean +- (12 sd + 10), outside which the mass is negligible, so it neither underflows at large n p
    (the fix-check of #552: exp(n log1p(-p)) is 0.0 once n p > ~745) nor walks to n."""
    if p <= 0:
        return 0, 0
    if p >= 1:
        return n, n
    mu, sd = n * p, math.sqrt(n * p * (1 - p))
    a, b = max(0, int(mu - 12 * sd - 10)), min(n, int(mu + 12 * sd + 10) + 1)
    base = math.lgamma(n + 1)
    lp, lq = math.log(p), math.log1p(-p)
    cdf, lo = 0.0, None
    for j in range(a, b + 1):
        cdf += math.exp(base - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq)
        if lo is None and cdf >= lo_q:
            lo = j
        if cdf >= hi_q:
            return lo, j
    return (lo if lo is not None else b), b


def section3_tables(c, r):
    """The registered section-3 tables for one condition (F3): per-parent counts (N4), k per 200,000 with Wilson, the
    transfer-function census (3.8), the decomposition with the slope bound (3.4, 1), the resting-input probe (11.1),
    and -- labelled DESCRIPTIVE -- the per-unit count that keeps arrivals with a flagged unit (F2)."""
    n = sum(r["pools"].values())
    arr = r["arrivals"]
    kept = [a for a in arr if not arrival_flagged(a)]
    print(f"\n### {c}: section-3 tables\n")
    k32 = len(k_at(r, RUNGS[PRIMARY]))
    lo, hi = wilson(k32, n)
    print(f"k a32 = {k32} of {n} lineages = {2e5 * k32 / max(n, 1):.2f} per 200,000 "
          f"[{2e5 * lo:.2f}, {2e5 * hi:.2f}] (Wilson 95%); {len(arr) - len(kept)} arrivals excluded whole for a flagged unit")
    kd = len(k_at(r, RUNGS[PRIMARY], reader=arrival_a_per_unit))
    print(f"DESCRIPTIVE ONLY, not registered (F2): k a32 counting each arrival's unflagged units, flagged arrivals kept = {kd}")
    par = {}
    for a in arr:
        key = (a["label"], a["parent"])
        tot, hit = par.get(key, (0, 0))
        par[key] = (tot + 1, hit + ((arrival_a(a) or 0.0) >= RUNGS[PRIMARY]))
    print("\nper parent (N4): " + "; ".join(f"{lab}#{p}: {t} arrivals, {h} >= a32" for (lab, p), (t, h) in sorted(par.items())))
    funcs = {}
    for a in arr:
        for u in a["units"]:
            funcs[u["func"]] = funcs.get(u["func"], 0) + 1
    print("transfer census of predicate units (3.8): " + ", ".join(f"{f} {x}" for f, x in sorted(funcs.items(), key=lambda t: -t[1])))
    units = [u for a in kept for u in a["units"] if "cf" in u]
    if units:
        print("\n| read (unflagged arrivals' units) | " + " | ".join(f">= {name} {x}" for name, x in RUNGS.items()) + " | median |")
        print("|---|" + "---|" * (len(RUNGS) + 1))
        cols = {"as is": [abs(u["a"]) for u in units]}
        cols.update({name: [abs(u["cf"][name]) for u in units if not u["cf_flip"][name]] for name in CF})
        cols["resting input (11.1, descriptive)"] = [abs(u["rest"]) for u in units]
        cols["slope bound |product| x max f'"] = [FMAX[u["func"]] * abs(u["prod"]) for u in units]
        for name, v in cols.items():
            v = [x for x in v if np.isfinite(x)]
            print(f"| {name} (n={len(v)}) | " + " | ".join(str(sum(1 for x in v if x >= rr)) for rr in RUNGS.values())
                  + f" | {np.median(v) if v else float('nan'):.4f} |")
        bk = [abs(u["bk"]) for u in units]
        be = [u["bE"] for u in units]
        print(f"\n|b_k| median {np.median(bk):.2f}; max|b_E| median {np.median(be):.2f}")


def readout():
    have = {c: json.load(open(os.path.join(OUT, f"{c}.json"))) for c in CONDITIONS
            if os.path.exists(os.path.join(OUT, f"{c}.json"))}
    print("# RBT-134 readout (DESIGN.md r3, registered)\n")
    if "B0" not in have:
        print("B0 has not run: nothing can be read against it.")
        return
    void = []
    b0 = have["B0"]
    print("| condition | lineages | arrivals | flagged arrivals | k a16 | **k a32** | k a64 | k >= 6.8664 | per arrival a32 "
          "| sham arrivals | bg unflagged >= 6.8664 | bg all | flagged bg | pair events (refused full / no wheel pair) | git |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c, r in have.items():
        n = sum(r["pools"].values())
        flagged = sum(1 for a in r["arrivals"] if any(u["flip"] for u in a["units"]))
        ks = {name: len(k_at(r, x)) for name, x in RUNGS.items()}
        x, d = bg_hits(r)
        xa, da = bg_hits(r, unflagged=False)
        nfl = sum(1 for b in r["bg"] if b[4])
        lo, hi = wilson(ks[PRIMARY], len(r["arrivals"])) if r["arrivals"] else (float("nan"),) * 2
        print(f"| {c} | {n} | {len(r['arrivals'])} | {flagged} | {ks['a16']} | **{ks['a32']}** | {ks['a64']} "
              f"| {len(k_at(r, WHOLE))} | {ks[PRIMARY]}/{len(r['arrivals'])} [{100 * lo:.1f}, {100 * hi:.1f}]% "
              f"| {r['sham']} | {x}/{d} = {100 * x / max(d, 1):.3f}% | {xa}/{da} | {nfl} "
              f"| {r['pair_events']['events']} ({r['pair_events']['refused']} / {r['pair_events'].get('no_pair', 0)}) | {r['git'][:9]} |")
        if r["mismatch"]:
            void.append(f"{c}: the generalised predicate disagrees with structural_rate.motif_units on {r['mismatch']} lineages")

    print("\n## Registered section-3 tables")
    for c, r in have.items():
        section3_tables(c, r)

    # ---- controls (DESIGN.md 9)
    print("\n## Controls\n")
    for c, name in TWIN_READOUT.items():
        if c not in have:
            continue
        want = committed_arrivals(name)
        got = sorted((a["label"], a["i"]) for a in have[c]["arrivals"])
        ok = sorted((lab, i) for lab, i, *_ in want) == got
        line = f"I2 {c}: arrival set equals {name}'s {len(want)}: {'YES' if ok else 'NO'}"
        if c == "B0" and ok:  # line for line: links alone and whole brain on units[0], 4 dp
            byid = {(a["label"], a["i"]): a for a in have[c]["arrivals"]}
            same = all(abs(byid[(lab, i)]["units"][0]["a"] - alone) < 5e-5 and abs(byid[(lab, i)]["whole"] - whole) < 5e-5
                       for lab, i, alone, whole in want)
            line += f"; responses line for line: {'YES' if same else 'NO'}"
            ok = ok and same
        print(line)
        if not ok:
            void.append(line)
    if b0["n_bg_per_pool"] >= 5_000:
        for kind, (x0, d0) in B0_BG_PREFIX.items():
            x, d = bg_hits(b0, unflagged=(kind == "unflagged"), prefix=5_000)
            ok = (x, d) == (x0, d0)
            print(f"B0 background, first 5,000 per pool, {kind}: {x} of {d} (registered {x0} of {d0}): {'YES' if ok else 'NO'}")
            if not ok:
                void.append(f"B0 background prefix {kind}")
    for c, r in have.items():
        viol = [(a["label"], a["i"], u["func"]) for a in r["arrivals"] if not arrival_flagged(a) for u in a["units"]
                if np.isfinite(u["a"]) and abs(u["a"]) > FMAX[u["func"]] * abs(u["prod"]) * (1 + 1e-9) + 1e-12]
        k32 = len(k_at(r, RUNGS[PRIMARY]))
        bound = CHECK_BOUND.get(c)
        bad = bool(viol) or (bound is not None and k32 > bound)
        print(f"I3 {c}: slope-bound violations {len(viol)}" + (f"; k a32 {k32} <= {bound}: {'YES' if k32 <= bound else 'NO'}" if bound is not None else ""))
        if bad:
            void.append(f"I3 {c}")
        n_lin = sum(r["pools"].values())
        if c in PAIR_CONDITIONS:
            # amendment I5-a (coordinator, pre-data): the pair event wires only the food noses (_wheel_pairs selects
            # source == "food"), so this condition is not sensor-blind; its agent sham is checked against B0's food rate
            ref_k, ref_n, ref = len(b0["arrivals"]), sum(b0["pools"].values()), "B0's food count"
        else:
            ref_k, ref_n, ref = len(r["arrivals"]), n_lin, "the food count"
        lo, hi = binom_range(n_lin, ref_k / ref_n if ref_n else 0.0)
        ok5 = lo <= r["sham"] <= hi
        print(f"I5 {c}: sham arrivals {r['sham']} within the 99% Binomial({n_lin}, {ref_k}/{ref_n}) range "
              f"[{lo}, {hi}] of {ref}: {'YES' if ok5 else 'NO'}")
        if not ok5:
            void.append(f"I5 {c}")
    if "B0" in have:
        k0 = k_at(b0, RUNGS[PRIMARY])
        if k0:
            void.append(f"B0's own k at a32 is {len(k0)}, not 0")

    # ---- verdicts
    def verdict(c, alpha=None):
        r = have[c]
        kc, k0 = k_at(r, RUNGS[PRIMARY]), k_at(b0, RUNGS[PRIMARY])
        b, cc = len(kc - k0), len(k0 - kc)
        p = binom_sf(b, b + cc) if b + cc else 1.0
        x1, n1 = bg_hits(r)
        x0, n0 = bg_hits(b0)
        up = katz_upper(x1, n1, x0, n0)
        return b, cc, p, x1, n1, x0, n0, up

    print("\n## The family (Holm, m = 2; DESIGN.md 4, 6)\n")
    fam = [c for c in FAMILY if c in have]
    if len(fam) < len(FAMILY):
        print(f"incomplete: {', '.join(c for c in FAMILY if c not in have)} not yet run; no family verdict.")
    else:
        rows = {c: verdict(c) for c in fam}
        order = sorted(fam, key=lambda c: rows[c][2])
        alive = True
        for j, c in enumerate(order):
            b, cc, p, x1, n1, x0, n0, up = rows[c]
            a_j = 0.05 / (len(order) - j)
            rej = alive and p <= a_j
            alive = rej
            holds = up <= MARGIN
            v = ("PASS" if holds else "MOVES-WITH-BACKGROUND") if rej else "NULL"
            print(f"{c}: discordant {b} up / {cc} down, p = {p:.4g} against alpha {a_j:.4f}: {'REJECTS' if rej else 'does not reject'}; "
                  f"background {x1}/{n1} vs B0 {x0}/{n0}, ratio upper bound {up:.3f} {'<=' if holds else '>'} {MARGIN}: "
                  f"{'HOLDS' if holds else 'fails'}  ->  **{v}**")
    print("\n## Checks and the positive control\n")
    for c in ("A0", "P1", "P4", "P5", "C+"):
        if c not in have:
            continue
        b, cc, p, x1, n1, x0, n0, up = verdict(c)
        k32 = len(k_at(have[c], RUNGS[PRIMARY]))
        extra = ""
        if c in CEILING:
            extra = f"; ceiling {CEILING[c]}: {'CEILING FAILURE (k >= 6)' if k32 >= 6 else 'held'}"
        if c == "C+":
            ok = p <= 0.05 / 2 and k32 >= 6 and up <= MARGIN
            extra = f"; must PASS: {'PASS' if ok else 'FAILED -> VOID (I4)'}"
            if not ok:
                void.append("I4 C+")
        print(f"{c}: k a32 {k32}, p = {p:.4g}, background upper ratio {up:.3f}{extra}")
    print("\n## VOID\n")
    print("none" if not void else "\n".join(f"- {v}" for v in void))


# --------------------------------------------------------------------------- #
# Re-signing (DESIGN.md 3.6): arrivals with own-link |a| >= 6.2831, at most 400 by lineage index
# --------------------------------------------------------------------------- #

def _resign_one(task):
    cond, label, i, a = task
    ra = _load("ra91", os.path.join(_ROOT, "runs", "RBT-91", "resign_arrivals.py"))
    cfg, pool = rbt78._load(label)
    fields = CONDITIONS[cond]
    mcfg = replace(cfg.mutation, add_link_rate=ADD, remove_link_rate=REM, **fields)
    seed = [rbt78.MASTER_SEED, zlib.crc32(label.encode()), K, i]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    aux = np.random.default_rng(np.random.SeedSequence(seed + [AUX_KEY]))
    g = pool[i % len(pool)]
    for _ in range(K):
        g = mutate_controller(g, rng, mcfg, aux_rng=aux)
    h, R = ra.heading(g, cfg)
    return label, i, a, h, R, ra.rbt80.FOUNDER_BACKWARD


def resign(cond, cap, workers, go=False):
    if not go:
        sys.exit("refused: re-signing runs only after the merge and the coordinator's GO (pass --go)")
    r = json.load(open(os.path.join(OUT, f"{cond}.json")))
    rows = []
    for arr in sorted(r["arrivals"], key=lambda x: (x["label"], x["i"])):
        if arrival_flagged(arr):
            continue  # excluded from k whole (F2 option a), so not re-signed either
        vals = [u for u in arr["units"] if np.isfinite(u["a"])]
        if vals:
            best = max(vals, key=lambda u: abs(u["a"]))
            if abs(best["a"]) >= RUNGS["a16"]:
                rows.append((cond, arr["label"], arr["i"], best["a"]))
    rows = sorted(rows, key=lambda t: t[2])[:cap]
    from multiprocessing import get_context
    with get_context("fork").Pool(workers) as p:
        res = p.map(_resign_one, rows)
    comp = anti = und = 0
    lines = []
    for label, i, a, h, R, fb in res:
        if h is None or abs(abs(h) - 90.0) < 15.0:
            und += 1
            verdict = "UNDETERMINED"
        else:
            signed = a if ((abs(h) > 90) == fb) else -a  # own-link sign (ERRATA.md:141)
            comp += signed > 0
            anti += signed <= 0
            verdict = "COMPASS" if signed > 0 else "ANTI"
        lines.append(f"| {label} #{i} | {a:+.4f} | {h if h is None else round(h, 1)} | {R:.2f} | {verdict} |")
    out = os.path.join(OUT, f"{cond}-resign.txt")
    with open(out, "w") as f:
        f.write(f"# {cond}: re-signed at the reference probe (16 x 15 s), own-link sign, cap {cap}\n\n")
        f.write("| arrival | own-link a | heading | R | verdict |\n|---|---|---|---|---|\n")
        f.write("\n".join(lines) + f"\n\ncompasses {comp}, anti {anti}, undetermined {und} of {len(res)}\n")
    print(f"wrote {out}")


# --------------------------------------------------------------------------- #

def smoke(n=150, workers=2):
    """B0 only (the default operator, published), a few hundred lineages: the pipeline runs and agrees with RBT-91."""
    from concurrent.futures import ProcessPoolExecutor
    tasks = [("B0", label, 0, n, n) for label in rbt78.POOLS]
    with ProcessPoolExecutor(workers) as ex:
        rs = list(ex.map(chunk, tasks))
    mism = sum(r["mismatch"] for r in rs)
    arr = [a for r in rs for a in r["arrivals"]]
    want = [(lab, i) for lab, i, *_ in committed_arrivals("RBT-91-alone-baseline.txt") if i < n]
    ok = sorted((a["label"], a["i"]) for a in arr) == sorted(want) and mism == 0
    print(f"smoke B0 n={n}/pool: arrivals {len(arr)} (committed below {n}: {len(want)}), predicate mismatches {mism}, "
          f"background rows {sum(len(r['bg']) for r in rs)}: {'OK' if ok else 'FAILED'}")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("cond")
    p.add_argument("--n", type=int, default=100_000)
    p.add_argument("--n-bg", type=int, default=20_000)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--go", action="store_true")
    p = sub.add_parser("resign")
    p.add_argument("cond")
    p.add_argument("--cap", type=int, default=400)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--go", action="store_true")
    sub.add_parser("readout")
    p = sub.add_parser("smoke")
    p.add_argument("--n", type=int, default=150)
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.cond, a.n, a.n_bg, a.workers, a.go)
    elif a.cmd == "resign":
        resign(a.cond, a.cap, a.workers, a.go)
    elif a.cmd == "readout":
        readout()
    else:
        sys.exit(0 if smoke(a.n) else 1)


if __name__ == "__main__":
    main()
