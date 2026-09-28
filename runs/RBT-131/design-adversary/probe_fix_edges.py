"""RBT-131 design adversary: edge cases of the final/ clear, on whichever rabbitstew/ tree is on PYTHONPATH.

    PYTHONPATH=<tree> python runs/RBT-131/design-adversary/probe_fix_edges.py

(A) a crash inside _save_populations after one member file, on a run resumed through a cull (final/ held 6 + 6);
    then a no-op resume (same seasons) to show the next save repairs final/.
(B) which file names the clear removes.
(C) a fork whose <kind>/final is a symlink to the parent's final/ (no committed script forks this way).
(D) a fresh run launched (not resumed) into a directory holding a finished run with a larger population.
Test-sized ecologies only (tests/test_ecology_switches helpers); no committed run is touched.
"""
import json, os, shutil, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests"))
import rabbitstew
from rabbitstew import genotype as G
from rabbitstew.ecology import Ecology
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC
from test_ecology_switches import _eco, _evo

CULL = dict(cull_at=2, cull="holistic=3,conventional=2")
print("tree:", os.path.dirname(rabbitstew.__file__))


def final(out, k):
    d = os.path.join(out, k, "final")
    return sorted(os.listdir(d)) if os.path.isdir(d) else None


def living(out, k):
    return [m["name"] for m in json.load(open(os.path.join(out, "state.json")))["populations"][k]]


def names(out, k):
    return [json.load(open(os.path.join(out, k, "final", f)))["name"] for f in final(out, k) if f.endswith(".json")]


def report(tag, out):
    for k in (HOLISTIC, CONVENTIONAL):
        n = names(out, k)
        dead = [x for x in n if x not in living(out, k)]
        print(f"  {tag} {k:12s} files {len(n)} living {len(living(out, k))} dead-in-final {len(dead)} missing-living {len([x for x in living(out, k) if x not in n])}")


tmp = tempfile.mkdtemp()
# (A)
out = os.path.join(tmp, "A")
Ecology(_evo(), _eco(seasons=2, capacity=6, **CULL), out_dir=out, log=None).run()
real, calls = G.Genotype.save, {"n": 0}
def boom(self, path):
    calls["n"] += 1
    if calls["n"] > 1:
        raise KeyboardInterrupt("simulated kill inside _save_populations")
    real(self, path)
G.Genotype.save = boom
try:
    Ecology.resume(out, seasons=4, log=None).run()
except KeyboardInterrupt as e:
    print("(A)", e)
G.Genotype.save = real
report("after kill ", out)
Ecology.resume(out, seasons=4, log=None).run()
report("after no-op resume", out)

# (B)
out = os.path.join(tmp, "B")
Ecology(_evo(), _eco(seasons=2, capacity=6), out_dir=out, log=None).run()
d = os.path.join(out, HOLISTIC, "final")
extra = ["0999.json", "1000.json", "٣.json", "².json", "best.json", "003.JSON", "003.json.bak", "notes.txt", ".004.json", "config.json"]
for f in extra:
    open(os.path.join(d, f), "w").write("{}")
Ecology.resume(out, seasons=2, log=None).run()
left = set(os.listdir(d))
print("(B) removed:", [f for f in extra if f not in left], " kept:", [f for f in extra if f in left])

# (C)
par = os.path.join(tmp, "Cparent")
Ecology(_evo(), _eco(seasons=2, capacity=6), out_dir=par, log=None).run()
before = {k: final(par, k) for k in (HOLISTIC, CONVENTIONAL)}
fork = os.path.join(tmp, "Cfork")
shutil.copytree(par, fork, ignore=shutil.ignore_patterns("final"))
for k in (HOLISTIC, CONVENTIONAL):
    os.symlink(os.path.join(par, k, "final"), os.path.join(fork, k, "final"))
cfg = json.load(open(os.path.join(fork, "config.json"))); cfg["ecology"].update(CULL)
json.dump(cfg, open(os.path.join(fork, "config.json"), "w"))
Ecology.resume(fork, seasons=4, log=None).run()
for k in (HOLISTIC, CONVENTIONAL):
    print(f"(C) parent {k:12s} final/ files {len(before[k])} -> {len(final(par, k))} (parent's own state.json population {len(living(par, k))})")

# (D)
out = os.path.join(tmp, "D")
Ecology(_evo(), _eco(seasons=2, capacity=6), out_dir=out, log=None).run()
Ecology(_evo(), _eco(seasons=4, capacity=6, **CULL), out_dir=out, log=None).run()  # a fresh launch over it, as `ecology --out` allows
report("(D) fresh-over-finished", out)
shutil.rmtree(tmp)
