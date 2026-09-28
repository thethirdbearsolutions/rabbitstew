"""Launch-adversary probe L5: PR #437's reuse of RBT-125 section B's nose-step harness (runs/RBT-125/gate/steps.py).

Run on a scratch tree = PR #435 + RBT-128 #432 (the conflict resolved as ADVERSARY-LAUNCH L3) + #437's steps.py, with
the integration branch's steps.py beside it as steps_base.py.  No physics bout is run: the Pool is faked as in #437's
own tests (a) and (d), or runs a tiny introspection function (b).
  (a) does every --fair physics value and every RBT-125 smell/eat setting of a Stage 0 block live in "sim"?  and can
      steps.py --config read what stages.py pays hands it (worlds/<id>.json)?
  (b) do fork-Pool children see SEEDS[:], HOST and rp.RUN["cell"] as set in main()?
  (c) routed.unit_indices: refuses hosts that cannot carry the motif; what does it not check?
  (d) with no new flag, is the run (tasks and stdout) identical to the integration branch's steps.py?

python3 probe_launch_harness.py <scratch tree>
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile

import numpy as np

T = sys.argv[1]
sys.path[:0] = [T, os.path.join(T, "runs/RBT-129/launch")]
GATE = os.path.join(T, "runs/RBT-125/gate")
sys.path.insert(0, GATE)
import blocks  # noqa: E402
from rabbitstew.simulation import SimConfig  # noqa: E402


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, f"{p}{k}."))
        else:
            out[f"{p}{k}"] = v
    return out


print("## (a) where the fairness preset and the RBT-125 settings live, in a Stage 0 PAYS cell's config")
for pid in ("c2-p030-PW-G", "c0-p030-HP-L"):
    fair = flat(blocks.config_dict(blocks.world_argv(pid, fair=["--fair"])))
    pend = flat(blocks.config_dict(blocks.world_argv(pid)))
    moved = sorted(k for k in set(fair) | set(pend) if fair.get(k) != pend.get(k))
    outside = [k for k in moved if not k.startswith("sim.")]
    print(f"  {pid}: keys --fair changes: {moved}")
    print(f"     outside 'sim': {outside}")
    smell = {k: v for k, v in fair.items() if any(s in k for s in ("smell", "eat_", "decay", "patch", "regrow"))}
    print(f"     smell/eat keys: {smell}")
    cfg = blocks.config_dict(blocks.world_argv(pid, fair=["--fair"]))
    rt = SimConfig.from_dict(cfg["sim"]).to_dict()
    lost = sorted(k for k in flat(cfg["sim"]) if flat(json.loads(json.dumps(rt))).get(k) != flat(cfg["sim"])[k])
    print(f"     SimConfig.from_dict(sim).to_dict() round trip: {'exact' if not lost else 'LOSES ' + str(lost)}")
    mut = {k: v for k, v in fair.items() if k.startswith("mutation.") and "bias" in k}
    print(f"     mutation bias keys (not in the preset; irrelevant to a fixed-controller bout): {mut}")
with tempfile.TemporaryDirectory() as t:
    blocks.export(t, ["c1-p030-PW-G"], fair=["--fair"])
    w = json.load(open(os.path.join(t, "c1-p030-PW-G.json")))
    print(f"  stages.py pays hands steps.py {{world}} = worlds/<id>.json, whose top-level keys are {sorted(w)}:")
    try:
        SimConfig.from_dict(w["sim"])
        print("     steps.py --config reads it")
    except KeyError as e:
        print(f"     steps.py --config on it: KeyError {e} (it needs a config.json with a 'sim' block)")


def load(name):
    spec = importlib.util.spec_from_file_location(f"probe_{name}", os.path.join(GATE, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def child_view(_):
    m = sys.modules["probe_steps"]
    return os.getpid(), m.SEEDS[:3], len(m.SEEDS), sorted(m.HOST)[:3], type(m.rp.RUN.get("cell")).__name__


print("\n## (b) fork children and module state set in main()")
m = load("steps")
sys.modules["probe_steps"] = m
m.SEEDS[:] = [900 + i for i in range(4)]
m.HOST.update({0: "a", 1: "b"})
m.rp.RUN["cell"] = SimConfig()
from multiprocessing import get_context  # noqa: E402
with get_context("fork").Pool(2) as pool:
    views = pool.map(child_view, range(4))
print(f"  parent pid {os.getpid()}; children: {sorted(set(map(str, views)))}")

print("\n## (c) routed.unit_indices")
from rabbitstew.fixed import pioneer_genotype  # noqa: E402
from rabbitstew.genotype import random_genotype  # noqa: E402
import copy  # noqa: E402
ui = m.rp.routed.unit_indices
cases = {}
cases["Pioneer, evolved layout (food, contact; rich)"] = pioneer_genotype(np.random.default_rng(1), sources=("food", "contact"), rich=True)
cases["Pioneer, default (no food nose)"] = pioneer_genotype(np.random.default_rng(1))
g = copy.deepcopy(cases["Pioneer, evolved layout (food, contact; rich)"])
g.nodes[1].segment.brain.units = [u for u in g.nodes[1].segment.brain.units if getattr(u, "source", None) != "food"]
cases["Pioneer, left wheel's nose removed"] = g
cases["random holistic genotype"] = random_genotype(np.random.default_rng(3))
g = copy.deepcopy(cases["Pioneer, evolved layout (food, contact; rich)"])
seg = g.nodes[0].segment
seg.dims = tuple(1.7 * x for x in seg.dims)
cases["Pioneer layout on a reshaped chassis (not the designed body plan)"] = g
from rabbitstew import fair as fair_mod  # noqa: E402
for label, g in cases.items():
    try:
        r = f"accepted {ui(g)}"
    except Exception as e:
        r = f"REFUSED ({type(e).__name__})"
    print(f"  {label:66s} {r}; fair.is_designed: {fair_mod.is_designed(g)}")

print("\n## (d) the registered defaults: integration's steps.py against #437's, same argv, fake pool")


class Pool:
    seen = []

    def __init__(self, *a):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def map(self, f, tasks, chunksize=1):
        Pool.seen.append(list(tasks))
        rng = np.random.default_rng(0)
        out = []
        for t in tasks:
            if isinstance(t[0], str):
                out.append((t[2], t[4], 0.0, -1.0, 10))
            else:
                h, w, sign, seed, speed = t
                f_ = float(rng.poisson(1 + 0.05 * w + (0.3 if speed else 0)))
                out.append(((h, w, speed), seed, f_, f_ - 0.1, 0.3 * (1.25 if speed else 1.0)))
        return out


with tempfile.TemporaryDirectory() as root:
    for s in (1, 2, 3):
        d = os.path.join(root, "O1", str(s), "U", "conventional", "final")
        os.makedirs(d)
        for i in range(8):
            open(os.path.join(d, f"g{i}.json"), "w").write("{}")
    res = {}
    for name in ("steps_base", "steps"):
        mod = load(name)
        mod.get_context = lambda kind: type("Ctx", (), {"Pool": Pool})
        Pool.seen = []
        sys.argv = ["steps.py", root, "U-G2.5"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mod.main()
        res[name] = (buf.getvalue(), Pool.seen)
    same_out = res["steps_base"][0] == res["steps"][0]
    same_tasks = res["steps_base"][1] == res["steps"][1]
    n = sum(len(x) for x in res["steps"][1])
    print(f"  stdout identical: {same_out}; every task identical: {same_tasks} ({n} tasks, seeds "
          f"{min(t[3] for t in res['steps'][1][1])}..{max(t[3] for t in res['steps'][1][1])})")
