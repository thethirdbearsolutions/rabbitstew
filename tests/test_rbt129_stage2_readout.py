"""RBT-129 Stage 2's readout drivers (runs/RBT-129/stage2/s2readout.py), end to end on a synthetic tree built through the
real path (#535 adversary R-8): the emitters' units (``s2lanes.s2a_units``, ``stages.rb_units``, ``s2b.s2b_units``)
run job by job through ``s2lanes.run_job`` / ``stages.run_job`` (done-markers, snapshots, forks, the seed rule, s60cmp,
K-SALT, ``check_not_crashed``), with only the ecology process itself replaced by a deterministic toy (``toy_ecology``)
that writes what the instrumented build writes: lineage.jsonl, history.json, state.json, config.json, platform.json, and
the EPA log's start, season, overflow and run-lane exit lines.  Crashes are real crash shapes: two native exits, the
second at workers 1, then ``check_not_crashed``'s refusal; the coordinator's ``CRASHED:`` record; the lane re-emitted
without the run (``s2lanes.droppable``).  No marker is fabricated.

Stage 1 (registered data from stock runs) is written by the same toy, without EPA logs."""
import importlib.util
import json
import os
import shutil

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "runs", "RBT-129", "stage2", "s2readout.py")
spec = importlib.util.spec_from_file_location("s2readout", SCRIPT)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
sr, s2, stages, s2lanes, s2b = R.sr, R.s2, R.stages, R.s2lanes, R.s2b
H, D = sr.H, sr.D
EPA = s2.registered_epa()
QDIR = sr.QUARANTINED_DIR
SHA = s2.REGISTERED_SHA
NO_RES = lambda lo, hi, rule, n, reps: ([(0.0, 0.0, 0.0, 0.0, False)] * 2, False)

# -- the toy world: a deterministic function of the point, the seed and the salts ------------------------------------- #

GAIN = {"U": 0.3, "HP": -0.3, "PW": 0.0}
NOISY = ("c05-p030-U-G", "c15-p010-U-G")          # Stage-2a points whose income is noise around 0: R4-eligible
MARGINAL_PT = "c05-p080-U-G"                       # H's per-birth income below the living cost: MARGINAL on its EARNS-H
SIGNAL3 = "c15-p030-U-G"                           # the income signal sits on 3 seeds that overflow (OVERFLOW-SENSITIVE)


def food(pid, j, salt_h):
    g = GAIN[pid.split("-")[2]]
    if pid in NOISY:
        g = 0.3 * (-1) ** j
    if pid == SIGNAL3:
        g = 0.6 if j in (1, 2, 3) else 0.01 * (-1) ** j
    return 1.0 + g + 0.01 * (j % 8) + 0.001 * salt_h, 1.0


def per_birth_fitness(pid):
    return (0.20, 0.60) if pid == MARGINAL_PT else (0.60, 0.60)


ROW_SEASONS = lambda s: s < 60 or s >= 180         # lineage rows only where a reader reads them (flows, g0, regime, K-SALT)


def ctx_of(d):
    parts = os.path.normpath(d).split(os.sep)
    i = parts.index("RBT-129")
    sd, arm = int(parts[-2]), parts[-1]
    return {"pid": parts[-3], "j": sd - 129000, "arm": arm, "where": parts[i + 1]}


def season_rows(ctx, cfg, s):
    """(rows, history entries) of one season."""
    pid, j = ctx["pid"], ctx["j"]
    fh, fd = food(pid, j, cfg.get("holistic_stream_salt", 0) or 0)
    pbh, pbd = per_birth_fitness(pid)
    eco = cfg["ecology"]
    merge = eco.get("merge_after") is not None
    null = eco.get("merge_null")
    pops = ((null, fh if null == H else fd, pbh if null == H else pbd),) if null else ((H, fh, pbh), (D, fd, pbd))
    rows, hist = [], []
    for k, f, pb in pops:
        ext = ctx.get("extinct", {}).get(k)
        if ext is not None and s >= ext:
            continue
        mem = [{"name": f"{k[0]}F", "parents": [], "age": s + 1, "evals": s + 1, "fitness": f, "energy": 5.0, "food": f}]
        if s >= 1:
            mem.append({"name": f"{k[0]}c{s - 1}", "parents": [f"{k[0]}F"], "age": 1, "evals": 1, "fitness": pb,
                        "energy": 1.0, "food": f, "death": "aged"})
        mem.append({"name": f"{k[0]}c{s}", "parents": [f"{k[0]}F"], "age": 0, "evals": 0, "fitness": 0.0, "energy": 1.0})
        if ROW_SEASONS(s):
            for m in mem:
                r = {"generation": s, "population": k, "nodes": 5, **m}
                if "food" in r:
                    r.update({"last_score": r["food"], "work": 0.0})
                rows.append(r)
        alive = 2
        if merge and s >= 60:
            alive = 60 + (10 + j if k == H else -(10 + j)) if not null else 60 + (5 if j % 2 else -5)
        hist.append({"season": s, "population": k, "alive": alive, "births": 1, "deaths": 1 if s >= 1 else 0})
    if null:
        hist.append({"season": s, "population": "null_b", "alive": 60, "births": 0, "deaths": 0})
    return rows, hist


SCEN = {"overflow": {}, "crash": {}}
_PID = [1000]


def continuation_dir(d):
    return ctx_of(d)["where"] in ("stage2a", "rb", "stage2b", "mn-corruption-scan")


def scen_key(d):
    c = ctx_of(d)
    return (c["where"], c["pid"], c["j"] + 129000, c["arm"])


def toy_ecology(cmd, d, label, long=False):
    """``stages._ecology`` replaced: one 'process' runs the toy for the requested seasons, logging as the build's wrapper
    and run-lane do (start, season and overflow lines; the exit line through ``epa_ecology.write_exit``)."""
    import mjbuild
    seasons = int(cmd[cmd.index("--seasons") + 1])
    if "--resume" in cmd:
        cfg = json.load(open(os.path.join(d, "config.json")))
        start = json.load(open(os.path.join(d, "state.json")))["season"]
    else:
        flag = {v: k for k, v in stages.SALT_FLAG.items()}
        salts = {flag[cmd[i]]: int(cmd[i + 1]) for i in range(len(cmd) - 1) if cmd[i] in flag}
        cfg = {"sim": {"food": {"work_cost": 0.03}}, "ecology": {"living_cost": 0.25, "merge_after": None},
               "seed": int(cmd[cmd.index("--seed") + 1]), "holistic_stream_salt": salts.get(H, 0),
               "designed_stream_salt": salts.get(D, 0), "workers": 2}
        json.dump(cfg, open(os.path.join(d, "config.json"), "w"))
        start = 0
    key, cont = scen_key(d), continuation_dir(d)
    log = os.path.join(d, mjbuild.EPA_LOG)
    crash = SCEN["crash"].get(key)
    natives = sum(1 for r in EPA._records(log) if r.get("exit", {}).get("native"))
    crashing = crash is not None and natives < 2
    end = min(seasons, crash["at"]) if crashing else seasons
    _PID[0] += 1
    pid = _PID[0]
    if cont:
        with open(log, "a") as f:
            f.write(json.dumps({"start": "T", "unit": EPA.unit_id(d), "attempt": EPA.attempts(log),
                                "workers": 1 if crashing and natives == 1 else 2, "pid": pid, "libmujoco_sha256": SHA}) + "\n")
    hist = json.load(open(os.path.join(d, "history.json")))["history"] if os.path.exists(os.path.join(d, "history.json")) else []
    hist = [e for e in hist if e["season"] < start]
    ctx = {**ctx_of(d), "extinct": SCEN.get("extinct", {}).get((ctx_of(d)["pid"], ctx_of(d)["j"]), {})}
    with open(os.path.join(d, "lineage.jsonl"), "a") as lf, open(log, "a") if cont else open(os.devnull, "w") as ef:
        for s in range(start, end):
            rows, h = season_rows(ctx, cfg, s)
            lf.write("".join(json.dumps(r) + "\n" for r in rows))
            hist += h
            ef.write(json.dumps({"season": s, "pid": pid}) + "\n")
            if s in SCEN["overflow"].get(key, ()):
                ef.write(json.dumps({"event": "overflow", "unit": EPA.unit_id(d), "attempt": EPA.attempts(log) - 1,
                                     "pid": pid, "seq": s, "nedges": 25, "step": 1}) + "\n")
        if crashing and crash.get("attested", True):
            ef.write(json.dumps({"event": "overflow", "unit": EPA.unit_id(d), "attempt": EPA.attempts(log) - 1,
                                 "pid": pid, "seq": end, "nedges": 25, "step": 2}) + "\n")
    write_state(d, hist, end)
    if cont:
        p = os.path.join(d, "platform.json")
        rec = json.load(open(p)) if os.path.exists(p) else {"mujoco": "3.14.0", "mujoco_build": {"libmujoco_sha256": SHA}, "resumes": []}
        if os.path.exists(p):
            rec["resumes"].append({"mujoco_build": {"libmujoco_sha256": SHA}})
        json.dump(rec, open(p, "w"))
        EPA.write_exit(d, -11 if crashing else 0)
    if crashing:
        raise SystemExit(f"{label}: ecology exited -11 (see {d}/run.log)")


def write_state(d, hist, end):
    json.dump({"history": hist}, open(os.path.join(d, "history.json"), "w"))
    last = [e for e in hist if e["season"] == end - 1]
    json.dump({"season": end, "populations": {e["population"]: [f"{e['population'][0]}F"] * (e["alive"] > 0) for e in last}},
              open(os.path.join(d, "state.json"), "w"))


def toy_run(d, start, end, seed, salts=(0, 0), settings=None, src=None):
    """A stock run (Stage 1 or the census), written directly: no EPA log.  A fork is ``stages.fork_config`` of its
    source, as the lanes make it."""
    if src:
        stages.fork_config(src, d, settings or {})
        cfg = json.load(open(os.path.join(d, "config.json")))
        hist = [e for e in json.load(open(os.path.join(d, "history.json")))["history"] if e["season"] < start]
    else:
        os.makedirs(d, exist_ok=True)
        cfg = {"sim": {"food": {"work_cost": 0.03}}, "ecology": {"living_cost": 0.25, "merge_after": None}, "seed": seed,
               "holistic_stream_salt": salts[0], "designed_stream_salt": salts[1], "workers": 2}
        hist = []
        json.dump(cfg, open(os.path.join(d, "config.json"), "w"))
    ctx = {**ctx_of(d), "extinct": SCEN.get("extinct", {}).get((ctx_of(d)["pid"], ctx_of(d)["j"]), {})}
    with open(os.path.join(d, "lineage.jsonl"), "a") as lf:
        for s in range(start, end):
            rows, h = season_rows(ctx, cfg, s)
            lf.write("".join(json.dumps(r) + "\n" for r in rows))
            hist += h
    write_state(d, hist, end)


# -- building the tree ----------------------------------------------------------------------------------------------- #

SALTS = stages._salts_line(stages.read_launch(os.path.join(REPO, "runs", "RBT-129", "lanes", "1", "launch.txt"))["salts"])


def place(root, j):
    return {**j, **{k: os.path.join(root, j[k]) for k in ("dir", "src", "ref") if k in j},
            "worlds": os.path.join(R.RUNS, "worlds")}


def run_jobs(root, jobs, excl, on_crash=None):
    """The lanes' job loop, restarts included: a job that raises is restarted (a lane restart), a CRASHED refusal is
    ruled by the coordinator (``on_crash`` appends its ``CRASHED:`` record), and the lane goes on re-emitted without it
    (``s2lanes.droppable``)."""
    for j in jobs:
        for _ in range(4):
            if j["name"] in s2lanes.droppable(jobs, *excl):
                break
            try:
                s2lanes.run_job(place(root, j))
                break
            except SystemExit as e:
                if e.code == 4 and on_crash:
                    excl[1].append(R.run_label(j["dir"]))
                    continue
                if isinstance(e.code, str) and "ecology exited -11" in e.code:
                    continue            # the ecology died natively: the lane is restarted
                raise
        else:
            raise AssertionError(f"{j['name']} neither finished nor was dropped")


def write_lanes(root, stage, jobs, excl, points=()):
    d = os.path.join(root, "runs", "RBT-129", "lanes", R.LANES[stage])
    gone = s2lanes.droppable(jobs, *excl)
    if stage == "2a":
        shutil.copytree(os.path.join(REPO, "runs", "RBT-129", "lanes", "S2A"), d)
        for f in os.listdir(d):
            if f.endswith(".jsonl"):
                raw = [json.loads(x) for x in open(os.path.join(d, f)) if x.strip()]
                open(os.path.join(d, f), "w").write("".join(json.dumps(x) + "\n" for x in raw if x["name"] not in gone))
    elif stage == "2b":
        os.makedirs(d)
        gate = s2b.s2b_gate(points)
        open(os.path.join(d, "launch.txt"), "w").write(
            f"hosts 10\ns2b_points {' '.join(points)}\ns2b_m {' '.join(r['point'] for r in gate if r['m'])}\n"
            f"s2b_n {' '.join(r['point'] for r in gate if r['n'])}\n")
        for f, lane in s2b.lane_slices(points, 10).items():
            open(os.path.join(d, f), "w").write("".join(json.dumps(x) + "\n" for x in lane if x["name"] not in gone))
    else:
        shutil.copytree(os.path.join(REPO, "runs", "RBT-129", "lanes", "RB"), d)


def stage1_tree(root):
    for name in ("1", "1-MN"):
        shutil.copytree(os.path.join(REPO, "runs", "RBT-129", "lanes", name), os.path.join(root, "runs", "RBT-129", "lanes", name))
    forks = sr.mn_forks(root)
    for pid in sr.STAGE1_POINTS:
        fk = forks.get(pid, {"M": [], "N": []})
        for j in sr.SEEDS:
            u = os.path.join(root, "runs", "RBT-129", "stage1", pid, str(129000 + j))
            toy_run(os.path.join(u, "S"), 0, 300, 129000 + j, SALTS[129000 + j])
            toy_run(os.path.join(u, "ckpt60"), 0, 60, 129000 + j, SALTS[129000 + j])
            stages._mark(os.path.join(u, "S"), "S")              # Stage 1's lanes marked these (registered data)
            stages._mark(os.path.join(u, "ckpt60"), "ckpt60")
            for arm in ("M", "N"):
                if j in fk[arm] and not (pid == sr.CRASHED_POINT and j == 1 and arm == "M"):
                    st = {"merge_after": 60, "pooled_capacity": 120}
                    if arm == "N":
                        st["merge_null"] = sr.null_kind(j)
                    toy_run(os.path.join(u, arm), 60, 300, 129000 + j, src=os.path.join(u, "ckpt60"), settings=st)
                    stages._mark(os.path.join(u, arm), arm)
    os.makedirs(os.path.join(root, QDIR), exist_ok=True)
    open(os.path.join(root, QDIR, "config.json"), "w").write("{poison")
    for pid in s2.STAGE2A_POINTS:                       # the census S 0-59 the re-simulation and K-SALT compare with
        for j in (1, 2, 3):
            toy_run(os.path.join(root, "runs", "RBT-129", "stage0", pid, str(129000 + j), "S"), 0, 60, 129000 + j)


def scan_lane(root, which):
    """lanes/SCAN with the owner's scan of ``which`` Stage-1 M forks, run through the real fork and scancmp jobs."""
    units, _ = stages.scan_units(R.RUNS)
    jobs = [{**j, **{k: R._rel(j[k]) for k in ("dir", "src", "ref") if k in j}} for u in units for j in u["jobs"]
            if j["name"].split("/")[1:3] in [[p, str(s)] for p, s, _ in which] and j["name"].split("/")[3].startswith("M")]
    d = os.path.join(root, "runs", "RBT-129", "lanes", stages.SCAN_LANES)
    os.makedirs(d)
    open(os.path.join(d, "host0-lane0.jsonl"), "w").write("".join(json.dumps(j) + "\n" for j in jobs))
    for j in jobs:
        stages.run_job(place(root, j))


def registered_from(root):
    """The 'accepted Stage-1 record' of the synthetic tree: its own refit, as the real record is the real data's."""
    s1 = R.stage1_arms(root)
    h = {p: [("1", R.assemble(root, "1", p, sr.SEEDS, s1[p]))] for p in sr.STAGE1_POINTS}
    calls = R.call_map(h, NO_RES)[0]
    hab = [p for p in sr.STAGE1_POINTS if calls[p]["body"] not in sr.HABITABLE_OUT]
    model = sr.world_model([(p, x) for p in hab for x in calls[p]["x"]])
    rej, ps = sr.map_holm(model)
    return {"T": {n: R.t_line(model, ps, rej, n) for n in ("T1", "T2", "T3")},
            "calls": {p: (calls[p]["body"], calls[p]["income"]["call"]) for p in sr.STAGE1_POINTS}}


_FORKS = sr.mn_forks(os.path.join(REPO))
SCANNED = [("c1-p080-U-L", 129000 + j, "M") for j in _FORKS["c1-p080-U-L"]["M"][:2]]
CRASH_M = ("stage2a", "c1-p053-U-L", 129006, "M")       # an attested crash in an M fork (seasons 60-299)
CRASH_S60 = ("rb", "c1-p030-U-G", 129012, "S")          # an attested crash in an S60 phase: its unit has no fork source
OVER_S = [("stage2a", SIGNAL3, 129000 + j, "S") for j in (1, 2, 3)]
OVER_M = ("stage2a", "c1-p053-U-G", 129003, "M")


@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    root = str(tmp_path_factory.mktemp("s2"))
    mp = pytest.MonkeyPatch()
    mp.setenv("NO_DURABLE", "1")
    mp.setattr(stages, "_ecology", toy_ecology)
    mp.setattr(stages, "check_continuation_build", lambda line=None: {})
    mp.setattr(stages, "CONTINUATION_PREFIXES", stages.CONTINUATION_PREFIXES)
    s2lanes.with_s2a_prefix()
    s2b.with_s2b_prefix()
    SCEN["overflow"] = {k: (150,) for k in OVER_S} | {OVER_M: (200,), ("mn-corruption-scan",) + SCANNED[0]: (200,)}
    SCEN["crash"] = {CRASH_M: {"at": 150}, CRASH_S60: {"at": 30}}
    excl = ([], [])
    stage1_tree(root)
    scan_lane(root, SCANNED)
    jobs = {"2a": R.emission("2a"), "rb": R.emission("rb")}
    for st in ("2a", "rb"):
        run_jobs(root, jobs[st], excl, on_crash=True)
        write_lanes(root, st, jobs[st], excl)
    _, lines = R.interim(root, restore=lambda d: None, resolvable=NO_RES, excl=excl)
    path = os.path.join(root, s2b.INTERIM_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("\n".join(lines) + "\n")
    points = s2b.parse_interim("\n".join(lines))
    jobs["2b"] = R.emission("2b", points)
    run_jobs(root, jobs["2b"], excl, on_crash=True)
    write_lanes(root, "2b", jobs["2b"], excl, points)
    yield {"root": root, "excl": excl, "points": points, "interim": lines, "jobs": jobs, "record": registered_from(root)}
    mp.undo()


def _copy(src, dst):
    """A copy of the synthetic tree, with each log's unit names re-homed (outside the repository a run's unit id is its
    absolute path)."""
    shutil.copytree(src, dst)
    for base, _, files in os.walk(dst):
        for n in files:
            if n.startswith("epa_overflow"):
                f = os.path.join(base, n)
                text = open(f).read().replace(json.dumps(src)[1:-1] + "/", json.dumps(dst)[1:-1] + "/")
                open(f, "w").write(text)


# -- the tests ---------------------------------------------------------------------------------------------------------- #

def test_the_layout_override_is_scoped():
    saved = sr.unit_dir, sr.SEEDS
    with R.layout("stage2a", range(1, 9)):
        assert sr.unit_dir("/r", "p", 3).endswith(os.path.join("stage2a", "p", "129003"))
    assert (sr.unit_dir, sr.SEEDS) == saved


def test_the_tree_holds_real_crash_shapes(tree):
    """R-1: the crashed runs have no done-marker, their logs meet RULING item 5's count with both attempts attested,
    and the crashed S60's unit has no ckpt60, S, M or N."""
    root = tree["root"]
    m = os.path.join(root, "runs", "RBT-129", *map(str, CRASH_M))
    assert not os.path.exists(os.path.join(m, ".rbt129-done-M"))
    st = EPA.crash_state(os.path.join(m, "epa_overflow.jsonl"), EPA.unit_id(m))
    assert st and st["attested"]
    u = os.path.join(root, "runs", "RBT-129", *map(str, CRASH_S60[:3]))
    assert not os.path.exists(os.path.join(u, "S", ".rbt129-done-S60")) and not os.path.exists(os.path.join(u, "ckpt60"))
    assert {R.run_label(os.path.relpath(m, root)), R.run_label(os.path.relpath(os.path.join(u, "S"), root))} == set(tree["excl"][1])


def test_the_interim_prints_integrity_and_the_r4_list_only(tree):
    root, excl = tree["root"], tree["excl"]
    written = []
    ilines, lines = R.interim(root, restore=lambda d: None, resolvable=NO_RES, on_integrity=written.append, excl=excl)
    assert written and written[0] == ilines
    it = "\n".join(ilines)
    assert "## S2A: 356 jobs in the emission" in it and "1 omitted by ruled exclusions" in it
    assert "CRASHED: S2A/c1-p053-U-L/129006/M" in it and "crash events (distinct run directories, rule §4.4): 1" in it
    assert f"OVERFLOWED: S2A/{SIGNAL3}/129001/S" in it and "OVERFLOWED: S2A/c1-p053-U-G/129003/M" in it
    assert "gate re-check: PASS" in it and "SKIPPED" not in it                          # R-9: skips folded into done
    text = "\n".join(lines)
    for word in ("EARNS", "NOT RUN", "PARTIAL", "EXCLUDED", "§8 headline", "DEPEND", "x̄"):   # S2-R3: no call, no §8
        assert word not in text, word
    rb = [l.split(":")[0].strip() for l in lines if ": CP " in l]
    assert set(NOISY) <= set(rb) and set(rb) <= set(s2.STAGE2A_POINTS) and len(rb) <= 11
    assert "the R-B caps less GO-1's M 1 and N 0" in text                               # R-4: GO-1's slot deducted


def test_s2b_is_mechanical_from_the_interim(tree):
    """R-4: lanes/S2B is exactly the emission from the interim's R4 list; any other set is refused."""
    root, points = tree["root"], tree["points"]
    lanes = os.path.join(root, "runs", "RBT-129", "lanes", "S2B")
    s2b.check_s2b(lanes, points, excl=tree["excl"])
    assert {j["name"].split("/")[1] for j in tree["jobs"]["2b"]} == set(points)
    gate = {r["point"]: r for r in s2b.s2b_gate(points)}
    assert sum(r["m"] for r in gate.values()) <= 6 - 1 and sum(r["n"] for r in gate.values()) <= 2
    with pytest.raises(SystemExit):
        s2b.check_s2b(lanes, points[:-1], excl=tree["excl"])                              # a point dropped after the fact
    assert s2b.parse_interim("\n".join(tree["interim"])) == points
    with pytest.raises(SystemExit):
        s2b.parse_interim("\n".join(tree["interim"]).replace(f"  {points[0]}: CP", "  c1-p030-U-G: CP"))


@pytest.fixture(scope="module")
def final(tree):
    written = []
    out = R.final(tree["root"], restore=lambda d: None, resolvable=NO_RES, on_integrity=written.append,
                  excl=tree["excl"], record=tree["record"])
    return out, written


def test_the_final_map_end_to_end(tree, final):
    (ilines, flines), written = final
    assert written and written[0] == ilines
    it, text = "\n".join(ilines), "\n".join(flines)
    assert "## RB:" in it and "## S2B:" in it and "CRASHED: RB/c1-p030-U-G/129012/S" in it
    assert "crash events (distinct run directories, rule §4.4): 1" in it                # the S60 crash: one event
    assert "attested crash events: continue" in it and "standing sentence" in it
    assert "## Stage-1 M/N scan" in it and "UNSCANNED" in it
    for section in ("## §8 headline", "NON-REGISTERED (C3-2 literal verdict 5)", "exclude-known-flagged map",
                    "## per-point table", "## families", "## M1 call counts", "## M4 area shares", "## M2:",
                    "M2 sensitivity fit", "M2 share model (registered", "M2 share model (NON-REGISTERED",
                    "## M3 break-evens, final map", "M6 concordance", "## M7", "## §12 registered predictions",
                    "## M3 break-evens, Stage-1 points only", "## §12 scorecard for the Stage-1 points",
                    "per-birth income (C3-5: births 180-238", "the censored 240-299 figure", "T1: stat",
                    "(registered Stage-1 fit, L410-L412; refit and checked, R-7)", "# exclusions"):
        assert section in text, section
    rows = {l.split()[0]: l for l in flines if l.startswith("  c") and " | " in l}
    assert len(rows) == 48
    for p in rows:
        lay = p.split("-")[2]
        if lay == "U" and p not in NOISY + (SIGNAL3,) and "income 0/" not in rows[p]:
            assert "EARNS-H" in rows[p], rows[p]
        if lay == "HP" and "income 0/" not in rows[p]:
            assert "EARNS-D" in rows[p], rows[p]
    assert "EARNS-H MARGINAL" in rows[MARGINAL_PT]                                       # C3-5 on the uncensored measure
    assert "(combined, n 16)" in rows["c1-p010-U-G"] and "(combined, n 15)" in rows["c1-p030-U-G"]


def test_overflow_sensitivity_is_the_whole_map_with_values_beside(final):
    """R-3: excluding the 3 overflowed S seeds that carry SIGNAL3's income changes its call; the line is marked and the
    sensitivity value printed beside it, and the families line that changes with it is marked too."""
    (_, flines), _ = final
    row = next(l for l in flines if l.startswith(f"  {SIGNAL3} ") and " | " in l)
    assert "EARNS-H" in row.split("[OVERFLOW-SENSITIVE")[0] and "[OVERFLOW-SENSITIVE; exclude-known-flagged:" in row
    assert "EARNS-H" not in row.split("exclude-known-flagged:")[1]
    fam = next(l for l in flines if "income EARNS and TIE:" in l)
    assert "OVERFLOW-SENSITIVE" in fam


def test_crashes_in_the_final_map(final):
    """R-1, R-5: the CRASHED M is counted, never read, with its y′ bound; the S60-crashed seed leaves n at its R-B
    point, whose income is CRASH-AFFECTED and whose body call carries the feasible-completion word."""
    (_, flines), _ = final
    m = next(l for l in flines if l.startswith("  c1-p053-U-L ") and " | " in l)
    assert "(1 CRASHED" in m
    assert any(l.startswith("  ") and "y′ bound under arbitrary missingness" in l for l in flines)
    s = next(l for l in flines if l.startswith("  c1-p030-U-G ") and " | " in l)
    assert "CRASH-AFFECTED" in s and "[body " in s and "n 15" in s
    assert "OVERFLOW-SENSITIVE" not in s                         # no flagged seed there: the two analyses agree


def test_a_crash_never_read_and_never_unscanned(tree, tmp_path):
    """R-1: the lanes re-emitted without the crashed S60 cannot make its unit UNSCANNED: the readout derives the units
    from the emission and reads the run as CRASHED from its ruled record, never restoring it."""
    root = str(tmp_path / "t")
    _copy(tree["root"], root)
    states = R.integrity(root, {"rb": tree["jobs"]["rb"]}, lambda d: None, tree["excl"])[1]["rb"]
    assert states[("c1-p030-U-G", 129012, "S")] == s2.CRASHED
    assert all(states[("c1-p030-U-G", 129012, a)] in (s2.CRASHED,) for a in ("S",))
    restored = []
    guard = R.guarded_restore(root, restored.append, tree["excl"][0])
    R.integrity(root, {"rb": tree["jobs"]["rb"]}, guard, tree["excl"])
    assert not any("129012" in d and "c1-p030-U-G" in d for d in restored)


def test_a_crash_reads_from_its_log_until_ruled_and_an_unattested_one_is_a_help(tree, tmp_path):
    """R-1: a lane that omits a run no record rules is a HELP; an attested crash not yet ruled reads from its own log as
    CRASHED (rule §4.3: the hive does not stop); an unattested one is a HELP."""
    root = str(tmp_path / "t")
    _copy(tree["root"], root)
    jobs = tree["jobs"]["2a"]
    with pytest.raises(R.Help, match="not the emission"):
        R.integrity(root, {"2a": jobs}, lambda d: None, ([], []))
    lanes = os.path.join(root, "runs", "RBT-129", "lanes", "S2A")
    shutil.rmtree(lanes)
    shutil.copytree(os.path.join(REPO, "runs", "RBT-129", "lanes", "S2A"), lanes)    # as emitted, nothing dropped
    states = R.integrity(root, {"2a": jobs}, lambda d: None, ([], []))[1]["2a"]
    assert states[CRASH_M[1:]] == s2.CRASHED
    m = os.path.join(root, "runs", "RBT-129", *map(str, CRASH_M))
    log = os.path.join(m, "epa_overflow.jsonl")
    kept = [x for x in open(log) if '"overflow"' not in x]
    open(log, "w").write("".join(kept))
    with pytest.raises(R.Help, match="unattested"):
        R.integrity(root, {"2a": jobs}, lambda d: None, ([], []))


def test_an_incomplete_stage_and_a_failed_s60cmp_are_a_help(tree, tmp_path):
    root = str(tmp_path / "t")
    _copy(tree["root"], root)
    os.remove(os.path.join(root, "runs", "RBT-129", "stage2a", "c05-p080-U-G", "129004", "S", ".rbt129-done-S"))
    with pytest.raises(R.Help, match="not complete"):
        R.integrity(root, {"2a": tree["jobs"]["2a"]}, lambda d: None, tree["excl"])
    root2 = str(tmp_path / "t2")
    _copy(tree["root"], root2)
    open(os.path.join(root2, "runs", "RBT-129", "stage2a", "c05-p080-U-G", "129001", "s60cmp", "S60CMP.txt"), "w").write(
        "S60CMP DIFFER: synthetic\n")
    with pytest.raises(R.Help, match="S60CMP"):
        R.integrity(root2, {"2a": tree["jobs"]["2a"]}, lambda d: None, tree["excl"])


def test_the_registered_stage1_values_are_checked(tree):
    """R-7: a refit that does not reproduce the accepted record (T1-T3, or a Stage-1 call) is a HELP."""
    bad = {"T": {**tree["record"]["T"], "T1": "stat 69.704, p 1.181e-13 REJECTED"}, "calls": tree["record"]["calls"]}
    with pytest.raises(R.Help, match="T1"):
        R.final(tree["root"], restore=lambda d: None, resolvable=NO_RES, excl=tree["excl"], record=bad)
    rec = R.registered_stage1()
    assert rec["T"]["T1"] == "stat 69.704, p 1.181e-13 REJECTED" and rec["calls"]["c0-p010-U-G"] == ("NOT RUN", "EARNS-D")
    assert len(rec["calls"]) == 36


def test_the_arms_under_each_rule():
    st = {("p", 129001, "S"): s2.CLEAN, ("p", 129001, "M"): s2.OVERFLOWED, ("p", 129002, "S"): s2.OVERFLOWED,
          ("p", 129002, "M"): s2.CLEAN, ("p", 129003, "S"): s2.CRASHED, ("p", 129004, "S"): s2.CLEAN,
          ("p", 129004, "M"): s2.CRASHED, ("p", 129004, "N"): s2.CRASHED, ("p", 129005, "S"): s2.CLEAN,
          ("p", 129005, "M"): "SKIPPED", ("p", 129006, "S"): R.EXCLUDED}
    inc = R.arms_for(st, "p", range(1, 7), "include-flagged")
    assert inc["void"] == [3, 6] and inc["s_crashed"] == [3] and inc["m"] == [1, 2, 4] and inc["m_crashed"] == [4]
    assert inc["n_crashed"] == [4] and inc["n"] == []                                    # R-5: a CRASHED N is reported
    exc = R.arms_for(st, "p", range(1, 7), "exclude-known-flagged")
    assert exc["void"] == [2, 3, 6] and exc["m_out"] == [1, 4] and exc["s_excluded"] == [2]


def test_y_bound():
    assert R.y_bound([0.1, 0.3], [0.5]) == pytest.approx(((0.4 - 0.5) / 3, (0.4 + 0.5) / 3))
    assert R.y_bound([0.1], [None]) is None


def test_the_drivers_sit_outside_the_pinned_trees_and_the_labels_are_disjoint():
    for f in (SCRIPT, os.path.join(REPO, "runs", "RBT-129", "stage2", "s2b.py")):
        for t in stages.PINNED_TREES:
            assert not os.path.abspath(f).startswith(os.path.join(REPO, t) + os.sep)
    pre = {st: stages._label(os.path.join(stages.RUNS, d, "p")).rsplit("-p", 1)[0] + "-" for st, d in R.STAGE_DIRS.items()}
    assert len(set(pre.values())) == 4
    assert not any(a != b and pre[a].startswith(pre[b]) for a in pre for b in pre)
    with pytest.raises(sr.QuarantineRefusal):
        R.guarded_restore(REPO, lambda d: None)(os.path.join(REPO, sr.QUARANTINED_DIR))


def test_main_refuses_while_the_locks_are_closed():
    for step, go in (("interim", "RBT129-S2-INTERIM-GO-1"), ("final", "RBT129-S2-FINAL-GO-1")):
        if s2.refusal(step, go):
            assert R.main([step, "--go", go]) == 9


def _git(cwd, *a):
    import subprocess
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_the_s2b_runner_gates(tree, tmp_path):
    """The 2b(2a) lane's own gates: every job a 2b(2a) job of the gate; the code by blob; and on the merged base the
    2a GO (FC-2), 2B2A COMMITTED, GO-ID-INTERIM open and the committed interim output (exit 10 otherwise)."""
    points = tree["points"]
    gate = s2b.s2b_gate(points)
    launch = {"s2b_points": " ".join(points), "s2b_m": " ".join(r["point"] for r in gate if r["m"]),
              "s2b_n": " ".join(r["point"] for r in gate if r["n"])}
    jobs = [place(R.ROOT, j) for j in tree["jobs"]["2b"]]
    s2b.check_lane_s2b(jobs, launch)
    m = {**jobs[2], "job": "fork", "name": jobs[2]["name"].rsplit("/", 1)[0] + "/M", "dir": jobs[2]["dir"][:-1] + "M",
         "src": jobs[2]["dir"][:-1] + "ckpt60", "seed_rule": True, "set": {"merge_after": 60, "pooled_capacity": 120}}
    with pytest.raises(SystemExit) as e:
        s2b.check_lane_s2b(jobs + [m], launch)                       # an M the gate did not admit
    assert e.value.code == 4
    pins = s2b.code_pins()
    assert set(pins) == {f"code:{p}" for p in s2b.CODE_FILES}
    s2b.check_code(pins, loaded=s2b.CODE_FILES)
    with pytest.raises(SystemExit) as e:
        s2b.check_code({k: v for k, v in pins.items() if "s2b" not in k}, loaded=s2b.CODE_FILES)
    assert e.value.code == 5
    # the GO checks, in a scratch repository whose origin is a local bare repository
    origin, work = str(tmp_path / "o.git"), str(tmp_path / "w")
    _git(str(tmp_path), "init", "-q", "--bare", origin)
    _git(str(tmp_path), "init", "-q", work)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        _git(work, "config", k, v)
    _git(work, "remote", "add", "origin", origin)
    rel = s2lanes.RULINGS_REL
    os.makedirs(os.path.join(work, os.path.dirname(rel)))
    text = open(os.path.join(REPO, rel)).read()
    for msg, t in (("base", text), ("open the 2a GO", text.replace("GO-ID-2A-PENDING:", "GO-ID-2A:"))):
        open(os.path.join(work, rel), "w").write(t)
        _git(work, "add", "-A")
        _git(work, "commit", "-q", "-m", msg)
    _git(work, "push", "-q", "origin", "HEAD:refs/heads/b")
    with pytest.raises(SystemExit) as e:
        s2b.check_go_2b("b", work)                                    # GO-ID-INTERIM still pending
    assert e.value.code == 10
    open(os.path.join(work, rel), "w").write(open(os.path.join(work, rel)).read().replace("GO-ID-INTERIM-PENDING:", "GO-ID-INTERIM:"))
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", "open the interim")
    _git(work, "push", "-q", "origin", "HEAD:refs/heads/b")
    with pytest.raises(SystemExit) as e:
        s2b.check_go_2b("b", work)                                    # no committed interim output
    assert e.value.code == 10
    os.makedirs(os.path.join(work, os.path.dirname(s2b.INTERIM_REL)), exist_ok=True)
    open(os.path.join(work, s2b.INTERIM_REL), "w").write("\n".join(tree["interim"]) + "\n")
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", "the interim output")
    _git(work, "push", "-q", "origin", "HEAD:refs/heads/b")
    blob = s2b.check_go_2b("b", work)
    assert len(blob) == 40 and s2b.interim_points("origin/b", work) == points
