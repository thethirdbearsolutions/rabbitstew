"""RBT-130 (the RBT-129 sweep's hooks, "RBT-129a"): --merge-null, the lesioned-motif marker (--lesion-fauna), the
single-fauna path (--only-fauna), the sweep log (--sweep-log) and --obstacle-radius.

* Off is byte-identical: RBT-126's golden runs (whose digests were recorded on the code before RBT-126's flags) give
  the same bytes with every RBT-130 field left off or named at its default, and the defaults write no new keys.
* --merge-null (RBT-129 ADVERSARY M8 and section 1.7): B is a separate label with its own mate pool (a B child never
  has an A parent), its own stream (independent of every other stream: its spawn key collides with none, and the run is
  byte-identical to the merged run up to the merge), its own names; it is subsampled to the replaced fauna's count at
  the merge and keeps the copied members' records; the merged cohort's arena bank starts full at the merge in both the
  M and the N arm (the transient is the same); a run resumes byte for byte across the merge.
* --lesion-fauna: every food sensor of that fauna reads 0 (legacy intensity and contrast channel alike); the other
  fauna's seasons are untouched.
* --only-fauna: the fauna's seasons are its half of a two-fauna run at the same seed, byte for byte.
* --sweep-log: the fields are present, add up, and appear only when asked.
* The strips compose: RBT-120's motor budget, RBT-125's smell channel and eating rule and RBT-126's breed rule, with
  --merge-null and --sweep-log, in one run that resumes byte for byte (RBT-124 is pending, PR #420).
"""
import json
import platform

import numpy as np
import pytest

from rabbitstew.cli import build_parser
from rabbitstew.ecology import NULL_B, Ecology, EcologyConfig, breed_seed_sequence, merge_null_seed_sequence
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, STREAMS, EvolutionConfig
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation
from rabbitstew.world import WorldConfig

from test_ecology_switches import _breeding_eco, _evo
from test_rbt126 import CLI_ECO, CLI_NEUTRAL, GOLDEN, GOLDEN_CLI, _sha

SWEEP_OFF = dict(merge_null=None, lesion_fauna=None, only_fauna=None, sweep_log=False)


def _cli(argv, out):
    args = build_parser().parse_args(argv + ["--out", str(out)])
    args.func(args)


def _history(out):
    return json.loads((out / "history.json").read_text())["history"]


def _rows(out):
    return [json.loads(l) for l in (out / "lineage.jsonl").read_text().splitlines()]


def _run(out, eco, evo=None):
    Ecology(evo or _evo(11, 1.5), eco, out_dir=str(out), log=None).run()
    return out


# --- off is byte-identical ---------------------------------------------------------------------------------------

@pytest.mark.skipif(platform.machine() != "x86_64", reason="digests recorded on x86_64 (RBT-96)")
def test_off_is_byte_identical_with_the_new_fields_named_at_their_defaults(tmp_path):
    Ecology(_evo(11, 1.5), _breeding_eco(seasons=6, **SWEEP_OFF), out_dir=str(tmp_path / "eco"), log=None).run()
    Ecology(_evo(11, 1.5), _breeding_eco(seasons=6, starvation=False, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0, **SWEEP_OFF),
            out_dir=str(tmp_path / "neutral"), log=None).run()
    _cli(CLI_ECO, tmp_path / "cli")
    _cli(CLI_NEUTRAL, tmp_path / "clin")
    got = {k: _sha(tmp_path / k) for k in {**GOLDEN, **GOLDEN_CLI}}
    assert got == {**GOLDEN, **GOLDEN_CLI}


def test_defaults_write_no_new_keys_and_set_values_round_trip(tmp_path):
    d = EcologyConfig().to_dict()
    assert not set(SWEEP_OFF) & set(d)
    on = EcologyConfig(merge_after=3, merge_null=HOLISTIC, sweep_log=True).to_dict()
    assert on["merge_null"] == HOLISTIC and on["sweep_log"] is True and "lesion_fauna" not in on
    back = EcologyConfig(**json.loads(json.dumps(on)))
    assert back.merge_null == HOLISTIC and back.sweep_log
    evo = EvolutionConfig(sim=SimConfig(food=FoodConfig())).to_dict()
    assert "smell_lesion" not in evo["sim"]["food"]
    evo_on = EvolutionConfig(sim=SimConfig(food=FoodConfig(smell_lesion=True))).to_dict()
    assert evo_on["sim"]["food"]["smell_lesion"] is True


def test_obstacle_radius_is_a_flag_and_only_then_changes_the_config(tmp_path):
    _cli(CLI_ECO + ["--seasons", "1"], tmp_path / "a")
    _cli(CLI_ECO + ["--seasons", "1", "--obstacle-radius", "3.6"], tmp_path / "b")
    a = json.loads((tmp_path / "a" / "config.json").read_text())
    b = json.loads((tmp_path / "b" / "config.json").read_text())
    assert a["sim"]["world"]["random_radius"] == 2.6 and b["sim"]["world"]["random_radius"] == 3.6
    a["sim"]["world"]["random_radius"] = 3.6
    assert a == b


# --- validation ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kw, msg", [
    (dict(merge_null=HOLISTIC), "merge_null needs merge_after"),
    (dict(merge_null="pioneer", merge_after=2), "merge_null must be"),
    (dict(lesion_fauna=CONVENTIONAL, merge_after=2), "lesion_fauna"),
    (dict(only_fauna=HOLISTIC, merge_after=2), "only_fauna"),
    (dict(lesion_fauna=CONVENTIONAL, challenge="solo"), "foraging"),
    (dict(lesion_fauna=CONVENTIONAL, only_fauna=HOLISTIC), "lesion nothing"),
    (dict(merge_null=HOLISTIC, merge_after=2, cull_at=2, cull="1"), "cull"),
])
def test_a_flag_that_cannot_be_honoured_is_refused(kw, msg):
    with pytest.raises(ValueError, match=msg):
        Ecology(_evo(11, 0.3), _breeding_eco(seasons=1, **kw), log=None)


def test_the_flags_cannot_be_shifted_mid_run():
    for f in SWEEP_OFF:
        with pytest.raises(ValueError, match="not a shiftable"):
            Ecology(_evo(11, 0.3), _breeding_eco(seasons=1, shift_at=1, shift=f"{f}=1"), log=None)


# --- --merge-null (ADVERSARY M8, section 1.7) ---------------------------------------------------------------------

def test_the_null_stream_is_independent_of_every_other_stream():
    seed = 11
    null = [merge_null_seed_sequence(seed, k) for k in (HOLISTIC, CONVENTIONAL)]
    others = [np.random.SeedSequence(seed).spawn(len(STREAMS))[i] for i in range(len(STREAMS))]
    others += [breed_seed_sequence(seed, k) for k in range(1, 6)]
    others += [np.random.SeedSequence(seed, spawn_key=(STREAMS.index(HOLISTIC), s)) for s in range(1, 6)]  # RBT-96's salt
    keys = {tuple(s.spawn_key) for s in null}
    assert len(keys) == 2 and not keys & {tuple(s.spawn_key) for s in others}
    draws = {tuple(np.random.default_rng(s).integers(0, 2**31, 8)) for s in null + others}
    assert len(draws) == len(null) + len(others)


@pytest.fixture(scope="module")
def merged(tmp_path_factory):
    base = tmp_path_factory.mktemp("rbt130")
    out = {}
    for name, kw in (("M", {}), ("NH", dict(merge_null=HOLISTIC)), ("NC", dict(merge_null=CONVENTIONAL))):
        # free pooled slots (16 > 6 + 6) and a longer life, so that both labels breed after the merge
        out[name] = _run(base / name, _breeding_eco(seasons=9, merge_after=3, sweep_log=True, pooled_capacity=16, max_age=8, **kw))
    return out


@pytest.mark.parametrize("arm", ["NH", "NC"])
def test_the_null_run_is_the_merged_run_until_the_merge(merged, arm):
    m = [r for r in _rows(merged["M"]) if r["generation"] < 3]
    n = [r for r in _rows(merged[arm]) if r["generation"] < 3]
    assert m == n  # creating B's stream draws nothing from any other stream
    hm = [e for e in _history(merged["M"]) if e["season"] < 3]
    hn = [e for e in _history(merged[arm]) if e["season"] < 3]
    assert hm == hn


@pytest.mark.parametrize("arm, kind", [("NH", HOLISTIC), ("NC", CONVENTIONAL)])
def test_b_replaces_the_other_fauna_at_its_count_and_keeps_the_copied_records(merged, arm, kind):
    other = CONVENTIONAL if kind == HOLISTIC else HOLISTIC
    rows = _rows(merged[arm])
    living = [r for r in rows if "death" not in r]
    before = {r["name"]: r for r in living if r["generation"] == 2 and r["population"] == kind}
    n_other = sum(1 for r in living if r["generation"] == 2 and r["population"] == other)
    gone = [r for r in rows if r.get("death") == "merge-null"]
    assert len(gone) == n_other and all(r["population"] == other for r in gone)
    hist = _history(merged[arm])
    at = [e for e in hist if e["season"] == 3]
    assert {e["population"] for e in at} == {kind, NULL_B}
    assert at[0]["merge_counts"][other] == n_other and at[0]["merge_counts"][kind] == len(before)
    assert all(e["population"] in (kind, NULL_B) for e in hist if e["season"] >= 3)
    genomes = sorted((merged[arm] / NULL_B / "genomes").glob("*.json"))
    docs = [json.loads(p.read_text()) for p in genomes]
    copies = [d for d in docs if len(d["parents"]) == 1 and d["parents"][0] in before]
    assert len(copies) == n_other  # adversary M1: B's count is always the replaced fauna's count
    assert all(d["name"].startswith("b") for d in copies)


@pytest.mark.parametrize("arm", ["NH", "NC"])
def test_a_b_child_never_has_an_a_parent(merged, arm):
    rows = _rows(merged[arm])
    pop = {}
    for r in rows:
        pop.setdefault(r["name"], r["population"])
    born_b = [r for r in rows if r["population"] == NULL_B and r["age"] == 0 and r["parents"] and "death" not in r]
    born_a = [r for r in rows if r["population"] != NULL_B and r["age"] == 0 and r["parents"] and r["generation"] >= 3 and "death" not in r]
    assert born_b, "B bred"
    for r in born_b:
        assert r["name"].startswith("be")
        assert all(pop.get(p) == NULL_B for p in r["parents"]), r
    for r in born_a:
        assert all(pop.get(p) != NULL_B for p in r["parents"]), r


def test_b_breeds_with_the_copied_fauna_s_body_model(merged):
    for arm, kind in (("NH", HOLISTIC), ("NC", CONVENTIONAL)):
        g = json.loads(sorted((merged[arm] / NULL_B / "genomes").glob("be*.json"))[0].read_text())
        a = json.loads(sorted((merged[arm] / kind / "genomes").glob("*.json"))[0].read_text())
        assert (len(g["nodes"]) == len(a["nodes"])) or kind == HOLISTIC  # the designed body is fixed; the holistic one mutates


@pytest.mark.parametrize("kind", [HOLISTIC, CONVENTIONAL])
def test_b_matches_the_replaced_count_when_its_fauna_is_the_minority(tmp_path, kind):
    """Adversary M1: a cull before the merge leaves the copied fauna short; B is still the replaced fauna's count
    (a stratified fill: every member copied floor or ceil(n/m) times), so N starts from M's composition."""
    other = CONVENTIONAL if kind == HOLISTIC else HOLISTIC
    eco = _breeding_eco(seasons=4, merge_after=3, merge_null=kind, sweep_log=True, cull_at=2, cull=f"{kind}=5")
    out = _run(tmp_path / "n", eco)
    at = [e for e in _history(out) if e["season"] == 3]
    n, m = at[0]["merge_counts"][other], at[0]["merge_counts"][kind]
    assert m < n, (m, n)  # the minority case
    gone = [r for r in _rows(out) if r.get("death") == "merge-null"]
    assert len(gone) == n
    docs = [json.loads(p.read_text()) for p in (out / NULL_B / "genomes").glob("*.json")]
    copies = [d for d in docs if not d["parents"][0].startswith("b")]
    assert len(copies) == n and len({d["name"] for d in copies}) == n  # unique names
    per = {}
    for d in copies:
        per[d["parents"][0]] = per.get(d["parents"][0], 0) + 1
    assert set(per.values()) <= {n // m, -(-n // m)} and len(per) == m


@pytest.mark.parametrize("kind", [None, HOLISTIC, CONVENTIONAL])
def test_forking_an_s_checkpoint_into_m_or_n_is_the_straight_run(tmp_path, kind):
    """Adversary M2 (DESIGN section 5.2, 5.6 item 2, K1): S runs to its season-59 checkpoint (here 3); the merge (and
    the null) are set in its config.json; the resume is byte-identical to a run that had them from season 0."""
    merge = dict(merge_after=3, merge_null=kind)
    straight = _run(tmp_path / "straight", _breeding_eco(seasons=7, sweep_log=True, **merge))
    fork = _run(tmp_path / "fork", _breeding_eco(seasons=3, sweep_log=True))
    cfg = json.loads((fork / "config.json").read_text())
    cfg["ecology"]["merge_after"] = 3
    if kind is not None:
        cfg["ecology"]["merge_null"] = kind
    (fork / "config.json").write_text(json.dumps(cfg, indent=2))
    Ecology.resume(str(fork), seasons=7, log=None).run()
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json"):
        assert (fork / name).read_bytes() == (straight / name).read_bytes(), name


def test_the_merge_null_resumes_byte_for_byte(tmp_path):
    whole, part = tmp_path / "whole", tmp_path / "part"
    eco = dict(merge_after=3, merge_null=CONVENTIONAL, sweep_log=True)
    _run(whole, _breeding_eco(seasons=7, **eco))
    _run(part, _breeding_eco(seasons=5, **eco))
    Ecology.resume(str(part), seasons=7, log=None).run()
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json"):
        assert (part / name).read_bytes() == (whole / name).read_bytes(), name


def _persistent_evo():
    return EvolutionConfig(seed=11, brain_model="foraging", conventional_topology=True,
                           sim=SimConfig(duration=1.0, random_start=True, score="food", world=WorldConfig(terrain="flat"),
                                         food=FoodConfig(items=4, radius=1.5, eat_radius=0.4, patches=2, patch_radius=0.4, regrow_delay=60.0)))


def test_the_arena_bank_transient_at_the_merge_is_the_same_in_m_and_n(tmp_path):
    """ADVERSARY M8: at the merge the merged cohort gets a fresh bank keyed on its labels (full arenas in a persistent
    world) in both arms, so M and N see the same transient."""
    logs = {}
    for name, kw in (("M", {}), ("N", dict(merge_null=HOLISTIC))):
        e = Ecology(_persistent_evo(), _breeding_eco(seasons=5, merge_after=2, **kw), out_dir=str(tmp_path / name), log=None)
        e.run()
        logs[name] = [r for r in e.arena_log if r["season"] == 2]
        key = "+".join(e._labels())
        assert logs[name] and logs[name][0]["population"] == key
    for name in logs:
        assert logs[name][0]["season_start_crop_mean"] == 4.0 and logs[name][0]["empty_fraction"] == 0.0
    assert logs["M"][0]["arenas"] == logs["N"][0]["arenas"]


# --- --lesion-fauna ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("contrast", [0.0, 2.5])
def test_a_lesioned_food_sensor_reads_zero(contrast):
    """Every food nose of a lesioned body reads the zero-information constant, 0, under the legacy intensity and under
    the contrast channel, while the same body unlesioned smells the food (RBT-125's placement helpers)."""
    from test_rbt125 import _food, _food_readings, _pioneer_sim
    reads = {}
    for lesion in (False, True):
        sim = _pioneer_sim(items=2, smell_contrast=contrast, smell_lesion=lesion)
        _food(sim, [(0.6, 0.3), (1.5, -0.8)])
        vals = [_food_readings(sim)]
        for _ in range(20):
            sim.step()
            vals.append(_food_readings(sim))
        reads[lesion] = np.array(vals)
    assert reads[True].size and np.all(reads[True] == 0.0)
    assert np.any(reads[False] != 0.0)


def test_the_lesion_touches_only_its_fauna(tmp_path):
    plain = _run(tmp_path / "plain", _breeding_eco(seasons=4))
    lesioned = _run(tmp_path / "lesion", _breeding_eco(seasons=4, lesion_fauna=CONVENTIONAL))
    for kind, same in ((HOLISTIC, True), (CONVENTIONAL, False)):
        a = [r for r in _rows(plain) if r["population"] == kind]
        b = [r for r in _rows(lesioned) if r["population"] == kind]
        assert (a == b) is same, kind
    assert json.loads((lesioned / "config.json").read_text())["ecology"]["lesion_fauna"] == CONVENTIONAL


# --- --only-fauna ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", [HOLISTIC, CONVENTIONAL])
def test_one_fauna_alone_is_its_half_of_the_two_fauna_run(tmp_path, kind):
    both = _run(tmp_path / "both", _breeding_eco(seasons=5))
    alone = _run(tmp_path / "alone", _breeding_eco(seasons=5, only_fauna=kind))
    assert [r for r in _rows(both) if r["population"] == kind] == _rows(alone)
    assert [e for e in _history(both) if e["population"] == kind] == _history(alone)
    cb = [l for l in (both / "cohorts.jsonl").read_text().splitlines() if json.loads(l)["cohort"] == kind]
    assert cb == (alone / "cohorts.jsonl").read_text().splitlines()


# --- --sweep-log ----------------------------------------------------------------------------------------------------

def test_the_sweep_log_adds_up(merged):
    hist = _history(merged["M"])
    for e in hist:
        assert e["starved"] + e["aged"] == e["deaths"] - e.get("culled", {}).get(e["population"], 0)
        assert 0 <= e["eligible"] and e["share"] == e["alive"] / e["capacity"]
        assert e["food_mean"] is None or e["food_mean"] >= 0
    at = [e for e in hist if e["season"] == 3]
    assert all("merge_counts" in e for e in at) and not any("merge_counts" in e for e in hist if e["season"] != 3)
    merged_rows = [e for e in hist if e["season"] >= 3]
    for s in {e["season"] for e in merged_rows}:
        cap = {e["capacity"] for e in merged_rows if e["season"] == s}.pop()
        assert abs(sum(e["share"] for e in merged_rows if e["season"] == s) - sum(e["alive"] for e in merged_rows if e["season"] == s) / cap) < 1e-12


def test_the_season_s_dead_are_on_disk_and_in_the_means(merged):
    """Adversary S1: under --sweep-log the season's starved and aged are written to the lineage with their season's
    food, so every cohort seat has a lineage row for its season; the *_mean fields cover them, *_mean_living does not."""
    out = merged["M"]
    rows = _rows(out)
    have = {(r["generation"], r["name"]) for r in rows}
    seats = [(c["season"], s["name"]) for c in map(json.loads, (out / "cohorts.jsonl").read_text().splitlines()) for g in c["groups"] for s in g]
    assert all(seat in have for seat in seats)
    hist = _history(out)
    dead = {(e["season"], e["population"]): e["starved"] + e["aged"] for e in hist}
    logged = {}
    for r in rows:
        if r.get("death") in ("starved", "aged"):
            logged[(r["generation"], r["population"])] = logged.get((r["generation"], r["population"]), 0) + 1
    assert logged == {k: v for k, v in dead.items() if v}
    for e in hist:
        mine = [r for r in rows if r["generation"] == e["season"] and r["population"] == e["population"] and "food" in r and r.get("death") != "merge-null"]
        if mine:
            assert abs(e["food_mean"] - np.mean([r["food"] for r in mine])) < 1e-3


def test_no_sweep_fields_without_the_flag(tmp_path):
    hist = _history(_run(tmp_path / "off", _breeding_eco(seasons=3, merge_after=1)))
    for k in ("share", "starved", "aged", "eligible", "median_energy", "food_mean", "merge_counts"):
        assert all(k not in e for e in hist), k


# --- the strips compose --------------------------------------------------------------------------------------------

def test_every_merged_strip_composes_and_resumes(tmp_path):
    """RBT-120's motor budget, RBT-125's contrast channel and root eating, RBT-126's breed rule (warned), with
    --merge-null and --sweep-log, in one run; resumed from a mid-run checkpoint it gives the same bytes."""
    def evo():
        e = _evo(11, 1.5)
        e.sim.world.motor_budget = 1.77
        e.sim.food.smell_contrast, e.sim.food.eat_from = 2.5, "root"
        return e
    eco = dict(merge_after=3, merge_null=HOLISTIC, sweep_log=True, breed_rule="leakx:0.3")
    whole, part = tmp_path / "whole", tmp_path / "part"
    with pytest.warns(UserWarning, match="breed_rule"):
        _run(whole, _breeding_eco(seasons=6, **eco), evo())
    with pytest.warns(UserWarning, match="breed_rule"):
        _run(part, _breeding_eco(seasons=4, **eco), evo())
    with pytest.warns(UserWarning, match="breed_rule"):
        Ecology.resume(str(part), seasons=6, log=None).run()
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json"):
        assert (part / name).read_bytes() == (whole / name).read_bytes(), name
    cfg = json.loads((whole / "config.json").read_text())
    assert cfg["sim"]["world"]["motor_budget"] == 1.77 and cfg["sim"]["food"]["smell_contrast"] == 2.5
    assert cfg["ecology"]["merge_null"] == HOLISTIC and cfg["ecology"]["breed_rule"] == "leakx:0.3"
    assert {e["population"] for e in _history(whole) if e["season"] >= 3} == {HOLISTIC, NULL_B}


def test_the_retention_arms_compose(tmp_path):
    """RBT-129's R_sel / R_marker pair: one fauna alone, with the contrast channel, lesioned or not."""
    def evo():
        e = _evo(11, 1.5)
        e.sim.food.smell_contrast = 2.5
        return e
    sel = _run(tmp_path / "sel", _breeding_eco(seasons=3, only_fauna=CONVENTIONAL), evo())
    marker = _run(tmp_path / "marker", _breeding_eco(seasons=3, only_fauna=CONVENTIONAL, lesion_fauna=CONVENTIONAL), evo())
    assert {e["population"] for e in _history(marker)} == {CONVENTIONAL}
    assert _rows(sel) != _rows(marker)
