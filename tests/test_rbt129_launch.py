"""RBT-129 launch readiness (runs/RBT-129/launch/): the world blocks, the pre-launch prints and the Stage P / Stage 0
launchers.  Nothing here runs a sweep arm: the runner is exercised on a tiny non-sweep world only."""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch"))
import blocks  # noqa: E402
import prints  # noqa: E402
import stages  # noqa: E402

from rabbitstew.ecology import Ecology  # noqa: E402
from rabbitstew.cli import build_parser, ecology_configs  # noqa: E402
from rabbitstew.world import Scenery, Shape  # noqa: E402
from rabbitstew import quat  # noqa: E402


def test_the_grid_is_150_unique_ids_that_parse_back():
    ids = blocks.all_ids()
    assert len(ids) == 150 == len(set(ids))
    for pid in ids:
        assert blocks.point_id(*blocks.parse_id(pid)) == pid
    assert "c1-p030-PW-G" in ids and "c05-p018-HP-L" in ids and "c15-p053-U-G" in ids
    assert set(blocks.PILOT) | set(blocks.ANCHORS) | set(blocks.PAYS_CELLS) <= set(ids)
    assert len(blocks.PAYS_CELLS) == 18 == len(set(blocks.PAYS_CELLS))


@pytest.mark.parametrize("layout,counts,radius", [("U", (0, 7, 14, 21, 28), 2.6), ("HP", (0, 7, 14, 21, 28), 2.6),
                                                  ("PW", (0, 16, 32, 48, 64), 3.6)])
def test_obstacle_counts_are_the_registered_free_area_counts(layout, counts, radius):
    for c, n in zip(blocks.CLUTTER, counts):
        argv = blocks.world_argv(blocks.point_id(c, 0.03, layout, "G"))
        args = build_parser().parse_args(["ecology", *argv])
        if n == 0:
            assert args.terrain == "flat"
        else:
            assert (args.terrain, args.obstacles, args.obstacle_radius) == ("random", n, radius)


def test_the_axes_reach_the_config():
    b = blocks.block("c2-p053-PW-G")["block"]
    assert b["sim.world.random_obstacles"] == 64 and b["sim.world.random_radius"] == 3.6
    assert b["sim.food.work_cost"] == 0.053 and b["sim.food.smell_contrast"] == 2.5 and b["sim.food.smell_tau"] == 2.0
    assert (b["sim.food.patches"], b["sim.food.patch_radius"], b["sim.food.radius"]) == (2, 0.4, 4.0)
    assert (b["sim.food.regrow_delay"], b["sim.food.smell"], b["sim.food.decay"]) == (60.0, "log", 1.5)
    assert b["sim.food.eat_from"] == "root" and b["ecology.sweep_log"] is True
    assert (b["ecology.living_cost"], b["ecology.initial_energy"], b["ecology.capacity"], b["ecology.group_size"]) == (0.25, 3.0, 60, 4)
    u = blocks.block("c1-p010-U-L")["block"]
    assert u["sim.food.patches"] == 0 and u["sim.food.radius"] == 3.0 and "sim.food.smell_contrast" not in u
    assert u["sim.world.terrain"] == "random" and u["sim.world.random_obstacles"] == 14 and u["sim.world.random_radius"] == 2.6
    assert blocks.block("c0-p030-U-L")["block"]["sim.world.terrain"] == "flat"
    for f in blocks.ARM_FIELDS:
        assert f not in u


def test_a_block_is_the_config_json_the_ecology_writes(tmp_path):
    """The export's block is read from the config.json that `ecology` itself writes for those flags (no season run)."""
    pid = "c1-p030-PW-G"
    exported = json.loads(open(blocks.export(str(tmp_path / "worlds"), [pid])[0]).read())
    assert exported["id"] == pid and exported["fair_pending"] is True and exported["argv"] == blocks.world_argv(pid)
    args = build_parser().parse_args(["ecology", *exported["argv"], "--seed", "129001", "--seasons", "300"])
    evo, eco = ecology_configs(args)
    Ecology(evo, eco, out_dir=str(tmp_path / "arm"), log=None)  # writes config.json at construction; runs nothing
    written = blocks._flatten(json.loads((tmp_path / "arm" / "config.json").read_text()))
    assert exported["block"] == {k: v for k, v in written.items() if k not in blocks.ARM_FIELDS}
    assert written["seed"] == 129001 and written["ecology.seasons"] == 300


def test_fair_flags_enter_argv_and_block():
    b = blocks.block("c1-p030-U-L", fair=["--motor-budget", "1.77"])
    assert b["fair_pending"] is False and b["argv"][-3:] == ["--motor-budget", "1.77", "--sweep-log"]
    assert b["block"]["sim.world.motor_budget"] == 1.77 and "sim.world.motor_budget" not in blocks.block("c1-p030-U-L")["block"]


def test_footprint_mask_on_constructed_obstacles():
    box = Scenery(Shape.BOX, (1.0, 0.2, 0.3), (0.0, 0.0, 0.15), tuple(quat.yaw(np.pi / 2)))  # long axis along y
    cyl = Scenery(Shape.CYLINDER, (0.3, 0.05), (2.0, 0.0, 0.025))  # 5 cm tall
    sph = Scenery(Shape.SPHERE, (0.5,), (-2.0, 0.0, -0.3))  # sunk: ground circle radius 0.4
    items = np.array([[0.0, 0.45], [0.45, 0.0], [2.0, 0.25], [2.0, 0.35], [-2.0, 0.39], [-2.0, 0.41], [5.0, 5.0]])
    assert prints.footprint_mask(items, [box, cyl, sph]).tolist() == [True, False, True, False, True, False, False]
    assert prints.footprint_mask(items, [box, cyl, sph], tall=0.1).tolist() == [True, False, False, False, True, False, False]
    # the reach-limited mask: deeper than 0.20 m from every edge.  The 0.2 m-wide box has no such interior at all; a
    # 0.6 m-wide one (half-length 0.5) does, as does the sphere's 0.4 m circle
    deep = np.array([[0.0, 0.25], [0.0, 0.35], [-2.0, 0.15], [-2.0, 0.25]])
    assert not prints.footprint_mask(deep[:2], [box], tall=0.1, margin=0.2).any()
    wide = Scenery(Shape.BOX, (1.0, 0.6, 0.3), (0.0, 0.0, 0.15), tuple(quat.yaw(np.pi / 2)))
    assert prints.footprint_mask(deep, [wide, cyl, sph], tall=0.1, margin=0.2).tolist() == [True, False, True, False]


def test_unreachable_share_is_zero_on_flat_and_positive_in_clutter():
    assert prints.unreachable("c0-p030-U-L", 3)[:3] == (0.0, 0.0, 0.0)
    share, tall, deep, total = prints.unreachable("c2-p030-U-L", 10)
    assert total == 120 and 0.0 <= deep <= tall <= share < 1.0 and share > 0


def test_food_per_new_cell_covers_ground():
    key, food, cells = prints.cell_season(("k", "c0-p030-U-L", "pioneer-drive", 1000, [], list(blocks.EAT_CANDIDATE)))
    assert key == "k" and cells > 20 and food >= 0.0


def test_the_committed_prints_are_the_prints_script():
    text = open(os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch", "prints.txt")).read()
    assert "## items inside a footprint, and out of reach" in text and "## food per new cell" in text
    assert "# fairness flags: --fair" in text and "reach-limited" in text
    assert text.count("\n  ") == 15 + 30


@pytest.fixture
def fair_check(monkeypatch):
    """RBT-128's ``fair.check(config) -> deviations`` arrives with #432's fixes; until then a stand-in that finds none,
    so the launcher's own checks are what these tests exercise.  With the real function on the tree, it is used."""
    from rabbitstew import fair as fair_mod

    if not hasattr(fair_mod, "check"):
        monkeypatch.setattr(fair_mod, "check", lambda config: [], raising=False)
    return fair_mod


EAT = "--eat=--eat-from root"


def test_the_fair_guard(tmp_path):
    """Launch adversary L1: only exactly --fair passes; the bypass, other flags, or none are refused."""
    stages.check_fair(["--fair"])
    for bad in (["--fair-v2"], [], ["--unfair-i-know"], ["--fair", "--unfair-i-know"], ["--motor-budget", "1.77"],
                ["--sweep-log"], ["fair"], ["--fair", "--seed", "7"]):
        with pytest.raises(SystemExit) as e:
            stages.check_fair(bad)
        assert e.value.code == 4, bad
    with pytest.raises(SystemExit) as e:
        stages.emit(["P"], 10, str(tmp_path), ["--fair-v2"], list(blocks.EAT_CANDIDATE))
    assert e.value.code == 4 and not (tmp_path / "lanes").exists()
    with pytest.raises(SystemExit) as e:
        stages.main(["prelaunch", "--fair=", EAT, "--root", str(tmp_path)])
    assert e.value.code == 4
    for eat in ([], ["--eat-from"], ["--eat-rule", "surface"]):  # S6: the eating rule is explicit
        with pytest.raises(SystemExit) as e:
            stages.check_eat(eat)
        assert e.value.code == 4


def test_every_block_must_be_the_ruled_set(tmp_path, monkeypatch):
    """L1 and coordinator 02:17 (3): a block is refused unless its config carries the marker, every preset value, and
    passes RBT-128's fair.check; without fair.check on the tree, every block is refused."""
    from rabbitstew import fair as fair_mod

    b = blocks.block("c1-p030-U-L", fair=["--fair"])
    if not hasattr(fair_mod, "check"):
        with pytest.raises(SystemExit) as e:
            stages.check_block(b)
        assert e.value.code == 4
        assert any("fair.check is not on this tree" in d for d in stages.fair_deviations(blocks.config_dict(b["argv"])))
    monkeypatch.setattr(fair_mod, "check", lambda config: [], raising=False)
    stages.check_block(b)
    monkeypatch.setattr(fair_mod, "check", lambda config: ["motor_budget differs"], raising=False)
    with pytest.raises(SystemExit):
        stages.check_block(b)
    monkeypatch.setattr(fair_mod, "check", lambda config: [], raising=False)
    for argv in (b["argv"][:-2] + ["--unfair-i-know", "--sweep-log"],  # the bypass: no marker, no preset
                 [x for x in b["argv"] if x != "--fair"] + ["--motor-budget", "1.77"]):  # one preset flag by hand
        dev = stages.fair_deviations(blocks.config_dict(argv))
        assert any("fairness" in d for d in dev), argv
        with pytest.raises(SystemExit):
            stages.check_block({**b, "argv": argv})


def test_a_fair_block_is_the_config_json_the_ecology_writes_key_for_key(tmp_path):
    """Coordinator 02:08: under --fair, a blocks.py block equals ecology's own config.json key for key, and carries
    "fairness": "fair" and the preset's expanded values."""
    from rabbitstew import fair as fair_mod

    for pid in ("c1-p030-PW-G", "c0-p030-U-L"):
        b = blocks.block(pid, fair=["--fair"])
        args = build_parser().parse_args(["ecology", *b["argv"], "--seed", "129001", "--seasons", "300"])
        evo, eco = ecology_configs(args)
        Ecology(evo, eco, out_dir=str(tmp_path / pid), log=None)  # writes config.json; runs no season
        written = blocks._flatten(json.loads((tmp_path / pid / "config.json").read_text()))
        assert b["block"] == {k: v for k, v in written.items() if k not in blocks.ARM_FIELDS}
        assert b["block"]["fairness"] == "fair" and b["fair_pending"] is False
        cfg = b["block"]
        assert cfg["sim.synthesis.mass_budget"] == 15.34 and cfg["sim.world.motor_budget"] == 1.77
        assert cfg["sim.world.ball_cone"] == cfg["sim.world.hinge_range"] == dict((d, v) for d, v, _ in fair_mod.PRESET)["ball_cone"]
        assert cfg["sim.settle_until_rest"] == 0.01 and cfg["sim.settle_max"] == 10.0
    assert "fairness" not in blocks.block("c1-p030-U-L")["block"]  # without --fair nothing is written
    # the PAYS harnesses read only the config's "sim" section (RBT-103's config(), #437's --config): every preset value
    # must live there, but for the Effector bias step, a mutation setting that a fixed host never uses
    for dest, value, flag in fair_mod.PRESET:
        keys = [k for k in b["block"] if k.split(".")[-1] == dest]
        assert keys and (keys[0].startswith("sim.") or dest == "effector_bias_sigma"), (flag, keys)


def test_the_cli_run_under_fair_writes_the_block(tmp_path, monkeypatch):
    """The subcommand itself (guard, expansion, then ecology_configs) writes what the block says; resume skips the
    guard.  A 1-season run of a tiny non-sweep world stands in: the block's own world is never run."""
    from rabbitstew.cli import main

    out = tmp_path / "run"
    argv = TINY + ["--fair", "--seed", "3", "--seasons", "1", "--out", str(out)]
    assert main(["ecology", *argv]) == 0
    args = build_parser().parse_args(["ecology", *argv])
    evo, eco = ecology_configs(args)
    from rabbitstew.ecology import _jsonable
    assert json.loads((out / "config.json").read_text()) == json.loads(json.dumps({**_jsonable(evo.to_dict()), "ecology": eco.to_dict()}))
    assert json.loads((out / "config.json").read_text())["fairness"] == "fair"
    with pytest.raises(SystemExit):  # neither --fair nor --unfair-i-know: refused
        main(["ecology", *TINY, "--seasons", "1", "--out", str(tmp_path / "bare")])
    assert main(["ecology", "--resume", "--seasons", "2", "--out", str(out)]) == 0  # resume never meets the guard


def test_the_steer_guard_refuses_until_the_pinned_files_exist(tmp_path, fair_check):
    """S5: probes and pays refuse unless steer.py (and section B's harness) exist at their ruled blob hashes, every
    template is given, and the fairness and eating flags are explicit."""
    steer, harness = tmp_path / "steer.py", tmp_path / "steps.py"
    common = ["--fair=--fair", EAT, "--root", str(tmp_path)]
    probes = ["probes", "--steer", str(steer), "--steer-cmd", "steer {run} {season} {rng} {out}", "--planted-cmd", "plant {point} {config} {out}"]
    with pytest.raises(SystemExit) as e:
        stages.main(probes + ["--steer-sha", "0" * 40] + common)
    assert e.value.code == 6
    steer.write_text("# stand-in\n")
    harness.write_text("# stand-in B\n")
    sha, hsha = stages.git_hash(str(steer)), stages.git_hash(str(harness))
    with pytest.raises(SystemExit) as e:  # present, but not the pinned version
        stages.main(probes + ["--steer-sha", "0" * 40] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # no planted-set template
        stages.main(probes[:-2] + ["--steer-sha", sha] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # the eating rule not given
        stages.main(probes + ["--steer-sha", sha, "--fair=--fair", "--root", str(tmp_path)])
    assert e.value.code == 4
    assert stages.main(probes + ["--steer-sha", sha] + common) == 0
    lines = (tmp_path / "lanes" / "probes.sh").read_text().splitlines()[2:]
    assert len(lines) == 4 * (4 * 2 + 1) and sum(x.startswith("plant ") for x in lines) == 4
    pays = ["pays", "--steer", str(steer), "--steer-sha", sha, "--pays-cmd", "steer {point} {world} {out}"]
    with pytest.raises(SystemExit) as e:  # no section-B harness
        stages.main(pays + ["--steps-cmd", "steps {point} {config} {out}"] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # the harness, not at its pinned hash
        stages.main(pays + ["--steps-harness", str(harness), "--steps-sha", sha, "--steps-cmd", "steps {point}"] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # the harness, but no command
        stages.main(pays + ["--steps-harness", str(harness), "--steps-sha", hsha] + common)
    assert e.value.code == 6
    assert stages.main(pays + ["--steps-harness", str(harness), "--steps-sha", hsha, "--steps-cmd", "steps {point} {config} {out}"] + common) == 0
    lines = (tmp_path / "lanes" / "pays.sh").read_text().splitlines()[2:]
    assert len(lines) == 36 and lines[0].startswith("steer c0-p030-U-L ") and lines[1].startswith("steps c0-p030-U-L ")
    # S11 (#441): steps.py --config takes a real config.json, which carries the marker and the whole "sim" section
    stages.main(pays + ["--steps-harness", str(harness), "--steps-sha", hsha, "--steps-cmd", "steps --config {config_json}"] + common)
    cj = (tmp_path / "lanes" / "pays.sh").read_text().splitlines()[3].split("--config ")[1]
    cfg = json.loads(open(cj).read())
    assert cfg["fairness"] == "fair" and cfg["sim"]["food"]["eat_from"] == "root"


def test_the_designed_prize_leg_launches_without_steer_or_section_b(tmp_path, fair_check):
    """Stage 0's split: the designed prize at a = 6 needs only --fair, the eating rule and RBT-125's ten hosts."""
    bodies = tmp_path / "bodies"
    assert stages.main(["pays-prize", "--fair=--fair", EAT, "--bodies", str(bodies), "--root", str(tmp_path)]) == 7
    for s in stages.PRIZE_HOSTS:
        (bodies / f"forage-{s}").mkdir(parents=True)
        (bodies / f"forage-{s}" / "state.json").write_text("{}")
    with pytest.raises(SystemExit):
        stages.main(["pays-prize", "--fair=--unfair-i-know", EAT, "--bodies", str(bodies), "--root", str(tmp_path)])
    with pytest.raises(SystemExit):
        stages.main(["pays-prize", "--fair=--fair", "--bodies", str(bodies), "--root", str(tmp_path)])  # no eating rule
    assert stages.main(["pays-prize", "--fair=--fair", EAT, "--bodies", str(bodies), "--root", str(tmp_path)]) == 0
    lines = (tmp_path / "lanes" / "pays-prize.sh").read_text().splitlines()[2:]
    assert len(lines) == 18 * 10 and all(" --w 3 " in x and "prize_gate.py" in x for x in lines)
    cfg = json.loads((tmp_path / "worlds" / "config" / "c1-p030-PW-G" / "config.json").read_text())
    assert cfg["fairness"] == "fair" and cfg["sim"]["food"]["smell_contrast"] == 2.5


def test_the_plan_is_the_design_and_within_budget(tmp_path):
    p = stages.plan(["P", "0"], 10, str(tmp_path))
    assert p["arm_seasons"]["P"] == 16 * (60 + 240 * 3) + 4 * (65 + 5)
    assert p["arm_seasons"]["0"] == 150 * 3 * 60
    (p20, p25), (c20, c25) = p["core_h"]["P"]["total"], p["core_h"]["0"]["total"]
    assert c20 == (195.0, 195.0) and c25[1] <= 232.5
    extras = 4 * stages.PLANTED_POINT + stages.core_h(4 * 70)[1]  # the planted set and K1, beyond the r4 line
    # the r4 table rounds its per-seed arm costs (1.67 + 1.33 + 1.33 core-h); 1 core-h covers that rounding
    assert p25[1] <= stages.BUDGET["P"][1][1] + extras + 1.0 and p20[1] <= stages.BUDGET["P"][0][1] + extras + 1.0
    total = stages.BUDGET["total"][1][1] + stages.BUDGET["anchor fallback"][1][1] + (p25[1] - stages.BUDGET["P"][1][1])
    assert total <= stages.BRIEF_ENVELOPE[1]


@pytest.mark.parametrize("which", [["P"], ["0"], ["P", "0"]])
def test_the_host_layout_places_every_unit_once_and_splits_seeds(tmp_path, which):
    units = stages.units_for(which, str(tmp_path))
    lanes = stages.layout(units, 10)
    names = [j["name"] for lane in lanes for u in lane for j in u["jobs"]]
    assert sorted(names) == sorted(j["name"] for u in units for j in u["jobs"])
    for h in range(10):
        a, b = lanes[2 * h], lanes[2 * h + 1]
        common = {u["seed"] for u in a} & {u["seed"] for u in b}
        # a seed on both lanes of a session is the split census seed: lane 1 holds only its census jobs, and runs them last
        assert all(u.get("shared") for u in b if u["seed"] in common)
        assert all(u.get("shared") or u["stage"] == "P" for u in a if u["seed"] in common)
        if any(u.get("shared") for u in a):
            k = max(i for i, u in enumerate(a) if u.get("shared"))
            assert all(u.get("shared") for u in a[:k + 1])  # lane 0 runs the shared seed first
        if any(u.get("shared") for u in b):
            k = min(i for i, u in enumerate(b) if u.get("shared"))
            assert all(u.get("shared") for u in b[k:])  # lane 1 runs it last
    loads = [sum(j["cost"] for u in lane for j in u["jobs"]) for lane in lanes]
    if "0" in which:
        assert max(loads) <= 1.05 * np.mean(loads)
    else:  # 16 pilot chains on 20 lanes: one chain a lane
        assert sorted(len(lane) for lane in lanes) == [0] * 4 + [1] * 16
    for u in units:
        if u["stage"] == "P":
            chain = [j["name"].split("/")[-1] for j in u["jobs"]]
            assert chain[:5] == ["S60", "ckpt60", "S", "M", "N"]
            n = next(j for j in u["jobs"] if j["name"].endswith("/N"))
            assert n["set"]["merge_null"] == ("holistic" if u["seed"] % 2 else "conventional")


TINY = ["--capacity", "4", "--challenge", "foraging", "--group-size", "2", "--brain-model", "foraging", "--food-items", "4",
        "--duration", "0.4", "--terrain", "flat", "--conventional-topology", "--score", "food", "--living-cost", "0.05",
        "--initial-energy", "2", "--birth-threshold", "0.5", "--birth-cost", "0.2", "--max-age", "6"]


def test_the_runner_forks_and_checks_k1_on_a_tiny_world(tmp_path, monkeypatch):
    """The lane runner's job kinds on a tiny non-sweep world: fresh to the checkpoint, snapshot, resume, the M and N
    forks, and K1 (a straight run against the fork with the merge unset)."""
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    d = tmp_path / "pt" / "7"
    base = {"worlds": str(worlds), "seed": 7}
    jobs = [
        {"job": "fresh", "name": "x/S60", "point": "tiny", "dir": f"{d}/S", "seasons": 3},
        {"job": "snapshot", "name": "x/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "season": 3},
        {"job": "resume", "name": "x/S", "dir": f"{d}/S", "seasons": 5},
        {"job": "fork", "name": "x/M", "src": f"{d}/ckpt60", "dir": f"{d}/M", "seasons": 5, "set": {"merge_after": 3, "pooled_capacity": 8}},
        {"job": "fork", "name": "x/N", "src": f"{d}/ckpt60", "dir": f"{d}/N", "seasons": 5,
         "set": {"merge_after": 3, "pooled_capacity": 8, "merge_null": "holistic"}},
        {"job": "fresh", "name": "x/K1ref", "point": "tiny", "dir": f"{d}/K1ref", "seasons": 5},
        {"job": "fork", "name": "x/K1fork", "src": f"{d}/ckpt60", "dir": f"{d}/K1fork", "seasons": 5, "set": {}},
        {"job": "k1", "name": "x/K1", "ref": f"{d}/K1ref", "dir": f"{d}/K1fork"},
    ]
    for j in jobs:
        stages.run_job({**base, **j})
    assert (d / "K1.txt").read_text().startswith("K1 PASS")
    assert any("genomes" in n for n in stages.output_files(str(d / "K1ref")))  # S3: genomes and state.json compared too
    assert "state.json" in stages.output_files(str(d / "K1ref"))
    # S7's equivalence: a run checkpointed at the census's season and resumed (S) is the straight run, file for file,
    # so Stage 1 may resume from the census's S 0-59 states
    assert stages.k1_compare(str(d / "K1ref"), str(d / "S"))[0] == "PASS"
    g = sorted(p for p in stages.output_files(str(d / "K1fork")) if "genomes" in p)[0]
    with open(d / "K1fork" / g, "a") as f:
        f.write(" ")
    verdict, lines = stages.k1_compare(str(d / "K1ref"), str(d / "K1fork"))
    assert verdict == "FAIL" and lines[-1] == f"DIFFERS: {g}"
    m = json.loads((d / "M" / "config.json").read_text())["ecology"]
    n = json.loads((d / "N" / "config.json").read_text())["ecology"]
    assert m["merge_after"] == 3 and "merge_null" not in m and n["merge_null"] == "holistic"
    assert json.loads((d / "ckpt60" / "config.json").read_text())["ecology"].get("merge_after") is None
    assert any(e.get("merged") for e in json.loads((d / "M" / "history.json").read_text())["history"])
    stages.run_job({**base, **jobs[2]})  # a finished job is skipped, not re-run
    assert (d / "S" / "command.txt").read_text().count("\n") == 2
    import shutil
    shutil.rmtree(d / "ckpt60")
    with pytest.raises(SystemExit, match="not the fork's 3"):  # S has moved on: the lost checkpoint is not faked
        stages.run_job({**base, **jobs[1]})


def test_a_job_never_waits_on_durable_sh(tmp_path, monkeypatch):
    """L4: a long job's durable loop is killed when the run exits; the job returns at once, not after the loop's sleep."""
    import time
    fake = tmp_path / "repo"
    (fake / "scripts").mkdir(parents=True)
    (fake / "scripts" / "durable.sh").write_text("#!/bin/bash\nsleep 120\n")
    (fake / "scripts" / "durable.sh").chmod(0o755)
    monkeypatch.setattr(stages, "ROOT", str(fake))
    monkeypatch.delenv("NO_DURABLE", raising=False)
    run = tmp_path / "run"
    run.mkdir()
    t0 = time.time()
    with pytest.raises(SystemExit):  # an ecology resume of an empty directory fails at once
        stages._ecology(["--resume", "--seasons", "2"], str(run), "rbt-129-test", long=True)
    assert time.time() - t0 < 30


def _launch_dir(tmp_path, fair="--fair", eat="--eat-from root", trees=None):
    lanes = tmp_path / "lanes"
    lanes.mkdir(exist_ok=True)
    trees = trees or {t: stages._git("rev-parse", f"HEAD:{t}") for t in stages.PINNED_TREES}
    (lanes / "launch.txt").write_text("# test\n" + "".join(f"tree:{t} {v}\n" for t, v in trees.items()) + f"fair {fair}\neat {eat}\n")
    return lanes


def test_run_lane_refuses_another_tree(tmp_path):
    """L2: a session whose pinned trees differ from launch.txt's is refused before any job."""
    trees = {t: stages._git("rev-parse", f"HEAD:{t}") for t in stages.PINNED_TREES}
    trees["runs/RBT-129/launch"] = "0" * 40
    lanes = _launch_dir(tmp_path, trees=trees)
    (lanes / "host0-lane0.jsonl").write_text("")
    with pytest.raises(SystemExit) as e:
        stages.run_lane(str(lanes / "host0-lane0.jsonl"))
    assert e.value.code == 5
    launch = stages.read_launch(str(lanes / "launch.txt"))
    assert launch["fair"] == "--fair" and launch["tree:scripts"] == stages._git("rev-parse", "HEAD:scripts")


def test_run_lane_refuses_an_edited_block(tmp_path, fair_check):
    """L1: every fresh job's world file is rebuilt from launch.txt's flags; an edited one is refused."""
    worlds = tmp_path / "worlds"
    blocks.export(str(worlds), ["c1-p030-U-L"], fair=["--fair"], eat=list(blocks.EAT_CANDIDATE))
    launch = stages.read_launch(str(_launch_dir(tmp_path) / "launch.txt"))
    job = {"job": "fresh", "name": "0/c1-p030-U-L/129001/S", "point": "c1-p030-U-L", "seed": 129001, "worlds": str(worlds)}
    stages.check_lane_blocks([job], launch)
    path = worlds / "c1-p030-U-L.json"
    b = json.loads(path.read_text())
    b["argv"] = [x if x != "14" else "13" for x in b["argv"]]  # a hand edit of N
    path.write_text(json.dumps(b))
    with pytest.raises(SystemExit) as e:
        stages.check_lane_blocks([job], launch)
    assert e.value.code == 4
    with pytest.raises(SystemExit):  # launch.txt with the bypass
        stages.check_lane_blocks([job], {**launch, "fair": "--unfair-i-know"})


def test_lane_files_hold_repository_relative_paths(tmp_path, fair_check):
    """S9: emit writes paths relative to the repository root; the runner refuses absolute or escaping ones."""
    root = os.path.join(stages.ROOT, "runs", "RBT-129", "_test_emit")
    try:
        paths = stages.emit(["P"], 10, root, ["--fair"], list(blocks.EAT_CANDIDATE))
        jobs = [json.loads(x) for p in paths for x in open(p) if x.strip()]
        assert jobs and all(not os.path.isabs(j[k]) and not j[k].startswith("..") for j in jobs for k in stages.PATH_KEYS if k in j)
        launch = stages.read_launch(os.path.join(root, "lanes", "P", "launch.txt"))
        assert set(launch) >= {"commit", "fair", "eat", *(f"tree:{t}" for t in stages.PINNED_TREES)}
    finally:
        import shutil
        shutil.rmtree(root, ignore_errors=True)
    for bad in ("/etc/x", "../x"):
        with pytest.raises(SystemExit):
            stages.absolute(bad)
