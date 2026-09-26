"""RBT-104 (adversary F2): the config comparison tolerates fields later tickets add at their defaults."""
import copy
import importlib.util
import json
import os

import pytest

from rabbitstew.ecology import EcologyConfig
from rabbitstew.evolution import EvolutionConfig

_p = os.path.join(os.path.dirname(__file__), "..", "runs", "RBT-104", "configcmp.py")
_s = importlib.util.spec_from_file_location("rbt104_configcmp", _p)
cc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(cc)


def _cfg():
    return json.loads(json.dumps({**EvolutionConfig().to_dict(), "ecology": dict(EcologyConfig().__dict__)}))


@pytest.mark.parametrize("path", [("morph_protection",), ("ecology", "shift_at"), ("mutation", "motor_rate"),
                                  ("sim", "control_substeps")])
def test_a_field_added_at_its_default_is_tolerated_and_named(path):
    got = _cfg()
    ref = copy.deepcopy(got)
    d = ref
    for k in path[:-1]:
        d = d[k]
    del d[path[-1]]  # the committed config predates the field
    assert got != ref
    names = cc.added_at_default(got, ref)
    assert names == [".".join(path)]
    assert got == ref


def test_a_field_added_away_from_its_default_is_not_tolerated():
    got, ref = _cfg(), _cfg()
    del ref["morph_protection"]
    got["morph_protection"] = 3
    assert cc.added_at_default(got, ref) == []
    assert got != ref


def test_an_unknown_added_field_is_not_tolerated():
    got, ref = _cfg(), _cfg()
    got["ecology"]["no_such_field"] = 0
    assert cc.added_at_default(got, ref) == []
    assert got != ref
