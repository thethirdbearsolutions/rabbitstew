"""Launch-adversary probe L2: can PR #435's guards be bypassed, and does the fairness marker reach the blocks once
RBT-128 (#432) is merged?

Run from a tree: python3 probe_launch_guards.py <tree> [label]
  <tree> is a checkout of PR #435 (4464a4e), or the adversary's scratch merge of #432 into it (the conflict resolved by
  calling fair.expand in ecology_configs and fair.guard in cmd_ecology after the resume branch).
Runs only the tiny non-sweep world of tests/test_rbt129_launch.py (TINY), 2-3 seasons.  No sweep arm or cell.
"""
import json
import os
import subprocess
import sys
import tempfile

TREE = sys.argv[1]
LABEL = sys.argv[2] if len(sys.argv) > 2 else TREE
sys.path[:0] = [TREE, os.path.join(TREE, "runs/RBT-129/launch")]
import blocks  # noqa: E402
import stages  # noqa: E402

print(f"# tree: {LABEL}")
merged = "--fair" in stages.ecology_options()
print(f"# '--fair' is an ecology option here: {merged}; '--unfair-i-know': {'--unfair-i-know' in stages.ecology_options()}")

print("## 1. check_fair (emit, prelaunch and every fresh job) on candidate 'fairness' flag lists")
for fair in ([], ["--fair"], ["--unfair-i-know"], ["--sweep-log"], ["--motor-budget", "1.77"], ["--seed", "7"], ["fair"], ["--fair", "--unfair-i-know"]):
    try:
        stages.check_fair(fair)
        r = "ACCEPTED"
    except SystemExit as e:
        r = f"refused ({e.code if isinstance(e.code, int) else 'exit'})"
    print(f"   {str(fair):32s} {r}")

print("## 2. what reaches a block's config (c1-p030-U-L)")
for fair in (["--fair"], ["--unfair-i-know"], ["--motor-budget", "1.77"]):
    try:
        b = blocks.block("c1-p030-U-L", fair=fair)["block"]
        keys = {k: b.get(k) for k in ("fairness", "sim.synthesis.mass_budget", "sim.world.motor_budget", "sim.world.ball_cone",
                                     "sim.world.hinge_range", "sim.settle_until_rest")}
        print(f"   fair={str(fair):28s} {keys}")
    except SystemExit as e:
        print(f"   fair={str(fair):28s} SystemExit: {str(e)[:120]}")
    except Exception as e:
        print(f"   fair={str(fair):28s} {type(e).__name__}: {str(e)[:120]}")

TINY = ["--capacity", "4", "--challenge", "foraging", "--group-size", "2", "--brain-model", "foraging", "--food-items", "4",
        "--duration", "0.4", "--terrain", "flat", "--conventional-topology", "--score", "food", "--living-cost", "0.05",
        "--initial-energy", "2", "--birth-threshold", "0.5", "--birth-cost", "0.2", "--max-age", "6"]
if merged:
    print("## 3. tiny world under --fair: fresh 2 seasons, then --resume to 3 (must not meet the guard); fork + resume")
    with tempfile.TemporaryDirectory() as t:
        cli = [sys.executable, "-m", "rabbitstew.cli", "ecology"]
        env = {**os.environ, "PYTHONPATH": TREE}
        r1 = subprocess.run(cli + TINY + ["--fair", "--seed", "3", "--seasons", "2", "--workers", "1", "--out", f"{t}/S"], cwd=TREE, env=env, capture_output=True, text=True)
        print(f"   fresh --fair: exit {r1.returncode}")
        cfg = json.load(open(f"{t}/S/config.json"))
        print(f"   config.json fairness={cfg.get('fairness')!r} motor_budget={cfg['sim']['world'].get('motor_budget')}")
        r2 = subprocess.run(cli + ["--resume", "--seasons", "3", "--out", f"{t}/S"], cwd=TREE, env=env, capture_output=True, text=True)
        print(f"   resume (no --fair on the command line): exit {r2.returncode} {r2.stderr.strip()[-120:]}")
        stages.fork_config(f"{t}/S", f"{t}/M", {"merge_after": 2, "pooled_capacity": 8})
        r3 = subprocess.run(cli + ["--resume", "--seasons", "3", "--out", f"{t}/M"], cwd=TREE, env=env, capture_output=True, text=True)
        print(f"   fork (merge set) + resume: exit {r3.returncode} {r3.stderr.strip()[-120:]}")
        r4 = subprocess.run(cli + TINY + ["--seed", "3", "--seasons", "2", "--workers", "1", "--out", f"{t}/X"], cwd=TREE, env=env, capture_output=True, text=True)
        print(f"   fresh with no fairness flag: exit {r4.returncode} ({'refused by the RBT-128 guard' if r4.returncode else 'ran'})")
        # the block path equals what the CLI writes, on the fairness fields
        args = TINY + ["--fair", "--seed", "3", "--seasons", "2"]
        from rabbitstew.cli import build_parser, ecology_configs
        from rabbitstew.ecology import _jsonable
        evo, eco = ecology_configs(build_parser().parse_args(["ecology", *args]))
        d = json.loads(json.dumps({**_jsonable(evo.to_dict()), "ecology": eco.to_dict()}))
        diff = sorted(k for k in set(d) | set(cfg) if k not in ("workers",) and d.get(k) != cfg.get(k))
        print(f"   ecology_configs vs the CLI's config.json, top-level keys differing (workers aside): {diff}")
