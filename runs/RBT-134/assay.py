"""RBT-134: the registered proposal-rate assay, Pioneer (runs/RBT-134/DESIGN.md r3, sections 3, 4, 6, 9).

RBT-91's instrument, imported, not reimplemented (`runs/RBT-91/structural_rate.py`): the predicate, the probes,
RBT-78's pools, MASTER_SEED and the lineage seeds.  One pass per condition: 19 `mutate_controller` mutations from
the committed parents, 100,000 lineages per pool (200,000), add 0.15 rem 0.1, the condition's MutationConfig fields,
and the registered auxiliary stream SeedSequence([MASTER_SEED, crc32(label), 19, i, 134]) for every extra draw.

    assay.py run COND --go [--n 100000] [--n-bg 20000] [--workers 4]   -> OUT/COND.json
    assay.py resign COND --go [--cap 400] [--workers 4]                 -> OUT/COND-resign.txt
    assay.py readout                                                    -> stdout (tee OUT/readout.txt)
    assay.py smoke                                                      -> a tiny B0 pass and the self-checks
    assay.py run134b COND --seed S --go [--swap] [--n ..] [--n-bg ..]   -> OUT/134b-S/COND[-swap].json (DESIGN-134b.md; C-: n = n_bg)
    assay.py readout134b --seed S | validate134b                        -> stdout

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
    with open(path + ".tmp", "w") as f:  # atomic: a partial JSON never sits at the final path (lane restarts)
        json.dump(res, f)
    os.replace(path + ".tmp", path)
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


def check_i2(have, void):
    """I2 (DESIGN.md 9): the twin conditions reproduce their committed arrival sets; B0 line for line."""
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


def check_i3(c, r, void):
    """I3 (DESIGN.md 9): no unflagged probe above the slope bound; the bounded checks' k at a32."""
    viol = [(a["label"], a["i"], u["func"]) for a in r["arrivals"] if not arrival_flagged(a) for u in a["units"]
            if np.isfinite(u["a"]) and abs(u["a"]) > FMAX[u["func"]] * abs(u["prod"]) * (1 + 1e-9) + 1e-12]
    k32 = len(k_at(r, RUNGS[PRIMARY]))
    bound = CHECK_BOUND.get(c)
    bad = bool(viol) or (bound is not None and k32 > bound)
    print(f"I3 {c}: slope-bound violations {len(viol)}" + (f"; k a32 {k32} <= {bound}: {'YES' if k32 <= bound else 'NO'}" if bound is not None else ""))
    if bad:
        void.append(f"I3 {c}")


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
    check_i2(have, void)
    if b0["n_bg_per_pool"] >= 5_000:
        for kind, (x0, d0) in B0_BG_PREFIX.items():
            x, d = bg_hits(b0, unflagged=(kind == "unflagged"), prefix=5_000)
            ok = (x, d) == (x0, d0)
            print(f"B0 background, first 5,000 per pool, {kind}: {x} of {d} (registered {x0} of {d0}): {'YES' if ok else 'NO'}")
            if not ok:
                void.append(f"B0 background prefix {kind}")
    for c, r in have.items():
        check_i3(c, r, void)
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
    with open(out + ".tmp", "w") as f:  # atomic, as `run` (the lanes treat an existing file as complete)
        f.write(f"# {cond}: re-signed at the reference probe (16 x 15 s), own-link sign, cap {cap}\n\n")
        f.write("| arrival | own-link a | heading | R | verdict |\n|---|---|---|---|---|\n")
        f.write("\n".join(lines) + f"\n\ncompasses {comp}, anti {anti}, undetermined {und} of {len(res)}\n")
    os.replace(out + ".tmp", out)
    print(f"wrote {out}")


# --------------------------------------------------------------------------- #
# RBT-134b (runs/RBT-134/DESIGN-134b.md): the redesigned C+, the never-structured background, I5-S and I9.
# The r3 path above (`run`, `chunk`, `readout`, CONDITIONS) is unchanged; 134b's runs write under OUT/134b-<seed>/.
# --------------------------------------------------------------------------- #

#: held-out validation seeds (DESIGN-134b.md 5): neither MASTER_SEED 20260912 nor GATE-FAILURE.md 3.4's 20261011
HELDOUT_SEEDS = (20261101, 20261102)
#: C+'s rate ladder (DESIGN-134b.md 3.2): the same plant as r3's C+ (x16, bias 0, tanh), at a family-scale rate
CPLUS_LADDER = (5e-5, 2e-4, 1e-3)
_CPLUS = {"pair_event_scale": 16.0, "pair_event_zero_bias": True}
#: the C+ rung registered for the MASTER_SEED run; set by the registration amendment after validation, never before
CPLUS_REGISTERED = None
CONDITIONS_134B = {
    "B0": {},
    **{f"C+L{j + 1}": {"pair_event_rate": r, **_CPLUS} for j, r in enumerate(CPLUS_LADDER)},
    "C-": {"weight_sigma": 4.0},  #: RBT-91's coupled widening: a known whole-brain pump (DESIGN-134b.md 4.4)
    **{c: CONDITIONS[c] for c in ("A0", "P1", "P2", "P3", "P4", "P5")},
}
VALIDATION_CONDITIONS = ("B0", "C+L1", "C+L2", "C+L3", "C-")
#: I5-S applies (DESIGN-134b.md 6).  C- is sensor-blind too, but its swap is not run (trim iii, DESIGN-134b.md 8)
SENSOR_BLIND_134B = ("B0", "A0", "P1", "P2", "P3", "P4")
#: trim (iv): at MASTER_SEED, I5-S B0 is the RBT-134 diagnosis's swap token on B0 (GATE-FAILURE.md 4.2 I5-3; relayed
#: I5-A with swap EXACT), cited and not re-run: the same identity on the same lineages (I2 B0 checks they are r3's)
I5S_B0_MASTER_CITED = "EXACT"
#: C- is sealed (DESIGN-134b.md 4.4, review M2): it runs on its background block only (n = n_bg, trim ii), records no
#: arrival, food or sham set, and its held-out readout prints only its token, until the registered readout
SEALED_134B = ("C-",)
ACCEPT_K = 20  #: a C+ rung is accepted on a held-out seed only with k a32 >= 20 there (DESIGN-134b.md 5.2)
#: the owner's cost cap for all 134b compute from validation on (OWNER-DECISIONS-2026-10-10 item 7; DESIGN-134b.md 8)
CPU_CAP_134B = 30.0
#: planning CPU-h, x1.5 margin over design-134b/timing.txt (DESIGN-134b.md 8): a full 134b condition (200,000
#: lineages, 40,000 tracked and probed), C- (40,000 tracked and probed), a swap regeneration (200,000, predicates only)
COST_H = {"condition": 0.9, "C-": 0.4, "swap": 0.7}
RESIGN_S = 5.6  #: CPU-s per re-signed robot: 16 seasons x 0.35 s (DESIGN.md 12)
RESIGN_RESERVE_H = 5.0  #: re-signing at its cap (DESIGN.md 12), held in reserve until it runs
#: the registered run still to come, at MASTER_SEED: B0, the C+ rung, A0, P1-P5 and the swaps of A0, P1-P4
REGISTERED_RUN_H = 8 * COST_H["condition"] + 5 * COST_H["swap"]


def swap_sources(g):
    """A copy of genotype g with every `food` and `agent` sensor relabelled into each other; nothing else changes."""
    g = g.copy()
    for _, brain in g.brains():
        for u in brain.units:
            if u.kind == "sensor" and u.source in ("food", "agent"):
                u.source = "agent" if u.source == "food" else "food"
    return g


def _planted_total():
    c = genetics.PAIR_EVENT_COUNTS
    return c["events"] - c["refused"] - c["no_pair"]


def lineage_134b(label, i, fields, master, track=False, swap=False):
    """(final phenotype, parent index, ever-structured, planted) for lineage i at `master`.

    ever-structured: the food predicate held at some depth 0..K (only computed when track; else None).
    planted: a pair event wired its unit in this lineage.  The streams are r3's (`lineage`), keyed by `master`."""
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=ADD, remove_link_rate=REM, **fields)
    seed = [master, zlib.crc32(label.encode()), K, i]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    aux = np.random.default_rng(np.random.SeedSequence(seed + [AUX_KEY]))
    g = pool[i % len(pool)]
    if swap:
        g = swap_sources(g)
    syn = cfg.sim.synthesis
    ever = bool(predicate(synthesize(g, syn), "food")) if track else None
    before = _planted_total()
    for _ in range(K):
        g = mutate_controller(g, rng, mcfg, aux_rng=aux)
        if track and not ever:
            ever = bool(predicate(synthesize(g, syn), "food"))
    return synthesize(g, syn), i % len(pool), ever, _planted_total() > before


def chunk_134b(task):
    """One block of lineages.  bg rows are r3's [label, i, structured, |whole a|, flag] plus [ever, planted]."""
    cond, label, lo, hi, n_bg, master, swap = task
    fields = CONDITIONS_134B[cond]
    sealed = cond in SEALED_134B  # background rows only: no arrival, food or sham set (DESIGN-134b.md 4.4)
    genetics.PAIR_EVENT_COUNTS.update(events=0, refused=0, no_pair=0)
    out = {"label": label, "n": hi - lo, "arrivals": [], "bg": [], "food_ids": [], "sham_ids": [], "planted": [],
           "mismatch": 0}
    for i in range(lo, hi):
        ph, parent, ever, planted = lineage_134b(label, i, fields, master, track=(i < n_bg and not swap), swap=swap)
        units = predicate(ph, "food")
        if units and not sealed:
            out["food_ids"].append(i)
        if not sealed and predicate(ph, "agent"):
            out["sham_ids"].append(i)
        if swap:
            continue  # I5-S: the two predicate sets only, no probes
        out["mismatch"] += units != sr.motif_units(ph)
        if planted:
            if ever is None:  # outside the background block: re-run tracked (deterministic) for I9
                saved = dict(genetics.PAIR_EVENT_COUNTS)
                ever = lineage_134b(label, i, fields, master, track=True)[2]
                genetics.PAIR_EVENT_COUNTS.update(saved)
            out["planted"].append([i, bool(ever)])
        whole = None
        if units and not sealed:
            whole = float(sr.small_signal_a(ph))
            out["arrivals"].append({"label": label, "i": i, "parent": parent, "whole": whole,
                                    "units": [unit_record(ph, k) for k in units]})
        if i < n_bg:
            if whole is None:
                whole = float(sr.small_signal_a(ph))
            out["bg"].append((i, bool(units), abs(whole) if np.isfinite(whole) else 0.0,
                              bool(dec.sign_flip(ph, None)), bool(ever), bool(planted)))
    out["pair_events"] = dict(genetics.PAIR_EVENT_COUNTS)
    return out


def out_134b(master):
    return os.path.join(OUT, f"134b-{master}")


def check_seed_134b(cond, master):
    """The run guard (DESIGN-134b.md 5, 7): held-out seeds run the validation conditions only; MASTER_SEED runs only
    after the registration amendment has set CPLUS_REGISTERED, and never a C+ rung other than the registered one."""
    if cond not in CONDITIONS_134B:
        return f"unknown 134b condition {cond!r}"
    if master in HELDOUT_SEEDS:
        return None if cond in VALIDATION_CONDITIONS else f"{cond} does not run at a held-out seed"
    if master != rbt78.MASTER_SEED:
        return f"seed {master} is neither MASTER_SEED nor a registered held-out seed {HELDOUT_SEEDS}"
    if CPLUS_REGISTERED is None:
        return "MASTER_SEED runs wait for the registration amendment (CPLUS_REGISTERED is not set)"
    if cond == "C-" or (cond.startswith("C+L") and cond != CPLUS_REGISTERED):
        return f"{cond} does not run at MASTER_SEED"
    return None


def check_swap_134b(cond, master):
    """Which swap regenerations run (DESIGN-134b.md 6.1, 8): B0's at the held-out seeds; A0's and P1-P4's at
    MASTER_SEED.  No C- swap (trim iii); no B0 swap at MASTER_SEED, where the diagnosis's EXACT is cited (trim iv)."""
    if cond not in SENSOR_BLIND_134B:
        return f"I5-S does not run on {cond} (DESIGN-134b.md 6.1, 8)"
    if master in HELDOUT_SEEDS and cond != "B0":
        return f"no {cond} swap at a held-out seed"
    if master == rbt78.MASTER_SEED and cond == "B0":
        return "B0's swap at MASTER_SEED is the RBT-134 diagnosis's EXACT, cited, not re-run (trim iv)"
    return None


def cpu_h_now():
    """CPU-h used so far by this process and its reaped children."""
    import resource
    s, c = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return (s.ru_utime + s.ru_stime + c.ru_utime + c.ru_stime) / 3600


def run_134b(cond, master, n, n_bg, workers, go, swap=False):
    why = check_seed_134b(cond, master)
    if why:
        sys.exit(f"refused: {why}")
    if not go:
        sys.exit("refused: 134b runs only after review and the owner's GO (pass --go)")
    if swap and check_swap_134b(cond, master):
        sys.exit(f"refused: {check_swap_134b(cond, master)}")
    if cond in SEALED_134B:
        n = n_bg  # trim (ii): C- runs on its background block only
    # the cost stop rule, on every run (DESIGN-134b.md 8): this run, plus what is registered still to come
    item = COST_H["swap"] if swap else COST_H.get(cond, COST_H["condition"])
    later = (REGISTERED_RUN_H if master in HELDOUT_SEEDS else 0.0) + RESIGN_RESERVE_H
    stop = cost_gate_134b(item * n / 100_000 if cond not in SEALED_134B else item, still_to_come=later)
    if stop:
        sys.exit(stop)
    cpu0 = cpu_h_now()
    from concurrent.futures import ProcessPoolExecutor
    step = 2_000
    tasks = [(cond, label, lo, min(lo + step, n), n_bg, master, swap) for label in rbt78.POOLS for lo in range(0, n, step)]
    res = {"condition": cond, "fields": CONDITIONS_134B[cond], "master_seed": master, "swap": swap, "n_per_pool": n,
           "n_bg_per_pool": n_bg, "aux_key": AUX_KEY, "git": _git_head(), "pools": {}, "arrivals": [], "bg": [],
           "food_ids": [], "sham_ids": [], "planted": [], "mismatch": 0,
           "pair_events": {"events": 0, "refused": 0, "no_pair": 0}}
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(chunk_134b, tasks):
            lab = r["label"]
            res["pools"][lab] = res["pools"].get(lab, 0) + r["n"]
            res["arrivals"] += r["arrivals"]
            res["bg"] += [[lab] + list(b) for b in r["bg"]]
            for key in ("food_ids", "sham_ids", "planted"):
                res[key] += [[lab] + (x if isinstance(x, list) else [x]) for x in r[key]]
            res["mismatch"] += r["mismatch"]
            for key in ("events", "refused", "no_pair"):
                res["pair_events"][key] += r["pair_events"][key]
    res["cpu_h"] = cpu_h_now() - cpu0  # read by the cost stop rule (DESIGN-134b.md 8); never relayed
    d = out_134b(master)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{cond}{'-swap' if swap else ''}.json")
    with open(path + ".tmp", "w") as f:
        json.dump(res, f)
    os.replace(path + ".tmp", path)
    print(f"wrote {path}")


def bg_never(res, rung=WHOLE):
    """THE 134b BACKGROUND (DESIGN-134b.md 4.1): unflagged background lineages on which the food predicate held at
    no depth 0..19, and the share of them whose whole-brain |a| >= rung.  (hits, denominator)."""
    rows = [b for b in res["bg"] if not b[5] and not b[4]]
    return sum(1 for b in rows if b[3] >= rung), len(rows)


def katz_lower(x1, n1, x0, n0, z=1.6449):
    """The one-sided 95% Katz lower bound on the rate ratio (C-'s requirement, DESIGN-134b.md 4.4)."""
    if x1 == 0:
        return 0.0
    if x0 == 0:
        return float("inf")
    r = (x1 / n1) / (x0 / n0)
    return r * math.exp(-z * math.sqrt(1 / x1 - 1 / n1 + 1 / x0 - 1 / n0))


def binom_two_sided(b, n):
    """Exact two-sided p of b of n under Binomial(n, 1/2) (U2's paired test, descriptive in 134b)."""
    if n == 0:
        return 1.0
    lo = sum(math.comb(n, j) for j in range(0, b + 1)) / 2 ** n
    return min(1.0, 2 * min(lo, binom_sf(b, n)))


def _ids(res, key):
    return {(x[0], x[1]) for x in res[key]}


def i9_leaks(c, b0):
    """I9 (DESIGN-134b.md 4.3): the never-structured background is remnant-proof on a pair condition.  Returns the
    list of violations (empty = holds):
      (a) every planted lineage is ever-structured;
      (b) every never-structured background row of c is unplanted and equals B0's row for the same lineage (same
          structured, |a|, flag and ever-structured): an unplanted pair-condition lineage IS B0's lineage;
      (c) c's food and sham sets, restricted to unplanted lineages, equal B0's restricted the same way."""
    bad = [f"planted lineage {lab} #{i} never carried the structure" for lab, i, ever in c["planted"] if not ever]
    planted = {(lab, i) for lab, i, _ in c["planted"]}
    ref = {(b[0], b[1]): b for b in b0["bg"]}
    for b in c["bg"]:
        if b[5]:
            continue
        key = (b[0], b[1])
        if b[6]:
            bad.append(f"never-structured background lineage {key} is planted")
        elif key not in ref or list(ref[key][2:6]) != list(b[2:6]):
            bad.append(f"never-structured background lineage {key} differs from B0's")
    for key in ("food_ids", "sham_ids"):
        if _ids(c, key) - planted != _ids(b0, key) - planted:
            bad.append(f"{key} on unplanted lineages differ from B0's")
    return bad


def i5s(orig, swp):
    """I5-S (DESIGN-134b.md 6): regenerated from food<->agent swapped parents, the food set is the original sham set
    and the sham set is the original food set, lineage by lineage."""
    return _ids(swp, "food_ids") == _ids(orig, "sham_ids") and _ids(swp, "sham_ids") == _ids(orig, "food_ids")


def exclusion_flag(r, b0):
    """EXCLUSION-FLAG (DESIGN-134b.md 4.6, review M5): the never-structured measure leaves out a condition's remnants
    (unflagged background lineages structured at some depth, not at 19).  Flagged iff the condition's remnant share
    exceeds B0's by at least B0's never-structured hit rate: the excess remnants, were every one a hit, would alone
    take the ratio from 1 to the margin 2.  Descriptive: printed beside the verdict, never changes it.
    Returns (excess share, threshold, flagged)."""
    def share(res):
        rows = [b for b in res["bg"] if not b[4]]
        return sum(1 for b in rows if b[5] and not b[2]) / len(rows) if rows else 0.0
    x0, n0 = bg_never(b0)
    excess, thr = share(r) - share(b0), (x0 / n0 if n0 else 0.0)
    return excess, thr, excess >= thr


def spent_134b():
    """CPU-h recorded by every 134b run so far, at every seed (each JSON's cpu_h; DESIGN-134b.md 8)."""
    import glob
    return sum(json.load(open(p)).get("cpu_h", 0.0) for p in glob.glob(os.path.join(OUT, "134b-*", "*.json")))


def cost_gate_134b(item_h, spent=None, still_to_come=0.0):
    """THE COST STOP RULE (DESIGN-134b.md 8): an item may start only if spent + the item + what is still registered to
    come stays within CPU_CAP_134B.  Returns None (go) or the stop message (stop, and return to the owner)."""
    spent = spent_134b() if spent is None else spent
    total = spent + item_h + still_to_come
    if total > CPU_CAP_134B:
        return (f"STOP-COST: spent {spent:.1f} + this item {item_h:.1f} + still to come {still_to_come:.1f} = "
                f"{total:.1f} CPU-h > the cap {CPU_CAP_134B:.0f}: stop and return to the owner")
    return None


def resign_cost_h(n_robots):
    """Planning CPU-h for re-signing n robots (x1.5, as COST_H)."""
    return 1.5 * n_robots * RESIGN_S / 3600


def verdict_134b(r, b0):
    """(k a32, discordant up, down, McNemar p, never-structured bg hits/n, B0's, Katz upper, PASS)."""
    kc, k0 = k_at(r, RUNGS[PRIMARY]), k_at(b0, RUNGS[PRIMARY])
    up, down = len(kc - k0), len(k0 - kc)
    p = binom_sf(up, up + down) if up + down else 1.0
    x1, n1 = bg_never(r)
    x0, n0 = bg_never(b0)
    ku = katz_upper(x1, n1, x0, n0)
    return len(kc), up, down, p, (x1, n1), (x0, n0), ku, (p <= 0.05 / 2 and len(kc) >= 6 and ku <= MARGIN)


def readout_134b(master):
    """The 134b readout at one seed: per-condition table, I4b, I9, I5-S, C-, and (MASTER_SEED) the family.
    Returns {name: True/False} for the acceptance items the validation summary reads."""
    d = out_134b(master)
    have = {c: json.load(open(os.path.join(d, f"{c}.json"))) for c in CONDITIONS_134B
            if os.path.exists(os.path.join(d, f"{c}.json"))}
    swaps = {c: json.load(open(os.path.join(d, f"{c}-swap.json"))) for c in SENSOR_BLIND_134B
             if os.path.exists(os.path.join(d, f"{c}-swap.json"))}
    held = master in HELDOUT_SEEDS
    print(f"# RBT-134b readout, seed {master} ({'HELD-OUT VALIDATION: a tuning set, never pooled' if held else 'registered'})\n")
    acc = {}
    if "B0" not in have:
        print("B0 has not run at this seed: nothing can be read against it.")
        return acc
    b0, void = have["B0"], []
    print("| condition | lineages | arrivals | k a32 | sham | planted | remnants (ever, not final) | bg never-structured "
          "(134b) | bg structureless at 19 (r3, descriptive) | remnant share over B0's / flag threshold (4.6) "
          "| pair events (refused / no pair) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for c, r in have.items():
        if c in SEALED_134B:  # DESIGN-134b.md 4.4: only C-'s token is read before the registered readout
            print(f"| {c} | sealed until the registered readout: only its token below is read |" + " |" * 9)
            if r["mismatch"]:
                void.append(f"{c}: predicate mismatch")
            continue
        x, n = bg_never(r)
        xo, no = bg_hits(r)
        rem = sum(1 for b in r["bg"] if b[5] and not b[2])
        ex, thr, flag = exclusion_flag(r, b0)
        pe = r["pair_events"]
        print(f"| {c} | {sum(r['pools'].values())} | {len(r['arrivals'])} | {len(k_at(r, RUNGS[PRIMARY]))} "
              f"| {len(r['sham_ids'])} | {len(r['planted'])} | {rem} | {x}/{n} | {xo}/{no} "
              f"| {ex:+.5f} / {thr:.5f}{' EXCLUSION-FLAG' if flag else ''} "
              f"| {pe['events']} ({pe['refused']} / {pe['no_pair']}) |")
        if r["mismatch"]:
            void.append(f"{c}: predicate mismatch on {r['mismatch']} lineages")
    if not held:
        print("\n## Registered section-3 tables (carried over, DESIGN.md 3)")
        for c, r in have.items():
            if c not in SEALED_134B:
                section3_tables(c, r)
    print("\n## Controls\n")
    if not held:  # carried over unchanged (DESIGN-134b.md 7): I2, I3
        check_i2(have, void)
        for c, r in have.items():
            if c not in SEALED_134B:
                check_i3(c, r, void)
        if k_at(b0, RUNGS[PRIMARY]):
            void.append("B0's own k at a32 is not 0")
    if not held and b0["n_bg_per_pool"] >= 5_000:  # r3's continuity, on r3's measure
        for kind, (x0, d0) in B0_BG_PREFIX.items():
            x, dd = bg_hits(b0, unflagged=(kind == "unflagged"), prefix=5_000)
            ok = (x, dd) == (x0, d0)
            print(f"B0 r3 background, first 5,000 per pool, {kind}: {x} of {dd} (registered {x0} of {d0}): {'YES' if ok else 'NO'}")
            if not ok:
                void.append(f"B0 background prefix {kind}")
    for c, r in have.items():
        if not c.startswith("C+L") and c != "P5":
            continue
        leaks = i9_leaks(r, b0)
        print(f"I9 {c}: never-structured background remnant-proof: {'YES' if not leaks else 'NO'}"
              + "".join(f"\n  - {x}" for x in leaks[:20]))
        acc[f"I9 {c}"] = not leaks
        if leaks:
            void.append(f"I9 {c}")
    for c in SENSOR_BLIND_134B:
        if c not in have:
            continue
        if c == "B0" and not held:  # trim (iv): the diagnosis's swap on these same lineages, cited
            ok = I5S_B0_MASTER_CITED == "EXACT"
            print(f"I5-S B0: cited, the RBT-134 diagnosis's swap on B0 at MASTER_SEED: {I5S_B0_MASTER_CITED} "
                  f"(the same lineages: I2 B0 above): {'YES' if ok else 'NO'}")
        elif c not in swaps:
            print(f"I5-S {c}: swap regeneration missing: NO")
            ok = False
        else:
            ok = i5s(have[c], swaps[c])
            print(f"I5-S {c}: swapped food set = sham set and swapped sham set = food set: {'YES' if ok else 'NO'}")
        acc[f"I5-S {c}"] = ok
        if not ok:
            void.append(f"I5-S {c}")
    f0, s0 = _ids(b0, "food_ids"), _ids(b0, "sham_ids")
    print(f"U2 (descriptive, a property of the parents): B0 food-only {len(f0 - s0)}, sham-only {len(s0 - f0)}, "
          f"two-sided exact p {binom_two_sided(len(f0 - s0), len(f0 ^ s0)):.4g}")
    for c, r in have.items():
        if not c.startswith("C+L"):
            continue
        k, up, down, p, (x1, n1), (x0, n0), ku, ok = verdict_134b(r, b0)
        acc[f"I4b {c}"] = ok
        line = (f"I4b {c}: k a32 {k}, discordant {up} up / {down} down, p = {p:.4g}; never-structured background "
                f"{x1}/{n1} vs B0 {x0}/{n0}, ratio upper bound {ku:.3f}: {'PASS' if ok else 'not PASS'}"
                f"{' (EXCLUSION-FLAG, descriptive)' if exclusion_flag(r, b0)[2] else ''}")
        if held:
            acc[f"ACCEPT {c}"] = ok and k >= ACCEPT_K and acc.get(f"I9 {c}", False)
            line += f"; accepted at this seed (PASS, k >= {ACCEPT_K}, I9): {'YES' if acc[f'ACCEPT {c}'] else 'NO'}"
        elif c == CPLUS_REGISTERED and not ok:
            void.append("I4 C+")
        print(line)
    if "C-" in have:
        x1, n1 = bg_never(have["C-"])
        x0, n0 = bg_never(b0)
        lo = katz_lower(x1, n1, x0, n0)
        acc["C- fails"] = lo > MARGIN
        # sealed (review M2): the token only; C-'s counts and bound are read at the registered readout
        print(f"C- fails clearly (never-structured ratio lower bound > {MARGIN}): {'YES' if lo > MARGIN else 'NO'}")
    if not held:
        print("\n## The family (Holm, m = 2; DESIGN.md 4, 6; background: DESIGN-134b.md 4.1)\n")
        fam = [c for c in FAMILY if c in have]
        if len(fam) < len(FAMILY):
            print("incomplete: no family verdict.")
        else:
            rows = {c: verdict_134b(have[c], b0) for c in fam}
            alive = True
            for j, c in enumerate(sorted(fam, key=lambda c: rows[c][3])):
                k, up, down, p, (x1, n1), (x0, n0), ku, _ = rows[c]
                a_j = 0.05 / (len(fam) - j)
                rej = alive and p <= a_j
                alive = rej
                v = ("PASS" if ku <= MARGIN else "MOVES-WITH-BACKGROUND") if rej else "NULL"
                r3u = katz_upper(*bg_hits(have[c]), *bg_hits(b0))  # descriptive: r3's measure, remnants included
                flag = exclusion_flag(have[c], b0)[2]
                print(f"{c}: discordant {up} up / {down} down, p = {p:.4g} against alpha {a_j:.4f}; background "
                      f"{x1}/{n1} vs B0 {x0}/{n0}, ratio upper bound {ku:.3f}  ->  **{v}**"
                      f"{' with EXCLUSION-FLAG' if flag else ''}  "
                      f"(descriptive, r3's measure: ratio upper bound {r3u:.3f}, {'holds' if r3u <= MARGIN else 'fails'})")
    print("\n## VOID\n")
    print("none" if not void else "\n".join(f"- {v}" for v in void))
    acc["VOID none"] = not void
    return acc


def validation_summary():
    """DESIGN-134b.md 5.3: each held-out seed read on its own (never pooled).  ESCALATE if C- does not fail, I5-S B0
    does not hold or anything is VOID on EITHER seed; otherwise the registered C+ rung is the first rung ACCEPTED on
    both seeds.  A climb to the next rung first passes the cost stop rule (DESIGN-134b.md 8)."""
    per = {}
    for s in HELDOUT_SEEDS:
        per[s] = readout_134b(s)
        print()
    base = all(per[s].get(x, False) for s in HELDOUT_SEEDS for x in ("C- fails", "I5-S B0", "VOID none"))
    print("# 134b validation summary (each seed separately; nothing pooled)\n")
    for s in HELDOUT_SEEDS:
        print(f"seed {s}: " + ", ".join(f"{k}: {'YES' if v else 'NO'}" for k, v in sorted(per[s].items())))
    if not base:
        print("\nESCALATE: on at least one seed the background clause, I5-S or I9 failed validation (C- did not fail, "
              "I5-S B0 did not hold, or a VOID item)")
        return "ESCALATE"
    for j in range(len(CPLUS_LADDER)):  # ladder order: a rung is read only once every seed has run it
        c = f"C+L{j + 1}"
        if not all(f"ACCEPT {c}" in per[s] for s in HELDOUT_SEEDS):
            if j:  # a climb: the rung on both seeds, with the registered run and re-signing still to come
                stop = cost_gate_134b(len(HELDOUT_SEEDS) * COST_H["condition"],
                                      still_to_come=REGISTERED_RUN_H + RESIGN_RESERVE_H)
                if stop:
                    print(f"\n{stop}")
                    return "STOP-COST"
            print(f"\nWAITING: run {c} on every held-out seed")
            return "WAITING"
        if all(per[s][f"ACCEPT {c}"] for s in HELDOUT_SEEDS):
            print(f"\nREGISTER C+ = {c} ({CONDITIONS_134B[c]})")
            return c
    print("\nESCALATE: no C+ rung accepted on every held-out seed")
    return "ESCALATE"


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
    p = sub.add_parser("run134b")
    p.add_argument("cond")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--n", type=int, default=100_000)
    p.add_argument("--n-bg", type=int, default=20_000)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--swap", action="store_true")
    p.add_argument("--go", action="store_true")
    p = sub.add_parser("readout134b")
    p.add_argument("--seed", type=int, required=True)
    sub.add_parser("validate134b")
    p = sub.add_parser("smoke")
    p.add_argument("--n", type=int, default=150)
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.cond, a.n, a.n_bg, a.workers, a.go)
    elif a.cmd == "resign":
        resign(a.cond, a.cap, a.workers, a.go)
    elif a.cmd == "readout":
        readout()
    elif a.cmd == "run134b":
        run_134b(a.cond, a.seed, a.n, a.n_bg, a.workers, a.go, swap=a.swap)
    elif a.cmd == "readout134b":
        readout_134b(a.seed)
    elif a.cmd == "validate134b":
        validation_summary()
    else:
        sys.exit(0 if smoke(a.n) else 1)


if __name__ == "__main__":
    main()
