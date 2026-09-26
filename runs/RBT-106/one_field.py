"""RBT-106 item 1: is patchiness one field, and is the run unchanged at its default?

The flag is the existing `--food-patches N` (`sim.food.patches`, RBT-19); no code is added.

Check 1 (byte identity at the default).  A short run of RBT-90 part 2's command with
`--food-patches 0` written out must pass RBT-104's `byte_identity.default` (imported): seasons.txt
rows byte-identical to the committed part-2 rows, config.json equal outside seasons, generations and
workers (fields later tickets added at their defaults tolerated and named).

Check 2 (one field).  A short run with `--food-patches 3` must write a config.json that differs from
the committed part-2 one in exactly one field outside those three: sim.food.patches, 0 -> 3.  In
particular `regrow_delay` stays 0, so the ecology's persistent-arena mode (RBT-19; Ecology.persistent
is regrow_delay > 0) stays off: RBT-103's "12 items, 3 patches" world had regrow_delay 45, which is a
second field and a different ecology, and is NOT the world used here.

Check 3 (the seeded pair differs in the world only).  Two short runs loading RBT-104's seeded
founders (w = 1), at patches 0 and 3, must save byte-identical founders of both faunas (the flag
touches no genome, no founder draw and no age), and differ in their seasons from season 0 on (the
world is the one thing that changed, and both faunas forage in it).

Usage: one_field.py P0_RUN P3_RUN S1P0_RUN S1P3_RUN SEED
"""
import glob
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_byte_identity", os.path.join(_ROOT, "runs", "RBT-104", "byte_identity.py"))
bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bi)


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, p + k + "."))
        else:
            out[p + k] = v
    return out


def one_field(run, seed):
    got = json.load(open(f"{run}/config.json"))
    ref = json.load(open(os.path.join(_ROOT, "runs", "RBT-90", f"forage-{seed}", "config.json")))
    extra = bi._cc.added_at_default(got, ref)
    a, b = flat(bi.strip(got)), flat(bi.strip(ref))
    diff = sorted(k for k in set(a) | set(b) if a.get(k, "<absent>") != b.get(k, "<absent>"))
    print(f"# RBT-106 check 2: --food-patches 3 against RBT-90 part 2's config, seed {seed}\n")
    for k in diff:
        print(f"  differs: {k}: committed {b.get(k, '<absent>')!r} -> here {a.get(k, '<absent>')!r}")
    print(f"  fields added since by other tickets, at their defaults (tolerated): {extra}")
    print(f"  sim.food.regrow_delay here: {a['sim.food.regrow_delay']!r} (persistent arenas off: {a['sim.food.regrow_delay'] == 0})")
    ok = diff == ["sim.food.patches"] and a["sim.food.patches"] == 3 and a["sim.food.regrow_delay"] == 0
    print(f"exactly one field differs, sim.food.patches 0 -> 3: {'YES' if ok else 'NO'}")
    return ok


def founders(p0, p3):
    print("\n# RBT-106 check 3: the seeded pair, patches 0 against 3, RBT-104's w = 1 founders loaded in both\n")
    ok = True
    for kind in ("holistic", "conventional"):
        names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(p0, kind, "genomes", "*0-*.json")))
        names = [n for n in names if json.load(open(os.path.join(p0, kind, "genomes", n))).get("parents") in ([], None)]
        same = sum(open(os.path.join(p0, kind, "genomes", n), "rb").read() == open(os.path.join(p3, kind, "genomes", n), "rb").read()
                   for n in names if os.path.exists(os.path.join(p3, kind, "genomes", n)))
        print(f"  {kind} founders saved at birth: {same} of {len(names)} byte-identical")
        ok &= same == len(names) and len(names) == 60
    bi.measure.summarise(p0)
    bi.measure.summarise(p3)
    r0, r3 = bi.rows(f"{p0}/seasons.txt"), bi.rows(f"{p3}/seasons.txt")
    first = next((i for i, (x, y) in enumerate(zip(r0[1:], r3[1:])) if x != y), None)
    si = r0[0].split("\t").index("season")
    print(f"  seasons.txt: first differing row {first} (season {r0[1 + first].split(chr(9))[si] if first is not None else '-'}); "
          f"the world differs from season 0, for both faunas")
    ok &= first == 0
    print(f"founders identical, seasons differ from season 0: {'YES' if ok else 'NO'}")
    return ok


if __name__ == "__main__":
    p0, p3, s1p0, s1p3, seed = sys.argv[1:6]
    print(f"(RBT-106 check 1: {p0} is part 2's command with --food-patches 0 written out; RBT-104's check, imported, prints the header below)\n")
    r1 = bi.default(p0, seed)
    r2 = one_field(p3, int(seed))
    r3 = founders(s1p0, s1p3)
    sys.exit(0 if (r1 == 0 and r2 and r3) else 1)
