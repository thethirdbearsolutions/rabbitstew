"""Command-line interface: ``rabbitstew <command> ...``."""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from .evolution import Experiment, EvolutionConfig
from .fixed import drive_straight_genotype, pioneer_genotype
from .gallery import build_gallery
from .report import build_report
from .genetics import MutationConfig
from .genotype import Genotype, random_genotype
from .simulation import SimConfig, Simulation, run_bout
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
    return cfg


def cmd_random(args) -> int:
    rng = np.random.default_rng(args.seed)
    g = random_genotype(rng, n_nodes=args.nodes, name=f"random-{args.seed}")
    g.save(args.out)
    print(f"wrote {args.out}: {len(g.nodes)} nodes, {g.count_links()} links")
    return 0


def cmd_fixed(args) -> int:
    rng = np.random.default_rng(args.seed)
    g = drive_straight_genotype(args.power) if args.drive else pioneer_genotype(rng, hidden=args.hidden)
    g.save(args.out)
    print(f"wrote {args.out}: fixed Pioneer-style body ({'constant drive' if args.drive else 'random weights'})")
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
    build_gallery(args.run_dir, args.out, every=args.every, record_every=args.record_every, title=args.title)
    return 0


def cmd_report(args) -> int:
    info = build_report(args.run_dirs, args.out, title=args.title)
    t = info["totals"]
    print(f"wrote {args.out}: {info['runs']} run(s), holistic {t['wins']}-{t['losses']} of {t['n']} champion bouts, by thirds {info['thirds']}")
    return 0


def cmd_history(args) -> int:
    with open(args.history) as f:
        data = json.load(f)
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
    s.add_argument("--terrain", choices=["flat", "plateau", "rails"], default=None)
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
    s.add_argument("--champion-mode", choices=["best", "roundrobin"], default="best")
    s.add_argument("--workers", type=int, default=1)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--duration", type=float, default=None, help="seconds of simulated time per bout")
    s.add_argument("--size-ratio", type=float, default=None)
    s.add_argument("--start-distance", type=float, default=None)
    s.add_argument("--arena", type=float, default=0.0)
    s.add_argument("--mass-budget", type=float, default=None, help="cap every robot's total mass (kg), e.g. 15.34 to match the Pioneer")
    s.add_argument("--terrain", choices=["flat", "plateau", "rails"], default=None, help="task terrain (default flat)")
    s.add_argument("--brain-model", choices=["paper", "rich"], default="paper", help="paper: contact + direction sensors, tanh, torque; rich: many sensors, neuron functions and servo motors")
    s.add_argument("--conventional-topology", action="store_true", help="let the fixed body's controller topology evolve too, so only the body differs between populations")
    s.add_argument("--resume", action="store_true", help="continue the run in --out from its saved state (optionally to a higher --generations)")
    s.add_argument("--out", default="runs/experiment")
    s.set_defaults(func=cmd_evolve)

    s = sub.add_parser("gallery", help="re-simulate every generation's champion bout into one HTML page with a slider")
    s.add_argument("run_dir", help="an experiment output directory (from `evolve --out`)")
    s.add_argument("--out", default="gallery.html")
    s.add_argument("--every", type=int, default=1, help="render every N-th generation (the last is always included)")
    s.add_argument("--record-every", type=int, default=4, help="control ticks between replay frames (higher = smaller page)")
    s.add_argument("--title", default=None)
    s.set_defaults(func=cmd_gallery)

    s = sub.add_parser("report", help="champion curve and size statistics for one run or several seeds, as an HTML page")
    s.add_argument("run_dirs", nargs="+", help="experiment output directories (several = seeds of one configuration)")
    s.add_argument("--out", default="report.html")
    s.add_argument("--title", default=None)
    s.set_defaults(func=cmd_report)

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
