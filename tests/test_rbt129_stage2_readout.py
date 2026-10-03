"""RBT-129 Stage 2's readout drivers (runs/RBT-129/stage2/s2readout.py), end to end on a synthetic tree.

No Stage-2 output exists.  The tree is made here: Stage 1 (36 points x 8 seeds, M and N as lanes/1-MN admits them, the
CRASHED unit's directory poisoned), Stage 2a and R-B as their committed lanes list them, and 2b(2a) at the points the
interim's R4 list names, every continuation arm with its build record (epa_overflow.jsonl, platform.json)."""
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
sr, s2, stages = R.sr, R.s2, R.stages
H, D = sr.H, sr.D
EPA = s2.registered_epa()
QDIR = sr.QUARANTINED_DIR
NO_RES = lambda lo, hi, rule, n, reps: ([(0.0, 0.0, 0.0, 0.0, False)] * 2, False)


def _hist(alive_by, lo=0, hi=299):
    return [{"season": s, "population": k, "alive": f(s), "births": 0, "deaths": 0} for s in range(lo, hi + 1)
            for k, f in alive_by.items() if f(s) > 0]


def _rows(kind, food, lo=180, hi=299, n=2):
    return [{"generation": s, "population": kind, "name": f"{kind[0]}{i}", "parents": [], "fitness": food, "nodes": 5,
             "energy": 2.0, "age": s - lo + 1, "evals": s - lo + 1, "last_score": food, "food": food, "work": 0.0}
            for s in range(lo, hi + 1) for i in range(n)]


def _run(d, hist, rows, season=300):
    os.makedirs(d, exist_ok=True)
    json.dump({"sim": {"food": {"work_cost": 0.03}}, "ecology": {"living_cost": 0.25}}, open(os.path.join(d, "config.json"), "w"))
    json.dump({"history": hist}, open(os.path.join(d, "history.json"), "w"))
    json.dump({"season": season, "populations": {H: [1], D: [1]}}, open(os.path.join(d, "state.json"), "w"))
    with open(os.path.join(d, "lineage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _build_record(d, start, overflow_at=()):
    """The registered build's record of one continuation run: platform.json and an epa_overflow.jsonl in the tooling's
    format, one clean attempt that ran seasons start-299, with overflows at ``overflow_at``."""
    json.dump({"mujoco": "3.14.0", "mujoco_build": {"libmujoco_sha256": s2.REGISTERED_SHA}, "resumes": []},
              open(os.path.join(d, "platform.json"), "w"))
    u = EPA.unit_id(d)
    out = [{"start": "T", "unit": u, "attempt": 1, "workers": 2, "pid": 7, "libmujoco_sha256": s2.REGISTERED_SHA}]
    for s in range(start, 300):
        out.append({"season": s, "pid": 7})
        if s in overflow_at:
            out.append({"event": "overflow", "unit": u, "attempt": 1, "pid": 8, "seq": s, "nedges": 25, "step": 1})
    out.append({"exit": {"attempt": 1, "code": 0, "signal": None, "native": False}})
    with open(os.path.join(d, "epa_overflow.jsonl"), "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in out))


def _mark(d, tag, note=""):
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, f".rbt129-done-{tag}"), "w").write("2026-10-04T00:00:00Z" + (f" {note}" if note else ""))


def _chain(u, j, gain, m=False, n=False, h_alive=True):
    hist = _hist({H: (lambda s: 2) if h_alive else (lambda s: 2 if s < 30 else 0), D: lambda s: 2})
    _run(os.path.join(u, "S"), hist, (_rows(H, 1.0 + gain + 0.01 * j) if h_alive else []) + _rows(D, 1.0))
    _run(os.path.join(u, "ckpt60"), [e for e in hist if e["season"] <= 59], [], season=60)
    if m:
        _run(os.path.join(u, "M"), _hist({H: lambda s: 60 + j % 8, D: lambda s: 60 - j % 8}, lo=60), _rows(H, 1.2) + _rows(D, 1.0))
    if n:
        k = sr.null_kind(j)
        _run(os.path.join(u, "N"), _hist({k: lambda s: 60, "null_b": lambda s: 60}, lo=60), _rows(k, 1.0))


GAIN = {"U": 0.3, "HP": -0.3, "PW": 0.0}
#: 2a points whose income is noise around 0 (UNDECIDED, so R4-eligible as NOT RUN with an UNDECIDED income call)
NOISY = ("c05-p030-U-G", "c15-p010-U-G")


def _continuation(root, stage, overflow=()):
    """Every arm a stage's lanes list, with its markers and build record; ``overflow`` names (point, seed, arm) whose
    run logs an overflow."""
    jobs = R.lane_jobs(root, stage)
    units = {}
    for j in jobs:
        pid, sd, tag = j["name"].split("/")[1:]
        units.setdefault((pid, int(sd)), set()).add(tag)
    for (pid, sd), tags in units.items():
        u = os.path.join(root, "runs", "RBT-129", R.STAGE_DIRS[stage], pid, str(sd))
        jj = sd - 129000
        gain = 0.3 * (-1) ** jj if stage == "2a" and pid in NOISY else GAIN[pid.split("-")[2]]
        _chain(u, jj, gain, m="M" in tags, n="N" in tags)
        for arm, start in (("S", 0), ("M", 60), ("N", 60)):
            if os.path.isdir(os.path.join(u, arm)):
                _build_record(os.path.join(u, arm), start, (150,) if (pid, sd, arm) in overflow else ())
        for tag in tags:
            d = {"S60": "S", "S60CMP": "s60cmp", "KSALT": "ksalt"}.get(tag, tag)
            _mark(os.path.join(u, d), tag)
        if "S60CMP" in tags:
            open(os.path.join(u, "s60cmp", "S60CMP.txt"), "w").write("S60CMP IDENTICAL: synthetic\n")
        if "KSALT" in tags:
            open(os.path.join(u, "ksalt", "KSALT.txt"), "w").write("KSALT PASS: synthetic\n")


def _tree(root):
    lanes = os.path.join(root, "runs", "RBT-129", "lanes")
    for name in ("1-MN", "S2A", "RB"):
        shutil.copytree(os.path.join(REPO, "runs", "RBT-129", "lanes", name), os.path.join(lanes, name))
    forks = sr.mn_forks(root)
    table = sr.parse_gate_table(os.path.join(lanes, "1-MN", "gate_table.txt"))
    for pid in sr.STAGE1_POINTS:
        fk = forks.get(pid, {"M": [], "N": []})
        k = table.get(pid, (None,))[0]
        for j in sr.SEEDS:
            alive = j in fk["M"] if fk["M"] else (k is None or j <= k)
            _chain(os.path.join(root, "runs", "RBT-129", "stage1", pid, str(129000 + j)), j, GAIN[pid.split("-")[2]],
                   m=j in fk["M"] and not (pid == sr.CRASHED_POINT and j == 1), n=j in fk["N"], h_alive=alive)
    os.makedirs(os.path.join(root, QDIR), exist_ok=True)
    open(os.path.join(root, QDIR, "config.json"), "w").write("{poison")
    _continuation(root, "2a", overflow={("c1-p053-U-G", 129003, "M")})
    _continuation(root, "rb", overflow={("c0-p010-HP-G", 129010, "S")})


def _s2b(root, points):
    """lanes/S2B as the 2b(2a) emitter will write it: S at seeds 9-16 at the R4 points (M/N omitted here)."""
    d = os.path.join(root, "runs", "RBT-129", "lanes", "S2B")
    os.makedirs(d)
    with open(os.path.join(d, "host0-lane0.jsonl"), "w") as f:
        for pid in points:
            for j in range(9, 17):
                u = f"runs/RBT-129/stage2b/{pid}/{129000 + j}"
                for tag, kind, sub in (("S60", "fresh", "S"), ("ckpt60", "snapshot", "ckpt60"), ("S", "resume", "S")):
                    f.write(json.dumps({"job": kind, "name": f"S2B/{pid}/{129000 + j}/{tag}", "dir": f"{u}/{sub}",
                                        "seed": 129000 + j}) + "\n")
    _continuation(root, "2b")


@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    root = str(tmp_path_factory.mktemp("s2"))
    _tree(root)
    return root


def test_the_layout_override_is_scoped():
    saved = sr.unit_dir, sr.SEEDS
    with R.layout("stage2a", range(1, 9)):
        assert sr.unit_dir("/r", "p", 3).endswith(os.path.join("stage2a", "p", "129003"))
    assert (sr.unit_dir, sr.SEEDS) == saved


def test_the_interim_prints_integrity_and_the_r4_list_only(tree):
    restored, written = [], []
    ilines, lines = R.interim(tree, restore=restored.append, resolvable=NO_RES, on_integrity=written.append)
    assert written and written[0] == ilines                      # integrity is handed over first
    assert all(QDIR not in os.path.relpath(d, tree) for d in restored)
    it = "\n".join(ilines)
    assert "## S2A: 356 jobs" in it and "OVERFLOWED: S2A/c1-p053-U-G/129003/M" in it and "crash ceiling" in it
    text = "\n".join(lines)
    assert "## R4 list for 2b(2a)" in text and "core-h" in text
    for word in ("EARNS", "NOT RUN", "PARTIAL", "EXCLUDED", "§8 headline", "DEPEND", "x̄"):   # S2-R3: no call, no §8
        assert word not in text, word
    rb = [l.split(":")[0].strip() for l in lines if ": CP " in l]
    assert rb and set(rb) <= set(s2.STAGE2A_POINTS) and len(rb) <= 11


def test_the_final_map_end_to_end(tree):
    _, lines = R.interim(tree, restore=lambda d: None, resolvable=NO_RES)
    _s2b(tree, [l.split(":")[0].strip() for l in lines if ": CP " in l])
    restored = []
    ilines, flines = R.final(tree, restore=restored.append, resolvable=NO_RES)
    assert all(QDIR not in os.path.relpath(d, tree) for d in restored)
    it = "\n".join(ilines)
    assert "## RB:" in it and "## S2B:" in it and "OVERFLOWED: RB/c0-p010-HP-G/129010/S" in it
    assert "standing sentence" in it
    text = "\n".join(flines)
    for section in ("## §8 headline", "NON-REGISTERED (C3-2 literal verdict 5)", "exclude-known-flagged map",
                    "## per-point table", "## families", "## M2 (registered", "## M2 sensitivity fit", "## M3 break-evens",
                    "## M1 and M4", "## M7", "## §12", "NON-REGISTERED: gated out at", "# exclusions"):
        assert section in text, section
    table = [l for l in flines if l.startswith("  c") and " income " in l]
    assert len(table) == 48
    assert any("(combined, n 16" in l for l in table)          # the R-B / 2b(2a) halves are combined
    assert "PERCEPTION NOT MEASURED" in text


def test_a_missing_marker_is_a_help(tree, tmp_path):
    root = str(tmp_path / "t")
    shutil.copytree(tree, root)
    victim = os.path.join(root, "runs", "RBT-129", "stage2a", "c05-p080-U-G", "129004", "S", ".rbt129-done-S")
    os.remove(victim)
    with pytest.raises(R.Help):
        R.interim(root, restore=lambda d: None, resolvable=NO_RES)


def test_a_failed_s60cmp_and_a_wrong_build_are_a_help(tree, tmp_path):
    root = str(tmp_path / "t")
    shutil.copytree(tree, root)
    u = os.path.join(root, "runs", "RBT-129", "stage2a", "c05-p080-U-G", "129001")
    open(os.path.join(u, "s60cmp", "S60CMP.txt"), "w").write("S60CMP DIFFER: synthetic\n")
    with pytest.raises(R.Help):
        R.interim(root, restore=lambda d: None, resolvable=NO_RES)
    open(os.path.join(u, "s60cmp", "S60CMP.txt"), "w").write("S60CMP IDENTICAL: synthetic\n")
    json.dump({"mujoco_build": {"libmujoco_sha256": "0" * 64}}, open(os.path.join(u, "S", "platform.json"), "w"))
    with pytest.raises(R.Help):
        R.interim(root, restore=lambda d: None, resolvable=NO_RES)


def test_the_arms_under_each_rule():
    st = {("p", 129001, "S"): s2.CLEAN, ("p", 129001, "M"): s2.OVERFLOWED, ("p", 129002, "S"): s2.OVERFLOWED,
          ("p", 129002, "M"): s2.CLEAN, ("p", 129003, "S"): s2.CRASHED, ("p", 129004, "S"): s2.CLEAN,
          ("p", 129004, "M"): s2.CRASHED, ("p", 129005, "S"): s2.CLEAN, ("p", 129005, "M"): "SKIPPED"}
    inc = R.arms_for(st, "p", range(1, 6), "include-flagged")
    assert inc["void"] == [3] and inc["s_crashed"] == [3] and inc["m"] == [1, 2, 4] and inc["crashed"] == [4]
    exc = R.arms_for(st, "p", range(1, 6), "exclude-known-flagged")
    assert exc["void"] == [2, 3] and exc["m"] == [4] and exc["crashed"] == [4]


def test_main_refuses_while_the_locks_are_closed():
    for step, go in (("interim", "RBT129-S2-INTERIM-GO-1"), ("final", "RBT129-S2-FINAL-GO-1")):
        if s2.refusal(step, go):
            assert R.main([step, "--go", go]) == 9


def _crash_log(d, start, attested=True):
    """Two consecutive native attempts, the second at workers 1 (RULING item 5's count); attested when each attempt's
    own pid, dying on SIGSEGV, wrote an overflow line after its last season line."""
    u = EPA.unit_id(d)
    out = []
    for a, (pid, workers) in enumerate(((7, 2), (9, 1)), 1):
        out.append({"start": "T", "unit": u, "attempt": a, "workers": workers, "pid": pid, "libmujoco_sha256": s2.REGISTERED_SHA})
        out += [{"season": s, "pid": pid} for s in range(start, start + 5)]
        if attested:
            out.append({"event": "overflow", "unit": u, "attempt": a, "pid": pid, "seq": 1, "nedges": 25, "step": 1})
        out.append({"exit": {"attempt": a, "code": None, "signal": 11, "native": True}})
    with open(os.path.join(d, "epa_overflow.jsonl"), "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in out))


def _unit(root, pid, sd, arm=""):
    return os.path.join(root, "runs", "RBT-129", "stage2a", pid, str(sd), arm)


def _rule_cases(root):
    """An S60-phase overflow (S's own log at season 30, M and N inheriting it through their source log, A2); an UNLOGGED
    S (a season with no season line); an attested CRASHED M and an attested CRASHED S, at two points."""
    u = _unit(root, "c1-p018-PW-L", 129004)
    _build_record(os.path.join(u, "S"), 0, (30,))
    lines = open(os.path.join(u, "S", "epa_overflow.jsonl")).readlines()
    src = lines[:next(i for i, l in enumerate(lines) if json.loads(l).get("season") == 60)]  # the copy taken at 60
    for arm in ("M", "N"):
        open(os.path.join(u, arm, "epa_overflow.source.jsonl"), "w").write("".join(src))
    log = os.path.join(_unit(root, "c05-p080-U-G", 129005, "S"), "epa_overflow.jsonl")
    kept = [l for l in open(log) if json.loads(l).get("season") != 200]
    open(log, "w").write("".join(kept))
    _crash_log(_unit(root, "c1-p053-U-L", 129006, "M"), 60)
    _crash_log(_unit(root, "c15-p030-U-G", 129007, "S"), 0)


def test_the_rule_cases_end_to_end(tree, tmp_path):
    root = str(tmp_path / "t")
    shutil.copytree(tree, root)
    _rule_cases(root)
    ilines, _ = R.interim(root, restore=lambda d: None, resolvable=NO_RES)
    it = "\n".join(ilines)
    for arm in ("S", "M", "N"):                                   # the S60 phase reaches S, M and N (A2)
        assert f"OVERFLOWED: S2A/c1-p018-PW-L/129004/{arm}" in it, arm
    assert "OVERFLOWED: S2A/c1-p018-PW-L/129005/M" not in it      # a clean neighbour stays clean
    assert "UNLOGGED: S2A/c05-p080-U-G/129005/S" in it
    assert "CRASHED: S2A/c1-p053-U-L/129006/M" in it and "CRASHED: S2A/c15-p030-U-G/129007/S" in it
    assert "2 attested crash events: continue" in it
    states = R.integrity(root, ("2a",), lambda d: None)[1]["2a"]
    inc = R.arms_for(states, "c15-p030-U-G", s2.SEEDS_HALF1, "include-flagged")
    assert inc["void"] == [7] and inc["s_crashed"] == [7]          # a CRASHED S leaves n with its arms
    assert R.crashed_s_merges(root, {"2a": states}) == {"c15-p030-U-G": {7: (True, True)}}   # its ckpt60 at 59
    inc = R.arms_for(states, "c1-p053-U-L", s2.SEEDS_HALF1, "include-flagged")
    assert inc["crashed"] == [6] and 6 in inc["m"]                 # a CRASHED M is counted, never read
    exc = R.arms_for(states, "c1-p018-PW-L", s2.SEEDS_HALF1, "exclude-known-flagged")
    assert 4 in exc["void"] and 4 not in exc["m"] and 4 not in exc["n"]
    exc = R.arms_for(states, "c05-p080-U-G", s2.SEEDS_HALF1, "exclude-known-flagged")
    assert 5 in exc["void"]                                        # UNLOGGED is flagged (rule §4.6)
    if not os.path.isdir(os.path.join(root, "runs", "RBT-129", "lanes", "S2B")):
        _s2b(root, [l.split(":")[0].strip() for l in R.interim(root, lambda d: None, NO_RES)[1] if ": CP " in l])
    _, flines = R.final(root, restore=lambda d: None, resolvable=NO_RES)
    text = "\n".join(flines)
    assert "# exclusions" in text and len([l for l in flines if l.startswith("  c") and " income " in l]) == 48
    row = next(l for l in flines if l.startswith("  c15-p030-U-G ") and " income " in l)
    assert "CRASH-AFFECTED" in row and "[body crash-robust]" in row  # one seed cannot move NOT RUN (plan §3.4)


def test_an_unattested_crash_and_the_ceiling_are_a_help(tree, tmp_path):
    root = str(tmp_path / "t")
    shutil.copytree(tree, root)
    _crash_log(_unit(root, "c1-p053-U-L", 129006, "M"), 60, attested=False)
    with pytest.raises(R.Help, match="unattested"):
        R.interim(root, restore=lambda d: None, resolvable=NO_RES)
    _crash_log(_unit(root, "c1-p053-U-L", 129006, "M"), 60)
    _crash_log(_unit(root, "c1-p053-U-L", 129007, "M"), 60)       # a second at one point (S2-R2)
    with pytest.raises(R.Help, match="ceiling"):
        R.interim(root, restore=lambda d: None, resolvable=NO_RES)


def test_the_drivers_sit_outside_the_pinned_trees_and_the_labels_are_disjoint():
    """NOTE 17; finding 13 (g): the labels of Stage 1, 2a, GO-1 and 2b(2a) are disjoint (no stage's label prefix is
    another's), and the readers go through the guarded, quarantine-checked restore."""
    for t in stages.PINNED_TREES:
        assert not os.path.abspath(SCRIPT).startswith(os.path.join(REPO, t) + os.sep)
    pre = {st: stages._label(os.path.join(stages.RUNS, d, "p")).rsplit("-p", 1)[0] + "-" for st, d in R.STAGE_DIRS.items()}
    assert len(set(pre.values())) == 4
    assert not any(a != b and pre[a].startswith(pre[b]) for a in pre for b in pre)
    with pytest.raises(sr.QuarantineRefusal):
        R.guarded_restore(REPO, lambda d: None)(os.path.join(REPO, sr.QUARANTINED_DIR))
