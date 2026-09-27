"""RBT-125 adversary: RBT-120's motor_budget strip and RBT-125's perception strip, together (the merge at c40ecd5).

Checks, on EvolutionConfig.to_dict() and SimConfig.to_dict(), built through the CLI as experiments build them:
  off/off   neither key family written
  on/off, off/on, on/on   exactly the families that are on written, and from_dict round-trips both
  smell_contrast > 0 with smell_tau at its default 2.0: is tau written?  (it is stripped: the config.json then
  does not state the time constant of the channel it ran)
"""
import json
from rabbitstew.cli import build_parser, evolve_config
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.simulation import PERCEPTION_DEFAULTS, SimConfig

BASE = ["evolve", "--food-items", "12", "--out", "/nonexistent"]
MB = ["--motor-budget", "1.77"]
PK = ["--smell-contrast", "2.5", "--smell-tau", "1", "--eat-from", "root"]
ok = True
for name, extra in (("off/off", []), ("budget on", MB), ("pack on", PK), ("both on", MB + PK)):
    e = evolve_config(build_parser().parse_args(BASE + extra))
    for label, d in (("EvolutionConfig", e.to_dict()["sim"]), ("SimConfig", e.sim.to_dict())):
        d = json.loads(json.dumps(d))
        has_mb = "motor_budget" in d["world"]
        has_pk = sorted(set(PERCEPTION_DEFAULTS) & set(d["food"]))
        want_mb, want_pk = bool(MB[0] in extra), bool(PK[0] in extra)
        good = has_mb == want_mb and bool(has_pk) == want_pk
        rt = SimConfig.from_dict(d)
        good &= rt.world.motor_budget == e.sim.world.motor_budget and rt.food == e.sim.food
        ok &= good
        print(f"{name:10s} {label:16s} motor_budget written {has_mb!s:5s} perception keys {has_pk}  round-trip+expected: {'ok' if good else 'WRONG'}")
    rt = EvolutionConfig.from_dict(json.loads(json.dumps(e.to_dict())))
    print(f"{'':10s} EvolutionConfig round-trip: {'ok' if rt.sim.food == e.sim.food and rt.sim.world.motor_budget == e.sim.world.motor_budget else 'WRONG'}")
e = evolve_config(build_parser().parse_args(BASE + ["--smell-contrast", "2.5"]))
print(f"\nG 2.5 at the default tau: config.json food block carries smell_tau? {'smell_tau' in e.to_dict()['sim']['food']}  "
      f"(keys written: {sorted(set(PERCEPTION_DEFAULTS) & set(e.to_dict()['sim']['food']))})")
print("ALL OK" if ok else "FAILURES")
