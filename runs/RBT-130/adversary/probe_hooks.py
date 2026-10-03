"""RBT-130 adversary probes (PR #424 @ 424b82a).  Run from the repo root: python runs/RBT-130/adversary/probe_hooks.py

P1  merge-null count when the copied fauna is the minority at the merge (M1: N must start from M's composition)
P2  spawn-key census: every stream family the code can build at one seed, first draws pairwise distinct
P3  only-fauna byte identity beyond the PR's test: persistent food, workers 2, stagger ages, cull, seeded founders
P4  lesion: workers 1 vs 2 byte-identical (the flag survives pickling); the other fauna untouched under persistent food
P5  sweep-log / lineage coverage: are the season's dead in lineage.jsonl, and are the sweep means survivor-only?
"""
import json
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests"))
from test_ecology_switches import _breeding_eco, _evo  # noqa: E402

from rabbitstew.ecology import NULL_B, Ecology, breed_seed_sequence, merge_null_seed_sequence  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, STREAMS, EvolutionConfig  # noqa: E402
from rabbitstew.simulation import FoodConfig, SimConfig  # noqa: E402
from rabbitstew.world import WorldConfig  # noqa: E402

TMP = tempfile.mkdtemp(prefix="rbt130adv_")


def run(name, eco, evo=None):
    out = os.path.join(TMP, name)
    Ecology(evo or _evo(11, 1.5), eco, out_dir=out, log=None).run()
    return out


def rows(out):
    return [json.loads(l) for l in open(os.path.join(out, "lineage.jsonl")).read().splitlines()]


def hist(out):
    return json.load(open(os.path.join(out, "history.json")))["history"]


def cohorts(out):
    return [json.loads(l) for l in open(os.path.join(out, "cohorts.jsonl")).read().splitlines()]


def persistent_evo(workers=1):
    return EvolutionConfig(seed=11, brain_model="foraging", conventional_topology=True, workers=workers,
                           sim=SimConfig(duration=1.5, random_start=True, score="food", world=WorldConfig(terrain="random"),
                                         food=FoodConfig(items=4, radius=1.5, eat_radius=0.4, patches=2, patch_radius=0.4, regrow_delay=60.0)))


print("P1  merge-null with the copied fauna the minority at the merge")
print("    cull at season 2 leaves one fauna short; merge_after 3; capacity 6 per fauna, pooled 12")
for kind, cull in ((HOLISTIC, "holistic=4,conventional=0"), (CONVENTIONAL, "holistic=0,conventional=4")):
    for arm, kw in (("M", {}), ("N", dict(merge_null=kind))):
        out = run(f"p1_{kind}_{arm}", _breeding_eco(seasons=4, merge_after=3, cull_at=2, cull=cull, sweep_log=True, **kw))
        at = [e for e in hist(out) if e["season"] == 3]
        mc = at[0]["merge_counts"]
        other = CONVENTIONAL if kind == HOLISTIC else HOLISTIC
        if arm == "M":
            print(f"    {kind:12s} M: counts at merge {mc}  -> {kind} share at merge {mc[kind] / (mc[kind] + mc[other]):.2f}")
        else:
            nb = sum(1 for r in rows(out) if r["population"] == NULL_B and r["generation"] == 3 and r["name"].startswith("b") and not r["name"].startswith("be"))
            b0 = len([p for p in os.listdir(os.path.join(out, NULL_B, "genomes")) if p.startswith("b") and not p.startswith("be")])
            print(f"    {kind:12s} N: A={kind} {mc[kind]}, replaced {other} {mc[other]}, B copies made {b0}"
                  f"  -> A share at merge {mc[kind] / (mc[kind] + b0):.2f} (M's {kind} share {mc[kind] / (mc[kind] + mc[other]):.2f}; B should hold {mc[other]})")

print("\nP2  spawn-key census at seed 11 (keys and first 8 draws)")
fams = {}
for i, s in enumerate(np.random.SeedSequence(11).spawn(len(STREAMS))):
    fams[f"spawn[{STREAMS[i]}]"] = s
for k in range(1, 201):
    fams[f"breed_stream {k}"] = breed_seed_sequence(11, k)
    fams[f"salt {k}"] = np.random.SeedSequence(11, spawn_key=(STREAMS.index(HOLISTIC), k))
for kind in (HOLISTIC, CONVENTIONAL):
    fams[f"null {kind}"] = merge_null_seed_sequence(11, kind)
keys = {n: tuple(s.spawn_key) for n, s in fams.items()}
dup_keys = len(keys) - len(set(keys.values()))
draws = {n: tuple(np.random.default_rng(s).integers(0, 2**63, 4)) for n, s in fams.items()}
dup_draws = len(draws) - len(set(draws.values()))
print(f"    {len(fams)} streams; duplicate spawn keys {dup_keys}; duplicate first draws {dup_draws}")
print(f"    null keys: {keys['null holistic']} {keys['null conventional']}; breed (0,0,K); salt (0,S); plain (i,)")

print("\nP3  only-fauna == its half of the two-fauna run")


def half_equal(both, alone, kind):
    a = [r for r in rows(both) if r["population"] == kind] == rows(alone)
    b = [e for e in hist(both) if e["population"] == kind] == hist(alone)
    c = [json.dumps(r) for r in cohorts(both) if r["cohort"] == kind] == [json.dumps(r) for r in cohorts(alone)]
    return a, b, c


cases = [
    ("persistent food", dict(), persistent_evo),
    ("persistent, workers 2", dict(), lambda: persistent_evo(2)),
    ("stagger ages", dict(stagger_ages=True), None),
    ("cull at 2 (holistic=2,conventional=1)", dict(cull_at=2, cull="holistic=2,conventional=1"), None),
    ("breed_stream 3", dict(breed_stream=3), None),
    ("sweep_log + leakx", dict(sweep_log=True, breed_rule="leakx:0.3"), None),
]
import warnings  # noqa: E402
warnings.simplefilter("ignore")
for label, kw, evo in cases:
    for kind in (HOLISTIC, CONVENTIONAL):
        both = run(f"p3_{label}_{kind}_both".replace(" ", "_"), _breeding_eco(seasons=5, **kw), evo() if evo else None)
        alone = run(f"p3_{label}_{kind}_alone".replace(" ", "_"), _breeding_eco(seasons=5, only_fauna=kind, **kw), evo() if evo else None)
        print(f"    {label:40s} {kind:12s} lineage/history/cohorts equal: {half_equal(both, alone, kind)}")

print("\nP4  lesion")
w1 = run("p4_w1", _breeding_eco(seasons=4, lesion_fauna=HOLISTIC), persistent_evo(1))
w2 = run("p4_w2", _breeding_eco(seasons=4, lesion_fauna=HOLISTIC), persistent_evo(2))
plain = run("p4_plain", _breeding_eco(seasons=4), persistent_evo(1))
print(f"    lesioned, workers 1 vs 2 lineage identical: {rows(w1) == rows(w2)}")
print(f"    persistent food: conventional untouched {[r for r in rows(plain) if r['population'] == CONVENTIONAL] == [r for r in rows(w1) if r['population'] == CONVENTIONAL]};"
      f" holistic changed {[r for r in rows(plain) if r['population'] == HOLISTIC] != [r for r in rows(w1) if r['population'] == HOLISTIC]}")
cfg = json.load(open(os.path.join(w1, "config.json")))
print(f"    config.json: ecology.lesion_fauna={cfg['ecology'].get('lesion_fauna')!r}; sim.food.smell_lesion present: {'smell_lesion' in cfg['sim']['food']}")

print("\nP5  the season's dead: lineage coverage and survivor-only sweep means")
out = run("p5", _breeding_eco(seasons=7, merge_after=3, sweep_log=True, merge_null=HOLISTIC))
lin = {(r["generation"], r["name"]) for r in rows(out)}
missing, total = 0, 0
for c in cohorts(out):
    for g in c["groups"]:
        for m in g:
            total += 1
            missing += (c["season"], m["name"]) not in lin
deaths = sum(e["deaths"] for e in hist(out))
print(f"    cohort seats {total}; seats with no lineage row for that season (the season's dead) {missing}; deaths logged in history {deaths}")
print("    so food per member per group is not recoverable for the members who died that season, and food_mean/work_mean/path_mean")
print("    average survivors only (ecology.py _sweep_fields: rows = members of `alive`)")
print(f"\n(outputs under {TMP})")
