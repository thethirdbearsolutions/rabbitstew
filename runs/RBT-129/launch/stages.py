"""RBT-129 Stage P (pilot) and Stage 0 (census) launchers (DESIGN sections 4.1, 5.1, 5.2, 5.5 K1, 11.1, 11.2).

    stages.py plan   P|0|P,0 [--hosts 10]           the arms, seeds, host layout and core-h against the budget (no run)
    stages.py emit   P|0|P,0 --fair '--fair' [--eat '--eat-from root'] [--hosts 10] [--root runs/RBT-129]
                                                     the lane files, the world blocks (worlds/<id>.json) and launch.txt
    stages.py prelaunch --fair=--fair [--eat ...]   the pre-launch prints (prints.py) under the launch block, to
                                                     lanes/prelaunch_prints.txt (fixtures only; guarded like emit)
    stages.py run-lane LANEFILE                     one lane (launch as a harness background task, one per lane,
                                                     WORKERS=2, two lanes a 4-core session)
    stages.py probes P --steer PATH --steer-cmd TEMPLATE      Stage P's perception probes and planted set (steer.py)
    stages.py pays   --steer PATH --pays-cmd TEMPLATE         Stage 0's 18 PAYS cells (steer.py, RBT-125's harness)

**Guards.** ``emit`` and ``run-lane`` REFUSE (exit 4) until every flag given by ``--fair`` is an option of the
``ecology`` subcommand on this tree (RBT-128 pending), and ``run-lane`` also refuses off x86_64 (RBT-96) and with
uncommitted changes under ``rabbitstew/``.  ``probes`` and ``pays`` REFUSE (exit 6) until ``--steer`` names an existing
file (RBT-116's ``steer.py``, pending) and a command template is given; they emit job files for the ruled CLI, whose
arguments this design does not fix.  **No-peek:** the runner prints progress only (job names and exit codes); no income,
share, season table or garden figure is printed or read by this tool.

**Stage P** (4 points x seeds 129001-129004, 300 seasons).  Per point and seed, one chain on one lane:
  S60     a fresh S run to its season-59 checkpoint (``--seasons 60``: state.json at season 60; RBT-130 README)
  ckpt60  a copy of that directory, before S continues (the fork's source)
  S       S resumed to 300
  M       ckpt60 forked with ``ecology.merge_after = 60``, ``pooled_capacity = 120``, resumed to 300
  N       the same with ``merge_null`` = holistic on odd seeds, conventional on even (all 4 seeds at the pilot, S10)
and per point, on seed 129001's chain, **K1** (DESIGN 5.5): a straight run to season 65, and ckpt60 forked with the
merge unset and resumed to 65; K1 PASSES when their lineage.jsonl, cohorts.jsonl and history.json are byte-identical.

**Stage 0** (150 points x seeds 129001-129003, arm S only, seasons 0-59): one fresh run a job.

**Host layout** (DESIGN 11.2; RBT-107's packing rule): ``--hosts`` 4-core sessions, two lanes each at WORKERS = 2.
Units (a pilot chain, a census job) go to lanes by longest-first greedy on cost; within a lane, census jobs are ordered
by a seed rotation, and while a job runs its lane holds an exclusive lock on its seed (``/tmp/rbt129-locks``), so the
two lanes of a session never run the same seed at once.
"""
import argparse
import fcntl
import json
import os
import platform
import shutil
import subprocess
import sys
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
          "anchor fallback": ((46, 46), (57, 57))}
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


def check_fair(fair: list) -> None:
    """Refuse unless the fairness flags are given and every one is an ``ecology`` option on this tree."""
    if not fair:
        raise SystemExit("REFUSED (exit 4): no --fair flags given; RBT-129's every arm runs under RBT-128's ruled set (DESIGN 2)")
    known = ecology_options()
    missing = [f for f in fair if f.startswith("--") and f.split("=")[0] not in known]
    if missing:
        print(f"REFUSED: {' '.join(missing)} is not an option of `ecology` on this tree (RBT-128 --fair not merged)", file=sys.stderr)
        raise SystemExit(4)


def check_steer(path, template) -> None:
    if not path or not os.path.isfile(path):
        print(f"REFUSED: steer.py not found at {path!r} (RBT-116's instrument at its ruled version is a gate, DESIGN 11.1)", file=sys.stderr)
        raise SystemExit(6)
    if not template:
        print("REFUSED: no command template: give the ruled steer.py's command line (DESIGN 5.3(c))", file=sys.stderr)
        raise SystemExit(6)


def check_host() -> None:
    if platform.machine() != "x86_64":
        print("REFUSED: RBT-129 arms run on the cloud x86_64 image only (RBT-96)", file=sys.stderr)
        raise SystemExit(3)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "rabbitstew"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        print("REFUSED: rabbitstew/ has uncommitted changes; launch from a clean checkout", file=sys.stderr)
        raise SystemExit(5)


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


def units_for(stages: list, root: str) -> list:
    return (pilot_units(root) if "P" in stages else []) + (census_units(root) if "0" in stages else [])


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
    for st in stages:
        s = sum(j["cost"] for u in units if u["stage"] == st for j in u["jobs"])
        arms = core_h(s)
        if st == "P":
            extra = tuple(len(blocks.PILOT) * len(PILOT_SEEDS) * p + len(blocks.PILOT) * PLANTED_POINT for p in PROBE_SEED)
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
        print(f"# Stage 0: {len(blocks.all_ids())} points x {len(CENSUS_SEEDS)} seeds, S 0-59; PAYS at {len(blocks.PAYS_CELLS)} cells (guarded: steer.py)")
    print("# stage  arm-seasons  arms at 20 / 25 core-s   + " + "probes, planted set (P) or PAYS cells (0)   = total at 20 | at 25   DESIGN 11.2 line")
    grand = [0.0, 0.0, 0.0, 0.0]
    for st in p["stages"]:
        c = p["core_h"][st]
        (t20, t25), ((d20lo, d20hi), (d25lo, d25hi)) = c["total"], BUDGET[st]
        print(f"  {st:5s}  {p['arm_seasons'][st]:10d}   {c['arms'][0]:6.1f} / {c['arms'][1]:6.1f}        + {c['extra'][0]:.1f}-{c['extra'][1]:.1f}"
              f"                                 = {t20[0]:.1f}-{t20[1]:.1f} | {t25[0]:.1f}-{t25[1]:.1f}   {d20lo}-{d20hi} | {d25lo}-{d25hi}")
        grand = [grand[0] + t20[0], grand[1] + t20[1], grand[2] + t25[0], grand[3] + t25[1]]
    if "P" in p["stages"]:
        print("  (P is above its DESIGN line by the planted set at the pilot, 4 x 0.8 core-h, and K1's straight run to 65 at one"
              " seed a point (4 x 70 arm-seasons); neither was in the r4 table)")
    (t20, t25), (a20, a25) = BUDGET["total"], BUDGET["anchor fallback"]
    print(f"# these stages: {grand[0]:.1f}-{grand[1]:.1f} core-h at 20 core-s, {grand[2]:.1f}-{grand[3]:.1f} at 25")
    print(f"# the programme: DESIGN total {t20[0]:,}-{t25[1]:,} + the adopted anchor fallback {a20[0]}-{a25[1]} ="
          f" {t20[0] + a20[0]:,}-{t25[1] + a25[1]:,} core-h (the brief's envelope: {BRIEF_ENVELOPE[0]:,}-{BRIEF_ENVELOPE[1]:,})")
    print("# host lane  units  seeds                          arm-seasons  wall h at 20 / 25 core-s (WORKERS = 2)")
    for ln in p["lanes"]:
        seeds = ",".join(str(x) for x in ln["seeds"])
        print(f"  {ln['host']:4d} {ln['lane']:4d}  {ln['units']:5d}  {seeds:29s}  {ln['arm_seasons']:11d}  {ln['wall_h'][0]:5.1f} / {ln['wall_h'][1]:5.1f}")
    walls = [ln["wall_h"] for ln in p["lanes"]]
    print(f"# wall time (the longest lane): {max(w[0] for w in walls):.1f} to {max(w[1] for w in walls):.1f} h, before probes and PAYS")


# -- emit --------------------------------------------------------------------------------------------------------- #

def emit(stages: list, hosts: int, root: str, fair: list, eat: list) -> list:
    check_fair(fair)
    units = units_for(stages, root)
    lanes = layout(units, hosts)
    points = sorted({j["point"] for u in units for j in u["jobs"] if "point" in j})
    worlds = os.path.join(root, "worlds")
    blocks.export(worlds, points, fair=fair, eat=eat)
    lane_dir = os.path.join(root, "lanes", "-".join(stages))
    os.makedirs(lane_dir, exist_ok=True)
    rev = lambda *a: subprocess.run(["git", "rev-parse", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    with open(os.path.join(lane_dir, "launch.txt"), "w") as f:
        f.write(f"# RBT-129 launch record: stages {','.join(stages)}\ncommit {rev('HEAD')}\nrabbitstew_tree {rev('HEAD:rabbitstew')}\n"
                f"fair {' '.join(fair)}\neat {' '.join(eat)}\nemitted {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
    paths = []
    for k, lane in enumerate(lanes):
        path = os.path.join(lane_dir, f"host{k // 2}-lane{k % 2}.jsonl")
        with open(path, "w") as f:
            for u in lane:
                for j in u["jobs"]:
                    f.write(json.dumps({**j, "worlds": worlds}) + "\n")
        paths.append(path)
    return paths


# -- run ---------------------------------------------------------------------------------------------------------- #

def _done(d: str, tag: str) -> bool:
    return os.path.exists(os.path.join(d, f".rbt129-done-{tag}"))


def _mark(d: str, tag: str) -> None:
    with open(os.path.join(d, f".rbt129-done-{tag}"), "w") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ\n", time.gmtime()))


def _ecology(cmd: list, d: str, label: str) -> None:
    workers = os.environ.get("WORKERS", "2")
    full = [sys.executable, "-m", "rabbitstew.cli", "ecology", *cmd, "--workers", workers, "--out", d]
    with open(os.path.join(d, "command.txt"), "a") as f:
        f.write(" ".join(full) + "\n")
    with open(os.path.join(d, "run.log"), "a") as log:
        proc = subprocess.Popen(full, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        durable = None
        if not os.environ.get("NO_DURABLE"):
            durable = subprocess.Popen([os.path.join(ROOT, "scripts", "durable.sh"), "every", "20", d, label], cwd=ROOT,
                                       env={**os.environ, "DURABLE_WATCH_PID": str(proc.pid)},
                                       stdout=open(os.path.join(d, "durable.log"), "a"), stderr=subprocess.STDOUT)
        code = proc.wait()
        if durable is not None:
            durable.wait()
    if code:
        raise SystemExit(f"{label}: ecology exited {code} (see {d}/run.log)")


def _label(d: str) -> str:
    """One checkpoint branch per run directory (``ckpt/rbt-129-<path under runs/RBT-129>``), whichever job writes it."""
    rel = os.path.relpath(os.path.abspath(d), RUNS)
    return "rbt-129-" + rel.replace(os.sep, "-")


def _restore(d: str) -> None:
    """A directory lost with its container comes back from its latest snapshot (done-markers included)."""
    if not os.environ.get("NO_DURABLE") and not os.path.exists(os.path.join(d, "state.json")):
        subprocess.run([os.path.join(ROOT, "scripts", "durable.sh"), "restore", d, _label(d)], cwd=ROOT, capture_output=True)


def _save(d: str) -> None:
    if not os.environ.get("NO_DURABLE"):
        subprocess.run([os.path.join(ROOT, "scripts", "durable.sh"), "save", d, _label(d)], cwd=ROOT, capture_output=True)


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


def run_job(job: dict) -> None:
    kind, d, tag = job["job"], job["dir"], job["name"].split("/")[-1]
    _restore(d)
    if _done(d, tag):
        return
    if kind == "fresh":
        if os.path.exists(os.path.join(d, "state.json")):
            _ecology(["--resume", "--seasons", str(job["seasons"])], d, _label(d))
        else:
            if os.path.isdir(d):
                shutil.rmtree(d)  # never finished a season: nothing of it is kept (lineage.jsonl appends)
            os.makedirs(d)
            b = json.load(open(os.path.join(job["worlds"], f"{job['point']}.json")))
            check_fair(b["fair"] or [])
            _ecology([*b["argv"], "--seed", str(job["seed"]), "--seasons", str(job["seasons"])], d, _label(d))
    elif kind == "snapshot":  # the season-60 state, kept apart (and saved) before S continues
        at = json.load(open(os.path.join(job["src"], "state.json")))["season"]
        if at != job.get("season", MERGE):
            raise SystemExit(f"{job['name']}: {job['src']} is at season {at}, not the fork's {job.get('season', MERGE)};"
                             " the checkpoint is lost and S must be re-run from 0 to rebuild it")
        if os.path.isdir(d):
            shutil.rmtree(d)
        fork_config(job["src"], d, {})
        _mark(d, tag)
        _save(d)
        return
    elif kind == "resume":
        _ecology(["--resume", "--seasons", str(job["seasons"])], d, _label(d))
    elif kind == "fork":
        if not os.path.exists(os.path.join(d, "state.json")):
            if os.path.isdir(d):
                shutil.rmtree(d)
            _restore(job["src"])
            fork_config(job["src"], d, job["set"])
        _ecology(["--resume", "--seasons", str(job["seasons"])], d, _label(d))
    elif kind == "k1":
        _restore(job["ref"])
        same = {n: open(os.path.join(job["ref"], n), "rb").read() == open(os.path.join(d, n), "rb").read()
                for n in ("lineage.jsonl", "cohorts.jsonl", "history.json")}
        verdict = "PASS" if all(same.values()) else "FAIL"
        with open(os.path.join(os.path.dirname(d), "K1.txt"), "w") as f:
            f.write(f"K1 {verdict}: fork of the season-60 state (merge unset) vs a straight run, seasons 0-64: "
                    + ", ".join(f"{n} {'identical' if s else 'DIFFERS'}" for n, s in same.items()) + "\n")
        print(f"{job['name']}: K1 {verdict}")  # the control's verdict, not an outcome
        return
    else:
        raise ValueError(f"unknown job {kind}")
    _mark(d, tag)
    _save(d)  # the marker reaches the snapshot, so a restored finished run is not re-run


def run_lane(path: str) -> None:
    check_host()
    jobs = [json.loads(line) for line in open(path) if line.strip()]
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


# -- the steer.py-dependent steps --------------------------------------------------------------------------------- #

def probe_jobs(root: str, template: str) -> list:
    """Stage P's probes (DESIGN 5.3(c), (e)): 20 members per fauna per seed at seasons 0 and 300, 8 draws, the RNG
    129300 + j; and the planted set per point (8 hosts a plant, a = 6).  ``template`` is formatted with run, season,
    seed, rng, point and out."""
    out = []
    for pid in blocks.PILOT:
        for j in PILOT_SEEDS:
            run = os.path.join(root, "stageP", pid, str(seed(j)), "S")
            for season in (0, SEASONS):
                o = os.path.join(root, "stageP", pid, str(seed(j)), f"probes-{season}")
                out.append(template.format(run=run, season=season, seed=seed(j), rng=129300 + j, point=pid, out=o))
    return out


def pays_jobs(root: str, template: str) -> list:
    """Stage 0's PAYS cells (DESIGN 5.1): per fauna, under the sweep's block; ``template`` is formatted with point,
    world (the block's json) and out."""
    return [template.format(point=pid, world=os.path.join(root, "worlds", f"{pid}.json"), out=os.path.join(root, "stage0", "pays", pid))
            for pid in blocks.PAYS_CELLS]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "emit"):
        s = sub.add_parser(name)
        s.add_argument("stages", help="P, 0 or P,0")
        s.add_argument("--hosts", type=int, default=10)
        s.add_argument("--root", default=RUNS)
        s.add_argument("--fair", default="", help="the fairness flags, as one string (RBT-128's '--fair')")
        s.add_argument("--eat", default=" ".join(blocks.EAT_CANDIDATE))
    s = sub.add_parser("prelaunch")
    s.add_argument("--root", default=RUNS)
    s.add_argument("--fair", default="")
    s.add_argument("--eat", default=" ".join(blocks.EAT_CANDIDATE))
    s.add_argument("--procs", type=int, default=4)
    s = sub.add_parser("run-lane")
    s.add_argument("lane")
    for name in ("probes", "pays"):
        s = sub.add_parser(name)
        s.add_argument("--root", default=RUNS)
        s.add_argument("--steer", default=os.path.join(ROOT, "runs", "RBT-116", "steer.py"))
        s.add_argument("--steer-cmd" if name == "probes" else "--pays-cmd", dest="template", default="")
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
        path = os.path.join(a.root, "lanes", "prelaunch_prints.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f, contextlib.redirect_stdout(f):
            prints.main([f"--fair={a.fair}", f"--eat={a.eat}", "--procs", str(a.procs)])
        print(path)
    elif a.cmd == "run-lane":
        run_lane(a.lane)
    else:
        check_steer(a.steer, a.template)
        jobs = probe_jobs(a.root, a.template) if a.cmd == "probes" else pays_jobs(a.root, a.template)
        path = os.path.join(a.root, "lanes", f"{a.cmd}.sh")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("#!/bin/bash\nset -e\n" + "\n".join(jobs) + "\n")
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
