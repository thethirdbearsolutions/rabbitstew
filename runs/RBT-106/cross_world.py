"""RBT-106 readout (b) in a named world: RBT-104's `function.py`, imported and run unchanged, with
the WORLD taken from another config.json (RBT-103's --config-from, for function.py).

function.py scores a run's bests in that run's own world.  The patchy and the uniform arms'
champions would then be scored in different worlds, and a compass pays more in the patchy one
(prize.txt), so F(patchy arm) > F(uniform arm) could be the measuring world rather than anything
the arm evolved.  The pre-registered contrast therefore scores BOTH arms' champions in BOTH worlds
(PREREGISTRATION.md §6.2): each arm's own world is function.py as it stands; the other world is this
wrapper.  Only `routed_populations.config` is replaced, for the run named by --run; bodies, seeds,
the decoy, the lesion, the install control and every rule are function.py's.

Usage: cross_world.py --world WORLD_DIR  [function.py's own arguments...]
"""
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))


def main(argv):
    if "--world" not in argv:
        sys.exit("usage: cross_world.py --world WORLD_DIR [function.py arguments]")
    i = argv.index("--world")
    world = argv[i + 1].rstrip("/")
    rest = argv[:i] + argv[i + 2:]
    spec = importlib.util.spec_from_file_location("rbt104_function", os.path.join(_ROOT, "runs", "RBT-104", "function.py"))
    fn = importlib.util.module_from_spec(spec)
    sys.modules["rbt104_function"] = fn
    spec.loader.exec_module(fn)
    from rabbitstew.simulation import SimConfig
    wcfg = SimConfig.from_dict(json.load(open(os.path.join(world, "config.json")))["sim"])
    own = fn.rp.config
    run = rest[rest.index("--run") + 1].rstrip("/")
    fn.rp.config = lambda r: wcfg if r.rstrip("/") == run else own(r)
    print(f"# RBT-106 cross_world: function.py on {run}'s bodies in the world of {world}/config.json "
          f"(patches {wcfg.food.patches}, items {wcfg.food.items}, regrow_delay {wcfg.food.regrow_delay:g})")
    sys.argv = ["function.py"] + rest
    fn.main()


if __name__ == "__main__":
    main(sys.argv[1:])
