"""RBT-111: the three-salt A/A's runner matches RBT-96's exactly but for the salt, salt 2 is a third independent
holistic stream, and the pre-registered readout (exact sign-flip test, Holm, reading table) computes what
PREREGISTRATION.md says it does."""
import importlib.util
import itertools
import json
import os
import re
import shutil

import pytest

from rabbitstew.cli import build_parser
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, TERRAIN, spawn_streams

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")


def _load(name, *path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ro = _load("rbt111_readout", "runs", "RBT-111", "readout.py")


def _evolve_args(script):
    text = open(os.path.join(ROOT, "scripts", script)).read()
    m = re.search(r"rabbitstew evolve --generations.*?--out \"\$OUT\"", text, re.S)
    return m.group(0)


def test_runner_is_rbt96s_configuration_exactly():
    assert _evolve_args("rbt111_run.sh") == _evolve_args("rbt96_run.sh")
    text = open(os.path.join(ROOT, "scripts", "rbt111_run.sh")).read()
    assert "s0) SALT=0" in text and "s1) SALT=1" in text and "s2) SALT=2" in text
    assert "OUT=runs/RBT-111/$ARM-$SEED" in text


def test_salt_2_parses_and_is_a_third_independent_holistic_stream():
    args = build_parser().parse_args(["evolve", "--seed", "217", "--holistic-stream-salt", "2", "--out", "/nonexistent"])
    assert args.holistic_stream_salt == 2
    draws = {s: {k: g.integers(0, 2**31 - 1, 8).tolist() for k, g in spawn_streams(217, s).items()} for s in (0, 1, 2)}
    for a, b in itertools.combinations((0, 1, 2), 2):
        assert draws[a][HOLISTIC] != draws[b][HOLISTIC]
        assert draws[a][CONVENTIONAL] == draws[b][CONVENTIONAL]
        assert draws[a][TERRAIN] == draws[b][TERRAIN]


def test_sign_flip_is_exact_enumeration():
    xs = [0.3, -0.1, 0.25, 0.05, -0.2]
    obs = abs(sum(xs))
    hit = sum(abs(sum(s * x for s, x in zip(signs, xs))) >= obs - 1e-12 for signs in itertools.product((1, -1), repeat=len(xs)))
    assert ro.sign_flip_p(xs) == (hit / 32, hit, 32)
    assert ro.sign_flip_p([0.1] * 12)[1:] == (2, 4096)  # only all-positive and all-negative reach the observed sum
    assert ro.sign_flip_p([0.0] * 12)[0] == 1.0


def test_sign_flip_reproduces_rbt108s_post_hoc_p():
    """The adversary's F3 figure, 0.0024 = 10/4096 over 205-216, from the committed RBT-96 summaries."""
    r85 = ro.r85
    d = [r85.summary(os.path.join(ROOT, "runs", "RBT-96", f"s1-{s}"), True)["final_fifth"]
         - r85.summary(os.path.join(ROOT, "runs", "RBT-96", f"s0-{s}"), True)["final_fifth"] for s in range(205, 217)]
    assert ro.sign_flip_p(d)[1:] == (10, 4096)


def test_holm_and_reading_table():
    assert ro.holm({"c0": 0.02, "c12": 0.5}) == {"c0": (0.04, True), "c12": (0.5, False)}
    assert ro.holm({"c0": 0.03, "c12": 0.5}) == {"c0": (0.06, False), "c12": (0.5, False)}  # 0.03 > 0.05 / 2
    assert ro.holm({"c0": 0.02, "c12": 0.04})["c12"] == (0.04, True)  # step-down: second at 0.05
    assert ro.holm({"c0": 0.04, "c12": 0.04}) == {"c0": (0.08, False), "c12": (0.08, False)}
    assert ro.reading(True, False) == "salt0"
    assert ro.reading(True, True) == ro.reading(False, True) == "keys"
    assert ro.reading(False, False) == "chance"
    assert "NOT DECIDED" in ro.READING["chance"]


def test_trimmed_mean_cuts_20_percent_each_end():
    assert ro.trimmed_mean(list(range(12))) == pytest.approx(5.5)  # drops 0, 1 and 10, 11
    assert ro.trimmed_mean([0] * 10 + [100, 100]) == 0


def _fake_root(tmp_path, offsets):
    """Twelve seeds x three arms, each a copy of RBT-96's committed s0-205 summaries, with offsets[arm] added to
    every final-fifth checkpoint's champ_holistic_mean (generation 0 untouched)."""
    src = os.path.join(ROOT, "runs", "RBT-96", "s0-205")
    for s in ro.SEEDS:
        for arm in ro.ARMS:
            d = tmp_path / f"{arm}-{s}"
            shutil.copytree(src, d)
            lines = (d / "generations.txt").read_text().splitlines()
            head = lines[0].split("\t")
            c = head.index("champ_holistic_mean")
            out = [lines[0]]
            for line in lines[1:]:
                f = line.split("\t")
                if f[c] and int(f[0]) >= 200:
                    f[c] = f"{float(f[c]) + offsets[arm]:.6f}"
                out.append("\t".join(f))
            (d / "generations.txt").write_text("\n".join(out) + "\n")
    return str(tmp_path)


def test_readout_end_to_end_salt0_offset(tmp_path, capsys):
    root = _fake_root(tmp_path, {"s0": -0.10, "s1": 0.0, "s2": 0.0})
    r = ro.main(root, ro.SEEDS, from_summaries=True)
    assert r["complete"]
    assert r["c0"] == pytest.approx([0.10] * 12, abs=2e-6)
    assert r["c12"] == pytest.approx([0.0] * 12, abs=2e-6)
    assert r["stats"]["c0"]["hit"] == 2 and r["holm"]["c0"][1] and not r["holm"]["c12"][1]
    assert r["reading"] == "salt0"
    assert len(set(r["gen0"].values())) == 1  # generation 0 untouched: the secondary contrasts are all zero
    out = capsys.readouterr().out
    assert "SALT 0's OFFSET" in out and "SECONDARY" in out
    # identical copies: the conventional hash matches but the holistic lineages do not differ, so the check fails
    row = next(line.split() for line in out.splitlines() if line.startswith("217 ") and "(5000)" in line)
    assert row[-5:] == ["True", "False", "True", "(250)", "False"]  # conv identical, holistic distinct, env, PASS


def test_readout_end_to_end_keys_and_chance(tmp_path):
    assert ro.main(_fake_root(tmp_path / "a", {"s0": 0.0, "s1": 0.0, "s2": 0.10}), ro.SEEDS, from_summaries=True)["reading"] == "keys"
    r = ro.main(_fake_root(tmp_path / "b", {"s0": 0.0, "s1": 0.0, "s2": 0.0}), ro.SEEDS, from_summaries=True)
    assert r["reading"] == "chance" and r["stats"]["c0"]["p"] == 1.0


def test_missing_arm_is_not_a_result(tmp_path, capsys):
    root = _fake_root(tmp_path, {"s0": 0.0, "s1": 0.0, "s2": 0.0})
    shutil.rmtree(os.path.join(root, "s2-228"))
    r = ro.main(root, ro.SEEDS, from_summaries=True)
    assert not r["complete"] and len(r["c0"]) == 11
    assert "NOT A RESULT" in capsys.readouterr().out
