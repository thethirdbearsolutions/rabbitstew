"""RBT-95 item 3, adversary probes: the ecology's streams, checkpoint and resume with reproduction ON.

Every item-3 test in tests/test_ecology_switches.py runs with birth_threshold=100 and max_age=1000,
so none of them makes a single reproduction draw, a death, or a child's name.  These probes turn
breeding and deaths on and ask the same questions again, then try to break the resume.

    python runs/RBT-95/adversary_streams.py > docs/artifacts/RBT-95-adversary-streams.txt

No result is read from any of this: tiny ecologies, 1.5 s seasons, mechanics only.
"""

import json
import os
import shutil
import sys
import tempfile

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig
from rabbitstew.simulation import FoodConfig, SimConfig
from rabbitstew.world import WorldConfig

TMP = tempfile.mkdtemp(prefix="rbt95-adv-")


def evo(seed=11, **food):
    f = dict(items=12, radius=1.5, eat_radius=0.4)
    f.update(food)
    return EvolutionConfig(seed=seed, brain_model="foraging", conventional_topology=True,
                           sim=SimConfig(duration=1.5, random_start=True, score="food", world=WorldConfig(terrain="random"), food=FoodConfig(**f)))


def eco(**kw):
    # breeding ON (threshold under the founders' energy), deaths ON (max_age 5, staggered), crossover ON
    base = dict(seasons=8, capacity=6, challenge="foraging", group_size=2, max_age=5, initial_energy=2.0,
                birth_threshold=1.2, birth_cost=0.5, living_cost=0.05, crossover_rate=0.5, log_every=1000)
    base.update(kw)
    return EcologyConfig(**base)


def run(name, e, seed=11, **food):
    out = os.path.join(TMP, name)
    shutil.rmtree(out, ignore_errors=True)
    Ecology(evo(seed, **food), e, out_dir=out, log=None).run()
    return out


def rows(out, kind=None):
    with open(os.path.join(out, "lineage.jsonl")) as f:
        r = [json.loads(l) for l in f]
    return [x for x in r if kind is None or x["population"] == kind]


def raw(out, name):
    with open(os.path.join(out, name), "rb") as f:
        return f.read()


def hist(out):
    return json.loads(raw(out, "history.json"))["history"]


def streams(out):
    return json.loads(raw(out, "state.json"))["rngs"]


def turnover(out, kind):
    h = [e for e in hist(out) if e["population"] == kind]
    return sum(e["births"] for e in h), sum(e["deaths"] for e in h)


def genomes(out):
    found = {}
    for kind in (HOLISTIC, CONVENTIONAL):
        d = os.path.join(out, kind, "genomes")
        for n in sorted(os.listdir(d)):
            found[f"{kind}/{n}"] = raw(d, n)
    return found


class Killed(Exception):
    pass


def killed_run(name, e, at_season, where, seed=11, **food):
    """Run to `at_season`, then die inside it: `where` is 'between' (the holistic fauna's cohort and
    lineage rows and its children's genomes are on disk, the conventional fauna's are not) or
    'conv-cohort' (the conventional cohort row is also written, its lineage rows are not)."""
    out = os.path.join(TMP, name)
    shutil.rmtree(out, ignore_errors=True)
    x = Ecology(evo(seed, **food), e, out_dir=out, log=None)
    challenge, record = x._challenge, x._record

    def dying_challenge(members, sim, start_seed, key=()):
        if where == "between" and x.season == at_season and key == (CONVENTIONAL,):
            raise Killed()
        return challenge(members, sim, start_seed, key=key)

    def dying_record(kind, **kw):
        if where == "conv-cohort" and x.season == at_season and kind == CONVENTIONAL:
            raise Killed()
        return record(kind, **kw)

    x._challenge, x._record = dying_challenge, dying_record
    try:
        x.run()
    except Killed:
        pass
    x.runner.close()
    return out


def same(a, b, names=("lineage.jsonl", "cohorts.jsonl", "history.json")):
    return {n: raw(a, n) == raw(b, n) for n in names}


print("RBT-95 item 3, adversary probes (breeding and deaths ON; mechanics only, nothing here is a result)")
print()

# --------------------------------------------------------------------------- #
print("=== P1. unmerged pair, arms differing in the holistic founders, reproduction ON ===")
donor = run("donor", eco(seasons=1), seed=3)
base = run("p1-base", eco(merge_after=None))
other = run("p1-other", eco(merge_after=None, seed_holistic=donor))
for label, out in (("base", base), ("other", other)):
    print(f"  {label}: conventional births/deaths {turnover(out, CONVENTIONAL)}, holistic births/deaths {turnover(out, HOLISTIC)}")
conv_b = [l for l in raw(base, "lineage.jsonl").splitlines() if json.loads(l)["population"] == CONVENTIONAL]
conv_o = [l for l in raw(other, "lineage.jsonl").splitlines() if json.loads(l)["population"] == CONVENTIONAL]
print(f"  conventional lineage byte-identical across arms: {conv_b == conv_o} ({len(conv_b)} rows)")
print(f"  holistic lineage differs (the flag took): {rows(base, HOLISTIC) != rows(other, HOLISTIC)}")
print(f"  conventional stream final state identical: {streams(base)[CONVENTIONAL] == streams(other)[CONVENTIONAL]}; terrain: {streams(base)['terrain'] == streams(other)['terrain']}")
gb, go = genomes(base), genomes(other)
conv_files = sorted(k for k in gb if k.startswith(CONVENTIONAL))
print(f"  conventional genomes byte-identical: {all(gb[k] == go.get(k) for k in conv_files)} ({len(conv_files)} files, {sum(1 for k in conv_files if '/ce' in k)} of them children)")
print()

# --------------------------------------------------------------------------- #
print("=== P2. resume after a kill inside a season, reproduction ON ===")
whole = run("p2-whole", eco())
print(f"  uninterrupted: conventional births/deaths {turnover(whole, CONVENTIONAL)}, holistic {turnover(whole, HOLISTIC)}")
for where in ("between", "conv-cohort"):
    part = killed_run(f"p2-{where}", eco(), at_season=4, where=where)
    state = json.loads(raw(part, "state.json"))
    orphan_l = sum(1 for r in rows(part) if r["generation"] >= state["season"])
    with open(os.path.join(part, "cohorts.jsonl")) as f:
        orphan_c = sum(1 for l in f if json.loads(l)["season"] >= state["season"])
    Ecology.resume(part, log=None).run()
    g_w, g_p = genomes(whole), genomes(part)
    print(f"  killed {where!r} at season 4: state.json at season {state['season']}; rows on disk from the unfinished season: {orphan_l} lineage, {orphan_c} cohort")
    print(f"    after resume, byte-identical to the uninterrupted run: {same(part, whole)}; genomes: {g_w == g_p} ({len(g_w)} files)")
part = killed_run("p2-cull", eco(cull_at=4, cull="holistic=2,conventional=1"), at_season=4, where="between")
whole_c = run("p2-cull-whole", eco(cull_at=4, cull="holistic=2,conventional=1"))
n_cull_before = sum(1 for r in rows(part) if r.get("death") == "cull")
Ecology.resume(part, log=None).run()
n_cull_after = sum(1 for r in rows(part) if r.get("death") == "cull")
print(f"  killed in the cull season after the cull rows were written ({n_cull_before} on disk): after resume {n_cull_after} cull rows, byte-identical: {same(part, whole_c)}")
print()

# --------------------------------------------------------------------------- #
print("=== P3. after a merge, reproduction ON: what is shared across arms, field by field ===")
base = run("p3-base", eco(seasons=10, merge_after=3))
other = run("p3-other", eco(seasons=10, merge_after=3, seed_holistic=donor))
b, o = rows(base, CONVENTIONAL), rows(other, CONVENTIONAL)
pre_b, pre_o = [r for r in b if r["generation"] < 3], [r for r in o if r["generation"] < 3]
print(f"  before the merge (seasons 0-2): conventional rows identical: {pre_b == pre_o} ({len(pre_b)} rows)")
for label, out in (("base", base), ("other", other)):
    h = [e for e in hist(out) if e["population"] == CONVENTIONAL and e["season"] >= 3]
    print(f"  {label}: conventional births/deaths after the merge {sum(e['births'] for e in h)}/{sum(e['deaths'] for e in h)}, alive by season {[e['alive'] for e in h]}")
first_split = None
for s in range(3, 10):
    nb = [r["name"] for r in b if r["generation"] == s]
    no = [r["name"] for r in o if r["generation"] == s]
    if nb != no:
        first_split = s
        print(f"  first season whose living conventional fauna differs between arms: {s}")
        print(f"    base : {nb}")
        print(f"    other: {no}")
        break
if first_split is None:
    print("  the living conventional fauna is the same names every season (the probe did not separate the arms; read nothing from it)")
fields = sorted({k for r in b + o for k in r})
by_key = lambda rs: {(r["generation"], r["name"]): r for r in rs if r["generation"] >= 3}
kb, ko = by_key(b), by_key(o)
shared = sorted(set(kb) & set(ko))
differ = {f: sum(1 for k in shared if kb[k].get(f) != ko[k].get(f)) for f in fields}
print(f"  post-merge (season, name) rows present in both arms: {len(shared)} of {len(kb)} base / {len(ko)} other")
print(f"    fields that differ on those rows (count of rows): { {f: n for f, n in differ.items() if n} }")
print(f"    fields that never differ on those rows: {[f for f, n in differ.items() if not n]}")
children = sorted({r["name"] for r in b + o if r["name"].startswith("ce")})
cb, co = {r["name"]: r["parents"] for r in b}, {r["name"]: r["parents"] for r in o}
same_name_other_parents = [n for n in children if n in cb and n in co and cb[n] != co[n]]
gb, go = genomes(base), genomes(other)
same_name_other_genome = [n for n in children if f"{CONVENTIONAL}/{n}.json" in gb and f"{CONVENTIONAL}/{n}.json" in go and gb[f"{CONVENTIONAL}/{n}.json"] != go[f"{CONVENTIONAL}/{n}.json"]]
print(f"  conventional children born in either arm: {len(children)}; same name, different parents across arms: {same_name_other_parents}")
print(f"    same name, different genome bytes across arms: {same_name_other_genome}")
print(f"  conventional stream final state identical across arms: {streams(base)[CONVENTIONAL] == streams(other)[CONVENTIONAL]}")
print(f"  terrain stream final state identical: {streams(base)['terrain'] == streams(other)['terrain']}; worlds identical every season: {[(e['season'], e['terrain_seed'], e['start_seed']) for e in hist(base) if e['population'] == CONVENTIONAL] == [(e['season'], e['terrain_seed'], e['start_seed']) for e in hist(other) if e['population'] == CONVENTIONAL]}")
print()

# --------------------------------------------------------------------------- #
print("=== P4. broken on purpose: a kill that tears the last lineage line ===")
part = killed_run("p4-torn", eco(), at_season=4, where="between")
path = os.path.join(part, "lineage.jsonl")
data = raw(part, "lineage.jsonl")
with open(path, "wb") as f:
    f.write(data[: len(data) - 37])  # what a SIGKILL between two buffered 8 KiB flushes leaves: a row cut mid-way
try:
    Ecology.resume(part, log=None).run()
    print(f"  resume survived a torn final line; byte-identical to the uninterrupted run: {same(part, whole)}")
except Exception as err:  # noqa: BLE001 - the probe reports whatever the resume does
    print(f"  resume on a lineage.jsonl whose final row is cut mid-way: {type(err).__name__}: {str(err)[:100]}")
    print("  (the torn row belongs to the unfinished season, which the resume is about to drop anyway)")
print()

# --------------------------------------------------------------------------- #
print("=== P5. what a resume does to config.json ===")
part = run("p5-part", eco(seasons=3, seed_holistic=donor))
before = json.loads(raw(part, "config.json"))["ecology"]
Ecology.resume(part, seasons=5, log=None).run()
after = json.loads(raw(part, "config.json"))["ecology"]
print(f"  before the resume: seed_holistic = {os.path.basename(before['seed_holistic'])!r}, seasons = {before['seasons']}")
print(f"  after the resume : seed_holistic = {after['seed_holistic']!r}, seasons = {after['seasons']}")
whole5 = run("p5-whole", eco(seasons=5, seed_holistic=donor))
print(f"  resumed run against the uninterrupted one: {same(part, whole5, names=('lineage.jsonl', 'cohorts.jsonl', 'history.json', 'config.json'))}")
print()

# --------------------------------------------------------------------------- #
print("=== P6. the persistent world (regrow_delay > 0), resume after a kill, reproduction ON ===")
pw = dict(patches=2, patch_radius=0.5, regrow_delay=2.0)
whole = run("p6-whole", eco(), **pw)
part = killed_run("p6-part", eco(), at_season=4, where="between", **pw)
Ecology.resume(part, log=None).run()
print(f"  byte-identical to the uninterrupted run: {same(part, whole, names=('lineage.jsonl', 'cohorts.jsonl', 'history.json', 'arenas.json'))}")
print()

# --------------------------------------------------------------------------- #
print("=== P7. --resume pointed at the wrong kind of state ===")
part = run("p7", eco(seasons=2))
state = json.loads(raw(part, "state.json"))
state["rngs"].pop("terrain")
with open(os.path.join(part, "state.json"), "w") as f:
    json.dump(state, f)
try:
    Ecology.resume(part, log=None)
    print("  a state.json missing one of the three streams: resumed without complaint")
except Exception as err:  # noqa: BLE001
    print(f"  a state.json missing one of the three streams: {type(err).__name__}: {str(err)[:100]}")

shutil.rmtree(TMP, ignore_errors=True)
sys.exit(0)
