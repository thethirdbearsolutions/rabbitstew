"""RBT-107: fork a base ecology directory, stopped at the end of season T - 1, into an event arm that takes its event at T.

    python runs/RBT-107/fork.py BASE_DIR OUT_DIR {shift|cull20}

Copies BASE_DIR to OUT_DIR and writes the event into OUT_DIR/config.json: T = the state's season (the next season to
play), shift -> ecology.shift_at = T, ecology.shift = "terrain=flat" (C4, as RBT-101's arms record it);
cull20 -> ecology.cull_at = T, ecology.cull = "holistic=20,conventional=20" (as RBT-92's cull20 arms record it).
Then `rabbitstew ecology --resume --seasons N --out OUT_DIR` plays it.  fork_check.sh shows the result is byte-identical
to a fresh run with the flag.  Refuses a directory whose config already carries an event.
"""
import json
import os
import shutil
import sys

EVENTS = {"shift": {"shift_at": None, "shift": "terrain=flat"},
          "cull20": {"cull_at": None, "cull": "holistic=20,conventional=20"}}


def main(base, out, kind):
    cfg = json.load(open(os.path.join(base, "config.json")))
    eco = cfg["ecology"]
    if any(eco.get(k) is not None for k in ("shift_at", "shift", "cull_at", "cull")):
        sys.exit(f"{base} already carries an event; fork only a plain base")
    T = int(json.load(open(os.path.join(base, "state.json")))["season"])
    if os.path.exists(out):
        sys.exit(f"{out} exists")
    shutil.copytree(base, out)
    ev = dict(EVENTS[kind])
    ev[next(k for k in ev if k.endswith("_at"))] = T
    eco.update(ev)
    with open(os.path.join(out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"forked {base} at season {T} into {out}: {ev}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
