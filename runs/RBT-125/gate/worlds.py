"""RBT-125 world gate: the cells' worlds, written as config.json files the RBT-103 harness takes by --config-from.

Every cell is RBT-90 part 2's committed world (runs/RBT-90/forage-801/config.json: random terrain, 12 items, work
cost 0.03/kJ, 15 s, random start, eat from any geom centre) with ONLY its food block changed:

  U    the committed uniform world, as it is (instant random regrowth, sum smell, decay 1)
  HP   RBT-106's one-field patchy world (runs/RBT-106/world-patchy): patches = 3, nothing else
  PW   RBT-121 audit C's perception-demanding layout: 2 patches of 0.4 m in a 4 m disc, own-spot regrowth after
       60 s (longer than the bout: an eaten item does not come back within it), log smell, decay 1.5

and G the RBT-125 smell contrast (food.smell_contrast, tau 2 s); G = 0 is the legacy reading.  The eating rule is
the committed one in every cell (the gate is the smell channel's; the eating rules' side effects are read apart).

    python runs/RBT-125/gate/worlds.py      # (re)writes runs/RBT-125/gate/worlds/<cell>/config.json
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BASE = os.path.join(ROOT, "runs", "RBT-90", "forage-801", "config.json")

LAYOUTS = {
    "U": {},
    "HP": {"patches": 3},
    "PW": {"patches": 2, "patch_radius": 0.4, "radius": 4.0, "regrow_delay": 60.0, "smell": "log", "decay": 1.5},
}
GS = (0.0, 2.5, 10.0)
TAU = 2.0
#: the ruling's M5 sensitivity cell (descriptive): PW at G = 2.5 with tau = 1 s, RBT-116's draft value
EXTRA = (("PW", 2.5, 1.0),)


def cell(layout, G, tau=TAU):
    return f"{layout}-G{G:g}" + ("" if tau == TAU else f"-tau{tau:g}")


def world(layout, G, tau=TAU):
    d = copy.deepcopy(json.load(open(BASE)))
    d["sim"]["food"].update(LAYOUTS[layout])
    if G:
        d["sim"]["food"].update(smell_contrast=float(G), smell_tau=float(tau))
    return d


def main():
    for layout, G, tau in [(l, G, TAU) for l in LAYOUTS for G in GS] + list(EXTRA):
        out = os.path.join(HERE, "worlds", cell(layout, G, tau))
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "config.json"), "w") as f:
            json.dump(world(layout, G, tau), f, indent=2)
        print(out, json.dumps(world(layout, G, tau)["sim"]["food"]))


if __name__ == "__main__":
    main()
