"""RBT-125 world gate, part B: a nose step against a +25% speed step, on real RBT-113 hosts (REGISTRATION.md §B).

Hosts: RBT-113's designed-body (Pioneer) U-line finals, arm O1, seeds 1-3, K = 5 per seed drawn by a fixed rng
(default_rng(125)) from the 40 finals of each: 15 hosts, restored from ckpt/rbt-113-O1 into HOSTS_ROOT (bulk, never
committed).  World: runs/RBT-125/gate/worlds/<cell> (RBT-90 part 2's world, which is RBT-113's, with the cell's food
block).  Every host carries RBT-97's routed motif at output weight w (linear gain a = 2w), signed per host by the
RBT-103 harness's two direction probes, which must agree (else the host is UNDETERMINED and leaves every arm).

Arms, per host, on the same 128 paired start seeds (125000..125127), each a 15 s solo season (amended per the
coordinator's ruling of 22:28, M4):
  w0     the host as it is
  w0.4   the first weak nose           (a 0 -> 0.8: each of the motif's two output links one weight sigma, 0.4)
  w1, w1.4    one step at a = 2 -> 2.8
  w3, w3.4    one step at a = 6 -> 6.8  (the gate's rung)
  speed@w    for w in {0, 1, 3}: arm w with world.joint_damping / 1.25.  The Pioneer's wheels are torque motors whose
         free-spin speed is gear / damping, so this raises the top wheel speed by 25% at the same torque (it also lowers
         the casters' passive damping by the same factor).  The REALISED speed is measured: per host and base w,
         r = mean centre-of-mass path speed of speed@w / that of w, over the 128 seeds.
The speed step "per unit of realised speed" is, per host and base w, (items of speed@w - items of w) x 0.25 / (r - 1),
the step rescaled to a realised +25%; a host with r < 1.10 (a speed arm that did not speed it up by 10%) leaves the
per-unit comparison at that w and is counted.  Per host: mean items (and net: items - 0.03 x kJ) per season in each
arm; the steps are paired differences.  Across hosts: mean and Student t(n - 1) 95% interval; the equivalence test
is two one-sided t tests at 5% (the 90% interval of nose - speed inside +-DELTA, DELTA = 0.10 items per season).

    steps.py HOSTS_ROOT CELL [--procs 4]    -> stdout       (the registered §B run: exactly as registered)

Reuse for other worlds and hosts (the RBT-129 sweep's Stage 0), without changing the registered defaults:
    steps.py HOSTS_ROOT LABEL --config PATH [--hosts-file FILE] [--seeds N] [--seed0 S]
  --config      a config.json (or a directory holding one) whose "sim" block is the world, instead of worlds/<CELL>;
                its top-level "fairness" must be "fair" (RBT-128's --fair), or the run is refused (S12)
  --hosts-file  one Pioneer-shaped genotype path per line (relative paths resolve against HOSTS_ROOT), instead of the
                registered RBT-113 O1 draw; every host must carry the routed motif (a food nose and an effector on each
                drive wheel), as routed.unit_indices checks, and be a designed body, as rabbitstew.fair.is_designed
                checks (S13; refused if rabbitstew.fair is absent)
  --seeds/--seed0  the paired start seeds (defaults: 128 from 125000, the registered ones)
"""
import argparse
import json
import math
import os
import sys
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prize_gate  # noqa: E402  (the harness module, with the decoy patch; only its direction probe is used here)

rp = prize_gate.rp
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

SEEDS = [125000 + i for i in range(128)]
SPEED_WS = (0.0, 1.0, 3.0)
R_MIN = 1.10  #: a speed arm must realise at least +10% to enter the per-unit comparison
DELTA = 0.10  #: the equivalence margin, items per season (auditor B's ~0.1 selection threshold)
WS = (0.0, 0.4, 1.0, 1.4, 3.0, 3.4)
SPEED = 1.25
K = 5
HOST = {}


def hosts(root):
    rng = np.random.default_rng(125)
    out = []
    for seed in (1, 2, 3):
        d = os.path.join(root, "O1", str(seed), "U", "conventional", "final")
        fs = sorted(os.listdir(d))
        for i in sorted(rng.choice(len(fs), K, replace=False)):
            out.append(os.path.join(d, fs[i]))
    return out


def _is_designed(g):
    """rabbitstew.fair.is_designed (RBT-128, #432).  Guarded: without it --hosts-file cannot check its hosts, so it refuses."""
    try:
        from rabbitstew.fair import is_designed
    except ImportError:
        raise SystemExit("refusing: --hosts-file needs rabbitstew.fair.is_designed (RBT-128, #432), which this tree lacks")
    return is_designed(g)


def bout(task):
    h, w, sign, seed, speed = task
    cfg = rp.RUN["cell"]
    if speed:
        cfg = replace(cfg, world=replace(cfg.world, joint_damping=cfg.world.joint_damping / SPEED))
    g = Genotype.load(HOST[h])
    if w:
        g = rp.routed.install(g, w, sign=sign)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    path, last = 0.0, sim.center_of_mass(0)[:2].copy()
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        now = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(now - last))
        last = now.copy()
    h_ = sim.harvest(0)
    return (h, w, speed), seed, h_["food"], sim.food_score(0), path / cfg.duration


def _betainc(a, b, x):
    """The regularized incomplete beta I_x(a, b), by its continued fraction (Numerical Recipes' betacf)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _betainc(b, a, 1.0 - x)
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        for num in (m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m)), -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))):
            d = 1.0 + num * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + num / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            break
    return front * h / a


def t_ppf(q, df):
    """Student t quantile, scipy-free (RBT-125 #437: the readouts run in a plain `.[dev]` venv): bisection on the CDF
    1 - I_{df/(df+t^2)}(df/2, 1/2) / 2, to 1e-13.  Matches scipy.stats.t.ppf to < 1e-9 for df 1..500 (tested)."""
    if q == 0.5:
        return 0.0
    if q < 0.5:
        return -t_ppf(1.0 - q, df)
    cdf = lambda t: 1.0 - 0.5 * _betainc(df / 2.0, 0.5, df / (df + t * t))
    lo, hi = 0.0, 1.0
    while cdf(hi) < q:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if cdf(mid) < q:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    return 0.5 * (lo + hi)


def t_int(x, level=0.95):
    x = np.asarray(x, float)
    if len(x) < 2:
        return float(x.mean()) if len(x) else float("nan"), float("nan"), float("nan")
    hw = t_ppf(0.5 + level / 2, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - hw, x.mean() + hw


def reading(d):
    """The registered reading of nose - speed over hosts (REGISTRATION.md §B, amended)."""
    m, lo, hi = t_int(d)
    _, lo90, hi90 = t_int(d, 0.90)
    if lo > 0:
        return "NOSE LEADS"
    if hi < 0:
        return "SPEED LEADS"
    if -DELTA < lo90 and hi90 < DELTA:
        return "COMPARABLE (equivalent within +-0.10)"
    return "TIED, UNRESOLVED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hosts_root")
    ap.add_argument("cell")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--config", default=None, help="a config.json, or a directory holding one, instead of worlds/<CELL>")
    ap.add_argument("--hosts-file", default=None, help="genotype paths, one per line, instead of the registered host draw")
    ap.add_argument("--seeds", type=int, default=len(SEEDS))
    ap.add_argument("--seed0", type=int, default=SEEDS[0])
    a = ap.parse_args()
    SEEDS[:] = [a.seed0 + i for i in range(a.seeds)]
    cfg_path = os.path.join(HERE, "worlds", a.cell, "config.json") if a.config is None else (
        os.path.join(a.config, "config.json") if os.path.isdir(a.config) else a.config)
    raw = json.load(open(cfg_path))
    if a.config is not None:  # S12 (RBT-129 launch adversary): a PAYS bout runs only on a config the fairness set built
        print(f"# fairness: {raw.get('fairness')!r}")
        if raw.get("fairness") != "fair":
            raise SystemExit(f"refusing: {cfg_path} has fairness {raw.get('fairness')!r}, not 'fair' (RBT-128's --fair)")
    cfg = SimConfig.from_dict(raw["sim"])
    rp.RUN["cell"] = cfg
    if a.hosts_file:
        paths = [ln.strip() for ln in open(a.hosts_file) if ln.strip() and not ln.startswith("#")]
        paths = [p if os.path.isabs(p) else os.path.join(a.hosts_root, p) for p in paths]
        for p in paths:
            g = Genotype.load(p)
            rp.routed.unit_indices(g)  # refuses a host that cannot carry the motif
            if not _is_designed(g):  # S13: and a Pioneer brain on a reshaped body
                raise SystemExit(f"refusing: {p} is not a designed body (rabbitstew.fair.is_designed)")
    else:
        paths = hosts(a.hosts_root)
    HOST.update({i: p for i, p in enumerate(paths)})
    rp.genotype = lambda run, kind, gen: Genotype.load(HOST[gen])  # the harness's direction probe, on these hosts
    print(f"# RBT-125 gate B: nose step against +25% speed step, cell {a.cell}: {json.dumps(json.load(open(cfg_path))['sim']['food'])}")
    if a.config is not None:
        print(f"# world from {cfg_path}; {len(SEEDS)} paired seeds from {SEEDS[0]}")
    print(f"# hosts: {len(paths)} {'from ' + a.hosts_file if a.hosts_file else 'RBT-113 O1 U designed finals'} ({', '.join(os.path.relpath(p, a.hosts_root) for p in paths)})")
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(rp.direction_bout, [("cell", "conventional", h, i, k) for k in rp.g500.PROBES for h in HOST for i in range(16)], chunksize=4)
    by = {}
    for r in rows:
        by.setdefault((r[1], r[0]), []).append(r[2:])
    sign = {}
    for h in HOST:
        backs = []
        for k in rp.g500.PROBES:
            sn, cs, n = (sum(x[j] for x in by[(k, h)]) for j in range(3))
            backs.append(abs(np.degrees(np.arctan2(sn / n, cs / n))) > 90 if n else None)
        if backs[0] is not None and backs[0] == backs[1]:
            sign[h] = +1.0 if backs[0] == rp.mech.rs.PUBLISHED_IS_BACKWARD else -1.0
    und = [h for h in HOST if h not in sign]
    print(f"# direction: {len(sign)} signed, {len(und)} UNDETERMINED (out of every arm): {[os.path.relpath(HOST[h], a.hosts_root) for h in und]}")
    tasks = [(h, w, sign[h], s, False) for h in sign for w in WS for s in SEEDS] + [(h, w, sign[h], s, True) for h in sign for w in SPEED_WS for s in SEEDS]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=8)
    got = {(k, s): (f, net, v) for k, s, f, net, v in rows}
    arms = [(w, False) for w in WS] + [(w, True) for w in SPEED_WS]
    name = lambda w, sp: f"speed@w{w:g}" if sp else f"w{w:g}"
    print("\n| host | " + " | ".join(name(*arm) for arm in arms) + " | " + " | ".join(f"r@w{w:g}" for w in SPEED_WS) + " |")
    print("|---|" + "---|" * (len(arms) + len(SPEED_WS)))
    M = {}
    r = {}
    for h in sign:
        M[h] = {arm: np.array([[got[((h, arm[0], arm[1]), s)][j] for s in SEEDS] for j in range(3)]) for arm in arms}
        r[h] = {w: M[h][(w, True)][2].mean() / max(M[h][(w, False)][2].mean(), 1e-9) for w in SPEED_WS}
        print(f"| {os.path.relpath(HOST[h], a.hosts_root)} | " + " | ".join(f"{M[h][arm][0].mean():.3f}" for arm in arms)
              + " | " + " | ".join(f"{r[h][w]:.3f}" for w in SPEED_WS) + " |")
    steps = {"first nose (w 0 -> 0.4)": ((0.4, False), (0.0, False)), "nose step w 1 -> 1.4": ((1.4, False), (1.0, False)),
             "nose step w 3 -> 3.4": ((3.4, False), (3.0, False)), "installed a = 6 (w 3) - host": ((3.0, False), (0.0, False))}
    steps.update({f"speed step at w{w:g} (raw)": ((w, True), (w, False)) for w in SPEED_WS})
    print(f"\n## steps across {len(sign)} hosts, per-host means over {len(SEEDS)} paired seeds; mean [t 95%]")
    print("| step | items | net (items - work) |")
    print("|---|---|---|")
    per = {}
    for label, (hi, lo) in steps.items():
        per[label] = {h: (M[h][hi][0] - M[h][lo][0]).mean() for h in sign}
        net = [(M[h][hi][1] - M[h][lo][1]).mean() for h in sign]
        print(f"| {label} | {'{:+.3f} [{:+.3f}, {:+.3f}]'.format(*t_int(list(per[label].values())))} | {'{:+.3f} [{:+.3f}, {:+.3f}]'.format(*t_int(net))} |")
    print("\n## realised speed ratio r of each speed arm (registered step: 1.25)")
    unit = {}
    for w in SPEED_WS:
        rs = [r[h][w] for h in sign]
        ok = [h for h in sign if r[h][w] >= R_MIN]
        unit[w] = {h: per[f"speed step at w{w:g} (raw)"][h] * 0.25 / (r[h][w] - 1.0) for h in ok}
        print(f"  at w{w:g}: r {'{:.3f} [{:.3f}, {:.3f}]'.format(*t_int(rs))}, range {min(rs):.2f}..{max(rs):.2f}; "
              f"{len(ok)} of {len(sign)} hosts at r >= {R_MIN:.2f} enter the per-unit comparison; "
              f"per-unit speed step (+25% realised) {'{:+.3f} [{:+.3f}, {:+.3f}]'.format(*t_int(list(unit[w].values())))}")
    print("\n## nose step - speed step (items), paired per host, at the same base w -> reading (REGISTRATION.md §B)")
    print(f"   NOSE LEADS: 95% lower bound > 0; SPEED LEADS: 95% upper bound < 0; COMPARABLE: 90% interval inside +-{DELTA}; else TIED, UNRESOLVED")
    for label, w in (("first nose (w 0 -> 0.4)", 0.0), ("nose step w 1 -> 1.4", 1.0), ("nose step w 3 -> 3.4", 3.0)):
        raw = [per[label][h] - per[f"speed step at w{w:g} (raw)"][h] for h in sign]
        pu = [per[label][h] - unit[w][h] for h in unit[w]]
        print(f"STEP {a.cell} | {label:24s} | vs raw speed@w{w:g}: {'{:+.3f} [{:+.3f}, {:+.3f}]'.format(*t_int(raw))} {reading(raw)} "
              f"| vs per-unit speed (n {len(pu)}): {'{:+.3f} [{:+.3f}, {:+.3f}]'.format(*t_int(pu)) if len(pu) > 1 else '--'} {reading(pu) if len(pu) > 1 else 'NOT READABLE'}")


if __name__ == "__main__":
    main()
