"""RBT-134 lanes (runs/RBT-134/lanes/, LAUNCH.md): the sha-bound GO, the clean-tree and untracked-file refusals, the
restart skips and stale-output refusals, the console that carries no sub-command output, the control gate, and a RELAY
block that carries no numbers.  Nothing registered runs: every lane here is refused, in RBT134_DRY=1 plan mode, or
driven by a stub interpreter that only prints noise and writes placeholder files, inside a throwaway git repository
(runs/RBT-134 copied, every other runs/ directory symlinked).
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

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
    """A throwaway clean git repo: runs/RBT-134's scripts copied (the working tree's), every other runs/ directory a
    symlink to this checkout's, so imports resolve but nothing under the real runs/RBT-134/out/ is touched."""
    r = tmp_path / "repo"
    shutil.copytree(os.path.join(ROOT, "runs", "RBT-134"), r / "runs" / "RBT-134",
                    ignore=shutil.ignore_patterns("out", "__pycache__", "*.pyc"))
    for d in os.listdir(os.path.join(ROOT, "runs")):
        if d != "RBT-134" and os.path.isdir(os.path.join(ROOT, "runs", d)):
            os.symlink(os.path.join(ROOT, "runs", d), r / "runs" / d)
    shutil.copy(os.path.join(ROOT, ".gitignore"), r / ".gitignore")
    (r / "README").write_text("x\n")
    _git(r, "init", "-q")
    _git(r, "add", "-A")
    _git(r, "add", "-f", "runs/RBT-134")
    _git(r, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
    return r


def _lane(repo, lane, env_extra, *args, go=True, python=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("RBT134_")}
    env.update({"PYTHON": python or sys.executable, "RBT134_NO_PUSH": "1"})
    if go:
        env["RBT134_GO"] = _git(repo, "rev-parse", "HEAD")
    env.update(env_extra)
    return subprocess.run(["bash", str(repo / "runs" / "RBT-134" / "lanes" / f"lane{lane}.sh")] + list(args),
                          capture_output=True, text=True, env=env, timeout=300)


@pytest.mark.parametrize("lane", ["A", "B"])
def test_refuses_without_the_go(repo, lane):
    p = _lane(repo, lane, {}, go=False)
    assert p.returncode == 3 and "refused" in p.stderr


@pytest.mark.parametrize("lane", ["A", "B"])
@pytest.mark.parametrize("go", ["1", "0" * 40])
def test_refuses_a_go_that_is_not_head(repo, lane, go):
    p = _lane(repo, lane, {"RBT134_GO": go})
    assert p.returncode == 5 and "not this checkout's HEAD" in p.stderr


@pytest.mark.parametrize("lane", ["A", "B"])
def test_refuses_a_dirty_tree(repo, lane):
    (repo / "README").write_text("dirty\n")
    p = _lane(repo, lane, {})
    assert p.returncode == 4 and "dirty" in p.stderr


def test_refuses_an_untracked_file_outside_out(repo):
    (repo / "runs" / "RBT-134" / "numpy.py").write_text("raise SystemExit\n")  # would shadow an import
    p = _lane(repo, "A", {"RBT134_DRY": "1"})
    assert p.returncode == 4 and "untracked" in p.stderr
    os.remove(repo / "runs" / "RBT-134" / "numpy.py")
    (repo / "runs" / "RBT-134" / "out").mkdir()
    (repo / "runs" / "RBT-134" / "out" / "anything.txt").write_text("x\n")  # out/ is the lanes' own
    p = _lane(repo, "A", {"RBT134_DRY": "1"})
    assert p.returncode == 0, p.stderr


def _complete_json(path, head, n=100_000, n_bg=20_000):
    cond = os.path.basename(path)[:-5]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"condition": cond, "fields": _relay()._conditions()[cond], "n_per_pool": n,
                                "n_bg_per_pool": n_bg, "git": head, "pools": {"W4b-801-bests": n, "P-801-final60": n}}))


def _done_text(path, head):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("done\n")
    (path.parent / (path.name + ".head")).write_text(head + "\n")


def test_lane_a_skips_complete_outputs_and_plans_the_rest(repo):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    _complete_json(out / "B0.json", head)
    _complete_json(out / "C+.json", head)
    (out / "A0.json").write_text('{"truncated":')  # incomplete: re-run
    _done_text(out / "B0-resign.txt", head)
    p = _lane(repo, "A", {"RBT134_DRY": "1"})
    assert p.returncode == 0, p.stderr
    plan = p.stdout
    assert "skip B0 (complete)" in plan and "skip C+ (complete)" in plan
    assert "PLAN run A0:" in plan and "PLAN run P2:" in plan and "PLAN run P3:" in plan
    assert "skip B0-resign (complete)" in plan and "PLAN run C+-resign:" in plan
    order = [m.group(1) for m in re.finditer(r"PLAN run (\S+?):", plan)]
    assert order[:7] == ["A0", "control-gate", "P1", "P4", "P5", "P2", "P3"]  # controls, the gate, checks, P2 then P3
    assert "PLAN control gate" in plan


@pytest.mark.parametrize("bad", ["foreign", "nohead", "wrongcond", "wrongfields", "wrongbg"])
def test_lane_a_refuses_or_reruns_a_json_that_is_not_this_conditions_at_head(repo, bad):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    _complete_json(out / "B0.json", head)
    r = json.loads((out / "B0.json").read_text())
    if bad == "foreign":
        r["git"] = "0" * 40
    elif bad == "nohead":
        del r["git"]
    elif bad == "wrongcond":
        r["condition"] = "P2"
    elif bad == "wrongfields":
        r["fields"] = {"link_sigma": 4.0}
    else:
        r["n_bg_per_pool"] = 5_000
    (out / "B0.json").write_text(json.dumps(r))
    p = _lane(repo, "A", {"RBT134_DRY": "1"})
    if bad in ("foreign", "nohead"):
        assert p.returncode == 5 and "not written at this head" in p.stderr
    else:
        assert p.returncode == 0 and "PLAN run B0:" in p.stdout  # not this condition's registered run: re-run


@pytest.mark.parametrize("bad", ["foreign", "nohead"])
def test_lane_a_refuses_a_resign_text_not_from_this_head(repo, bad):
    out = repo / "runs" / "RBT-134" / "out"
    _done_text(out / "P2-resign.txt", "0" * 40)
    if bad == "nohead":
        os.remove(out / "P2-resign.txt.head")
    p = _lane(repo, "A", {"RBT134_DRY": "1"})
    assert p.returncode == 5 and "not completed at this head" in p.stderr


@pytest.mark.parametrize("bad", [None, "foreign", "nohead"])
def test_lane_b_skips_only_text_outputs_marked_with_this_head(repo, tmp_path, bad):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    _done_text(out / "e1.txt", head)
    _done_text(out / "e2-B0-801.txt", head)
    (out / "h1-B0.json").write_text(json.dumps({"condition": "B0", "n_per_pool": 100_000, "git": head,
                                                "pools": {"a": 100_000, "b": 100_000}, "rows": []}))
    (out / "h1-A0.json").write_text(json.dumps({"condition": "B0", "n_per_pool": 100_000, "git": head,  # mislabelled
                                                "pools": {"a": 100_000, "b": 100_000}, "rows": []}))
    if bad == "foreign":
        (out / "e2-P3-4.txt").write_text("x\n")
        (out / "e2-P3-4.txt.head").write_text("0" * 40 + "\n")
    elif bad == "nohead":
        (out / "e2-P3-4.txt").write_text("x\n")
    p = _lane(repo, "B", {"RBT134_DRY": "1"}, str(tmp_path / "founders"))
    if bad:
        assert p.returncode == 5 and "e2-P3-4.txt was not completed at this head" in p.stderr
        return
    assert p.returncode == 0, p.stderr
    assert "skip e1 (complete)" in p.stdout and "skip e2-B0-801 (complete)" in p.stdout
    assert "skip h1-B0 (complete)" in p.stdout and "PLAN run h1-A0:" in p.stdout
    assert "PLAN run e2-P5-7:" in p.stdout and "PLAN run founders-801:" in p.stdout


def test_founders_reused_only_when_digest_and_files_match(tmp_path):
    relay = _relay()
    d = tmp_path / "founders-w32-801"
    assert relay.founders_ok(str(d), 801) == "no"  # absent
    (d / "conventional").mkdir(parents=True)
    (d / "conventional" / "000.json").write_text("{}")
    import hashlib
    h = hashlib.sha256(b"{}").hexdigest()
    (d / "SHA256SUMS").write_text(f"{h}  conventional/000.json\n")
    assert relay.founders_ok(str(d), 801) == "no"  # self-consistent but not RBT-106's committed digest
    real = subprocess.run([sys.executable, os.path.join(ROOT, "runs", "RBT-106", "founders.py"), "801", "32",
                           str(tmp_path / "real")], capture_output=True, text=True)
    assert real.returncode == 0, real.stderr
    assert relay.founders_ok(str(tmp_path / "real"), 801) == "ok"
    assert relay.founders_ok(str(tmp_path / "real"), 804) == "no"  # another seed's digest
    victim = sorted((tmp_path / "real" / "conventional").iterdir())[0]
    victim.write_text(victim.read_text() + " ")  # partial or edited founder under an intact SHA256SUMS
    assert relay.founders_ok(str(tmp_path / "real"), 801) == "no"


STUB = """
import os, sys
print("k a32 = 17, p = 7.6e-06, 412/39871 MOVES-WITH-BACKGROUND")
print("debug 12345 arrivals 84", file=sys.stderr)
args = sys.argv[1:]
out = os.path.join(os.getcwd(), "runs", "RBT-134", "out")
if args[0].endswith("assay.py") and args[1] == "readout":
    print("## VOID\\n")
    print(os.environ.get("STUB_VOID", "none"))
elif args[0].endswith("assay.py") and args[1] == "resign":
    with open(os.path.join(out, args[2] + "-resign.txt.tmp"), "w") as f:
        f.write("compasses 3, anti 1\\n")
    os.replace(os.path.join(out, args[2] + "-resign.txt.tmp"), os.path.join(out, args[2] + "-resign.txt"))
"""


def _stub(tmp_path):
    """An interpreter that runs relay.py for real and replaces every other sub-command with noise (digits on stdout
    and stderr) and placeholder outputs."""
    (tmp_path / "stub.py").write_text(textwrap.dedent(STUB))
    py = tmp_path / "python-stub"
    py.write_text(f'#!/bin/bash\ncase "$1" in *relay.py) exec {sys.executable} "$@" ;; esac\n'
                  f'exec {sys.executable} {tmp_path / "stub.py"} "$@"\n')
    py.chmod(0o755)
    return str(py)


def _console_outside_relay(p):
    text = p.stdout + p.stderr
    head, _, rest = text.partition("===== RELAY")
    tail = rest.partition("===== END RELAY =====")[2]
    return head + tail


def test_a_stubbed_lane_a_console_carries_no_sub_command_output(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    for c in ("B0", "C+", "A0", "P1", "P4", "P5", "P2", "P3"):
        _complete_json(out / f"{c}.json", head)
    p = _lane(repo, "A", {}, python=_stub(tmp_path))
    assert p.returncode == 0, p.stdout + p.stderr
    console = _console_outside_relay(p)
    assert "run control-gate" in console and "run P3-resign" in console
    fixed = console
    for name in ("RBT134_NO_PUSH=1", "RBT-134", "rbt134"):  # fixed names, not results
        fixed = fixed.replace(name, "")
    assert not re.search(r"\d", IDS.sub("", fixed)), console
    assert "MOVES" not in p.stdout + p.stderr and "12345" not in p.stdout + p.stderr
    log = (out / "lane-A.log").read_text()
    assert "12345" in log and "MOVES" in log  # step stdout and stderr, and to_file stderr, go to the log
    assert "MOVES" in (out / "readout.txt").read_text()  # to_file stdout goes to its file
    assert (out / "P3-resign.txt.head").read_text().strip() == head
    block = p.stdout.partition("===== RELAY")[2]
    assert f"head {head}" in block and "NOT COMMITTED" in block and "status done" in block
    assert re.search(r"TIME readout wall_h=0 cpu_h=0", block)
    assert "TIME resign" not in block and not re.search(r"TIME \S*resign", block)  # re-signing is untimed (#565 nit a)
    assert [m.group(1) for m in re.finditer(r"TIME (\S+) ", block)] == ["controls", "gate", "checks-and-family", "readout"]


def test_lane_a_stops_at_the_control_gate(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    for c in ("B0", "C+", "A0"):
        _complete_json(out / f"{c}.json", head)
    p = _lane(repo, "A", {"STUB_VOID": "- I5 C+"}, python=_stub(tmp_path))
    assert p.returncode == 8, p.stdout + p.stderr
    assert "STOPPED at the control gate" in p.stdout and "run P1" not in p.stdout
    block = p.stdout.partition("===== RELAY")[2]
    assert "status stopped-at-control-gate" in block and "VOID I5 C+" in block
    assert not (out / "readout.txt").exists()


def test_commit_refuses_a_missing_output(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    for c in ("B0", "C+", "A0", "P1", "P4", "P5", "P2", "P3"):
        _complete_json(out / f"{c}.json", head)
    stub = _stub(tmp_path)
    (tmp_path / "stub.py").write_text(textwrap.dedent(STUB).replace('args[1] == "resign"', 'args[1] == "resign-never"'))
    p = _lane(repo, "A", {}, python=stub)
    assert p.returncode == 7 and "missing" in p.stderr


def _crashing_relay(tmp_path, query, behaviour):
    """An interpreter that runs relay.py for real except QUERY, which crashes (exit 1) or answers garbage."""
    py = tmp_path / "python-crash"
    act = "exit 1" if behaviour == "crash" else "echo maybe; exit 0" if behaviour == "garbage" else "exit 0"
    py.write_text(f'#!/bin/bash\nif [[ "$1" == *relay.py && "$2" == {query} ]]; then {act}; fi\n'
                  f'exec {sys.executable} "$@"\n')
    py.chmod(0o755)
    return str(py)


@pytest.mark.parametrize("behaviour", ["crash", "garbage", "silent"])
def test_a_crashing_completeness_check_fails_closed(repo, tmp_path, behaviour):
    head = _git(repo, "rev-parse", "HEAD")
    _complete_json(repo / "runs" / "RBT-134" / "out" / "B0.json", head)
    p = _lane(repo, "A", {"RBT134_DRY": "1"}, python=_crashing_relay(tmp_path, "complete-assay", behaviour))
    assert p.returncode == 6 and "FAILED: relay.py check" in p.stderr, p.stdout + p.stderr  # (#565 nit b)
    assert "PLAN run B0" not in p.stdout  # never read as "incomplete" -> re-run


@pytest.mark.parametrize("query, lane", [("complete-h1", "B"), ("founders-ok", "B")])
def test_other_crashing_checks_fail_closed(repo, tmp_path, query, lane):
    p = _lane(repo, lane, {"RBT134_DRY": "1"}, str(tmp_path / "founders"), python=_crashing_relay(tmp_path, query, "crash"))
    assert p.returncode == 6 and "FAILED: relay.py check" in p.stderr, p.stdout + p.stderr


def test_a_crashing_gate_fails_closed(repo, tmp_path):
    head = _git(repo, "rev-parse", "HEAD")
    out = repo / "runs" / "RBT-134" / "out"
    for c in ("B0", "C+", "A0"):
        _complete_json(out / f"{c}.json", head)
    stub = _stub(tmp_path)
    text = open(stub).read().replace('case "$1" in', 'if [[ "$2" == gate ]]; then exit 1; fi\ncase "$1" in')
    open(stub, "w").write(text)
    p = _lane(repo, "A", {}, python=stub)
    assert p.returncode == 6 and "FAILED: relay.py check (control-gate)" in p.stderr, p.stdout + p.stderr
    assert "run P1" not in p.stdout


def test_cpu_times_counts_children(tmp_path):
    script = tmp_path / "t.sh"
    script.write_text(f'TIMESF=$(mktemp)\nsource <(sed -n "/^cpu_now()/,/^}}/p" {os.path.join(LANES, "common.sh")})\n'
                      f'{sys.executable} -c "x = sum(i * i for i in range(30_000_000))"\ncpu_now\necho "$CPU_NOW"\n')
    p = subprocess.run(["bash", str(script)], capture_output=True, text=True, timeout=120)
    assert int(p.stdout.strip()) >= 1, p.stdout + p.stderr


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
    relay.relay("A", str(out), "f" * 40, "no", "done", ["assay:12345:98765", "resign:1800:5400"])
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
        assert re.fullmatch(r"\s*[0-9a-f]{64}  runs/RBT-134/out/\S+|TIME [a-z-]+ wall_h=\d+ cpu_h=\d+|===== END RELAY =====|", line), line
    assert "TIME assay wall_h=3 cpu_h=27" in rest and "TIME resign wall_h=1 cpu_h=2" in rest  # relay.py rounds any stage
    assert "NOT COMMITTED" in block and f"head {'f' * 40}" in block


def test_relay_lane_b_tokens_are_yes_no(tmp_path, capsys):
    relay = _relay()
    out = tmp_path / "out"
    out.mkdir()
    (out / "e1.txt").write_text("| B0 | holistic | 0.9000 | 1.0% | 1 | 1.00% |\n")
    relay.relay("B", str(out), "f" * 40)
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
    p = tmp_path / "h1-B0.json"
    assert relay.complete(str(p), "h", 10) == "incomplete"
    rec = {"condition": "B0", "n_per_pool": 10, "git": "h", "pools": {"a": 10, "b": 10}}
    p.write_text(json.dumps(rec))
    assert relay.complete(str(p), "h", 10) == "complete"
    assert relay.complete(str(p), "other", 10) == "stale"
    p.write_text(json.dumps({**rec, "pools": {"a": 10, "b": 9}}))
    assert relay.complete(str(p), "h", 10) == "incomplete"
    p.write_text(json.dumps({k: v for k, v in rec.items() if k != "git"}))
    assert relay.complete(str(p), "h", 10) == "stale"  # no head recorded: never accepted
    p.write_text(json.dumps({**rec, "condition": "A0"}))
    assert relay.complete(str(p), "h", 10) == "incomplete"
    q = tmp_path / "P3.json"
    arec = {**rec, "condition": "P3", "n_bg_per_pool": 4, "fields": {"link_sigma": 4.0, "bias_reset_rate": 0.2}}
    q.write_text(json.dumps(arec))
    assert relay.complete(str(q), "h", 10, 4) == "complete"
    assert relay.complete(str(q), "h", 10, 5) == "incomplete"
    q.write_text(json.dumps({**arec, "fields": {"link_sigma": 4.0}}))
    assert relay.complete(str(q), "h", 10, 4) == "incomplete"


def test_gate(tmp_path):
    relay = _relay()
    p = tmp_path / "r.txt"
    assert relay.gate(str(p)) == "STOP"  # missing
    p.write_text("## Controls\n\n## VOID\n\nnone\n")
    assert relay.gate(str(p)) == "PASS"
    p.write_text("## VOID\n\n- I2 B0: arrival set equals x's 84: NO\n")
    assert relay.gate(str(p)) == "STOP"
    p.write_text("## Controls\n")  # no VOID section at all
    assert relay.gate(str(p)) == "STOP"
