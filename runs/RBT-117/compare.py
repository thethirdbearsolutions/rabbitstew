"""RBT-117: does the holistic fauna respond more strongly to imposed selection than the designed body?  A registered,
additive comparison on RBT-113's default-operator seed directories (PREREGISTRATION.md), fixed before any RBT-113 arm
was read.  It changes nothing in RBT-113: it imports RBT-113's readout.py and applies RBT-113's own per-seed-directory
statistics and controls, then compares the two faunas seed by seed.

    compare.py [--post-hoc] SEED_DIR [SEED_DIR ...]  > runs/RBT-117/compare.txt

SEED_DIRs are RBT-113's default-operator seed directories, `runs/RBT-113/O[1-4]/[0-9]*` (12 seeds).  A Z directory is
refused: RBT-112's operator reaches only the designed body, so a Z directory is not a matched pair of faunas.
`--post-hoc` labels every verdict EXPLORATORY: the registration's automatic fallback if RBT-117 is not merged before
RBT-113's readout is run (the coordinator's ruling, RBT-117, about 16:55 UTC).

Per seed s and fauna f (holistic, conventional = the designed body), from RBT-113's readout.line_series:
  D_f(s) = m_U(G-1) - m_D(G-1)            the final-generation up-minus-down divergence, RAW net yield (items eaten
                                          minus 0.03 per kJ; both faunas are scored in this one currency by one
                                          SimConfig, evolution.py `evaluate`, simulation.py `food_score`)
  PRIMARY  d(s) = D_holistic(s) - D_conventional(s)
  CONTROL  c(s) = C_holistic(s) - C_conventional(s),  C_f(s) = m_C(G-1) - m_C(0), the unselected lines' drift
  SECONDARY (printed, not scored): d in sigma0 units (each fauna's D over its own sigma0, RBT-113's pooled median
  generation-0 SD over these directories), and the differences in RBT-113's b_div and realised h2.
Test: exact two-sided sign-flip permutation over the paired seeds (readout.sign_flip_p: 2^12 = 4096 patterns at 12).
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_spec = importlib.util.spec_from_file_location("rbt113_readout", os.path.join(ROOT, "runs", "RBT-113", "readout.py"))
ro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ro)

ALPHA = 0.05
#: the control VOIDs the verdict only if the unselected lines' fauna difference is significant AND at least this
#: fraction of the primary difference's size (PREREGISTRATION.md §5: a fauna-specific mutational bias is expected and
#: cancels in U - D, so a small significant C difference is reported, not fatal)
CONTROL_FRACTION = 0.5
VERDICTS = ("HOLISTIC RESPONDS MORE", "DESIGNED RESPONDS MORE", "NOT DECIDED")
SCOPE_1 = ("This compares the two populations as built: body, controller topology and mutation operator all differ "
           "between them. It does not test the variability mechanism in isolation.")
SCOPE_2 = (f"RBT-113's D2 disclaimers apply: \"{ro.DISCLAIMER_1}\"; \"{ro.DISCLAIMER_2}\".")
SCOPE_3 = ("The primary quantity is in raw net-yield units, the currency both faunas are scored in: a larger raw "
           "response can come from more phenotypic variation, more heritability or both; the sigma0-unit line "
           "beside it is the per-unit-of-variation reading and is not scored.")


def per_seed(sd):
    """RBT-113's per-seed-directory statistics for both faunas, plus RBT-117's quantities.  -> (seed, stats, failures)"""
    name, op, seed = ro.parse_seed_dir(sd)
    if op:
        raise SystemExit(f"{sd}: a Z seed directory; RBT-117 compares the default-operator directories only")
    cfgs, runs = {}, {}
    for L in ro.LINES:
        cfgs[L], runs[L] = ro.read_run(os.path.join(sd, L))
    G = cfgs["U"]["generations"]
    wl = {L: ro.worlds(os.path.join(sd, L)) for L in ro.LINES}
    bad = [f"[{sc or 'both faunae'}] {m}" for sc, m in ro.controls(sd, cfgs, runs, G, wl)]
    st = {}
    for f in ro.FAUNAE:
        ser, S = {}, {}
        for L in ro.LINES:
            m, s_, sd0, _ = ro.line_series(runs[L][f])
            ser[L], S[L] = (m, s_), s_
        bad += [f"[{sc}] {m}" for sc, m in ro.selection_checks(f, S)]
        a = ro.arm_stats(ser)  # raw units
        st[f] = {"D": float(ser["U"][0][-1] - ser["D"][0][-1]), "Cdrift": float(ser["C"][0][-1] - ser["C"][0][0]),
                 "b_div": a["b_div"], "h2": a["h2"], "sd0": sd0}
    dec = None
    if os.path.exists(os.path.join(sd, "decompose.json")):
        dec = json.load(open(os.path.join(sd, "decompose.json")))
    return seed, st, bad, dec, G


def decide(d, c):
    """The registered verdict from the paired per-seed differences.  d: primary, c: control.  -> (verdict, detail)"""
    d, c = np.asarray(d, float), np.asarray(c, float)
    p, pc = ro.sign_flip_p(d), ro.sign_flip_p(c)
    if len(d) < 2:
        return "NOT DECIDED", {"p": p, "p_control": pc, "void": None}
    if pc < ALPHA and abs(float(c.mean())) >= CONTROL_FRACTION * abs(float(d.mean())):
        return "VOID", {"p": p, "p_control": pc,
                        "void": f"the unselected C lines differ between faunas (p = {pc:.4f}) by {c.mean():+.4f}, at least "
                                f"{CONTROL_FRACTION} x the primary difference {d.mean():+.4f}"}
    if p < ALPHA and d.mean() > 0:
        return VERDICTS[0], {"p": p, "p_control": pc, "void": None}
    if p < ALPHA and d.mean() < 0:
        return VERDICTS[1], {"p": p, "p_control": pc, "void": None}
    return VERDICTS[2], {"p": p, "p_control": pc, "void": None}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-hoc", action="store_true", help="the automatic fallback: every verdict is EXPLORATORY")
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    status = "EXPLORATORY (post hoc; enters no verdict)" if a.post_hoc else "CONFIRMATORY (registered before RBT-113's readout)"
    print(f"# RBT-117 comparison (runs/RBT-117/compare.py): {status}")
    rows, fails, decs = [], [], {}
    G = None
    for sd in a.seed_dirs:
        seed, st, bad, dec, G = per_seed(sd)
        rows.append((seed, st))
        decs[seed] = dec
        fails += [f"seed {seed}: {b}" for b in bad]
        print(f"seed {seed:3d} RBT-113 controls {'PASS' if not bad else 'FAIL'}" + "".join(f"\n    {b}" for b in bad))
    rows.sort()
    seeds = [s for s, _ in rows]
    sig0 = {f: float(np.median([st[f]["sd0"] for _, st in rows])) for f in ro.FAUNAE}
    d = [st["holistic"]["D"] - st["conventional"]["D"] for _, st in rows]
    c = [st["holistic"]["Cdrift"] - st["conventional"]["Cdrift"] for _, st in rows]
    ds = [st["holistic"]["D"] / sig0["holistic"] - st["conventional"]["D"] / sig0["conventional"] for _, st in rows]

    print(f"\n## per seed (raw net yield; generation {G - 1 if G else '?'}; sigma0 holistic {sig0['holistic']:.4f}, designed {sig0['conventional']:.4f})")
    print(f"  {'seed':>4s} {'D_hol':>9s} {'D_des':>9s} {'d (prim)':>9s} {'C_hol':>9s} {'C_des':>9s} {'c (ctrl)':>9s} {'d sigma0':>9s}")
    for (s, st), di, ci, dsi in zip(rows, d, c, ds):
        print(f"  {s:4d} {st['holistic']['D']:+9.4f} {st['conventional']['D']:+9.4f} {di:+9.4f} "
              f"{st['holistic']['Cdrift']:+9.4f} {st['conventional']['Cdrift']:+9.4f} {ci:+9.4f} {dsi:+9.3f}")

    verdict, det = decide(d, c)
    if fails:
        verdict, det["void"] = "VOID", "an RBT-113 control failed in a default-operator seed directory (above)"
    print(f"\n## primary: d = D_holistic - D_designed, raw net yield, {len(d)} paired seeds")
    print(f"  mean {ro.ci_text(d, '+.4f')}  exact sign-flip p = {det['p']:.4f}")
    print(f"## control: c = C-line drift, holistic - designed:  mean {ro.ci_text(c, '+.4f')}  p = {det['p_control']:.4f}")
    print("## secondary (printed, not scored)")
    print(f"  d in sigma0 units        {ro.ci_text(ds)}  p = {ro.sign_flip_p(ds):.4f}")
    for k in ("b_div", "h2"):
        v = [st["holistic"][k] / (sig0["holistic"] if k == "b_div" else 1) - st["conventional"][k] / (sig0["conventional"] if k == "b_div" else 1) for _, st in rows]
        print(f"  {k + (' (sigma0 units)' if k == 'b_div' else ''):24s} {ro.ci_text(v)}  p = {ro.sign_flip_p(v):.4f}")

    print("\n## food/work at the final generation (RBT-113's decompose.json; descriptive, not scored)")
    if all(decs[s] is not None for s in seeds) and seeds:
        for f in ro.FAUNAE:
            fu = ro.food_units({s: decs[s] for s in seeds}, f, [[s] for s in seeds])
            df = [x["U-D food"] for x in fu]
            dw = [x["U-D work"] for x in fu]
            print(f"  {f:12s} U - D: food {ro.ci_text(df)}  work {ro.ci_text(dw)}  food share {ro.food_share(df, dw):.0%}"
                  f" (food {'+' if np.mean(df) >= 0 else '-'}, work {'+' if np.mean(dw) >= 0 else '-'})")
    else:
        print(f"  NOT YET RUN: decompose.json missing for seeds {[s for s in seeds if decs[s] is None]} (RBT-113 RUNNER §6 step 2)")

    label = "" if not a.post_hoc else "EXPLORATORY, post hoc: "
    print(f"\n## VERDICT: {label}{verdict}" + (f"  ({det['void']})" if verdict == "VOID" else ""))
    print(f"  {SCOPE_1}\n  {SCOPE_2}\n  {SCOPE_3}")
    return 0 if verdict != "VOID" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
