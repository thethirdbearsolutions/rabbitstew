"""scripts/regime.py (RBT-126) on a hand-built lineage whose every figure is worked out below, and on the replica."""
import importlib.util
import json
import pathlib

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


regime = _load("regime", ROOT / "scripts" / "regime.py")


def _row(g, name, age, evals, fitness, energy, parents=(), **extra):
    r = {"generation": g, "population": "holistic", "name": name, "parents": list(parents), "fitness": fitness,
         "energy": energy, "age": age, "evals": evals, "last_score": 0.0}
    r.update(extra)
    return r


def _synthetic(tmp_path):
    """Living cost 0.25, threshold 3, birth cost 1, max age 4, seasons 0-9.

    F1 (founder) breeds C1 at season 0 (energy 4.5 -> 3.5) and C2 at season 2 (4.1 -> 3.1); dies of age at 4.
    F2 (founder) never eligible; dies of age at 4.  F3 (founder) lives to the end, never eligible (censored).
    C1: born 0, lifetime mean 0.05, starves at season 2.  C2: born 2, lifetime mean 0.75, eligible once (season 5),
    dies of age at 6."""
    rows = []
    for s in range(10):
        rows.append(_row(s, "F3", 1 + s, 1 + s, 0.25, 2.0))
    rows += [_row(0, "F1", 1, 1, 1.5, 3.5, last_score=1.5), _row(0, "F2", 1, 1, 0.1, 1.0),
             _row(0, "C1", 0, 0, 0.0, 1.0, ["F1"]),
             _row(1, "F1", 2, 2, 1.0, 4.0, last_score=0.5), _row(1, "F2", 2, 2, 0.1, 0.9), _row(1, "C1", 1, 1, 0.05, 0.8),
             _row(2, "F1", 3, 3, 1.0, 3.1, last_score=1.0), _row(2, "F2", 3, 3, 0.1, 0.8),
             _row(2, "C2", 0, 0, 0.0, 1.0, ["F1", "F3"]),
             _row(3, "F1", 3, 3, 1.0, 3.1, last_score=1.0), _row(3, "F2", 3, 3, 0.1, 0.7), _row(3, "C2", 1, 1, 0.75, 1.5),
             _row(4, "C2", 2, 2, 0.75, 2.0), _row(5, "C2", 3, 3, 0.75, 3.0, last_score=1.0)]
    # F1 and F2's season-3 rows repeat age 3 (a founder's age is its staggered start + evals); both die at season 4
    rows.sort(key=lambda r: r["generation"])
    with open(tmp_path / "lineage.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(tmp_path / "config.json", "w") as f:
        json.dump({"ecology": {"living_cost": 0.25, "birth_threshold": 3.0, "birth_cost": 1.0, "max_age": 4,
                               "starvation": True}}, f)
    return tmp_path


def test_synthetic_every_figure(tmp_path):
    res = regime.regime(str(_synthetic(tmp_path)), windows=((0, 9),))
    assert res["last_season"] == 9 and res["source"] == "lineage.jsonl"
    (w,) = res["fauna"]["holistic"]
    assert w["births"] == 2 and w["complete_lives"] == 2 and w["censored_lives"] == 0
    # solvent = C2 only (ever eligible): (0.75 - 0.25) / 0.25
    assert w["saturation"] == pytest.approx(2.0)
    assert w["solvent_share"] == pytest.approx(0.5)
    # per birth: mean(0.05, 0.75) - 0.25 = 0.15 -> 0.6 x cost
    assert w["net_per_birth"] == pytest.approx(0.15)
    assert w["viability"] == pytest.approx(0.6)
    # deaths in 0-9: C1 starved (2), F1 and F2 of age (4), C2 of age (6); F3 censored
    assert w["deaths"] == 4
    assert w["death_share"]["age"] == pytest.approx(0.75)
    assert w["death_share"]["starvation"] == pytest.approx(0.25)
    assert w["death_share"]["cull"] == 0
    # eligible before births: s0 F1 (3.5 + 1), s1 F1, s2 F1 (3.1 + 1), s3 F1, s5 C2 -> 5 over 10 seasons
    assert w["eligible_breeders"] == pytest.approx(0.5)
    # window-local: the season gains of the eligible member-seasons, 1.5, 0.5, 1.0, 1.0 (F1) and 1.0 (C2): (1.0 - 0.25) / 0.25
    assert w["saturation_local"] == pytest.approx(3.0)
    assert w["distinct_parents"] == 1
    assert w["parent_age"] == pytest.approx(2.0)  # F1 at ages 1 and 3
    # the quintiles hold both lives, and neither had children
    assert sum(q["n"] for q in w["quintiles"] if q) == 2
    assert all(q["children"] == 0 for q in w["quintiles"] if q)


def test_windows_split_lives_by_birth_and_deaths_by_death_season(tmp_path):
    res = regime.regime(str(_synthetic(tmp_path)), windows=((0, 1), (2, 9)))
    w0, w1 = res["fauna"]["holistic"]
    assert (w0["births"], w1["births"]) == (1, 1)
    assert w0["saturation"] is None  # C1 was never eligible
    assert w1["saturation"] == pytest.approx(2.0)
    assert w0["deaths"] == 0 and w1["deaths"] == 4


def test_parent_counts_children_through_parents0_only(tmp_path):
    d = _synthetic(tmp_path)
    pops, last, has_energy = regime.read_lineage(str(d))
    lives = pops["holistic"]["lives"]
    assert lives["F1"].kids == 2 and lives["F3"].kids == 0  # F3 is C2's crossover mate, not its breeder
    assert lives["C2"].depth == 1 and lives["F1"].depth == 0


def test_cull_rows_are_deaths_by_cull_not_living(tmp_path):
    d = _synthetic(tmp_path)
    with open(d / "lineage.jsonl", "a") as f:
        f.write(json.dumps(_row(9, "F3", 10, 10, 0.25, 2.0, death="cull")) + "\n")
    # F3's cull row at 9 (the last season) makes its life complete; it is a founder, so only the deaths count
    pops, last, _ = regime.read_lineage(str(d))
    assert pops["holistic"]["lives"]["F3"].culled


def test_lineage_last_fallback(tmp_path):
    head = "population\tname\tgeneration\tage\tevals\tfitness\tparents\n"
    body = ["holistic\tF1\t3\t3\t4\t1.0\t", "holistic\tC1\t1\t1\t1\t0.05\tF1", "holistic\tC2\t5\t3\t3\t0.75\tF1,F3",
            "holistic\tF3\t9\t10\t10\t0.25\t"]
    (tmp_path / "lineage-last.txt").write_text(head + "\n".join(body) + "\n")
    (tmp_path / "config.json").write_text(json.dumps({"ecology": {"living_cost": 0.25, "max_age": 4}}))
    res = regime.regime(str(tmp_path), windows=((0, 9),), min_life=2)
    (w,) = res["fauna"]["holistic"]
    assert res["source"] == "lineage-last.txt"
    assert w["complete_lives"] == 2
    assert w["saturation"] == pytest.approx(2.0)  # solvent = lived >= 2 seasons: C2
    assert "eligible_breeders" not in w


def test_replica_income_orders_the_regime(tmp_path):
    """On the replica (runs/RBT-126/breeding_rules.py), a richer world reads as more saturated, and a sub-cost one as
    non-viable; the replica's per-birth net income tracks g0 - work - cost."""
    br = _load("breeding_rules", ROOT / "runs" / "RBT-126" / "breeding_rules.py")
    sat = {}
    for g0 in (0.5, 1.3):
        d = tmp_path / f"g{g0}"
        br.write_lineage(str(d), g0, seasons=300, seed=3)
        (w,) = regime.regime(str(d), windows=((100, 250),))["fauna"]["replica"]
        sat[g0] = w
        assert w["complete_lives"] > 50
    assert sat[1.3]["saturation"] > 2.0 > sat[0.5]["saturation"]
    assert sat[1.3]["saturation_local"] > 2.0 > sat[0.5]["saturation_local"]
    # the eligible's season gain is the resident's: (g0 - work - cost) / cost, within noise
    assert sat[1.3]["saturation_local"] == pytest.approx((1.3 - 0.1 - 0.25) / 0.25, abs=0.3)
    assert sat[1.3]["death_share"]["age"] > sat[0.5]["death_share"]["age"]
    assert sat[1.3]["net_per_birth"] == pytest.approx(1.3 - 0.1 - 0.25, abs=0.15)
