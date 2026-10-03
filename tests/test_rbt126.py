"""RBT-126: the opt-in breeding rule (`ecology --breed-rule`) and drift-arm gate (`ecology --breed-gate none`).

* Off is byte-identical: four tiny ecology runs (two built in Python, one through the CLI with the economy, one
  through the CLI with --neutral) write the config.json, lineage.jsonl, history.json, state.json and cohorts.jsonl
  whose digests were recorded on the code before the flags (integration head 3503cc2), and so does naming the
  defaults explicitly.
* Each rule orders a hand-built set of breeders as runs/RBT-126/BREEDING-RULES.md specifies -- within each fauna
  after a merge (PR #417 §3), keeping the fauna interleaving of the committed shuffle -- and the replica
  (runs/RBT-126/breeding_rules.py) orders the same energies under the same stream identically.
* The leak's energy is accounted for: every member's energy moves by gain - cost - leak - birth cost x children,
  and each season's recorded `leaked` is the sum of what the rule took from the members that entered the season.
* A short embodied run under every rule breeds, applies the rule to both fauna (R6) and resumes byte for byte.
* --breed-gate none is refused outside --neutral, and inside it lets a member with negative energy breed.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import platform
from types import SimpleNamespace

import numpy as np
import pytest

from rabbitstew.cli import build_parser
from rabbitstew.ecology import Ecology, EcologyConfig, leak_energy, order_breeders, parse_breed_rule
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC

from test_ecology_switches import _breeding_eco, _evo

ROOT = pathlib.Path(__file__).resolve().parents[1]
RULES = ("shuffle", "energy", "tickets", "leak:0.2", "leakx:0.3")

GOLDEN = {  # sha256 on the code before the flags (3503cc2), x86_64, mujoco 3.14.0, numpy 2.4.6
    "eco/config.json": "b4f93ce781aef045a429850ecfa7c9f5fb0f7189d2b58b974fe0b8bde6886d5e",
    "eco/lineage.jsonl": "f518f1056110f8a71a6725fe570dcb2a03b38d0a2e1adff054ed954ed5ff2415",
    "eco/history.json": "343648cf448ee38575b0eb8555d2b2a29f77d6c5a3a82b5c3d2766a6f627d480",
    "eco/state.json": "455fcab480e129d4e0972b00a8da2636a6e1a92b9066e8d008981f51f9b0804f",
    "eco/cohorts.jsonl": "00250fe5907a45b40e74f25234d9f7a18c91bd590358015ba913be3859b4a45a",
    "neutral/config.json": "6cb803f458c5399e37e11b0341e93a3f27f911b2ee17faeacedbfb7a74d1a5de",
    "neutral/lineage.jsonl": "09684a17bbe8df55e0c222d6967fc23358e211a9a6559103cb50ac503d1236a1",
    "neutral/history.json": "04f336f115128a91bca24e7f012ca23be13023f27fc066b1814c5ad8906e3915",
    "neutral/state.json": "1623284fc0d59a3c8e0419bc6f0afe1e112878973b456ebe124d72b4fb79e543",
    "neutral/cohorts.jsonl": "b8d0ff853d4787c23a4cd2ece5c893132bd083fd877133d34dedd1b7204cc57f",
}
CLI = "ecology --seasons 5 --max-age 3 --capacity 4 --challenge foraging --group-size 2 --duration 0.5 --seed 5".split()
CLI_ECO = CLI + "--living-cost 0.25 --initial-energy 3 --birth-threshold 2".split()
CLI_NEUTRAL = CLI + "--neutral --initial-energy 3".split()
GOLDEN_CLI = {
    "cli/config.json": "0a2453a8d8cff2dd368c0e22652fec692fb547d05f5b51ca93e3536030335bb9",
    "cli/lineage.jsonl": "d0b3b8e3d8b40f7c8f513dace8fdff2a822a7078da2fda3a3ce2c845ca666299",
    "cli/history.json": "f3dae4b5415bc90972590b84b2c8024f72754e5dd2e956e0a217503caa5fb26d",
    "cli/state.json": "c9fb6eb3a2ee67badcc0a41f252a164873c9c40c99754b46417d7fd4b15ad2f3",
    "cli/cohorts.jsonl": "d121a1f6520001cb08f90cd0a5512ba959255fe6fc2fd388cc4a64d462553b90",
    "clin/config.json": "3e6084aeec8a92169b5d75f969a6987b4c2e98d02c4a12b0bdfec36cb2d7bf30",
    "clin/lineage.jsonl": "1dcf648f2c163d42392845744dadad57142b4e6e5175c762a6a775dffb7d64af",
    "clin/history.json": "a84c7c625248b5402cc39f29ccddd8e7c38b57e72b0814daafcb45d1d1402594",
    "clin/state.json": "a81b88e2bafa009d6e3fe92641e3eda991898b865e95239d2025825cb7afa428",
    "clin/cohorts.jsonl": "052f838988d818286503046e904400ecd9ab8730a144055a4445607c10303cf2",
}


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _cli(argv, out):
    args = build_parser().parse_args(argv + ["--out", str(out), "--unfair-i-know"])  # RBT-128: a pre-preset command line
    args.func(args)


def _replica():
    spec = importlib.util.spec_from_file_location("breeding_rules", ROOT / "runs" / "RBT-126" / "breeding_rules.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _history(out):
    return json.loads((out / "history.json").read_text())["history"]


def _rows(out):
    return [json.loads(l) for l in (out / "lineage.jsonl").read_text().splitlines()]


# --- off is byte-identical --------------------------------------------------------------------------------------

@pytest.mark.skipif(platform.machine() != "x86_64", reason="digests recorded on x86_64 (RBT-96)")
@pytest.mark.parametrize("explicit", [False, True])
def test_off_is_byte_identical_to_the_code_before_the_flags(tmp_path, explicit):
    kw = dict(breed_rule="shuffle", breed_gate="energy") if explicit else {}
    Ecology(_evo(11, 1.5), _breeding_eco(seasons=6, **kw), out_dir=str(tmp_path / "eco"), log=None).run()
    Ecology(_evo(11, 1.5), _breeding_eco(seasons=6, starvation=False, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0, **kw),
            out_dir=str(tmp_path / "neutral"), log=None).run()
    flags = ["--breed-rule", "shuffle", "--breed-gate", "energy"] if explicit else []
    _cli(CLI_ECO + flags, tmp_path / "cli")
    _cli(CLI_NEUTRAL + flags, tmp_path / "clin")
    got = {k: _sha(tmp_path / k) for k in {**GOLDEN, **GOLDEN_CLI}}
    assert got == {**GOLDEN, **GOLDEN_CLI}


def test_defaults_write_no_new_keys_and_set_values_round_trip(tmp_path):
    d = EcologyConfig().to_dict()
    assert "breed_rule" not in d and "breed_gate" not in d
    on = EcologyConfig(breed_rule="leakx:0.3").to_dict()
    assert on["breed_rule"] == "leakx:0.3" and "breed_gate" not in on
    assert EcologyConfig(**json.loads(json.dumps(on))).breed_rule == "leakx:0.3"
    _cli(CLI_ECO + ["--breed-rule", "leakx:0.3", "--seasons", "1"], tmp_path / "a")
    assert json.loads((tmp_path / "a" / "config.json").read_text())["ecology"]["breed_rule"] == "leakx:0.3"
    _cli(CLI_NEUTRAL + ["--breed-gate", "none", "--seasons", "1"], tmp_path / "b")
    assert json.loads((tmp_path / "b" / "config.json").read_text())["ecology"]["breed_gate"] == "none"


# --- validation -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("bad", ["", "Energy", "leak", "leakx:0", "leakx:1.5", "leak:x", "energy:0.3", "tickets:1"])
def test_a_malformed_rule_is_refused(bad):
    with pytest.raises(ValueError):
        parse_breed_rule(bad)
    with pytest.raises(SystemExit):
        build_parser().parse_args(CLI_ECO + ["--breed-rule", bad, "--out", "/nonexistent"])


@pytest.mark.parametrize("rule, kind, leak", [("shuffle", "shuffle", 0.0), ("energy", "energy", 0.0), ("tickets", "tickets", 0.0),
                                              ("leak:0.2", "leak", 0.2), ("leakx:1", "leakx", 1.0)])
def test_rules_parse(rule, kind, leak):
    assert parse_breed_rule(rule) == (kind, leak)


def test_the_gate_is_removed_only_in_the_no_selection_economy(tmp_path):
    with pytest.raises(SystemExit, match="--neutral"):
        _cli(CLI_ECO + ["--breed-gate", "none"], tmp_path / "a")
    with pytest.raises(ValueError, match="no-selection"):
        EcologyConfig(breed_gate="none").check_breeding()
    with pytest.raises(ValueError, match="no-selection"):
        EcologyConfig(breed_gate="none", starvation=False, birth_cost=0.0, living_cost=0.05).check_breeding()
    EcologyConfig(breed_gate="none", starvation=False, birth_cost=0.0, living_cost=0.0, birth_threshold=0.0).check_breeding()
    with pytest.raises(ValueError):
        EcologyConfig(breed_gate="off").check_breeding()


def test_a_ranking_rule_is_refused_where_it_has_nothing_to_rank(tmp_path):
    with pytest.raises(SystemExit, match="no-selection"):
        _cli(CLI_NEUTRAL + ["--breed-rule", "energy"], tmp_path / "a")
    with pytest.raises(ValueError, match="relative"):
        EcologyConfig(breed_rule="leakx:0.3", living_cost="relative").check_breeding()
    with pytest.raises(ValueError, match="breed_rule"):
        Ecology(_evo(), _breeding_eco(breed_rule="leakx:0"), log=None)


def test_the_flags_cannot_be_shifted_mid_run(tmp_path):
    with pytest.raises(ValueError):
        Ecology(_evo(), _breeding_eco(shift_at=2, shift="breed_rule=energy"), log=None)


# --- ordering on a hand-built population ------------------------------------------------------------------------

def _members(energies):
    return [SimpleNamespace(name=f"m{i}", record={"energy": float(e)}) for i, e in enumerate(energies)]


ENERGIES = [3.0, 12.5, 4.0, 4.0, 30.0, 3.2, 7.7, 4.0]


def test_shuffle_is_the_committed_shuffle_alone():
    a, b = _members(ENERGIES), _members(ENERGIES)
    order_breeders(a, "shuffle", np.random.default_rng(4))
    np.random.default_rng(4).shuffle(b)
    assert [m.name for m in a] == [m.name for m in b]


@pytest.mark.parametrize("kind", ["energy", "leakx"])
def test_energy_and_leakx_take_the_richest_first_and_break_ties_by_the_shuffle(kind):
    seen_tie_orders = set()
    for seed in range(20):
        got = order_breeders(_members(ENERGIES), kind, np.random.default_rng(seed))
        es = [m.record["energy"] for m in got]
        assert es == sorted(ENERGIES, reverse=True)
        seen_tie_orders.add(tuple(m.name for m in got if m.record["energy"] == 4.0))
        shuffled = _members(ENERGIES)
        np.random.default_rng(seed).shuffle(shuffled)
        assert [m.name for m in got if m.record["energy"] == 4.0] == [m.name for m in shuffled if m.record["energy"] == 4.0]
    assert len(seen_tie_orders) > 1  # the ties really are broken at random


def test_leak_orders_like_shuffle():
    a = order_breeders(_members(ENERGIES), "leak", np.random.default_rng(9))
    b = order_breeders(_members(ENERGIES), "shuffle", np.random.default_rng(9))
    assert [m.name for m in a] == [m.name for m in b]


def test_tickets_draws_every_breeder_once_with_the_richest_first_most_often():
    firsts = []
    for seed in range(4000):
        got = order_breeders(_members(ENERGIES), "tickets", np.random.default_rng(seed))
        assert sorted(m.name for m in got) == sorted(f"m{i}" for i in range(len(ENERGIES)))
        firsts.append(got[0].name)
    share = firsts.count("m4") / len(firsts)  # m4 holds 30 of the 68.4 energy
    assert share == pytest.approx(30.0 / sum(ENERGIES), abs=0.03)
    assert firsts.count("m0") / len(firsts) == pytest.approx(3.0 / sum(ENERGIES), abs=0.015)


@pytest.mark.parametrize("kind", ["energy", "leakx", "tickets"])
def test_after_a_merge_each_fauna_is_ranked_only_within_the_places_the_shuffle_gave_it(kind):
    """PR #417 §3: a pooled sort would give every freed slot to the richer fauna.  Each fauna keeps the positions of the
    committed shuffle, and only its own members are reordered into them."""
    for seed in range(50):
        def pool():
            rich = [SimpleNamespace(name=f"h{i}", record={"energy": 30.0 + i, "kind": HOLISTIC}) for i in range(5)]
            poor = [SimpleNamespace(name=f"c{i}", record={"energy": 3.0 + 0.1 * i, "kind": CONVENTIONAL}) for i in range(5)]
            return rich + poor
        got = order_breeders(pool(), kind, np.random.default_rng(seed))
        shuffled = pool()
        np.random.default_rng(seed).shuffle(shuffled)
        assert [m.record["kind"] for m in got] == [m.record["kind"] for m in shuffled]  # the interleaving is the shuffle's
        if kind != "tickets":
            for f in (HOLISTIC, CONVENTIONAL):
                es = [m.record["energy"] for m in got if m.record["kind"] == f]
                assert es == sorted(es, reverse=True)
        assert sorted(m.name for m in got) == sorted(m.name for m in shuffled)


def test_one_fauna_is_the_plain_ranking():
    one = [SimpleNamespace(name=m.name, record={**m.record, "kind": HOLISTIC}) for m in _members(ENERGIES)]
    a = order_breeders(one, "energy", np.random.default_rng(3))
    b = order_breeders(_members(ENERGIES), "energy", np.random.default_rng(3))
    assert [m.name for m in a] == [m.name for m in b]


# --- the replica agrees ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("rule", RULES + ("leakx:1.0",))
def test_the_replica_ranks_who_breeds_as_the_embodied_code_does(rule):
    br = _replica()
    kind, _ = parse_breed_rule(rule)
    rng = np.random.default_rng(126)
    for trial in range(200):
        n = int(rng.integers(1, 30))
        energies = list(np.round(rng.uniform(3.0, 40.0, n), 1))
        if n > 3:
            energies[1] = energies[2] = energies[3]  # ties
        seed = int(rng.integers(0, 2**31))
        embodied = order_breeders(_members(energies), kind, np.random.default_rng(seed))
        # the replica's member: [type, energy, age, id, depth, score_sum, evals, parent, last gain]
        replica = br.order(np.random.default_rng(seed), [[0, e, 0, i, 0, 0.0, 0, None, 0.0] for i, e in enumerate(energies)], rule)
        assert [m.name for m in embodied] == [f"m{p[3]}" for p in replica], (rule, trial)


@pytest.mark.parametrize("rule", ["leak:0.2", "leakx:0.3", "leakx:1.0"])
def test_the_replica_leaks_what_the_embodied_code_leaks(rule):
    kind, lam = parse_breed_rule(rule)
    for e in (0.5, 2.9, 3.0, 3.1, 7.0, 55.0):
        replica = e * (1 - lam) if kind == "leak" else (e - lam * (e - 3.0) if e > 3.0 else e)  # breeding_rules.run
        assert e - leak_energy(e, kind, lam, 3.0) == pytest.approx(replica, abs=1e-12)


# --- the embodied rule: smoke, parity, accounting, resume ------------------------------------------------------

def _rule_eco(rule, **kw):
    # _breeding_eco with a threshold the founders start above, so the rules have rich members to rank
    base = dict(seasons=5, breed_rule=rule, initial_energy=3.0, birth_threshold=1.2, birth_cost=0.5, living_cost=0.05)
    base.update(kw)
    return _breeding_eco(**base)


@pytest.fixture(scope="module")
def smoke(tmp_path_factory):
    base = tmp_path_factory.mktemp("rbt126")
    out = {}
    for rule in RULES:
        d = base / rule.replace(":", "_")
        Ecology(_evo(11, 1.5), _rule_eco(rule), out_dir=str(d), log=None).run()
        out[rule] = d
    return out


@pytest.mark.parametrize("rule", RULES)
def test_a_short_embodied_run_breeds_under_every_rule_for_both_fauna(smoke, rule):
    hist = _history(smoke[rule])
    for kind in (HOLISTIC, CONVENTIONAL):
        assert sum(e["births"] for e in hist if e["population"] == kind) > 0, kind
        if rule.startswith("leak"):
            assert sum(e["leaked"] for e in hist if e["population"] == kind) > 0, kind  # R6: the rule runs on both fauna
        else:
            assert all("leaked" not in e for e in hist)
    cfg = json.loads((smoke[rule] / "config.json").read_text())["ecology"]
    assert cfg.get("breed_rule", "shuffle") == rule


def test_the_rules_change_who_breeds(smoke):
    parents = {rule: [(r["generation"], tuple(r["parents"])) for r in _rows(smoke[rule]) if r["age"] == 0 and r["parents"]] for rule in RULES}
    assert parents["energy"] != parents["shuffle"] and parents["tickets"] != parents["shuffle"]


@pytest.mark.parametrize("rule", ["leak:0.2", "leakx:0.3"])
def test_the_leak_conserves_energy(smoke, rule):
    """Every member's energy moves by gain - cost - leak - birth cost x its children; the season's `leaked` is the sum
    of the rule's leak over the members that entered the season (the living and those about to die).  Energies are
    logged to 3 decimals and gains to 4, so identities hold to 2e-3 per member."""
    kind, lam = parse_breed_rule(rule)
    eco = _rule_eco(rule)
    rows, hist = _rows(smoke[rule]), _history(smoke[rule])
    by = {}
    for r in rows:
        by[(r["population"], r["generation"], r["name"])] = r
    kids = {}
    for r in rows:
        if r["age"] == 0 and r["evals"] == 0 and r["parents"]:
            key = (r["population"], r["generation"], r["parents"][0])
            kids[key] = kids.get(key, 0) + 1
    checked = 0
    for (pop, g, name), r in by.items():
        prev = by.get((pop, g - 1, name))
        if prev is None or r["evals"] == 0:
            continue
        e0 = prev["energy"]
        want = e0 - leak_energy(e0, kind, lam, eco.birth_threshold) + r["last_score"] - eco.living_cost - eco.birth_cost * kids.get((pop, g, name), 0)
        assert r["energy"] == pytest.approx(want, abs=2e-3), (pop, g, name)
        checked += 1
    assert checked > 20
    for e in hist:
        if e["season"] == 0:
            continue
        entering = [r["energy"] for (pop, g, _), r in by.items() if pop == e["population"] and g == e["season"] - 1]
        assert e["leaked"] == pytest.approx(sum(leak_energy(x, kind, lam, eco.birth_threshold) for x in entering), abs=2e-3 * len(entering) + 1e-9)


@pytest.mark.parametrize("rule", ["tickets", "leakx:0.3"])
def test_a_run_under_a_rule_resumes_byte_for_byte(tmp_path, rule):
    whole = tmp_path / "whole"
    part = tmp_path / "part"
    Ecology(_evo(11, 1.5), _rule_eco(rule, seasons=5), out_dir=str(whole), log=None).run()
    Ecology(_evo(11, 1.5), _rule_eco(rule, seasons=2), out_dir=str(part), log=None).run()
    Ecology.resume(str(part), seasons=5, log=None).run()
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json"):
        assert (part / name).read_bytes() == (whole / name).read_bytes(), name


@pytest.mark.parametrize("rule", ["energy", "leakx:0.3", "tickets"])
def test_after_a_merge_the_rule_runs_on_both_fauna(tmp_path, monkeypatch, rule):
    """Inside a real merged run (#422 SHOULD 3): at every call, the fauna interleaving is the bare shuffle's, so each
    fauna takes the free slots the shuffle gave it, and energy / leakx sort each fauna within its own slots."""
    import copy
    import rabbitstew.ecology as E
    real, calls = E.order_breeders, {"merged": 0}

    def checked(breeders, kind, rng, **kw):
        bare = list(breeders)
        twin = np.random.Generator(type(rng.bit_generator)())
        twin.bit_generator.state = copy.deepcopy(rng.bit_generator.state)
        twin.shuffle(bare)
        got = real(breeders, kind, rng, **kw)
        faunas = [m.record["kind"] for m in got]
        assert faunas == [m.record["kind"] for m in bare]
        if kind in ("energy", "leakx"):
            for f in set(faunas):
                es = [m.record["energy"] for m in got if m.record["kind"] == f]
                assert es == sorted(es, reverse=True)
        calls["merged"] += len(set(faunas)) > 1
        return got

    monkeypatch.setattr(E, "order_breeders", checked)
    Ecology(_evo(11, 1.5), _rule_eco(rule, merge_after=2, seasons=6), out_dir=str(tmp_path / "m"), log=None).run()
    assert calls["merged"] > 0  # the check ran on pooled cohorts
    hist = _history(tmp_path / "m")
    late = [e for e in hist if e["season"] >= 2]
    assert all(e["merged"] for e in late) and {e["population"] for e in late} == {HOLISTIC, CONVENTIONAL}
    if rule.startswith("leak"):
        assert all(e["leaked"] >= 0 for e in hist)


# --- the warning (#422 MUST) -----------------------------------------------------------------------------------

@pytest.mark.parametrize("rule", ["energy", "tickets", "leak:0.2", "leakx:0.3"])
def test_every_rule_but_shuffle_warns_on_stderr_and_in_the_log(tmp_path, rule):
    logged = []
    with pytest.warns(UserWarning, match="failed RBT-126's breeding-rule screen"):
        Ecology(_evo(11, 0.3), _rule_eco(rule, seasons=1), out_dir=str(tmp_path / "w"), log=logged.append).run()
    assert any(rule in m and "failed RBT-126" in m for m in logged)
    for name in ("config.json", "history.json", "lineage.jsonl"):  # the warning changes no output file
        assert "failed RBT-126" not in (tmp_path / "w" / name).read_text()
    with pytest.warns(UserWarning, match="failed RBT-126"):  # a resume warns too
        Ecology.resume(str(tmp_path / "w"), seasons=2, log=None).run()


def test_shuffle_does_not_warn(tmp_path, recwarn):
    logged = []
    Ecology(_evo(11, 0.3), _rule_eco("shuffle", seasons=1), out_dir=str(tmp_path / "s"), log=logged.append).run()
    assert not [w for w in recwarn if "RBT-126" in str(w.message)]
    assert not any("RBT-126" in m for m in logged)


def test_the_cli_prints_the_warning(tmp_path, capsys):
    _cli(CLI_ECO + ["--breed-rule", "energy", "--seasons", "1"], tmp_path / "c")
    err_out = capsys.readouterr()
    assert "failed RBT-126's breeding-rule screen" in err_out.out + err_out.err


# --- the drift-arm gate ------------------------------------------------------------------------------------------

def _neutral(gate):
    return _breeding_eco(seasons=1, capacity=4, starvation=False, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0,
                         max_age=5, breed_gate=gate)


@pytest.mark.parametrize("gate, breeds", [("energy", False), ("none", True)])
def test_without_the_gate_a_member_in_debt_breeds_in_a_neutral_arm(gate, breeds):
    e = Ecology(_evo(11, 0.3), _neutral(gate), log=None)
    for kind in (HOLISTIC, CONVENTIONAL):
        for i, m in enumerate(e.populations[kind]):
            m.record["energy"] = -5.0  # every member's cumulative gain far below zero
            m.record["age"] = 4 if i == 0 else 0  # one dies of age this season and frees a slot
    e.step()
    for kind in (HOLISTIC, CONVENTIONAL):
        born = [m for m in e.populations[kind] if m.record["age"] == 0]
        assert bool(born) is breeds, kind
