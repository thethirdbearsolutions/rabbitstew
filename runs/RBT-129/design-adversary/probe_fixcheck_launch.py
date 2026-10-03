"""RBT-129 launch FIX-CHECK probe: PR #435 at 1155e33, trial-merged on integration 4c32cec.

Builds configs; runs only the tests' tiny non-sweep world (TINY, 2-3 seasons); no sweep arm, cell or founder.
python3 probe_fixcheck_launch.py <trial-merged tree>
"""
import json
import os
import subprocess
import sys
import tempfile
import time

T = sys.argv[1]
sys.path[:0] = [T, os.path.join(T, "runs/RBT-129/launch")]
import blocks  # noqa: E402
import stages  # noqa: E402
from rabbitstew import fair as fair_mod  # noqa: E402

EAT_CAND = ["--eat-from", "root"]
EAT_RULED = ["--eat-from", "root", "--eat-rule", "surface"]


def attempt(f, *a):
    try:
        f(*a)
        return "accepted"
    except SystemExit as e:
        return f"refused ({e.code if isinstance(e.code, int) else 'exit'})"


print("## L1: check_fair")
for fair in ([], ["--fair"], ["--unfair-i-know"], ["--fair", "--unfair-i-know"], ["--motor-budget", "1.77"], ["--sweep-log"], ["fair"]):
    print(f"   {str(fair):32s} {attempt(stages.check_fair, fair)}")
print("## L1: check_block (fair.check + the marker + every preset value)")
print(f"   preset: {[d for d, _, _ in fair_mod.PRESET]}")
for fair in (["--fair"], ["--unfair-i-know"]):
    try:
        b = blocks.block("c1-p030-PW-G", fair=fair, eat=EAT_CAND)
        print(f"   block fair={fair}: {attempt(stages.check_block, b)}")
    except SystemExit as e:
        print(f"   block fair={fair}: build refused ({e.code})")
b = blocks.block("c1-p030-PW-G", fair=["--fair"], eat=EAT_CAND)["block"]
print("   --fair block values: " + str({k: v for k, v in b.items() if k == "fairness" or k.split(".")[-1] in [d for d, _, _ in fair_mod.PRESET]}))

print("\n## the eating rule re-ruled 03:10 to root + surface")
print(f"   blocks.EAT_CANDIDATE = {blocks.EAT_CANDIDATE}")
for eat in (EAT_CAND, EAT_RULED, ["--eat-from", "root", "--eat-rule", "surface", "--clear-from", "geoms"]):
    print(f"   check_eat({' '.join(eat)}): {attempt(stages.check_eat, eat)}")
bs = blocks.config_dict(blocks.world_argv("c1-p030-U-L", fair=["--fair"], eat=EAT_RULED))["sim"]["food"]
print(f"   a block built with the ruled rule has food.eat_from={bs.get('eat_from')!r}, eat_rule={bs.get('eat_rule')!r}, clear_from={bs.get('clear_from', 'root (default, absent)')!r}")
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402
from rabbitstew.fixed import drive_straight_genotype  # noqa: E402
import rabbitstew.simulation as simmod  # noqa: E402
cfg = SimConfig.from_dict(blocks.config_dict(blocks.world_argv("c1-p030-U-L", fair=["--fair"], eat=EAT_RULED))["sim"])
sim = Simulation([drive_straight_genotype(0.6)], cfg, spawns=spawn_layout(1, cfg, 0))
cp = sim._clearance_points()
print(f"   under root + surface (clear_from root), _clearance_points() measures from "
      f"{'every geom surface (the fix)' if cp is simmod._SURFACE_CLEAR else 'the root centre only (the leak RBT-125 BC MUST 2 names)'}")

print("\n## L3: the CLI under --fair, resume and the guard (tiny world)")
TINY = ["--capacity", "4", "--challenge", "foraging", "--group-size", "2", "--brain-model", "foraging", "--food-items", "4",
        "--duration", "0.4", "--terrain", "flat", "--conventional-topology", "--score", "food", "--living-cost", "0.05",
        "--initial-energy", "2", "--birth-threshold", "0.5", "--birth-cost", "0.2", "--max-age", "6"]
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
env["PYTHONPATH"] = T
cli = [sys.executable, "-m", "rabbitstew.cli", "ecology"]
with tempfile.TemporaryDirectory() as t:
    r = subprocess.run(cli + TINY + ["--fair", "--seed", "3", "--seasons", "2", "--workers", "1", "--out", f"{t}/S"], cwd=T, env=env, capture_output=True, text=True)
    c = json.load(open(f"{t}/S/config.json"))
    print(f"   fresh --fair: exit {r.returncode}; fair.check(config) = {fair_mod.check(c)}; fairness {c.get('fairness')!r}")
    r = subprocess.run(cli + ["--resume", "--seasons", "3", "--out", f"{t}/S"], cwd=T, env=env, capture_output=True, text=True)
    print(f"   --resume without flags: exit {r.returncode} {r.stderr.strip()[-100:]}")
    r = subprocess.run(cli + TINY + ["--seed", "3", "--seasons", "2", "--workers", "1", "--out", f"{t}/X"], cwd=T, env=env, capture_output=True, text=True)
    print(f"   fresh, no fairness flag: exit {r.returncode} ({'refused by the guard' if r.returncode else 'RAN'})")

print("\n## L4: a long job's durable loop, against a local bare remote (tiny world, 3 seasons)")
with tempfile.TemporaryDirectory() as t:
    subprocess.run(["git", "init", "-q", "--bare", f"{t}/bare.git"])
    os.environ["DURABLE_REMOTE"] = f"{t}/bare.git"
    os.environ.pop("NO_DURABLE", None)
    d = os.path.join(t, "run")
    os.makedirs(d)
    t0 = time.time()
    stages._ecology([*TINY, "--fair", "--seed", "4", "--seasons", "3"], d, "rbt-129-fixcheck-probe", long=True)
    print(f"   _ecology(long=True) returned after {time.time() - t0:.1f} s (the run itself is seconds; r1 waited 20 min)")

print("\n## S11: pays hands steps.py a config.json it parses, with fairness 'fair'")
with tempfile.TemporaryDirectory() as t:
    dirs = stages.world_config_dirs(t, ["c1-p030-PW-G"], ["--fair"], EAT_CAND)
    p = os.path.join(dirs["c1-p030-PW-G"], "config.json")
    raw = json.load(open(p))
    SimConfig.from_dict(raw["sim"])
    print(f"   {os.path.relpath(p, t)}: SimConfig parses; fairness {raw.get('fairness')!r}; fair.check {fair_mod.check(raw)}")
    jobs = stages.pays_jobs(t, "steer {config_json}", "python steps.py H {point} --config {config_json}")
    print(f"   a pays job: {jobs[1].replace(t, '<root>')}")
