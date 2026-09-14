"""The composite "link-driven effector AND no linked oscillator" is two conditions, and on this
arm they come apart. Report each along the whole descent DAG (RBT-84).

The champion he988 has twelve link-driven effectors and two linked oscillators, so the composite
reads False entirely on the oscillator clause while the drive clause holds. Scoring only the
composite would hide that the two halves of RBT-28's finding behave in opposite directions here.

usage: halves.py RUN_DIR [KIND]
"""
import importlib.util, json, os, pathlib, sys
from collections import deque
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec); spec.loader.exec_module(adv)

run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-84/forage-807"
kind = sys.argv[2] if len(sys.argv) > 2 else "holistic"
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
rows = [json.loads(l) for l in open(f"{run}/lineage.jsonl") if l.strip()]
last = {r["name"]: r for r in rows if r["population"] == kind}
fs = max(r["generation"] for r in rows if r["population"] == kind)
start = max((r for r in rows if r["population"] == kind and r["generation"] == fs),
            key=lambda r: r["fitness"])["name"]

seen, q = {}, deque([start])
while q:
    n = q.popleft()
    if n in seen:
        continue
    p = os.path.join(run, kind, "genomes", f"{n}.json")
    seen[n] = adv.wiring(Genotype.load(p), cfg) if os.path.exists(p) else None
    for par in (last.get(n) or {}).get("parents", []):
        if par not in seen:
            q.append(par)

known = {n: c for n, c in seen.items() if c}
founders = [n for n in seen if not (last.get(n) or {}).get("parents")]
fd = [seen[n]["eff_driven"] > 0 for n in founders if seen.get(n)]
fo = [seen[n]["osc_linked"] == 0 for n in founders if seen.get(n)]
drive = [c["eff_driven"] > 0 for c in known.values()]
osc = [c["osc_linked"] == 0 for c in known.values()]

print(f"{run} {kind}: champion {start}  eff_driven={seen[start]['eff_driven']}  "
      f"osc_linked={seen[start]['osc_linked']}")
print(f"DAG: {len(known)} ancestors, {len(founders)} founders, "
      f"{sum(1 for n in seen if seen[n] is None)} genomes missing\n")
print(f"{'half':34} {'champion':>9} {'founders':>10} {'ancestors lacking it':>21}")
print(f"{'a link into a live effector':34} {str(seen[start]['eff_driven'] > 0):>9} "
      f"{f'{sum(fd)}/{len(fd)}':>10} {f'{len(drive) - sum(drive)} of {len(drive)}':>21}")
print(f"{'no outgoing oscillator link':34} {str(seen[start]['osc_linked'] == 0):>9} "
      f"{f'{sum(fo)}/{len(fo)}':>10} {f'{len(osc) - sum(osc)} of {len(osc)}':>21}")
print(json.dumps({"champion": start, "ancestors": len(known), "founders": len(founders),
                  "drive_champion": seen[start]["eff_driven"] > 0, "drive_founders": sum(fd),
                  "drive_lacking": len(drive) - sum(drive),
                  "osc_champion": seen[start]["osc_linked"] == 0, "osc_founders": sum(fo),
                  "osc_lacking": len(osc) - sum(osc)}))
