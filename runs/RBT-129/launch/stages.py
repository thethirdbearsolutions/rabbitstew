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
    stages.py screen-emit --fair=--fair [--hosts 10]
                                                     Stage F (AMENDMENT-FOUNDING F1-F5; RBT-129c): the founder screen's lanes
                                                     at W118-b, seeds 129001-129016, each fauna alone, salts 0..20 in order
                                                     (salt 0 is the REQUIRED single-fauna re-run), and the salt-0
                                                     byte-compare against the census / pilot halves for 129001-129004
    stages.py screen-table                          F8: the screen table, the founding layer, the stop rule (F4) and the
                                                     side-effect table, to stageF/screen_table.txt
    stages.py fork-source-emit --fair=--fair [--seeds 8|16]
                                                     F5 / MUST 3: the anchor fallback's two-fauna S 0-59 at W118-b at
                                                     (s_j, t_j), with K-SALT against the seed's W118-b run where s >= 1,
                                                     t = 0 (F7); refused (exit 8) unless the screen gate passes.  The gate
                                                     re-derives every record from its attempt runs and recomputes every
                                                     salt-0 compare (129001-129008), restoring missing directories
    stages.py stage1-emit --fair=--fair             Stage 1's S chains at the screened salts, n = 8 (129001 resumes the
                                                     census only at salts (0, 0), F7; K-SALT where s >= 1, t = 0); refused
                                                     (exit 8) unless the screen is complete, every salt-0 compare PASSes
                                                     and the stop rule has not fired.  Emits lanes only: nothing launches
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
#: the chains whose unit directory has a record (Stage P, and Stage 1's S chains: #495 ruling, SHOULD 8)
UNIT_PREFIXES = ("P/", "1/")


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


def _fresh(job: dict, d: str, long: bool, extra=()) -> None:
    """A fresh run of the job's world block from season 0 (or its resume, when a killed run left a state behind).
    ``extra`` holds only the founding flags (``--only-fauna`` and the two stream salts, amendment F); anything else is
    refused, so a lane file cannot change the world."""
    check_extra(extra)
    if os.path.exists(os.path.join(d, "state.json")):
        if any(len(m) for m in json.load(open(os.path.join(d, "state.json")))["populations"].values()):
            _resume(job, d, long)  # fix1b: an emptied run (killed before its marker) is done as it stands
    else:
        if os.path.isdir(d):
            shutil.rmtree(d)  # never finished a season: nothing of it is kept (lineage.jsonl appends)
        os.makedirs(d)
        b = json.load(open(os.path.join(job["worlds"], f"{job['point']}.json")))
        check_fair(b["fair"] or [])
        _ecology([*b["argv"], *extra, "--seed", str(job["seed"]), "--seasons", str(job["seasons"])], d, _label(d), long)


def run_job(job: dict) -> None:
    """One job; its paths are absolute here (``run_lane`` resolves the lane file's relative ones).  Every job that runs
    ends with its done-marker and a save of its directory (K1 included, on both its paths); a pilot unit's own files go
    to its record (``unit_file``)."""
    kind, d, tag = job["job"], job["dir"], job["name"].split("/")[-1]
    long = job.get("cost", 0) >= DURABLE_MIN
    pilot = job["name"].startswith(UNIT_PREFIXES)
    if pilot:
        restore_record(_unit(job))
    _restore(d, SCREEN_FILE if kind in ("screen", "salt0cmp") else KSALT_FILE if kind == "ksalt" else "state.json")
    if _done(d, tag):
        return
    if kind == "fresh":
        _fresh(job, d, long, job.get("extra", []))
    elif kind == "adopt":  # Stage 1 (amendment F7): 129001's census S 0-59 at salts (0, 0) is the S60 of this chain
        adopt_census(job, d)
    elif kind in ("screen", "salt0cmp", "ksalt"):
        founding_job(job, d)
        _mark(d, tag)
        _save(d)
        return
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
    for pid in sorted({j["point"] for j in jobs if j["job"] in ("fresh", "screen", "adopt")}):
        wpath = next(os.path.join(j["worlds"], f"{pid}.json") for j in jobs if j.get("point") == pid)
        rebuilt = json.loads(json.dumps(blocks.block(pid, fair=fair, eat=eat)))
        if json.load(open(wpath)) != rebuilt:
            _refuse(f"{wpath} is not the block launch.txt's flags build for {pid}; re-emit", 4)
        check_block(rebuilt)


def check_lane_salts(jobs: list, launch: dict) -> None:
    """A lane emitted with a ``salts`` line (Stage 1, the fork source) runs every fresh job at exactly its seed's
    screened salts; a hand-edited ``extra`` is refused (exit 4)."""
    if "salts" not in launch:
        return
    salts = {int(k): tuple(int(x) for x in v.split("/")) for k, v in (p.split(":") for p in launch["salts"].split())}
    for j in jobs:
        if j["job"] == "fresh" and list(j.get("extra", [])) != salts_argv(*salts.get(j["seed"], (-1, -1))):
            _refuse(f"{j['name']}: its salts {j.get('extra')} are not launch.txt's {salts.get(j['seed'])}", 4)


def run_lane(path: str) -> None:
    launch = read_launch(os.path.join(os.path.dirname(os.path.abspath(path)), "launch.txt"))
    check_host(launch)
    jobs = [json.loads(line) for line in open(path) if line.strip()]
    jobs = [{k: (absolute(v) if k in PATH_KEYS else v) for k, v in j.items()} for j in jobs]
    check_lane_blocks(jobs, launch)
    check_lane_salts(jobs, launch)
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


# -- Stage F: the founder screen (AMENDMENT-FOUNDING F1-F8; RBT-129c) --------------------------------------------- #

H, D = "holistic", "conventional"
FAUNAS = (H, D)
#: F1: the anchor, W118-b (not a Stage-1 point), under the sweep's block and --fair exactly as the census ran it
SCREEN_POINT = ANCHOR_NO_STAGE1
#: F5: seeds 129001-129016, all screened before Stage 1
SCREEN_SEEDS = tuple(range(1, 17))
#: F3, F4: salt 0 first, then the 20 redraws, in this order; the first that founds is kept
SCREEN_SALTS = tuple(range(0, 21))
#: F2: >= 30 of the fauna's 60 alive at season 59, counted before same-season refill (ruling item 3)
SCREEN_CRITERION = 30
SCREEN_SEASONS = MERGE  # an attempt is S 0-59: --seasons 60, as the census ran
SCREEN_SEASON = SCREEN_SEASONS - 1
#: F5 (ruling item 8): salt 0 re-run alone, REQUIRED, for seeds 1-8, each byte-compared with the two-fauna run of its
#: seed at W118-b: the census S for 129001-129003, the pilot S for 129004 (both required by the ruling) and the A-stage
#: S for 129005-129008 (same launch; #495 ruling, SHOULD 2).  These are also the fork source's K-SALT references (F7)
SALT0_SEEDS = tuple(range(1, 9))
SALT0_REF = {j: ("stageP" if j == 4 else "stage0") for j in SALT0_SEEDS}
#: the committed census FOUNDING-FAIL layer, printed beside the founding layer (F8; #495 ruling, SHOULD 4)
CENSUS_READOUT = os.path.join(RUNS, "stageP0-readout", "stageP0_readout.txt")
#: F4 (ruling item 4): Stage 1 does not launch if >= 3 of the 16 seeds, or >= 2 of seeds 1-8, are SCREEN-CAPPED
STOP_ALL, STOP_FIRST, FIRST_HALF = 3, 2, tuple(range(1, 9))
#: Stage 1 (DESIGN 4.1): 27 points at G (c in {0, 1, 2} x p x L) and 9 at L (c = 1); n = 8 (ruling item 2)
STAGE1_POINTS = tuple([f"c{c}-p{p}-{L}-G" for c in ("0", "1", "2") for p in ("010", "030", "080") for L in blocks.LAYOUTS]
                      + [f"c1-p{p}-{L}-L" for p in ("010", "030", "080") for L in blocks.LAYOUTS])
STAGE1_N = 8
#: the seed whose census S 0-59 Stage 1 resumes (F7; DESIGN 11.1's 02:22 note, as amended by T10)
RESUME_SEED = 1
SALT_FLAG = {H: "--holistic-stream-salt", D: "--designed-stream-salt"}
SCREEN_FILE = "SCREEN.json"
SALT0_FILE = "SALT0.txt"
KSALT_FILE = "KSALT.txt"
SIDE_SEASONS = range(0, 15)
CLAIM = "among holistic and designed stream draws (founders and their early history) that establish at W118-b"


def check_extra(extra) -> None:
    """A lane job's extra flags may be the founding flags only: ``--only-fauna K`` and the two salts, each >= 0."""
    extra = list(extra)
    if len(extra) % 2:
        _refuse(f"extra flags must be flag/value pairs: {extra}", 4)
    for flag, value in zip(extra[0::2], extra[1::2]):
        if flag == "--only-fauna" and value in FAUNAS:
            continue
        if flag in SALT_FLAG.values() and str(value).isdigit():
            continue
        _refuse(f"a lane job may add only --only-fauna and the stream salts, not {flag} {value}", 4)


def screen_argv(fauna: str, salt: int) -> list:
    """F1: the fauna alone (RBT-130's only_fauna path), its own stream at ``salt``."""
    return ["--only-fauna", fauna, SALT_FLAG[fauna], str(int(salt))]


def salts_argv(s: int, t: int) -> list:
    """Both faunas at (s_j, t_j): only the non-zero salts are passed, so salt 0 is today's command and config."""
    return ([SALT_FLAG[H], str(s)] if s else []) + ([SALT_FLAG[D], str(t)] if t else [])


def _history(d: str) -> list:
    path = os.path.join(d, "history.json")
    return json.load(open(path))["history"] if os.path.exists(path) else []


def alive_before_refill(hist: list, kind: str, season: int = None) -> int:
    """F2's count: the fauna's alive at ``season`` (59) less that season's births (the refill); 0 with no row (extinct)."""
    season = SCREEN_SEASON if season is None else season
    rows = [e for e in hist if e["population"] == kind and e["season"] == season]
    return rows[0]["alive"] - rows[0]["births"] if rows else 0


def last_alive(hist: list, kind: str) -> int:
    """The last season the fauna had a member alive before refill (the readouts' ``lastlive``), or -1."""
    return max([e["season"] for e in hist if e["population"] == kind and e["alive"] - e["births"] > 0], default=-1)


def attempt_outcome(d: str, kind: str) -> tuple:
    hist = _history(d)
    return alive_before_refill(hist, kind), last_alive(hist, kind)


def founds(alive59: int) -> bool:
    """F2: >= 30 of 60 alive at season 59, before refill."""
    return alive59 >= SCREEN_CRITERION


def screen(attempt, salts=None) -> dict:
    """F3-F4 for one seed and fauna: try each salt in order, ``attempt(salt) -> (alive at 59, last season alive)``,
    and keep the first that founds; no later salt is run.  After all fail the fauna keeps salt 0, SCREEN-CAPPED."""
    tried = []
    for salt in SCREEN_SALTS if salts is None else salts:
        alive59, last = attempt(salt)
        tried.append({"salt": int(salt), "alive59": int(alive59), "last": int(last)})
        if founds(alive59):
            return {"tried": tried, "salt": int(salt), "capped": False}
    return {"tried": tried, "salt": 0, "capped": True}


def check_screen_record(rec: dict) -> None:
    """A SCREEN.json must be what the rule gives on its own attempts: salts 0, 1, ... in order, and the kept salt and
    the cap re-derived from the alive counts (a hand-edited record is refused)."""
    tried = rec.get("tried") or []
    if [a["salt"] for a in tried] != list(SCREEN_SALTS[:len(tried)]):
        _refuse(f"seed {rec.get('seed')} {rec.get('fauna')}: salts tried out of order: {[a['salt'] for a in tried]}", 8)
    by = {a["salt"]: (a["alive59"], a["last"]) for a in tried}
    again = screen(lambda s: by[s] if s in by else _refuse(f"seed {rec.get('seed')} {rec.get('fauna')}: the record stops at salt"
                                                           f" {tried[-1]['salt'] if tried else None} before the rule does", 8))
    if again != {k: rec.get(k) for k in ("tried", "salt", "capped")}:
        _refuse(f"seed {rec.get('seed')} {rec.get('fauna')}: SCREEN.json is not the rule applied to its own attempts", 8)


def capped_seeds(results: dict) -> list:
    """Seeds j with either fauna SCREEN-CAPPED (F4 counts either fauna)."""
    return sorted({j for (j, _), r in results.items() if r["capped"]})


def stop_rule(capped: list) -> list:
    """F4 (ruling item 4): why Stage 1 does not launch; empty when it may."""
    why = []
    all_ = [j for j in capped if j in SCREEN_SEEDS]
    first = [j for j in all_ if j in FIRST_HALF]
    if len(all_) >= STOP_ALL:
        why.append(f"{len(all_)} of {len(SCREEN_SEEDS)} seeds SCREEN-CAPPED (>= {STOP_ALL}): {', '.join(str(seed(j)) for j in all_)}")
    if len(first) >= STOP_FIRST:
        why.append(f"{len(first)} of seeds {seed(FIRST_HALF[0])}-{seed(FIRST_HALF[-1])} SCREEN-CAPPED (>= {STOP_FIRST}):"
                   f" {', '.join(str(seed(j)) for j in first)}")
    return why


def screen_dir(root: str, j: int, fauna: str) -> str:
    return os.path.join(root, "stageF", SCREEN_POINT, str(seed(j)), fauna)


def attempt_dir(root: str, j: int, fauna: str, salt: int) -> str:
    return os.path.join(screen_dir(root, j, fauna), f"salt{salt}")


def salt0_ref(root: str, j: int) -> str:
    return os.path.join(root, SALT0_REF[j], SCREEN_POINT, str(seed(j)), "S")


def screen_units(root: str) -> list:
    """Per seed, one unit: each fauna's screen (salt 0 first: for seeds 1-8 that attempt is the REQUIRED salt-0 re-run),
    then, for 129001-129004, each fauna's salt-0 attempt byte-compared with its half of the census or pilot run."""
    units = []
    for j in SCREEN_SEEDS:
        jobs = [{"job": "screen", "name": f"F/{SCREEN_POINT}/{seed(j)}/{k}/screen", "point": SCREEN_POINT, "seed": seed(j),
                 "fauna": k, "dir": screen_dir(root, j, k), "seasons": SCREEN_SEASONS, "cost": SCREEN_SEASONS} for k in FAUNAS]
        if j in SALT0_REF:
            jobs += [{"job": "salt0cmp", "name": f"F/{SCREEN_POINT}/{seed(j)}/{k}/salt0cmp", "seed": seed(j), "fauna": k,
                      "dir": screen_dir(root, j, k), "src": attempt_dir(root, j, k, 0), "ref": salt0_ref(root, j), "cost": 0}
                     for k in FAUNAS]
        units.append({"stage": "F", "seed": seed(j), "jobs": jobs})
    return units


def half_lines(d: str, kind: str, upto: int = None) -> tuple:
    """One fauna's rows of history.json (as serialized) and its lines of lineage.jsonl (raw), seasons 0..upto (59)."""
    upto = SCREEN_SEASON if upto is None else upto
    hist = [json.dumps(e) for e in _history(d) if e["population"] == kind and e["season"] <= upto]
    lin = []
    path = os.path.join(d, "lineage.jsonl")
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            if r["population"] == kind and r["generation"] <= upto:
                lin.append(line.rstrip("\n"))
    return hist, lin


def half_compare(a: str, b: str, kind: str, upto: int = None) -> tuple:
    """(verdict, lines): ``kind``'s history rows and lineage lines, seasons 0..upto (59), of run ``a`` against run ``b``."""
    upto = SCREEN_SEASON if upto is None else upto
    (ha, la), (hb, lb) = half_lines(a, kind, upto), half_lines(b, kind, upto)
    lines = [f"{kind}: {len(ha)} / {len(hb)} history rows, {len(la)} / {len(lb)} lineage lines, seasons 0-{upto}"]
    if not ha or not la:
        lines.append(f"EMPTY: no {kind} rows in {a}")
    for name, x, y in (("history.json", ha, hb), ("lineage.jsonl", la, lb)):
        if x != y:
            k = next((i for i, (p, q) in enumerate(zip(x, y)) if p != q), min(len(x), len(y)))
            lines.append(f"DIFFERS: {name}, first at {kind} row {k}")
    return ("PASS" if len(lines) == 1 else "FAIL"), lines


def founding_job(job: dict, d: str) -> None:
    """Stage F's jobs and Stage 1's K-SALT (paths absolute)."""
    kind = job["job"]
    if kind == "screen":
        fauna = job["fauna"]

        def attempt(salt):
            sub = os.path.join(d, f"salt{salt}")
            _restore(sub)
            if not _done(sub, f"salt{salt}"):
                _fresh({**job, "dir": sub}, sub, False, screen_argv(fauna, salt))
                _mark(sub, f"salt{salt}")
                _save(sub)
            return attempt_outcome(sub, fauna)

        rec = {"seed": job["seed"], "fauna": fauna, "point": job["point"], "criterion": SCREEN_CRITERION, **screen(attempt)}
        with open(os.path.join(d, SCREEN_FILE), "w") as f:
            json.dump(rec, f, indent=1)
    elif kind == "salt0cmp":
        _restore(job["ref"])
        verdict, lines = half_compare(job["src"], job["ref"], job["fauna"])
        with open(os.path.join(d, SALT0_FILE), "w") as f:
            f.write(f"SALT0 {verdict}: {job['fauna']} alone at salt 0 against its half of {rel_or_abs(job['ref'])},"
                    f" seasons 0-{SCREEN_SEASON} (history.json rows, lineage.jsonl lines)\n" + "".join(f"  {x}\n" for x in lines))
        print(f"{job['name']}: SALT0 {verdict}", flush=True)  # the control's verdict, not an outcome
        if verdict != "PASS":
            _save(d)
            raise SystemExit(f"{job['name']}: SALT0 MISMATCH: the fauna alone is not its half of the two-fauna run. This"
                             " re-opens RBT-130's stream claim; Stage 1 does not launch until it is resolved (AMENDMENT-FOUNDING F5)")
    elif kind == "ksalt":
        os.makedirs(d, exist_ok=True)
        _restore(job["ref"])
        verdict, lines = half_compare(job["src"], job["ref"], D)
        word = "PASS" if verdict == "PASS" else "VOID"
        text = (f"KSALT {word}: the designed half (s >= 1, t = 0) of {rel_or_abs(job['src'])} against {rel_or_abs(job['ref'])},"
                f" seasons 0-{SCREEN_SEASON}\n" + "".join(f"  {x}\n" for x in lines))
        with open(os.path.join(d, KSALT_FILE), "w") as f:
            f.write(text)
        if job["name"].startswith(UNIT_PREFIXES):
            unit_file(os.path.dirname(d), KSALT_FILE, text)  # into the unit's record, saved to its branch (SHOULD 6)
        print(f"{job['name']}: KSALT {word}", flush=True)  # the control's verdict, not an outcome
        if word == "VOID":
            _mark(d, job["name"].split("/")[-1], "KSALT VOID")
            _save(d)
            print(f"KSALT VOID: {job['name']}: the designed half differs from the census's. The point is VOID for this seed"
                  " and RBT-129c's stream claim is re-opened (AMENDMENT-FOUNDING F7); tell the coordinator", file=sys.stderr, flush=True)
            raise SystemExit(f"{job['name']}: KSALT VOID (F7): the lane stops here; restarting it continues past this record")
    else:
        raise ValueError(kind)


def _arm_config(d: str) -> dict:
    c = json.load(open(os.path.join(d, "config.json")))
    c.pop("workers", None)
    return c


def adopt_census(job: dict, d: str) -> None:
    """F7: 129001's Stage-1 S60 is the census S 0-59 at the same point, taken as it stands (exact at salts (0, 0)).
    Refused unless the census config is the one this chain's fresh S60 would write (salts 0 included), bar workers."""
    if os.path.exists(os.path.join(d, "state.json")):
        return
    src = job["src"]
    _restore(src)
    if not os.path.exists(os.path.join(src, "state.json")):
        _refuse(f"{job['name']}: the census state {src} is not here and has no snapshot", 4)
    b = json.load(open(os.path.join(job["worlds"], f"{job['point']}.json")))
    want = blocks.config_dict(b["argv"] + list(job.get("extra", [])), seed=job["seed"], seasons=job["seasons"])
    want.pop("workers", None)
    if _arm_config(src) != want:
        _refuse(f"{job['name']}: {src}'s config.json is not this chain's S60 config (salts (0, 0), the block, seed, seasons)", 4)
    if os.path.isdir(d):
        shutil.rmtree(d)
    fork_config(src, d, {})


def stage1_units(root: str, salts: dict, n: int = STAGE1_N) -> list:
    """Stage 1's S chains (DESIGN 4.1, 5.2) at the 36 points and seeds 1..n, each at its screened (s_j, t_j) (F3, T4).
    Per point and seed: S60, then ckpt60 (the season-59 state, the gated M and N arms' fork source), then S to 300.
    S60 is the census's own S 0-59 **only** for 129001 and only when both its salts are 0 (F7); every other seed runs
    fresh with its salts.  Where a census seed runs with s >= 1 and t = 0, K-SALT byte-compares the designed half with
    the census's (F7).  M and N are gated on S at the merge (T5) and are not emitted here."""
    units = []
    for pid in STAGE1_POINTS:
        for j in range(1, n + 1):
            s, t = salts[j]
            d = os.path.join(root, "stage1", pid, str(seed(j)))
            census = os.path.join(root, "stage0", pid, str(seed(j)), "S")
            if j == RESUME_SEED and (s, t) == (0, 0):
                first = {"job": "adopt", "name": f"1/{pid}/{seed(j)}/S60", "point": pid, "seed": seed(j), "src": census,
                         "dir": f"{d}/S", "seasons": MERGE, "cost": 0}
            else:
                first = {"job": "fresh", "name": f"1/{pid}/{seed(j)}/S60", "point": pid, "seed": seed(j), "dir": f"{d}/S",
                         "seasons": MERGE, "extra": salts_argv(s, t), "cost": MERGE}
            jobs = [first]
            if first["job"] == "fresh" and j in CENSUS_SEEDS and s >= 1 and t == 0:
                jobs.append({"job": "ksalt", "name": f"1/{pid}/{seed(j)}/KSALT", "seed": seed(j), "src": f"{d}/S", "ref": census,
                             "dir": f"{d}/ksalt", "cost": 0})
            jobs += [
                {"job": "snapshot", "name": f"1/{pid}/{seed(j)}/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "seed": seed(j), "cost": 0},
                {"job": "resume", "name": f"1/{pid}/{seed(j)}/S", "dir": f"{d}/S", "seed": seed(j), "seasons": SEASONS, "cost": SEASONS - MERGE},
            ]
            units.append({"stage": "1", "seed": seed(j), "jobs": jobs})
    return units


def fork_source_units(root: str, salts: dict, n: int = STAGE1_N) -> list:
    """F5 / MUST 3: the anchor fallback's fork source, a two-fauna S 0-59 at W118-b at (s_j, t_j), once per seed.  Where
    s_j >= 1 and t_j = 0 and the seed has a two-fauna run at W118-b (census 1-3, pilot 4, A-stage 5-8), K-SALT
    byte-compares its designed half with that run's (F7: "and 129007 and 129008 at W118-b"; #495 ruling, MUST 1)."""
    units = []
    for j in range(1, n + 1):
        s, t = salts[j]
        d = os.path.join(root, "stageF", "fork", SCREEN_POINT, str(seed(j)))
        jobs = [{"job": "fresh", "name": f"Ffork/{SCREEN_POINT}/{seed(j)}/S", "point": SCREEN_POINT, "seed": seed(j),
                 "dir": f"{d}/S", "seasons": MERGE, "extra": salts_argv(s, t), "cost": MERGE}]
        if j in SALT0_REF and s >= 1 and t == 0:
            jobs.append({"job": "ksalt", "name": f"Ffork/{SCREEN_POINT}/{seed(j)}/KSALT", "seed": seed(j), "src": f"{d}/S",
                         "ref": salt0_ref(root, j), "dir": f"{d}/ksalt", "cost": 0})
        units.append({"stage": "Ffork", "seed": seed(j), "jobs": jobs})
    return units


def screen_block_argv(root: str) -> list:
    """The W118-b block's flags the screen ran under, rebuilt from ``lanes/F/launch.txt``'s fairness and eating flags
    (never read from a world file that could have been edited)."""
    path = os.path.join(root, "lanes", "F", "launch.txt")
    if not os.path.exists(path):
        _refuse(f"{rel_or_abs(path)} is missing: the screen's launch record (re-emit, or restore it)", 8)
    launch = read_launch(path)
    fair, eat = launch["fair"].split(), launch["eat"].split()
    check_fair(fair)
    check_eat(eat)
    return blocks.world_argv(SCREEN_POINT, fair=fair, eat=eat)


def check_attempt(root: str, j: int, k: str, a: dict, argv: list) -> None:
    """One recorded attempt against its own run directory (#495 ruling, SHOULD 1): the directory exists (restored from
    its branch where missing, SHOULD 5), its config.json is the screen's command at this salt (the block, the fauna
    alone, the salt, the seed, seasons 0-59; bar workers), the run is complete (at season 60, or the fauna extinct),
    and its alive count at 59 and last season alive are the record's."""
    sub = attempt_dir(root, j, k, a["salt"])
    _restore(sub)
    where = f"seed {seed(j)} {k} salt {a['salt']}"
    if not os.path.exists(os.path.join(sub, "config.json")) or not os.path.exists(os.path.join(sub, "state.json")):
        _refuse(f"{where}: no attempt run at {rel_or_abs(sub)}: a record with no run behind it", 8)
    want = blocks.config_dict(argv + screen_argv(k, a["salt"]), seed=seed(j), seasons=SCREEN_SEASONS)
    want.pop("workers", None)
    if _arm_config(sub) != want:
        _refuse(f"{where}: {rel_or_abs(sub)}/config.json is not the screen's command at this salt", 8)
    state = json.load(open(os.path.join(sub, "state.json")))
    if state["season"] != SCREEN_SEASONS and any(len(m) for m in state["populations"].values()):
        _refuse(f"{where}: the attempt stopped at season {state['season']} with members alive: not complete", 8)
    if attempt_outcome(sub, k) != (a["alive59"], a["last"]):
        _refuse(f"{where}: the record says {a['alive59']} alive at {SCREEN_SEASON} (last {a['last']}); the run says"
                f" {attempt_outcome(sub, k)}", 8)


def load_screen(root: str) -> dict:
    """{(j, fauna): SCREEN.json} for all 16 seeds and both faunas; each record is checked against the rule, and every
    attempt it lists against that attempt's own run (``check_attempt``).  Missing directories are restored from their
    branches first; refused (exit 8) while any record is missing or does not match its runs."""
    out, missing = {}, []
    argv = None
    for j in SCREEN_SEEDS:
        for k in FAUNAS:
            _restore(screen_dir(root, j, k), SCREEN_FILE)
            path = os.path.join(screen_dir(root, j, k), SCREEN_FILE)
            if not os.path.exists(path):
                missing.append(rel_or_abs(path))
                continue
            rec = json.load(open(path))
            if rec.get("seed") != seed(j) or rec.get("fauna") != k:
                _refuse(f"{path} is not seed {seed(j)} {k}", 8)
            if rec.get("point") != SCREEN_POINT or rec.get("criterion") != SCREEN_CRITERION:
                _refuse(f"{path}: point {rec.get('point')!r} and criterion {rec.get('criterion')!r} are not"
                        f" {SCREEN_POINT} and {SCREEN_CRITERION}", 8)
            check_screen_record(rec)
            argv = screen_block_argv(root) if argv is None else argv
            for a in rec["tried"]:
                check_attempt(root, j, k, a, argv)
            out[(j, k)] = rec
    if missing:
        _refuse(f"the screen is not complete: {len(missing)} of {2 * len(SCREEN_SEEDS)} records missing, first {missing[0]}", 8)
    return out


def salt0_verdicts(root: str) -> dict:
    """{(j, fauna): 'PASS' | 'FAIL'} for the salt-0 re-runs of 129001-129008, recomputed by ``half_compare`` from the
    attempt and its reference (both restored where missing), not read from SALT0.txt (#495 ruling, SHOULD 1)."""
    out = {}
    for j in SALT0_REF:
        for k in FAUNAS:
            src = attempt_dir(root, j, k, 0)
            _restore(src)
            _restore(salt0_ref(root, j))
            out[(j, k)] = half_compare(src, salt0_ref(root, j), k)[0]
    return out


def screen_salts(results: dict) -> dict:
    return {j: (results[(j, H)]["salt"], results[(j, D)]["salt"]) for j in SCREEN_SEEDS}


def screen_gate(root: str) -> dict:
    """What Stage 1 and the fork source need (T10): the screen complete, every salt-0 byte-compare PASS, the stop rule
    not fired.  Returns the salts {j: (s_j, t_j)}; refuses (exit 8) otherwise."""
    results = load_screen(root)
    bad = {k: v for k, v in salt0_verdicts(root).items() if v != "PASS"}
    if bad:
        _refuse("the salt-0 single-fauna byte-compare is not PASS: " + ", ".join(f"{seed(j)} {k} {v}" for (j, k), v in sorted(bad.items()))
                + " (AMENDMENT-FOUNDING F5: RBT-130's stream claim is re-opened; Stage 1 does not launch)", 8)
    why = stop_rule(capped_seeds(results))
    if why:
        _refuse("the stop rule fired (AMENDMENT-FOUNDING F4); Stage 1 does not launch: " + "; ".join(why)
                + ". The screen table goes to the coordinator; the fallback (b) needs its own amendment", 8)
    return screen_salts(results)


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple:
    """The exact binomial interval (stdlib, by bisection on the binomial tail)."""
    from math import comb

    def tail_ge(p):  # P(X >= k)
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    def solve(f, target):
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if f(mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else solve(tail_ge, alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: 1 - (1 - tail_ge(p) + (comb(n, k) * p ** k * (1 - p) ** (n - k))), 1 - alpha / 2)
    return lower, upper


def _net(r: dict, price: float) -> float:
    """A member-season's net income, food - p * kJ (the Stage-0 readout's ``net``)."""
    return r.get("food", 0.0) - price * r.get("work", 0.0) / 1000.0


def side_effects(d: str, kind: str) -> dict:
    """F8 / R10 for one attempt, seasons 0-14: per season, founders alive, their mean node count, the mean net income of
    every member-season (the dead included) and births; and the founders' solvency, the Stage-0 readout's definition
    over 0-14 (``stageP0_readout.py``: every lineage row but cull and merge-null, so a founder's dying season counts
    and a founder dead in season 0 is a founder; solvent when its mean net income is at least the living cost)."""
    cfg = json.load(open(os.path.join(d, "config.json")))
    price, cost = cfg["sim"]["food"]["work_cost"], float(cfg["ecology"]["living_cost"])
    rows = []
    path = os.path.join(d, "lineage.jsonl")
    if os.path.exists(path):  # the readout's rows(): the starved and aged rows kept, cull and merge-null dropped (MUST 2)
        rows = [r for r in map(json.loads, open(path)) if r["population"] == kind and r.get("death") not in ("cull", "merge-null")
                and r["generation"] in SIDE_SEASONS]
    founders = {}
    for r in rows:  # the founders: every no-parent row at 0-14, a founder dying in season 0 included
        if not r["parents"]:
            founders.setdefault(r["name"], r["nodes"])
    hist = {e["season"]: e for e in _history(d) if e["population"] == kind}
    per, fnet = {}, {}
    for r in rows:
        if r["name"] in founders:
            fnet.setdefault(r["name"], []).append(_net(r, price))  # its dying season included, as the readout's
    for s in SIDE_SEASONS:
        at = [r for r in rows if r["generation"] == s]  # income: the season's dead included (the readout's flows)
        fa = [r for r in at if r["name"] in founders and r.get("death") is None]  # founders alive: the living rows
        per[s] = {"founders_alive": len(fa), "founder_nodes": sum(r["nodes"] for r in fa) / len(fa) if fa else None,
                  "income": sum(_net(r, price) for r in at) / len(at) if at else None,
                  "births": hist[s]["births"] if s in hist else 0}
    solvent = sum(1 for v in fnet.values() if sum(v) / len(v) >= cost)
    return {"founders": len(founders), "founder_nodes": sum(founders.values()) / len(founders) if founders else None,
            "solvency": solvent / len(founders) if founders else None, "seasons": per}


def _fmt(x, spec="{:.3f}"):
    return "-" if x is None else spec.format(x)


def census_founding_fail(path: str = None) -> list:
    """The census's (unscreened) FOUNDING-FAIL layer, as the committed Stage-0 readout prints it (F8; SHOULD 4): per
    fauna, the points FOUNDING-FAIL, and W118-b's extinct seeds."""
    path = path or CENSUS_READOUT
    out = [f"  the census FOUNDING-FAIL layer, unscreened, beside it (T3; from {rel_or_abs(path)}):"]
    if not os.path.exists(path):
        return out + ["    NOT FOUND: the committed readout is missing"]
    text = open(path).read().splitlines()
    try:
        at = next(i for i, l in enumerate(text) if l.startswith("C2 FOUNDING-FAIL"))
    except StopIteration:
        return out + ["    NOT FOUND: no C2 FOUNDING-FAIL section in the readout"]
    for line in text[at + 1:at + 3]:
        kind, _, rest = line.strip().partition(": ")
        out.append(f"    {kind:12s} FOUNDING-FAIL at {rest.split(' points')[0]} points")
    row = next((l for l in text if l.strip().startswith(SCREEN_POINT + " ")), None)
    if row:
        out.append(f"    at W118-b ({SCREEN_POINT}), census seeds extinct at 59 H/D: {row.split()[1]} of {len(CENSUS_SEEDS)}")
    return out


def screen_report(root: str) -> str:
    """F8: the screen table, the founding layer, the stop-rule verdict, the salt-0 byte-compare and the side-effect
    table (accepted against rejected draws at W118-b, seasons 0-14).  Descriptive; no call is made at W118-b (T7)."""
    results = load_screen(root)
    s0 = salt0_verdicts(root)
    capped = capped_seeds(results)
    why = stop_rule(capped)
    out = [f"# RBT-129 Stage F: the founder screen at W118-b = {SCREEN_POINT}, each fauna alone, S 0-{SCREEN_SEASON}, under the"
           " sweep's block and --fair (AMENDMENT-FOUNDING F1-F8)",
           f"# criterion: >= {SCREEN_CRITERION} of 60 alive at season {SCREEN_SEASON}, before same-season refill; salts"
           f" {SCREEN_SALTS[0]}..{SCREEN_SALTS[-1]} in order, the first that founds kept; all fail: salt 0, SCREEN-CAPPED",
           f"# claim label: {CLAIM}", "", "## screen table (per seed and fauna: every salt tried, alive at 59, last season alive)",
           "# seed    fauna         kept  status        attempts (salt:alive59/last)"]
    for j in SCREEN_SEEDS:
        for k in FAUNAS:
            r = results[(j, k)]
            status = "SCREEN-CAPPED" if r["capped"] else "founds"
            out.append(f"  {seed(j)}  {k:12s}  {r['salt']:4d}  {status:13s} " + " ".join(f"{a['salt']}:{a['alive59']}/{a['last']}" for a in r["tried"]))
    out += ["", "## salts (s_j, t_j), written into every Stage-1/2 arm's config.json when non-zero (absent means 0: the pre-salt"
            " config byte for byte); lanes/1/launch.txt and lanes/F-fork/launch.txt carry them as a salts line"]
    out += [f"  {seed(j)}  s = {results[(j, H)]['salt']:2d}  t = {results[(j, D)]['salt']:2d}" for j in SCREEN_SEEDS]
    out += ["", "## founding layer (per fauna: attempts, passes, pass rate with its Clopper-Pearson 95% interval)"]
    for k in FAUNAS:
        att = [a for j in SCREEN_SEEDS for a in results[(j, k)]["tried"]]
        n, p = len(att), sum(founds(a["alive59"]) for a in att)
        lo, hi = clopper_pearson(p, n)
        out.append(f"  {k:12s} attempts {n:3d}  passes {p:3d}  rate {p / n:.3f}  95% CI {lo:.3f}-{hi:.3f}")
    out += census_founding_fail()
    out += ["", f"## salt-0 single-fauna re-run, byte-compared (F5; REQUIRED for {seed(SALT0_SEEDS[0])}-{seed(SALT0_SEEDS[-1])}):"
            " against the census S (129001-129003), the pilot S (129004) and the A-stage S (129005-129008) at W118-b"]
    out += [f"  {seed(j)}  {k:12s}  SALT0 {v}" for (j, k), v in sorted(s0.items())]
    out += ["", "## stop rule (F4)", f"  SCREEN-CAPPED seeds: {', '.join(str(seed(j)) for j in capped) or 'none'}"]
    bad0 = [x for x, v in s0.items() if v != "PASS"]
    if why or bad0:
        out += [f"  STAGE 1 DOES NOT LAUNCH: {w}" for w in why]
        if bad0:
            out.append("  STAGE 1 DOES NOT LAUNCH: the salt-0 byte-compare is not PASS everywhere (RBT-130's stream claim re-opened)")
    else:
        out.append("  not fired: Stage 1 may be emitted (stage1-emit); the launch stays the owner's decision")
    out += ["", "## side-effect table (F8, R10): accepted, rejected and capped draws at W118-b, seasons 0-14, mean over draws",
            "# accepted: the kept passing draw; rejected: a failed draw of a fauna that later passed; capped: every draw of a"
            " SCREEN-CAPPED fauna (its salt-0 draw is the one Stage 1 runs)",
            "# per draw: founders (every no-parent row, the dead included), mean founder node count, founder solvency (the"
            " Stage-0 readout's: mean net income over the founder's rows at 0-14, its dying season included, >= living cost)",
            "# per season: founders alive, their mean node count, mean net income of every member-season (the dead included), births"]
    for k in FAUNAS:
        groups = {"accepted": [], "rejected": [], "capped": []}
        for j in SCREEN_SEEDS:
            r = results[(j, k)]
            for a in r["tried"]:
                g = "capped" if r["capped"] else "accepted" if a["salt"] == r["salt"] else "rejected"
                groups[g].append(side_effects(attempt_dir(root, j, k, a["salt"]), k))
        for g, draws in groups.items():
            mean = lambda xs: (sum(xs) / len(xs)) if xs else None
            out.append(f"  {k:12s} {g:8s} draws {len(draws):3d}  founder nodes {_fmt(mean([x['founder_nodes'] for x in draws if x['founder_nodes'] is not None]), '{:.2f}')}"
                       f"  founder solvency {_fmt(mean([x['solvency'] for x in draws if x['solvency'] is not None]))}")
            for s in SIDE_SEASONS:
                col = [x["seasons"][s] for x in draws]
                out.append(f"      season {s:2d}  founders alive {_fmt(mean([c['founders_alive'] for c in col]), '{:.1f}')}"
                           f"  founder nodes {_fmt(mean([c['founder_nodes'] for c in col if c['founder_nodes'] is not None]), '{:.2f}')}"
                           f"  income {_fmt(mean([c['income'] for c in col if c['income'] is not None]))}"
                           f"  births {_fmt(mean([c['births'] for c in col]), '{:.1f}')}")
    return "\n".join(out) + "\n"


def emit_lanes(name: str, units: list, hosts: int, root: str, fair: list, eat: list, extra: dict = None) -> list:
    """The guarded emission of ``units`` into ``lanes/<name>/`` (the same guards, blocks and launch record as ``emit``)."""
    rel(root)  # refused before anything is written when the root is outside the repository (#495 adversary nit)
    check_fair(fair)
    check_eat(eat)
    check_surface_clearance(eat)
    points = sorted({j["point"] for u in units for j in u["jobs"] if "point" in j})
    for pid in points:
        check_block(blocks.block(pid, fair=fair, eat=eat))
    worlds = os.path.join(root, "worlds")
    blocks.export(worlds, points, fair=fair, eat=eat)
    lane_dir = os.path.join(root, "lanes", name)
    os.makedirs(lane_dir, exist_ok=True)
    with open(os.path.join(lane_dir, "launch.txt"), "w") as f:
        f.write(f"# RBT-129 launch record: {name}\ncommit {_git('rev-parse', 'HEAD')}\n"
                + "".join(f"tree:{t} {_git('rev-parse', f'HEAD:{t}')}\n" for t in PINNED_TREES)
                + f"fair {' '.join(fair)}\neat {' '.join(eat)}\n" + "".join(f"{k} {v}\n" for k, v in (extra or {}).items())
                + f"emitted {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
    paths = []
    for k, lane in enumerate(layout(units, hosts)):
        path = os.path.join(lane_dir, f"host{k // 2}-lane{k % 2}.jsonl")
        with open(path, "w") as f:
            for u in lane:
                for j in u["jobs"]:
                    j = {**j, "worlds": worlds}
                    f.write(json.dumps({k: (rel(v) if k in PATH_KEYS else v) for k, v in j.items()}) + "\n")
        paths.append(path)
    return paths


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
            if j["name"].startswith(UNIT_PREFIXES):
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


def calib_name(stage2: str = "", rerun: str = "") -> str:
    """The calibration's output (and lane) name: ``calibration``, ``-<rerun>`` for a re-run under a new ruling (its own
    directories and branches, never resuming an earlier run's), ``-s2`` for the S2 second stage."""
    return "calibration" + (f"-{rerun}" if rerun else "") + ("-s2" if stage2 else "")


def calib_jobs(root: str, hosts: str, workers: int = 4, stage2: str = "", rerun: str = "") -> tuple:
    """Per calibration cell, ``planters.py planted`` into ``calibration/<cell>`` (its log, F, calls and K3/K4 stay in
    the files), then ``calib-extract`` of its planted.json into ``calibration.txt``, which alone is printed.

    ``stage2`` (DESIGN 12, the 12:52 amendment, S2): planters' calibration-only flag that runs the confirmation battery
    on every (a) and (c) plant; the lane then writes ``calibration-s2/<cell>``, saved to its own branches, and prints
    the same lines."""
    jobs, dirs = [], []
    for pid in CALIB_CELLS:
        d = rel(os.path.join(root, calib_name(stage2, rerun), pid))
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
    s.add_argument("--rerun", default="", metavar="TAG",
                   help="a re-run under a new ruling: outputs calibration-TAG[-s2]/<cell> and lanes/calibrate-TAG[-s2]/, its own"
                        " branches (the earlier run's are never resumed)")
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
    for name, what in (("screen-emit", "Stage F (amendment F): the founder screen's lanes at W118-b, seeds 1-16, each fauna alone"),
                       ("fork-source-emit", "amendment F5 / MUST 3: the anchor fallback's two-fauna S 0-59 at W118-b at (s_j, t_j)"),
                       ("stage1-emit", "Stage 1's S lanes at the screened salts (n = 8), after the screen gate; not launched")):
        s = sub.add_parser(name, help=what)
        s.add_argument("--hosts", type=int, default=10)
        s.add_argument("--root", default=RUNS)
        s.add_argument("--fair", default="")
        s.add_argument("--eat", default=" ".join(blocks.EAT_RULED))
        if name == "fork-source-emit":
            s.add_argument("--seeds", type=int, choices=(8, 16), default=8, help="8, or 16 if R-B extends")
    s = sub.add_parser("screen-table", help="Stage F's screen table, founding layer, stop rule and side-effect table (F8)")
    s.add_argument("--root", default=RUNS)
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
    elif a.cmd == "screen-emit":
        for path in emit_lanes("F", screen_units(a.root), a.hosts, a.root, a.fair.split(), a.eat.split(),
                               {"stage": "F founder screen (AMENDMENT-FOUNDING F1-F5)", "criterion": f">= {SCREEN_CRITERION} of 60 alive at 59"}):
            print(path)
    elif a.cmd == "screen-table":
        text = screen_report(a.root)
        path = os.path.join(a.root, "stageF", "screen_table.txt")
        with open(path, "w") as f:
            f.write(text)
        print(path)
    elif a.cmd in ("fork-source-emit", "stage1-emit"):
        check_fair(a.fair.split())
        salts = screen_gate(a.root)
        pairs = " ".join(f"{seed(j)}:{s}/{t}" for j, (s, t) in sorted(salts.items()))
        if a.cmd == "fork-source-emit":
            units, name, what = fork_source_units(a.root, salts, a.seeds), "F-fork", "F5 fork source (two-fauna S 0-59 at W118-b)"
        else:
            units, name, what = stage1_units(a.root, salts), "1", f"Stage 1 S chains, n = {STAGE1_N} (M and N gated on S at the merge, not emitted)"
        for path in emit_lanes(name, units, a.hosts, a.root, a.fair.split(), a.eat.split(), {"stage": what, "salts": pairs}):
            print(path)
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
        if a.rerun and not a.rerun.replace("-", "").isalnum():
            _refuse(f"--rerun {a.rerun!r}: a tag of letters, digits and dashes", 4)
        leg = "calibrate" + calib_name(a.stage2, a.rerun)[len("calibration"):]
        leg_dir = os.path.join(a.root, "lanes", leg)
        what = (f"{leg} (K3's calibration, S2: the confirmation on every (a) and (c) plant, DESIGN 12 12:52)" if a.stage2
                else f"{leg} (K3's calibration: the planted controls, DESIGN 12 09:44)")
        if a.rerun:
            what += f"; re-run {a.rerun}"
        launch = write_leg_launch(leg_dir, what, CALIB_CELLS, fair, eat,
                                  {"hosts": a.hosts, "workers": a.workers, **({"stage2": a.stage2} if a.stage2 else {}),
                                   **({"rerun": a.rerun} if a.rerun else {})}, STEER_TOOLS)
        jobs, dirs = calib_jobs(a.root, a.hosts, a.workers, a.stage2, a.rerun)
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
