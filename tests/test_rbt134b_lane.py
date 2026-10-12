"""RBT-134b registered-run lane (runs/RBT-134/lanes/lane134b.sh, relay134b.py; REGISTRATION-134b.md): the sha-bound GO,
the refusals (no GO, GO not HEAD, dirty tree, the wrong mujoco), DESIGN.md 13's order, the restart skips and stale
refusals, the control gate, the STOP-COST stop, a console that carries no sub-command output, and a RELAY block that
carries no numbers.  Nothing registered runs: every lane here is refused, in RBT134_DRY=1 plan mode, or driven by a
stub interpreter that only prints noise and writes placeholder files, inside a throwaway git repository (runs/RBT-134
copied, every other runs/ directory symlinked), as tests/test_rbt134_lanes.py does for lanes A and B.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANES = os.path.join(ROOT, "runs", "RBT-134", "lanes")
SEED = 20260912
CONTROLS = ("B0", "C+L1", "A0")
ALL = ("B0", "C+L1", "A0", "P1", "P4", "P5", "P2", "P3")
SWAPS = ("A0", "P1", "P4", "P2", "P3")
IDS = re.compile(r"\b(I[1-9]|I5-S|B0|C\+L1|C\+|A0|P[1-5])\b")


def _relay():
    spec = importlib.util.spec_from_file_location("relay134b_t", os.path.join(LANES, "relay134b.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo)] + list(args), check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    shutil.copytree(os.path.join(ROOT, "runs", "RBT-134"), r / "runs" / "RBT-134",
                    ignore=shutil.ignore_patterns("out", "__pycache__", "*.pyc"))
    for d in os.listdir(os.path.join(ROOT, "runs")):
        if d != "RBT-134" and os.path.isdir(os.path.join(ROOT, "runs", d)):
            os.symlink(os.path.join(ROOT, "runs", d), r / "runs" / d)
    shutil.copy(os.path.join(ROOT, ".gitignore"), r / ".gitignore")
    (r / "README").write_text("x\n")
    p = r / "runs" / "RBT-134" / "assay.py"  # a registered validation spend (any value here; the real one is sent)
    p.write_text(re.sub(r"^VALIDATION_SPENT_H = .*$", "VALIDATION_SPENT_H = 1.0", p.read_text(), count=1, flags=re.M))
    _git(r, "init", "-q")
    _git(r, "add", "-A")
    _git(r, "add", "-f", "runs/RBT-134")
    _git(r, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
    return r


def _out(repo):
    return repo / "runs" / "RBT-134" / "out" / f"134b-{SEED}"


STUB = """
import os, sys
print("k a32 = 17, p = 7.6e-06, 412/39871 MOVES-WITH-BACKGROUND")
print("debug 12345 arrivals 84", file=sys.stderr)
args = sys.argv[1:]
out = os.path.join(os.getcwd(), "runs", "RBT-134", "out", "134b-20260912")
if args[0].endswith("assay.py") and args[1] == "readout134b":
    print("## VOID\\n")
    print(os.environ.get("STUB_VOID", "none"))
elif args[0].endswith("assay.py") and args[1] == "run134b" and args[2] == os.environ.get("STUB_STOP"):
    print("STOP-COST: spent 28.1 + this item 1.2 + still to come 9.0 = 38.3 CPU-h > the cap 30", file=sys.stderr)
    sys.exit(9)
elif args[0].endswith("assay.py") and args[1] == "resign134b-check" and os.environ.get("STUB_STOP") == "re-signing":
    print("STOP-COST at re-signing: 30 CPU-h would be passed; stop and return to the owner", file=sys.stderr)
    sys.exit(9)
elif args[0].endswith("assay.py") and args[1] == "resign134b" and args[2] == os.environ.get("STUB_STOP_RESIGN"):
    print("STOP-COST at re-signing: stop and return to the owner (no output written)", file=sys.stderr)
    sys.exit(9)
elif args[0].endswith("assay.py") and args[1] == "resign134b":
    with open(os.path.join(out, args[2] + "-resign.txt.tmp"), "w") as f:
        f.write("compasses 3, anti 1\\n")
    os.replace(os.path.join(out, args[2] + "-resign.txt.tmp"), os.path.join(out, args[2] + "-resign.txt"))
"""


def _python(tmp_path, stub=True, mujoco="ok", crash=None):
    """An interpreter for the lane: relay134b.py runs for real (relay.py too), except `mujoco-ok`, answered as given,
    and CRASH, which exits 1; with stub, every other sub-command is replaced by noise and placeholder outputs."""
    (tmp_path / "stub.py").write_text(textwrap.dedent(STUB))
    py = tmp_path / "python-134b"
    other = f'exec {sys.executable} {tmp_path / "stub.py"} "$@"' if stub else f'exec {sys.executable} "$@"'
    crash_line = f'if [[ "$2" == {crash} ]]; then exit 1; fi\n' if crash else ""
    py.write_text(f'#!/bin/bash\n{crash_line}if [[ "$1" == *relay134b.py && "$2" == mujoco-ok ]]; then echo {mujoco}; exit 0; fi\n'
                  f'case "$1" in *relay134b.py|*relay.py) exec {sys.executable} "$@" ;; esac\n{other}\n')
    py.chmod(0o755)
    return str(py)


def _set_validation_spent(repo, value):
    """Set assay.VALIDATION_SPENT_H in the throwaway repo's copy and commit it (the lane needs a clean tree)."""
    p = repo / "runs" / "RBT-134" / "assay.py"
    text = re.sub(r"^VALIDATION_SPENT_H = .*$", f"VALIDATION_SPENT_H = {value}", p.read_text(), count=1, flags=re.M)
    p.write_text(text)
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-am", f"spent {value}")


def _lane(repo, tmp_path, env_extra=None, go=True, **kw):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("RBT134_", "RBT134B_"))}
    env.update({"PYTHON": _python(tmp_path, **kw), "RBT134_NO_PUSH": "1"})
    if go:
        env["RBT134B_GO"] = _git(repo, "rev-parse", "HEAD")
    env.update(env_extra or {})
    return subprocess.run(["bash", str(repo / "runs" / "RBT-134" / "lanes" / "lane134b.sh")],
                          capture_output=True, text=True, env=env, timeout=300)


def _complete(path, head, swap=False, n=100_000, n_bg=20_000):
    cond = path.name[:-len("-swap.json")] if swap else path.name[:-5]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"condition": cond, "fields": _relay()._conditions()[cond], "swap": swap,
                                "master_seed": SEED, "n_per_pool": n, "n_bg_per_pool": n_bg, "git": head,
                                "pools": {"W4b-801-bests": n, "P-801-final60": n}}))


def _all_complete(repo, conds=ALL):
    head = _git(repo, "rev-parse", "HEAD")
    for c in conds:
        _complete(_out(repo) / f"{c}.json", head)
        if c in SWAPS:
            _complete(_out(repo) / f"{c}-swap.json", head, swap=True)
    (_out(repo) / "cpu-ledger.jsonl").write_text('{"cond": "B0", "swap": false, "cpu_s": 61.5}\n')  # the runs' ledger
    return head


def test_the_lane_wires_the_registered_rung(assay_module):
    text = open(os.path.join(LANES, "lane134b.sh")).read()
    assert f"CPLUS={assay_module.CPLUS_REGISTERED} " in text
    assert set(re.search(r'SWAPS_OF=" ([^"]*) "', text).group(1).split()) == \
        set(assay_module.SENSOR_BLIND_134B) - {"B0"}  # B0's I5-S is cited at MASTER_SEED (trim iv)


@pytest.fixture(scope="module")
def assay_module():
    spec = importlib.util.spec_from_file_location("assay134b_lane", os.path.join(ROOT, "runs", "RBT-134", "assay.py"))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def test_refuses_without_the_go(repo, tmp_path):
    p = _lane(repo, tmp_path, go=False)
    assert p.returncode == 3 and "owner's GO" in p.stderr


def test_the_lane_does_not_take_lane_a_s_go(repo, tmp_path):
    p = _lane(repo, tmp_path, {"RBT134_GO": _git(repo, "rev-parse", "HEAD")}, go=False)
    assert p.returncode == 3  # RBT134_GO (lanes A and B) is not the registered run's GO


@pytest.mark.parametrize("go", ["1", "0" * 40])
def test_refuses_a_go_that_is_not_head(repo, tmp_path, go):
    p = _lane(repo, tmp_path, {"RBT134B_GO": go})
    assert p.returncode == 5 and "not this checkout's HEAD" in p.stderr


def test_refuses_a_dirty_tree(repo, tmp_path):
    (repo / "README").write_text("dirty\n")
    p = _lane(repo, tmp_path)
    assert p.returncode == 4 and "dirty" in p.stderr


def test_refuses_another_mujoco(repo, tmp_path):
    p = _lane(repo, tmp_path, {"RBT134_DRY": "1"}, mujoco="no")
    assert p.returncode == 10 and "3.14.0" in p.stderr and "PLAN" not in p.stdout


def test_refuses_while_the_validation_spend_is_not_registered(repo, tmp_path):
    _set_validation_spent(repo, "None")
    p = _lane(repo, tmp_path, {"RBT134_DRY": "1"})
    assert p.returncode == 11 and "VALIDATION_SPENT_H" in p.stderr and "PLAN" not in p.stdout


def test_mujoco_check(monkeypatch):
    relay = _relay()
    for version, want in (("3.14.0", "ok"), ("3.15.0", "no")):
        monkeypatch.setitem(sys.modules, "mujoco", types.SimpleNamespace(__version__=version))
        assert relay.mujoco_ok() == want


def test_the_plan_follows_design_13(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    _complete(_out(repo) / "B0.json", head)
    (_out(repo) / "A0.json").write_text('{"truncated":')  # incomplete: re-run
    p = _lane(repo, tmp_path, {"RBT134_DRY": "1"}, stub=False)
    assert p.returncode == 0, p.stdout + p.stderr
    plan = p.stdout
    assert "skip B0 (complete)" in plan and "PLAN run B0-swap" not in plan  # B0's I5-S is cited
    order = [m.group(1) for m in re.finditer(r"PLAN run (\S+?):", plan)]
    assert order == ["C+L1", "A0", "A0-swap", "control-gate", "P1", "P1-swap", "P4", "P4-swap", "P5",
                     "P2", "P2-swap", "P3", "P3-swap", "readout", "re-signing-check"] + [f"{c}-resign" for c in ALL if c != "A0"]
    assert "A0-resign" not in plan  # A0 is not re-signed (OWNER-DECISIONS item 8)
    assert "run134b C+L1 --seed 20260912 --go --n 100000 --n-bg 20000" in plan
    assert "run134b P2 --seed 20260912 --go --swap" in plan
    assert "resign134b P3 --go --cap 400" in plan
    assert "PLAN control gate" in plan


@pytest.mark.parametrize("bad", ["foreign", "nohead", "wrongcond", "wrongfields", "wrongbg", "wrongseed", "notswap"])
def test_refuses_or_reruns_a_json_that_is_not_this_conditions_at_head(repo, tmp_path, bad):
    head = _git(repo, "rev-parse", "HEAD")
    target = _out(repo) / ("A0-swap.json" if bad == "notswap" else "B0.json")
    _complete(target, head, swap=(bad == "notswap"))
    r = json.loads(target.read_text())
    if bad == "foreign":
        r["git"] = "0" * 40
    elif bad == "nohead":
        del r["git"]
    elif bad == "wrongcond":
        r["condition"] = "P2"
    elif bad == "wrongfields":
        r["fields"] = {"link_sigma": 4.0}
    elif bad == "wrongbg":
        r["n_bg_per_pool"] = 5_000
    elif bad == "wrongseed":
        r["master_seed"] = 20261101
    else:
        r["swap"] = False
    target.write_text(json.dumps(r))
    p = _lane(repo, tmp_path, {"RBT134_DRY": "1"}, stub=False)
    if bad in ("foreign", "nohead"):
        assert p.returncode == 5 and "not written at this head" in p.stderr
    else:
        name = "A0-swap" if bad == "notswap" else "B0"
        assert p.returncode == 0 and f"PLAN run {name}:" in p.stdout  # not this registered output: re-run


def test_refuses_a_resign_text_not_from_this_head(repo, tmp_path):
    out = _out(repo)
    out.mkdir(parents=True)
    (out / "P2-resign.txt").write_text("x\n")
    (out / "P2-resign.txt.head").write_text("0" * 40 + "\n")
    p = _lane(repo, tmp_path, {"RBT134_DRY": "1"}, stub=False)
    assert p.returncode == 5 and "not completed at this head" in p.stderr


def _console_outside_relay(p):
    text = p.stdout + p.stderr
    head, _, rest = text.partition("===== RELAY")
    return head + rest.partition("===== END RELAY =====")[2]


def test_a_stubbed_lane_runs_in_order_and_its_console_carries_no_numbers(repo, tmp_path):
    head = _all_complete(repo)
    p = _lane(repo, tmp_path)
    assert p.returncode == 0, p.stdout + p.stderr
    console = _console_outside_relay(p)
    assert "run control-gate" in console and "run re-signing" in console
    assert "-resign" not in console  # which condition is being re-signed is never shown (OWNER-DECISIONS item 10)
    fixed = console
    for name in ("RBT134_NO_PUSH=1", "RBT-134b", "RBT-134", "rbt134b", "134b"):  # fixed names, not results
        fixed = fixed.replace(name, "")
    assert not re.search(r"\d", IDS.sub("", fixed)), console
    assert "MOVES" not in p.stdout + p.stderr and "12345" not in p.stdout + p.stderr
    log = (_out(repo) / "lane-134b.log").read_text()
    assert "12345" in log and "MOVES" in log
    assert (_out(repo) / "P3-resign.txt.head").read_text().strip() == head
    block = p.stdout.partition("===== RELAY")[2]
    assert f"head {head}" in block and "NOT COMMITTED" in block and "status done" in block and "VOID none" in block
    assert [m.group(1) for m in re.finditer(r"TIME (\S+) ", block)] == ["controls", "gate", "checks-and-family", "readout"]


def test_the_lane_stops_at_the_control_gate(repo, tmp_path):
    _all_complete(repo, CONTROLS)
    p = _lane(repo, tmp_path, {"STUB_VOID": "- I5-S A0"})
    assert p.returncode == 8, p.stdout + p.stderr
    assert "STOPPED at the control gate" in p.stdout and "run P1" not in p.stdout
    block = p.stdout.partition("===== RELAY")[2]
    assert "status stopped-at-control-gate" in block and "VOID I5-S A0" in block
    assert not (_out(repo) / "readout.txt").exists()


def test_a_stop_cost_stops_the_lane_cleanly(repo, tmp_path):
    _all_complete(repo, CONTROLS)
    p = _lane(repo, tmp_path, {"STUB_STOP": "P4"})
    assert p.returncode == 9, p.stdout + p.stderr
    assert "STOPPED: STOP-COST at P4" in p.stdout and "run P2" not in p.stdout and "run readout" not in p.stdout
    assert "38.3" not in p.stdout + p.stderr  # the stop's figures stay in the log
    block = p.stdout.partition("===== RELAY")[2]
    assert "status stopped-cost" in block and "TOKENS (readout-controls.txt)" in block


def test_a_crashing_gate_fails_closed(repo, tmp_path):
    _all_complete(repo, CONTROLS)
    p = _lane(repo, tmp_path, crash="gate")
    assert p.returncode == 6 and "FAILED: relay.py check (control-gate)" in p.stderr, p.stdout + p.stderr
    assert "run P1" not in p.stdout


@pytest.mark.parametrize("query", ["complete-run", "mujoco-ok"])
def test_a_crashing_check_fails_closed(repo, tmp_path, query):
    _all_complete(repo, ("B0",))
    py = tmp_path / "python-crash"
    py.write_text(f'#!/bin/bash\nif [[ "$2" == {query} ]]; then exit 1; fi\n'
                  f'if [[ "$2" == mujoco-ok ]]; then echo ok; exit 0; fi\nexec {sys.executable} "$@"\n')
    py.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("RBT134_", "RBT134B_"))}
    env.update({"PYTHON": str(py), "RBT134_NO_PUSH": "1", "RBT134_DRY": "1",
                "RBT134B_GO": _git(repo, "rev-parse", "HEAD")})
    p = subprocess.run(["bash", str(repo / "runs" / "RBT-134" / "lanes" / "lane134b.sh")],
                       capture_output=True, text=True, env=env, timeout=300)
    assert p.returncode == 6 and "FAILED: relay.py check" in p.stderr, p.stdout + p.stderr
    assert "PLAN run B0" not in p.stdout


SYNTHETIC = """# RBT-134b readout, seed 20260912 (registered)

| condition | lineages | arrivals | k a32 | sham | planted | remnants (ever, not final) | bg never-structured (134b) | bg structureless at 19 (r3, descriptive) | remnant share over B0's / flag threshold (4.6) | pair events (refused / no pair) |
| B0 | 200000 | 84 | 0 | 61 | 0 | 12 | 88/39950 | 88/39960 | +0.00000 / 0.00220 | 0 (0 / 0) |
| P2 | 200000 | 66 | 17 | 70 | 0 | 140 | 300/39800 | 412/39871 | +0.00300 / 0.00220 EXCLUSION-FLAG | 0 (0 / 0) |

## Controls

I2 B0: arrival set equals RBT-91-alone-baseline.txt's 84: YES; responses line for line: YES
I2 P2: arrival set equals RBT-91-alone-4.0.txt's 66: NO
I3 P2: slope-bound violations 2; k a32 17 <= 29: YES
B0 r3 background, first 5,000 per pool, all: 26 of 9996 (registered 26 of 9996): YES
B0 r3 background, first 5,000 per pool, unflagged: 22 of 9990 (registered 22 of 9990): YES
I9 C+L1: never-structured background remnant-proof: YES
I9 P5: never-structured background remnant-proof: NO
  - planted lineage W4b-801-bests #1234 never carried the structure
I5-S B0: cited, the RBT-134 diagnosis's swap on B0 at MASTER_SEED: EXACT (the same lineages: I2 B0 above): YES
I5-S P2: swapped food set = sham set and swapped sham set = food set: YES
U2 (descriptive, a property of the parents): B0 food-only 30, sham-only 7, two-sided exact p 0.0001
I4b C+L1: k a32 61, discordant 61 up / 0 down, p = 4.337e-19; never-structured background 88/39950 vs B0 88/39950, ratio upper bound 1.285: PASS

## The family (Holm, m = 2; DESIGN.md 4, 6; background: DESIGN-134b.md 4.1)

P2: discordant 17 up / 0 down, p = 7.629e-06 against alpha 0.0250; background 300/39800 vs B0 88/39950, ratio upper bound 4.100  ->  **MOVES-WITH-BACKGROUND** with EXCLUSION-FLAG  (descriptive, r3's measure: ratio upper bound 5.300, fails)

## VOID

- I2 P2: arrival set equals RBT-91-alone-4.0.txt's 66: NO
- I9 P5
- I4 C+
- P2: predicate mismatch on 12 lineages
- something unforeseen with 12345 in it
"""


def test_relay_carries_no_numbers(tmp_path, capsys):
    relay = _relay()
    out = tmp_path / f"134b-{SEED}"
    out.mkdir()
    (out / "readout.txt").write_text(SYNTHETIC)
    (out / "P2.json").write_text("{}")
    (out / "cpu-ledger.jsonl").write_text('{"cpu_s": 61.5}\n')
    relay.relay(str(out), "f" * 40, "no", "done", ["controls:12345:98765"])
    block = capsys.readouterr().out
    tokens = block.split("TOKENS", 1)[1].split("SHA256", 1)[0]
    stripped = IDS.sub("", tokens)
    assert not re.search(r"\d", stripped), stripped
    assert "I2 B0: YES YES" in tokens and "I2 P2: NO" in tokens and "I3 P2: YES" in tokens
    assert "I9 C+L1: YES" in tokens and "I9 P5: NO" in tokens and "I5-S B0: YES" in tokens and "I5-S P2: YES" in tokens
    assert "B0-background-prefix all: YES" in tokens and "B0-background-prefix unflagged: YES" in tokens
    assert "VOID I2 P2, I9 P5, I4 C+, predicate-mismatch P2, OTHER" in tokens
    for leaked in ("MOVES", "PASS", "EXCLUSION", "U2", "I4b", "1234", "61", "Katz", "ratio"):
        assert leaked not in tokens, leaked
    rest = block.split("SHA256", 1)[1]
    for line in rest.strip().splitlines():
        assert re.fullmatch(r"\s*[0-9a-f]{64}  runs/RBT-134/out/134b-20260912/\S+|TIME [a-z-]+ wall_h=\d+ cpu_h=\d+|"
                            r"===== END RELAY =====|", line), line
    assert "cpu-ledger.jsonl" in rest and "TIME controls wall_h=3 cpu_h=27" in rest


def test_gate(tmp_path):
    relay = _relay()
    p = tmp_path / "r.txt"
    assert relay.gate(str(p)) == "STOP"
    p.write_text("## Controls\n\n## VOID\n\nnone\n")
    assert relay.gate(str(p)) == "PASS"
    p.write_text("## VOID\n\n- I5-S A0\n")
    assert relay.gate(str(p)) == "STOP"
    p.write_text("## Controls\n")
    assert relay.gate(str(p)) == "STOP"


def test_completeness(tmp_path):
    relay = _relay()
    p = tmp_path / "P3.json"
    assert relay.complete(str(p), "h", 10, 4, False) == "incomplete"
    _complete(p, "h", n=10, n_bg=4)
    assert relay.complete(str(p), "h", 10, 4, False) == "complete"
    assert relay.complete(str(p), "other", 10, 4, False) == "stale"
    assert relay.complete(str(p), "h", 10, 5, False) == "incomplete"
    assert relay.complete(str(p), "h", 10, 4, True) == "incomplete"  # not a swap file
    q = tmp_path / "P3-swap.json"
    _complete(q, "h", swap=True, n=10, n_bg=4)
    assert relay.complete(str(q), "h", 10, 4, True) == "complete"
    assert relay.complete(str(q), "h", 10, 4, False) == "incomplete"
    r = json.loads(q.read_text())
    q.write_text(json.dumps({**r, "master_seed": 20261101}))
    assert relay.complete(str(q), "h", 10, 4, True) == "incomplete"


def test_a_stop_at_re_signing_names_the_stage_only(repo, tmp_path):
    """OWNER-DECISIONS item 10: a STOP-COST during re-signing shows the stage "re-signing", never a condition."""
    _all_complete(repo)
    p = _lane(repo, tmp_path, {"STUB_STOP": "re-signing"})
    assert p.returncode == 9, p.stdout + p.stderr
    assert "STOPPED: STOP-COST at re-signing" in p.stdout
    console = _console_outside_relay(p)
    assert "-resign" not in console and "re-signing-check" not in console
    after = console.partition("run re-signing")[2]
    assert not re.search(r"\b(B0|C\+L1|A0|P[1-5])\b", after), after
    block = p.stdout.partition("===== RELAY")[2]
    assert "status stopped-cost" in block and not list((_out(repo)).glob("*-resign.txt"))


def test_a_stopped_relay_withholds_the_re_signing_outputs(repo, tmp_path):
    """#580 round 4 MINOR: after a stop with two conditions re-signed (B0, C+L1; the stop at the third), the RELAY
    block names no re-signing output (no "-resign" anywhere), and says only that they are withheld; the files are
    kept for the commit."""
    _all_complete(repo)
    p = _lane(repo, tmp_path, {"STUB_STOP_RESIGN": "P1"})
    assert p.returncode == 9, p.stdout + p.stderr
    assert (_out(repo) / "B0-resign.txt").exists() and (_out(repo) / "C+L1-resign.txt").exists()
    block = p.stdout.partition("===== RELAY")[2].partition("===== END RELAY =====")[0]
    assert "-resign" not in block and "status stopped-cost" in block
    assert "re-signing outputs: withheld (stopped)" in block
    assert "STOPPED: STOP-COST at re-signing" in p.stdout and "-resign" not in _console_outside_relay(p)


def test_a_done_relay_lists_the_re_signing_outputs(tmp_path, capsys):
    relay = _relay()
    out = tmp_path / f"134b-{SEED}"
    out.mkdir()
    (out / "readout.txt").write_text("## VOID\n\nnone\n")
    (out / "P2-resign.txt").write_text("x\n")
    relay.relay(str(out), "f" * 40, "no", "done")
    block = capsys.readouterr().out
    assert "P2-resign.txt" in block and "withheld" not in block
    relay.relay(str(out), "f" * 40, "no", "stopped-cost")
    block = capsys.readouterr().out
    assert "-resign" not in block and "re-signing outputs: withheld (stopped)" in block
