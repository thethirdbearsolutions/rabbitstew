"""RBT-133 step 1: where do ARM and x86 part ways?  Physics (MuJoCo), brain (numpy/BLAS), sensors, or the model build?

Subcommands (every output is plain text so that it can be diffed across platforms and committed):

  gen0 [--seed 201]          RBT-96/RBT-85's arena config, generation 0 only: both populations' evaluation bouts.
                             Prints the generations.txt columns (h_best, h_mean, c_best, c_mean) and every bout's
                             fitness as float.hex.  The laptop's row is committed in runs/RBT-85/base-201, the cloud's
                             in runs/RBT-96/s0-201, so this says which of the two a machine reproduces.
  record OUT [--bout K]      Re-run gen-0 bout K of the conventional population (closed loop, native) and write
                             everything needed to localise a divergence: the generated XML, the compiled model (MJB),
                             the state right after the settle, and per control tick the sensors, the brain activations,
                             the ctrl vector, and a sha256 of the physics state after every mj_step.
  compare REF OTHER          First tick at which two `record` outputs differ, and in which quantity.  The order inside
                             a tick is sensors -> brain -> ctrl -> physics, so the first differing quantity names the
                             layer that introduced the difference.
  replay-physics REF         Open loop: load REF's MJB and post-settle state, drive REF's ctrl sequence through native
                             MuJoCo, and compare the per-step state hashes to REF's.  Also compiles REF's XML locally
                             and compares the model to REF's MJB.  Isolates MuJoCo from everything in Python.
  replay-brain REF           Feed REF's recorded sensor readings to RuntimeBrain and compare activations bit for bit.
                             Isolates the brain (numpy/BLAS) from physics and sensors.
  numpy-probe                Bit hashes of the numpy and libm primitives the brain and sensors use, on fixed inputs.

Nothing here changes the package: it wraps mujoco.mj_step through a proxy module object for the simulation module only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import types

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import mujoco  # noqa: E402

from rabbitstew import simulation, world  # noqa: E402
from rabbitstew.brain import RuntimeBrain  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, TERRAIN, EvolutionConfig, draw_start_seeds, draw_terrain_seed, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

CONFIG = os.path.join(ROOT, "runs", "RBT-96", "s0-201", "config.json")


def h(*arrays) -> str:
    s = hashlib.sha256()
    for a in arrays:
        s.update(np.ascontiguousarray(a).tobytes())
    return s.hexdigest()[:16]


def state_hash(d) -> str:
    return h(np.array([d.time]), d.qpos, d.qvel, d.act, d.qacc_warmstart)


def platform_line() -> str:
    from rabbitstew.provenance import _cpu_model

    return f"{platform.system()} {platform.machine()} | {_cpu_model()} | python {platform.python_version()} | mujoco {mujoco.__version__} | numpy {np.__version__}"


def load_config(seed: int) -> EvolutionConfig:
    with open(CONFIG) as f:
        d = json.load(f)
    d["seed"] = seed
    d["workers"] = 1
    return EvolutionConfig.from_dict(d)


def gen0_pairs(cfg: EvolutionConfig):
    """Generation 0's evaluation pairs for both populations, drawn exactly as Experiment.run + evaluate draw them."""
    rngs = spawn_streams(cfg.seed, cfg.holistic_stream_salt)
    pops = {HOLISTIC: initial_population(HOLISTIC, cfg, rngs[HOLISTIC]), CONVENTIONAL: initial_population(CONVENTIONAL, cfg, rngs[CONVENTIONAL])}
    terrain_seed = draw_terrain_seed(cfg, rngs[TERRAIN])
    start_seeds = draw_start_seeds(cfg, rngs[TERRAIN])
    sim = generation_sim(cfg, terrain_seed, 0)
    out = {}
    for kind, pop in pops.items():
        rng = rngs[kind]
        n = len(pop.members)
        best = int(rng.integers(0, n))  # evaluate(): no best yet at generation 0
        top = [best]
        pairs = []
        for i in range(n):
            opps = [t for t in top if t != i][:1]
            if not opps:
                others = [j for j in range(n) if j != i]
                opps = [int(rng.choice(others))]
            for o in opps:
                for sd in start_seeds:
                    swap = bool(rng.random() < 0.5) if cfg.random_sides else False
                    pairs.append((i, pop.members[i], pop.members[o], swap, sd))
        out[kind] = pairs
    return out, sim, terrain_seed


def cmd_gen0(args) -> None:
    cfg = load_config(args.seed)
    pairs, sim, terrain_seed = gen0_pairs(cfg)
    print(f"# platform: {platform_line()}")
    print(f"# seed {args.seed} terrain_seed {terrain_seed}")
    for kind, prefix in ((HOLISTIC, "h"), (CONVENTIONAL, "c")):
        fits = []
        for k, (i, a, b, swap, sd) in enumerate(pairs[kind]):
            r = simulation.run_bout(a, b, sim, swap=swap, start_seed=sd)
            fits.append(r.fitness[0])
            print(f"{prefix} bout {k:2d} member {i:2d} swap {int(swap)} fitness {r.fitness[0]:.6f} {float(r.fitness[0]).hex()} dist {float(r.distances[0]).hex()}")
        print(f"ROW {prefix}_best {max(fits):.6f} {prefix}_mean {float(np.mean(fits)):.6f}")


class _StepProxy(types.ModuleType):
    """Stands in for `mujoco` inside rabbitstew.simulation: every mj_step is hashed."""

    def __init__(self, log: list):
        super().__init__("mujoco_proxy")
        self._log = log

    def __getattr__(self, name):
        return getattr(mujoco, name)

    def mj_step(self, m, d):
        mujoco.mj_step(m, d)
        self._log.append(state_hash(d))


def cmd_record(args) -> None:
    cfg = load_config(args.seed)
    pairs, sim_cfg, terrain_seed = gen0_pairs(cfg)
    i, a, b, swap, sd = pairs[args.population][args.bout]
    os.makedirs(args.out, exist_ok=True)
    order = [b, a] if swap else [a, b]
    for k, g in enumerate(order):
        g.save(os.path.join(args.out, f"robot{k}.json"))
    with open(os.path.join(args.out, "simconfig.json"), "w") as f:
        json.dump(sim_cfg.to_dict(), f, indent=1, default=list)
    xmls = []
    orig_build_xml = world.build_xml

    def capture(*a_, **k_):
        x = orig_build_xml(*a_, **k_)
        xmls.append(x)
        return x

    steps: list = []
    world.build_xml = capture
    simulation.mujoco = _StepProxy(steps)
    try:
        sim = simulation.Simulation(order, sim_cfg, spawns=simulation.spawn_layout(2, sim_cfg, sd))
        settle_steps = len(steps)
        with open(os.path.join(args.out, "model.xml"), "w") as f:
            f.write(xmls[-1])
        mujoco.mj_saveModel(sim.model, os.path.join(args.out, "model.mjb"), None)
        d = sim.data
        np.save(os.path.join(args.out, "init_state.npy"), np.concatenate([[d.time], d.qpos, d.qvel, d.act, d.qacc_warmstart]))
        sensors, acts, ctrls = [], [], []
        # the bout loop of Simulation.run, one tick at a time; the brains' inputs are captured by wrapping step()
        captured = []
        for br in sim.brains:
            orig = br.step

            def wrapped(vals, _orig=orig, _br=br):
                captured.append(np.array(vals, dtype=float))
                return _orig(vals)

            br.step = wrapped
        n = int(round(sim_cfg.duration / sim_cfg.control_dt))
        for _ in range(n):
            captured.clear()
            sim.step()
            sensors.append(np.concatenate(captured) if captured else np.zeros(0))
            acts.append(np.concatenate([br.activation for br in sim.brains]))
            ctrls.append(d.ctrl.copy())
    finally:
        world.build_xml = orig_build_xml
        simulation.mujoco = mujoco
    np.save(os.path.join(args.out, "sensors.npy"), np.array(sensors))
    np.save(os.path.join(args.out, "activations.npy"), np.array(acts))
    np.save(os.path.join(args.out, "ctrl.npy"), np.array(ctrls))
    with open(os.path.join(args.out, "steps.txt"), "w") as f:
        f.write(f"# settle_steps {settle_steps} substeps {sim_cfg.control_substeps}\n")
        f.write("\n".join(steps) + "\n")
    dists = [sim.distance_from_center(k) for k in range(2)]
    summary = {
        "platform": platform_line(),
        "population": args.population,
        "bout": args.bout,
        "member": i,
        "swap": swap,
        "terrain_seed": terrain_seed,
        "xml_sha": hashlib.sha256(xmls[-1].encode()).hexdigest()[:16],
        "first_xml_sha": hashlib.sha256(xmls[0].encode()).hexdigest()[:16],
        "mjb_sha": file_sha(os.path.join(args.out, "model.mjb")),
        "settle_steps": settle_steps,
        "init_state": h(np.load(os.path.join(args.out, "init_state.npy"))),
        "final_state": steps[-1],
        "distances_hex": [float(x).hex() for x in dists],
        "exploded": list(sim.exploded),
    }
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


def file_sha(p: str) -> str:
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def _steps(path: str):
    with open(path) as f:
        head = f.readline().split()
        return int(head[2]), int(head[4]), [ln.strip() for ln in f if ln.strip()]


def cmd_compare(args) -> None:
    A, B = args.ref, args.other
    sa = json.load(open(os.path.join(A, "summary.json")))
    sb = json.load(open(os.path.join(B, "summary.json")))
    print(f"A: {sa['platform']}\nB: {sb['platform']}")
    for key in ("first_xml_sha", "xml_sha", "mjb_sha", "settle_steps", "init_state", "final_state", "distances_hex", "exploded"):
        print(f"{key:14s} {'same' if sa[key] == sb[key] else 'DIFFERS'}  {sa[key]}  {sb[key]}")
    settle_a, sub, st_a = _steps(os.path.join(A, "steps.txt"))
    settle_b, _, st_b = _steps(os.path.join(B, "steps.txt"))
    first_settle = next((k for k in range(min(settle_a, settle_b)) if st_a[k] != st_b[k]), None)
    print(f"settle: first differing mj_step {first_settle} of {settle_a}/{settle_b}")
    S = [np.load(os.path.join(p, "sensors.npy")) for p in (A, B)]
    Z = [np.load(os.path.join(p, "activations.npy")) for p in (A, B)]
    C = [np.load(os.path.join(p, "ctrl.npy")) for p in (A, B)]
    for t in range(min(len(S[0]), len(S[1]))):
        layers = []
        if not np.array_equal(S[0][t], S[1][t]):
            layers.append(("sensors", S))
        if not np.array_equal(Z[0][t], Z[1][t]):
            layers.append(("activations", Z))
        if not np.array_equal(C[0][t], C[1][t]):
            layers.append(("ctrl", C))
        phys = [st_a[settle_a + t * sub + j] != st_b[settle_b + t * sub + j] for j in range(sub)]
        if any(phys):
            layers.append(("physics", None))
        if layers:
            print(f"first differing tick {t}: {[n for n, _ in layers]}  (physics substeps differing: {phys})")
            for name, arr in layers:
                if arr is None:
                    continue
                diff = np.nonzero(arr[0][t] != arr[1][t])[0]
                k = diff[0]
                x, y = arr[0][t][k], arr[1][t][k]
                ulp = abs(int(np.float64(x).view(np.int64)) - int(np.float64(y).view(np.int64)))
                print(f"  {name}: {len(diff)} entries differ, first index {k}: {x!r} vs {y!r} ({ulp} ulp)")
            break
    else:
        print("no tick differs")
    # how the gap grows: max |qpos-ish| difference is not stored, so report sensor gap per second
    n = min(len(S[0]), len(S[1]))
    for t in (0, 50, 100, 200, 400, n - 1):
        if t < n:
            print(f"  tick {t:4d}: max |sensor diff| {np.max(np.abs(S[0][t] - S[1][t])) if S[0][t].size else 0:.3e}")


def cmd_replay_physics(args) -> None:
    R = args.ref
    sref = json.load(open(os.path.join(R, "summary.json")))
    settle, sub, ref_steps = _steps(os.path.join(R, "steps.txt"))
    print(f"ref:  {sref['platform']}\nhere: {platform_line()}")
    # (a) compile the reference XML here: is the model the same?
    m_here = mujoco.MjModel.from_xml_path(os.path.join(R, "model.xml"))
    tmp = os.path.join(args.scratch, "here.mjb")
    mujoco.mj_saveModel(m_here, tmp, None)
    print(f"compile ref XML here: mjb {file_sha(tmp)} vs ref {sref['mjb_sha']} -> {'same' if file_sha(tmp) == sref['mjb_sha'] else 'DIFFERS'}")
    # (b) open loop from the reference MJB and post-settle state
    m = mujoco.MjModel.from_binary_path(os.path.join(R, "model.mjb"))
    d = mujoco.MjData(m)
    st = np.load(os.path.join(R, "init_state.npy"))
    o = 1
    d.time = st[0]
    for arr in (d.qpos, d.qvel, d.act, d.qacc_warmstart):
        arr[:] = st[o : o + arr.size]
        o += arr.size
    mujoco.mj_forward(m, d)
    ctrl = np.load(os.path.join(R, "ctrl.npy"))
    first = None
    k = 0
    for t in range(len(ctrl)):
        d.ctrl[:] = ctrl[t]
        for _ in range(sub):
            mujoco.mj_step(m, d)
            if first is None and state_hash(d) != ref_steps[settle + k]:
                first = (t, k)
            k += 1
    print(f"open-loop physics: {k} steps replayed; first differing step: {first if first else 'none'}; final {state_hash(d)} vs ref {ref_steps[-1]}")
    # NB: the reference's ctrl at tick t was applied before tick t's substeps; mj_forward above recomputes derived
    # quantities but changes no state, so a same-platform replay must match the reference exactly (checked in CI).


def cmd_replay_brain(args) -> None:
    R = args.ref
    sref = json.load(open(os.path.join(R, "summary.json")))
    simcfg = simulation.SimConfig.from_dict(json.load(open(os.path.join(R, "simconfig.json"))))
    gs = [Genotype.load(os.path.join(R, f"robot{k}.json")) for k in range(2)]
    brains = [RuntimeBrain(synthesize(g, simcfg.synthesis)) for g in gs]
    S = np.load(os.path.join(R, "sensors.npy"))
    Z = np.load(os.path.join(R, "activations.npy"))
    ns = [len(b.sensors) for b in brains]
    print(f"ref:  {sref['platform']}\nhere: {platform_line()}")
    first = None
    for t in range(len(S)):
        o = 0
        for b, n in zip(brains, ns):
            b.step(S[t][o : o + n])
            o += n
        z = np.concatenate([b.activation for b in brains])
        if first is None and not np.array_equal(z, Z[t]):
            k = int(np.nonzero(z != Z[t])[0][0])
            first = (t, k, z[k], Z[t][k])
    print(f"brain replay on recorded sensors: {len(S)} ticks; first differing tick: {first if first else 'none'}")


def cmd_numpy_probe(args) -> None:
    rng = np.random.default_rng(12345)
    x = rng.normal(0, 3, 4096)
    W = rng.normal(0, 1, (40, 40))
    v = rng.normal(0, 1, 40)
    R3 = rng.normal(0, 1, (3, 3))
    v3 = rng.normal(0, 1, 3)
    rows = [
        ("np.tanh", h(np.tanh(x))),
        ("np.sin", h(np.sin(x))),
        ("np.cos", h(np.cos(x))),
        ("np.exp", h(np.exp(x / 3))),
        ("np.log", h(np.log(np.abs(x) + 1e-3))),
        ("np.arccos", h(np.arccos(np.clip(x / 10, -1, 1)))),
        ("np.sqrt", h(np.sqrt(np.abs(x)))),
        ("math.tanh", h(np.array([math.tanh(t) for t in x]))),
        ("math.sin", h(np.array([math.sin(t) for t in x]))),
        ("math.exp", h(np.array([math.exp(t / 3) for t in x]))),
        ("W@v 40x40 (BLAS gemv)", h(W @ v)),
        ("W@v 12x12", h(W[:12, :12] @ v[:12])),
        ("R3@v3 3x3", h(R3 @ v3)),
        ("R3.T@v3", h(R3.T @ v3)),
        ("np.linalg.norm(v3)", h(np.array([np.linalg.norm(v3)]))),
        ("np.dot(v,v)", h(np.array([np.dot(v, v)]))),
        ("sum(v)", h(np.array([v.sum()]))),
        ("python-loop dot", h(np.array([sum(float(a) * float(b) for a, b in zip(W[0], v))]))),
    ]
    print(f"# platform: {platform_line()}")
    try:
        cfg = np.show_config(mode="dicts")
        blas = cfg["Build Dependencies"]["blas"]
        print(f"# blas: {blas.get('name')} {blas.get('version', '')}")
        simd = cfg.get("SIMD Extensions", {})
        print(f"# simd found: {simd.get('found')}")
    except Exception as e:  # pragma: no cover
        print(f"# blas: unknown ({e})")
    for name, val in rows:
        print(f"{name:28s} {val}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("gen0")
    g.add_argument("--seed", type=int, default=201)
    r = sp.add_parser("record")
    r.add_argument("out")
    r.add_argument("--seed", type=int, default=201)
    r.add_argument("--population", default=CONVENTIONAL, choices=[HOLISTIC, CONVENTIONAL])
    r.add_argument("--bout", type=int, default=0)
    c = sp.add_parser("compare")
    c.add_argument("ref")
    c.add_argument("other")
    rp = sp.add_parser("replay-physics")
    rp.add_argument("ref")
    rp.add_argument("--scratch", default=os.environ.get("TMPDIR", "/tmp"))
    rb = sp.add_parser("replay-brain")
    rb.add_argument("ref")
    sp.add_parser("numpy-probe")
    a = p.parse_args()
    {"gen0": cmd_gen0, "record": cmd_record, "compare": cmd_compare, "replay-physics": cmd_replay_physics, "replay-brain": cmd_replay_brain, "numpy-probe": cmd_numpy_probe}[a.cmd](a)


if __name__ == "__main__":
    main()
