"""RBT-129 launch readiness (runs/RBT-129/launch/): the world blocks, the pre-launch prints and the Stage P / Stage 0
launchers.  Nothing here runs a sweep arm: the runner is exercised on a tiny non-sweep world only."""
import json
import os
import platform
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


@pytest.fixture(autouse=True)
def _receipts_in_tmp(tmp_path, monkeypatch):
    """No test writes this machine's durable receipts (#510 adversary S-2)."""
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "durable-done"))


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
    assert b["sim.food.eat_from"] == "root" and b["sim.food.eat_rule"] == "surface" and b["ecology.sweep_log"] is True
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
    share, tall, deep, total, fallbacks = prints.unreachable("c2-p030-U-L", 10)
    assert total == 120 and 0.0 <= deep <= tall <= share < 1.0 and share > 0


def test_food_per_new_cell_covers_ground():
    key, food, cells, fallbacks = prints.cell_season(("k", "c0-p030-U-L", "pioneer-drive", 1000, [], list(blocks.EAT_RULED)))
    assert key == "k" and cells > 20 and food >= 0.0


def test_the_committed_prints_are_the_prints_script():
    text = open(os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch", "prints.txt")).read()
    assert "## items inside a footprint, and out of reach" in text and "## food per new cell" in text
    assert "# fairness flags: --fair" in text and "reach-limited" in text
    assert text.count("\n  ") == 15 + 30


REAL_SURFACE_PROBE = stages.surface_clearance_ok


def _mujoco_is(monkeypatch, v):
    """Make ``importlib.metadata.version("mujoco")`` and the imported module's ``__version__`` report ``v`` (None: not
    installed); other packages unchanged."""
    import importlib.metadata
    import mujoco
    real = importlib.metadata.version

    def version(name):
        if name != "mujoco":
            return real(name)
        if v is None:
            raise importlib.metadata.PackageNotFoundError(name)
        return v
    monkeypatch.setattr(importlib.metadata, "version", version)
    monkeypatch.setattr(mujoco, "__version__", v)


@pytest.fixture(autouse=True)
def surface_clearance(monkeypatch):
    """The launchers refuse a surface-eating launch unless this tree clears food by surface distance (RBT-125 #446;
    R1), and on any MuJoCo but the ruled one (exit 9).  The tests of the rest of the launcher run as on a tree that has
    the clearance, on the pinned MuJoCo whatever is installed (#511 adversary M1); the probe and the pin are tested
    below (``REAL_SURFACE_PROBE``, ``_mujoco_is``)."""
    monkeypatch.setattr(stages, "surface_clearance_ok", lambda *a, **k: True)
    _mujoco_is(monkeypatch, stages.MUJOCO_PINNED)


@pytest.fixture
def fair_check(monkeypatch):
    """RBT-128's ``fair.check(config) -> deviations`` arrives with #432's fixes; until then a stand-in that finds none,
    so the launcher's own checks are what these tests exercise.  With the real function on the tree, it is used."""
    from rabbitstew import fair as fair_mod

    if not hasattr(fair_mod, "check"):
        monkeypatch.setattr(fair_mod, "check", lambda config: [], raising=False)
    return fair_mod


EAT = "--eat=" + " ".join(blocks.EAT_RULED)


@pytest.fixture
def repo_tmp():
    """A scratch root inside the repository (the leg scripts hold repository-relative paths, S9), removed after."""
    import pathlib
    import shutil
    import uuid
    root = pathlib.Path(stages.ROOT, "runs", "RBT-129", f"_test_{uuid.uuid4().hex[:8]}")
    root.mkdir(parents=True)
    yield root
    shutil.rmtree(root, ignore_errors=True)


def test_the_fair_guard(tmp_path):
    """Launch adversary L1: only exactly --fair passes; the bypass, other flags, or none are refused."""
    stages.check_fair(["--fair"])
    for bad in (["--fair-v2"], [], ["--unfair-i-know"], ["--fair", "--unfair-i-know"], ["--motor-budget", "1.77"],
                ["--sweep-log"], ["fair"], ["--fair", "--seed", "7"]):
        with pytest.raises(SystemExit) as e:
            stages.check_fair(bad)
        assert e.value.code == 4, bad
    with pytest.raises(SystemExit) as e:
        stages.emit(["P"], 10, str(tmp_path), ["--fair-v2"], list(blocks.EAT_RULED))
    assert e.value.code == 4 and not (tmp_path / "lanes").exists()
    with pytest.raises(SystemExit) as e:
        stages.main(["prelaunch", "--fair=", EAT, "--root", str(tmp_path)])
    assert e.value.code == 4
    for eat in ([], ["--eat-from"], ["--eat-rule", "surface"], ["--eat-from", "root", "--clear-from", "geoms"],
                ["--eat-from", "mouth"], ["--eat-from", "root"], ["--eat-from", "any", "--eat-rule", "surface"],
                ["--eat-rule", "surface", "--eat-from", "root"]):  # R1: exactly the ruled rule, nothing else
        with pytest.raises(SystemExit) as e:
            stages.check_eat(eat)
        assert e.value.code == 4
    stages.check_eat(list(blocks.EAT_RULED))
    assert blocks.EAT_RULED == ("--eat-from", "root", "--eat-rule", "surface")  # coordinator 03:10


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


@pytest.fixture
def rbt132_tools(repo_tmp, monkeypatch):
    """RBT-132's planters.py, probe_members.py and probe_power.py arrive with #459; until then, stand-ins inside the
    repository take their place in the tool lists (the tools that are on the tree stay themselves)."""
    stand = {}
    for t in stages.PROBE_TOOLS:
        if not os.path.isfile(os.path.join(stages.ROOT, t)):
            path = repo_tmp / "tools" / os.path.basename(t)
            path.parent.mkdir(exist_ok=True)
            path.write_text(f"# stand-in for {t}\n")
            stand[t] = stages.rel(str(path))
    sub = lambda tools: tuple(stand.get(t, t) for t in tools)
    monkeypatch.setattr(stages, "STEER_TOOLS", sub(stages.STEER_TOOLS))
    monkeypatch.setattr(stages, "PROBE_TOOLS", sub(stages.PROBE_TOOLS))
    monkeypatch.setattr(stages, "PLANTERS", stand.get(stages.PLANTERS, stages.PLANTERS))
    return stand


def _units(root, extinct=(), unknown=()):
    """Pilot units as Stage P leaves them: each with its record's UNIT.txt, and EXTINCT.txt where extinct."""
    for pid in blocks.PILOT:
        for j in stages.PILOT_SEEDS:
            u = root / "stageP" / pid / str(stages.seed(j))
            if (pid, j) in unknown:
                continue
            (u / "record").mkdir(parents=True, exist_ok=True)
            names = [stages.UNIT] + ([stages.EXTINCT] if (pid, j) in extinct else [])
            for n in names:
                (u / n).write_text("EXTINCT pre-merge at season 12: test\n" if n == stages.EXTINCT else "unit\n")
                (u / "record" / n).write_text((u / n).read_text())


def test_the_steer_guard_refuses_until_the_pinned_files_exist(repo_tmp, fair_check, monkeypatch):
    """S5: probes and pays refuse unless steer.py exists at its ruled blob hash, every template is given, and the
    fairness and eating flags are explicit; and (09:44) while RBT-132's planters.py and probe tools are not on the tree."""
    monkeypatch.setenv("NO_DURABLE", "1")
    tmp_path = repo_tmp
    steer = tmp_path / "steer.py"
    common = ["--fair=--fair", EAT, "--root", str(tmp_path)]
    probes = ["probes", "--steer", str(steer), "--steer-cmd", "steer {run} {season} {rng} {out}", "--planted-cmd", "plant {point} {config} {out}"]
    with pytest.raises(SystemExit) as e:
        stages.main(probes + ["--steer-sha", "0" * 40] + common)
    assert e.value.code == 6
    steer.write_text("# stand-in\n")
    sha = stages.git_hash(str(steer))
    with pytest.raises(SystemExit) as e:  # present, but not the pinned version
        stages.main(probes + ["--steer-sha", "0" * 40] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # no planted-set template
        stages.main(probes[:-2] + ["--steer-sha", sha] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # a malformed eating rule
        stages.main(probes + ["--steer-sha", sha, "--fair=--fair", "--eat=--eat-rule surface", "--root", str(tmp_path)])
    assert e.value.code == 4
    if not os.path.isfile(os.path.join(stages.ROOT, stages.PLANTERS)):
        with pytest.raises(SystemExit) as e:  # RBT-132's tools not on this tree
            stages.main(probes + ["--steer-sha", sha] + common)
        assert e.value.code == 6


def test_the_probes_run_the_planted_set_first_and_skip_extinct_units(repo_tmp, fair_check, rbt132_tools, monkeypatch):
    """RBT132.md (i) and (iv), the 09:44 brief: per point the planted line comes first (the probes read the battery it
    writes); a unit extinct pre-merge is skipped at both seasons and listed in lanes/probes/extinct.txt; a unit whose
    status is not known is refused (exit 7); HOSTS_ROOT is the leg's restored O1 root; every tool is pinned."""
    monkeypatch.setenv("NO_DURABLE", "1")
    tmp_path = repo_tmp
    steer = tmp_path / "steer.py"
    steer.write_text("# stand-in\n")
    sha = stages.git_hash(str(steer))
    args = ["probes", "--steer", str(steer), "--steer-sha", sha, "--steer-cmd", "steer {run} {season} {rng} {out}",
            "--planted-cmd", "plant {point} {config_json} {out} --hosts HOSTS_ROOT", "--fair=--fair", EAT, "--root", str(tmp_path)]
    gone = (blocks.PILOT[1], 3)
    _units(tmp_path, unknown={gone})
    with pytest.raises(SystemExit) as e:
        stages.main(args)
    assert e.value.code == 7
    _units(tmp_path, extinct={gone})
    assert stages.main(args) == 0
    lines = [x for x in _jobs(tmp_path / "lanes" / "probes.sh") if x.startswith("mkdir -p ")]
    cmds = [x.split("rc=0; ")[1].split(" > ")[0] for x in lines]
    assert len(cmds) == 4 + (16 - 1) * 2 and sum(c.startswith("plant ") for c in cmds) == 4
    per_point = {pid: [c for c in cmds if f"/stageP/{pid}/" in c] for pid in blocks.PILOT}
    for pid, cs in per_point.items():
        assert cs[0].startswith(f"plant {pid} ") and all(c.startswith("steer ") for c in cs[1:]), pid
    u = stages.rel(str(tmp_path / "stageP" / gone[0] / str(stages.seed(gone[1]))))
    assert not any(f"{u}/" in c for c in cmds)
    assert (tmp_path / "lanes" / "probes" / "extinct.txt").read_text().splitlines()[1:] == [u]
    assert all(" --hosts runs/RBT-129/hosts113" in c for c in cmds if c.startswith("plant "))
    text = (tmp_path / "lanes" / "probes.sh").read_text()
    assert "rbt-113-O1" in text and "stages.py verify " in text and f"durable.sh restore {u}/S " not in text
    assert "stages.py save " in text and "FAILED: " in text  # every output saved; failures print the dir and exit only
    launch = stages.read_launch(str(tmp_path / "lanes" / "probes" / "launch.txt"))
    tools = {k[5:] for k in launch if k.startswith("tool:")}
    assert tools == {stages.rel(str(steer))} | set(stages.PROBE_TOOLS) - {"runs/RBT-116/steer.py"}
    assert {"runs/RBT-97/mechanism.py", "runs/RBT-97/resign_rbt67.py"} <= tools


def test_holistic_pays_is_one_planters_line_per_cell(repo_tmp, fair_check, rbt132_tools, monkeypatch):
    """RBT132.md (v): one --pays-cmd line per PAYS cell, out = stage0/pays/<cell> (planters writes holistic/ in it); the
    holistic nose step is optional until its harness exists, and pinned when given."""
    monkeypatch.setenv("NO_DURABLE", "1")
    tmp_path = repo_tmp
    steer, harness = tmp_path / "steer.py", tmp_path / "hsteps.py"
    steer.write_text("# stand-in\n")
    harness.write_text("# stand-in holistic steps\n")
    sha, hsha = stages.git_hash(str(steer)), stages.git_hash(str(harness))
    common = ["--fair=--fair", EAT, "--root", str(tmp_path)]
    pays = ["pays", "--steer", str(steer), "--steer-sha", sha,
            "--pays-cmd", "python runs/RBT-116/planters.py pays {point} {config_json} {out} --hosts HOSTS_ROOT --workers 4"]
    assert stages.main(pays + common) == 0
    cmds = [x.split("rc=0; ")[1].split(" > ")[0] for x in _jobs(tmp_path / "lanes" / "pays.sh") if x.startswith("mkdir -p ")]
    assert len(cmds) == 18 and all(" --hosts runs/RBT-129/hosts113 " in c for c in cmds)
    for pid, c in zip(blocks.PAYS_CELLS, cmds):
        assert c.split()[3:6] == [pid, stages.rel(stages.config_json_path(str(tmp_path), pid)), stages.rel(str(tmp_path / "stage0" / "pays" / pid))]
    cfg = json.loads(open(os.path.join(stages.ROOT, cmds[0].split()[4])).read())
    assert cfg["fairness"] == "fair" and cfg["sim"]["food"]["eat_from"] == "root"  # S11: a real config.json
    text = (tmp_path / "lanes" / "pays.sh").read_text()
    assert f"{stages.rel(str(tmp_path / 'stage0' / 'pays' / 'c0-p030-U-L'))}/holistic/.rbt129-done-job" in text
    launch = stages.read_launch(str(tmp_path / "lanes" / "pays" / "launch.txt"))
    assert {k[5:] for k in launch if k.startswith("tool:")} == {stages.rel(str(steer))} | set(stages.STEER_TOOLS) - {"runs/RBT-116/steer.py"}
    with pytest.raises(SystemExit) as e:  # the harness, not at its pinned hash
        stages.main(pays + ["--steps-harness", str(harness), "--steps-sha", sha, "--steps-cmd", "hsteps {point}"] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # the harness, but no command
        stages.main(pays + ["--steps-harness", str(harness), "--steps-sha", hsha] + common)
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:  # a command, but no harness to pin
        stages.main(pays + ["--steps-cmd", "hsteps {point}"] + common)
    assert e.value.code == 6
    assert stages.main(pays + ["--steps-harness", str(harness), "--steps-sha", hsha, "--steps-cmd", "hsteps {point} {out}"] + common) == 0
    cmds = [x.split("rc=0; ")[1].split(" > ")[0] for x in _jobs(tmp_path / "lanes" / "pays.sh") if x.startswith("mkdir -p ")]
    assert len(cmds) == 36 and cmds[1].startswith("hsteps c0-p030-U-L ")
    assert f"git hash-object {stages.rel(str(harness))}" in (tmp_path / "lanes" / "pays.sh").read_text()


def test_the_designed_prize_leg_launches_without_steer_or_section_b(repo_tmp, fair_check):
    """Stage 0's split: the designed prize at a = 6 needs only --fair, the eating rule and RBT-125's ten hosts, which each
    runner restores from ckpt/rbt-90-SEED where missing.  The leg carries its own launch record and host guards."""
    tmp_path = repo_tmp
    with pytest.raises(SystemExit):
        stages.main(["pays-prize", "--fair=--unfair-i-know", EAT, "--root", str(tmp_path)])
    with pytest.raises(SystemExit):
        stages.main(["pays-prize", "--fair=--fair", "--eat=--eat-from", "--root", str(tmp_path)])  # malformed
    assert stages.main(["pays-prize", "--fair=--fair", EAT, "--root", str(tmp_path), "--runners", "3"]) == 0
    leg = tmp_path / "lanes" / "pays-prize"
    scripts = sorted(leg.glob("runner*.sh"))
    assert [p.name for p in scripts] == ["runner0.sh", "runner1.sh", "runner2.sh"]
    jobs = [x for p in scripts for x in _jobs(p) if "prize_gate.py" in x]
    assert len(jobs) == 18 * 10 and len(set(jobs)) == 180 and all(" --w 3 " in x for x in jobs)
    assert all(not x.split("--run ")[1].startswith("/") for x in jobs)  # repository-relative (S9)
    text = scripts[0].read_text()
    assert "stages.py verify " in text and "rbt-90-801" in text and "exit 7" in text  # guards and host restore
    assert "run_in_background" in text and "never nohup" in text and "pkill" in text  # S-4
    launch = stages.read_launch(str(leg / "launch.txt"))
    assert launch["fair"] == "--fair" and launch["eat"] == " ".join(blocks.EAT_RULED)
    assert launch["cells"].split() == list(blocks.PAYS_CELLS) and launch["tree:rabbitstew"] == stages._git("rev-parse", "HEAD:rabbitstew")
    # S-1: exactly the tools the leg runs, import chain included; not steer.py
    assert {k[5:] for k in launch if k.startswith("tool:")} == set(stages.PRIZE_TOOLS)
    assert launch["tool:runs/RBT-97/routed_p801.py"] == stages.git_hash(os.path.join(stages.ROOT, "runs/RBT-97/routed_p801.py"))
    # L-2: --decoy 3 exactly at the six PW cells, as RBT-125's registered run_gate.sh has it
    decoy = {x.split("--label ")[1].split()[0].split("-", 1)[1] for x in jobs if "--decoy 3" in x}
    assert decoy == {p for p in blocks.PAYS_CELLS if "-PW-" in p} and len(decoy) == 6
    assert sum("--decoy" in x for x in jobs) == 60
    # S-3: every promoted job snapshots its cell's output dir, and each cell belongs to one runner only
    assert all("scripts/durable.sh save runs/RBT-129/" in x for x in jobs)
    cells = [{x.split("--label ")[1].split()[0].split("-", 1)[1] for x in _jobs(p) if "prize_gate.py" in x} for p in scripts]
    assert sum(len(c) for c in cells) == 18 and not (cells[0] & cells[1]) and not (cells[1] & cells[2])
    assert "scripts/durable.sh restore runs/RBT-129/" in text and "stage0/pays/" in text
    cfg = json.loads((tmp_path / "worlds" / "config" / "c1-p030-PW-G" / "config.json").read_text())
    assert cfg["fairness"] == "fair" and cfg["sim"]["food"]["smell_contrast"] == 2.5


def test_verify_refuses_an_edited_cell_config(repo_tmp, fair_check, monkeypatch):
    """The leg's guard where it runs: an edited config.json (exit 4) or a changed tool (exit 6) is refused; the host and
    tree checks (exit 3, 5) are check_host's, tested with run-lane."""
    tmp_path = repo_tmp
    stages.main(["pays-prize", "--fair=--fair", EAT, "--root", str(tmp_path)])
    launch = str(tmp_path / "lanes" / "pays-prize" / "launch.txt")
    monkeypatch.setattr(stages, "check_host", lambda launch: None)  # this checkout is mid-edit; exit 5 is tested elsewhere
    stages.verify_leg(launch, str(tmp_path))
    p = tmp_path / "worlds" / "config" / "c1-p030-PW-G" / "config.json"
    cfg = json.loads(p.read_text())
    cfg["sim"]["food"]["smell_tau"] = 1.0
    p.write_text(json.dumps(cfg))
    with pytest.raises(SystemExit) as e:
        stages.verify_leg(launch, str(tmp_path))
    assert e.value.code == 4
    stages.main(["pays-prize", "--fair=--fair", EAT, "--root", str(tmp_path)])
    stages.verify_leg(launch, str(tmp_path))
    # #465 adversary S-4: the copy the RBT132.md templates and calibrate read, worlds/<id>.config.json, is verified too
    q = tmp_path / "worlds" / "c1-p030-PW-G.config.json"
    for edit in (("food", "smell_tau", 1.0), ("world", "motor_budget", 3.0)):
        keep = q.read_text()
        cfg = json.loads(keep)
        cfg["sim"][edit[0]][edit[1]] = edit[2]
        q.write_text(json.dumps(cfg))
        with pytest.raises(SystemExit) as e:
            stages.verify_leg(launch, str(tmp_path))
        assert e.value.code == 4, edit
        q.write_text(keep)
    q.unlink()
    with pytest.raises(SystemExit) as e:
        stages.verify_leg(launch, str(tmp_path))
    assert e.value.code == 4
    stages.main(["pays-prize", "--fair=--fair", EAT, "--root", str(tmp_path)])
    rec = open(launch).read().replace("tool:runs/RBT-97/routed_p801.py ", "tool:runs/RBT-97/routed_p801.py 0000")
    open(launch, "w").write(rec)
    with pytest.raises(SystemExit) as e:
        stages.verify_leg(launch, str(tmp_path))
    assert e.value.code == 6


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


def _jobs(path):
    """An emitted script's job lines (its header re-verifies the tools' hashes, R1 (4))."""
    return [x for x in open(path).read().splitlines() if not x.startswith(("#", "set -e", "[ ", "cd ", "python runs/RBT-129/launch/stages.py verify"))]


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


def _launch_dir(tmp_path, fair="--fair", eat=" ".join(blocks.EAT_RULED), trees=None):
    lanes = tmp_path / "lanes"
    lanes.mkdir(exist_ok=True)
    trees = trees or {t: stages._git("rev-parse", f"HEAD:{t}") for t in stages.PINNED_TREES}
    (lanes / "launch.txt").write_text("# test\n" + "".join(f"tree:{t} {v}\n" for t, v in trees.items()) + f"fair {fair}\neat {eat}\n")
    return lanes


def test_run_lane_refuses_another_tree(tmp_path, monkeypatch):
    """L2: a session whose pinned trees differ from launch.txt's is refused before any job."""
    _mujoco_is(monkeypatch, stages.MUJOCO_PINNED)  # #511 adversary M1: exit 5 on any installed MuJoCo
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
    blocks.export(str(worlds), ["c1-p030-U-L"], fair=["--fair"], eat=list(blocks.EAT_RULED))
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
        paths = stages.emit(["P"], 10, root, ["--fair"], list(blocks.EAT_RULED))
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


def test_s11_the_pays_config_json_is_what_steps_py_reads(tmp_path, capsys, fair_check):
    """S11 (#441; coordinator 02:33): emit writes a real worlds/<id>.config.json per PAYS cell, and RBT-125 section B's
    harness (steps.py --config, #437) parses it: the fairness marker passes its S12 refusal, and the world it prints
    is the block's food, root + surface eating included.  The pool is faked (no physics), as in test_rbt125_harness."""
    from test_rbt125_harness import _pioneer, _run, _steps

    import pathlib
    import shutil
    root = os.path.join(stages.ROOT, "runs", "RBT-129", "_test_s11")  # emit writes repository-relative lane paths (S9)
    try:
        stages.emit(["0"], 10, root, ["--fair"], list(blocks.EAT_RULED))
        names = sorted(p.name for p in pathlib.Path(root, "worlds").glob("*.config.json"))
        cj = str(tmp_path / "c1-p030-PW-G.config.json")
        shutil.copy(stages.config_json_path(root, "c1-p030-PW-G"), cj)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    assert names == sorted(f"{p}.config.json" for p in blocks.PAYS_CELLS)
    cfg = json.loads(open(cj).read())
    assert cfg == blocks.config_dict(blocks.world_argv("c1-p030-PW-G", fair=["--fair"], eat=list(blocks.EAT_RULED)))
    hosts = tmp_path / "hosts.txt"
    hosts.write_text(_pioneer(str(tmp_path / "h0.json")) + "\n")
    out = _run(_steps(), [str(tmp_path), "c1-p030-PW-G", "--config", cj, "--hosts-file", str(hosts), "--seeds", "2"], capsys)
    assert "# fairness: 'fair'" in out and f"world from {cj}" in out
    food = json.loads(out.split("cell c1-p030-PW-G: ")[1].splitlines()[0])
    assert food == cfg["sim"]["food"] and food["eat_rule"] == "surface" and food["smell_contrast"] == 2.5


def test_r1_the_surface_probe_refuses_a_tree_that_clears_from_the_root_centre(monkeypatch):
    """R1 (2): with the clearance measured from the root's centre only (the tree before RBT-125 #446), items land within
    reach of the root's surface: the probe reads False and every surface launch is refused."""
    from rabbitstew import simulation

    monkeypatch.setattr(simulation.Simulation, "_clearance_points", lambda self: self._robot_positions())
    assert REAL_SURFACE_PROBE() is False
    monkeypatch.setattr(stages, "surface_clearance_ok", REAL_SURFACE_PROBE)
    with pytest.raises(SystemExit) as e:
        stages.check_surface_clearance(list(blocks.EAT_RULED))
    assert e.value.code == 4


def test_r1_the_surface_probe_passes_a_tree_that_clears_by_surface(monkeypatch):
    """R1 (2): with clearance by surface distance, the probe reads True.  On a tree with #446 that is the tree itself;
    on one without it, the older all-geoms surface clearance (clear_from = geoms) stands in."""
    from rabbitstew import simulation

    if not REAL_SURFACE_PROBE():
        monkeypatch.setattr(simulation.Simulation, "_clearance_points", lambda self: simulation._SURFACE_CLEAR)
    assert REAL_SURFACE_PROBE() is True


def test_r1_emitted_scripts_reverify_their_tools(repo_tmp, fair_check, rbt132_tools):
    """R1 (4): the emitted probes, pays and pays-prize scripts check every tool's blob hash where they run.  The pin
    lines are run on their own here (the verify line needs a clean launch checkout)."""
    import subprocess
    tmp_path = repo_tmp
    steer, harness = tmp_path / "steer.py", tmp_path / "steps.py"
    steer.write_text("# stand-in\n")
    harness.write_text("# stand-in B\n")
    sha, hsha = stages.git_hash(str(steer)), stages.git_hash(str(harness))
    common = ["--fair=--fair", "--root", str(tmp_path)]
    stages.main(["pays", "--steer", str(steer), "--steer-sha", sha, "--pays-cmd", "true {point}",
                 "--steps-harness", str(harness), "--steps-sha", hsha, "--steps-cmd", "true {point}"] + common)
    text = (tmp_path / "lanes" / "pays.sh").read_text()
    assert f'git hash-object {stages.rel(str(steer))}' in text and f'git hash-object {stages.rel(str(harness))}' in text
    assert "stages.py verify " in text and "git hash-object runs/RBT-97/mechanism.py" in text
    pins = tmp_path / "pins.sh"
    pins.write_text("\n".join(x for x in text.splitlines() if x.startswith(("#!", "set -e", "[ \"$(git hash-object"))) + "\n")
    assert subprocess.run(["bash", str(pins)], capture_output=True).returncode == 0
    steer.write_text("# edited after emit\n")
    r = subprocess.run(["bash", str(pins)], capture_output=True, text=True)
    assert r.returncode == 6 and "REFUSED" in r.stderr
    stages.main(["pays-prize"] + common)
    text = (tmp_path / "lanes" / "pays-prize" / "runner0.sh").read_text()
    assert "git hash-object runs/RBT-125/gate/prize_gate.py" in text and "git hash-object runs/RBT-103/routed_populations.py" in text


def test_the_designed_step_leg_is_section_b_unchanged_in_each_cell(repo_tmp, fair_check):
    """The designed nose-step leg: RBT-125 section B's steps.py (#437) on its registered hosts and seeds, with each PAYS
    cell's config.json (S11), restoring RBT-113 O1 where missing, under the same launch record and guards."""
    tmp_path = repo_tmp
    assert stages.main(["pays-steps", "--fair=--fair", EAT, "--root", str(tmp_path), "--runners", "3"]) == 0
    leg = tmp_path / "lanes" / "pays-steps"
    jobs = [x for p in sorted(leg.glob("runner*.sh")) for x in _jobs(p) if "steps.py" in x]
    assert len(jobs) == 18 and all("--seeds" not in x and "--hosts-file" not in x for x in jobs)
    # L-1: the steps input is the verified config directory, not a second, unchecked copy
    for x in jobs:
        pid = x.split("steps.py ")[1].split()[1]
        assert x.split("--config ")[1].split()[0] == stages.rel(os.path.join(str(tmp_path), "worlds", "config", pid))
    text = (leg / "runner0.sh").read_text()
    assert "rbt-113-O1" in text and "stages.py verify " in text and "git hash-object runs/RBT-125/gate/steps.py" in text
    launch = stages.read_launch(str(leg / "launch.txt"))
    assert launch["cells"].split() == list(blocks.PAYS_CELLS) and {k[5:] for k in launch if k.startswith("tool:")} == set(stages.STEP_TOOLS)


def test_l1_an_edited_steps_input_is_refused(repo_tmp, fair_check, monkeypatch):
    """L-1: a committed edit to the file the steps leg reads (motor budget, centre eating) is refused with exit 4."""
    tmp_path = repo_tmp
    stages.main(["pays-steps", "--fair=--fair", EAT, "--root", str(tmp_path)])
    launch = str(tmp_path / "lanes" / "pays-steps" / "launch.txt")
    monkeypatch.setattr(stages, "check_host", lambda launch: None)  # this checkout is mid-edit; exit 5 is tested elsewhere
    stages.verify_leg(launch, str(tmp_path))
    jobs = [x for p in sorted((tmp_path / "lanes" / "pays-steps").glob("runner*.sh")) for x in _jobs(p) if "steps.py" in x]
    target = os.path.join(stages.ROOT, jobs[0].split("--config ")[1].split()[0], "config.json")
    for edit in (("world", "motor_budget", 3.0), ("food", "eat_rule", "centre")):
        cfg = json.load(open(target))
        keep = json.dumps(cfg)
        cfg["sim"][edit[0]][edit[1]] = edit[2]
        open(target, "w").write(json.dumps(cfg))
        with pytest.raises(SystemExit) as e:
            stages.verify_leg(launch, str(tmp_path))
        assert e.value.code == 4, edit
        open(target, "w").write(keep)


def test_fix1_a_unit_extinct_before_the_merge_runs_through(tmp_path, monkeypatch):
    """fix1: when S goes fully extinct before the fork's season, the ecology stops ('everyone died', exit 0) and S60 is
    done early.  The snapshot records EXTINCT.txt instead of refusing, the unit's resume, M, N and K1 fork are marked
    skipped and run nothing, K1ref still runs (and dies at the same season), and K1 reads UNTESTABLE."""
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    doomed = [x for x in TINY]
    doomed[doomed.index("--living-cost") + 1] = "50"  # every member starves in its first season
    (worlds / "doomed.json").write_text(json.dumps({"id": "doomed", "argv": doomed + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    d = tmp_path / "pt" / "7"
    base = {"worlds": str(worlds), "seed": 7}
    jobs = [
        {"job": "fresh", "name": "x/S60", "point": "doomed", "dir": f"{d}/S", "seasons": 3},
        {"job": "snapshot", "name": "x/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "season": 3},
        {"job": "resume", "name": "x/S", "dir": f"{d}/S", "seasons": 5},
        {"job": "fork", "name": "x/M", "src": f"{d}/ckpt60", "dir": f"{d}/M", "seasons": 5, "set": {"merge_after": 3}},
        {"job": "fork", "name": "x/N", "src": f"{d}/ckpt60", "dir": f"{d}/N", "seasons": 5, "set": {"merge_after": 3, "merge_null": "holistic"}},
        {"job": "fresh", "name": "x/K1ref", "point": "doomed", "dir": f"{d}/K1ref", "seasons": 5},
        {"job": "fork", "name": "x/K1fork", "src": f"{d}/ckpt60", "dir": f"{d}/K1fork", "seasons": 5, "set": {}},
        {"job": "k1", "name": "x/K1", "ref": f"{d}/K1ref", "dir": f"{d}/K1fork"},
    ]
    for j in jobs:
        stages.run_job({**base, **j})
    state = json.loads((d / "S" / "state.json").read_text())
    assert state["season"] < 3 and all(len(m) == 0 for m in state["populations"].values())
    assert (d / "EXTINCT.txt").read_text().startswith(f"EXTINCT pre-merge at season {state['season']}:")
    assert stages.extinct_season(str(d)) == state["season"]
    for sub, tag in (("ckpt60", "ckpt60"), ("S", "S"), ("M", "M"), ("N", "N"), ("K1fork", "K1fork")):
        assert "skipped: extinct pre-merge" in (d / sub / f".rbt129-done-{tag}").read_text(), sub
    for sub in ("ckpt60", "M", "N", "K1fork"):
        assert not (d / sub / "state.json").exists(), sub  # nothing was copied or run
    assert (d / "S" / "command.txt").read_text().count("\n") == 1  # S was not resumed
    ref = json.loads((d / "K1ref" / "state.json").read_text())
    assert ref["season"] == state["season"]  # the straight run dies at the same season, deterministically
    assert (d / "K1.txt").read_text().startswith("K1 UNTESTABLE (extinct pre-merge")
    for j in jobs:  # a rerun of the lane is idempotent
        stages.run_job({**base, **j})


def test_fix1_a_partial_s_before_the_merge_still_refuses(tmp_path, monkeypatch):
    """fix1 keeps the refusal for a real lost checkpoint: S short of the fork's season with a fauna alive."""
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    d = tmp_path / "pt" / "7"
    base = {"worlds": str(worlds), "seed": 7}
    stages.run_job({**base, "job": "fresh", "name": "x/S60", "point": "tiny", "dir": f"{d}/S", "seasons": 2})
    state = json.loads((d / "S" / "state.json").read_text())
    assert state["season"] == 2 and any(len(m) for m in state["populations"].values())
    with pytest.raises(SystemExit, match="not the fork's 3"):
        stages.run_job({**base, "job": "snapshot", "name": "x/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "season": 3})
    assert not (d / "EXTINCT.txt").exists()


def test_fix1b_extinction_exactly_at_the_fork_season(tmp_path, monkeypatch):
    """fix1b (the #456 adversary): S that empties in its last pre-merge season reads state.json season == the fork's
    season with every population empty.  That is extinct pre-merge too: the unit runs through and K1 is UNTESTABLE,
    never a false K1 FAIL from a one-season-longer empty fork.  And an emptied S60 whose done-marker was lost (a kill
    after the ecology exits) is not resumed for an extra empty season."""
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    doomed = [x for x in TINY]
    doomed[doomed.index("--living-cost") + 1] = "50"
    (worlds / "doomed.json").write_text(json.dumps({"id": "doomed", "argv": doomed + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    d = tmp_path / "pt" / "7"
    base = {"worlds": str(worlds), "seed": 7}
    stages.run_job({**base, "job": "fresh", "name": "x/S60", "point": "doomed", "dir": f"{d}/S", "seasons": 3})
    at = json.loads((d / "S" / "state.json").read_text())["season"]
    (d / "S" / ".rbt129-done-S60").unlink()  # a kill between the ecology's exit and the marker
    stages.run_job({**base, "job": "fresh", "name": "x/S60", "point": "doomed", "dir": f"{d}/S", "seasons": 3})
    assert json.loads((d / "S" / "state.json").read_text())["season"] == at  # not resumed
    assert (d / "S" / "command.txt").read_text().count("\n") == 1
    jobs = [
        {"job": "snapshot", "name": "x/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "season": at},  # the fork season itself
        {"job": "resume", "name": "x/S", "dir": f"{d}/S", "seasons": at + 4},
        {"job": "fork", "name": "x/M", "src": f"{d}/ckpt60", "dir": f"{d}/M", "seasons": at + 4, "set": {"merge_after": at}},
        {"job": "fresh", "name": "x/K1ref", "point": "doomed", "dir": f"{d}/K1ref", "seasons": at + 4},
        {"job": "fork", "name": "x/K1fork", "src": f"{d}/ckpt60", "dir": f"{d}/K1fork", "seasons": at + 4, "set": {}},
        {"job": "k1", "name": "x/K1", "ref": f"{d}/K1ref", "dir": f"{d}/K1fork"},
    ]
    for j in jobs:
        stages.run_job({**base, **j})
    assert stages.extinct_season(str(d)) == at
    assert not (d / "ckpt60" / "state.json").exists() and not (d / "M" / "state.json").exists()
    assert (d / "K1.txt").read_text().startswith("K1 UNTESTABLE (extinct pre-merge")


# -- the 09:44 brief: durability, K1's marker, the branch check, the calibration lane, the RBT-97 chain ------------- #

def test_prize_and_step_legs_pin_rbt97s_whole_chain():
    """Ruled 07:11: routed_p801.py and g500_direction.py load mechanism.py, which loads resign_rbt67.py; both are pinned."""
    chain = {"runs/RBT-97/mechanism.py", "runs/RBT-97/resign_rbt67.py"}
    chain.add("docs/artifacts/RBT-67/compass_dose_response.py")  # mechanism.py loads it (#465 adversary S-5)
    for tools in (stages.PRIZE_TOOLS, stages.STEP_TOOLS, stages.STEER_TOOLS, stages.PROBE_TOOLS):
        assert chain <= set(tools)
    assert all(os.path.isfile(os.path.join(stages.ROOT, t)) for t in stages.RBT97_CHAIN)
    # planters.py loads probe_power.py at run time (power_line, in the planted set): pinned wherever planters runs
    assert "runs/RBT-116/probe_power.py" in stages.STEER_TOOLS and "runs/RBT-116/probe_power.py" in stages.PROBE_TOOLS


def _fake_durable(tmp_path, monkeypatch, body):
    fake = tmp_path / "repo"
    (fake / "scripts").mkdir(parents=True)
    (fake / "scripts" / "durable.sh").write_text("#!/bin/bash\n" + body)
    (fake / "scripts" / "durable.sh").chmod(0o755)
    monkeypatch.setattr(stages, "ROOT", str(fake))
    monkeypatch.setattr(stages, "DURABLE_LOCK", str(tmp_path / "durable.lock"))
    monkeypatch.setattr(stages, "DURABLE_LOG", str(tmp_path / "durable.log"))
    monkeypatch.setenv("DURABLE_RETRY_S", "0")
    monkeypatch.delenv("NO_DURABLE", raising=False)
    return fake


def test_saves_are_serialized_and_logged(tmp_path, monkeypatch):
    """The 09:44 brief: saves run one at a time on a machine (a lock), in the background (the caller goes on), and each
    outcome is logged with its exit code and durable.sh's output; a failure is retried once, then warned (label and exit
    code only) and logged, never discarded."""
    import time
    spans = tmp_path / "spans"
    _fake_durable(tmp_path, monkeypatch, f'echo "start $(date +%s.%N)" >> {spans}; sleep 0.3; echo "end $(date +%s.%N)" >> {spans}\n'
                  'echo "durable: saved $2 at 7/9"; [ "${3#*bad}" = "$3" ]\n')
    t0 = time.time()
    threads = [stages._save(str(tmp_path / f"d{k}"), f"rbt-129-test-{k}") for k in range(3)]
    assert time.time() - t0 < 0.3  # the caller did not wait
    for t in threads:
        t.join()
    times = [float(x.split()[1]) for x in spans.read_text().splitlines()]
    kinds = [x.split()[0] for x in spans.read_text().splitlines()]
    assert kinds == ["start", "end"] * 3 and times == sorted(times)  # never two at once
    log = (tmp_path / "durable.log").read_text()
    assert log.count(" exit 0\n") == 3 and "durable: saved" in log
    code = stages.save_now(str(tmp_path / "d9"), "rbt-129-bad")
    log = (tmp_path / "durable.log").read_text()
    assert code == 1 and log.count("ckpt/rbt-129-bad") == 2 and log.count(" exit 1\n") == 2  # tried twice, both logged


def test_a_long_job_is_snapshotted_while_it_runs_and_not_after(tmp_path, monkeypatch):
    """A long job's periodic snapshots go through the same serialized save, and stop when the run exits."""
    import time
    calls = []
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: calls.append((d, label, time.time())) or 0)
    monkeypatch.delenv("NO_DURABLE", raising=False)
    monkeypatch.setenv("DURABLE_EVERY_S", "0.2")
    fake = tmp_path / "python"
    fake.write_text("#!/bin/bash\nsleep 1.1\n")
    fake.chmod(0o755)
    monkeypatch.setattr(sys, "executable", str(fake))
    run = tmp_path / "run"
    run.mkdir()
    stages._ecology(["--seasons", "2"], str(run), "rbt-129-long", long=True)
    t_end, n = time.time(), len(calls)
    assert n >= 3 and all(c[1] == "rbt-129-long" for c in calls)
    time.sleep(0.6)
    assert len(calls) == n  # stopped with the run
    stages._ecology(["--seasons", "2"], str(run), "rbt-129-short", long=False)
    assert len(calls) == n  # a short job has no periodic snapshots


def _pilot_chain(d, point, at=3, end=5):
    return [
        {"job": "fresh", "name": "P/x/7/S60", "point": point, "dir": f"{d}/S", "seasons": at},
        {"job": "snapshot", "name": "P/x/7/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "season": at},
        {"job": "resume", "name": "P/x/7/S", "dir": f"{d}/S", "seasons": end},
        {"job": "fork", "name": "P/x/7/M", "src": f"{d}/ckpt60", "dir": f"{d}/M", "seasons": end, "set": {"merge_after": at}},
        {"job": "fresh", "name": "P/x/7/K1ref", "point": point, "dir": f"{d}/K1ref", "seasons": end},
        {"job": "fork", "name": "P/x/7/K1fork", "src": f"{d}/ckpt60", "dir": f"{d}/K1fork", "seasons": end, "set": {}},
        {"job": "k1", "name": "P/x/7/K1", "ref": f"{d}/K1ref", "dir": f"{d}/K1fork"},
    ]


@pytest.mark.parametrize("world", ["tiny", "doomed"])
def test_every_job_and_every_unit_file_is_saved_and_k1_is_marked(tmp_path, monkeypatch, world):
    """The 09:44 brief: every job's directory is saved when it ends (short ones too); the unit's EXTINCT.txt, K1.txt and
    UNIT.txt are mirrored into <unit>/record/ and saved to its own branch; K1 writes a done marker on both its paths
    (verdict and UNTESTABLE), so a rerun neither recompares nor resaves; a unit restored without its files gets them
    back from its record."""
    import shutil
    saves = []
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: saves.append(label or stages._label(d)) or 0)
    monkeypatch.setattr(stages, "_restore", lambda d, probe="state.json": None)
    monkeypatch.delenv("NO_DURABLE", raising=False)
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    argv = list(TINY)
    if world == "doomed":
        argv[argv.index("--living-cost") + 1] = "50"
    (worlds / f"{world}.json").write_text(json.dumps({"id": world, "argv": argv + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    d = tmp_path / "pt" / "7"
    base = {"worlds": str(worlds), "seed": 7}
    at = 3
    if world == "doomed":
        stages.run_job({**base, **_pilot_chain(d, world)[0]})
        at = json.loads((d / "S" / "state.json").read_text())["season"]
    jobs = _pilot_chain(d, world, at, at + 2)
    for j in jobs:
        stages.run_job({**base, **j})
    for t in list(__import__("threading").enumerate()):
        if t.name.startswith("save "):
            t.join()
    lab = stages._label
    rec = d / "record"
    want = {lab(str(d / x)) for x in ("S", "ckpt60", "M", "K1ref", "K1fork")} | {lab(str(rec))}
    assert want <= set(saves)
    names = {"UNIT.txt", "K1.txt"} | ({"EXTINCT.txt"} if world == "doomed" else set())
    assert set(os.listdir(rec)) == names
    for n in names:
        assert (rec / n).read_text() == (d / n).read_text()
    k1 = (d / "K1.txt").read_text()
    assert k1.startswith("K1 UNTESTABLE" if world == "doomed" else "K1 PASS")
    assert (d / "K1fork" / ".rbt129-done-K1").exists()
    n = len(saves)
    (d / "K1.txt").write_text("sentinel\n")
    for j in jobs:
        stages.run_job({**base, **j})
    assert len(saves) == n and (d / "K1.txt").read_text() == "sentinel\n"  # nothing re-run or re-saved
    for n_ in names:
        (d / n_).unlink()
    stages.restore_record(str(d))
    assert (d / "K1.txt").read_text() == (rec / "K1.txt").read_text()
    if world == "doomed":
        assert stages.extinct_season(str(d)) == at and stages.unit_status(str(d)) == "extinct"
    else:
        assert stages.unit_status(str(d)) == "alive"
    shutil.rmtree(rec)
    for n_ in ("UNIT.txt", "EXTINCT.txt"):
        if (d / n_).exists():
            (d / n_).unlink()
    # a unit written before records existed is read from its ckpt60 done-marker (#465 M-1, S-3), extinct ones included
    assert stages.unit_status(str(d)) == ("extinct" if world == "doomed" else "alive")
    assert ("K1 UNTESTABLE" if world == "doomed" else "K1 PASS") in (d / "K1fork" / ".rbt129-done-K1").read_text()  # S-3
    mark = (d / "ckpt60" / ".rbt129-done-ckpt60").read_text()
    (d / "ckpt60" / ".rbt129-done-ckpt60").unlink()
    monkeypatch.setattr(stages, "branch_file", lambda label, member: mark if label == stages._label(str(d / "ckpt60")) else None)
    assert stages.unit_status(str(d)) == ("extinct" if world == "doomed" else "alive")  # the marker from ckpt60's branch
    monkeypatch.setattr(stages, "branch_file", lambda label, member: None)
    assert stages.unit_status(str(d)) is None


def test_check_branches_names_every_run_dir_and_unit_without_a_branch(repo_tmp, monkeypatch, capsys):
    """Readout side (09:44): every run directory a lane writes and every pilot unit's record must have a checkpoint
    branch; the missing ones are named (labels only) and the exit is 1; --save snapshots those on this machine."""
    root = repo_tmp
    unit = root / "stageP" / "c0-p030-PW-G" / "129001"
    lane = root / "lane.jsonl"
    jobs = [{"job": "fresh", "name": "P/c0-p030-PW-G/129001/S60", "dir": stages.rel(str(unit / "S")), "seed": 129001},
            {"job": "snapshot", "name": "P/c0-p030-PW-G/129001/ckpt60", "src": stages.rel(str(unit / "S")), "dir": stages.rel(str(unit / "ckpt60")), "seed": 129001},
            {"job": "k1", "name": "P/c0-p030-PW-G/129001/K1", "ref": stages.rel(str(unit / "K1ref")), "dir": stages.rel(str(unit / "K1fork")), "seed": 129001},
            {"job": "fresh", "name": "0/c0-p030-U-L/129002/S", "dir": stages.rel(str(root / "stage0" / "c0-p030-U-L" / "129002" / "S")), "seed": 129002}]
    lane.write_text("".join(json.dumps(j) + "\n" for j in jobs))
    want = stages.expected_branches([str(lane)])
    labels = {stages._label(str(unit / x)) for x in ("S", "ckpt60", "K1fork", "record")} | {stages._label(str(root / "stage0" / "c0-p030-U-L" / "129002" / "S"))}
    assert set(want) == labels
    remote = set(labels) - {stages._label(str(unit / "record")), stages._label(str(unit / "K1fork"))}
    monkeypatch.setattr(stages, "remote_ckpt", lambda: set(remote))
    assert stages.main(["check-branches", str(lane)]) == 1
    out = capsys.readouterr().out
    assert out.count("MISSING ckpt/") == 2 and "3 of 5 run directories" in out and stages._label(str(unit / "record")) in out
    (unit / "record").mkdir(parents=True)
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: remote.add(label) or 0)
    assert stages.main(["check-branches", str(lane), "--save"]) == 1  # K1fork is not on this machine
    out = capsys.readouterr().out
    assert out.count("MISSING ckpt/") == 1 and "not on this machine" in out
    remote.add(stages._label(str(unit / "K1fork")))
    assert stages.main(["check-branches", str(lane)]) == 0


def _plant_rec(dts, conf_dts=None, c3=True):
    import numpy as np
    steer = stages._steer()

    def stats(x):
        x = np.asarray(x, float)
        lb = steer.lower_bound(x)
        return {"n": len(x), "F": 0.9, "lbF": 0.1, "dT": float(x.mean()), "lbdT": lb, "c1": True, "c2": bool(lb > 0), "c3": c3}
    rec = {"call": "STEERS", "stage": 3, "stage2": stats(dts)}
    if conf_dts is not None:
        rec["k3_confirm"] = stats(conf_dts)
    return rec


def test_calib_extract_prints_only_seen_and_dt(tmp_path):
    """The calibration lane's only printed lines: per (a) and (c) plant SEEN, dT's mean and SD (SD recovered exactly
    from the bound) and n, on stage 2 and the confirmation, and the SEEN share per kind; no F, call or K3/K4."""
    import numpy as np
    x = [0.3, 0.1, 0.4, 0.2, 0.35, 0.15, 0.25, 0.3]
    recs = {"a": [_plant_rec(x, x), _plant_rec([-0.1, 0.1, -0.2, 0.05, 0.0, -0.1, 0.1, -0.05]),
                  _plant_rec(x, [0.3, -0.2, 0.1, -0.3, 0.2, -0.1, 0.05, -0.2])],  # N-2: stage 2 passes, the confirmation not
            "c": [_plant_rec(x, x, c3=False)], "b": [_plant_rec(x, x)], "motors-off": [_plant_rec(x)]}
    p = tmp_path / "planted.json"
    p.write_text(json.dumps({"point": "c0-p030-PW-G", "K": {"K3": True, "K3_seen": [1, 0]}, "carrying": {"a": "8 of 9"}, "calls": recs}))
    out = stages.calib_extract(str(p))
    rows = [r.split() for r in out.splitlines()[2:-1]]
    assert [r[:3] for r in rows] == [["a", "0", "yes"], ["a", "1", "no"], ["a", "2", "no"], ["c", "0", "no"]]
    assert float(rows[0][4]) == pytest.approx(float(np.std(x, ddof=1)), abs=1e-4)
    assert float(rows[0][3]) == pytest.approx(float(np.mean(x)), abs=1e-4) and rows[0][5] == "8" and rows[0][8] == "8"
    assert rows[1][6:] == ["-", "-", "-"]  # no confirmation ran
    assert out.splitlines()[-1] == "SEEN share: (a) 1 of 3 = 0.333; (c) 0 of 1 = 0.000"
    for word in ("F", "STEERS", "K3", "K4", "carrying", "8 of 9", "motors"):
        assert word not in out.split("\n", 1)[1], word


def test_seen_is_planters_seen():
    """calib-extract's SEEN is RBT-132's (the 07:10 ruling), read the same way."""
    path = os.path.join(stages.ROOT, "runs", "RBT-116", "planters.py")
    if not os.path.isfile(path):
        pytest.skip("RBT-132's planters.py is not on this tree yet (#459)")
    sys.path.insert(0, os.path.dirname(path))
    import planters
    x = [0.3, 0.1, 0.4, 0.2]
    for r in (_plant_rec(x, x), _plant_rec(x), _plant_rec(x, x, c3=False), {"call": "NONE", "stage": 1}):
        assert stages._seen(r) == planters.seen(r)


def test_the_calibration_lane(repo_tmp, fair_check, rbt132_tools, monkeypatch):
    """The 09:44 amendment's calibration: refused (exit 6) until planters.py is on the tree; then one runner for the two
    cells (c0-p030-PW-G, c0-p030-HP-G) with the leg's guards, RBT-132's and RBT-97's tools pinned and O1 restored.  Run
    against a stand-in planters.py that prints and logs F and K3, its output is exactly calib-extract's lines; a failing
    cell prints only its directory and exit code, the other cell still runs, and the runner exits 1."""
    import subprocess
    tmp_path = repo_tmp
    monkeypatch.setenv("NO_DURABLE", "1")
    common = ["calibrate", "--fair=--fair", EAT, "--root", str(tmp_path)]
    with monkeypatch.context() as m:
        m.setattr(stages, "STEER_TOOLS", stages.STEER_TOOLS[:1] + ("runs/RBT-129/_absent/planters.py",) + stages.STEER_TOOLS[2:])
        with pytest.raises(SystemExit) as e:
            stages.main(common)
        assert e.value.code == 6
    stand_path = tmp_path / "tools" / "planters_standin.py"  # never the real planters.py, once it is on the tree
    stand_path.parent.mkdir(exist_ok=True)
    monkeypatch.setattr(stages, "PLANTERS", stages.rel(str(stand_path)))
    planted = json.dumps({"point": "P", "K": {"K3": True}, "calls": {"a": [_plant_rec([0.3, 0.1, 0.4, 0.2], [0.3, 0.2, 0.4, 0.1])], "c": []}})
    stand_path.write_text(
        "import json, os, sys\n"
        "point, out = sys.argv[2], sys.argv[4]\n"
        "print('F +0.512 STEERS K3 PASS')\n"
        "if point.endswith('HP-G'):\n    sys.exit(8)\n"
        "os.makedirs(out, exist_ok=True)\n"
        "open(os.path.join(out, 'planted.txt'), 'w').write('K3 PASS F +0.512\\n')\n"
        f"open(os.path.join(out, 'planted.json'), 'w').write({planted!r})\n")
    assert stages.main(common) == 0
    leg = tmp_path / "lanes" / "calibrate"
    text = (leg / "runner.sh").read_text()
    launch = stages.read_launch(str(leg / "launch.txt"))
    assert launch["cells"].split() == ["c0-p030-PW-G", "c0-p030-HP-G"] and {k[5:] for k in launch if k.startswith("tool:")} == set(stages.STEER_TOOLS)
    assert "stages.py verify " in text and "rbt-113-O1" in text and "git hash-object runs/RBT-97/resign_rbt67.py" in text
    jobs = [x for x in _jobs(leg / "runner.sh") if not x.startswith("scripts/durable.sh")]
    assert sum(f"planted {c} " in x for x in jobs for c in stages.CALIB_CELLS) == 2
    assert all(" --hosts runs/RBT-129/hosts113 --workers 4" in x for x in jobs if " planted " in x)
    script = tmp_path / "jobs.sh"
    script.write_text("set -e\n" + "\n".join(jobs) + "\n")
    env = {**os.environ, "PATH": os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"]}
    r = subprocess.run(["bash", str(script)], cwd=stages.ROOT, capture_output=True, text=True, env=env)
    assert r.returncode == 1
    pw = stages.rel(str(tmp_path / "calibration" / "c0-p030-PW-G"))
    hp = stages.rel(str(tmp_path / "calibration" / "c0-p030-HP-G"))
    assert r.stdout == open(os.path.join(stages.ROOT, pw, "calibration.txt")).read()
    assert r.stdout.startswith("# RBT-129 K3 calibration at P") and "SEEN share: (a) 1 of 1" in r.stdout
    assert r.stderr.strip() == f"FAILED: {hp} (exit 8)"
    assert "+0.512" not in r.stdout + r.stderr and "K3 PASS" not in r.stdout + r.stderr
    r2 = subprocess.run(["bash", str(script)], cwd=stages.ROOT, capture_output=True, text=True, env=env)
    assert r2.stdout == r.stdout and r2.stderr == r.stderr  # the done cell is not re-run; its record is re-printed


def test_a_hung_save_is_killed_logged_retried_and_releases_the_lock(tmp_path, monkeypatch, capsys):
    """#465 adversary M-2: a save past its timeout is killed with its process group (the push included), logged as
    exit timeout, retried once, then warned; the lock is free afterwards and the caller returns."""
    import fcntl
    import time
    pids = tmp_path / "pids"
    _fake_durable(tmp_path, monkeypatch, f"sleep 60 & echo $! >> {pids}; wait\n")
    monkeypatch.setenv("DURABLE_TIMEOUT_S", "0.5")
    t0 = time.time()
    code = stages.save_now(str(tmp_path / "d"), "rbt-129-hung")
    assert code != 0 and time.time() - t0 < 10
    log = (tmp_path / "durable.log").read_text()
    assert log.count("ckpt/rbt-129-hung") == 2 and log.count(" exit timeout\n") == 2
    assert "WARN: durable save ckpt/rbt-129-hung failed (exit timeout" in capsys.readouterr().err
    with open(stages.DURABLE_LOCK, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # free: raises if still held
    time.sleep(0.2)
    for pid in pids.read_text().split():
        try:
            os.kill(int(pid), 0)
            alive = open(f"/proc/{pid}/stat").read().split()[2] != "Z"
        except (ProcessLookupError, FileNotFoundError):
            alive = False
        assert not alive, pid  # the grandchild (the "push") was killed too


def test_the_periodic_save_is_not_a_daemon_and_ends_after_its_save(tmp_path, monkeypatch):
    """#465 adversary S-2: the periodic thread is not a daemon; stopped mid-save, it finishes (and logs) that save,
    then ends."""
    import threading
    import time
    events = []

    def slow(d, label=None, retries=1):
        events.append("start")
        time.sleep(0.6)
        events.append("end")
        return 0
    monkeypatch.setattr(stages, "save_now", slow)
    monkeypatch.delenv("NO_DURABLE", raising=False)
    monkeypatch.setenv("DURABLE_EVERY_S", "0.3")
    fake = tmp_path / "python"
    fake.write_text("#!/bin/bash\nsleep 0.5\n")
    fake.chmod(0o755)
    monkeypatch.setattr(sys, "executable", str(fake))
    run = tmp_path / "run"
    run.mkdir()
    stages._ecology(["--seasons", "2"], str(run), "rbt-129-mid", long=True)
    t = [x for x in threading.enumerate() if x.name == "every rbt-129-mid"]
    assert t and not t[0].daemon and events[-1] == "start"  # stopped while a save runs
    t[0].join(5)
    assert not t[0].is_alive() and events == ["start", "end"]


def test_check_branches_backfills_stage_p_units_from_another_checkout(tmp_path, monkeypatch, capsys):
    """#465 adversary M-1, end to end on a real git remote: a Stage P checkout whose units ran before records existed
    (EXTINCT.txt, K1.txt and the ckpt60 marker in the container only).  ``check-branches --repo DIR`` names the missing
    records; ``--save`` backfills them from the unit files and ckpt60's marker and saves them; and a unit's status is
    then read from ckpt60's branch on a machine with none of its files."""
    import shutil
    import subprocess
    monkeypatch.setattr(stages, "ROOT", stages.ROOT)  # set_repo moves these; restored after the test
    monkeypatch.setattr(stages, "RUNS", stages.RUNS)
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"), ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(k, v)
    here = stages.ROOT
    bare, repo = tmp_path / "origin.git", tmp_path / "stageP-session"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", str(bare)], check=True)
    (repo / "scripts").mkdir()
    shutil.copy(os.path.join(here, "scripts", "durable.sh"), repo / "scripts" / "durable.sh")
    monkeypatch.setattr(stages, "DURABLE_LOCK", str(tmp_path / "durable.lock"))
    monkeypatch.setattr(stages, "DURABLE_LOG", str(tmp_path / "durable.log"))
    monkeypatch.delenv("NO_DURABLE", raising=False)
    runs = repo / "runs" / "RBT-129"
    jobs = []
    for pid, extinct in (("c0-p030-PW-G", True), ("c1-p030-PW-G", False)):
        u = runs / "stageP" / pid / "129001"
        (u / "S").mkdir(parents=True)
        (u / "S" / "state.json").write_text("{}")
        (u / "ckpt60").mkdir()
        (u / "ckpt60" / ".rbt129-done-ckpt60").write_text("2026-09-28T05:00:00Z" + (" skipped: extinct pre-merge at season 12" if extinct else "") + "\n")
        (u / "K1.txt").write_text("K1 UNTESTABLE (extinct pre-merge at season 12)\n" if extinct else "K1 PASS: test\n")
        if extinct:
            (u / "EXTINCT.txt").write_text("EXTINCT pre-merge at season 12: test\n")
        r = f"runs/RBT-129/stageP/{pid}/129001"
        jobs += [{"job": "fresh", "name": f"P/{pid}/129001/S60", "dir": f"{r}/S", "seed": 129001},
                 {"job": "snapshot", "name": f"P/{pid}/129001/ckpt60", "src": f"{r}/S", "dir": f"{r}/ckpt60", "seed": 129001}]
    lane = tmp_path / "host0-lane0.jsonl"
    lane.write_text("".join(json.dumps(j) + "\n" for j in jobs))
    assert stages.main(["check-branches", str(lane), "--repo", str(repo)]) == 1
    out = capsys.readouterr().out
    assert out.count("MISSING ckpt/") == 6 and "0 of 6" in out
    assert stages.main(["check-branches", str(lane), "--repo", str(repo), "--save"]) == 0
    assert "6 of 6" in capsys.readouterr().out
    u0 = runs / "stageP" / "c0-p030-PW-G" / "129001"
    assert (u0 / "record" / "EXTINCT.txt").read_text() == (u0 / "EXTINCT.txt").read_text()
    assert "extinct pre-merge" in (u0 / "record" / "UNIT.txt").read_text() and (u0 / "record" / "K1.txt").exists()
    assert "season-60 checkpoint" in (runs / "stageP" / "c1-p030-PW-G" / "129001" / "record" / "UNIT.txt").read_text()
    assert "extinct pre-merge at season 12" in stages.branch_file("rbt-129-stageP-c0-p030-PW-G-129001-ckpt60", ".rbt129-done-ckpt60")
    for pid, want in (("c0-p030-PW-G", "extinct"), ("c1-p030-PW-G", "alive")):
        u = runs / "stageP" / pid / "129001"
        shutil.rmtree(u)
        monkeypatch.setattr(stages, "restore_record", lambda unit: None)  # no record: ckpt60's branch alone decides
        assert stages.unit_status(str(u)) == want, pid


def test_the_stage2_calibration_lane(repo_tmp, fair_check, monkeypatch):
    """DESIGN 12, the 12:52 amendment (S2): the second stage is emitted only with planters' calibration-only flag, and
    only when this tree's planters.py takes it (exit 6 otherwise); it runs both cells into calibration-s2/<cell>, saved
    to its own branches, with the same pins and guards and the same printed lines, and leaves the 16-draw lane alone."""
    tmp_path = repo_tmp
    common = ["calibrate", "--fair=--fair", EAT, "--root", str(tmp_path)]
    monkeypatch.setattr(stages, "planters_accepts", lambda flag: False)
    with pytest.raises(SystemExit) as e:
        stages.main(common + ["--stage2=--confirm-all"])
    assert e.value.code == 6 and not (tmp_path / "lanes" / "calibrate-s2").exists()
    monkeypatch.setattr(stages, "planters_accepts", lambda flag: flag == "--confirm-all")
    assert stages.main(common + ["--stage2=--confirm-all"]) == 0
    leg = tmp_path / "lanes" / "calibrate-s2"
    text = (leg / "runner.sh").read_text()
    launch = stages.read_launch(str(leg / "launch.txt"))
    assert launch["stage2"] == "--confirm-all" and launch["cells"].split() == list(stages.CALIB_CELLS)
    assert {k[5:] for k in launch if k.startswith("tool:")} == set(stages.STEER_TOOLS) and "stages.py verify " in text
    planted = [x for x in text.splitlines() if " planted " in x]
    assert len(planted) == 2 and all(" --workers 4 --confirm-all > " in x for x in planted)
    for c in stages.CALIB_CELLS:
        d = stages.rel(str(tmp_path / "calibration-s2" / c))
        assert f"stages.py save {d};" in text and f"cat {d}/calibration.txt" in text
        assert f"durable.sh restore {d} {stages._label(os.path.join(stages.ROOT, d))} " in text
        assert stages._label(os.path.join(stages.ROOT, d)).endswith(f"-calibration-s2-{c}")  # its own branch
    assert not (tmp_path / "lanes" / "calibrate").exists()
    assert stages.main(common) == 0
    assert "--confirm-all" not in (tmp_path / "lanes" / "calibrate" / "runner.sh").read_text()


def test_planters_accepts_reads_the_real_help():
    """The flag check reads planters.py's own --help (no season runs): a flag it has passes, an invented one does not."""
    assert stages.planters_accepts("--hosts") and stages.planters_accepts("--workers=4")
    assert not stages.planters_accepts("--no-such-flag")


def test_the_steps_remeasurement_lane_at_c1_and_c2(repo_tmp, fair_check, monkeypatch):
    """The coordinator's ruling on #467: the steps leg re-measured at the 12 c >= 1 PAYS cells, on 128 fresh seeds from
    126000 with --exclude-exploded (#475), the same hosts, verified configs and flags; cells split over 3 runners, each
    output saved to ckpt/rbt-129-stage0-pays-<cell>-steps2.  Refused (exit 6) while steps.py has no --exclude-exploded."""
    tmp_path = repo_tmp
    common = ["pays-steps2", "--fair=--fair", EAT, "--root", str(tmp_path)]
    real = os.path.join(stages.ROOT, stages.STEP_TOOLS[0])
    if "--exclude-exploded" not in open(real).read():
        with pytest.raises(SystemExit) as e:
            stages.main(common)
        assert e.value.code == 6 and not (tmp_path / "lanes" / "pays-steps-c1c2").exists()
        stand = tmp_path / "steps.py"
        stand.write_text(open(real).read() + "\n# stand-in: --exclude-exploded\n")
        monkeypatch.setattr(stages, "STEP_TOOLS", (stages.rel(str(stand)),) + stages.STEP_TOOLS[1:])
    assert len(stages.STEPS2_CELLS) == 12 and all(not p.startswith("c0-") for p in stages.STEPS2_CELLS)
    assert stages.main(common) == 0
    leg = tmp_path / "lanes" / "pays-steps-c1c2"
    scripts = sorted(leg.glob("runner*.sh"))
    assert [p.name for p in scripts] == ["runner0.sh", "runner1.sh", "runner2.sh"]
    jobs = [[x for x in _jobs(p) if "steps.py" in x] for p in scripts]
    assert [len(j) for j in jobs] == [4, 4, 4]
    cells = [{x.split("steps.py ")[1].split()[1] for x in j} for j in jobs]
    assert set().union(*cells) == set(stages.STEPS2_CELLS) and sum(len(c) for c in cells) == 12
    for x in (x for j in jobs for x in j):
        pid = x.split("steps.py ")[1].split()[1]
        assert x.split("steps.py ")[1].split()[0] == "runs/RBT-129/hosts113"
        assert f"--config {stages.rel(os.path.join(str(tmp_path), 'worlds', 'config', pid))} " in x
        assert " --procs 4 --seed0 126000 --exclude-exploded " in x and "--seeds" not in x and "--hosts-file" not in x
        d = stages.rel(os.path.join(str(tmp_path), "stage0", "pays", pid, "steps2"))
        assert f"durable.sh save {d} {stages._label(os.path.join(stages.ROOT, d))} " in x
        assert stages._label(os.path.join(stages.ROOT, d)).endswith(f"-stage0-pays-{pid}-steps2")
    text = scripts[0].read_text()
    assert "rbt-113-O1" in text and "stages.py verify " in text and "git hash-object runs/RBT-97/resign_rbt67.py" in text
    launch = stages.read_launch(str(leg / "launch.txt"))
    assert launch["cells"].split() == list(stages.STEPS2_CELLS) and launch["flags"] == "--seed0 126000 --exclude-exploded"
    assert {k[5:] for k in launch if k.startswith("tool:")} == set(stages.STEP_TOOLS)


def test_a_calibration_rerun_has_its_own_outputs_and_branches(repo_tmp, fair_check, monkeypatch):
    """The re-run under the (c) screen rule (ruling on #478): --rerun TAG writes calibration-TAG[-s2]/<cell> and
    lanes/calibrate-TAG[-s2]/, so it never restores or resumes the earlier run's directories or branches; the S2 lane
    composes with it; a malformed tag is refused."""
    tmp_path = repo_tmp
    common = ["calibrate", "--fair=--fair", EAT, "--root", str(tmp_path)]
    monkeypatch.setattr(stages, "planters_accepts", lambda flag: flag == "--calibration")
    with pytest.raises(SystemExit) as e:
        stages.main(common + ["--rerun", "c/../x"])
    assert e.value.code == 4
    assert stages.main(common + ["--rerun", "c"]) == 0
    assert stages.main(common + ["--rerun", "c", "--stage2=--calibration"]) == 0
    for leg, out, flag in (("calibrate-c", "calibration-c", False), ("calibrate-c-s2", "calibration-c-s2", True)):
        text = (tmp_path / "lanes" / leg / "runner.sh").read_text()
        launch = stages.read_launch(str(tmp_path / "lanes" / leg / "launch.txt"))
        assert launch["rerun"] == "c" and (launch.get("stage2") == "--calibration") == flag
        for c in stages.CALIB_CELLS:
            d = stages.rel(str(tmp_path / out / c))
            assert f"durable.sh restore {d} {stages._label(os.path.join(stages.ROOT, d))} " in text
            assert stages._label(os.path.join(stages.ROOT, d)).endswith(f"-{out}-{c}")
        assert "/calibration/" not in text  # the earlier run's directories are never touched
        assert all((" --calibration > " in x) == flag for x in text.splitlines() if " planted " in x)
    assert not (tmp_path / "lanes" / "calibrate").exists()


# -- the lost-save hazard: a job is done only once its done-marker is on its branch ----------------------------------- #

def _join_saves():
    import threading
    for t in list(threading.enumerate()):
        if t.name.startswith("save "):
            t.join()


def _extinct_resume(tmp_path):
    """A job that writes its marker and saves without running the ecology: a resume in a unit extinct pre-merge."""
    unit = tmp_path / "stage1" / "c0-p080-U-G" / "129005"
    unit.mkdir(parents=True)
    (unit / stages.EXTINCT).write_text("EXTINCT pre-merge at season 41: test\n")
    return {"job": "resume", "name": "0/c0-p080-U-G/129005/S", "dir": str(unit / "S"), "seed": 129005, "seasons": 300}


def test_a_lane_killed_between_marker_and_save_saves_the_marker_before_it_skips(tmp_path, monkeypatch, capsys):
    """Stage 1's lost save (host9, c0-p080-U-G/129005/ckpt60): the lane process is SIGKILLed after the done-marker is
    written, while its background save is still running.  On restart the job is not re-run, but its directory is saved,
    marker included, before the skip; a later restart neither saves nor runs it again."""
    import signal
    import subprocess
    import time
    saves, saving = tmp_path / "saves", tmp_path / "saving"
    fake = _fake_durable(tmp_path, monkeypatch, f'case "$1" in\n'
                         f'  save) if [ -n "$HANG" ]; then echo $$ > {saving}; exec sleep 60; fi\n'
                         f'        echo "$3 $(ls -A "$2" | grep "^\\.rbt129-done-" | tr "\\n" " ")" >> {saves} ;;\n'
                         f'  *) exit 1 ;;\nesac\n')
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "receipts"))
    job = _extinct_resume(tmp_path)
    child = (f"import sys, json; sys.path.insert(0, {os.path.dirname(stages.__file__)!r}); import stages\n"
             f"stages.ROOT, stages.DURABLE_DONE = {str(fake)!r}, {str(tmp_path / 'receipts')!r}\n"
             f"stages.DURABLE_LOCK, stages.DURABLE_LOG = {stages.DURABLE_LOCK!r}, {stages.DURABLE_LOG!r}\n"
             f"stages.run_job(json.loads({json.dumps(job)!r}))\n")
    env = {**os.environ, "HANG": "1"}
    env.pop("NO_DURABLE", None)
    proc = subprocess.Popen([sys.executable, "-c", child], cwd=stages.ROOT, env=env, start_new_session=True)
    t0 = time.time()
    while not (saving.exists() and saving.read_text().strip()) and time.time() - t0 < 60:
        time.sleep(0.05)
    assert saving.exists(), "the final save never started"
    os.killpg(proc.pid, signal.SIGKILL)  # the 2 h cap: the lane dies inside its final save
    os.kill(int(saving.read_text()), signal.SIGKILL)
    proc.wait()
    mark = tmp_path / "stage1" / "c0-p080-U-G" / "129005" / "S" / ".rbt129-done-S"
    assert mark.exists() and not saves.exists() and not list((tmp_path / "receipts").glob("*.S"))
    text = mark.read_text()
    assert stages._done(str(mark.parent), "S")  # the old test: the restarted lane would have skipped it unsaved
    stages.run_job(job)  # the restart
    _join_saves()
    label = stages._label(str(mark.parent))
    assert saves.read_text() == f"{label} .rbt129-done-S \n"  # one save, the marker in it
    assert mark.read_text() == text  # not re-run
    assert (tmp_path / "receipts" / f"{label}.S").read_text() == text
    assert "has no saved snapshot" in capsys.readouterr().err
    stages.run_job(job)  # a second restart: the receipt says the branch has it
    _join_saves()
    assert saves.read_text().count("\n") == 1


def test_a_finished_fresh_job_whose_save_never_ran_is_saved_not_rerun(tmp_path, monkeypatch):
    """The main path (a fresh run): marker written, the save thread never ran (killed); the restart saves it, once."""
    monkeypatch.setenv("WORKERS", "1")
    monkeypatch.delenv("NO_DURABLE", raising=False)
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "receipts"))
    monkeypatch.setattr(stages, "_restore", lambda d, probe="state.json": None)
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    d = tmp_path / "pt" / "7" / "S"
    job = {"worlds": str(worlds), "seed": 7, "job": "fresh", "name": "x/S60", "point": "tiny", "dir": str(d), "seasons": 2}
    saved, killed, save = [], [True], stages._save
    monkeypatch.setattr(stages, "_save", lambda *a, **k: None if killed[0] else save(*a, **k))  # killed before the save
    stages.run_job(job)
    assert (d / ".rbt129-done-S60").exists() and not list((tmp_path / "receipts").glob("*.S60"))
    killed[0] = False
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: saved.append(sorted(os.listdir(d))) or 0)
    for _ in range(2):
        stages.run_job(job)
        _join_saves()
    assert len(saved) == 1 and ".rbt129-done-S60" in saved[0]
    assert (d / "command.txt").read_text().count("\n") == 1  # the run itself was not repeated


def test_a_failed_final_save_is_retried_at_the_next_restart(tmp_path, monkeypatch, capsys):
    """A final save that fails leaves no receipt; each restart saves again until one exits 0.  Never a re-run."""
    monkeypatch.delenv("NO_DURABLE", raising=False)
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "receipts"))
    monkeypatch.setattr(stages, "_restore", lambda d, probe="state.json": None)
    codes, saved = [1, 1, 0], []
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: saved.append(d) or codes[len(saved) - 1])
    job = _extinct_resume(tmp_path)
    for _ in range(4):
        stages.run_job(job)  # the first runs it (background save fails), the next two save and fail/succeed
        _join_saves()
    assert len(saved) == 3
    assert (tmp_path / "receipts" / f"{stages._label(job['dir'])}.S").read_text() == stages._marker_text(job["dir"], "S")


def test_no_durable_counts_the_marker_alone(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "receipts"))
    monkeypatch.setattr(stages, "save_now", lambda *a, **k: pytest.fail("NO_DURABLE saved"))
    d = tmp_path / "S"
    assert not stages._finished(str(d), "S")
    stages._finish(str(d), "S")
    assert stages._finished(str(d), "S") and not (tmp_path / "receipts").exists()


def test_a_restored_marker_is_on_its_branch_and_a_local_one_is_not(tmp_path, monkeypatch):
    """A marker the restore brought back came from the branch: receipted, no save.  A marker already here before the
    restore, unchanged by it, proves nothing: it is saved before the skip."""
    fake = _fake_durable(tmp_path, monkeypatch, 'mkdir -p "$2" && echo 9 > "$2/state.json" && echo "t0" > "$2/.rbt129-done-S"\n')
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "receipts"))
    saved = []
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: saved.append(d) or 0)
    d = str(tmp_path / "a" / "S")
    stages._restore(d)
    assert stages._finished(d, "S") and saved == []
    e = str(tmp_path / "b" / "S")
    os.makedirs(e)
    with open(os.path.join(e, ".rbt129-done-S"), "w") as f:
        f.write("t0\n")
    stages._restore(e)  # brings the same text: not shown to be from the branch
    assert stages._finished(e, "S") and saved == [e]
    (fake / "scripts" / "durable.sh").write_text('#!/bin/bash\nexit 1\n')
    g = str(tmp_path / "g" / "S")
    stages._restore(g)  # no branch yet, nothing unpacked: as before, no receipt and no sentinel
    assert sorted(os.listdir(tmp_path / "receipts")) == sorted([f"{stages._label(d)}.S", f"{stages._label(e)}.S"])
    (fake / "scripts" / "durable.sh").write_text('#!/bin/bash\nmkdir -p "$2" && echo "t1" > "$2/.rbt129-done-S"; exit 1\n')
    f = str(tmp_path / "c" / "S")
    with pytest.raises(SystemExit) as x:  # a restore that fails part-way receipts nothing, and the lane stops
        stages._restore(f)
    assert x.value.code == 7
    assert not os.path.exists(os.path.join(str(tmp_path / "receipts"), f"{stages._label(f)}.S"))


def test_m1_a_lane_killed_inside_a_restore_restores_again_and_never_saves_the_part(tmp_path, monkeypatch, capsys):
    """#510 adversary M-1: durable.sh restore unpacks in place.  A lane SIGKILLed inside it leaves state.json and the
    done-marker but not lineage.jsonl; the restart must not save that part over the complete snapshot (a force-push):
    it restores again, whatever the probe says, and the restored marker is then on its branch (no save at all)."""
    import signal
    import subprocess
    import time
    saves, saving = tmp_path / "saves", tmp_path / "saving"
    fake = _fake_durable(tmp_path, monkeypatch, f'case "$1" in\n'
                         f'  restore) [ ! -e "$2/state.json" ] || exit 1; mkdir -p "$2"; echo s > "$2/state.json"\n'
                         f'           echo t0 > "$2/.rbt129-done-S"\n'
                         f'           if [ -n "$HANG" ]; then echo $$ > {saving}; exec sleep 60; fi\n'
                         f'           echo l > "$2/lineage.jsonl" ;;\n'
                         f'  save) echo "$3 $(ls -A "$2" | tr "\\n" " ")" >> {saves} ;;\nesac\n')
    receipts = str(tmp_path / "receipts")
    monkeypatch.setattr(stages, "DURABLE_DONE", receipts)
    job = _extinct_resume(tmp_path)
    child = (f"import sys, json; sys.path.insert(0, {os.path.dirname(stages.__file__)!r}); import stages\n"
             f"stages.ROOT, stages.DURABLE_DONE = {str(fake)!r}, {receipts!r}\n"
             f"stages.DURABLE_LOCK, stages.DURABLE_LOG = {stages.DURABLE_LOCK!r}, {stages.DURABLE_LOG!r}\n"
             f"stages.run_job(json.loads({json.dumps(job)!r}))\n")
    env = {**os.environ, "HANG": "1"}
    env.pop("NO_DURABLE", None)
    proc = subprocess.Popen([sys.executable, "-c", child], cwd=stages.ROOT, env=env, start_new_session=True)
    t0 = time.time()
    while not (saving.exists() and saving.read_text().strip()) and time.time() - t0 < 60:
        time.sleep(0.05)
    os.killpg(proc.pid, signal.SIGKILL)  # killed inside the restore
    os.kill(int(saving.read_text()), signal.SIGKILL)
    proc.wait()
    d = job["dir"]
    assert sorted(os.listdir(d)) == [".rbt129-done-S", "state.json"]  # the part: the probe is there, lineage is not
    stages.run_job(job)  # the restart
    _join_saves()
    assert set(os.listdir(d)) - {"run.lock"} == {".rbt129-done-S", "lineage.jsonl", "state.json"}  # restored whole
    assert not saves.exists()  # nothing pushed over the snapshot; its marker is receipted
    assert "cut short; restoring it again" in capsys.readouterr().err
    assert os.listdir(receipts) == [f"{stages._label(d)}.S"]  # and the sentinel is gone
    stages.run_job(job)
    _join_saves()
    assert not saves.exists()


def test_m1_a_restore_that_fails_again_refuses_and_keeps_its_sentinel(tmp_path, monkeypatch):
    _fake_durable(tmp_path, monkeypatch, "exit 1\n")
    monkeypatch.setattr(stages, "save_now", lambda *a, **k: pytest.fail("a partial directory was saved"))
    d = tmp_path / "S"
    d.mkdir()
    (d / "state.json").write_text("s")
    (d / ".rbt129-done-S").write_text("t0\n")
    os.makedirs(stages.DURABLE_DONE)
    pending = os.path.join(stages.DURABLE_DONE, f"{stages._label(str(d))}.restoring")
    with open(pending, "w") as f:
        json.dump({"existed": False, "state": False, "markers": {}}, f)
    for _ in range(2):
        with pytest.raises(SystemExit) as e:
            stages.run_job({"job": "fresh", "name": "0/x/7/S", "dir": str(d), "seed": 7})
        assert e.value.code == 7 and os.path.exists(pending)


def test_m2_a_record_whose_save_was_lost_is_saved_at_the_restart(tmp_path, monkeypatch):
    """#510 adversary M-2 (Stage 1's extinct ckpt60): unit_file's background record saves are lost with the lane while
    ckpt60's own save lands.  At the restart, the unit's first job saves the record (EXTINCT.txt in it), in the
    foreground, once; ckpt60 is not saved again."""
    monkeypatch.delenv("NO_DURABLE", raising=False)
    monkeypatch.setattr(stages, "_restore", lambda d, probe="state.json": None)
    unit = tmp_path / "stage1" / "c0-p080-U-G" / "129005"
    (unit / "S").mkdir(parents=True)
    (unit / "S" / "state.json").write_text(json.dumps({"season": 41, "populations": {"holistic": [], "conventional": []}}))
    job = {"job": "snapshot", "name": "1/c0-p080-U-G/129005/ckpt60", "src": str(unit / "S"), "dir": str(unit / "ckpt60"),
           "season": 60, "seed": 129005}
    saved, lost = [], [True]

    def save_now(d, label=None, retries=1):
        if lost[0] and os.path.basename(d) == "record":
            return 1  # killed: the record's saves never land
        saved.append((os.path.basename(d), sorted(os.listdir(d))))
        return 0
    monkeypatch.setattr(stages, "save_now", save_now)
    stages.run_job(job)
    _join_saves()
    assert saved == [("ckpt60", [".rbt129-done-ckpt60"])]
    lost[0] = False
    stages._SETTLED.discard(str(unit))  # a new process
    stages.run_job(job)
    _join_saves()
    assert saved[1:] == [("record", ["EXTINCT.txt", "UNIT.txt"])]
    stages._SETTLED.discard(str(unit))
    stages.run_job(job)  # and the next restart has nothing to save
    _join_saves()
    assert len(saved) == 2


def test_s4_check_branches_save_receipts_what_it_saved(repo_tmp, monkeypatch):
    unit = repo_tmp / "stageP" / "c0-p030-PW-G" / "129001"
    (unit / "S").mkdir(parents=True)
    (unit / "S" / ".rbt129-done-S60").write_text("t0\n")
    lane = repo_tmp / "lane.jsonl"
    lane.write_text(json.dumps({"job": "fresh", "name": "0/c0-p030-PW-G/129001/S60", "dir": stages.rel(str(unit / "S")), "seed": 129001}) + "\n")
    remote = set()
    monkeypatch.setattr(stages, "remote_ckpt", lambda: set(remote))
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: remote.add(label) or 0)
    assert stages.main(["check-branches", str(lane), "--save"]) == 0
    assert stages._receipted(str(unit / "S"), "S60", "t0\n")


def test_s3_receipts_race_safely_and_never_kill_the_lane(tmp_path, monkeypatch, capsys):
    import threading
    d = str(tmp_path / "S")
    ts = [threading.Thread(target=stages._receipt, args=(d, "S", "t0\n")) for _ in range(16)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert stages._receipted(d, "S", "t0\n") and os.listdir(stages.DURABLE_DONE) == [f"{stages._label(d)}.S"]
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "file"))
    (tmp_path / "file").write_text("")  # not a directory: the receipt cannot be written
    stages._receipt(d, "S", "t0\n")
    assert "WARN: receipt" in capsys.readouterr().err


def test_s1_receipts_live_beside_the_durable_log_under_ignored_runs(monkeypatch):
    """#510 adversary S-1: a reboot that wipes /tmp but keeps the run directories keeps the receipts too."""
    import subprocess
    monkeypatch.undo()  # this module's fixture points them at tmp_path
    assert os.path.dirname(stages.DURABLE_DONE) == os.path.dirname(stages.DURABLE_LOG) == stages.RUNS
    path = os.path.join("runs", "RBT-129", ".durable-done", "x")
    assert subprocess.run(["git", "check-ignore", "-q", path], cwd=stages.ROOT).returncode == 0


def test_n1_a_record_restore_cut_short_is_completed_not_pushed(tmp_path, monkeypatch):
    """#510 fix-check N1: a record's restore cut short (UNIT.txt copied, EXTINCT.txt not) leaves record/ present; the
    restart restores it again (its sentinel) before reading it, so the unit is extinct again and nothing partial is
    pushed over the record's branch; and a save is refused while a sentinel stands."""
    _fake_durable(tmp_path, monkeypatch, 'mkdir -p "$2"; echo u > "$2/UNIT.txt"; echo e > "$2/EXTINCT.txt"\n')
    saved = []
    monkeypatch.setattr(stages, "save_now", lambda d, label=None, retries=1: saved.append(sorted(os.listdir(d))) or 0)
    unit = tmp_path / "stage1" / "c0-p080-U-G" / "129005"
    rec = unit / "record"
    rec.mkdir(parents=True)
    (rec / "UNIT.txt").write_text("u\n")  # the part
    os.makedirs(stages.DURABLE_DONE)
    with open(stages._restoring(str(rec)), "w") as f:
        json.dump({"existed": False, "state": False, "markers": {}}, f)
    assert stages._saved(str(rec)) == 1 and saved == []  # never pushed while the sentinel stands
    stages.restore_record(str(unit))
    stages._settle_record(str(unit))
    assert sorted(os.listdir(rec)) == ["EXTINCT.txt", "UNIT.txt"] and (unit / "EXTINCT.txt").exists()
    assert not os.path.exists(stages._restoring(str(rec)))
    assert saved == []  # restored whole: its digest is receipted, nothing to push


def test_n2_a_kill_inside_a_new_jobs_fetch_does_not_wedge_the_lane(tmp_path, monkeypatch):
    """#510 fix-check N2: on a fresh host a new job's directory has no branch; a kill inside that restore's fetch left
    the sentinel, and every restart refused (exit 7).  durable.sh now exits 3 for "no such branch": nothing was ever
    unpacked, so the sentinel goes and the job runs."""
    _fake_durable(tmp_path, monkeypatch, 'echo "durable: no ckpt/$3" >&2; exit 3\n')
    d = str(tmp_path / "new" / "S")
    os.makedirs(stages.DURABLE_DONE)
    with open(stages._restoring(d), "w") as f:  # left by the kill
        json.dump({"existed": False, "state": False, "markers": {}}, f)
    for _ in range(2):
        stages._restore(d)  # no SystemExit
        assert not os.path.exists(stages._restoring(d))


def test_n2_durable_sh_exits_3_only_when_the_branch_is_absent(tmp_path, monkeypatch):
    """The real durable.sh against a local bare remote: no ckpt/LABEL is exit 3 and unpacks nothing; after a save the
    same restore exits 0."""
    import shutil
    import subprocess
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"), ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(k, v)
    bare, repo = tmp_path / "origin.git", tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", str(bare)], check=True)
    (repo / "scripts").mkdir()
    shutil.copy(os.path.join(stages.ROOT, "scripts", "durable.sh"), repo / "scripts" / "durable.sh")
    sh = str(repo / "scripts" / "durable.sh")
    r = subprocess.run([sh, "restore", "run/S", "rbt-129-t"], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 3 and "no ckpt/rbt-129-t" in r.stderr and not (repo / "run").exists()
    (repo / "run" / "S").mkdir(parents=True)
    (repo / "run" / "S" / "x.txt").write_text("x")
    assert subprocess.run([sh, "save", "run/S", "rbt-129-t"], cwd=repo, capture_output=True).returncode == 0
    shutil.rmtree(repo / "run")
    r = subprocess.run([sh, "restore", "run/S", "rbt-129-t"], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0 and (repo / "run" / "S" / "x.txt").read_text() == "x"
    monkeypatch.setenv("DURABLE_REMOTE", str(tmp_path / "missing.git"))  # an unreachable remote is not exit 3
    shutil.rmtree(repo / "run")
    r = subprocess.run([sh, "restore", "run/S", "rbt-129-t"], cwd=repo, capture_output=True, text=True)
    assert r.returncode not in (0, 3)


# -- the physics pin: runs/RBT-129/mn-crash/RULING.md item 6 ------------------------------------------------------- #

def test_the_pin_is_the_rulings_version():
    assert stages.MUJOCO_PINNED == "3.14.0"
    ruling = open(os.path.join(stages.RUNS, "mn-crash", "RULING.md")).read()
    assert "must refuse any installed MuJoCo other than 3.14.0" in " ".join(ruling.split())


@pytest.mark.parametrize("v", ["3.13.2", "3.14.1", "3.15.0", "3.14.0.post1", "3.14", "3.14.0rc1", None])
def test_any_other_mujoco_is_refused(monkeypatch, capsys, v):
    _mujoco_is(monkeypatch, v)
    with pytest.raises(SystemExit) as e:
        stages.check_mujoco()
    assert e.value.code == 9
    err = capsys.readouterr().err
    assert err.startswith("REFUSED: MuJoCo ") and (v or "(not installed)") in err and "RULING.md" in err


def test_mujoco_3_14_0_passes(monkeypatch):
    _mujoco_is(monkeypatch, "3.14.0")
    stages.check_mujoco()


X86 = pytest.mark.skipif(platform.machine() != "x86_64", reason="check_host refuses off x86_64 (exit 3) first")


@X86
def test_run_lane_and_a_legs_verify_refuse_another_mujoco_before_any_job(tmp_path, monkeypatch):
    """Every launch passes check_host: run-lane, and each emitted leg script's ``stages.py verify``.  On another MuJoCo
    both refuse with exit 9 before reading a job (this lane's only line would fail to parse)."""
    _mujoco_is(monkeypatch, "3.15.0")
    monkeypatch.setattr(stages, "run_job", lambda job: pytest.fail("a job ran"))
    lanes = _launch_dir(tmp_path)
    (lanes / "host0-lane0.jsonl").write_text("not json\n")
    with pytest.raises(SystemExit) as e:
        stages.run_lane(str(lanes / "host0-lane0.jsonl"))
    assert e.value.code == 9
    with pytest.raises(SystemExit) as e:
        stages.main(["verify", str(lanes / "launch.txt")])
    assert e.value.code == 9
    _mujoco_is(monkeypatch, "3.14.0")  # the pinned version goes on to the tree checks
    with pytest.raises(SystemExit) as e:
        stages.check_host({})
    assert e.value.code == 5


@pytest.mark.parametrize("module", ["3.3.7", "3.14.1", None])
def test_the_imported_module_must_agree_with_the_metadata(monkeypatch, capsys, module):
    """#511 adversary S3: stale dist-info, or a build on PYTHONPATH, can make importlib.metadata say 3.14.0 while
    another MuJoCo is imported.  That is refused too."""
    import mujoco
    _mujoco_is(monkeypatch, "3.14.0")
    monkeypatch.setattr(mujoco, "__version__", module)
    with pytest.raises(SystemExit) as e:
        stages.check_mujoco()
    assert e.value.code == 9 and "the mujoco module imported here" in capsys.readouterr().err


def test_the_emitters_refuse_another_mujoco_before_they_simulate_or_write(repo_tmp, fair_check, monkeypatch):
    """#511 adversary S2: a wrong MuJoCo is refused at emit time (exit 9), before the surface probe simulates on it,
    before any gate reads a run, and before a lane file is written."""
    _mujoco_is(monkeypatch, "3.3.7")
    for name in ("surface_clearance_ok", "screen_gate", "mn_plan", "plan"):
        monkeypatch.setattr(stages, name, lambda *a, _name=name, **k: pytest.fail(f"{_name} ran on the wrong MuJoCo"))
    with pytest.raises(SystemExit) as e:
        stages.check_surface_clearance(list(blocks.EAT_RULED))
    assert e.value.code == 9
    fe = ["--fair=--fair", EAT, "--root", str(repo_tmp)]
    for argv in (["emit", "P", *fe], ["screen-emit", *fe], ["stage1-emit", *fe], ["fork-source-emit", *fe],
                 ["mn-emit", *fe], ["prelaunch", *fe], ["pays-prize", *fe]):
        with pytest.raises(SystemExit) as e:
            stages.main(argv)
        assert e.value.code == 9, argv
    assert not (repo_tmp / "lanes").exists()

