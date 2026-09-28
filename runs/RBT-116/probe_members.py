"""RBT-132: RBT-129's Stage P probe command (DESIGN §5.3(c)), one run, one season.

    probe_members.py RUN SEASON SEED RNG POINT OUT --battery BATTERY_JSON --config CONFIG [--workers W]

``stages.py probes`` emits one line per (point, seed, season) from a template; this is the command it names:
``--steer-cmd 'python runs/RBT-116/probe_members.py {run} {season} {seed} {rng} {point} {out} --battery
<point's planted>/battery.json --config {config_json}'`` (the battery comes from the point's planted command, which runs
first).  Per fauna:
- **the season** must be 0 (the founders) or the run's last completed season (from ``history.json``); any other is
  refused (the 07:10 ruling, S2).  A unit whose S went extinct before the merge (``EXTINCT.txt`` beside the run, as
  RBT-129's launcher writes it) is written **EXTINCT** for both faunas and not probed;
- **the members**: the S run's living members at ``SEASON``. Season 0 is the founders, read by name from the run's
  ``cohorts.jsonl`` (season 0) and ``<kind>/genomes/``; the final season is ``<kind>/final/``.  20 are drawn by
  ``default_rng(RNG)`` without replacement (all of them if fewer).  The same RNG serves both faunas, as RBT-129 §5.3(c)
  registers one RNG per seed ("129300 + j"); with equal pool sizes the two faunas get the same index set, which is
  deliberate and harmless (the pools are independent).  A fauna with fewer than 5 is written MISSING, not zero;
- **f**: each member's intact − decoy food on the first 8 stage-2 draws of the point's battery (§6.3's per-seed
  statistic is their mean).  Its seasons are cached and reused by the call, so f costs no extra season when the call
  reaches stage 2;
- **the call**: ``steer.call_genome`` on the full battery, at the point's own registered τ;
- **the power line** for the point's τ (``probe_power.txt``), printed beside the calls.
Writes ``OUT/probes.txt`` (one row per member) and ``OUT/probes.json``.  Nothing runs on import.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planters  # noqa: E402

steer = planters.steer
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig  # noqa: E402

N_PROBE, N_MIN, N_F = 20, 5, 8  #: RBT-129 §5.3(c): 20 per fauna; fewer than 5 is missing; f on 8 draws
KINDS = ("holistic", "conventional")


EXTINCT = "EXTINCT.txt"  #: RBT-129's marker of a unit whose S went fully extinct before the merge (stages.py, fix1)


def last_season(run: str) -> int:
    """The number of seasons the run completed (its ``history.json``): the final population is the population at it."""
    h = json.load(open(os.path.join(run, "history.json")))["history"]
    return max(int(e["season"]) for e in h) + 1 if h else 0


def check_season(run: str, season: int) -> None:
    """The ruled S2: season 0 (the founders) or the run's last completed season; anything else is refused."""
    if season != 0 and season != last_season(run):
        raise ValueError(f"season {season} is neither 0 nor {run}'s last completed season ({last_season(run)}): refused")


def extinct(run: str) -> bool:
    return any(os.path.exists(os.path.join(d, EXTINCT)) for d in (run, os.path.dirname(os.path.abspath(run))))


def members(run: str, season: int, kind: str) -> list:
    """The living members of ``kind`` at ``season``: the founders at 0 (by name, from cohorts.jsonl and genomes/), the
    final population otherwise.  Paths, sorted by name."""
    if season == 0:
        names = set()
        for line in open(os.path.join(run, "cohorts.jsonl")):
            row = json.loads(line)
            if row["season"] != 0:
                continue
            names.update(seat["name"] for grp in row["groups"] for seat in grp if seat["kind"] == kind)
        paths = [os.path.join(run, kind, "genomes", f"{n}.json") for n in sorted(names)]
        missing = [p for p in paths if not os.path.isfile(p)]
        if missing:
            raise FileNotFoundError(f"{len(missing)} founders' genomes are missing under {run}/{kind}/genomes (save_genomes off?)")
        return paths
    d = os.path.join(run, kind, "final")
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f[:-5].isdigit() and f.endswith(".json"))


def draw_members(paths: list, rng: int) -> list:
    """RBT-129 §5.3(c): 20 by default_rng(RNG), without replacement, in the drawn order; all of them if fewer."""
    if len(paths) <= N_PROBE:
        return list(paths)
    idx = np.random.default_rng(int(rng)).choice(len(paths), N_PROBE, replace=False)
    return [paths[i] for i in idx]


def _probe(args):
    gd, cfg_d, bat_d, point = args
    cfg, bat = SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d)
    season = cached(steer.point_season(point))
    f = [season(gd, cfg, d, "intact").food - season(gd, cfg, d, "decoy").food for d in bat.stage2[:N_F]]
    return float(np.mean(f)), steer.call_genome(gd, cfg, bat, season)


def cached(season):
    """A season function that runs each (draw, condition) once per member: f and the call share the stage-2 seasons."""
    memo = {}

    def run(genome, cfg, draw, cond):
        key = (draw.terrain_seed, draw.start_seed, cond)
        if key not in memo:
            try:
                memo[key] = season(genome, cfg, draw, cond)
            except steer.ThetaRefused as e:
                memo[key] = e
        if isinstance(memo[key], Exception):
            raise memo[key]
        return memo[key]
    return run


def probe(run: str, season: int, seed: int, rng: int, point: str, out: str, battery: str, config: str, workers: int = 1) -> int:
    path = os.path.join(config, "config.json") if os.path.isdir(config) else config
    raw = json.load(open(path))
    cfg = SimConfig.from_dict(raw.get("sim", raw))
    steer.assert_world_point(cfg, point)
    steer.assert_registered_channel(cfg, point)
    steer.assert_fair_config(raw, point)
    steer.assert_point_world(raw, point)
    bat = steer.Battery.from_dict(json.load(open(battery)))
    steer.assert_battery_size(bat, point)  # #471 M1(b): members at the same counts as the point's plants
    os.makedirs(out, exist_ok=True)
    rows, summary = [], {}
    if extinct(run):
        summary = {kind: {"status": "EXTINCT", "n": 0} for kind in KINDS}
        with open(os.path.join(out, "probes.json"), "w") as fh:
            json.dump({"run": run, "season": season, "seed": seed, "rng": rng, "point": point, "summary": summary, "members": []}, fh, indent=1)
        with open(os.path.join(out, "probes.txt"), "w") as fh:
            print(f"# RBT-129 probes at {point}, seed {seed}, season {season}: EXTINCT pre-merge ({EXTINCT}); not probed", file=fh)
        return 0
    check_season(run, season)
    for kind in KINDS:
        alive = members(run, season, kind)
        if len(alive) < N_MIN:  # RBT-129 §5.3(c): a fauna-seed with fewer than 5 living members is missing, not zero
            summary[kind] = {"status": "MISSING", "n": len(alive)}
            continue
        chosen = draw_members(alive, rng)
        args = [(Genotype.load(p).to_dict(), cfg.to_dict(), bat.to_dict(), point) for p in chosen]
        if workers > 1:
            with ProcessPoolExecutor(workers) as ex:
                res = list(ex.map(_probe, args, chunksize=1))
        else:
            res = [_probe(x) for x in args]
        for p, (f, rec) in zip(chosen, res):
            rows.append({"kind": kind, "member": os.path.relpath(p, run), "f": f, **steer._strip(rec)})
        calls = [rec["call"] for _, rec in res]
        summary[kind] = {"status": "PROBED", "n": len(chosen), "f_mean": float(np.mean([f for f, _ in res])),
                         "steers": calls.count(steer.STEERS), "smell_use": calls.count(steer.SMELL_USE),
                         "theta_refusal_rate": float(np.mean([rec.get("theta_refusal_rate", 0.0) for _, rec in res]))}
    with open(os.path.join(out, "probes.json"), "w") as fh:
        json.dump({"run": run, "season": season, "seed": seed, "rng": rng, "point": point, "summary": summary, "members": rows}, fh, indent=1)
    with open(os.path.join(out, "probes.txt"), "w") as fh:
        print(f"# RBT-129 probes at {point}, seed {seed}, season {season} (rng {rng}); tau {cfg.food.smell_tau} "
              f"(registered {steer.registered_tau(point)}), G {cfg.food.smell_contrast}; battery {battery}", file=fh)
        print(planters.power_line(point), file=fh)
        for r in rows:
            print(f"{r['kind']:12s} f {r['f']:+.3f} | " + steer.format_call(r["member"], r), file=fh)
        for kind, s in summary.items():
            print(f"# {kind}: " + json.dumps(s), file=fh)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run")
    ap.add_argument("season", type=int)
    ap.add_argument("seed", type=int)
    ap.add_argument("rng", type=int)
    ap.add_argument("point")
    ap.add_argument("out")
    ap.add_argument("--battery", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    return probe(a.run, a.season, a.seed, a.rng, a.point, a.out, a.battery, a.config, a.workers)


if __name__ == "__main__":
    sys.exit(main())
