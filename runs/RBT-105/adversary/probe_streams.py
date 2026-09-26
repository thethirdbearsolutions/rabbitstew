"""RBT-105 design adversary, probe 1b: does --breed-stream K share its random bits with RBT-96's
--holistic-stream-salt S (PR #146), and what happens when both are set?

    python runs/RBT-105/adversary/probe_streams.py                 # on this tree (the PR head)
    PYTHONPATH=<trial merge with PR #146> python runs/RBT-105/adversary/probe_streams.py

Part 1 needs numpy only. Part 2 runs only where spawn_streams takes a salt (a tree with PR #146 merged):
it builds a tiny Ecology with salt = K = 1 and compares the holistic generator's state after __init__
with a fresh generator at spawn key (0, 1).
"""
import inspect

import numpy as np

from rabbitstew import evolution
from rabbitstew.evolution import HOLISTIC, STREAMS

i = STREAMS.index(HOLISTIC)
print("part 1: the two flags' keys, numpy", np.__version__)
for seed in (7, 805):
    for k in (1, 2):
        breed = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(i, k)))  # ecology.py, breed_stream = k
        salt = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(i, k)))   # PR #146 spawn_streams, salt = k
        a, b = breed.integers(0, 2**63, 1000), salt.integers(0, 2**63, 1000)
        print(f"  seed {seed}: breed_stream {k} and holistic_stream_salt {k} give the same first 1000 draws: {bool((a == b).all())}")
print("  (the breed key is (holistic index, K); RBT-96's salted key is (holistic index, S): one namespace, two meanings)")

if "holistic_salt" in inspect.signature(evolution.spawn_streams).parameters:
    from rabbitstew.ecology import Ecology, EcologyConfig
    from rabbitstew.evolution import EvolutionConfig
    print("\npart 2: this tree has PR #146; an Ecology with holistic_stream_salt = 1 and breed_stream = 1")
    evo = EvolutionConfig(seed=7, holistic_stream_salt=1)
    eco = EcologyConfig(seasons=1, capacity=4, challenge="foraging", group_size=2, max_age=10, breed_stream=1)
    e = Ecology(evo, eco, out_dir=None, log=None)
    fresh = np.random.default_rng(np.random.SeedSequence(7, spawn_key=(i, 1)))
    same = e.rngs[HOLISTIC].bit_generator.state == fresh.bit_generator.state
    print(f"  the holistic history generator after __init__ is the salted founders' generator rewound to its start: {same}")
    print("  i.e. the history re-uses, from draw 0, the very bits that drew the founders; and the salt no longer")
    print("  moves the history at all (salt 1 and salt 2 with breed_stream 1 share one history stream):")
    e2 = Ecology(EvolutionConfig(seed=7, holistic_stream_salt=2), eco, out_dir=None, log=None)
    print(f"  salt 2, breed 1 history generator == salt 1, breed 1 history generator: {e2.rngs[HOLISTIC].bit_generator.state == e.rngs[HOLISTIC].bit_generator.state}")
else:
    print("\npart 2: skipped (spawn_streams takes no salt on this tree; PR #146 not merged)")
