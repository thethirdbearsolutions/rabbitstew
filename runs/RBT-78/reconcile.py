"""RBT-78: direct-route and path-route compass arrival rates on one denominator.

RBT-62 puts a direct 4-link antisymmetric motif at |a| >= 32 at order 1e-77. RBT-45 puts
a >= 32 at 0.70% of 19-mutation lineages. Both cannot describe the same quantity. The
offered reconciliation is that RBT-62 counts direct nose->effector links while RBT-45
allows indirect paths through the global brain, where weights multiply along a path and
sum across many. This tests that on one denominator: same pool, same seeds, same mutation
count, both quantities per lineage.

Conventions, asserted at startup rather than asserted in prose (rule III):

    s_i = g[n_i -> e1] + g[n_i -> e2]        signed gain from nose i to the steering axis
    a   = (s1 - s2) / 2                      the gradient (compass) coefficient
    c   = (s1 + s2) / 2                      the common mode (pirouette) coefficient

    DIRECT   uses M^1 only -- nose->effector links.
    PATH     uses M^1 + ... + M^DEPTH -- what runs/RBT-45/motif.py and the PATH column of
             runs/compass-gain/steering_gain.py both compute.
    INDIRECT is PATH - DIRECT, by construction.

An antisymmetric motif at per-link weight w gives a = 2w and c = 0; a single wired nose
gives |a| = |c|. Both are asserted before anything is measured.

No world, no selection, no simulation. Usage: reconcile.py [--n 2000] [--k 19] [--workers 4]
"""

from __future__ import annotations

import argparse, json, os, sys, time, zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

from rabbitstew.analysis import _parent_pool, _run_config
from rabbitstew.fixed import drive_commands
from rabbitstew.genetics import mutate_controller
from rabbitstew.genotype import Genotype
from rabbitstew.synthesis import synthesize

MASTER_SEED = 20260912  # RBT-45's, so the drift process is the same one
DEPTH = 4
THRESHOLDS = (16, 32, 64)

#: (label, parent directory, how parents are loaded). Neither is the pool RBT-78 asks for;
#: runs/RBT-23/W4b-801 is committed nowhere, so motif.py and reach.py cannot be run as written.
POOLS = {
    "W4b-801-bests": ("docs/artifacts/RBT-23-W4b-801", "bests"),
    "P-801-final60": ("runs/RBT-19/P-801", "final"),
}


def _nose_eff(ph, source="food"):
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == source:
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return nose, eff


def terms(ph, source="food", per_depth=False):
    """((a,c) direct, (a,c) path) for one phenotype, or None if it has no two-sensor pair.

    ``source="agent"`` runs the identical computation on the agent-smell pair, which sits on
    the same two parts and carries no food gradient: a control for whether the path quantity
    is measuring a compass or just network gain (RBT-78 P3).
    """
    nose, eff = _nose_eff(ph, source)
    if len(nose) != 2 or len(eff) != 2:
        return None
    n = len(ph.units)
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += w                       # signed, unclamped -- both source scripts do this
    out = {}
    depths = (("direct", 1), ("path", DEPTH)) if not per_depth else tuple((f"d{k}", k) for k in range(1, DEPTH + 1))
    for tag, depth in depths:
        sg = {}
        for part, si in nose.items():
            v = np.zeros(n); v[si] = 1.0
            tot = np.zeros(n)
            for _ in range(depth):
                v = M @ v
                tot += v
                if not v.any():
                    break
            sg[part] = tot[eff[1]] + tot[eff[2]]
        out[tag] = ((sg[1] - sg[2]) / 2.0, (sg[1] + sg[2]) / 2.0)
    return out


# --------------------------------------------------------------------------- #
# Calibration: the instrument must register a known-present effect (rules II, III)
# --------------------------------------------------------------------------- #

def calibrate(parent, syn):
    """Round-trip both metrics against motifs whose a and c are known by construction."""
    ph = synthesize(parent, syn)
    nose, eff = _nose_eff(ph)
    assert len(nose) == 2 and len(eff) == 2, "calibration parent carries no two-nose pair"
    base = list(ph.links)
    checks = []

    for w in (1.0, 8.0, 32.0):
        # antisymmetric motif, built through the RBT-64 helper rather than by hand
        wl, wr = drive_commands(steering=w, throttle=0.0)
        assert wl == wr == w, "drive_commands no longer puts a pure steering term on both effectors"
        ph.links = [(nose[1], eff[1], w), (nose[1], eff[2], w),
                    (nose[2], eff[1], -w), (nose[2], eff[2], -w)]
        t = terms(ph)
        for tag in ("direct", "path"):
            a, c = t[tag]
            assert abs(a - 2 * w) < 1e-9, f"{tag}: motif w={w} gave a={a}, expected {2*w}"
            assert abs(c) < 1e-9, f"{tag}: motif w={w} gave c={c}, expected 0"
        checks.append(f"antisymmetric w={w:g} -> a={t['path'][0]:.1f} c={t['path'][1]:.1f} (expect a={2*w:g}, c=0)")

    # a single wired nose is half compass, half pirouette
    ph.links = [(nose[1], eff[1], 10.0)]
    a, c = terms(ph)["direct"]
    assert abs(abs(a) - abs(c)) < 1e-9, f"single nose gave |a|={abs(a)}, |c|={abs(c)}; expected equal"
    checks.append(f"single wired nose -> |a|={abs(a):.1f} = |c|={abs(c):.1f}")

    # an indirect two-link route must be invisible to DIRECT and visible to PATH
    hidden = next(i for i, u in enumerate(ph.units) if u.unit.kind == "neuron")
    ph.links = [(nose[1], hidden, 3.0), (hidden, eff[1], 5.0), (hidden, eff[2], 5.0)]
    td, tp = terms(ph)["direct"], terms(ph)["path"]
    assert abs(td[0]) < 1e-9, f"DIRECT saw an indirect route: a={td[0]}"
    assert abs(tp[0] - 15.0) < 1e-9, f"PATH gave a={tp[0]}, expected 15.0 (3*5 + 3*5)/2"
    checks.append(f"indirect 2-link route -> direct a={td[0]:.1f}, path a={tp[0]:.1f} (expect 0 and 15)")

    ph.links = base
    return checks


# --------------------------------------------------------------------------- #
# The drift process
# --------------------------------------------------------------------------- #

def run_chunk(task):
    label, lo, hi, k, add, rem = task
    cfg, pool = _load(label)
    mcfg = replace(cfg.mutation, add_link_rate=add, remove_link_rate=rem)
    rows = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(label.encode()), k, i]))
        g = pool[i % len(pool)]
        for _ in range(k):
            g = mutate_controller(g, rng, mcfg)
        ph = synthesize(g, cfg.sim.synthesis)
        t = terms(ph)
        if t is None:
            continue
        ctrl = terms(ph, source="agent")           # P3 control: same maths, no food gradient
        dep = terms(ph, per_depth=True)            # P3: where does the magnitude accumulate?
        rows.append((t["direct"][0], t["direct"][1], t["path"][0], t["path"][1],
                     (ctrl["path"][0] if ctrl else float("nan")),
                     tuple(dep[f"d{k}"][0] for k in range(1, DEPTH + 1))))
    return label, rows


_CACHE = {}


def _load(label):
    if label not in _CACHE:
        d, how = POOLS[label]
        cfg = _run_config(d)
        if how == "bests":
            pool = [Genotype.load(os.path.join(d, "conventional", f)) for f in sorted(os.listdir(os.path.join(d, "conventional")))]
        else:
            pool = _parent_pool(d, "conventional")
        _CACHE[label] = (cfg, pool)
    return _CACHE[label]


def summarise(label, rows, k, n_req):
    ad = np.array([r[0] for r in rows]); cd = np.array([r[1] for r in rows])
    ap = np.array([r[2] for r in rows]); cp = np.array([r[3] for r in rows])
    ind = ap - ad
    out = {"pool": label, "k_mut": k, "n_requested": n_req, "n_with_two_noses": len(rows),
           "direct": {"median_abs_a": float(np.median(np.abs(ad))), "max_abs_a": float(np.abs(ad).max())},
           "path": {"median_abs_a": float(np.median(np.abs(ap))), "max_abs_a": float(np.abs(ap).max())}}
    for t in THRESHOLDS:
        # motif.py thresholds on SIGNED a ("correct sign"); steering_gain.py reports |a|.
        # Both are given so the numbers are directly comparable to either source table.
        out["direct"][f"frac_abs_a_ge_{t}"] = float((np.abs(ad) >= t).mean())
        out["path"][f"frac_abs_a_ge_{t}"] = float((np.abs(ap) >= t).mean())
        out["direct"][f"frac_signed_a_ge_{t}"] = float((ad >= t).mean())
        out["path"][f"frac_signed_a_ge_{t}"] = float((ap >= t).mean())
        # the only rate that can mean "drift proposed a compass": correct sign, magnitude,
        # AND the gradient term beating the pirouette term in the same individual.
        out["path"][f"frac_signed_a_ge_{t}_dominant"] = float(((ap >= t) & (np.abs(ap) > np.abs(cp))).mean())
    ctl = np.array([r[4] for r in rows])
    ctl = ctl[~np.isnan(ctl)]
    if len(ctl):
        out["agent_control"] = {"n": int(len(ctl)), "median_abs_a": float(np.median(np.abs(ctl))),
                                "max_abs_a": float(np.abs(ctl).max()),
                                **{f"frac_abs_a_ge_{t}": float((np.abs(ctl) >= t).mean()) for t in THRESHOLDS}}
    if len(ctl):
        for t in THRESHOLDS:
            out["agent_control"][f"frac_signed_a_ge_{t}"] = float((np.array([r[4] for r in rows if not np.isnan(r[4])]) >= t).mean())
    dep = np.array([r[5] for r in rows])           # (n, DEPTH) signed a at each depth
    out["per_depth_median_abs_a"] = [float(np.median(np.abs(dep[:, k]))) for k in range(DEPTH)]
    out["per_depth_max_abs_a"] = [float(np.abs(dep[:, k]).max()) for k in range(DEPTH)]
    clear = np.abs(ap) >= 16
    out["clearing_path_ge_16"] = int(clear.sum())
    if clear.any():
        share = np.abs(ind[clear]) / np.maximum(np.abs(ap[clear]), 1e-12)
        out["indirect_share_among_clearing"] = {
            "median": float(np.median(share)), "min": float(share.min()), "max": float(share.max()),
            "frac_majority_indirect": float((share > 0.5).mean()),
            "frac_over_80pct": float((share > 0.8).mean()),
            "direct_component_median_abs": float(np.median(np.abs(ad[clear]))),
            "gradient_dominant": int((np.abs(ap[clear]) > np.abs(cp[clear])).sum()),
        }
    return out


if __name__ == "__main__":
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--n", type=int, default=2000)
    ap_.add_argument("--k", type=int, default=19)
    ap_.add_argument("--add", type=float, default=0.15)
    ap_.add_argument("--rem", type=float, default=0.1)
    ap_.add_argument("--workers", type=int, default=4)
    args = ap_.parse_args()

    print("=== calibration (rule III round-trip; runs before anything is measured) ===")
    cfg0, pool0 = _load("W4b-801-bests")
    for line in calibrate(pool0[0], cfg0.sim.synthesis):
        print("  OK  " + line)

    results, t0 = [], time.time()
    for label in POOLS:
        cfg, pool = _load(label)
        print(f"\n=== {label}: {len(pool)} parents, {args.n} lineages x {args.k} mutations ===", flush=True)
        tasks = [(label, lo, min(lo + 50, args.n), args.k, args.add, args.rem) for lo in range(0, args.n, 50)]
        rows = []
        with Pool(args.workers) as p:
            for _, r in p.imap_unordered(run_chunk, tasks, chunksize=1):
                rows.extend(r)
        s = summarise(label, rows, args.k, args.n)
        results.append(s)
        print(f"  n with a two-nose pair: {s['n_with_two_noses']}/{args.n}")
        print(f"  {'route':8} {'median|a|':>10} {'max|a|':>10} " +
              " ".join(f"{'|a|>='+str(t):>10}" for t in THRESHOLDS) +
              " ".join(f"{'a>='+str(t):>10}" for t in THRESHOLDS))
        for route in ("direct", "path"):
            d = s[route]
            print(f"  {route:8} {d['median_abs_a']:10.4f} {d['max_abs_a']:10.3f} " +
                  " ".join(f"{100*d[f'frac_abs_a_ge_{t}']:9.2f}%" for t in THRESHOLDS) +
                  " ".join(f"{100*d[f'frac_signed_a_ge_{t}']:9.2f}%" for t in THRESHOLDS))
        if "indirect_share_among_clearing" in s:
            q = s["indirect_share_among_clearing"]
            print(f"  of the {s['clearing_path_ge_16']} lineages clearing path |a|>=16:")
            print(f"    indirect share of |a|: median {q['median']:.3f}  range [{q['min']:.3f}, {q['max']:.3f}]")
            print(f"    majority-indirect {100*q['frac_majority_indirect']:.1f}%   >80% indirect {100*q['frac_over_80pct']:.1f}%")
            print(f"    median |direct component| among them: {q['direct_component_median_abs']:.4f}")
            print(f"    gradient-dominant (|a|>|c|): {q['gradient_dominant']}/{s['clearing_path_ge_16']}")
        else:
            print(f"  no lineage cleared path |a|>=16")
        if "agent_control" in s:
            q = s["agent_control"]
            print(f"  CONTROL, same maths on the agent-smell pair (no food gradient):")
            print(f"    median|a| {q['median_abs_a']:.4f}  max|a| {q['max_abs_a']:.3f}  " +
                  "  ".join(f"|a|>={t}: {100*q[f'frac_abs_a_ge_{t}']:.2f}%" for t in THRESHOLDS))
        print(f"  gradient-dominant arrival (signed a>=t AND |a|>|c|): " +
              "  ".join(f"a>={t}: {100*s['path'][f'frac_signed_a_ge_{t}_dominant']:.2f}%" for t in THRESHOLDS))
        print(f"  |a| accumulating by depth: median " +
              " ".join(f"d{k+1}={v:.4f}" for k, v in enumerate(s["per_depth_median_abs_a"])) +
              "   max " + " ".join(f"d{k+1}={v:.2f}" for k, v in enumerate(s["per_depth_max_abs_a"])))
    json.dump({"master_seed": MASTER_SEED, "depth": DEPTH, "add": args.add, "rem": args.rem,
               "results": results, "seconds": round(time.time() - t0, 1)},
              open("runs/RBT-78/reconcile.json", "w"), indent=1)
    print(f"\nwrote runs/RBT-78/reconcile.json in {time.time()-t0:.0f}s")
