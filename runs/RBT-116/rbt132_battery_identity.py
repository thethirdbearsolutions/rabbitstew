"""RBT-132, #471's ruling M1(a): the per-point battery sizes leave every registered point's pool, battery and screen
byte-identical.

    python runs/RBT-116/rbt132_battery_identity.py > runs/RBT-116/rbt132_battery_identity.txt

**What it compares.** ``steer.py`` as it is now, with ``RAISED_N`` empty (as registered) and the screen at the
registered "at least half" rule (``SCREEN_ANY``, GATE_DIAG.md's proposal, is set aside for the comparison: the proposal
changes only that rule; the per-control ``ate_by_host`` column #478 adds at every point but W1 is checked to sum to
``ate`` and then set aside), against two earlier commits:
- W1 against ``ce69f17``, RBT-116's registered code;
- RBT-129's 18 points against ``914667e``, #459's merge, where they were added.

**On each point:**
- ``draw_pool`` (plain and extended);
- ``assign_battery`` on its admissible prefixes of 30, 35, 36, 37, 50 and 96 draws;
- ``screen_draws`` with a deterministic stand-in season, at four admissible shares that cover the plain pass, the
  extension and the gate failure.

The stand-in season eats on a draw iff a hash of the draw is below the share, so the screen's own logic (the table,
the extension, the battery) is what is compared.  No simulation runs, and no point's pool season runs.
"""
import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def at(sha, name):
    src = subprocess.run(["git", "show", f"{sha}:runs/RBT-116/steer.py"], capture_output=True, text=True, cwd=ROOT, check=True).stdout
    path = os.path.join(tempfile.mkdtemp(), f"{name}.py")
    open(path, "w").write(src)
    return load(name, path)


def pairs(draws):
    return [(d.terrain_seed, d.start_seed) for d in draws]


def bat(b):
    return None if b is None else {k: pairs(getattr(b, k)) for k in ("stage1", "stage2", "confirm")}


def season_at(share):
    def season(g, cfg, d, cond):
        h = int(hashlib.sha256(f"{d.terrain_seed},{d.start_seed}".encode()).hexdigest()[:8], 16) / 16 ** 8
        return types.SimpleNamespace(food=1.0 if h < share else 0.0)
    return season


def compare(old, new, point, label):
    n = 0
    for ext in (False, True):
        a = pairs(old.draw_pool(point, extended=ext))
        b = pairs(new.draw_pool(point, extended=ext))
        assert a == b, f"{label} {point}: draw_pool(extended={ext}) differs"
        n += 1
    pool = new.draw_pool(point, extended=True)
    for k in (30, 35, 36, 37, 50, 96):
        a = bat(old.assign_battery([old.Draw(*p) for p in pairs(pool[:k])]))
        b = bat(new.assign_battery(pool[:k], point))
        assert a == b, f"{label} {point}: assign_battery on {k} differs"
        n += 1
    any_rule, new.SCREEN_ANY = new.SCREEN_ANY, frozenset()  # the registered rule everywhere, for the comparison
    try:
        results = [(share, old.screen_draws(["h"], None, point, season_at(share)), new.screen_draws(["h"], None, point, season_at(share)))
                   for share in (0.9, 0.5, 0.45, 0.2)]
    finally:
        new.SCREEN_ANY = any_rule
    for share, ra, rb in results:
        # #478 S-1 adds each control's 0/1 (``ate_by_host``) to the table at every point but W1: it must sum to ``ate``,
        # and the table is otherwise unchanged
        assert point != "W1" or all("ate_by_host" not in r for r in rb["table"]), "W1's table must stay as registered"
        assert all(sum(r.get("ate_by_host", [r["ate"]])) == r["ate"] for r in rb["table"])
        rb = dict(rb, table=[{k: v for k, v in r.items() if k != "ate_by_host"} for r in rb["table"]])
        for key in ("table", "extended", "admissible", "passed"):
            assert ra[key] == rb[key], f"{label} {point}: screen_draws({share}) {key} differs"
        assert bat(ra["battery"]) == bat(rb["battery"]), f"{label} {point}: screen_draws({share}) battery differs"
        n += 1
    return n


def main():
    new = load("steer_now", os.path.join(HERE, "steer.py"))
    assert new.RAISED_N == {}, "RAISED_N must be empty as registered"
    w1_base, pts_base = at("ce69f17", "steer_ce69f17"), at("914667e", "steer_914667e")
    print("# rbt132_battery_identity.py: steer.py now (RAISED_N empty) against ce69f17 (W1) and 914667e (RBT-129's 18 points)")
    n = compare(w1_base, new, "W1", "ce69f17")
    print(f"W1: draw_pool x2, assign_battery x6, screen_draws x4 IDENTICAL ({n} comparisons)")
    total = n
    for pid in new.RBT129_POINTS:
        total += compare(pts_base, new, pid, "914667e")
    print(f"RBT-129's {len(new.RBT129_POINTS)} points: each draw_pool x2, assign_battery x6, screen_draws x4 IDENTICAL")
    print(f"# IDENTICAL: {total} comparisons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
