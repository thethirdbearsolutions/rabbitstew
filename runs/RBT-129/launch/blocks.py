"""RBT-129 world blocks (DESIGN section 2; section 5.6 item 5): every point of the sweep as one parameter block, built
from one table, so that no point is typed by hand.

A point's id is ``c<clutter>-p<price>-<layout>-<smell>`` (DESIGN section 2), with the clutter written without its point
(``c0``, ``c05``, ``c1``, ``c15``, ``c2``) and the price in thousandths of an item per kJ (``p010`` ... ``p080``).  A block
is:
  * ``argv``: the ``ecology`` flags of the world (the committed default world of RBT-90 part 2 / RBT-107, then the
    point's clutter, price, layout and smell, then the fixed eating rule, the fairness flags and ``--sweep-log``);
  * ``block``: the world as a flat dictionary of dotted config paths, read from the config.json those flags produce
    (``cli.ecology_configs``, the ``ecology`` subcommand's own path, without running anything).

Two fields are the gates' to fix and are therefore parameters, not constants: the fairness flags (RBT-128's ``--fair``,
#432) and the eating rule (RBT-125 section C, pending; the design's candidate is ``--eat-from root``).  A block built
without ``fair`` says so (``fair_pending``); the launchers refuse such blocks (``stages.py``).

    python runs/RBT-129/launch/blocks.py                 # the table: 150 ids, N and argv (no file written)
    python runs/RBT-129/launch/blocks.py --export DIR    # also DIR/<id>.json per point (at launch: runs/RBT-129/worlds)

Nothing here runs a season.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from rabbitstew.cli import build_parser, ecology_configs  # noqa: E402

#: clutter levels c (DESIGN section 3.1)
CLUTTER = (0.0, 0.5, 1.0, 1.5, 2.0)
#: obstacle counts N by layout family: the 3 m layouts (U, HP; obstacle disc 2.6 m) and PW (4 m food disc, obstacle
#: disc 3.6 m) at the registered free-area counts (DESIGN section 3.1, pre-data amendment 2026-09-28; RBT-130 census)
N_3M = {0.0: 0, 0.5: 7, 1.0: 14, 1.5: 21, 2.0: 28}
N_PW = {0.0: 0, 0.5: 16, 1.0: 32, 1.5: 48, 2.0: 64}
#: work prices per kJ (DESIGN section 3.2)
PRICES = (0.01, 0.018, 0.03, 0.053, 0.08)
#: food layouts (DESIGN section 3.3); MP is conditional on RBT-129b and has no block here
LAYOUTS = ("U", "HP", "PW")
LAYOUT_FLAGS = {
    "U": [],
    "HP": ["--food-patches", "3", "--patch-radius", "0.6"],
    "PW": ["--food-patches", "2", "--patch-radius", "0.4", "--food-radius", "4.0", "--regrow-delay", "60",
           "--smell", "log", "--food-decay", "1.5"],
}
#: smell levels (DESIGN section 3.4): L legacy, G the RBT-125 contrast channel at the registered G = 2.5, tau = 2 s
#: (RBT-125 gate section A: PASS at G = 2.5, #430 626ca4c)
SMELLS = ("L", "G")
G_REGISTERED = 2.5
TAU = 2.0
SMELL_FLAGS = {"L": [], "G": ["--smell-contrast", f"{G_REGISTERED:g}", "--smell-tau", f"{TAU:g}"]}
#: the committed default world (RBT-90 part 2's command, as RBT-107's fresh_seed.sh runs it), less the per-point axes.
#: DESIGN section 2's ecology row: capacity 60, group 4, initial energy 3, threshold 3, cost 1, max age 60, staggered
#: ages, living cost 0.25; the bout: 15 s, 12 items of value 1, eat radius 0.35
BASE = ["--capacity", "60", "--challenge", "foraging", "--group-size", "4", "--brain-model", "foraging",
        "--food-items", "12", "--food-radius", "3", "--eat-radius", "0.35", "--food-decay", "1.0",
        "--living-cost", "0.25", "--initial-energy", "3", "--birth-threshold", "3", "--birth-cost", "1", "--max-age", "60",
        "--duration", "15", "--mass-budget", "15.34", "--conventional-topology", "--random-start", "--score", "food"]
#: the eating rule's candidate (DESIGN section 2: "as RBT-125 rules it (candidate: eat_from root)")
EAT_CANDIDATE = ("--eat-from", "root")
#: the four pilot points and the three anchors (DESIGN sections 4.1 and 9.1)
PILOT = ("c1-p030-U-L", "c0-p030-U-L", "c1-p030-PW-G", "c2-p030-PW-G")
ANCHORS = ("c1-p030-U-L", "c0-p030-U-L", "c1-p030-PW-G")
#: the census's PAYS cells (DESIGN section 5.1): L x s x c in {0, 1, 2}, at p = 0.03
PAYS_CELLS = tuple(f"c{c}-p030-{L}-{s}" for L in LAYOUTS for s in SMELLS for c in ("0", "1", "2"))
#: the seeds (DESIGN sections 5.1, 5.2): j = 1..16, seed 129000 + j
SEED_BASE = 129000


def c_tag(c: float) -> str:
    return f"c{c:g}".replace(".", "")


def p_tag(p: float) -> str:
    return f"p{round(p * 1000):03d}"


def point_id(c: float, p: float, layout: str, smell: str) -> str:
    return f"{c_tag(c)}-{p_tag(p)}-{layout}-{smell}"


def parse_id(pid: str) -> tuple:
    ct, pt, layout, smell = pid.split("-")
    c = {c_tag(x): x for x in CLUTTER}[ct]
    p = {p_tag(x): x for x in PRICES}[pt]
    if layout not in LAYOUTS or smell not in SMELLS:
        raise ValueError(f"not a registered point: {pid}")
    return c, p, layout, smell


def all_ids() -> list:
    """The full 5 x 5 x 3 x 2 = 150 points (the census grid, DESIGN section 4.1), in a fixed order."""
    return [point_id(c, p, L, s) for c in CLUTTER for p in PRICES for L in LAYOUTS for s in SMELLS]


def obstacles(c: float, layout: str) -> tuple:
    """(N, obstacle radius) for clutter c in a layout; N = 0 is `terrain flat`."""
    if layout == "PW":
        return N_PW[c], 3.6
    return N_3M[c], 2.6


def world_argv(pid: str, fair=None, eat=EAT_CANDIDATE) -> list:
    """The ``ecology`` flags of a point's world (no seed, seasons, workers or out)."""
    c, p, layout, smell = parse_id(pid)
    n, radius = obstacles(c, layout)
    terrain = ["--terrain", "flat"] if n == 0 else ["--terrain", "random", "--obstacles", str(n), "--obstacle-radius", f"{radius:g}"]
    return (list(BASE) + ["--work-cost", f"{p:g}"] + terrain + LAYOUT_FLAGS[layout] + SMELL_FLAGS[smell]
            + list(eat) + list(fair or []) + ["--sweep-log"])


def _flatten(d: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, key + "."))
        else:
            out[key] = v
    return out


#: config.json fields that belong to the arm, not the world
ARM_FIELDS = ("seed", "workers", "generations", "ecology.seasons")


def config_dict(argv: list, seed: int = SEED_BASE + 1, seasons: int = 300) -> dict:
    """The config.json an ``ecology`` run with these flags writes, built by the subcommand's own path without running
    (``Ecology.__init__`` writes ``{**_jsonable(evo.to_dict()), "ecology": eco.to_dict()}``)."""
    from rabbitstew.ecology import _jsonable

    args = build_parser().parse_args(["ecology", *argv, "--seed", str(seed), "--seasons", str(seasons)])
    evo, eco = ecology_configs(args)
    return json.loads(json.dumps({**_jsonable(evo.to_dict()), "ecology": eco.to_dict()}))


def block(pid: str, fair=None, eat=EAT_CANDIDATE) -> dict:
    """The world block of a point: its id, axes, flags and the world as dotted config paths."""
    c, p, layout, smell = parse_id(pid)
    argv = world_argv(pid, fair=fair, eat=eat)
    flat = {k: v for k, v in _flatten(config_dict(argv)).items() if k not in ARM_FIELDS}
    n, radius = obstacles(c, layout)
    return {"id": pid, "axes": {"clutter": c, "price": p, "layout": layout, "smell": smell, "obstacles": n,
                                "obstacle_radius": radius if n else None},
            "fair": list(fair) if fair else None, "fair_pending": not fair, "eat": list(eat),
            "argv": argv, "block": flat}


def export(directory: str, ids=None, fair=None, eat=EAT_CANDIDATE) -> list:
    os.makedirs(directory, exist_ok=True)
    paths = []
    for pid in ids or all_ids():
        path = os.path.join(directory, f"{pid}.json")
        with open(path, "w") as f:
            json.dump(block(pid, fair=fair, eat=eat), f, indent=1, sort_keys=True)
            f.write("\n")
        paths.append(path)
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", metavar="DIR", default=None, help="write DIR/<id>.json per point")
    ap.add_argument("--fair", default="", help="the fairness flags, as one string (RBT-128's '--fair'); empty = pending")
    ap.add_argument("--eat", default=" ".join(EAT_CANDIDATE), help="the eating-rule flags (default: the design's candidate)")
    a = ap.parse_args(argv)
    fair, eat = a.fair.split(), a.eat.split()
    ids = all_ids()
    print(f"# RBT-129 world blocks: {len(ids)} points (5 clutter x 5 price x 3 layout x 2 smell)")
    print(f"# fairness flags: {' '.join(fair) if fair else 'PENDING (no --fair given): the launchers refuse these blocks'}")
    print(f"# eating rule: {' '.join(eat)}" + ("  (the design's candidate; RBT-125 section C pending)" if tuple(eat) == EAT_CANDIDATE else ""))
    print(f"# pilot: {' '.join(PILOT)};  anchors: {' '.join(ANCHORS)};  PAYS cells: {len(PAYS_CELLS)}")
    print("# id               N  R_o   argv (after the committed base)")
    for pid in ids:
        c, p, layout, smell = parse_id(pid)
        n, radius = obstacles(c, layout)
        tail = world_argv(pid, fair=fair, eat=eat)[len(BASE):]
        print(f"  {pid:16s} {n:2d}  {radius if n else 0:.1f}  {' '.join(tail)}")
    print(f"# base: {' '.join(BASE)}")
    if a.export:
        paths = export(a.export, ids, fair=fair, eat=eat)
        print(f"# exported {len(paths)} blocks to {a.export}")


if __name__ == "__main__":
    main()
