"""RBT-132: why the K3 calibration's reachability screen failed at c0-p030-PW-G and c0-p030-HP-G (pre-data diagnosis).

    python runs/RBT-116/gate_diag.py [WORKERS] > runs/RBT-116/gate_diag.txt

**Part 1: the saved screen tables.** It re-reads the two failed runs' ``reachability.json``, from
``ckpt/rbt-129-calibration-<cell>`` (the coordinator cleared this: they are the controls' eat-≥ 1 table, a world
property).  For each cell it prints:
- the eat count histogram (of 16 controls per draw);
- a dispersion test of the counts against Binomial(16, p̂) (descriptive: a per-draw count sums over the controls, so it
  cannot separate host heterogeneity from draw heterogeneity);
- the admissible share under the registered rule (≥ half the controls) and under each lower threshold;
- the selection each rule puts on the controls' own intact seasons: P(a control ate | its draw is admissible) against
  P(a control ate). The screen's hosts are the (a) and (c) plants that K3 then calls on the same draws, and seasons are
  deterministic, so this is the lift in their intact eating that K3's plants carry and members do not.

Nothing else from those runs is read (their ``planted.txt`` host lines are not printed).

**Part 2: a screen-only experiment in W1's block** (RBT-116 §4.1: PW's layout, work 0.03, 15 s, τ 1 s), on fixture
draws (``Draw(7000 + i, 8000 + i)``, not a registered pool) and committed RBT-19 bodies (P-801, not RBT-113 O1's
hosts):
- the controls are ``planters.py``'s own plants on those bodies: G8(a) signed by the direction probes, and G8(c) tuned
  over its sign;
- it runs on random terrain (W1) and flat terrain (the RBT-129 cells' terrain), at 15, 30 and 45 s;
- per condition it prints each control's eat-≥ 1 rate, the admissible share under ≥ ½ and ≥ 1, the same dispersion
  test, and the same selection lift.

Only intact seasons run. No call, F, ΔT or K3 is computed.
"""
import io
import json
import math
import os
import subprocess
import sys
import tarfile
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import planters  # noqa: E402

steer = planters.steer
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig  # noqa: E402

CELLS = ("c0-p030-PW-G", "c0-p030-HP-G")
P801 = os.path.join(ROOT, "runs", "RBT-19", "P-801")
DESIGNED = [f"best_gen{g:04d}.json" for g in (500, 550, 580, 590, 450, 400)]
HOLISTIC = [f"best_gen{g:04d}.json" for g in (0, 330, 390, 450, 480, 510, 270, 150)]
DRAWS = [steer.Draw(7000 + i, 8000 + i) for i in range(48)]
TUNE = [steer.Draw(6000 + i, 6100 + i) for i in range(4)]
DURATIONS = {"random": (15.0, 30.0, 45.0), "flat": (15.0, 30.0)}


# --------------------------------------------------------------------------- #
# Part 1: the saved tables
# --------------------------------------------------------------------------- #


def saved_table(cell: str) -> list:
    ref = f"origin/ckpt/rbt-129-calibration-{cell}"
    blob = subprocess.run(["git", "show", f"{ref}:run.tar.gz.part000"], capture_output=True, cwd=ROOT, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        return json.load(tf.extractfile(f"{cell}/reachability.json"))


def binom_sf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def chi2_sf(x: float, df: int) -> float:
    """Upper tail of χ²(df), by the Wilson–Hilferty normal approximation (df ≥ 30 here)."""
    z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return 0.5 * math.erfc(z / math.sqrt(2))


def describe(ate: list, n: int, label: str) -> list:
    """Dispersion, admission and selection lift for per-draw eat counts of n controls."""
    ate = np.asarray(ate)
    D = len(ate)
    p = ate.mean() / n
    var, vb = ate.var(ddof=1), n * p * (1 - p)
    stat = (D - 1) * var / vb
    out = [f"{label}: {D} draws x {n} controls; P(a control eats >= 1) {p:.3f}; eat-count variance {var:.2f} against "
           f"binomial {vb:.2f} (ratio {var / vb:.2f}; over-dispersion p = {chi2_sf(stat, D - 1):.3f})"]
    half = -(-n // 2)
    for k, name in ((half, "registered: >= half"), (1, ">= 1 (MUST 1's intent: some control reaches food)")):
        adm = ate >= k
        lift = ate[adm].mean() / n if adm.any() else float("nan")
        out.append(f"  {name:52s} admits {adm.sum():3d} of {D} ({adm.mean():.0%}; binomial expects {binom_sf(k, n, p):.0%}); "
                   f"a control's P(ate | admissible) {lift:.3f} against {p:.3f} (lift x{lift / p if p else float('nan'):.2f})")
    return out


def part1() -> list:
    lines = ["## Part 1: the saved screen tables (ckpt/rbt-129-calibration-<cell>, reachability.json only)"]
    for cell in CELLS:
        t = saved_table(cell)
        ate = [r["ate"] for r in t]
        hist = {k: ate.count(k) for k in range(17) if ate.count(k)}
        lines.append(f"### {cell}: eat-count histogram (controls of 16 eating >= 1): {hist}")
        lines += describe(ate, t[0]["hosts"], cell)
    return lines


# --------------------------------------------------------------------------- #
# Part 2: a screen-only experiment in W1's block, on fixture draws and RBT-19 bodies
# --------------------------------------------------------------------------- #


def w1_world(terrain: str, duration: float) -> SimConfig:
    """RBT-116 §4.1's W1 block: RBT-129's PW sim block (PW's layout, work 0.03, the fairness rows) with τ 1 s, on
    ``terrain`` (W1: random; the RBT-129 cells: flat), at ``duration``."""
    raw = json.load(open(os.path.join(ROOT, "runs", "RBT-129", "worlds", "c0-p030-PW-G.config.json")))["sim"]
    cfg = SimConfig.from_dict(raw)
    return replace(cfg, duration=duration, food=replace(cfg.food, smell_tau=1.0), world=replace(cfg.world, terrain=terrain))


def controls() -> list:
    base = w1_world("flat", 15.0)
    season = steer.run_season
    out = []
    for f in DESIGNED:
        g = Genotype.load(os.path.join(P801, "conventional", f))
        if not planters.is_designed(g):
            continue
        try:
            planters.routed.unit_indices(g)
        except (AssertionError, StopIteration):
            continue
        sign = planters.compass_sign(g, base)
        if sign is not None:
            out.append(("a", f, planters.plant_a(g, sign)))
    for f in HOLISTIC:
        g = Genotype.load(os.path.join(P801, "holistic", f))
        geom = planters.body_geometry(g, base, TUNE[0])
        lay = planters.c_layout(g, geom) if geom is not None else None
        if lay is None:
            continue
        best, _, _ = planters.tune([planters.plant_c(g, lay, s) for s in (+1.0, -1.0)], base, TUNE, season)
        out.append(("c", f, best))
    return out


def _ate(task):
    gd, terrain, duration, d = task
    return steer.run_season(gd, w1_world(terrain, duration), d, "intact").food >= 1


def part2(workers: int) -> list:
    ctl = controls()
    lines = ["## Part 2: screen-only, W1's block, fixture draws, RBT-19 P-801 bodies as planters.py plants them",
             f"controls: {len(ctl)} ({sum(k == 'a' for k, _, _ in ctl)} G8(a), {sum(k == 'c' for k, _, _ in ctl)} G8(c)): "
             + ", ".join(f"{k}:{f}" for k, f, _ in ctl)]
    conds = [(t, d) for t, ds in DURATIONS.items() for d in ds]
    tasks = [(g.to_dict(), t, d, dr) for t, d in conds for _, _, g in ctl for dr in DRAWS]
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_ate, tasks, chunksize=8))
    k = 0
    for t, d in conds:
        M = np.array(res[k:k + len(ctl) * len(DRAWS)]).reshape(len(ctl), len(DRAWS))
        k += len(ctl) * len(DRAWS)
        lines.append(f"### terrain {t}, {d:g} s: per-control P(eat >= 1) " + " ".join(f"{x:.2f}" for x in M.mean(axis=1)))
        lines += describe(M.sum(axis=0), len(ctl), f"{t} {d:g} s")
    return lines


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    print("# gate_diag.py: RBT-132 calibration gate diagnosis (pre-data; see the docstring for what is and is not read)")
    for ln in part1() + part2(workers):
        print(ln)


if __name__ == "__main__":
    main()
