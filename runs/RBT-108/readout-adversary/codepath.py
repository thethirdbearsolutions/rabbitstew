"""RBT-108 readout adversary, item (a): is salt 0 a different code path from salt != 0?

No arena arm.  Part 4 is a labelled 1-generation PROBE (scratch output, never an arm).

    python runs/RBT-108/readout-adversary/codepath.py [--probe SCRATCH_DIR] > runs/RBT-108/readout-adversary/codepath.txt

1. salt 0's stream is SeedSequence(seed).spawn(3)[0]; the salted branch builds SeedSequence(seed, spawn_key=(0, S)).
   Is the unsalted child the same object the salted branch would build with key (0,)?  (Then the "two routes" are one
   constructor with a different spawn key.)
2. Key collisions: does the salt-1 key (0, 1) equal any stream an s0 run draws from, or is it a descendant/ancestor of one?
3. Founders: the holistic gen-0 population drawn at salts 0, 1, 2 over seeds 1..300 (no simulation): size statistics.
4. PROBE (--probe): one generation of RBT-96's configuration at seed 205, (i) salt 0 as shipped and (ii) salt 0 forced
   through the salted branch with spawn key (0,).  lineage.jsonl and generations must be byte-identical.
"""
import hashlib
import json
import os
import statistics as st
import sys

import numpy as np

from rabbitstew import evolution as ev
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, STREAMS, TERRAIN, EvolutionConfig, _size_stats, initial_population, spawn_streams

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "..", "..", "RBT-96", "s0-205", "config.json")
SEEDS = list(range(201, 217))

print("RBT-108 readout adversary: salt code path (numpy", np.__version__, ")")
print(f"STREAMS = {STREAMS}; holistic index {STREAMS.index(HOLISTIC)}")

# 1 ---------------------------------------------------------------------------
same = []
for s in SEEDS:
    a = np.random.SeedSequence(s).spawn(len(STREAMS))[STREAMS.index(HOLISTIC)]
    b = np.random.SeedSequence(s, spawn_key=(STREAMS.index(HOLISTIC),))
    same.append(a.entropy == b.entropy and a.spawn_key == b.spawn_key and a.pool_size == b.pool_size
                and bool((a.generate_state(16) == b.generate_state(16)).all())
                and np.random.default_rng(a).random() == np.random.default_rng(b).random())
print(f"\n1. unsalted holistic child == SeedSequence(seed, spawn_key=(0,)) for seeds 201-216: {sum(same)}/{len(same)}")
print("   so salt 0 and salt S differ only in the spawn key, (0,) vs (0, S); both go through one SeedSequence -> PCG64 path.")
r0, r1 = spawn_streams(205, 0), spawn_streams(205, 1)
print(f"   spawn_streams(205, 0) vs (205, 1): conventional state identical {r0[CONVENTIONAL].bit_generator.state == r1[CONVENTIONAL].bit_generator.state}, "
      f"terrain identical {r0[TERRAIN].bit_generator.state == r1[TERRAIN].bit_generator.state}, holistic identical {r0[HOLISTIC].bit_generator.state == r1[HOLISTIC].bit_generator.state}")
print(f"   bit generator: salt 0 {type(r0[HOLISTIC].bit_generator).__name__}, salt 1 {type(r1[HOLISTIC].bit_generator).__name__}")

# 2 ---------------------------------------------------------------------------
keys0 = [(i,) for i in range(len(STREAMS))]
k1 = (STREAMS.index(HOLISTIC), 1)
print(f"\n2. keys drawn from by an s0 run: {keys0}; salt-1 holistic key {k1}")
print(f"   equal to one of them: {k1 in keys0};  (0, 1) is the second child of (0,) -- does anything call .spawn() on a stream?")
src = open(ev.__file__).read() + open(os.path.join(os.path.dirname(ev.__file__), "simulation.py")).read()
print(f"   '.spawn(' occurrences in evolution.py + simulation.py outside spawn_streams: {src.count('.spawn(') - 1};  "
      f"'seed_seq' occurrences: {src.count('seed_seq')}")
print("   other readers of the salt: evolution.EvolutionConfig.to_dict (drops the key at 0: config.json only),")
print("   spawn_streams, ecology (spawn_streams; refuses breed_stream with a salt).  grep: rabbitstew/ has no other reference.")

# 3 ---------------------------------------------------------------------------
cfg = EvolutionConfig.from_dict(json.load(open(CFG)))
print(f"\n3. founders (holistic gen 0, population {cfg.population_size}) at salts 0, 1, 2 over seeds 1..300: mean over seeds of the")
print("   per-seed founder mean; SE is the SD over seeds / sqrt 300.  Paired differences salt S - salt 0 per seed, t = mean / SE.")
stats = {}
for salt in (0, 1, 2):
    rows = []
    for s in range(1, 301):
        pop = initial_population(HOLISTIC, cfg, spawn_streams(s, salt)[HOLISTIC])
        z = [_size_stats(m, cfg.sim) for m in pop.members]
        rows.append({k: st.mean(x[k] for x in z) for k in ("best_parts", "best_units", "best_links", "best_mass")} | {"nodes": st.mean(len(m.nodes) for m in pop.members)})
    stats[salt] = rows
for k in ("nodes", "best_parts", "best_units", "best_links", "best_mass"):
    line = f"   {k:11s}"
    for salt in (0, 1, 2):
        xs = [r[k] for r in stats[salt]]
        line += f"  salt {salt}: {st.mean(xs):8.3f}"
    for salt in (1, 2):
        dd = [a[k] - b[k] for a, b in zip(stats[salt], stats[0])]
        se = st.stdev(dd) / len(dd) ** 0.5
        line += f"   {salt}-0 t {st.mean(dd) / se if se else 0:+.2f}"
    print(line)

# 4 ---------------------------------------------------------------------------
if "--probe" in sys.argv:
    scratch = sys.argv[sys.argv.index("--probe") + 1]
    print(f"\n4. PROBE (1 generation, seed 205, RBT-96 configuration, workers 2; scratch {scratch}; not an arm)")
    digests = {}
    orig = ev.spawn_streams

    def via_salted_branch(seed, holistic_salt=0):
        children = np.random.SeedSequence(seed).spawn(len(STREAMS))
        i = STREAMS.index(HOLISTIC)
        children[i] = np.random.SeedSequence(seed, spawn_key=(i,))  # the salted branch's constructor, key (0,)
        return {name: np.random.default_rng(ss) for name, ss in zip(STREAMS, children)}

    for label, fn in (("salt 0 as shipped", orig), ("salt 0 through the salted branch, key (0,)", via_salted_branch)):
        ev.spawn_streams = fn
        c = EvolutionConfig.from_dict(json.load(open(CFG)))
        c.generations, c.workers = 1, 2
        out = os.path.join(scratch, "salted-branch" if fn is via_salted_branch else "shipped")
        ex = ev.Experiment(c, out_dir=out, log=None)
        ex.run()
        h = hashlib.sha256(open(os.path.join(out, "lineage.jsonl"), "rb").read()).hexdigest()
        hist = json.dumps(ex.history, sort_keys=True)
        digests[label] = (h, hashlib.sha256(hist.encode()).hexdigest())
        print(f"   {label:45s} lineage.jsonl sha256 {h[:16]}  history sha256 {digests[label][1][:16]}  "
              f"holistic best {max(e['best_fitness'] for e in ex.history if e['population'] == HOLISTIC):.6f}")
    ev.spawn_streams = orig
    a, b = digests.values()
    print(f"   byte-identical: lineage {a[0] == b[0]}, history {a[1] == b[1]}")
    row = open(os.path.join(HERE, "..", "..", "RBT-96", "s0-205", "generations.txt")).read().splitlines()[1].split("\t")
    print(f"   committed s0-205 generation-0 row: terrain seed {row[1]}, h_best {row[3]}, h_mean {row[4]}  (the probe replays the committed arm's gen 0)")
