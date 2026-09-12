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


def test_synergy_profile_detects_an_inert_and_a_working_brain():
    from rabbitstew.analysis import synergy_profile, transplant_brain
    from rabbitstew.fixed import drive_straight_genotype, pioneer_genotype

    quick = TrialConfig(approach_duration=2.0, steering_bearings=(90.0,), steering_duration=1.0, terrain_seeds=(0,), terrain_duration=1.0, push_duration=1.0)
    driver = drive_straight_genotype(0.6)  # moves only through its links (biases are zero on the wheels)
    r = synergy_profile(driver, SimConfig(), quick, donors=[pioneer_genotype(np.random.default_rng(1), hidden=1)])
    assert r["full"]["approach"] > 0.3
    assert r["bias_only"]["approach"] < 0.1  # nothing drives the wheels without links
    assert r["brain_dependence"] is not None and r["brain_dependence"] > 0.5
    assert len(r["transplants"]) == 1  # same hidden size: structures align
    a, b = pioneer_genotype(np.random.default_rng(0)), pioneer_genotype(np.random.default_rng(1))
    t = transplant_brain(a, b)
    assert t is not None and [l.weight for _, br in t.brains() for l in br.links] == [l.weight for _, br in b.brains() for l in br.links]
    assert transplant_brain(a, pioneer_genotype(np.random.default_rng(2), hidden=3)) is None


def test_heritability_and_founder_model(tmp_path):
    from rabbitstew.analysis import founder_model, realised_heritability

    cfg = EvolutionConfig(population_size=6, generations=4, elites=1, champion_interval=0, seed=1, sim=SimConfig(duration=0.3))
    Experiment(cfg, out_dir=str(tmp_path), log=None).run()
    h = realised_heritability(str(tmp_path), "holistic")
    assert h["n"] == 18 and (h["heritability"] is None or -1.0 <= h["heritability"] <= 1.0)
    noise = founder_model(N=20, generations=100, replicates=5, checkpoints=(50, 100))
    strong = founder_model(N=20, generations=100, heritability=1.0, replicates=5, checkpoints=(50, 100))
    assert noise[100] > strong[100] and strong[100] <= 1.5 and 2 <= noise[100] <= 8


def _ecology_lineage(tmp_path, n_children=12):
    """A lineage log in the ecology's shape: one row per individual's last season, with a record.

    Ten founders that lived a while (f8 the exception, dead after one season), then children of
    them: the even ones long-lived, the odd ones dead after two seasons.
    """
    rows = []
    for i in range(10):
        rows.append({"generation": 40, "population": "holistic", "name": f"f{i}", "parents": [], "fitness": round(0.1 * i, 4),
                     "distance": None, "nodes": 3, "energy": 1.0, "age": 40, "evals": 1 if i == 8 else 8, "last_score": 0.1})
    for j in range(n_children):
        parent = f"f{j % 10}"
        long_lived = j % 2 == 0
        rows.append({"generation": 40, "population": "holistic", "name": f"c{j}", "parents": [parent],
                     "fitness": round(0.8 * 0.1 * (j % 10) + 0.02 * (j % 3), 4), "distance": None, "nodes": 3,
                     "energy": 0.5, "age": 30 if long_lived else 2, "evals": 9 if long_lived else 2, "last_score": 0.1})
    path = tmp_path / "lineage.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    (tmp_path / "config.json").write_text(json.dumps({"population_size": 10, "ecology": {"seasons": 40}}))
    return rows


def test_ecology_heritability_counts_only_lived_in_lifetimes(tmp_path):
    from rabbitstew.analysis import ECOLOGY_MIN_EVALS, is_ecology_run, realised_heritability

    _ecology_lineage(tmp_path, n_children=30)
    assert is_ecology_run(str(tmp_path)) and ECOLOGY_MIN_EVALS == 5
    loose = realised_heritability(str(tmp_path), "holistic", min_evals=0)
    strict = realised_heritability(str(tmp_path), "holistic", min_evals=5)
    assert loose["n"] == 30  # every child counts when a single season's yield is allowed to
    # the odd children lived two seasons, and f8's three long-lived children have a one-season parent
    assert strict["n"] == 12 and strict["min_evals"] == 5
    assert strict["heritability"] > 0.9  # yield is 0.8 of the parent's by construction
    # the window is in seasons of birth, which for an ecology row is its season less its age
    assert realised_heritability(str(tmp_path), "holistic", window=(0, 11), min_evals=5)["n"] == 12
    assert realised_heritability(str(tmp_path), "holistic", window=(11, 100), min_evals=5)["n"] == 0


def test_founder_survival_is_the_drift_baseline(tmp_path):
    from rabbitstew.analysis import founder_survival

    _ecology_lineage(tmp_path)
    got = founder_survival(str(tmp_path), "holistic")
    assert got["generation"] == 40 and got["of"] == 22  # everyone's last row is season 40
    assert got["founders"] == 10
    assert founder_survival(str(tmp_path), "conventional") == {"population": "conventional", "generation": None, "founders": None, "of": 0}


def test_ancestry_carries_the_ecology_record(tmp_path):
    _ecology_lineage(tmp_path)
    chain = ancestry(read_lineage(str(tmp_path)), "holistic", "c0")
    assert [c["name"] for c in chain] == ["c0", "f0"]
    assert chain[0]["evals"] == 9 and chain[0]["age"] == 30 and chain[0]["energy"] == 0.5


def test_mutation_heritability_of_a_runs_own_operators(tmp_path):
    from rabbitstew.analysis import mutation_heritability

    cfg = EvolutionConfig(population_size=6, generations=1, elites=1, champion_interval=0, seed=2, sim=SimConfig(duration=0.3))
    Experiment(cfg, out_dir=str(tmp_path), log=None).run()
    h = mutation_heritability(str(tmp_path), "holistic", n=12, seed=0)
    assert h["operator"] == "mutate" and h["n"] == 12 and h["descriptors"]
    assert all(-1.0 <= d["r"] <= 1.0 for d in h["descriptors"] if d["r"] is not None)
    assert all(d["change_sd"] >= 0 for d in h["descriptors"])
    assert -1.0 <= h["median_r"] <= 1.0
    c = mutation_heritability(str(tmp_path), "conventional", n=12, seed=0)
    assert c["operator"] == "mutate_weights"  # the fixed body's topology is not evolving in this config
    # the designed body is untouched by weight mutation, so its morphology is perfectly inherited
    morph = [d["r"] for d in c["descriptors"] if d["descriptor"].startswith("m:") and d["r"] is not None]
    assert morph == [] or min(morph) > 0.99
