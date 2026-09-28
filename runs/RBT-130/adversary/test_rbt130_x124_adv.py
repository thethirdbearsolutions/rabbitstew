"""RBT-130 adversary: every strip composed on a trial merge of #424 @ 424b82a with #420 @ 5c959ba.

Not collected from here (it needs #420's fields).  To run: merge #420 into #424 (two additive conflicts, keep both
sides), copy this file into tests/, and run  python -m pytest tests/test_rbt130_x124_adv.py."""
import json, math
import pytest
from rabbitstew.ecology import NULL_B, Ecology
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC
from test_ecology_switches import _breeding_eco, _evo


def evo():
    e = _evo(11, 1.5)
    e.sim.world.motor_budget = 1.77
    e.sim.world.ball_cone, e.sim.world.hinge_range = math.pi / 2, math.pi / 2
    e.mutation.effector_bias_sigma = 0.0
    e.sim.settle_until_rest, e.sim.settle_max = 0.01, 10.0
    e.sim.food.smell_contrast, e.sim.food.eat_from = 2.5, "root"
    e.sim.world.random_radius = 3.6
    return e


@pytest.mark.parametrize("kind", [HOLISTIC, CONVENTIONAL])
def test_all_strips_with_rbt124_merge_null_resume(tmp_path, kind):
    eco = dict(merge_after=3, merge_null=kind, sweep_log=True, breed_rule="leakx:0.3")
    whole, part = tmp_path / "whole", tmp_path / "part"
    with pytest.warns(UserWarning):
        Ecology(evo(), _breeding_eco(seasons=6, **eco), out_dir=str(whole), log=None).run()
    with pytest.warns(UserWarning):
        Ecology(evo(), _breeding_eco(seasons=4, **eco), out_dir=str(part), log=None).run()
    with pytest.warns(UserWarning):
        Ecology.resume(str(part), seasons=6, log=None).run()
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json"):
        assert (part / name).read_bytes() == (whole / name).read_bytes(), name
    cfg = json.loads((whole / "config.json").read_text())
    assert cfg["sim"]["world"]["ball_cone"] == math.pi / 2 and cfg["sim"]["settle_until_rest"] == 0.01
    assert cfg["mutation"]["effector_bias_sigma"] == 0.0 and cfg["ecology"]["merge_null"] == kind
    assert {e["population"] for e in json.loads((whole / "history.json").read_text())["history"] if e["season"] >= 3} == {kind, NULL_B}


@pytest.mark.parametrize("kind", [HOLISTIC, CONVENTIONAL])
def test_retention_pair_with_rbt124_and_only_fauna_half(tmp_path, kind):
    both = tmp_path / "both"
    Ecology(evo(), _breeding_eco(seasons=4), out_dir=str(both), log=None).run()
    sel = tmp_path / "sel"
    Ecology(evo(), _breeding_eco(seasons=4, only_fauna=kind), out_dir=str(sel), log=None).run()
    rows = lambda p: [json.loads(l) for l in (p / "lineage.jsonl").read_text().splitlines()]
    assert [r for r in rows(both) if r["population"] == kind] == rows(sel)
    marker = tmp_path / "marker"
    Ecology(evo(), _breeding_eco(seasons=4, only_fauna=kind, lesion_fauna=kind), out_dir=str(marker), log=None).run()
    assert rows(sel) != rows(marker)
