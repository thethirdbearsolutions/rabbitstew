"""RBT-129 Stage P (pilot) and Stage 0 (census) launchers (DESIGN sections 4.1, 5.1, 5.2, 5.5 K1, 11.1, 11.2).

    stages.py plan   P|0|P,0 [--hosts 10]           the arms, seeds, host layout and core-h against the budget (no run)
    stages.py emit   P|0|P,0 --fair=--fair [--eat='--eat-from root --eat-rule surface'] [--hosts 10] [--root runs/RBT-129]
                                                     the lane files, the world blocks (worlds/<id>.json) and launch.txt
    stages.py prelaunch --fair=--fair --eat=...     the pre-launch prints (prints.py) under the launch block, to
                                                     lanes/prelaunch_prints.txt (fixtures only; guarded like emit)
    stages.py run-lane LANEFILE                     one lane (launch as a harness background task, one per lane,
                                                     WORKERS=2, two lanes a 4-core session)
    stages.py probes --steer PATH --steer-sha SHA --steer-cmd TEMPLATE --planted-cmd TEMPLATE --fair=--fair --eat=...
                                                     Stage P's perception probes, each point's planted set first; units
                                                     extinct pre-merge skipped and listed in lanes/probes/extinct.txt
    stages.py pays-prize --fair=--fair --eat=... --bodies BODIES_ROOT   Stage 0's designed PAYS prize leg at the 18
                                                     cells (RBT-106's prize at a = 6 through RBT-125's merged section-A
                                                     harness, prize_gate.py, on its ten designed hosts)
    stages.py pays   --steer PATH --steer-sha SHA --pays-cmd TEMPLATE [--steps-harness PATH --steps-sha SHA
                     --steps-cmd TEMPLATE] --fair=--fair --eat=...
                                                     holistic PAYS at the 18 cells (RBT-132's planters.py pays, into
                                                     stage0/pays/<cell>/holistic/), and the holistic nose step once its
                                                     harness exists
    stages.py calibrate --fair=--fair [--hosts HOSTS_ROOT]
                                                     K3's calibration (DESIGN 12, the 09:44 amendment): the planted
                                                     controls at c0-p030-PW-G and c0-p030-HP-G; the runner prints only
                                                     per plant SEEN and dT's mean and SD (calib-extract)
    stages.py check-branches LANEFILE... [--save]    readout side: every run directory and pilot unit record has its
                                                     checkpoint branch (--save: snapshot the missing ones, serially)
    stages.py save DIR                               one serialized, logged snapshot (what the leg scripts call)

**Guards** (launch adversary L1, L2, S5, S6).  Every launching command refuses (exit 4) unless the fairness tokens are
exactly ``--fair`` (``--unfair-i-know`` never passes) and ``--fair`` exists on this tree, and unless the eating rule
is well formed (default: the ruled ``--eat-from root --eat-rule surface``, coordinator 03:10; any other is printed as
not the ruled one).  Every block it builds must pass ``fair_deviations``: the marker ``"fairness": "fair"``, every
value of RBT-128's preset, and RBT-128's own ``fair.check(config)``, which is required.  ``run-lane`` also refuses
off x86_64 (exit 3), and unless this session's ``rabbitstew/``, ``runs/RBT-129/launch/`` and ``scripts/`` trees are
the ones launch.txt records and nothing under them, the worlds or the lanes is uncommitted (exit 5).  It rebuilds
every world block from launch.txt's flags and refuses one that differs (exit 4).  ``probes`` and ``pays`` refuse
(exit 6) unless ``steer.py`` (and for ``pays``, section B's harness) exists at its ruled git blob hash and every command
template is given.  **No-peek:** the runner prints progress only (job names and exit codes, and K1's verdict); no
income, share, season table or garden figure is printed or read by this tool.

**Stage P** (4 points x seeds 129001-129004, 300 seasons).  Per point and seed, one chain on one lane:
  S60     a fresh S run to its season-59 checkpoint (``--seasons 60``: state.json at season 60; RBT-130 README)
  ckpt60  a copy of that directory, before S continues (the fork's source)
  S       S resumed to 300
  M       ckpt60 forked with ``ecology.merge_after = 60``, ``pooled_capacity = 120``, resumed to 300
  N       the same with ``merge_null`` = holistic on odd seeds, conventional on even (all 4 seeds at the pilot, S10)
and per point, on seed 129001's chain, **K1** (DESIGN 5.5): a straight run to season 65, and ckpt60 forked with the
merge unset and resumed to 65; K1 PASSES when every output file is byte-identical (genomes, state.json, lineage,
cohorts, history; config.json, platform.json and the logs excluded; r4's seasons.txt is history.json).

**Stage 0** (150 points x seeds 129001-129003, arm S only, seasons 0-59): one fresh run a job.  With it, **A**: S 0-59
at W118-b (``c0-p030-U-L``) for the anchor-fallback seeds the census and pilot do not make (129005-129008 with P),
the fork sources of the sweep's own anchor arms (S2).

**Host layout** (DESIGN 11.2; RBT-107's packing rule): ``--hosts`` 4-core sessions, two lanes each at WORKERS = 2.
Lane 0 takes odd seeds, lane 1 even; census seed 129003 is split, first on lane 0 and last on lane 1; a per-seed lock
(``/tmp/rbt129-locks``) makes it hard.  Lane files hold paths relative to the repository root (S9).  Jobs chain back to
back: none waits on a save (L4).  **Saves** (the 09:44 brief): every job's directory is saved when the job ends (a job of
120 arm-seasons or more also every 20 minutes while it runs), in a background thread, serialized on this machine by a
lock and logged (``durable.log``), never sent to /dev/null; a pilot unit's own files (EXTINCT.txt, K1.txt, UNIT.txt)
are mirrored into ``<unit>/record/`` and saved to its own branch.
"""
import argparse
import fcntl
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUNS))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import blocks  # noqa: E402

#: core-seconds per arm-season (DESIGN 11.2's two rates)
CORE_S = (20, 25)
#: the pilot's per-seed probes and levers (RBT-116 section 9), and the planted set per point (M7d), core-h
PROBE_SEED = (0.46, 0.83)
PLANTED_POINT = 0.8
#: Stage 0's 18 PAYS cells, core-h at the two rates (DESIGN 11.2: 195 - 150 and 232 - 187.5)
PAYS_CORE_H = (45.0, 45.0)
PILOT_SEEDS = (1, 2, 3, 4)
CENSUS_SEEDS = (1, 2, 3)
SEASONS = 300
MERGE = 60
POOLED = 120
K1_SEASONS = 65
#: DESIGN 11.2 (r4): the stages' lines and the total, at 20 and 25 core-s; the anchor fallback (9.1; RBT-118 has no
#: registration, so it is adopted, READINESS.md)
BUDGET = {"P": ((77, 83), (93, 99)), "0": ((195, 195), (232, 232)), "total": ((2044, 2270), (2457, 2683)),
          "anchor fallback": ((46, 46), (57, 57)), "A": ((46, 46), (57, 57))}
BRIEF_ENVELOPE = (2200, 2900)
LOCKS = "/tmp/rbt129-locks"


def seed(j: int) -> int:
    return blocks.SEED_BASE + j


def null_kind(j: int) -> str:
    return "holistic" if j % 2 else "conventional"


# -- the guards --------------------------------------------------------------------------------------------------- #

def ecology_options() -> set:
    from rabbitstew.cli import build_parser

    p = build_parser()
    sub = next(a for a in p._actions if isinstance(a, argparse._SubParsersAction))
    return {o for a in sub.choices["ecology"]._actions for o in a.option_strings}


FAIR = ["--fair"]


def _refuse(msg: str, code: int):
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(code)


def check_fair(fair: list) -> None:
    """Refuse unless the fairness tokens are exactly ``--fair`` (launch adversary L1): RBT-128's preset, on this tree.
    Any other list, the bypass ``--unfair-i-know`` included, is refused."""
    if list(fair) != FAIR:
        _refuse(f"the fairness flags must be exactly {' '.join(FAIR)} (RBT-128's ruled set, DESIGN 2); got {' '.join(fair) or 'none'}", 4)
    if "--fair" not in ecology_options():
        _refuse("--fair is not an option of `ecology` on this tree (RBT-128 #432 not merged)", 4)


def fair_deviations(config: dict) -> list:
    """What makes an arm's config.json not the ruled fairness set (L1; coordinator 02:17 (3)): RBT-128's own
    ``fair.check(config)``, which is required, plus this launcher's own reading of the marker and every preset value."""
    from rabbitstew import fair as fair_mod

    out = []
    if config.get("fairness") != "fair":
        out.append(f"fairness is {config.get('fairness')!r}, not 'fair'")
    flat = blocks._flatten(config)
    for dest, value, flag in fair_mod.PRESET:
        keys = [k for k in flat if k.split(".")[-1] == dest]
        if len(keys) != 1 or flat[keys[0]] != value:
            out.append(f"{flag}: config has {[(k, flat[k]) for k in keys] or 'no such key'}")
    check = getattr(fair_mod, "check", None)
    if check is None:
        out.append("rabbitstew.fair.check is not on this tree (#432's fixes, RBT-128 adversary S3)")
    else:
        out += [f"fair.check: {d}" for d in check(config)]
    return out


def check_block(b: dict) -> None:
    """Refuse a world block that is not under the ruled fairness set, or whose ``block`` is not its own config."""
    config = blocks.config_dict(b["argv"])
    dev = fair_deviations(config)
    if dev:
        _refuse(f"{b['id']}: not the ruled fairness set: " + "; ".join(dev), 4)


def check_eat(eat: list) -> None:
    """The eating rule must be exactly the ruled one, ``--eat-from root --eat-rule surface`` (coordinator 03:10; launch
    FIX-CHECK #447, R1).  Nothing else launches."""
    if tuple(eat) != blocks.EAT_RULED:
        _refuse(f"the eating rule must be exactly {' '.join(blocks.EAT_RULED)} (RBT-125 section C, re-ruled 03:10); got {' '.join(eat) or 'none'}", 4)


def surface_clearance_ok(draws: int = 8, items: int = 128) -> bool:
    """Capability probe (R1 (2)): does this tree carry RBT-125 #446's minimal guard for ``eat_rule = surface`` with
    ``clear_from = root``: no item placed within ``eat_radius`` of an eating geom's SURFACE (so nothing is eaten standing
    still), on top of the root-centre clearance?  A body with a long root (a 1.4 m bar after synthesis) is placed in a
    food world of that rule; on a tree that clears only from the root's centre (0.8 m), items land beyond the bar's
    ends within 0.35 m of its surface.  True iff
    every placed item clears the root's surface by ``eat_radius`` and its centre by ``clearance``, with no fallback."""
    import numpy as np
    from rabbitstew.genotype import Brain, Genotype, Node, Segment, Shape
    from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, spawn_layout

    g = Genotype(nodes=[Node(Segment(Shape.BOX, (10.0, 1.0, 1.0), Brain(units=[])))], name="long-root")  # 1.39 m x 0.14 m
    cfg = SimConfig(random_start=True, score="food",
                    food=FoodConfig(items=items, eat_from="root", eat_rule="surface", clear_from="root"))
    f = cfg.food
    for k in range(draws):
        sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, 7000 + k))
        sim.set_food_seed(7000 + k)
        spots = np.asarray(sim.food_spots)
        root = sim.robots[0].geoms[:1]
        centre = sim.data.xpos[sim.robots[0].root_body][:2]
        if getattr(sim, "food_fallbacks", 0):
            continue  # a spot placed without the rule proves nothing either way
        if (float(np.min(sim._surface_distance(root, spots))) < f.eat_radius - 1e-9
                or float(np.min(np.linalg.norm(spots - centre, axis=1))) < f.clearance - 1e-9):
            return False
    return True


def check_surface_clearance(eat: list) -> None:
    """Refuse a surface-eating launch on a tree without RBT-125's surface clearance (#446)."""
    pairs = dict(zip(eat[0::2], eat[1::2]))
    if pairs.get("--eat-rule") == "surface" and not surface_clearance_ok():
        _refuse("this tree clears food only from the root's centre under eat_rule = surface: items can be placed within"
                " eat_radius of the root's surface, eaten standing still (RBT-125 #446's minimal guard not in the tree)", 4)


#: per leg, exactly the tools it runs, with their whole import chain (legs adversary S-1), pinned by git blob hash in
#: its launch record and checked again where its scripts run (exit 6): prize_gate.py loads RBT-103's
#: routed_populations.py, which loads RBT-97's routed_p801.py and g500_direction.py; steps.py loads prize_gate.py
#: RBT-97's chain: routed_p801.py and g500_direction.py load mechanism.py, which loads resign_rbt67.py (ruled 07:11)
#: and RBT-67's compass_dose_response.py (#465 adversary S-5; scripts/compass_*.py are in the pinned scripts/ tree)
RBT97_CHAIN = ("runs/RBT-97/routed_p801.py", "runs/RBT-97/g500_direction.py", "runs/RBT-97/mechanism.py",
               "runs/RBT-97/resign_rbt67.py", "docs/artifacts/RBT-67/compass_dose_response.py")
PRIZE_TOOLS = ("runs/RBT-125/gate/prize_gate.py", "runs/RBT-103/routed_populations.py") + RBT97_CHAIN
STEP_TOOLS = ("runs/RBT-125/gate/steps.py",) + PRIZE_TOOLS
#: RBT-132's planted set and holistic PAYS (RBT132.md (ii)): steer.py, planters.py, which loads RBT-97's chain and, for
#: the planted set's power line, probe_power.py (planters.power_line); the probes add probe_members.py.  The lanes do
#: not read k3_projection.py (the adversary runs it on planted.json)
PLANTERS = "runs/RBT-116/planters.py"
STEER_TOOLS = ("runs/RBT-116/steer.py", PLANTERS, "runs/RBT-116/probe_power.py") + RBT97_CHAIN
PROBE_TOOLS = STEER_TOOLS + ("runs/RBT-116/probe_members.py",)
#: how every runner script must be started (legs adversary S-4)
RUNNER_NOTE = ("# Start this script as a harness background task (the Bash tool's run_in_background), one per session:\n"
               "# never nohup, never a trailing &, never setsid.  A reclaimed container is handled by restarting the same\n"
               "# script, which resumes.  Never pkill a runner by name: kill its children by pid.")


def write_leg_launch(leg_dir: str, leg: str, cells, fair: list, eat: list, extra: dict = None, tools=()) -> str:
    """A leg's own launch record (the same guards as Stage P/0's ``launch.txt``, pinned to this tree): the commit, the
    pinned trees, the fairness and eating flags, the cells whose config.json the leg reads, and every leg tool's blob."""
    os.makedirs(leg_dir, exist_ok=True)
    path = os.path.join(leg_dir, "launch.txt")
    with open(path, "w") as f:
        f.write(f"# RBT-129 launch record: leg {leg}\ncommit {_git('rev-parse', 'HEAD')}\n"
                + "".join(f"tree:{t} {_git('rev-parse', f'HEAD:{t}')}\n" for t in PINNED_TREES)
                + f"fair {' '.join(fair)}\neat {' '.join(eat)}\ncells {' '.join(cells)}\n"
                + "".join(f"tool:{t} {git_hash(os.path.join(ROOT, t)) if os.path.isfile(os.path.join(ROOT, t)) else 'absent'}\n" for t in tools)
                + "".join(f"{k} {v}\n" for k, v in (extra or {}).items())
                + f"emitted {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
    return path


def verify_leg(launch_path: str, root: str = RUNS) -> None:
    """Where a leg's script runs, before any job: x86_64 (exit 3); this session's pinned trees are launch.txt's and
    nothing under them, the worlds or the lanes is uncommitted (exit 5); exactly --fair and the ruled eating rule, the
    tree's surface clearance, and every cell's config.json is what the launch flags build and passes the fairness check
    (exit 4); every tool the record pins is still its blob (exit 6)."""
    launch = read_launch(launch_path)
    check_host(launch)
    fair, eat = launch["fair"].split(), launch["eat"].split()
    check_fair(fair)
    check_eat(eat)
    check_surface_clearance(eat)
    for pid in launch.get("cells", "").split():
        want = json.loads(json.dumps(blocks.config_dict(blocks.world_argv(pid, fair=fair, eat=eat))))
        # both copies (#465 adversary S-4): worlds/config/<id>/ (--config-from, steps.py) and worlds/<id>.config.json
        # (the RBT132.md templates' {config_json}, calibrate)
        for path in (os.path.join(root, "worlds", "config", pid, "config.json"), config_json_path(root, pid)):
            if not os.path.isfile(path):
                _refuse(f"{os.path.relpath(path, root)} is missing; re-emit", 4)
            got = json.load(open(path))
            if got != want:
                _refuse(f"{os.path.relpath(path, root)} is not what launch.txt's flags build; re-emit", 4)
            dev = fair_deviations(got)
            if dev:
                _refuse(f"{pid}: not the ruled fairness set: " + "; ".join(dev), 4)
    for k, v in launch.items():
        if k.startswith("tool:") and v != "absent" and git_hash(os.path.join(ROOT, k[5:])) != v:
            _refuse(f"{k[5:]} is not blob {v}", 6)


def write_script(path: str, jobs: list, pins: list, launch: str = None) -> None:
    """An emitted job script that re-verifies, where it runs, every tool's git blob hash before any job (R1 (4)), and
    refuses (exit 6) on a difference."""
    head = ["#!/bin/bash", RUNNER_NOTE, "set -e"]
    if launch:  # the leg's host guards, where it runs (exit 3, 4, 5, 6)
        head += ['cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"',
                 f"python runs/RBT-129/launch/stages.py verify {rel(launch)}"]
    for tool, sha in pins:
        head.append(f'[ "$(git hash-object {tool})" = "{sha}" ] || {{ echo "REFUSED: {tool} is not blob {sha}" >&2; exit 6; }}')
    with open(path, "w") as f:
        f.write("\n".join(head + jobs) + "\n")


def git_hash(path: str) -> str:
    return subprocess.run(["git", "hash-object", path], capture_output=True, text=True).stdout.strip()


def check_pinned(path, sha, what: str) -> None:
    """A tool the launch depends on must exist and be the ruled version: its git blob hash equals ``sha`` (S5)."""
    if not path or not os.path.isfile(path):
        _refuse(f"{what} not found at {path!r} (a gate, DESIGN 11.1)", 6)
    if not sha or git_hash(path) != sha:
        _refuse(f"{what} at {path} is blob {git_hash(path)}, not the ruled {sha or '(none given: --*-sha)'}", 6)


def check_steer(path, template, sha=None) -> None:
    check_pinned(path, sha, "RBT-116's steer.py")
    if not template:
        _refuse("no command template: give the ruled steer.py's command line (DESIGN 5.3(c))", 6)


def tool_pins(tools) -> list:
    """(tool, blob) for each repository-relative tool; refuse (exit 6) while one is not on this tree (RBT-132's
    planters.py, probe_members.py and probe_power.py arrive with #459)."""
    missing = [t for t in tools if not os.path.isfile(os.path.join(ROOT, t))]
    if missing:
        _refuse("not on this tree: " + ", ".join(missing) + " (RBT-132, #459)", 6)
    return [(t, git_hash(os.path.join(ROOT, t))) for t in tools]


#: the trees a launch pins (L2): the simulator, this launcher and the checkpoint script
PINNED_TREES = ("rabbitstew", "runs/RBT-129/launch", "scripts")
#: and what must be committed before any lane runs (the blocks and lane files every session reads)
CLEAN = PINNED_TREES + ("runs/RBT-129/worlds", "runs/RBT-129/lanes")


def _git(*a) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def read_launch(path: str) -> dict:
    rec = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        k, _, v = line.rstrip("\n").partition(" ")
        rec[k] = v
    return rec


def check_host(launch: dict) -> None:
    """Refuse off x86_64 (RBT-96), and unless this session runs the launch's code (L2): every pinned tree at HEAD equals
    the tree recorded in launch.txt, and nothing under the pinned trees, the worlds or the lanes is uncommitted."""
    if platform.machine() != "x86_64":
        _refuse("RBT-129 arms run on the cloud x86_64 image only (RBT-96)", 3)
    for t in PINNED_TREES:
        key = "tree:" + t
        if key not in launch or _git("rev-parse", f"HEAD:{t}") != launch[key]:
            _refuse(f"HEAD:{t} is {_git('rev-parse', f'HEAD:{t}')}, not the launch's {launch.get(key)}; check out the launch commit", 5)
    dirty = _git("status", "--porcelain", "--", *CLEAN)
    if dirty:
        _refuse("uncommitted changes under " + ", ".join(CLEAN) + ":\n" + dirty, 5)


# -- the plan ----------------------------------------------------------------------------------------------------- #

def pilot_units(root: str) -> list:
    """One unit per pilot point and seed: the chain S60, ckpt60, S, M, N (and K1 on seed 129001)."""
    units = []
    for pid in blocks.PILOT:
        for j in PILOT_SEEDS:
            d = os.path.join(root, "stageP", pid, str(seed(j)))
            jobs = [
                {"job": "fresh", "name": f"P/{pid}/{seed(j)}/S60", "point": pid, "seed": seed(j), "dir": f"{d}/S", "seasons": MERGE, "cost": MERGE},
                {"job": "snapshot", "name": f"P/{pid}/{seed(j)}/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "seed": seed(j), "cost": 0},
                {"job": "resume", "name": f"P/{pid}/{seed(j)}/S", "dir": f"{d}/S", "seed": seed(j), "seasons": SEASONS, "cost": SEASONS - MERGE},
                {"job": "fork", "name": f"P/{pid}/{seed(j)}/M", "src": f"{d}/ckpt60", "dir": f"{d}/M", "seed": seed(j), "seasons": SEASONS,
                 "set": {"merge_after": MERGE, "pooled_capacity": POOLED}, "cost": SEASONS - MERGE},
                {"job": "fork", "name": f"P/{pid}/{seed(j)}/N", "src": f"{d}/ckpt60", "dir": f"{d}/N", "seed": seed(j), "seasons": SEASONS,
                 "set": {"merge_after": MERGE, "pooled_capacity": POOLED, "merge_null": null_kind(j)}, "cost": SEASONS - MERGE},
            ]
            if j == PILOT_SEEDS[0]:
                jobs += [
                    {"job": "fresh", "name": f"P/{pid}/{seed(j)}/K1ref", "point": pid, "seed": seed(j), "dir": f"{d}/K1ref", "seasons": K1_SEASONS, "cost": K1_SEASONS},
                    {"job": "fork", "name": f"P/{pid}/{seed(j)}/K1fork", "src": f"{d}/ckpt60", "dir": f"{d}/K1fork", "seed": seed(j), "seasons": K1_SEASONS, "set": {}, "cost": K1_SEASONS - MERGE},
                    {"job": "k1", "name": f"P/{pid}/{seed(j)}/K1", "ref": f"{d}/K1ref", "dir": f"{d}/K1fork", "seed": seed(j), "cost": 0},
                ]
            units.append({"stage": "P", "seed": seed(j), "jobs": jobs})
    return units


def census_units(root: str) -> list:
    return [{"stage": "0", "seed": seed(j), "jobs": [
        {"job": "fresh", "name": f"0/{pid}/{seed(j)}/S", "point": pid, "seed": seed(j), "dir": os.path.join(root, "stage0", pid, str(seed(j)), "S"),
         "seasons": MERGE, "cost": MERGE}]} for pid in blocks.all_ids() for j in CENSUS_SEEDS]


#: the anchor fallback's point with no Stage-1 S arm (launch adversary S2): W118-b, c0-p030-U-L, is not a Stage-1
#: point (Stage 1's L points are c = 1), so its fallback M and N need S 0-59 at seeds 129001-129008 to fork from
ANCHOR_NO_STAGE1 = "c0-p030-U-L"
ANCHOR_SEEDS = tuple(range(1, 9))


def anchor_units(root: str, stages: list) -> list:
    """S 0-59 at W118-b for the anchor-fallback seeds that neither the census (129001-129003) nor, when it runs, the
    pilot (129001-129004, whose ckpt60 is the same state) already makes.  They sit beside the census's own runs of the
    point (stage0/<point>/<seed>/S), which are exact fork sources."""
    have = set(CENSUS_SEEDS) | (set(PILOT_SEEDS) if "P" in stages else set())
    pid = ANCHOR_NO_STAGE1
    return [{"stage": "A", "seed": seed(j), "jobs": [
        {"job": "fresh", "name": f"A/{pid}/{seed(j)}/S", "point": pid, "seed": seed(j), "dir": os.path.join(root, "stage0", pid, str(seed(j)), "S"),
         "seasons": MERGE, "cost": MERGE}]} for j in ANCHOR_SEEDS if j not in have]


def units_for(stages: list, root: str) -> list:
    return ((pilot_units(root) if "P" in stages else []) + (census_units(root) if "0" in stages else [])
            + (anchor_units(root, stages) if "0" in stages else []))


def layout(units: list, hosts: int) -> list:
    """Lanes (host, lane) -> units, so that a session's two lanes hold different seeds (RBT-107's packing rule).

    Lane 0 of every session takes the odd seeds, lane 1 the even ones.  A seed of the other parity class's size
    imbalance (census seed 129003, with three census seeds) is split between the classes to balance their load; lane 0
    runs its share FIRST and lane 1 LAST, so the two never meet on it in practice.  Within a class, units go longest
    first onto the least-loaded lane.  The seed lock in ``run_lane`` makes the rule hard even if the lanes' pace drifts."""
    cost = lambda u: sum(j["cost"] for j in u["jobs"])
    cls = {0: [], 1: []}
    load = {0: 0, 1: 0}
    census_seeds = sorted({u["seed"] for u in units if u["stage"] == "0"})
    shared = census_seeds[-1] if len(census_seeds) % 2 else None
    for u in units:
        if u["seed"] != shared or u["stage"] != "0":
            k = 0 if (u["seed"] - blocks.SEED_BASE) % 2 else 1
            cls[k].append(u)
            load[k] += cost(u)
    for u in (u for u in units if u["seed"] == shared and u["stage"] == "0"):
        k = min((0, 1), key=lambda i: (load[i], i))
        u["shared"] = True
        cls[k].append(u)
        load[k] += cost(u)
    lanes = [[] for _ in range(2 * hosts)]
    for k in (0, 1):
        mine = list(range(k, 2 * hosts, 2))
        lload = {i: 0 for i in mine}
        for u in sorted(cls[k], key=lambda u: -cost(u)):
            i = min(mine, key=lambda i: (lload[i], i))
            lanes[i].append(u)
            lload[i] += cost(u)
    for i, lane in enumerate(lanes):
        first = i % 2 == 0  # lane 0 runs the shared seed first, lane 1 last
        lane.sort(key=lambda u: ((0 if first else 2) if u.get("shared") else 1, u["stage"] != "P", u["seed"]))
    return lanes


def core_h(arm_seasons: int) -> tuple:
    return tuple(arm_seasons * r / 3600 for r in CORE_S)


def plan(stages: list, hosts: int, root: str) -> dict:
    """Per stage: arm-seasons and core-h as ((lo, hi) at 20 core-s, (lo, hi) at 25), and per lane its load and wall."""
    units = units_for(stages, root)
    lanes = layout(units, hosts)
    out = {"stages": stages, "hosts": hosts, "lanes": [], "arm_seasons": {}, "core_h": {}}
    for st in stages + (["A"] if "0" in stages else []):
        s = sum(j["cost"] for u in units if u["stage"] == st for j in u["jobs"])
        arms = core_h(s)
        if st == "P":
            extra = tuple(len(blocks.PILOT) * len(PILOT_SEEDS) * p + len(blocks.PILOT) * PLANTED_POINT for p in PROBE_SEED)
        elif st == "A":
            extra = (0.0, 0.0)
        else:
            extra = PAYS_CORE_H
        out["core_h"][st] = {"arms": arms, "extra": extra, "total": tuple((a + extra[0], a + extra[1]) for a in arms)}
        out["arm_seasons"][st] = s
    for k, lane in enumerate(lanes):
        s = sum(j["cost"] for u in lane for j in u["jobs"])
        out["lanes"].append({"host": k // 2, "lane": k % 2, "units": len(lane), "arm_seasons": s,
                             "seeds": sorted({u["seed"] for u in lane}), "wall_h": tuple(s * r / 2 / 3600 for r in CORE_S)})
    return out


def print_plan(p: dict) -> None:
    print(f"# RBT-129 launch plan: stage(s) {','.join(p['stages'])} on {p['hosts']} x 4-core sessions, 2 lanes each at WORKERS = 2")
    print(f"# seeds: pilot {', '.join(str(seed(j)) for j in PILOT_SEEDS)} (N: odd holistic, even conventional; all 4 at the pilot);"
          f" census {', '.join(str(seed(j)) for j in CENSUS_SEEDS)}")
    if "P" in p["stages"]:
        print(f"# Stage P points: {', '.join(blocks.PILOT)}; per point x seed: S 0-299 (S60 + resume), M and N forked from the"
              f" season-60 state, 60-299; K1 per point on seed {seed(PILOT_SEEDS[0])} (straight 0-64 vs fork 60-64)")
    if "0" in p["stages"]:
        print(f"# Stage 0: {len(blocks.all_ids())} points x {len(CENSUS_SEEDS)} seeds, S 0-59; PAYS at {len(blocks.PAYS_CELLS)} cells"
              " (designed prize leg: pays-prize; the holistic plant and the nose-step legs: pays, guarded on steer.py and section B)")
    print("# stage  arm-seasons  arms at 20 / 25 core-s   + " + "probes, planted set (P) or PAYS cells (0)   = total at 20 | at 25   DESIGN 11.2 line")
    grand = [0.0, 0.0, 0.0, 0.0]
    for st in p["core_h"]:
        c = p["core_h"][st]
        (t20, t25), ((d20lo, d20hi), (d25lo, d25hi)) = c["total"], BUDGET[st]
        print(f"  {st:5s}  {p['arm_seasons'][st]:10d}   {c['arms'][0]:6.1f} / {c['arms'][1]:6.1f}        + {c['extra'][0]:.1f}-{c['extra'][1]:.1f}"
              f"                                 = {t20[0]:.1f}-{t20[1]:.1f} | {t25[0]:.1f}-{t25[1]:.1f}   {d20lo}-{d20hi} | {d25lo}-{d25hi}")
        grand = [grand[0] + t20[0], grand[1] + t20[1], grand[2] + t25[0], grand[3] + t25[1]]
    if "P" in p["stages"]:
        print("  (P is above its r4 line by N at full cost, 16 x 240 arm-seasons where r4's prior_regime.py counts 0.85 x, +3.2"
              " core-h at 20 core-s; and K1's straight run to 65 plus its fork, 4 x 70 arm-seasons, +1.6. The planted set was in r4)")
    if "0" in p["stages"]:
        print(f"  (A: S 0-59 at {ANCHOR_NO_STAGE1} for the anchor fallback's seeds the census and pilot do not make; charged to the"
              " fallback's 46-57 core-h, not to Stage 0)")
    (t20, t25), (a20, a25) = BUDGET["total"], BUDGET["anchor fallback"]
    print(f"# these stages: {grand[0]:.1f}-{grand[1]:.1f} core-h at 20 core-s, {grand[2]:.1f}-{grand[3]:.1f} at 25")
    print(f"# the programme: DESIGN total {t20[0]:,}-{t25[1]:,} + the adopted anchor fallback {a20[0]}-{a25[1]} ="
          f" {t20[0] + a20[0]:,}-{t25[1] + a25[1]:,} core-h (the brief's envelope: {BRIEF_ENVELOPE[0]:,}-{BRIEF_ENVELOPE[1]:,})")
    print("# host lane  units  seeds                          arm-seasons  wall h at 20 / 25 core-s (WORKERS = 2)")
    for ln in p["lanes"]:
        seeds = ",".join(str(x) for x in ln["seeds"])
        print(f"  {ln['host']:4d} {ln['lane']:4d}  {ln['units']:5d}  {seeds:29s}  {ln['arm_seasons']:11d}  {ln['wall_h'][0]:5.1f} / {ln['wall_h'][1]:5.1f}")
    walls = [ln["wall_h"] for ln in p["lanes"]]
    print(f"# wall time (the longest lane): {max(w[0] for w in walls):.1f} to {max(w[1] for w in walls):.1f} h, before probes and PAYS;"
          " jobs chain back to back (no job waits on durable.sh: L4)")


# -- emit --------------------------------------------------------------------------------------------------------- #

PATH_KEYS = ("dir", "src", "ref", "worlds")


def rel(path: str) -> str:
    """A path as the lane files store it: relative to the repository root, and inside it (launch adversary S9)."""
    r = os.path.relpath(os.path.abspath(path), ROOT)
    if r.startswith(".."):
        raise SystemExit(f"REFUSED: {path} is outside the repository")
    return r


def absolute(path: str) -> str:
    if os.path.isabs(path) or path.startswith(".."):
        raise SystemExit(f"REFUSED: a lane path must be relative to the repository root and inside it: {path}")
    return os.path.join(ROOT, path)


def emit(stages: list, hosts: int, root: str, fair: list, eat: list) -> list:
    check_fair(fair)
    check_eat(eat)
    check_surface_clearance(eat)
    units = units_for(stages, root)
    lanes = layout(units, hosts)
    points = sorted({j["point"] for u in units for j in u["jobs"] if "point" in j})
    for pid in points:  # L1: every block under the ruled set, checked before anything is written
        check_block(blocks.block(pid, fair=fair, eat=eat))
    worlds = os.path.join(root, "worlds")
    blocks.export(worlds, points, fair=fair, eat=eat)
    # S11: a real config.json per PAYS cell (and per pilot point, for the planted set), beside the blocks
    world_config_dirs(root, sorted(set(blocks.PAYS_CELLS if "0" in stages else ()) | set(blocks.PILOT if "P" in stages else ())), fair, eat)
    lane_dir = os.path.join(root, "lanes", "-".join(stages))
    os.makedirs(lane_dir, exist_ok=True)
    with open(os.path.join(lane_dir, "launch.txt"), "w") as f:
        f.write(f"# RBT-129 launch record: stages {','.join(stages)}\ncommit {_git('rev-parse', 'HEAD')}\n"
                + "".join(f"tree:{t} {_git('rev-parse', f'HEAD:{t}')}\n" for t in PINNED_TREES)
                + f"fair {' '.join(fair)}\neat {' '.join(eat)}\nemitted {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
    paths = []
    for k, lane in enumerate(lanes):
        path = os.path.join(lane_dir, f"host{k // 2}-lane{k % 2}.jsonl")
        with open(path, "w") as f:
            for u in lane:
                for j in u["jobs"]:
                    j = {**j, "worlds": worlds}
                    f.write(json.dumps({k: (rel(v) if k in PATH_KEYS else v) for k, v in j.items()}) + "\n")
        paths.append(path)
    return paths


# -- run ---------------------------------------------------------------------------------------------------------- #

def _done(d: str, tag: str) -> bool:
    return os.path.exists(os.path.join(d, f".rbt129-done-{tag}"))


def _mark(d: str, tag: str, note: str = "") -> None:
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f".rbt129-done-{tag}"), "w") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + (f" {note}" if note else "") + "\n")


#: a unit whose S went fully extinct before the merge (fix1): ``<unit>/EXTINCT.txt``.  ``Ecology.run`` stops, exit 0,
#: when every population is empty ("everyone died"), so S60 is done at the extinction season.  That is a registered
#: outcome (DESIGN M2: pre-merge extinction, a survival call), not a lost checkpoint; the unit has no season-60 state,
#: so its resume, M, N, K1 fork and K1 are skipped.
EXTINCT = "EXTINCT.txt"


def _unit(job: dict) -> str:
    """A pilot chain's unit directory (``stageP/<point>/<seed>``), from any of its jobs."""
    return os.path.dirname(job["src"] if job["job"] in ("snapshot", "fork") else job["dir"])


def extinct_season(unit: str):
    """The season at which the unit's S went fully extinct before the merge, or None."""
    path = os.path.join(unit, EXTINCT)
    if not os.path.exists(path):
        return None
    return int(open(path).readline().split("season ")[1].split()[0].rstrip(":"))


#: jobs of fewer arm-seasons than this get no periodic snapshot: they rerun in minutes, and every snapshot makes a
#: checkpoint branch that sessions cannot delete (launch adversary L4)
DURABLE_MIN = 120


#: every durable save on this machine takes this lock, so saves never run at once (in-lane ``_save`` failed silently for
#: most of Stage P while manual serial sweeps succeeded), and logs its outcome to ``DURABLE_LOG``
DURABLE_LOCK = "/tmp/rbt129-durable.lock"
DURABLE_LOG = os.path.join(RUNS, "durable.log")
#: minutes between a long job's periodic snapshots
DURABLE_EVERY = 20


def _stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


#: seconds a save may take before it is killed (#465 adversary M-2): a hung push must never hold the lock
DURABLE_TIMEOUT = 900


def save_now(d: str, label: str = None, retries: int = 1) -> int:
    """One snapshot of ``d`` to ``ckpt/<label>``, now and serialized (``DURABLE_LOCK``); its exit code and durable.sh's
    output go to ``DURABLE_LOG``, written under the lock (never /dev/null).  A save that runs past ``DURABLE_TIMEOUT``
    is killed with its whole process group (the push included) and logged as ``exit timeout``, so the lock is always
    released.  A failure is retried once after 30 s, then warned on stderr with the label and exit code only (no-peek:
    the log's progress line stays in the file)."""
    import signal

    label = label or _label(d)
    limit = float(os.environ.get("DURABLE_TIMEOUT_S", DURABLE_TIMEOUT))
    code = 0
    for attempt in range(retries + 1):
        with open(DURABLE_LOCK, "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                proc = subprocess.Popen([os.path.join(ROOT, "scripts", "durable.sh"), "save", d, label], cwd=ROOT,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
                try:
                    out, _ = proc.communicate(timeout=limit)
                    code = proc.returncode
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    out, _ = proc.communicate()
                    code = "timeout"
                os.makedirs(os.path.dirname(DURABLE_LOG), exist_ok=True)
                with open(DURABLE_LOG, "a") as log:
                    log.write(f"{_stamp()} save ckpt/{label} {rel_or_abs(d)} exit {code}\n"
                              + "".join(f"    {x}\n" for x in (out or "").splitlines()))
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)
        if code == 0:
            return 0
        if attempt < retries:
            time.sleep(float(os.environ.get("DURABLE_RETRY_S", "30")))
    print(f"WARN: durable save ckpt/{label} failed (exit {code}; see {rel_or_abs(DURABLE_LOG)})", file=sys.stderr, flush=True)
    return 1 if code == "timeout" else code


def rel_or_abs(path: str) -> str:
    r = os.path.relpath(os.path.abspath(path), ROOT)
    return path if r.startswith("..") else r


def _save(d: str, label: str = None):
    """One snapshot, in the background: the lane goes on to its next job at once (L4).  A non-daemon thread, so the
    process does not exit before the save is done; ``save_now`` serializes and logs it.  Returns the thread."""
    if os.environ.get("NO_DURABLE"):
        return None
    t = threading.Thread(target=save_now, args=(d, label), name=f"save {label or _label(d)}")
    t.start()
    return t


def _every(d: str, label: str, stop: threading.Event) -> None:
    """A long job's periodic snapshots, serialized with every other save, until its run exits.  Its thread is not a
    daemon (#465 adversary S-2): once stopped it ends after the save it is in, which is then logged; a save is bounded
    by ``DURABLE_TIMEOUT``, so the process can always exit."""
    while not stop.wait(float(os.environ.get("DURABLE_EVERY_S", DURABLE_EVERY * 60))):
        save_now(d, label, retries=0)


def _ecology(cmd: list, d: str, label: str, long: bool = False) -> None:
    """Run one ecology command.  Never waits on a save (L4): a long job's periodic snapshots run in a thread beside the
    run, through the serialized ``save_now``, and stop when the run exits; the job's final save goes to the background."""
    workers = os.environ.get("WORKERS", "2")
    full = [sys.executable, "-m", "rabbitstew.cli", "ecology", *cmd, "--workers", workers, "--out", d]
    with open(os.path.join(d, "command.txt"), "a") as f:
        f.write(" ".join(full) + "\n")
    with open(os.path.join(d, "run.log"), "a") as log:
        proc = subprocess.Popen(full, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        stop = threading.Event()
        try:
            if long and not os.environ.get("NO_DURABLE"):
                threading.Thread(target=_every, args=(d, label, stop), name=f"every {label}").start()
            code = proc.wait()
        finally:
            stop.set()
    if code:
        raise SystemExit(f"{label}: ecology exited {code} (see {d}/run.log)")


def _label(d: str) -> str:
    """One checkpoint branch per run directory (``ckpt/rbt-129-<path under runs/RBT-129>``), whichever job writes it."""
    rel = os.path.relpath(os.path.abspath(d), RUNS)
    return "rbt-129-" + rel.replace(os.sep, "-")


def _restore(d: str, probe: str = "state.json") -> None:
    """A directory lost with its container comes back from its latest snapshot (done-markers included)."""
    if not os.environ.get("NO_DURABLE") and not os.path.exists(os.path.join(d, probe)):
        subprocess.run([os.path.join(ROOT, "scripts", "durable.sh"), "restore", d, _label(d)], cwd=ROOT, capture_output=True)


#: a pilot unit's own files (``EXTINCT.txt``, ``K1.txt`` and the snapshot job's ``UNIT.txt``) sit in the unit
#: directory, which no run directory's branch holds; each is mirrored into ``<unit>/record/``, saved to its own branch
#: (``ckpt/rbt-129-stageP-<point>-<seed>-record``), and restored from it
RECORD = "record"
UNIT = "UNIT.txt"


def unit_file(unit: str, name: str, text: str) -> None:
    """Write a unit's file, beside the unit's runs and in its record, and save the record (in the background)."""
    rec = os.path.join(unit, RECORD)
    os.makedirs(rec, exist_ok=True)
    for path in (os.path.join(unit, name), os.path.join(rec, name)):
        with open(path, "w") as f:
            f.write(text)
    _save(rec)


def restore_record(unit: str) -> None:
    """Bring back a unit's record (a reclaimed container), and its files into the unit directory where missing."""
    rec = os.path.join(unit, RECORD)
    if not os.path.isdir(rec):
        _restore(rec, UNIT)
    if os.path.isdir(rec):
        for name in os.listdir(rec):
            if not os.path.exists(os.path.join(unit, name)):
                shutil.copy2(os.path.join(rec, name), os.path.join(unit, name))


def fork_config(src: str, dst: str, settings: dict) -> None:
    """Copy S's checkpoint directory and set the merge (and null) in its config.json's ecology section (RBT-130 README)."""
    shutil.copytree(src, dst)
    for tag in os.listdir(dst):
        if tag.startswith(".rbt129-done-"):
            os.remove(os.path.join(dst, tag))
    path = os.path.join(dst, "config.json")
    cfg = json.load(open(path))
    cfg["ecology"].update(settings)
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)


#: what K1 does not compare (launch adversary S3): the fork rewrites config.json; the rest is provenance and logs.
#: r4's ``seasons.txt`` is taken as ``history.json`` (the ecology writes no seasons.txt)
K1_SKIP = ("config.json", "platform.json", "command.txt", "run.log", "durable.log")


def output_files(d: str) -> dict:
    out = {}
    for base, _, files in os.walk(d):
        for n in files:
            if n in K1_SKIP or n.startswith(".rbt129-done-"):
                continue
            path = os.path.join(base, n)
            out[os.path.relpath(path, d)] = path
    return out


def k1_compare(ref: str, fork: str) -> tuple:
    """(verdict, lines): every output file of the straight run against the fork's, byte for byte (genomes, state.json,
    lineage, cohorts, history)."""
    a, b = output_files(ref), output_files(fork)
    lines = [f"only in {'straight' if n in a else 'fork'}: {n}" for n in sorted(set(a) ^ set(b))]
    for n in sorted(set(a) & set(b)):
        if open(a[n], "rb").read() != open(b[n], "rb").read():
            lines.append(f"DIFFERS: {n}")
    return ("PASS" if not lines else "FAIL"), [f"{len(set(a) & set(b))} files compared"] + lines


def _clear_final(d: str) -> None:
    """Before a resume: drop ``<label>/final/``.  The ecology writes it only when a run ends, one file per member, and
    never clears it, so a resumed or forked run whose population shrank would keep the earlier run's surplus members
    there (found by K1's every-file comparison, S3); a probe reading final/ would then sample the dead."""
    for name in os.listdir(d):
        f = os.path.join(d, name, "final")
        if os.path.isdir(f):
            shutil.rmtree(f)


def _resume(job: dict, d: str, long: bool) -> None:
    _clear_final(d)
    _ecology(["--resume", "--seasons", str(job["seasons"])], d, _label(d), long)


def run_job(job: dict) -> None:
    """One job; its paths are absolute here (``run_lane`` resolves the lane file's relative ones).  Every job that runs
    ends with its done-marker and a save of its directory (K1 included, on both its paths); a pilot unit's own files go
    to its record (``unit_file``)."""
    kind, d, tag = job["job"], job["dir"], job["name"].split("/")[-1]
    long = job.get("cost", 0) >= DURABLE_MIN
    pilot = job["name"].startswith("P/")
    if pilot:
        restore_record(_unit(job))
    _restore(d)
    if _done(d, tag):
        return
    if kind == "fresh":
        if os.path.exists(os.path.join(d, "state.json")):
            if any(len(m) for m in json.load(open(os.path.join(d, "state.json")))["populations"].values()):
                _resume(job, d, long)  # fix1b: an emptied run (killed before its marker) is done as it stands
        else:
            if os.path.isdir(d):
                shutil.rmtree(d)  # never finished a season: nothing of it is kept (lineage.jsonl appends)
            os.makedirs(d)
            b = json.load(open(os.path.join(job["worlds"], f"{job['point']}.json")))
            check_fair(b["fair"] or [])
            _ecology([*b["argv"], "--seed", str(job["seed"]), "--seasons", str(job["seasons"])], d, _label(d), long)
    elif kind == "snapshot":  # the season-60 state, kept apart (and saved) before S continues
        state = json.load(open(os.path.join(job["src"], "state.json")))
        at = state["season"]
        unit = _unit(job)
        if at <= job.get("season", MERGE) and all(len(m) == 0 for m in state["populations"].values()):  # fix1b: <=
            unit_file(unit, EXTINCT, f"EXTINCT pre-merge at season {at}: S's state.json has every population empty (both faunas extinct;"
                      f" the ecology stopped, 'everyone died'), before the fork's season {job.get('season', MERGE)}.\n"
                      "The unit's S resume, M, N, K1 fork and K1 are skipped (lane fix1). DESIGN M2: a survival call.\n")
            unit_file(unit, UNIT, f"unit {os.path.relpath(unit, RUNS)}: S60 done; extinct pre-merge ({EXTINCT})\n")
            _mark(d, tag, f"skipped: extinct pre-merge at season {at}")
        else:
            if at != job.get("season", MERGE):
                raise SystemExit(f"{job['name']}: {job['src']} is at season {at}, not the fork's {job.get('season', MERGE)};"
                                 " the checkpoint is lost and S must be re-run from 0 to rebuild it")
            if os.path.isdir(d):
                shutil.rmtree(d)
            fork_config(job["src"], d, {})
            unit_file(unit, UNIT, f"unit {os.path.relpath(unit, RUNS)}: S60 done; season-{at} checkpoint taken (ckpt60)\n")
            _mark(d, tag)
        _save(d)
        return
    elif kind in ("resume", "fork", "k1") and extinct_season(_unit(job)) is not None:
        s = extinct_season(_unit(job))  # no-peek: recorded in the unit's files only, never printed to the runner's log
        note = f"skipped: extinct pre-merge at season {s}"
        if kind == "k1":
            unit_file(_unit(job), "K1.txt", f"K1 UNTESTABLE (extinct pre-merge at season {s}): this unit has no season-60 state to fork\n")
            note += "; K1 UNTESTABLE"  # S-3: the verdict rides K1fork's own branch too
        _mark(d, tag, note)
        _save(d)
        return
    elif kind == "resume":
        _resume(job, d, long)
    elif kind == "fork":
        if not os.path.exists(os.path.join(d, "state.json")):
            if os.path.isdir(d):
                shutil.rmtree(d)
            _restore(job["src"])
            fork_config(job["src"], d, job["set"])
        _resume(job, d, long)
    elif kind == "k1":
        verdict, lines = k1_compare(job["ref"], d)
        unit_file(_unit(job), "K1.txt", f"K1 {verdict}: every output file of a straight run to season {K1_SEASONS} against the fork of the"
                  f" season-60 state with the merge unset (config.json, platform.json and logs excluded)\n"
                  + "".join(f"  {x}\n" for x in lines))
        print(f"{job['name']}: K1 {verdict}")  # the control's verdict, not an outcome
        _mark(d, tag, f"K1 {verdict}")  # S-3: the verdict line rides K1fork's own branch
        _save(d)
        return
    else:
        raise ValueError(f"unknown job {kind}")
    _mark(d, tag)
    _save(d)  # every job, short ones included: the marker reaches the snapshot, so a restored run is not re-run


def check_lane_blocks(jobs: list, launch: dict) -> None:
    """L1: every fresh job's world file must be the block ``blocks.py`` builds from launch.txt's fairness and eating
    flags, and that block must be under the ruled set; a hand-edited argv or block is refused."""
    fair, eat = launch["fair"].split(), launch["eat"].split()
    check_fair(fair)
    check_eat(eat)
    check_surface_clearance(eat)
    for pid in sorted({j["point"] for j in jobs if j["job"] == "fresh"}):
        wpath = next(os.path.join(j["worlds"], f"{pid}.json") for j in jobs if j.get("point") == pid)
        rebuilt = json.loads(json.dumps(blocks.block(pid, fair=fair, eat=eat)))
        if json.load(open(wpath)) != rebuilt:
            _refuse(f"{wpath} is not the block launch.txt's flags build for {pid}; re-emit", 4)
        check_block(rebuilt)


def run_lane(path: str) -> None:
    launch = read_launch(os.path.join(os.path.dirname(os.path.abspath(path)), "launch.txt"))
    check_host(launch)
    jobs = [json.loads(line) for line in open(path) if line.strip()]
    jobs = [{k: (absolute(v) if k in PATH_KEYS else v) for k, v in j.items()} for j in jobs]
    check_lane_blocks(jobs, launch)
    os.makedirs(LOCKS, exist_ok=True)
    for job in jobs:
        with open(os.path.join(LOCKS, f"seed-{job['seed']}.lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)  # a session's two lanes never run one seed at once (RBT-107's packing)
            t0 = time.time()
            print(f"{time.strftime('%H:%M:%S')} start {job['name']}", flush=True)
            run_job(job)
            print(f"{time.strftime('%H:%M:%S')} done  {job['name']} ({(time.time() - t0) / 60:.1f} min)", flush=True)
            fcntl.flock(lock, fcntl.LOCK_UN)
    print(f"lane {os.path.basename(path)} complete: {len(jobs)} jobs")


# -- the readout-side check: every run directory and unit has a branch -------------------------------------------- #

def expected_branches(lane_paths: list) -> dict:
    """{label: directory}: every run directory a lane file's jobs write, and every pilot unit's record."""
    out = {}
    for path in lane_paths:
        for line in open(path):
            if not line.strip():
                continue
            j = json.loads(line)
            d = absolute(j["dir"])
            out[_label(d)] = d
            if j["name"].startswith("P/"):
                rec = os.path.join(_unit({**j, "dir": d, **({"src": absolute(j["src"])} if "src" in j else {})}), RECORD)
                out[_label(rec)] = rec
    return out


def remote_ckpt() -> set:
    """The ``ckpt/rbt-129-*`` labels the remote holds."""
    r = subprocess.run(["git", "ls-remote", "--heads", "origin", "refs/heads/ckpt/rbt-129-*"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        _refuse(f"git ls-remote failed (exit {r.returncode}): {r.stderr.strip()}", 7)
    return {line.split("refs/heads/ckpt/", 1)[1] for line in r.stdout.splitlines() if "refs/heads/ckpt/" in line}


def check_branches(lane_paths: list, save: bool = False) -> int:
    """Print every expected branch the remote lacks; with ``save``, first backfill each missing unit record from this
    machine's unit files (``backfill_record``), then snapshot (serially) each missing one whose directory is here, and
    check again.  Exit 1 while any is missing.  Prints labels and counts only (no-peek).

    **K1's verdict** for a unit (#465 ruling, M-1) is read, in order, from: the unit record's K1.txt; K1fork's
    done-marker note (``.rbt129-done-K1``, on K1fork's branch; new code); the ``ckpt/rbt-129-stageP-<point>-129001-unit``
    branches that Stage P hosts saved by hand, where present (their K1.txt); otherwise it is recomputed with
    ``k1_compare`` on K1ref and K1fork restored from their branches."""
    want = expected_branches(lane_paths)
    have = remote_ckpt()
    missing = sorted(k for k in want if k not in have)
    if save and missing:
        for k in missing:
            d = want[k]
            if os.path.basename(d) == RECORD and not os.path.isdir(d):
                backfill_record(os.path.dirname(d))
            if os.path.isdir(d):
                save_now(d, k)
        have = remote_ckpt()
        missing = sorted(k for k in want if k not in have)
    for k in missing:
        print(f"MISSING ckpt/{k}  ({rel_or_abs(want[k])}{'' if os.path.isdir(want[k]) else '; not on this machine'})")
    print(f"{len(want) - len(missing)} of {len(want)} run directories and unit records have a checkpoint branch")
    return 1 if missing else 0


def set_repo(repo: str) -> None:
    """``--repo DIR``: resolve lane paths, labels and durable.sh against another checkout (a Stage P session's, pinned
    at its launch commit), not this one."""
    global ROOT, RUNS
    ROOT = os.path.abspath(repo)
    RUNS = os.path.join(ROOT, "runs", "RBT-129")


# -- the steer.py-dependent steps --------------------------------------------------------------------------------- #

CKPT60_MARK = ".rbt129-done-ckpt60"


def branch_file(label: str, member: str):
    """One file's text from ``ckpt/<label>``'s latest snapshot, without restoring the directory (the tarball is read in
    memory), or None when the branch or the file is absent.  Reads nothing but that file."""
    import io
    import tarfile

    if os.environ.get("NO_DURABLE"):
        return None
    ref = f"refs/remotes/origin/ckpt/{label}"
    run = lambda *a, **k: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, timeout=600, **k)
    if run("fetch", "-q", "origin", f"+refs/heads/ckpt/{label}:{ref}").returncode:
        return None
    name = run("show", f"{ref}:MANIFEST", text=True).stdout.split("\n")[0]
    parts = sorted(x for x in run("ls-tree", "--name-only", ref, text=True).stdout.split() if x.startswith("run.tar.gz.part"))
    data = b"".join(run("cat-file", "blob", f"{ref}:{p}").stdout for p in parts)
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            f = tar.extractfile(f"{name}/{member}")
            return f.read().decode() if f else None
    except (KeyError, tarfile.TarError):
        return None


def _from_marker(text: str) -> str:
    """ckpt60's done-marker, written in the snapshot job's own save with the skip decision: ``skipped: extinct
    pre-merge at season N`` for an extinct unit, a bare timestamp for a live one."""
    return "extinct" if "skipped: extinct pre-merge" in text else "alive"


def unit_status(unit: str):
    """"extinct", "alive" or None (not known).  Read at emit time, after Stage P is DONE, in this order: the unit's
    record (restored from its branch); its local ckpt60 done-marker; **that marker read from ckpt60's own branch**
    (#465 adversary M-1: every unit Stage P ran saved its ckpt60 directory, marker included, whatever its code, so the
    status never depends on a container that may be gone)."""
    restore_record(unit)
    if os.path.exists(os.path.join(unit, EXTINCT)):
        return "extinct"
    mark = os.path.join(unit, "ckpt60", CKPT60_MARK)
    if os.path.exists(mark):
        return _from_marker(open(mark).read())
    if os.path.exists(os.path.join(unit, UNIT)):
        return "extinct" if "extinct" in open(os.path.join(unit, UNIT)).read() else "alive"
    text = branch_file(_label(os.path.join(unit, "ckpt60")), CKPT60_MARK)
    return None if text is None else _from_marker(text)


def backfill_record(unit: str) -> bool:
    """A unit Stage P ran before records existed (#465 adversary M-1): write ``<unit>/record/`` from what this machine
    holds (the unit's EXTINCT.txt and K1.txt, and a UNIT.txt from ckpt60's done-marker).  False when there is no
    marker here to derive it from.  Never overwrites the unit's own files."""
    mark = os.path.join(unit, "ckpt60", CKPT60_MARK)
    if not os.path.exists(mark):
        return False
    rec = os.path.join(unit, RECORD)
    os.makedirs(rec, exist_ok=True)
    for name in (EXTINCT, "K1.txt"):
        if os.path.exists(os.path.join(unit, name)):
            shutil.copy2(os.path.join(unit, name), os.path.join(rec, name))
    st = _from_marker(open(mark).read())
    with open(os.path.join(rec, UNIT), "w") as f:
        f.write(f"unit {os.path.relpath(unit, RUNS)}: S60 done; "
                + (f"extinct pre-merge ({EXTINCT})" if st == "extinct" else "season-60 checkpoint taken (ckpt60)")
                + "; backfilled from ckpt60's done-marker\n")
    return True


def _hosts(line: str, hosts: str) -> str:
    """RBT132.md's templates name the hosts root ``HOSTS_ROOT``: the leg's restored RBT-113 O1 root."""
    return line.replace("HOSTS_ROOT", hosts)


DONE_JOB = ".rbt129-done-job"


def _guarded(d: str, cmd: str, after: str = "", on_fail: str = "exit 1") -> str:
    """One resumable job line writing into ``d``: skipped when ``d`` holds its done-marker; its stdout and stderr go to
    files in ``d`` (no-peek: nothing it prints reaches the runner's log); on failure it prints only ``d`` and the exit
    code, then ``on_fail``; on success ``after`` runs and the marker is written; either way ``d`` is saved to its own
    branch (``stages.py save``: serialized and logged)."""
    save = f"python runs/RBT-129/launch/stages.py save {d}"
    return (f'mkdir -p {d}; if [ ! -e {d}/{DONE_JOB} ]; then rc=0; {cmd} > {d}/stdout.txt 2> {d}/stderr.txt || rc=$?;'
            f' if [ $rc -ne 0 ]; then echo "FAILED: {d} (exit $rc)" >&2; {save}; {on_fail};'
            f' else {after + "; " if after else ""}touch {d}/{DONE_JOB}; {save}; fi; fi')


def restore_runs(dirs: list) -> list:
    """Script lines that restore run directories a leg reads (a pilot unit's S) where missing, and refuse (exit 7) if
    one cannot be had.  durable.sh's output (its progress line) goes to the durable log, never the runner's (no-peek)."""
    log = rel(DURABLE_LOG)
    out = []
    for d in dirs:
        out.append(f"[ -f {d}/state.json ] || scripts/durable.sh restore {d} {_label(os.path.join(ROOT, d))} >> {log} 2>&1 || true")
        out.append(f'[ -f {d}/state.json ] || {{ echo "REFUSED: {d} missing (ckpt/{_label(os.path.join(ROOT, d))})" >&2; exit 7; }}')
    return out


def probe_jobs(root: str, template: str, planted: str, hosts: str = "runs/RBT-129/hosts113") -> tuple:
    """Stage P's probes (DESIGN 5.3(c), (e)), as (job lines, extinct units, the S directories read, output dirs).  Per point, **the planted set first**
    (RBT132.md (i): the probes read the battery it writes; ``planted``: point, world, config, config_json, out), then
    per seed 20 members per fauna at seasons 0 and 300, 8 draws, the RNG 129300 + j (``template``: run, season, seed,
    rng, point, out).  **A unit extinct pre-merge is skipped**, both seasons (RBT132.md (iv); DESIGN M2: it has no
    season-300 S), and returned; a unit whose status is not known here is refused (exit 7)."""
    out, extinct, unknown, runs, dirs = [], [], [], [], []
    for pid in blocks.PILOT:
        cdir = os.path.join(root, "worlds", "config", pid)
        po = rel(os.path.join(root, "stageP", pid, "planted"))
        dirs.append(po)
        out.append(_guarded(po, _hosts(planted.format(
            point=pid, world=rel(os.path.join(root, "worlds", f"{pid}.json")), config=rel(cdir),
            config_json=rel(config_json_path(root, pid)), out=po), hosts)))
        for j in PILOT_SEEDS:
            unit = os.path.join(root, "stageP", pid, str(seed(j)))
            st = unit_status(unit)
            if st is None:
                unknown.append(rel(unit))
                continue
            if st == "extinct":
                extinct.append(rel(unit))
                continue
            runs.append(rel(os.path.join(unit, "S")))
            for season in (0, SEASONS):
                o = rel(os.path.join(unit, f"probes-{season}"))
                dirs.append(o)
                out.append(_guarded(o, _hosts(template.format(
                    run=rel(os.path.join(unit, "S")), season=season, seed=seed(j), rng=129300 + j, point=pid, out=o), hosts)))
    if unknown:
        _refuse("these pilot units' status (extinct pre-merge or not) is not on this machine or a record branch; restore"
                " them (or run check-branches --save where Stage P ran) before emitting the probes: " + ", ".join(unknown), 7)
    return out, extinct, runs, dirs


#: RBT-125 section A's designed hosts (run_gate.sh SEEDS: BODIES_ROOT/forage-SEED, restored from ckpt/rbt-90-SEED)
PRIZE_HOSTS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def config_json_path(root: str, pid: str) -> str:
    """A point's real config.json (launch adversary S11): ``worlds/<id>.config.json``, what steps.py --config reads."""
    return os.path.join(root, "worlds", f"{pid}.config.json")


def world_config_dirs(root: str, ids, fair: list, eat: list) -> dict:
    """Per point, the block's config.json, written twice from ``blocks.config_dict``: as ``worlds/<id>.config.json``
    (steps.py --config; S11) and as ``worlds/config/<id>/config.json`` (a directory, which RBT-103's harness takes by
    --config-from).  Every block is checked first (L1)."""
    out = {}
    for pid in ids:
        check_block(blocks.block(pid, fair=fair, eat=eat))
        text = json.dumps(blocks.config_dict(blocks.world_argv(pid, fair=fair, eat=eat)), indent=2)
        d = os.path.join(root, "worlds", "config", pid)
        os.makedirs(d, exist_ok=True)
        for path in (config_json_path(root, pid), os.path.join(d, "config.json")):
            with open(path, "w") as f:
                f.write(text)
        out[pid] = d
    return out


def _promote(out: str, o: str, marker: str, cmd: str) -> str:
    """One resumable job: skipped if its output already holds ``marker``; promoted (mv) only when the run exits 0 with
    it (run_gate.sh's ``promote``); then the cell's output directory is snapshotted to its own checkpoint branch, so a
    reclaimed container does not redo it (legs adversary S-3).  A failed save warns and goes on."""
    return (f"mkdir -p {out}; if ! grep -q '{marker}' {o} 2>/dev/null; then ({cmd} > {o}.tmp 2> {o}.err"
            f" && grep -q '{marker}' {o}.tmp && mv {o}.tmp {o}) || {{ echo \"FAILED: {o}\" >&2; exit 1; }};"
            f" scripts/durable.sh save {out} {_label(os.path.join(ROOT, out))} >&2 || echo \"WARN: durable save of {out} failed\" >&2; fi")


def restore_outputs(outs: list) -> list:
    """Script lines that bring back a cell's promoted outputs from its checkpoint branch, where the directory is missing
    (a reclaimed container); no branch yet is fine."""
    return [f"[ -e {out} ] || scripts/durable.sh restore {out} {_label(os.path.join(ROOT, out))} >&2 2>/dev/null || true" for out in outs]


def prize_jobs(root: str, bodies: str, procs: int = 4) -> dict:
    """Stage 0's designed PAYS prize leg (DESIGN 5.1: "RBT-106's prize at a = 6"), as RBT-125's gate ran it
    (run_gate.sh ``prize``: --w 3 is a = 6; **--decoy 3 at the PW cells, exactly where the registered harness has it**,
    legs adversary L-2), under the sweep's block (``worlds/config/<id>/``), per cell and designed host.  Returns
    {cell: (output dir, job lines)}; paths are repository-relative (S9)."""
    gate = "runs/RBT-125/gate/prize_gate.py"
    out = {}
    for pid in blocks.PAYS_CELLS:
        d = rel(os.path.join(root, "stage0", "pays", pid, "prize"))
        cfg = rel(os.path.join(root, "worlds", "config", pid))
        decoy = " --decoy 3" if blocks.parse_id(pid)[2] == "PW" else ""
        out[pid] = (d, [_promote(d, f"{d}/{s}.txt", "^ROW", f"python {gate} --run {bodies}/forage-{s} --config-from {cfg}"
                                 f" --label {s}-{pid} --w 3{decoy} --procs {procs}") for s in PRIZE_HOSTS])
    return out


def restore_hosts(bodies: str) -> list:
    """Script lines that fetch RBT-125's ten designed hosts (ckpt/rbt-90-SEED, about 86 MB each) where they are missing,
    and refuse (exit 7) if one cannot be had."""
    out = []
    for s in PRIZE_HOSTS:
        d = f"{bodies}/forage-{s}"
        out.append(f"[ -f {d}/state.json ] || scripts/durable.sh restore {d} rbt-90-{s} >&2")
        out.append(f'[ -f {d}/state.json ] || {{ echo "REFUSED: host {d} missing (ckpt/rbt-90-{s})" >&2; exit 7; }}')
    return out


def step_jobs(root: str, hosts: str, procs: int = 4, cells=None, sub: str = "steps", extra: str = "") -> dict:
    """Stage 0's designed nose-step leg (DESIGN 5.1: "a nose step against a +25% speed step on real designed hosts"):
    RBT-125 section B's harness (steps.py, #437), unchanged, on its registered hosts (RBT-113 O1's 15 designed finals,
    ``hosts(HOSTS_ROOT)``) and seeds (128 from 125000).  Its world is the cell's **verified** config directory
    ``worlds/config/<id>`` (``--config`` takes a directory), the file ``verify`` rebuilds and checks (legs adversary
    L-1); steps.py also checks the fairness marker (S12).  Returns {cell: (output dir, job lines)}.

    ``cells``, ``sub`` and ``extra`` make the re-measurement (``STEPS2``): its cells, its own output directory (and so
    its own checkpoint branch) and its registered flags."""
    out = {}
    for pid in (blocks.PAYS_CELLS if cells is None else cells):
        d = rel(os.path.join(root, "stage0", "pays", pid, sub))
        cfg = rel(os.path.join(root, "worlds", "config", pid))
        out[pid] = (d, [_promote(d, f"{d}/designed.txt", "^STEP", f"python runs/RBT-125/gate/steps.py {hosts} {pid} --config {cfg} --procs {procs}"
                                 + (f" {extra}" if extra else ""))])
    return out


#: the steps leg's re-measurement at c >= 1 (the coordinator's ruling on #467, comment 5870339780): the 12 PAYS cells at
#: c1 and c2, on 128 fresh seeds from 126000, the same hosts, verified configs and flags, with steps.py's
#: --exclude-exploded (#475); outputs in stage0/pays/<cell>/steps2, saved to ckpt/rbt-129-stage0-pays-<cell>-steps2
STEPS2_CELLS = tuple(p for p in blocks.PAYS_CELLS if blocks.parse_id(p)[0] != blocks.parse_id("c0-p030-U-L")[0])
STEPS2_SEED0 = 126000
STEPS2_FLAGS = f"--seed0 {STEPS2_SEED0} --exclude-exploded"


def restore_step_hosts(hosts: str) -> list:
    """Script lines that fetch RBT-113 O1 (ckpt/rbt-113-O1, about 35 MB) into HOSTS_ROOT/O1 where missing (exit 7)."""
    d = f"{hosts}/O1"
    return [f"[ -f {d}/1/U/conventional/final/000.json ] || scripts/durable.sh restore {d} rbt-113-O1 >&2",
            f'[ -f {d}/1/U/conventional/final/000.json ] || {{ echo "REFUSED: hosts {d} missing (ckpt/rbt-113-O1)" >&2; exit 7; }}']


def split_by_cell(jobs: dict, runners: int) -> list:
    """Per runner: (output dirs, job lines), whole cells round-robin over the runners, so every cell's output directory
    (and its checkpoint branch) belongs to one runner only."""
    cells = list(jobs)
    return [([jobs[c][0] for c in cells[k::runners]], [line for c in cells[k::runners] for line in jobs[c][1]]) for k in range(runners)]


def pays_jobs(root: str, template: str, steps: str = "", hosts: str = "runs/RBT-129/hosts113") -> tuple:
    """The rest of Stage 0's PAYS cells (DESIGN 5.1), under the sweep's block, as (job lines, output dirs).  Per cell,
    **holistic PAYS** (RBT132.md (v): ``template`` is ``planters.py pays``, which writes ``<out>/holistic/``), and, when
    ``steps`` is given, the holistic nose step (its harness is pending; it writes into ``<out>/holistic-steps/``).  Both
    are formatted with point, world (the block's json: NOT a config), config (the directory holding its config.json),
    config_json (``worlds/<id>.config.json``; launch adversary S11) and out (``stage0/pays/<cell>``); ``HOSTS_ROOT``
    is the leg's restored RBT-113 O1 root."""
    jobs, dirs = [], []
    for pid in blocks.PAYS_CELLS:
        o = rel(os.path.join(root, "stage0", "pays", pid))
        kw = dict(point=pid, world=rel(os.path.join(root, "worlds", f"{pid}.json")), config=rel(os.path.join(root, "worlds", "config", pid)),
                  config_json=rel(config_json_path(root, pid)), out=o)
        for sub, t in (("holistic", template), ("holistic-steps", steps)):
            if t:
                jobs.append(_guarded(f"{o}/{sub}", _hosts(t.format(**kw), hosts)))
                dirs.append(f"{o}/{sub}")
    return jobs, dirs


# -- the K3 calibration (DESIGN 12, the 09:44 amendment) ---------------------------------------------------------- #

#: the calibration cells (ruling item 1): the planted controls only, at a = 6, before the probe leg
CALIB_CELLS = ("c0-p030-PW-G", "c0-p030-HP-G")


def calib_jobs(root: str, hosts: str, workers: int = 4, stage2: str = "") -> tuple:
    """Per calibration cell, ``planters.py planted`` into ``calibration/<cell>`` (its log, F, calls and K3/K4 stay in
    the files), then ``calib-extract`` of its planted.json into ``calibration.txt``, which alone is printed.

    ``stage2`` (DESIGN 12, the 12:52 amendment, S2): planters' calibration-only flag that runs the confirmation battery
    on every (a) and (c) plant; the lane then writes ``calibration-s2/<cell>``, saved to its own branches, and prints
    the same lines."""
    jobs, dirs = [], []
    for pid in CALIB_CELLS:
        d = rel(os.path.join(root, "calibration-s2" if stage2 else "calibration", pid))
        cmd = f"python {PLANTERS} planted {pid} {rel(config_json_path(root, pid))} {d} --hosts {hosts} --workers {workers}"
        if stage2:
            cmd += f" {stage2}"
        jobs.append(_guarded(d, cmd, f"python runs/RBT-129/launch/stages.py calib-extract {d}/planted.json > {d}/calibration.txt",
                             "fail=1"))
        jobs.append(f"if [ -e {d}/calibration.txt ]; then cat {d}/calibration.txt; fi")
        dirs.append(d)
    jobs.append('exit "${fail:-0}"')
    return jobs, dirs


def planters_accepts(flag: str) -> bool:
    """Does this tree's ``planters.py planted`` take ``flag``?  (Its --help, read without running a season.)"""
    r = subprocess.run([sys.executable, os.path.join(ROOT, PLANTERS), "planted", "--help"], cwd=ROOT, capture_output=True,
                       text=True, timeout=300)
    return r.returncode == 0 and flag.split("=")[0] in r.stdout.split()


def _planters():
    """RBT-132's pinned planters.py, when it is on this tree (#459), else None."""
    import importlib.util
    path = os.path.join(ROOT, "runs", "RBT-116", "planters.py")
    if not os.path.isfile(path):
        return None
    if "rbt116_planters" not in sys.modules:
        spec = importlib.util.spec_from_file_location("rbt116_planters", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["rbt116_planters"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["rbt116_planters"]


def _seen(rec: dict) -> bool:
    """K3's SEEN: the pinned ``planters.seen`` once #459 is on the tree (#465 adversary N-3); until then the same rule
    restated (the 07:10 ruling: stage 2's c3 and c2, repeated on the confirmation)."""
    pl = _planters()
    if pl is not None:
        return bool(pl.seen(rec))
    s2 = rec.get("stage2") or {}
    conf = rec.get("confirm") or rec.get("k3_confirm") or {}
    return bool(s2.get("c3") and s2.get("c2") and conf.get("c3") and conf.get("c2"))


def _dt_sd(stats: dict) -> float:
    """ΔT's SD over a battery's draws, recovered exactly from ``battery_stats``'s bound: lbdT = dT − t(0.95, n−1)·sd/√n."""
    import math
    n, dt, lb = stats.get("n", 0), stats.get("dT"), stats.get("lbdT")
    if dt is None or lb is None or n < 2 or not math.isfinite(lb):
        return float("nan")
    return (dt - lb) * math.sqrt(n) / _steer().t_quantile(0.95, n - 1)


def _steer():
    import importlib.util
    spec = importlib.util.spec_from_file_location("rbt116_steer", os.path.join(ROOT, "runs", "RBT-116", "steer.py"))
    if "rbt116_steer" not in sys.modules:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["rbt116_steer"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["rbt116_steer"]


def calib_extract(path: str) -> str:
    """The calibration's only printed lines: per (a) and (c) plant, SEEN and ΔT's mean and SD (with n) on stage 2 and
    on the confirmation battery, and the SEEN share per kind.  No F, no call, no K3/K4 verdict (no-peek)."""
    rec = json.load(open(path))
    f = lambda x: "-" if x is None else f"{x:+.4f}" if x == x else "nan"
    lines = [f"# RBT-129 K3 calibration at {rec['point']} (DESIGN 12, 09:44): the planted controls at a = 6; per plant SEEN,"
             " and dT mean / SD / n on stage 2 and the confirmation", "kind plant SEEN  s2_dT     s2_sd    s2_n  conf_dT   conf_sd  conf_n"]
    share = []
    for kind in ("a", "c"):
        recs = rec["calls"].get(kind, [])
        for i, r in enumerate(recs):
            cols = []
            for key in ("stage2", "confirm"):
                st = r.get(key) or (r.get("k3_confirm") if key == "confirm" else None) or {}
                cols += [f(st.get("dT")), f(_dt_sd(st)) if st else "-", str(st.get("n", "-"))]
            lines.append(f"{kind:4s} {i:5d} {'yes' if _seen(r) else 'no':4s}  {cols[0]:8s}  {cols[1]:8s} {cols[2]:4s}  {cols[3]:8s}  {cols[4]:8s} {cols[5]}")
        k = sum(_seen(r) for r in recs)
        share.append(f"({kind}) {k} of {len(recs)}" + (f" = {k / len(recs):.3f}" if recs else ""))
    lines.append("SEEN share: " + "; ".join(share))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "emit"):
        s = sub.add_parser(name)
        s.add_argument("stages", help="P, 0 or P,0")
        s.add_argument("--hosts", type=int, default=10)
        s.add_argument("--root", default=RUNS)
        s.add_argument("--fair", default="", help="the fairness flags, as one string (RBT-128's '--fair')")
        s.add_argument("--eat", default=" ".join(blocks.EAT_RULED), help="the eating rule (default: the ruled root + surface, RBT-125 section C)")
    s = sub.add_parser("prelaunch")
    s.add_argument("--root", default=RUNS)
    s.add_argument("--fair", default="")
    s.add_argument("--eat", default=" ".join(blocks.EAT_RULED), help="the eating rule (default: the ruled root + surface, RBT-125 section C)")
    s.add_argument("--procs", type=int, default=4)
    s = sub.add_parser("run-lane")
    s.add_argument("lane")
    for name in ("probes", "pays"):
        s = sub.add_parser(name)
        s.add_argument("--root", default=RUNS)
        s.add_argument("--steer", default=os.path.join(ROOT, "runs", "RBT-116", "steer.py"))
        s.add_argument("--steer-sha", default="", help="the ruled steer.py's git blob hash (git hash-object); required")
        s.add_argument("--steer-cmd" if name == "probes" else "--pays-cmd", dest="template", default="")
        s.add_argument("--fair", default="")
        s.add_argument("--eat", default=" ".join(blocks.EAT_RULED), help="the eating rule (default: the ruled root + surface)")
        s.add_argument("--hosts", default="runs/RBT-129/hosts113", help="repository-relative HOSTS_ROOT (RBT-113 O1, restored where missing)")
        if name == "probes":
            s.add_argument("--planted-cmd", dest="planted", default="", help="the planted set's command, per point (S4)")
        else:
            s.add_argument("--steps-cmd", dest="steps", default="", help="the holistic nose step's command (optional: its harness is pending)")
            s.add_argument("--steps-harness", default="", help="the harness file the command runs; required with --steps-cmd")
            s.add_argument("--steps-sha", default="", help="its ruled git blob hash; required with --steps-cmd")
    s = sub.add_parser("calibrate", help="K3's calibration (DESIGN 12, 09:44): the planted controls at the two cells")
    s.add_argument("--root", default=RUNS)
    s.add_argument("--fair", default="")
    s.add_argument("--eat", default=" ".join(blocks.EAT_RULED))
    s.add_argument("--hosts", default="runs/RBT-129/hosts113", help="repository-relative HOSTS_ROOT (RBT-113 O1, restored where missing)")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--stage2", default="", metavar="FLAG",
                   help="(as --stage2=FLAG) the S2 second stage (DESIGN 12, 12:52): planters' calibration-only flag that confirms every (a) and"
                        " (c) plant; emits lanes/calibrate-s2/ into calibration-s2/<cell>.  Only once the S2 trigger has fired")
    s = sub.add_parser("calib-extract", help="the calibration's printed lines, from a planted.json")
    s.add_argument("planted")
    s = sub.add_parser("save", help="one serialized, logged snapshot of a directory to its checkpoint branch")
    s.add_argument("dir")
    s = sub.add_parser("check-branches", help="readout side: every run directory and pilot unit has a checkpoint branch")
    s.add_argument("lanes", nargs="+", help="the lane files (lanes/<stages>/host*-lane*.jsonl)")
    s.add_argument("--save", action="store_true", help="first backfill missing unit records and snapshot, serially, each missing one on this machine")
    s.add_argument("--repo", default="", help="the checkout holding the runs (a Stage P session's), if not this one")
    s = sub.add_parser("pays-prize")
    s.add_argument("--root", default=RUNS)
    s.add_argument("--fair", default="")
    s.add_argument("--eat", default=" ".join(blocks.EAT_RULED), help="the eating rule (default: the ruled root + surface, RBT-125 section C)")
    s.add_argument("--bodies", default="runs/RBT-129/bodies", help="repository-relative BODIES_ROOT for RBT-125's ten hosts; each runner restores forage-SEED from ckpt/rbt-90-SEED where missing")
    s.add_argument("--procs", type=int, default=4)
    s.add_argument("--runners", type=int, default=3, help="scripts to split the 180 jobs over, one per 4-core session")
    s = sub.add_parser("pays-steps")
    s.add_argument("--root", default=RUNS)
    s.add_argument("--fair", default="")
    s.add_argument("--eat", default=" ".join(blocks.EAT_RULED), help="the eating rule (default: the ruled root + surface)")
    s.add_argument("--hosts", default="runs/RBT-129/hosts113", help="repository-relative HOSTS_ROOT; each runner restores O1 from ckpt/rbt-113-O1 where missing")
    s.add_argument("--procs", type=int, default=4)
    s.add_argument("--runners", type=int, default=3)
    s = sub.add_parser("pays-steps2", help="the steps leg's re-measurement at the 12 c >= 1 cells (ruling on #467; #475)")
    s.add_argument("--root", default=RUNS)
    s.add_argument("--fair", default="")
    s.add_argument("--eat", default=" ".join(blocks.EAT_RULED))
    s.add_argument("--hosts", default="runs/RBT-129/hosts113", help="repository-relative HOSTS_ROOT; each runner restores O1 from ckpt/rbt-113-O1 where missing")
    s.add_argument("--procs", type=int, default=4)
    s.add_argument("--runners", type=int, default=3)
    s = sub.add_parser("verify", help="a leg's host guards, where its script runs")
    s.add_argument("launch")
    s.add_argument("--root", default=RUNS)
    a = ap.parse_args(argv)
    if a.cmd in ("plan", "emit"):
        stages = [x for x in a.stages.split(",") if x]
        if not set(stages) <= {"P", "0"}:
            ap.error("stages are P, 0 or P,0")
        if a.cmd == "plan":
            print_plan(plan(stages, a.hosts, a.root))
        else:
            for path in emit(stages, a.hosts, a.root, a.fair.split(), a.eat.split()):
                print(path)
    elif a.cmd == "prelaunch":
        import contextlib
        import prints

        check_fair(a.fair.split())
        check_eat(a.eat.split())
        check_surface_clearance(a.eat.split())
        for pid in blocks.all_ids():
            check_block(blocks.block(pid, fair=a.fair.split(), eat=a.eat.split()))
        path = os.path.join(a.root, "lanes", "prelaunch_prints.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f, contextlib.redirect_stdout(f):
            prints.main([f"--fair={a.fair}", f"--eat={a.eat}", "--procs", str(a.procs)])
        print(path)
    elif a.cmd == "run-lane":
        run_lane(a.lane)
    elif a.cmd == "verify":
        verify_leg(a.launch, a.root)
        print(f"verified {a.launch}")
    elif a.cmd == "pays-steps":
        fair, eat = a.fair.split(), a.eat.split()
        check_fair(fair)
        check_eat(eat)
        check_surface_clearance(eat)
        world_config_dirs(a.root, blocks.PAYS_CELLS, fair, eat)
        leg_dir = os.path.join(a.root, "lanes", "pays-steps")
        launch = write_leg_launch(leg_dir, "pays-steps (Stage 0's designed nose step against a speed step)", blocks.PAYS_CELLS, fair, eat,
                                  {"hosts": a.hosts, "runners": a.runners, "procs": a.procs}, STEP_TOOLS)
        pins = [(t, git_hash(os.path.join(ROOT, t))) for t in STEP_TOOLS]
        for k, (outs, lines) in enumerate(split_by_cell(step_jobs(a.root, a.hosts, a.procs), a.runners)):
            path = os.path.join(leg_dir, f"runner{k}.sh")
            write_script(path, restore_step_hosts(a.hosts) + restore_outputs(outs) + lines, pins, launch)
            print(path)
    elif a.cmd == "pays-steps2":
        fair, eat = a.fair.split(), a.eat.split()
        check_fair(fair)
        check_eat(eat)
        check_surface_clearance(eat)
        if "--exclude-exploded" not in open(os.path.join(ROOT, STEP_TOOLS[0])).read():
            _refuse(f"{STEP_TOOLS[0]} has no --exclude-exploded (#475 not merged): the re-measurement's pin must be its blob", 6)
        world_config_dirs(a.root, STEPS2_CELLS, fair, eat)
        leg_dir = os.path.join(a.root, "lanes", "pays-steps-c1c2")
        launch = write_leg_launch(leg_dir, "pays-steps-c1c2 (the steps leg re-measured at c >= 1: ruling on #467; #475)", STEPS2_CELLS, fair, eat,
                                  {"hosts": a.hosts, "runners": a.runners, "procs": a.procs, "flags": STEPS2_FLAGS}, STEP_TOOLS)
        pins = [(t, git_hash(os.path.join(ROOT, t))) for t in STEP_TOOLS]
        jobs = step_jobs(a.root, a.hosts, a.procs, STEPS2_CELLS, "steps2", STEPS2_FLAGS)
        for k, (outs, lines) in enumerate(split_by_cell(jobs, a.runners)):
            path = os.path.join(leg_dir, f"runner{k}.sh")
            write_script(path, restore_step_hosts(a.hosts) + restore_outputs(outs) + lines, pins, launch)
            print(path)
    elif a.cmd == "pays-prize":
        fair, eat = a.fair.split(), a.eat.split()
        check_fair(fair)
        check_eat(eat)
        check_surface_clearance(eat)
        world_config_dirs(a.root, blocks.PAYS_CELLS, fair, eat)  # checks every cell's block first (L1)
        leg_dir = os.path.join(a.root, "lanes", "pays-prize")
        launch = write_leg_launch(leg_dir, "pays-prize (Stage 0's designed PAYS prize at a = 6)", blocks.PAYS_CELLS, fair, eat,
                                  {"bodies": a.bodies, "runners": a.runners, "procs": a.procs}, PRIZE_TOOLS)
        pins = [(t, git_hash(os.path.join(ROOT, t))) for t in PRIZE_TOOLS]
        for k, (outs, lines) in enumerate(split_by_cell(prize_jobs(a.root, a.bodies, a.procs), a.runners)):
            path = os.path.join(leg_dir, f"runner{k}.sh")
            write_script(path, restore_hosts(a.bodies) + restore_outputs(outs) + lines, pins, launch)
            print(path)
    elif a.cmd == "save":
        if not os.environ.get("NO_DURABLE"):
            save_now(os.path.abspath(a.dir))  # a failure is logged and warned, never fatal to the runner
    elif a.cmd == "calib-extract":
        sys.stdout.write(calib_extract(a.planted))
    elif a.cmd == "check-branches":
        lanes = [os.path.abspath(x) for x in a.lanes]
        if a.repo:
            set_repo(a.repo)
        return check_branches(lanes, a.save)
    elif a.cmd == "calibrate":
        fair, eat = a.fair.split(), a.eat.split()
        check_fair(fair)
        check_eat(eat)
        check_surface_clearance(eat)
        pins = tool_pins(STEER_TOOLS)
        if a.stage2 and not planters_accepts(a.stage2):
            _refuse(f"{PLANTERS} planted does not take {a.stage2}: the S2 flag (DESIGN 12, 12:52) is not on this tree", 6)
        world_config_dirs(a.root, CALIB_CELLS, fair, eat)
        leg_dir = os.path.join(a.root, "lanes", "calibrate-s2" if a.stage2 else "calibrate")
        what = ("calibrate-s2 (K3's calibration, S2: the confirmation on every (a) and (c) plant, DESIGN 12 12:52)" if a.stage2
                else "calibrate (K3's calibration: the planted controls, DESIGN 12 09:44)")
        launch = write_leg_launch(leg_dir, what, CALIB_CELLS, fair, eat,
                                  {"hosts": a.hosts, "workers": a.workers, **({"stage2": a.stage2} if a.stage2 else {})}, STEER_TOOLS)
        jobs, dirs = calib_jobs(a.root, a.hosts, a.workers, a.stage2)
        path = os.path.join(leg_dir, "runner.sh")
        write_script(path, restore_step_hosts(a.hosts) + restore_outputs(dirs) + jobs, pins, launch)
        print(path)
    else:
        check_steer(a.steer, a.template, a.steer_sha)
        check_fair(a.fair.split())
        check_eat(a.eat.split())
        check_surface_clearance(a.eat.split())
        if a.cmd == "probes" and not a.planted:
            _refuse("no --planted-cmd: the planted set per pilot point (DESIGN 5.3(c); launch adversary S4)", 6)
        steer_rel = rel(a.steer)
        tools = [t for t in (PROBE_TOOLS if a.cmd == "probes" else STEER_TOOLS) if t != "runs/RBT-116/steer.py"]
        pins = [(steer_rel, a.steer_sha)] + tool_pins(tools)
        if a.cmd == "pays" and (a.steps or a.steps_harness or a.steps_sha):
            check_pinned(a.steps_harness, a.steps_sha, "the holistic nose-step harness")
            if not a.steps:
                _refuse("--steps-harness without --steps-cmd: give the holistic nose step's command", 6)
            pins.append((rel(a.steps_harness), a.steps_sha))
        cells = blocks.PILOT if a.cmd == "probes" else blocks.PAYS_CELLS
        world_config_dirs(a.root, cells, a.fair.split(), a.eat.split())
        leg_dir = os.path.join(a.root, "lanes", a.cmd)
        if a.cmd == "probes":
            jobs, extinct, runs, dirs = probe_jobs(a.root, a.template, a.planted, a.hosts)
            os.makedirs(leg_dir, exist_ok=True)
            with open(os.path.join(leg_dir, "extinct.txt"), "w") as f:  # RBT132.md (iv): skipped, reported (DESIGN M2)
                f.write("# pilot units extinct pre-merge (EXTINCT.txt): not probed at either season (DESIGN M2)\n"
                        + "".join(u + "\n" for u in extinct))
            head = restore_step_hosts(a.hosts) + restore_runs(runs) + restore_outputs(dirs)
        else:
            jobs, dirs = pays_jobs(a.root, a.template, a.steps, a.hosts)
            head = restore_step_hosts(a.hosts) + restore_outputs(dirs)
        launch = write_leg_launch(leg_dir, a.cmd, cells, a.fair.split(), a.eat.split(), {"hosts": a.hosts}, [p for p, _ in pins])
        path = os.path.join(a.root, "lanes", f"{a.cmd}.sh")
        write_script(path, head + jobs, pins, launch)
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
