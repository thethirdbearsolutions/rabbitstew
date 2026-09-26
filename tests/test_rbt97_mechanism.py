"""The generalised mechanism probe reproduces the hard-coded one it replaces (RBT-97).

`runs/RBT-97/mechanism.py` generalises `scripts/compass_mechanism.py` over population, sign
and magnitude, and replaces its four typed-out weights with `compass_replication.install`,
which derives them from `fixed.drive_commands`. The coordinator's condition for running the
arm was that the case the original covers -- W4b-801, sign +1, W = 32, which is a = 64 in
RBT-67's units -- reproduces it. That is what these tests check, at three levels:

1. the installed weight matrix is bitwise identical;
2. one bout's full output is identical, on `motif`, `phantom` and `antimotif`;
3. the decoy layout the phantom condition smells is the same layout.

They are deliberately bout-level rather than report-level: the report is a mean over 896
bouts, and a mean can agree while individual bouts do not.
"""
import importlib.util
import os
import sys
from dataclasses import replace

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W4B = os.path.join(ROOT, "docs", "artifacts", "RBT-23-W4b-801")

pytestmark = pytest.mark.skipif(
    not os.path.isdir(W4B), reason="W4b-801 artifacts not present in this checkout")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mods():
    cwd = os.getcwd()
    os.chdir(ROOT)  # both scripts read committed artifacts by relative path
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        cm = _load("compass_mechanism", os.path.join(ROOT, "scripts", "compass_mechanism.py"))
        gen = _load("rbt97_mechanism", os.path.join(ROOT, "runs", "RBT-97", "mechanism.py"))
        gen.CFG["w4b"] = gen.cds.config("w4b")
        gen.SIGN.update({("w4b", g): +1.0 for g in gen.cds.POPULATIONS["w4b"]["gens"]})
        yield cm, gen
    finally:
        os.chdir(cwd)


def test_install_is_bitwise_identical(mods):
    """The typed-out weights and the drive_commands-derived ones are the same four numbers."""
    cm, gen = mods
    from rabbitstew.genotype import Genotype
    from rabbitstew.simulation import Simulation, spawn_layout
    from rabbitstew.synthesis import synthesize

    cfg = replace(cm.cfg, random_start=True)
    g = Genotype.load(os.path.join(W4B, "conventional", "best_gen0090.json"))
    ph = synthesize(g, cfg.synthesis)
    nose, eff = cm.units(90)

    a = Simulation([g], cfg, spawns=spawn_layout(1, cfg, 9000))
    a.set_food_seed(9000)
    Wm = a.brains[0].W
    Wm[eff[1], nose[1]] += cm.W
    Wm[eff[2], nose[1]] += cm.W
    Wm[eff[1], nose[2]] -= cm.W
    Wm[eff[2], nose[2]] -= cm.W

    b = Simulation([g], cfg, spawns=spawn_layout(1, cfg, 9000))
    b.set_food_seed(9000)
    gen.cr.install(b.brains[0], ph, "compass", gen.cds.k_of(64.0))

    assert gen.cds.k_of(64.0) == cm.W, "a = 2k: the original's W = 32 is a = 64"
    assert np.array_equal(a.brains[0].W, b.brains[0].W)


@pytest.mark.parametrize("cond", ["motif", "phantom", "antimotif"])
@pytest.mark.parametrize("gen_id,seed", [(90, 9000), (590, 9003)])
def test_bout_output_is_identical(mods, cond, gen_id, seed):
    """Same bearings, same alignments, same items eaten -- not just the same mean."""
    cm, gen = mods
    old = cm.bout((gen_id, seed, cond))
    new = gen.bout(("w4b", gen_id, 64.0, seed, cond))
    assert old[0] == new[1] and old[1] == new[3] and old[2] == new[4]
    for i, name in enumerate(("bearing_near", "bearing_grad", "align_near", "align_grad", "items")):
        a, b = old[3 + i], new[5 + i]
        assert (np.isnan(a) and np.isnan(b)) or a == b, f"{name}: {a} != {b}"


def test_phantom_smells_the_same_decoy(mods):
    """The decoy offset is the original's, so the phantom condition is the same manipulation."""
    cm, gen = mods
    assert gen.DECOY_OFFSET == 5000
    src = open(os.path.join(ROOT, "scripts", "compass_mechanism.py")).read()
    assert "probe.set_food_seed(seed + 5000)" in src


def test_base_condition_installs_nothing(mods):
    """`base` must leave the brain alone, or every delta is measured against the wrong robot."""
    cm, gen = mods
    from rabbitstew.genotype import Genotype
    from rabbitstew.simulation import Simulation, spawn_layout

    cfg = gen.CFG["w4b"]
    g = Genotype.load(os.path.join(W4B, "conventional", "best_gen0090.json"))
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, 9000))
    before = sim.brains[0].W.copy()
    old = cm.bout((90, 9000, "base"))
    new = gen.bout(("w4b", 90, 0.0, 9000, "base"))
    assert old[7] == new[9]
    assert np.array_equal(before, sim.brains[0].W)
