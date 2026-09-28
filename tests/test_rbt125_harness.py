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
                out.append(((h, w, speed), seed, f_, f_ - 0.1, 0.3 * (1.25 if speed else 1.0), False))
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


# --- --exclude-exploded (the coordinator's ruling on RBT-129 #467, after the legs readout adversary #473 §3) ----------

class _NoisyPool(_Pool):
    """A fake pool with noisy items and paths, no explosions: the fixture the flag-off digest was recorded on."""

    def map(self, f, tasks, chunksize=1):
        rng = np.random.default_rng(0)
        out = []
        for t in tasks:
            if isinstance(t[0], str):
                out.append((t[2], t[4], 0.0, -1.0, 10))
                continue
            h, w, sign, seed, speed = t
            f_ = float(rng.poisson(1 + 0.05 * w + (0.3 if speed else 0)))
            out.append(((h, w, speed), seed, f_, f_ - 0.1, 0.3 * (1.25 if speed else 1.0) * (1 + 0.1 * rng.standard_normal()), False))
        return out


#: sha256 of the stdout (tmp dir masked) of the fixture below, recorded on steps.py BEFORE --exclude-exploded existed
#: (integration b71c994d, whose bout returned five fields): flag off must reproduce it byte for byte
PRE_FLAG_DIGEST = "3bc4d0fbdf89416c7fee8a48329ee119a9d5f48dabf3f784755fc0cab02a63f7"


def test_flag_off_is_byte_identical_to_the_pre_flag_readout(tmp_path, capsys, fair_module):
    import hashlib
    m = _steps()
    paths = [_pioneer(str(tmp_path / f"h{i}.json")) for i in range(6)]
    hosts = tmp_path / "hosts.txt"
    hosts.write_text("\n".join(paths) + "\n")
    cfg = json.load(open(os.path.join(GATE, "worlds", "PW-G2.5", "config.json")))
    cfg["fairness"] = "fair"
    cp = tmp_path / "c.json"
    cp.write_text(json.dumps(cfg))
    m.get_context = lambda kind: type("Ctx", (), {"Pool": _NoisyPool})
    sys.argv = ["steps.py", str(tmp_path), "FIX", "--config", str(cp), "--hosts-file", str(hosts), "--seeds", "32"]
    m.main()
    out = capsys.readouterr().out.replace(str(tmp_path), "<TMP>")
    assert hashlib.sha256(out.encode()).hexdigest() == PRE_FLAG_DIGEST


def _synthetic(m, n_hosts=3, n_seeds=8, explode=(), speed_ratio=None, spike=None):
    """got / blew for a clean world: base items 1.0 + a per-seed effect shared by every arm (0.3 x seed, so dropping a
    seed from one arm only biases a step), a nose step +0.5 (w -> w + 0.4), speed +0.2 items at path x 1.25 (r = 1.25).  An exploded season (host, w, speed, seed) books 0 items, 0 net and a 1e4 m/s path, as a
    blow-up does (food forfeited, path summed through the explosion)."""
    m.SEEDS[:] = list(range(n_seeds))
    m.HOST.clear()
    m.HOST.update({h: f"/hosts/h{h}.json" for h in range(n_hosts)})
    got, blew = {}, {}
    for h in range(n_hosts):
        for w in m.WS:
            for sp in ((False, True) if w in m.SPEED_WS else (False,)):
                for s in m.SEEDS:
                    base_w = w - 0.4 if round(w % 1, 1) == 0.4 else w
                    items = 1.0 + 0.3 * s + (0.5 if base_w != w else 0.0) + (0.2 if sp else 0.0)
                    path = 0.3 * ((speed_ratio or {}).get(h, 1.25) if sp else 1.0)
                    path = (spike or {}).get((h, w, sp, s), path)
                    x = (h, w, sp, s) in explode
                    got[((h, w, sp), s)] = (0.0, 0.0, 1e4) if x else (items, items - 0.1, path)
                    blew[((h, w, sp), s)] = x
    import types
    return types.SimpleNamespace(hosts_root="/hosts", cell="SYN"), {h: 1.0 for h in range(n_hosts)}, got, blew


def _paired(m, capsys, **kw):
    a, sign, got, blew = _synthetic(m, **kw)
    m.paired_readout(a, sign, got, blew)
    return capsys.readouterr().out


def _step_line(out, label):
    return next(ln for ln in out.splitlines() if ln.startswith("STEP") and label in ln)


def test_an_exploded_season_in_each_arm_is_dropped_from_both(capsys):
    """One explosion in the speed arm (host 0), one in the base arm w3 (host 1), one in the nose arm w3.4 (host 2): with
    the pairing, every host reads the clean world exactly -- r 1.25, speed step +0.2, nose step +0.5, per-unit nose -
    speed +0.3 -- and the explosions are counted per arm."""
    m = _steps()
    out = _paired(m, capsys, explode={(0, 3.0, True, 7), (1, 3.0, False, 1), (2, 3.4, False, 6)})
    assert "r 1.250 [1.250, 1.250], range 1.25..1.25; 3 of 3 hosts" in out
    assert "| nose step w 3 -> 3.4 | 3 (0 out) | +0.500 [+0.500, +0.500]" in out
    assert "| speed step at w3 (raw) | 3 (0 out) | +0.200 [+0.200, +0.200]" in out
    assert "(n 3; 0 out for > 25% exploded): +0.300 [+0.300, +0.300] NOSE LEADS" in _step_line(out, "w 3 -> 3.4")
    assert "exploded seasons per arm, all hosts: w0 0, w0.4 0, w1 0, w1.4 0, w3 1, w3.4 1, speed@w0 0, speed@w1 0, speed@w3 1" in out


def test_without_the_pairing_the_same_seasons_poison_r(capsys):
    """The contamination the flag removes: the registered (flag-off) path over the same got gives r in the hundreds."""
    m = _steps()
    a, sign, got, blew = _synthetic(m, explode={(0, 3.0, True, 0)})
    paths_speed = np.array([got[((0, 3.0, True), s)][2] for s in m.SEEDS])
    paths_base = np.array([got[((0, 3.0, False), s)][2] for s in m.SEEDS])
    assert paths_speed.mean() / paths_base.mean() > 100


@pytest.mark.parametrize("n_exploded,out_of_line", [(2, False), (3, True)])
def test_a_host_over_25_percent_exploded_leaves_the_line(capsys, n_exploded, out_of_line):
    """8 paired seeds: 2 exploded (25%) stays in; 3 (37.5%) leaves the w3 line and is counted."""
    m = _steps()
    out = _paired(m, capsys, explode={(2, 3.0, True, s) for s in range(n_exploded)})
    line = _step_line(out, "w 3 -> 3.4")
    if out_of_line:
        assert "(n 2; 1 out for > 25% exploded)" in line and "vs raw speed@w3 (descriptive, n 2)" in line
    else:
        assert "(n 3; 0 out for > 25% exploded)" in line
    assert "(n 3; 0 out" in _step_line(out, "w 1 -> 1.4")  # the other lines keep the host


def test_fewer_than_two_hosts_is_not_readable(capsys):
    m = _steps()
    out = _paired(m, capsys, n_hosts=2, explode={(1, 3.0, True, s) for s in range(4)})
    assert _step_line(out, "w 3 -> 3.4").endswith("NOT READABLE")


class _ExplodingPool(_NoisyPool):
    """_NoisyPool with host 0's speed@w3 arm exploding on its first two seeds (a 5e4 m/s path, food forfeited)."""

    def map(self, f, tasks, chunksize=1):
        out = super().map(f, tasks, chunksize)
        for i, row in enumerate(out):
            if len(row) == 6 and row[0] == (0, 3.0, True) and row[1] in m_seeds[:2]:
                out[i] = (row[0], row[1], 0.0, 0.0, 5e4, True)
        return out


m_seeds = []


def test_the_flag_reaches_the_readout_end_to_end(tmp_path, capsys, fair_module):
    """main() with --exclude-exploded prints the paired readout (header, per-arm counts, r free of the blow-up); without
    the flag the same run prints the registered readout, where host 0's r@w3 is in the thousands."""
    m = _steps()
    paths = [_pioneer(str(tmp_path / f"h{i}.json")) for i in range(4)]
    hosts = tmp_path / "hosts.txt"
    hosts.write_text("\n".join(paths) + "\n")
    cfg = json.load(open(os.path.join(GATE, "worlds", "PW-G2.5", "config.json")))
    cfg["fairness"] = "fair"
    cp = tmp_path / "c.json"
    cp.write_text(json.dumps(cfg))
    m.get_context = lambda kind: type("Ctx", (), {"Pool": _ExplodingPool})
    m_seeds[:] = list(range(900, 916))
    base = [str(tmp_path), "FIX", "--config", str(cp), "--hosts-file", str(hosts), "--seeds", "16", "--seed0", "900"]
    sys.argv = ["steps.py"] + base
    m.main()
    off = capsys.readouterr().out
    host0 = next(ln for ln in off.splitlines() if ln.startswith("| h0.json"))
    assert float(host0.split("|")[-2]) > 1000  # r@w3 poisoned by the blow-up
    sys.argv = ["steps.py"] + base + ["--exclude-exploded"]
    m.main()
    on = capsys.readouterr().out
    assert "# --exclude-exploded:" in on and "speed@w3 2" in on
    host0 = next(ln for ln in on.splitlines() if ln.startswith("| h0.json"))
    assert float(host0.split("|")[-3]) < 2  # r@w3 over the 14 clean paired seeds
    assert on.count("STEP FIX |") == 3


def test_the_r_below_1_10_exclusion_is_kept_under_the_flag(capsys):
    """A host whose clean speed arm realises only +5% (r 1.05) still leaves the per-unit comparison (A1.4 unchanged)."""
    m = _steps()
    out = _paired(m, capsys, speed_ratio={2: 1.05}, explode={(0, 3.0, True, 3)})
    assert "2 of 3 hosts at r >= 1.10 enter the per-unit comparison" in out
    assert "(n 2; 0 out for > 25% exploded)" in _step_line(out, "w 3 -> 3.4")


def _r_row(out, host, w):
    row = next(ln for ln in out.splitlines() if ln.startswith(f"| h{host}.json | {w:g} |"))
    return [c.strip() for c in row.split("|")[3:7]]


def test_r_is_the_ratio_of_medians_so_one_sub_threshold_spike_cannot_carry_it(capsys):
    """Host 0's speed@w3 arm has one season that did not explode but ran at 3.8 m/s (the #473 host 1/016 case; the
    rest run 0.375): the ratio of means is carried to 2.68, the median r stays 1.25 and the per-unit line reads the
    clean world.  Host 2 realises only r 1.05, and one 1.2 m/s spike lifts its mean r over 1.10: it is listed as
    crossing, and stays out of the per-unit comparison."""
    m = _steps()
    out = _paired(m, capsys, speed_ratio={2: 1.05}, spike={(0, 3.0, True, 5): 3.8, (2, 3.0, True, 5): 1.2})
    assert _r_row(out, 0, 3.0) == ["1.250", "2.677", "3.800", "0.300"]
    assert _r_row(out, 2, 3.0)[:2] == ["1.050", "1.419"]
    assert "at w3: mean and median r on opposite sides of 1.10: h2.json" in out
    assert "at w1: mean and median r on opposite sides of 1.10: none" in out
    assert "2 of 3 hosts at r >= 1.10 enter the per-unit comparison" in out
    assert "(n 2; 0 out for > 25% exploded): +0.300 [+0.300, +0.300] NOSE LEADS" in _step_line(out, "w 3 -> 3.4")
    host0 = next(ln for ln in out.splitlines() if ln.startswith("| h0.json |") and ln.count("|") > 8)
    assert host0.split("|")[-3].strip() == "1.250"  # the per-host table's r is the median r too


def test_r_is_a_ratio_of_medians_not_a_median_of_per_seed_ratios(capsys):
    """Base paths 1..8 and speed paths 1.25 x (8, 1, 2, .., 7): the medians give r 1.25; the per-seed ratios' median
    (1.02) does not."""
    m = _steps()
    a, sign, got, blew = _synthetic(m)
    for s in m.SEEDS:
        for h in sign:
            k0, k1 = ((h, 3.0, False), s), ((h, 3.0, True), s)
            got[k0] = got[k0][:2] + (1.0 + s,)
            got[k1] = got[k1][:2] + (1.25 * (8 if s == 0 else s),)
    m.paired_readout(a, sign, got, blew)
    out = capsys.readouterr().out
    ratios = [1.25 * (8 if s == 0 else s) / (1.0 + s) for s in m.SEEDS]
    assert abs(np.median(ratios) - 1.25) > 0.2
    assert _r_row(out, 0, 3.0) == ["1.250", "1.250", "10.000", "8.000"]


def test_the_per_host_table_is_labelled_unpaired(capsys):
    m = _steps()
    out = _paired(m, capsys)
    lines = out.splitlines()
    i = lines.index("per-host table (unpaired): items per arm over its own non-exploded seeds; lines use per-comparison "
                    "pairs; r is the paired median r")
    assert lines[i + 2].startswith("| host | w0 |")


def test_a_one_host_summary_prints_dashes_not_nan(capsys):
    """Host 1 leaves the w3 lines (> 25% exploded): each w3 summary is over one host and prints `--`, never nan."""
    m = _steps()
    out = _paired(m, capsys, n_hosts=2, explode={(1, 3.0, True, s) for s in range(4)})
    assert "nan" not in out
    assert "| speed step at w3 (raw) | 1 (1 out) | +0.200 -- | +0.200 -- |" in out
    assert "r 1.250 --, range 1.25..1.25; 1 of 1 hosts" in out
    assert "per-unit speed step (+25% realised) +0.200 --" in out


def test_the_median_r_is_taken_over_the_paired_seeds_only(capsys):
    """Paths vary by seed (base 1 + s, speed 1.25 x (1 + s)) and host 0's speed@w3 arm explodes on seeds 0 and 1 (25%,
    so the host stays in): over the 6 paired seeds r is 1.25; over every seed the median would be 1.81 (the base arm
    keeps its two slow seasons, the speed arm's blow-ups sit at the top)."""
    m = _steps()
    a, sign, got, blew = _synthetic(m, explode={(0, 3.0, True, 0), (0, 3.0, True, 1)})
    for s in m.SEEDS:
        k0, k1 = ((0, 3.0, False), s), ((0, 3.0, True), s)
        got[k0] = got[k0][:2] + (1.0 + s,)
        if not blew[k1]:
            got[k1] = got[k1][:2] + (1.25 * (1.0 + s),)
    m.paired_readout(a, sign, got, blew)
    out = capsys.readouterr().out
    assert _r_row(out, 0, 3.0) == ["1.250", "1.250", "10.000", "8.000"]
    assert "at w3: 0 host(s) out for > 25% exploded; r 1.250 [1.250, 1.250]" in out
