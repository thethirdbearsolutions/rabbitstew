"""RBT-125 §B's nose-step harness (runs/RBT-125/gate/steps.py), as reused by the RBT-129 sweep: the registered defaults
are untouched, and --config / --hosts-file / --seeds / --seed0 reach the run.  The simulation is replaced by a fake
pool, so nothing here runs physics: it checks the plumbing and the readout, not a result."""
import importlib.util
import json
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "runs", "RBT-125", "gate")


def _steps():
    sys.path.insert(0, GATE)
    spec = importlib.util.spec_from_file_location("rbt125_steps_under_test", os.path.join(GATE, "steps.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class _Pool:
    seen = []

    def __init__(self, *a):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def map(self, f, tasks, chunksize=1):
        rng = np.random.default_rng(0)
        out = []
        for t in tasks:
            if isinstance(t[0], str):  # a direction bout: (run, kind, host, i, probe) -> always "forward"
                out.append((t[2], t[4], 0.0, -1.0, 10))
            else:
                h, w, sign, seed, speed = t
                _Pool.seen.append(seed)
                f_ = float(rng.poisson(1 + 0.05 * w + (0.3 if speed else 0)))
                out.append(((h, w, speed), seed, f_, f_ - 0.1, 0.3 * (1.25 if speed else 1.0)))
        return out


def _run(m, argv, capsys):
    _Pool.seen = []
    m.get_context = lambda kind: type("Ctx", (), {"Pool": _Pool})
    sys.argv = ["steps.py"] + argv
    m.main()
    return capsys.readouterr().out


@pytest.fixture
def fair_module(monkeypatch):
    """rabbitstew.fair (RBT-128, #432) as steps.py uses it: the real module when this tree has it, else a stand-in with
    the same is_designed rule (the Pioneer's or the quadruped's body plan)."""
    try:
        import rabbitstew.fair as fair  # noqa: F401
        return fair
    except ImportError:
        import types
        from rabbitstew.fixed import pioneer_genotype, quadruped_genotype
        from rabbitstew.genetics import body_plan
        plans = {body_plan(pioneer_genotype()), body_plan(quadruped_genotype())}
        mod = types.SimpleNamespace(is_designed=lambda g: body_plan(g) in plans)
        monkeypatch.setitem(sys.modules, "rabbitstew.fair", mod)
        return mod


def _fair_config(tmp_path, fairness="fair"):
    d = json.load(open(os.path.join(GATE, "worlds", "PW-G2.5", "config.json")))
    if fairness is not None:
        d["fairness"] = fairness
    p = tmp_path / f"config-{fairness}.json"
    p.write_text(json.dumps(d))
    return str(p)


def _pioneer(path):
    from rabbitstew.fixed import pioneer_genotype
    g = pioneer_genotype(np.random.default_rng(1), sources=("food", "contact"), rich=True)  # the evolved layout: (effector, joint_velocity, food)
    open(path, "w").write(json.dumps(g.to_dict()))
    return path


def test_the_registered_defaults_are_unchanged():
    m = _steps()
    assert m.SEEDS == [125000 + i for i in range(128)]
    assert m.SPEED_WS == (0.0, 1.0, 3.0) and m.R_MIN == 1.10 and m.DELTA == 0.10


def test_config_hosts_file_and_seeds_reach_the_run(tmp_path, capsys, fair_module):
    m = _steps()
    hosts = tmp_path / "hosts.txt"
    hosts.write_text("\n".join(_pioneer(str(tmp_path / f"h{i}.json")) for i in range(3)) + "\n")
    cfg = _fair_config(tmp_path)
    out = _run(m, [str(tmp_path), "STAGE0", "--config", cfg, "--hosts-file", str(hosts), "--seeds", "4", "--seed0", "900"], capsys)
    assert "world from " + cfg in out and "# fairness: 'fair'" in out
    assert "# hosts: 3 from " in out
    assert sorted(set(_Pool.seen)) == [900, 901, 902, 903]
    assert out.count("STEP STAGE0 |") == 3


@pytest.mark.parametrize("fairness", [None, "unfair"])
def test_s12_a_config_not_built_fair_is_refused(tmp_path, capsys, fairness):
    m = _steps()
    with pytest.raises(SystemExit, match="not 'fair'"):
        _run(m, [str(tmp_path), "X", "--config", _fair_config(tmp_path, fairness), "--seeds", "2"], capsys)


def test_s13_a_pioneer_brain_on_a_reshaped_body_is_refused(tmp_path, capsys, fair_module):
    """The motif check alone accepts it (the wheels' brain layout is intact); is_designed rejects the reshaped chassis."""
    from rabbitstew.fixed import pioneer_genotype
    m = _steps()
    g = pioneer_genotype(np.random.default_rng(1), sources=("food", "contact"), rich=True)
    g.nodes[0].segment.dims = (0.6, 0.38, 0.2)  # a longer chassis
    m.rp.routed.unit_indices(g)  # accepted by the motif check
    bad = tmp_path / "reshaped.json"
    bad.write_text(json.dumps(g.to_dict()))
    hosts = tmp_path / "hosts.txt"
    hosts.write_text(str(bad) + "\n")
    with pytest.raises(SystemExit, match="not a designed body"):
        _run(m, [str(tmp_path), "X", "--config", _fair_config(tmp_path), "--hosts-file", str(hosts), "--seeds", "2"], capsys)


def test_s13_without_rabbitstew_fair_the_hosts_file_is_refused(tmp_path, capsys, monkeypatch):
    monkeypatch.setitem(sys.modules, "rabbitstew.fair", None)  # import fails, as on a tree without #432
    m = _steps()
    hosts = tmp_path / "hosts.txt"
    hosts.write_text(_pioneer(str(tmp_path / "h.json")) + "\n")
    with pytest.raises(SystemExit, match="needs rabbitstew.fair"):
        _run(m, [str(tmp_path), "X", "--config", _fair_config(tmp_path), "--hosts-file", str(hosts), "--seeds", "2"], capsys)


def test_a_host_that_cannot_carry_the_motif_is_refused(tmp_path, capsys, fair_module):
    from rabbitstew.genotype import random_genotype
    m = _steps()
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(random_genotype(np.random.default_rng(3)).to_dict()))
    hosts = tmp_path / "hosts.txt"
    hosts.write_text(str(bad) + "\n")
    with pytest.raises(Exception):
        _run(m, [str(tmp_path), "X", "--config", _fair_config(tmp_path), "--hosts-file", str(hosts), "--seeds", "2"], capsys)


# the readout is scipy-free (the coordinator's trial merge on #437 ran in a plain `.[dev]` venv)
SCIPY_T = {  # scipy.stats.t.ppf(q, df), recorded with scipy 1.17.1
    (0.975, 1): 12.706204736174694, (0.95, 1): 6.313751514675037, (0.975, 2): 4.302652729749462, (0.95, 2): 2.9199855803537242,
    (0.975, 5): 2.5705818356363146, (0.95, 5): 2.0150483733330233, (0.975, 9): 2.262157162798205, (0.95, 9): 1.833112932656237,
    (0.975, 14): 2.144786687917804, (0.95, 14): 1.761310135774891, (0.975, 30): 2.0422724563012378, (0.95, 30): 1.697260886593957,
    (0.975, 127): 1.9788195347028539, (0.95, 127): 1.6569403435420642,
}


def test_the_t_quantile_needs_no_scipy_and_matches_it():
    m = _steps()
    src = open(os.path.join(GATE, "steps.py")).read()
    assert "import scipy" not in src and "from scipy" not in src
    for (q, df), want in SCIPY_T.items():
        assert m.t_ppf(q, df) == pytest.approx(want, abs=1e-9)
        assert m.t_ppf(1 - q, df) == pytest.approx(-want, abs=1e-9)


def test_the_t_quantile_matches_scipy_everywhere():
    stats = pytest.importorskip("scipy.stats")
    m = _steps()
    for df in range(1, 301):
        for q in (0.9, 0.95, 0.975, 0.99):
            assert abs(m.t_ppf(q, df) - stats.t.ppf(q, df)) < 1e-9
