"""RBT-111: the three-salt A/A's runner matches RBT-96's exactly but for the salt, salt 2 is a third independent
holistic stream, and the pre-registered readout (exact sign-flip test, Holm, reading table) computes what
PREREGISTRATION.md says it does."""
import importlib.util
import itertools
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys

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


def test_design_is_sixteen_seeds_217_to_232():
    assert ro.SEEDS == tuple(range(217, 233))
    waves = open(os.path.join(ROOT, "runs", "RBT-111", "waves.txt")).read()
    cmds = re.findall(r"runs/RBT-111/drive.sh ((?:\d+ ?)+)", waves)
    seeds = [int(s) for c in cmds for s in c.split()]
    assert len(cmds) == 4 and sorted(seeds) == list(ro.SEEDS)


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


def _brute_c0(rows):
    """The permutation test's definition: all 6^n within-seed labellings, by brute force (small n only)."""
    obs = abs(sum((r[1] + r[2]) / 2 - r[0] for r in rows))
    hit = tot = 0
    for perms in itertools.product(list(itertools.permutations(range(3))), repeat=len(rows)):
        s = sum((r[q[1]] + r[q[2]]) / 2 - r[q[0]] for r, q in zip(rows, perms))
        hit += abs(s) >= obs - 1e-12
        tot += 1
    return hit / tot


def _tail_rows(rng, n):
    return [tuple(rng.gauss(0, 0.06) + (0.25 if rng.random() < 1 / 16 else 0) for _ in range(3)) for _ in range(n)]


def test_perm_c0_equals_the_6n_brute_force_definition():
    rng = random.Random(7)
    for n in (1, 2, 3, 4, 5):
        for _ in range(3):
            rows = _tail_rows(rng, n)
            p, hit, tot = ro.perm_c0_p(rows)
            assert tot == 3 ** n and abs(p - _brute_c0(rows)) < 1e-12


def test_perm_c0_count_pinned_at_16_seeds():
    """The design adversary's perm.txt section 2 dataset (random.Random(111), replayed) and its exact count."""
    rng = random.Random(111)
    for n in (1, 2, 3, 4, 5):
        for _ in range(3):
            _tail_rows(rng, n)
    rows = [tuple(rng.gauss(0, 0.06) for _ in range(3)) for _ in range(16)]
    rows = [(r[0] - 0.04, r[1], r[2]) for r in rows]
    assert ro.perm_c0_p(rows)[1:] == (150463, 3 ** 16)
    lo, hi = ro.perm_c0_ci(rows)
    assert (round(lo, 3), round(hi, 3)) == (0.019, 0.085)


def test_perm_c0_invariances():
    rng = random.Random(11)
    rows = _tail_rows(rng, 9)
    rows[0] = (rows[0][0] - 0.1, rows[0][1], rows[0][2])
    p = ro.perm_c0_p(rows)
    swapped = [(a, c, b) if i % 2 else (a, b, c) for i, (a, b, c) in enumerate(rows)]
    shifted = [(a + k, b + k, c + k) for k, (a, b, c) in zip([0.3, -0.2, 1.0, 0, 0, 0.05, 0, -1, 2], rows)]
    reordered = rows[::-1]
    for other in (swapped, shifted, reordered):
        q = ro.perm_c0_p(other)
        assert q[2] == p[2] and abs(q[0] - p[0]) < 1e-12


def test_perm_c0_ci_is_guarded_and_terminates():
    rows = _tail_rows(random.Random(3), 16)
    for n in (0, 1, 2):
        assert ro.perm_c0_ci(rows[:n]) == (float("-inf"), float("inf"))
    for n in (3, 4, 5, 6, 16):
        lo, hi = ro.perm_c0_ci(rows[:n])
        assert math.isfinite(lo) and math.isfinite(hi) and lo <= hi


def test_checkpoint_label_platform_and_summaries_only_in_drive_sh():
    text = open(os.path.join(ROOT, "runs", "RBT-111", "drive.sh")).read()
    assert 'ARMS+=("$ARM-$SEED")' in text  # AS is ARM-SEED ...
    assert text.count('"rbt-111-$AS"') == 2  # ... so the label is rbt-111-ARM-SEED, for the loop and the final save
    assert "rbt-111-ARM-SEED" in text and "rbt-111-SEED-ARM" not in text
    assert '>> "$PLAT"' in text and '> "$PLAT"' not in text.replace('>> "$PLAT"', "")
    assert "date -u" in text and "slot $((i / 2 + 1))" in text
    waves = open(os.path.join(ROOT, "runs", "RBT-111", "waves.txt")).read()
    assert "scripts/durable.sh restore runs/RBT-111/ARM-SEED rbt-111-ARM-SEED" in waves
    prereg = open(os.path.join(ROOT, "runs", "RBT-111", "PREREGISTRATION.md")).read()
    assert "rbt-111-ARM-SEED" in prereg and "rbt-111-SEED-ARM" not in prereg


def _slot2_tree(tmp_path):
    """A checkout-shaped tree after slot 2 of session 1: s0/s1/s2-217 and s0-218, with the readout's imports."""
    for rel in (("RBT-111", "readout.py"), ("RBT-96", "readout.py"), ("RBT-85", "readout.py")):
        os.makedirs(tmp_path / "runs" / rel[0], exist_ok=True)
        shutil.copy(os.path.join(ROOT, "runs", *rel), tmp_path / "runs" / rel[0] / rel[1])
    for arm, s in (("s0", 217), ("s1", 217), ("s2", 217), ("s0", 218)):
        shutil.copytree(os.path.join(ROOT, "runs", "RBT-96", "s0-205"), tmp_path / "runs" / "RBT-111" / f"{arm}-{s}")
    return tmp_path


def test_drive_sh_per_slot_call_returns_on_a_slot_2_root(tmp_path):
    """Design adversary F1: drive.sh's exact per-slot command, on the tree it meets after slot 2, returns (it used to
    hang forever in the interval inversion at n = 1)."""
    tree = _slot2_tree(tmp_path)
    text = open(os.path.join(ROOT, "runs", "RBT-111", "drive.sh")).read()
    cmd = re.search(r"^\s*(python runs/RBT-111/readout\.py [^\n]*?\$SEEDS_IN_SLOT\")", text, re.M).group(1)
    assert "--summaries-only" in cmd
    env = dict(os.environ, SEEDS_IN_SLOT="217,218", PATH=os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"])
    done = subprocess.run(["bash", "-c", cmd.replace("python ", f"{sys.executable} ", 1)], cwd=tree, env=env, timeout=60,
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    # and the full read of the same partial tree also returns (the interval's guard), printing NOT A RESULT
    done = subprocess.run([sys.executable, "runs/RBT-111/readout.py", "--from-summaries", "--seeds", "217,218"], cwd=tree,
                          timeout=60, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert "3. READING (NOT A RESULT, n = 1 of 2)" in done.stdout and "(-inf, +inf)" in done.stdout.replace("[-inf", "(-inf").replace("+inf]", "+inf)")


def _fake_root(tmp_path, offsets, gen0_offsets=None):
    """Sixteen seeds x three arms, each a copy of RBT-96's committed s0-205 summaries, with offsets[arm] added to
    every final-fifth checkpoint's champ_holistic_mean and gen0_offsets[arm] (default none) to generation 0's."""
    gen0_offsets = gen0_offsets or {}
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
                if f[c] and int(f[0]) == 0:
                    f[c] = f"{float(f[c]) + gen0_offsets.get(arm, 0.0):.6f}"
                out.append("\t".join(f))
            (d / "generations.txt").write_text("\n".join(out) + "\n")
    return str(tmp_path)


def test_readout_end_to_end_salt0_offset(tmp_path, capsys):
    root = _fake_root(tmp_path, {"s0": -0.10, "s1": 0.0, "s2": 0.0})
    r = ro.main(root, ro.SEEDS, from_summaries=True)
    assert r["complete"]
    assert r["c0"] == pytest.approx([0.10] * 16, abs=2e-6)
    assert r["c12"] == pytest.approx([0.0] * 16, abs=2e-6)
    # c0 by the permutation test: only the observed labelling reaches |sum c0| = 1.6, so 1 of 3^16
    assert r["stats"]["c0"]["tot"] == 3 ** 16 and r["stats"]["c0"]["hit"] == 1 and r["holm"]["c0"][1] and not r["holm"]["c12"][1]
    assert r["stats"]["c12"]["tot"] == 2 ** 16
    assert r["reading"] == "salt0"
    assert len(set(r["gen0"].values())) == 1  # generation 0 untouched: the secondary contrasts are all zero
    out = capsys.readouterr().out
    assert "SALT 0's OFFSET" in out and "SECONDARY" in out and "(1/43046721)" in out
    assert ro.SALT0_BESIDE in out and "s1 - s0: mean +0.1000, 16/16 positive" in out  # F9, beside the reading
    assert not r["gen0_rejected"] and ro.GEN0_CONSEQUENCE not in out
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
    assert not r["complete"] and len(r["c0"]) == 15
    line = next(l for l in capsys.readouterr().out.splitlines() if l.startswith("3. READING"))
    assert line.startswith("3. READING (NOT A RESULT, n = 15 of 16): ")  # F7: on the reading line itself


def test_gen0_rejection_is_reported_with_its_consequence(tmp_path, capsys):
    """F8: founders differing by salt do not change the primary reading; with 'chance' the reading is qualified."""
    r = ro.main(_fake_root(tmp_path, {"s0": 0.0, "s1": 0.0, "s2": 0.0}, {"s0": -0.1}), ro.SEEDS, from_summaries=True)
    out = capsys.readouterr().out
    assert r["reading"] == "chance" and r["gen0_rejected"]
    assert ro.GEN0_CONSEQUENCE in out and ro.GEN0_CHANCE_QUALIFIER in out
