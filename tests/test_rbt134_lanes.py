"""RBT-134 lanes (runs/RBT-134/lanes/, LAUNCH.md): the GO and clean-tree refusals, the restart skip, the stale-output
refusal, and a RELAY block that carries no numbers.  Nothing registered runs: every lane here is either refused or in
RBT134_DRY=1 plan mode, inside a throwaway git repository holding only the lane scripts.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANES = os.path.join(ROOT, "runs", "RBT-134", "lanes")
IDS = re.compile(r"\b(I[1-7]|B0|C\+|A0|P[1-5])\b")


def _relay():
    spec = importlib.util.spec_from_file_location("relay134", os.path.join(LANES, "relay.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo)] + list(args), check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """A throwaway clean git repo with only the lane scripts (so no lane can run anything real)."""
    r = tmp_path / "repo"
    shutil.copytree(LANES, r / "runs" / "RBT-134" / "lanes")
    (r / "README").write_text("x\n")
    _git(r, "init", "-q")
    _git(r, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    _git(r, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
    return r


def _lane(repo, lane, env_extra, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("RBT134_")}
    env.update({"PYTHON": sys.executable, "RBT134_NO_PUSH": "1"}, **env_extra)
    return subprocess.run(["bash", str(repo / "runs" / "RBT-134" / "lanes" / f"lane{lane}.sh")] + list(args),
                          capture_output=True, text=True, env=env, timeout=120)


@pytest.mark.parametrize("lane", ["A", "B"])
def test_refuses_without_the_go(repo, lane):
    p = _lane(repo, lane, {})
    assert p.returncode == 3 and "refused" in p.stderr


@pytest.mark.parametrize("lane", ["A", "B"])
def test_refuses_a_dirty_tree(repo, lane):
    (repo / "README").write_text("dirty\n")
    p = _lane(repo, lane, {"RBT134_GO": "1"})
    assert p.returncode == 4 and "dirty" in p.stderr


def _complete_json(path, head, n=100_000):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"git": head, "pools": {"W4b-801-bests": n, "P-801-final60": n}}))


def test_lane_a_skips_complete_outputs_and_plans_the_rest(repo):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    _complete_json(out / "B0.json", head)
    _complete_json(out / "C+.json", head)
    (out / "A0.json").write_text('{"truncated":')  # incomplete: re-run
    (out / "B0-resign.txt").write_text("done\n")
    p = _lane(repo, "A", {"RBT134_GO": "1", "RBT134_DRY": "1"})
    assert p.returncode == 0, p.stderr
    plan = p.stdout
    assert "skip B0 (complete)" in plan and "skip C+ (complete)" in plan
    assert "PLAN run A0:" in plan and "PLAN run P2:" in plan and "PLAN run P3:" in plan
    assert "skip B0-resign (complete)" in plan and "PLAN run C+-resign:" in plan
    order = [m.group(1) for m in re.finditer(r"PLAN run (\S+?):", plan)]
    assert order[:6] == ["A0", "P1", "P4", "P5", "P2", "P3"]  # controls, checks, then P2 before P3


def test_lane_a_refuses_an_output_from_another_head(repo):
    out = repo / "runs" / "RBT-134" / "out"
    _complete_json(out / "B0.json", "0" * 40)
    p = _lane(repo, "A", {"RBT134_GO": "1", "RBT134_DRY": "1"})
    assert p.returncode == 5 and "another head" in p.stderr


def test_lane_b_skips_complete_outputs(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    out.mkdir(parents=True)
    (out / "e1.txt").write_text("done\n")
    (out / "e2-B0-801.txt").write_text("done\n")
    h1 = out / "h1-B0.json"
    h1.write_text(json.dumps({"git": head, "pools": {"a": 100_000, "b": 100_000}, "rows": []}))
    p = _lane(repo, "B", {"RBT134_GO": "1", "RBT134_DRY": "1"}, str(tmp_path / "founders"))
    assert p.returncode == 0, p.stderr
    assert "skip e1 (complete)" in p.stdout and "skip e2-B0-801 (complete)" in p.stdout
    assert "skip h1-B0 (complete)" in p.stdout and "PLAN run h1-A0:" in p.stdout
    assert "PLAN run e2-P5-7:" in p.stdout and "PLAN run founders-801:" in p.stdout


SYNTHETIC = """# RBT-134 readout (DESIGN.md r3, registered)

| condition | lineages | arrivals | flagged arrivals | k a16 | **k a32** | k a64 |
| B0 | 200000 | 84 | 0 | 0 | **0** | 0 |
| P2 | 200000 | 66 | 3 | 31 | **17** | 9 |

### P2: section-3 tables
k a32 = 17 of 200000 lineages = 17.00 per 200,000 [9.91, 27.21] (Wilson 95%)
DESCRIPTIVE ONLY, not registered (F2): k a32 counting each arrival's unflagged units = 18

## Controls

I2 B0: arrival set equals RBT-91-alone-baseline.txt's 84: YES; responses line for line: YES
I2 P2: arrival set equals RBT-91-alone-4.0.txt's 66: NO
B0 background, first 5,000 per pool, all: 26 of 9996 (registered 26 of 9996): YES
B0 background, first 5,000 per pool, unflagged: 22 of 9990 (registered 22 of 9990): YES
I3 P2: slope-bound violations 2; k a32 17 <= 29: YES
I5 C+: sham arrivals 91 within the 99% Binomial(200000, 84/200000) range [62, 109] of B0's food count: YES
I5 P5: sham arrivals 16800 within the 99% Binomial(200000, 84/200000) range [62, 109] of B0's food count: NO

## The family (Holm, m = 2; DESIGN.md 4, 6)

P2: discordant 17 up / 0 down, p = 7.629e-06 against alpha 0.0250: REJECTS; background 412/39871 vs B0 88/39960 -> **MOVES-WITH-BACKGROUND**

## VOID

- I2 P2: arrival set equals RBT-91-alone-4.0.txt's 66: NO
- I3 P2
- I5 P5
- B0 background prefix all
- something unforeseen with 12345 in it
"""


def test_relay_carries_no_numbers(tmp_path, capsys):
    relay = _relay()
    out = tmp_path / "out"
    out.mkdir()
    (out / "readout.txt").write_text(SYNTHETIC)
    (out / "P2.json").write_text("{}")
    relay.relay("A", str(out), "f" * 40, "123", "0m1.5s 0m0.2s")
    block = capsys.readouterr().out
    tokens = block.split("TOKENS", 1)[1].split("SHA256", 1)[0]
    stripped = IDS.sub("", tokens)
    assert not re.search(r"\d", stripped), stripped           # nothing but ids, YES/NO and VOID ids
    assert "I2 B0: YES YES" in tokens and "I2 P2: NO" in tokens and "I5 P5: NO" in tokens
    assert "B0-background-prefix all: YES" in tokens and "B0-background-prefix unflagged: YES" in tokens
    assert "VOID I2 P2, I3 P2, I5 P5, B0-background-prefix all, OTHER" in tokens
    for leaked in ("MOVES", "REJECTS", "17", "412", "Wilson", "section-3", "DESCRIPTIVE"):
        assert leaked not in tokens
    # the only other lines: head, sha256 of outputs, time
    rest = block.split("SHA256", 1)[1]
    for line in rest.strip().splitlines():
        assert re.fullmatch(r"\s*[0-9a-f]{64}  runs/RBT-134/out/\S+|TIME wall_s=\d+ cpu_children_user_sys=.*|===== END RELAY =====|", line), line


def test_relay_lane_b_tokens_are_yes_no(tmp_path, capsys):
    relay = _relay()
    out = tmp_path / "out"
    out.mkdir()
    (out / "e1.txt").write_text("| B0 | holistic | 0.9000 | 1.0% | 1 | 1.00% |\n")
    relay.relay("B", str(out), "f" * 40, "5", "")
    block = capsys.readouterr().out
    tokens = block.split("TOKENS", 1)[1].split("SHA256", 1)[0]
    assert "E1-B0-equals-parity.txt: NO" in tokens and "E2-B0-equals-RBT-112-tables: NO" in tokens
    assert not re.search(r"\d", tokens.replace("E1-B0", "").replace("E2-B0", "").replace("RBT-112", ""))


def test_e1_b0_check_accepts_the_committed_parity(tmp_path):
    relay = _relay()
    p = tmp_path / "e1.txt"
    p.write_text("| B0 | holistic | 0.9162 |  48.1% | 625 | 8.98% |\n| B0 | conventional | 0.9839 |  31.0% | 4000 | 0.00% |\n")
    assert relay.e1_b0_matches(str(p)) == "YES"
    p.write_text("| B0 | holistic | 0.9163 |  48.1% | 625 | 8.98% |\n| B0 | conventional | 0.9839 |  31.0% | 4000 | 0.00% |\n")
    assert relay.e1_b0_matches(str(p)) == "NO"


def test_completeness(tmp_path):
    relay = _relay()
    p = tmp_path / "x.json"
    assert relay.complete(str(p), "h", 10) == "incomplete"
    p.write_text(json.dumps({"git": "h", "pools": {"a": 10, "b": 10}}))
    assert relay.complete(str(p), "h", 10) == "complete"
    assert relay.complete(str(p), "other", 10) == "stale"
    p.write_text(json.dumps({"git": "h", "pools": {"a": 10, "b": 9}}))
    assert relay.complete(str(p), "h", 10) == "incomplete"
