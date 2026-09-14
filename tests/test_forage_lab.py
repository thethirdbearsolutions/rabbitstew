"""The forage-shaped champion lab (RBT-28), and the instrument it reads items per metre against.

`scripts/` is not a package, so the module is loaded by path the way a reader would run it.
"""

import importlib.util
import json
import pathlib

import numpy as np
import pytest

from rabbitstew.fixed import drive_straight_genotype
from rabbitstew.simulation import FoodConfig, SimConfig

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load():
    spec = importlib.util.spec_from_file_location("forage_lab", ROOT / "scripts" / "forage_lab.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_dir(tmp_path, food=True, duration=4.0):
    cfg = SimConfig(duration=duration, random_start=True, score="food",
                    food=FoodConfig(items=12, radius=3.0, eat_radius=0.35, regrow=True, clearance=0.8)
                    if food else None)
    (tmp_path / "holistic").mkdir()
    (tmp_path / "config.json").write_text(json.dumps({"sim": cfg.to_dict()}))
    drive_straight_genotype(0.6).save(str(tmp_path / "holistic" / "best_gen0001.json"))
    return tmp_path


def test_it_refuses_a_run_that_has_no_food(tmp_path):
    """Run on a locomotion champion it would print foraging columns for a task it was never in;
    the point of the sibling script is that it says so instead."""
    mod = _load()
    with pytest.raises(SystemExit):
        mod.load(str(_run_dir(tmp_path, food=False)), "holistic", 1)


def test_the_path_is_measured_every_tick_not_every_tenth(tmp_path):
    """RBT-39: sampling the path coarsely understates it and so OVERSTATES items per metre. The
    inherited script sampled every tenth control tick; this pins the fix by comparing against a
    deliberately coarse re-measurement of the same bout."""
    mod = _load()
    g, cfg = mod.load(str(_run_dir(tmp_path)), "holistic", 1)
    from rabbitstew.simulation import Simulation, spawn_layout
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, 8000))
    sim.set_food_seed(8000)
    steps = int(round(cfg.duration / cfg.control_dt))
    pts = []
    for _ in range(steps):
        sim.step()
        pts.append(sim.center_of_mass(0)[:2].copy())
    pts = np.array(pts)
    fine = float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())
    coarse = float(np.linalg.norm(np.diff(pts[::10], axis=0), axis=1).sum())
    assert coarse < fine                                  # the old sampling loses path
    row = mod.trial(g, cfg, mod.synthesize(g, cfg.synthesis),
                    mod.groups(mod.synthesize(g, cfg.synthesis)), 8000, "intact")
    assert row["path"] == pytest.approx(fine, rel=1e-6)   # the script uses the fine one


def test_a_blind_mower_reads_as_its_own_gait_and_the_null_is_populated(tmp_path):
    """The verdict instrument is the trajectory null, not the point-robot floor. A robot that
    drives in a straight line with no wiring from any sensor cannot be steering, so it must not
    read above its own gait's expectation."""
    mod = _load()
    g, cfg = mod.load(str(_run_dir(tmp_path)), "holistic", 1)
    ph = mod.synthesize(g, cfg.synthesis)
    gs = mod.groups(ph)
    rows = [mod.trial(g, cfg, ph, gs, 8000 + s, "intact", draws=40) for s in range(6)]
    assert all(np.isfinite(r["null"]) for r in rows)
    assert all(r["swept"] > 2 * cfg.food.eat_radius for r in rows)   # a real body, not a point
    d = np.array([r["food"] - r["null"] for r in rows])
    t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
    assert abs(t) < 2.5, f"a blind straight-line mower read t={t:+.2f} against its own gait"


def test_blanking_a_sensor_the_robot_does_not_have_changes_nothing(tmp_path):
    """The inert-nose question this ticket exists for: no_smell on a body with no smell sensor must
    be bit-identical to intact, so a non-zero difference anywhere is a real effect and not drift."""
    mod = _load()
    g, cfg = mod.load(str(_run_dir(tmp_path)), "holistic", 1)
    ph = mod.synthesize(g, cfg.synthesis)
    gs = mod.groups(ph)
    assert gs["smell"] == []                                        # the fixture has no nose
    for seed in (8000, 8001):
        a = mod.trial(g, cfg, ph, gs, seed, "intact")
        b = mod.trial(g, cfg, ph, gs, seed, "no_smell")
        assert a["food"] == b["food"] and a["path"] == pytest.approx(b["path"], rel=1e-12)


def test_it_reports_the_effect_size_its_sample_size_can_resolve(capsys):
    """RBT-28's adversary: a lesion table read at an n too small to reject anything is a design that
    cannot fail, which is worse than a wrong number because it looks like a measurement. So the
    script must say what its own n resolves, and say plainly when that is not enough."""
    mod = _load()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        run = _run_dir(pathlib.Path(tmp))
        mod.main(["forage_lab.py", str(run), "holistic", "1", "4", "10"])
    out = capsys.readouterr().out
    assert "power at n = 4 draws" in out
    assert "resolves a lesion difference of" in out
    assert "needs about" in out
    # four draws cannot resolve a quarter of this fixture's yield, and it must say so
    assert "CANNOT TEST a 25% effect" in out
