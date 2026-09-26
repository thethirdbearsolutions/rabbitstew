"""RBT-90 part 2, before any run: are the founders part 1 measured the founders a run would found?

Part 1's ``founder_diversity.founders(seed)`` draws the sixty holistic founders from
``np.random.default_rng(seed)``, which is what the ecology did when it had one RNG stream.  Since
RBT-95 (PR #56, merged before part 1's answer but after its branch was cut) the ecology draws them
from ``spawn_streams(seed)[HOLISTIC]``, a different generator.  This script asks, with no simulation:

1. per seed of the committed ten, how many of part 1's founders a run on this head would found;
2. the three rates of the founders this head does found, beside part 1's;
3. whether the committed ten pass the rule on this head's founders, against a reference rebuilt on
   this head's founders (seeds 1..200), and what ``--choose 10`` would choose there.

It imports part 1's script and swaps only ``founders``; nothing under docs/artifacts that part 1
committed is rewritten (the module's ART is pointed at a scratch directory).

    python runs/RBT-90/head_founders.py > docs/artifacts/RBT-90-head-founders.txt
"""
import importlib.util
import pathlib
import tempfile

import numpy as np

from rabbitstew.evolution import HOLISTIC, initial_population, spawn_streams

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("fd", ROOT / "runs" / "RBT-90" / "founder_diversity.py")
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

TEN = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
old_founders = fd.founders
fd.spawn_streams = lambda seed: {HOLISTIC: np.random.default_rng(seed)}  # part 1's generator for the part-1 column, now founders() draws the head's


def head_founders(seed):
    """Part 1's founders() with the one line changed: the generator the ecology now uses."""
    evo, _ = old_founders(seed)  # keeps part 1's config guard
    return evo, list(initial_population(HOLISTIC, evo, spawn_streams(seed)[HOLISTIC]).members)


def k(m):
    return f"{m['drive']}/60 {m['osc']}/60 {m['both']}/60"


print("RBT-90 part 2, before any run: part 1's founders against the founders this head's ecology draws (no simulation).")
print("part 1: initial_population(HOLISTIC, evo, default_rng(seed)); this head (RBT-95): spawn_streams(seed)[HOLISTIC].")
print()
print(f"{'seed':>5s}  {'shared bodies':>13s}  {'part 1 drive osc both':>24s}  {'this head drive osc both':>26s}")
part1 = {s: fd.measure(s) for s in TEN}
fd.founders = head_founders
fd.ART = pathlib.Path(tempfile.mkdtemp(prefix="rbt90-head-"))
head = {s: fd.measure(s) for s in TEN}
for s in TEN:
    shared = len(set(part1[s]["sigs"]) & set(head[s]["sigs"]))
    print(f"{s:5d}  {shared:10d}/60  {k(part1[s]):>24s}  {k(head[s]):>26s}")
print()

ref = fd.reference(200)
print("reference rebuilt on this head's founders, seeds 1..200; quartile thresholds as k/60:")
for key in fd.SPAN_ON + ("drive",):
    lo, hi = ref["span"][key]
    print(f"  {key:6s} [{fd.k60(lo)}, {fd.k60(hi)}]")
cache = dict(head)
print()
for key in fd.SPAN_ON:
    xs = [fd.rates(head[s])[key] for s in TEN]
    lo, hi = ref["span"][key]
    print(f"  the committed ten on this head's founders, {key}: min {fd.k60(min(xs))} max {fd.k60(max(xs))} -> {'spans' if min(xs) <= lo and max(xs) >= hi else 'DOES NOT SPAN'}")
print(f"  the committed ten pass clauses 1 and 2 on this head's founders: {fd.passes(TEN, ref, cache)}")
print(f"  the kept five alone: {fd.passes(fd.CALIBRATION, ref, cache)}")
print()
chosen, text = fd.choose(10, ref)
print("what --choose 10 selects on this head's founders (the same rule, the five kept by number):")
print(text)
