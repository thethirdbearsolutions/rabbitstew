"""Command-line interface: ``rabbitstew <command> ...``."""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

from .evolution import Experiment, EvolutionConfig
from .fixed import drive_straight_genotype, pioneer_genotype
from .gallery import build_gallery
from .report import build_comparison, build_report
from .analysis import TrialConfig, analyze_run
from .genetics import MutationConfig
from .genotype import Genotype, random_genotype
from .simulation import FoodConfig, SimConfig, Simulation, run_bout
from .synthesis import SynthesisConfig, describe, synthesize
from .trajectory import Trajectory
from .visualizer import write_html


def _sim_config(args) -> SimConfig:
    cfg = SimConfig()
    if getattr(args, "duration", None) is not None:
        cfg.duration = args.duration
    if getattr(args, "size_ratio", None) is not None:
        cfg.synthesis.size_ratio_limit = args.size_ratio
    if getattr(args, "start_distance", None) is not None:
        cfg.start_distance = args.start_distance
    if getattr(args, "arena", None):
        cfg.world.arena_radius = args.arena
    if getattr(args, "mass_budget", None) is not None:
        cfg.synthesis.mass_budget = args.mass_budget
    if getattr(args, "terrain", None):
        cfg.world.terrain = args.terrain
    if getattr(args, "terrain_seed", None) is not None:
        cfg.world.terrain_seed = args.terrain_seed
    if getattr(args, "obstacles", None) is not None:
        cfg.world.random_obstacles = args.obstacles
    if getattr(args, "random_start", False):
        cfg.random_start = True
    if getattr(args, "score", None):
        cfg.score = args.score
    if getattr(args, "waypoints", None):
        cfg.waypoints = args.waypoints
    if getattr(args, "food_items", None):
        cfg.food = FoodConfig(items=args.food_items, radius=args.food_radius, value=args.food_value, eat_radius=args.eat_radius, decay=args.food_decay, work_cost=args.work_cost, regrow=not getattr(args, 'no_regrow', False),
                              patches=getattr(args, "food_patches", 0) or 0, patch_radius=getattr(args, "patch_radius", 0.6), regrow_delay=getattr(args, "regrow_delay", 0.0) or 0.0)
    return cfg


def _add_food_args(s) -> None:
    s.add_argument("--food-items", type=int, default=0, help="> 0 turns on the foraging world with this many food items")
    s.add_argument("--food-radius", type=float, default=3.0)
    s.add_argument("--food-value", type=float, default=1.0)
    s.add_argument("--eat-radius", type=float, default=0.35)
    s.add_argument("--food-decay", type=float, default=1.0, help="intensity length scale (m) of the food and agent smell sensors")
    s.add_argument("--work-cost", type=float, default=0.0, help="energy charged per kJ of actuator work")
    s.add_argument("--no-regrow", action="store_true", help="eaten food does not regrow within a season (the arena depletes)")
    s.add_argument("--food-patches", type=int, default=0, help="> 0 clusters the food into this many patches instead of spreading it uniformly over the disc")
    s.add_argument("--patch-radius", type=float, default=0.6, help="radius (m) of a food patch under --food-patches")
    s.add_argument("--regrow-delay", type=float, default=0.0, help="> 0 regrows an eaten item at its own spot after this many seconds of simulated time (the persistent world); under the foraging ecology it also carries arena food state across seasons")


def cmd_random(args) -> int:
    rng = np.random.default_rng(args.seed)
    g = random_genotype(rng, n_nodes=args.nodes, name=f"random-{args.seed}")
    g.save(args.out)
    print(f"wrote {args.out}: {len(g.nodes)} nodes, {g.count_links()} links")
    return 0


def cmd_fixed(args) -> int:
    rng = np.random.default_rng(args.seed)
    if args.body == "quadruped":
        from .fixed import quadruped_genotype

        g = quadruped_genotype(rng, hidden=args.hidden)
    else:
        g = drive_straight_genotype(args.power) if args.drive else pioneer_genotype(rng, hidden=args.hidden)
    g.save(args.out)
    print(f"wrote {args.out}: fixed {args.body} body ({'constant drive' if args.drive and args.body == 'pioneer' else 'random weights'})")
    return 0


def cmd_inspect(args) -> int:
    g = Genotype.load(args.genotype)
    problems = g.validate()
    if problems:
        print("INVALID genotype:")
        for p in problems:
            print("  " + p)
        return 1
    cfg = SynthesisConfig()
    if args.size_ratio is not None:
        cfg.size_ratio_limit = args.size_ratio
    ph = synthesize(g, cfg)
    print(f"{g.name or args.genotype}: {len(g.nodes)} nodes, root {g.root}, reachable {sorted(g.reachable_nodes())}")
    print(describe(ph))
    return 0


def cmd_simulate(args) -> int:
    cfg = _sim_config(args)
    genotypes = [Genotype.load(p) for p in args.genotypes]
    if len(genotypes) == 2 and not args.view:
        res = run_bout(genotypes[0], genotypes[1], cfg, record=bool(args.out or args.html))
        for i, g in enumerate(genotypes):
            print(f"robot {i} ({g.name or args.genotypes[i]}): distance {res.distances[i]:.3f} m, fitness {res.fitness[i]:.3f}" + (" EXPLODED" if res.exploded[i] else ""))
        print(f"winner: robot {res.winner}")
        traj = res.trajectory
    else:
        sim = Simulation(genotypes, cfg)
        if args.out or args.html:
            sim.start_recording()
        if args.view:
            from .visualizer import launch_live

            launch_live(sim)
        else:
            sim.run()
        for i, g in enumerate(genotypes):
            print(f"robot {i} ({g.name or args.genotypes[i]}): distance {sim.distance_from_center(i):.3f} m" + (" EXPLODED" if sim.exploded[i] else ""))
        traj = sim.trajectory
    if traj is not None:
        if args.out:
            traj.write(args.out)
            print(f"wrote trajectory {args.out} ({traj.n_frames} frames)")
        if args.html:
            write_html(traj, args.html, title=args.title or "Rabbitstew replay")
            print(f"wrote replay {args.html}")
    return 0


def cmd_visualize(args) -> int:
    traj = Trajectory.read(args.trajectory)
    write_html(traj, args.out, title=args.title or "Rabbitstew replay")
    print(f"wrote {args.out}: {len(traj.units)} units, {traj.n_frames} frames, {traj.duration:.2f} s")
    return 0


def cmd_evolve(args) -> int:
    if args.resume:
        ex = Experiment.resume(args.out, generations=args.generations if args.generations_given else None, workers=args.workers)
        summary = ex.run()
        if summary["champions"]:
            last = summary["champions"][-1]
            print(f"final champion bouts: holistic mean fitness {last['holistic_mean_fitness']:.3f} ({last['holistic_wins']}-{last['conventional_wins']} of {last['n_bouts']})")
        return 0
    cfg = EvolutionConfig(
        population_size=args.population,
        generations=args.generations,
        elites=args.elites,
        champion_interval=args.champion_interval,
        champions=args.champions,
        champion_mode=args.champion_mode,
        workers=args.workers,
        seed=args.seed,
        sim=_sim_config(args),
        mutation=MutationConfig(),
        brain_model=args.brain_model,
        conventional_topology=args.conventional_topology,
        opponents=args.opponents,
        draws=args.draws,
        locomotion_phase=args.locomotion_phase,
        fixed_body=args.fixed_body,
        hidden_neurons=args.hidden,
        mirror=args.mirror,
        neighbour_links=args.neighbour_links,
        archive=args.archive,
        holistic_seed=args.holistic_seed or "",
        heading_curriculum=args.heading_curriculum,
        survival=args.survival,
        selection=args.selection,
    )
    ex = Experiment(cfg, out_dir=args.out)
    summary = ex.run()
    if summary["champions"]:
        last = summary["champions"][-1]
        print(f"final champion bouts: holistic mean fitness {last['holistic_mean_fitness']:.3f} ({last['holistic_wins']}-{last['conventional_wins']} of {last['n_bouts']})")
    if args.out:
        print(f"results in {args.out}/history.json")
    return 0


def cmd_gallery(args) -> int:
    gens = [int(x) for x in args.gens.split(",") if x.strip()] if args.gens else None
    build_gallery(args.run_dir, args.out, every=args.every, record_every=args.record_every, title=args.title, gens=gens)
    return 0


def cmd_report(args) -> int:
    info = build_report(args.run_dirs, args.out, title=args.title)
    t = info["totals"]
    print(f"wrote {args.out}: {info['runs']} run(s), holistic {t['wins']}-{t['losses']} of {t['n']} champion bouts, by thirds {info['thirds']}")
    return 0


def cmd_compare(args) -> int:
    groups = {}
    for spec in args.groups:
        if "=" not in spec:
            raise SystemExit(f"expected NAME=dir1,dir2,... but got {spec!r}")
        name, dirs = spec.split("=", 1)
        groups[name] = [d for d in dirs.split(",") if d]
    info = build_comparison(groups, args.out, title=args.title, note=args.note)
    print(f"wrote {args.out}: {info['conditions']} conditions")
    return 0


def cmd_analyze(args) -> int:
    out_json = args.out or os.path.join(args.run_dir, "analysis.json")
    out_html = args.html or os.path.join(args.run_dir, "analysis.html")
    res = analyze_run(args.run_dir, out_json=out_json, out_html=out_html, every=args.every, workers=args.workers, lesions=args.lesions, trials=TrialConfig(), log=print)
    print(f"wrote {out_json} and {out_html}: {len(res['individuals'])} individuals")
    return 0


def cmd_synergy(args) -> int:
    from .analysis import synergy_for_run

    out = {}
    for kind in ("holistic", "conventional"):
        r = synergy_for_run(args.run_dir, kind)
        out[kind] = r
        print(f"{kind} {r['name']}: capability full {r['full']['capability']:+.2f}  bias-only {r['bias_only']['capability']:+.2f}  random-links {r['random_links']['capability']:+.2f}  body-perturbed {r['body_perturbed']['capability']:+.2f}"
              + (f"  transplants {[round(t['capability'], 2) for t in r['transplants']]}" if r["transplants"] else "  (no aligned donors)"))
        print(f"    brain dependence {r.get('brain_dependence')}  body dependence {r.get('body_dependence')}  transplant dependence {r.get('transplant_dependence')}")
    path = args.out or os.path.join(args.run_dir, "synergy.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path}")
    return 0


def cmd_heritability(args) -> int:
    from .analysis import founder_model, realised_heritability

    for run in args.run_dirs:
        with open(os.path.join(run, "config.json")) as f:
            cfg = json.load(f)
        # A run with a locomotion phase changes its score halfway through; pooling both phases inflates
        # the parent-offspring correlation with between-phase variance, so report each window separately.
        windows = [None]
        if args.window:
            windows = [tuple(args.window)]
        elif cfg.get("locomotion_phase", 0) > 0:
            lp = int(cfg["locomotion_phase"])
            windows = [(1, lp + 1), (lp + 1, 10**9)]
        for w in windows:
            h = realised_heritability(run, "holistic", window=w)
            c = realised_heritability(run, "conventional", window=w)
            label = f"{run}" if w is None else f"{run} gens {w[0]}-{'end' if w[1] >= 10**9 else w[1] - 1}"
            print(f"{label}: holistic {h['heritability']} (n={h['n']})  conventional {c['heritability']} (n={c['n']})")
    if args.founder_model:
        with open(os.path.join(args.run_dirs[0], "config.json")) as f:
            cfg = json.load(f)
        m = founder_model(N=cfg["population_size"], elites=cfg["elites"], tournament=cfg["tournament_size"], crossover=cfg["crossover_rate"], generations=cfg["generations"])
        print("founders expected under pure-noise fitness for this reproduction scheme:", m)
    return 0


def _cost(text: str):
    return "relative" if text == "relative" else float(text)


def cmd_ecology(args) -> int:
    from .ecology import Ecology, EcologyConfig

    evo = EvolutionConfig(
        population_size=args.capacity,
        generations=args.seasons,
        workers=args.workers,
        seed=args.seed,
        sim=_sim_config(args),
        mutation=MutationConfig(),
        brain_model=args.brain_model,
        conventional_topology=args.conventional_topology,
        fixed_body=args.fixed_body,
        hidden_neurons=args.hidden,
        mirror=args.mirror,
        neighbour_links=args.neighbour_links,
        holistic_seed=args.holistic_seed or "",
        heading_curriculum=args.heading_curriculum,
    )
    eco = EcologyConfig(
        seasons=args.seasons,
        capacity=args.capacity,
        group_size=args.group_size,
        living_cost=args.living_cost,
        birth_threshold=args.birth_threshold,
        birth_cost=args.birth_cost,
        initial_energy=args.initial_energy,
        max_age=args.max_age,
        stagger_ages=not args.no_stagger_ages,
        crossover_rate=args.crossover,
        challenge=args.challenge,
        merge_after=args.merge_after,
        pooled_capacity=args.pooled_capacity,
        seed_from=args.from_run,
        seed_holistic=args.from_holistic,
        seed_conventional=args.from_conventional,
    )
    if args.neutral:
        eco.starvation, eco.birth_threshold, eco.birth_cost, eco.living_cost = False, 0.0, 0.0, 0.0
    if eco.merge_after is not None:
        if eco.merge_after >= args.seasons:
            print(f"warning: --merge-after {eco.merge_after} is not before season {args.seasons}, so the ecologies never meet")
        else:
            print(f"pre-registered: merge after season {eco.merge_after}, pooled capacity {eco.slots(True)}")
    Ecology(evo, eco, out_dir=args.out).run()
    print(f"results in {args.out}/history.json")
    return 0


def _ecology_history(data: dict) -> int:
    """Season table for an ecology run: population size, turnover, lifetime scores and ages."""
    print("season  pop           alive  births  deaths  best/mean lifetime  mean age  max age")
    by_season: dict = {}
    for e in data["history"]:
        by_season.setdefault(e["season"], {})[e["population"]] = e
    for season, pops in sorted(by_season.items()):
        for kind in ("holistic", "conventional"):
            e = pops.get(kind)
            if e is None:
                continue
            print(f"{season:6d}  {kind:12s} {e['alive']:6d}  {e['births']:6d}  {e['deaths']:6d}  {e['best_lifetime_score']:.3f}/{e['mean_lifetime_score']:.3f}       {e['mean_age']:8.1f}  {e['max_age']:7d}")
    return 0


def cmd_history(args) -> int:
    with open(args.history) as f:
        data = json.load(f)
    if data.get("ecology"):
        return _ecology_history(data)
    print("generation  holistic(best/mean)  conventional(best/mean)")
    by_gen: dict = {}
    for e in data["history"]:
        by_gen.setdefault(e["generation"], {})[e["population"]] = e
    for gen, pops in sorted(by_gen.items()):
        h = pops.get("holistic", {})
        c = pops.get("conventional", {})
        print(f"{gen:10d}  {h.get('best_fitness', float('nan')):.3f}/{h.get('mean_fitness', float('nan')):.3f}            {c.get('best_fitness', float('nan')):.3f}/{c.get('mean_fitness', float('nan')):.3f}")
    print()
    print("champion bouts (holistic mean fitness; 0.5 = parity)")
    for ch in data["champions"]:
        print(f"  gen {ch['generation']:3d}: {ch['holistic_mean_fitness']:.3f}  wins {ch['holistic_wins']}-{ch['conventional_wins']} of {ch['n_bouts']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rabbitstew", description="Robot simulator with variable morphologies.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("random", help="write a random genotype")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--nodes", type=int, default=None, help="number of nodes (default: random 2-5)")
    s.add_argument("--out", default="random.json")
    s.set_defaults(func=cmd_random)

    s = sub.add_parser("fixed", help="write the fixed Pioneer-style genotype")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--hidden", type=int, default=6, help="hidden neurons in the global brain")
    s.add_argument("--body", choices=["pioneer", "quadruped"], default="pioneer")
    s.add_argument("--drive", action="store_true", help="constant forward drive instead of random weights")
    s.add_argument("--power", type=float, default=0.6, help="drive level for --drive")
    s.add_argument("--out", default="pioneer.json")
    s.set_defaults(func=cmd_fixed)

    s = sub.add_parser("inspect", help="validate a genotype and describe its phenotype")
    s.add_argument("genotype")
    s.add_argument("--size-ratio", type=float, default=None)
    s.set_defaults(func=cmd_inspect)

    s = sub.add_parser("simulate", help="simulate one robot, or a two-robot bout")
    s.add_argument("genotypes", nargs="+", help="one or more genotype files")
    s.add_argument("--duration", type=float, default=None)
    s.add_argument("--size-ratio", type=float, default=None)
    s.add_argument("--start-distance", type=float, default=None)
    s.add_argument("--arena", type=float, default=0.0, help="radius of a fence around the arena (0 = none)")
    s.add_argument("--mass-budget", type=float, default=None, help="cap every robot's total mass (kg)")
    s.add_argument("--terrain", choices=["flat", "random", "plateau", "rails"], default=None)
    s.add_argument("--terrain-seed", type=int, default=None)
    s.add_argument("--obstacles", type=int, default=None)
    s.add_argument("--out", default=None, help="trajectory file to write")
    s.add_argument("--html", default=None, help="HTML replay to write")
    s.add_argument("--title", default=None)
    s.add_argument("--view", action="store_true", help="open the interactive MuJoCo viewer")
    s.set_defaults(func=cmd_simulate)

    s = sub.add_parser("visualize", help="turn a trajectory file into an HTML replay")
    s.add_argument("trajectory")
    s.add_argument("--out", default="replay.html")
    s.add_argument("--title", default=None)
    s.set_defaults(func=cmd_visualize)

    s = sub.add_parser("evolve", help="run the holistic-versus-conventional experiment")
    s.add_argument("--generations", type=int, default=30)
    s.add_argument("--population", type=int, default=20)
    s.add_argument("--elites", type=int, default=2)
    s.add_argument("--champion-interval", type=int, default=5)
    s.add_argument("--champions", type=int, default=3)
    s.add_argument("--champion-mode", choices=["best", "roundrobin", "all"], default="best", help="best: paper's best-vs-best; roundrobin: top-k each, both sides; all: every member vs every member, both sides")
    s.add_argument("--workers", type=int, default=1)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--duration", type=float, default=None, help="seconds of simulated time per bout")
    s.add_argument("--size-ratio", type=float, default=None)
    s.add_argument("--start-distance", type=float, default=None)
    s.add_argument("--arena", type=float, default=0.0)
    s.add_argument("--mass-budget", type=float, default=None, help="cap every robot's total mass (kg), e.g. 15.34 to match the Pioneer")
    s.add_argument("--terrain", choices=["flat", "random", "plateau", "rails"], default=None, help="task terrain (default flat); random draws obstacles afresh every generation")
    s.add_argument("--terrain-seed", type=int, default=None, help="fix a random terrain for the whole run instead of resampling it every generation")
    s.add_argument("--obstacles", type=int, default=None, help="obstacles in a random terrain (default 14)")
    s.add_argument("--brain-model", choices=["paper", "rich", "foraging"], default="paper", help="paper: contact + direction sensors, tanh, torque; rich: many sensors, neuron functions and servo motors")
    s.add_argument("--conventional-topology", action="store_true", help="let the fixed body's controller topology evolve too, so only the body differs between populations")
    s.add_argument("--random-start", action="store_true", help="draw the start bearing, distance and headings of every bout")
    s.add_argument("--score", choices=["distance", "time_at_target", "closeness", "food"], default=None, help="bout score: the paper's final-distance ratio, time spent at the target, or closeness integrated over the bout (dense)")
    s.add_argument("--opponents", type=int, default=1, help="opponents per member per generation (previous top ranks); 1 = all-versus-best")
    s.add_argument("--draws", type=int, default=1, help="start-layout draws per pairing")
    s.add_argument("--locomotion-phase", type=int, default=0, help="generations of solo fitness before competition begins")
    s.add_argument("--fixed-body", default="pioneer", help="the conventional population's body: pioneer, quadruped, or a genotype file whose body is kept and whose weights are redrawn")
    s.add_argument("--hidden", type=int, default=6, help="hidden neurons in the designed body's controller")
    s.add_argument("--waypoints", type=int, default=None, help="after holding the target, move it to a new random point up to this many times (demands steering)")
    s.add_argument("--holistic-seed", default=None, help="genotype file the holistic population starts from (fully evolvable) instead of random bodies")
    s.add_argument("--heading-curriculum", type=int, default=0, help="generations over which the random-start heading offset widens from 0 to full")
    s.add_argument("--survival", action="store_true", help="(mu+lambda) parents persist, are re-evaluated each generation and compete with children on running-mean fitness")
    s.add_argument("--selection", choices=["tournament", "lexicase"], default="tournament", help="parent selection: tournament on scalar fitness, or epsilon-lexicase over the score vector")
    s.add_argument("--mirror", action="store_true", help="allow mirrored (reflected) connections in the holistic encoding")
    s.add_argument("--neighbour-links", action="store_true", help="local brains may read neighbouring nodes' units, as in Sims (1994)")
    s.add_argument("--archive", action="store_true", help="breed the holistic population partly from a descriptor archive of structurally distinct elites")
    s.add_argument("--resume", action="store_true", help="continue the run in --out from its saved state (optionally to a higher --generations)")
    s.add_argument("--out", default="runs/experiment")
    _add_food_args(s)
    s.set_defaults(func=cmd_evolve)

    s = sub.add_parser("gallery", help="re-simulate every generation's champion bout into one HTML page with a slider")
    s.add_argument("run_dir", help="an experiment output directory (from `evolve --out`)")
    s.add_argument("--out", default="gallery.html")
    s.add_argument("--every", type=int, default=1, help="render every N-th generation (the last is always included); 0 = only --gens")
    s.add_argument("--gens", default=None, help="comma-separated generations to include in addition to --every")
    s.add_argument("--record-every", type=int, default=4, help="control ticks between replay frames (higher = smaller page)")
    s.add_argument("--title", default=None)
    s.set_defaults(func=cmd_gallery)

    s = sub.add_parser("report", help="champion curve and size statistics for one run or several seeds, as an HTML page")
    s.add_argument("run_dirs", nargs="+", help="experiment output directories (several = seeds of one configuration)")
    s.add_argument("--out", default="report.html")
    s.add_argument("--title", default=None)
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("compare", help="overlay the mean champion curves of several named conditions")
    s.add_argument("groups", nargs="+", help="NAME=dir1,dir2,... (one per condition; the dirs are its seeds)")
    s.add_argument("--out", default="compare.html")
    s.add_argument("--title", default=None)
    s.add_argument("--note", default=None, help="a caveat shown under the title")
    s.set_defaults(func=cmd_compare)

    s = sub.add_parser("analyze", help="solo capability trials, descriptors, lesion maps, diversity and ancestry for a run")
    s.add_argument("run_dir")
    s.add_argument("--every", type=int, default=5, help="analyse every N-th generation's bests (the last is always included)")
    s.add_argument("--workers", type=int, default=1)
    s.add_argument("--lesions", choices=["none", "final", "all"], default="final", help="which bests get a lesion map")
    s.add_argument("--out", default=None, help="analysis.json path (default: inside the run directory)")
    s.add_argument("--html", default=None, help="analysis.html path (default: inside the run directory)")
    s.set_defaults(func=cmd_analyze)

    s = sub.add_parser("synergy", help="brain and body ablations and brain transplants for a run's final champions")
    s.add_argument("run_dir")
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_synergy)

    s = sub.add_parser("heritability", help="realised heritability of fitness (parent-offspring correlation) from a run's lineage log")
    s.add_argument("run_dirs", nargs="+")
    s.add_argument("--founder-model", action="store_true", help="also print the founders expected under pure-noise fitness for the run's reproduction scheme")
    s.add_argument("--window", nargs=2, type=int, metavar=("FIRST", "LAST_PLUS_ONE"), help="restrict to children born in generations [FIRST, LAST_PLUS_ONE)")
    s.set_defaults(func=cmd_heritability)

    s = sub.add_parser("ecology", help="run both populations as ecologies (energy, age, births and deaths) instead of a GA")
    s.add_argument("--seasons", type=int, default=300)
    s.add_argument("--capacity", type=int, default=60, help="slots per population")
    s.add_argument("--living-cost", type=_cost, default="relative", help="energy per season, or 'relative' (each population's mean gain that season; conserves energy)")
    s.add_argument("--birth-threshold", type=float, default=3.0)
    s.add_argument("--birth-cost", type=float, default=1.0)
    s.add_argument("--initial-energy", type=float, default=2.0)
    s.add_argument("--max-age", type=int, default=60)
    s.add_argument("--no-stagger-ages", action="store_true", help="start every founder at age 0 (cohorts then die together)")
    s.add_argument("--neutral", action="store_true", help="drift control: no starvation, free breeding (threshold and cost 0), turnover only by age")
    s.add_argument("--crossover", type=float, default=0.3)
    s.add_argument("--challenge", choices=["solo", "paired", "foraging"], default="solo")
    s.add_argument("--group-size", type=int, default=4, help="robots per arena under the foraging challenge")
    s.add_argument("--merge-after", type=int, default=None, metavar="N", help="interchange: from season N the two ecologies share one arena and one pooled capacity, births of either kind taking any free slot (pre-register N)")
    s.add_argument("--pooled-capacity", type=int, default=None, metavar="SLOTS", help="slots in the merged arena (default: twice --capacity, so neither fauna gains or loses room by merging)")
    s.add_argument("--from-run", default=None, metavar="RUN", help="start both populations from a previous run's saved populations (RUN/<kind>/final)")
    s.add_argument("--from-holistic", default=None, metavar="PATH", help="start the holistic population from this run directory, population directory or genotype file (overrides --from-run)")
    s.add_argument("--from-conventional", default=None, metavar="PATH", help="the same for the designed-body population")
    s.add_argument("--workers", type=int, default=1)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--duration", type=float, default=None)
    s.add_argument("--size-ratio", type=float, default=None)
    s.add_argument("--start-distance", type=float, default=None)
    s.add_argument("--arena", type=float, default=0.0)
    s.add_argument("--mass-budget", type=float, default=None)
    s.add_argument("--terrain", choices=["flat", "random", "plateau", "rails"], default="random")
    s.add_argument("--terrain-seed", type=int, default=None)
    s.add_argument("--obstacles", type=int, default=None)
    s.add_argument("--random-start", action="store_true", default=True)
    s.add_argument("--score", choices=["distance", "time_at_target", "closeness", "food"], default="closeness")
    s.add_argument("--waypoints", type=int, default=None)
    s.add_argument("--brain-model", choices=["paper", "rich", "foraging"], default="rich")
    s.add_argument("--conventional-topology", action="store_true", default=True)
    s.add_argument("--fixed-body", default="pioneer")
    s.add_argument("--hidden", type=int, default=6)
    s.add_argument("--mirror", action="store_true")
    s.add_argument("--neighbour-links", action="store_true")
    s.add_argument("--holistic-seed", default=None)
    s.add_argument("--heading-curriculum", type=int, default=0)
    s.add_argument("--out", default="runs/ecology")
    _add_food_args(s)
    s.set_defaults(func=cmd_ecology)

    s = sub.add_parser("history", help="summarise an experiment's history.json")
    s.add_argument("history")
    s.set_defaults(func=cmd_history)
    return p


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(argv)
    args.generations_given = any(a == "--generations" or a.startswith("--generations=") for a in argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
