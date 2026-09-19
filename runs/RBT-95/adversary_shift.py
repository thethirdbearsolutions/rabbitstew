"""RBT-95 adversary probe (items 1 and 2, the RBT-89 delegate): three shifts the switch accepts, read
against docs/held-out-challenges.md section 5 and section 8.

1. ``terrain=flat`` at the onset: ``draw_terrain_seed`` draws nothing when the terrain is not random,
   so from the onset the shifted arm's terrain stream is one draw behind the control's per season and
   the start seeds diverge (the shifted arm's start seed is the control's terrain seed).  The C4
   challenge arm and its control and null arms then no longer share worlds after the onset.
2. ``food.regrow_delay=45`` at the onset: accepted, but ``Ecology.persistent`` is fixed at construction,
   so the simulation regrows food at its own spot while the ecology carries no arena state.
3. ``max_age=1`` at the onset: every living individual dies that season, and a fauna with nobody alive
   writes no history row (pre-existing), which is the row the protocol's classes D and E read.

Uses the test helpers of tests/test_ecology_switches.py; tiny runs; nothing read as a result.
"""
import importlib.util
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, "tests")
spec = importlib.util.spec_from_file_location("t", "tests/test_ecology_switches.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
from rabbitstew.ecology import Ecology  # noqa: E402

tmp = pathlib.Path(tempfile.mkdtemp())
print("# RBT-95 adversary: three accepted shifts, read against the protocol\n")
print("## 1. terrain=flat at season 3: terrain and start seeds against the control\n")
base = t._run(tmp, "base", t._eco(seasons=6))
flat = t._run(tmp, "flat", t._eco(seasons=6, shift_at=3, shift="terrain=flat"))
hb = json.load(open(base / "history.json"))["history"]
hf = json.load(open(flat / "history.json"))["history"]
for eb, ef in zip(hb[::2], hf[::2]):
    print(f"  season {eb['season']}: terrain seed {eb['terrain_seed']} vs {ef['terrain_seed']}; "
          f"start seed {eb['start_seed']} vs {ef['start_seed']}  "
          f"{'SAME' if eb['start_seed'] == ef['start_seed'] else 'DIVERGED (the shifted start seed is the control terrain seed: one draw behind)'}")
print("\n## 2. food.regrow_delay=45 at season 1: accepted, and the ecology's persistence flag\n")
e = Ecology(t._evo(), t._eco(seasons=3, shift_at=1, shift="food.regrow_delay=45"), out_dir=str(tmp / "rd"), log=None)
print(f"  accepted at construction; e.persistent = {e.persistent}")
e.step(); e.step()
print(f"  after the onset: sim.food.regrow_delay = {e.evo.sim.food.regrow_delay}; e.persistent = {e.persistent}  "
      f"{'(the simulation is persistent, the ecology carries no arena state)' if e.evo.sim.food.regrow_delay > 0 and not e.persistent else ''}")
print("\n## 3. max_age=1 at season 1: what the history table shows when a fauna dies out\n")
e = Ecology(t._evo(), t._eco(seasons=4, shift_at=1, shift="max_age=1"), out_dir=str(tmp / "ma"), log=None)
for _ in range(4):
    e.step()
rows = [(x["season"], x["population"], x["deaths"], x["alive"]) for x in e.history]
print(f"  history rows (season, fauna, deaths, alive): {rows}")
print(f"  seasons with a row: {sorted(set(r[0] for r in rows))} of 4 run; a fauna at alive = 0 writes no row after its extinction season.")
