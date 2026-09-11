import json

import numpy as np

from rabbitstew.analysis import TrialConfig, analyze_run, ancestry, capability_profile, controller_descriptors, descriptor_vector, diversity, founders, lesion_map, morphology_descriptors, read_lineage, sensor_influence
from rabbitstew.evolution import EvolutionConfig, Experiment
from rabbitstew.fixed import drive_straight_genotype, pioneer_genotype
from rabbitstew.genotype import random_genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

QUICK = TrialConfig(approach_duration=1.0, steering_bearings=(90.0,), steering_duration=1.0, terrain_seeds=(0,), terrain_duration=1.0, push_duration=1.0, lesion_duration=0.5)


def test_morphology_descriptors_of_the_pioneer():
    m = morphology_descriptors(pioneer_genotype(np.random.default_rng(0)), SimConfig())
    assert m["parts"] == 5 and m["nodes"] == 4 and m["expressed_nodes"] == 4 and m["recessive_fraction"] == 0.0
    assert m["max_depth"] == 1 and m["max_branching"] == 4
    assert m["symmetry"] > 0.9  # wheels mirror across the chassis
    assert m["joint_fractions"]["hinge"] == 1.0 and m["shape_fractions"]["cylinder"] == 0.8
    assert m["footprint"] == 4  # four wheels on the ground, chassis clear


def test_controller_descriptors_and_influence():
    g = pioneer_genotype(np.random.default_rng(0))
    c = controller_descriptors(g, SimConfig())
    assert c["units"] == 15 and c["live_effectors"] == 2 and c["driven_effectors"] == 2
    assert c["connected_fraction"] == 1.0 and c["centralisation"] == 1.0 and c["cyclic_units"] == 6
    assert c["mean_sensor_path"] == 2.0 and c["env_driven_effectors"] == 2 and c["oscillator_driven_effectors"] == 0
    inf = sensor_influence(synthesize(g))
    assert len(inf) == 7 and all(s["influence"] > 0 for s in inf)


def test_capability_profile_scores_a_driver():
    p = capability_profile(drive_straight_genotype(0.6), SimConfig(), TrialConfig(approach_duration=3.0, steering_bearings=(90.0,), steering_duration=1.0, terrain_seeds=(0,), terrain_duration=1.0, push_duration=2.0))
    assert p["approach"]["progress"] > 0.5 and p["approach"]["straightness"] > 0.9 and not p["approach"]["fell"]
    assert p["approach"]["work"] > 0 and p["approach"]["work_per_metre"] > 0
    assert p["steering"]["successes"] == 0  # it cannot turn
    assert p["push"]["block_mass"] > 10


def test_lesion_map_finds_the_drive_link():
    g = drive_straight_genotype(0.6)
    lm = lesion_map(g, SimConfig(), TrialConfig(lesion_duration=2.0))
    assert lm["baseline"] > 0.3
    losses = {u["label"]: u["loss"] for u in lm["units"] if u["kind"] == "effector"}
    assert all(v > 0.05 for v in losses.values())  # both wheel effectors matter
    assert lm["essential_units"] >= 2


def test_diversity_and_lineage_helpers(rng):
    sim = SimConfig()
    vecs = [descriptor_vector(random_genotype(rng), sim) for _ in range(4)]
    assert diversity(vecs) > 0
    assert diversity([vecs[0], vecs[0]]) == 0.0
    lineage = {("holistic", "h0-1"): {"generation": 0, "population": "holistic", "name": "h0-1", "parents": [], "fitness": 0.4},
               ("holistic", "h1-0"): {"generation": 1, "population": "holistic", "name": "h1-0", "parents": ["h0-1"], "fitness": 0.6}}
    chain = ancestry(lineage, "holistic", "h1-0")
    assert [c["name"] for c in chain] == ["h1-0", "h0-1"]
    assert founders(lineage, "holistic", ["h1-0"]) == {"founders": 1, "of": 1}
    assert read_lineage("/nonexistent") == {}


def test_analyze_run_end_to_end(tmp_path):
    cfg = EvolutionConfig(population_size=3, generations=2, elites=1, champion_interval=1, champions=2, seed=3, sim=SimConfig(duration=0.3))
    Experiment(cfg, out_dir=str(tmp_path), log=None).run()
    res = analyze_run(str(tmp_path), out_json=str(tmp_path / "a.json"), out_html=str(tmp_path / "a.html"), every=1, lesions="final", trials=QUICK, log=None)
    assert len(res["individuals"]) == 4
    finals = [r for r in res["individuals"] if r["generation"] == 1]
    assert all("lesions" in r for r in finals) and all("lesions" not in r for r in res["individuals"] if r["generation"] == 0)
    assert {d["scope"] for d in res["diversity"]} == {"champions", "final"}
    assert res["lineage"]["holistic"]["chain"][0]["generation"] == 1 and res["lineage"]["holistic"]["founders"]["of"] == 3
    data = json.loads((tmp_path / "a.json").read_text())
    assert data["individuals"][0]["capability"]["terrain"]["trials"][0]["seed"] == 0
    html = (tmp_path / "a.html").read_text()
    assert "const A = " in html and "Lesion map" in html
