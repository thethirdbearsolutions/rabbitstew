"""RBT-102: structural carriage of the routed motif in one RBT-90 part-2 arm (pre-registered in
runs/RBT-102/PREREG.md; nothing here is tuned after an arm was read).

    python runs/RBT-102/analyse.py ARM_DIR [--procs 4] [--no-probe]  > ARM_DIR/rbt102.txt

ARM_DIR is a FINISHED arm restored from ckpt/rbt-90-<seed> (state.json at 600/600). The
conventional (Pioneer) fauna only: RBT-91's predicate needs wheel noses and drive Effectors, which
the holistic fauna's evolved bodies do not have.

Every genome the arm saved at birth is synthesised once and put to RBT-91's predicate, imported
unmodified (`runs/RBT-91/structural_rate.py` via `resign_arrivals.py`). Carriage per season is read
over the living population named by `lineage.jsonl`. Carriers alive in the window are signed per
individual by direction of travel at RBT-80's reference probe (16 x 15 s), imported from
`resign_arrivals.heading`, with RBT-91's 15-degree undetermined band and RBT-91's re-signing rule
(the published motif is the compass for a BACKWARD driver; RBT-97).

The last line is a JSON summary for `aggregate.py`.
"""
import argparse
import glob
import importlib.util
import json
import os
import sys
import time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_argv, sys.argv = sys.argv, ["structural_rate.py"]
_s = importlib.util.spec_from_file_location("ra", os.path.join(ROOT, "runs", "RBT-91", "resign_arrivals.py"))
ra = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ra)
sys.argv = _argv
sr = ra.sr

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

KIND = "conventional"
# pre-registered: the second half of the 600-season run. The environment override exists for the
# smoke test on a throwaway run only, as in RBT-90 part2_analyse.py.
WINDOW = tuple(int(x) for x in os.environ.get("RBT102_WINDOW", "300,599").split(","))
PAYING = 6.8664              # RBT-91's first paying rung, realised small-signal response
DRIFT_K, DRIFT_N = 84, 200_000   # RBT-91 structural arrivals at weight_sigma 0.4 (decision doc)
MARGIN = ra.MARGIN           # 15 deg undetermined band, RBT-91's
PC_N, PC_SEED = 20, 102      # positive control: 20 window genomes, sampled with this seed
PC_INSTALLS = ((1.0, +1.0), (8.0, -1.0))
SIM = None


def _init(sim_dict):
    global SIM
    SIM = SimConfig.from_dict(sim_dict)


def read_genome(path):
    """(name, carrier?, n_units, whole-brain a, links-alone a) for one saved genome."""
    g = Genotype.load(path)
    name = os.path.splitext(os.path.basename(path))[0]
    ph = synthesize(g, SIM.synthesis)
    units = sr.motif_units(ph)
    if not units:
        return name, False, 0, None, None
    return name, True, len(units), float(sr.small_signal_a(ph)), float(sr.links_alone_a(ph, units[0]))


def probe(task):
    name, path = task

    class _C:
        sim = SIM
    h, R = ra.heading(Genotype.load(path), _C, seeds=ra.SEEDS, dur=ra.DUR)
    return name, h, R


def install_check(path):
    """Positive control on one arm genome: bare predicate, then the predicate on each install."""
    gm_spec = importlib.util.spec_from_file_location("gm", os.path.join(ROOT, "scripts", "genotype_motif.py"))
    gm = importlib.util.module_from_spec(gm_spec)
    gm_spec.loader.exec_module(gm)
    g = Genotype.load(path)
    bare = bool(sr.motif_units(synthesize(g, SIM.synthesis)))
    out = []
    for w, sign in PC_INSTALLS:
        try:
            out.append(bool(sr.motif_units(synthesize(gm.install(g, w, sign=sign), SIM.synthesis))))
        except (RuntimeError, IndexError) as e:
            out.append(f"install invalid: {type(e).__name__}")
    return bare, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arm")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--no-probe", action="store_true", help="smoke tests only")
    a = ap.parse_args()
    t0 = time.time()
    arm = a.arm.rstrip("/")
    cfg = json.load(open(os.path.join(arm, "config.json")))
    seasons_cfg = cfg["ecology"]["seasons"]
    state = json.load(open(os.path.join(arm, "state.json")))
    print(f"# RBT-102 structural carriage -- {arm}\n")
    print(f"seed {cfg['seed']}; state.json season {state['season']} of {seasons_cfg}; fauna: {KIND} "
          f"(fixed_body {cfg['fixed_body']!r}); window seasons {WINDOW[0]}-{WINDOW[1]}")
    if int(state["season"]) < seasons_cfg:
        print("REFUSED: the arm has not finished; a running arm is not read.")
        sys.exit(2)

    # --- the living population per season, and each individual's parents ---
    alive, parents = {}, {}
    for line in open(os.path.join(arm, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] != KIND or "death" in r:
            continue
        alive.setdefault(r["generation"], []).append(r["name"])
        parents.setdefault(r["name"], r["parents"])
    seasons = sorted(alive)

    # --- every genome saved at birth, through the predicate ---
    paths = sorted(glob.glob(os.path.join(arm, KIND, "genomes", "*.json")))
    by_name = {os.path.splitext(os.path.basename(p))[0]: p for p in paths}
    with get_context("fork").Pool(a.procs, initializer=_init, initargs=(cfg["sim"],)) as pool:
        rows = pool.map(read_genome, paths, chunksize=16)
    _init(cfg["sim"])
    info = {n: dict(carrier=c, units=k, a=wa, alone=la) for n, c, k, wa, la in rows}
    missing = sorted({n for s in seasons for n in alive[s]} - set(info))
    print(f"genomes saved at birth: {len(paths)}; living names without a genome: {len(missing)}")

    # --- positive control FIRST: install RBT-87's routed motif into window genomes ---
    window_names = sorted({n for s in seasons if WINDOW[0] <= s <= WINDOW[1] for n in alive[s]} & set(info))
    rng = np.random.default_rng(PC_SEED)
    pick = sorted(rng.choice(window_names, size=min(PC_N, len(window_names)), replace=False))
    with get_context("fork").Pool(a.procs, initializer=_init, initargs=(cfg["sim"],)) as pool:
        pcs = pool.map(install_check, [by_name[n] for n in pick])
    det = sum(1 for _, o in pcs for x in o if x is True)
    inv = sum(1 for _, o in pcs for x in o if isinstance(x, str))
    tot = sum(len(o) for _, o in pcs)
    bare = sum(1 for b, _ in pcs if b)
    pc_pass = det == tot
    print(f"\n## Positive control (before any number)\n")
    print(f"  {len(pick)} window genomes (seed {PC_SEED}); installs {PC_INSTALLS} (w, sign)")
    print(f"  installed motif detected {det} of {tot}; install invalid {inv}; bare genomes carrying {bare} of {len(pick)}")
    print(f"  positive control: {'PASSED' if pc_pass else 'FAILED -- zero readings in this arm are not meaningful'}")

    # --- depth along the mutated line (parents[0]); founders are depth 0 ---
    depth = {}

    def d_of(n):
        stack = []
        while n not in depth:
            p = parents.get(n)
            if not p:
                depth[n] = 0
                break
            stack.append(n)
            n = p[0]
        v = depth[n]
        for m in reversed(stack):
            v += 1
            depth[m] = v
        return depth[stack[0]] if stack else depth[n]
    for n in parents:
        d_of(n)

    # --- carriage per season ---
    print("\n## Carriage per season (living conventional fauna)\n")
    print("| season | alive | carriers | fraction | mean depth |")
    print("|---|---|---|---|---|")
    C = {}
    for s in seasons:
        live = [n for n in alive[s] if n in info]
        k = sum(1 for n in live if info[n]["carrier"])
        C[s] = k / len(live) if live else float("nan")
        print(f"| {s} | {len(live)} | {k} | {C[s]:.4f} | {np.mean([depth.get(n, 0) for n in live]):.1f} |")
    wins = [s for s in seasons if WINDOW[0] <= s <= WINDOW[1]]
    X = float(np.mean([C[s] for s in wins]))
    win_depth = float(np.mean([depth.get(n, 0) for s in wins for n in alive[s]]))
    ever = sum(1 for s in seasons if C[s] > 0)

    # --- births: de novo against inherited, and at matched depth ---
    born = [n for n in info if parents.get(n)]          # founders are not births
    carriers_born = [n for n in born if info[n]["carrier"]]
    de_novo = [n for n in carriers_born if not any(info.get(p, {}).get("carrier") for p in parents[n])]
    m_depth = [n for n in born if 17 <= depth.get(n, -1) <= 21]
    m_carr = sum(1 for n in m_depth if info[n]["carrier"])
    founders = [n for n in info if n in parents and not parents[n]]
    f_carr = sum(1 for n in founders if info[n]["carrier"])
    dl, dh = sr.wilson(DRIFT_K, DRIFT_N)
    print(f"\n## Births\n")
    print(f"  founders {len(founders)}, carrying {f_carr}")
    print(f"  births {len(born)}; carriers born {len(carriers_born)}; DE NOVO arrivals (no parent carries) {len(de_novo)}"
          f"; inherited {len(carriers_born) - len(de_novo)}")
    ml, mh = sr.wilson(m_carr, len(m_depth))
    print(f"  births at depth 17-21 (RBT-91's k = 19 +- 2): {m_carr} of {len(m_depth)}"
          + (f" = {100 * m_carr / len(m_depth):.3f}% [{100 * ml:.3f}, {100 * mh:.3f}]" if m_depth else ""))
    print(f"  RBT-91 drift proposal rate: {DRIFT_K} of {DRIFT_N} = {100 * DRIFT_K / DRIFT_N:.3f}% "
          f"[{100 * dl:.4f}, {100 * dh:.4f}] (Wilson 95%)")

    # --- the window statistic ---
    print(f"\n## Window statistic\n")
    print(f"  X = mean carriage over seasons {WINDOW[0]}-{WINDOW[1]} = {100 * X:.4f}%  "
          f"(mean depth of the living in the window {win_depth:.1f}); seasons with any carrier {ever} of {len(seasons)}")

    # --- signing: every distinct carrier alive in the window, at the reference probe ---
    w_carr = sorted(n for n in window_names if info[n]["carrier"])
    comp = anti = und = 0
    agree = 0
    reach = 0
    print(f"\n## Carriers alive in the window, signed at the reference probe ({ra.SEEDS} x {ra.DUR:g} s)\n")
    if w_carr and not a.no_probe:
        with get_context("fork").Pool(a.procs, initializer=_init, initargs=(cfg["sim"],)) as pool:
            heads = pool.map(probe, [(n, by_name[n]) for n in w_carr])
        print("| carrier | depth | seasons alive in window | whole-brain a | links-alone a | heading | R | re-signed a | verdict | links-alone sign agrees |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for n, h, R in heads:
            wa, la = info[n]["a"], info[n]["alone"]
            nwin = sum(1 for s in wins if n in alive[s])
            reach += abs(la) >= PAYING if np.isfinite(la) else 0
            if h is None or abs(abs(h) - 90.0) < MARGIN:
                und += 1
                print(f"| {n} | {depth.get(n)} | {nwin} | {wa:+.4f} | {la:+.4f} | "
                      f"{'—' if h is None else f'{h:+.1f}'} | {R:.2f} | — | UNDETERMINED | — |")
                continue
            back = abs(h) > 90
            signed = wa if back else -wa
            s_alone = la if back else -la
            v = signed > 0
            comp += v
            anti += not v
            ag = (s_alone > 0) == v
            agree += ag
            print(f"| {n} | {depth.get(n)} | {nwin} | {wa:+.4f} | {la:+.4f} | {h:+.1f} | {R:.2f} | "
                  f"{signed:+.4f} | {'COMPASS' if v else 'ANTI-COMPASS'} | {'yes' if ag else 'no'} |")
    elif a.no_probe:
        print("  (probe skipped: smoke test)")
    else:
        print("  no carrier is alive in the window.")
    print(f"\n  compasses {comp}, ANTI-COMPASSES (the inversion count) {anti}, undetermined {und} "
          f"of {len(w_carr)} distinct window carriers; links-alone |a| >= paying rung: {reach}")
    print(f"\nwall time {time.time() - t0:.0f} s")
    summary = dict(seed=cfg["seed"], pc_pass=pc_pass, pc_detected=det, pc_total=tot, pc_invalid=inv,
                   X=X, window_depth=win_depth, seasons_any=ever, n_seasons=len(seasons),
                   genomes=len(paths), missing=len(missing), founders=len(founders), founder_carriers=f_carr,
                   births=len(born), carriers_born=len(carriers_born), de_novo=len(de_novo),
                   depth_matched=len(m_depth), depth_matched_carriers=m_carr,
                   window_carriers=len(w_carr), compass=comp, anti=anti, undetermined=und,
                   alone_agrees=agree, alone_reaches_rung=reach, probed=not a.no_probe)
    print("SUMMARY " + json.dumps(summary))


if __name__ == "__main__":
    main()
