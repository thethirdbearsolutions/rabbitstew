import sys, os, json, collections
H0 = os.getcwd()
sys.path.insert(0, "runs/RBT-129/launch"); sys.path.insert(0, "runs/RBT-129/founding-screen-adversary")
import stages, blocks
from test_founding_screen_adversary import _readout_solvency
R = sys.argv[1]
H, D = stages.H, stages.D
# 1. adopt's config check against the real census config
for pid in ("c1-p030-U-L",):
    src = os.path.join(R, f"stage0-{pid}-129001-S")
    b = json.load(open(f"runs/RBT-129/worlds/{pid}.json"))
    want = blocks.config_dict(b["argv"], seed=129001, seasons=60); want.pop("workers", None)
    got = stages._arm_config(src)
    diff = {k: (got.get(k), want.get(k)) for k in set(got) | set(want) if got.get(k) != want.get(k)}
    print(f"adopt config check, census {pid}/129001: {'EQUAL' if got == want else 'DIFFERS ' + str(diff)[:400]}")
# 2. the salt-0 compare's references: rows, and duplicated lineage lines in seasons 0-59
for name in ("stage0-c0-p030-U-L-129001-S", "stage0-c0-p030-U-L-129002-S", "stageP-c0-p030-U-L-129004-S"):
    d = os.path.join(R, name)
    hist = stages._history(d)
    for k in (H, D):
        h, l = stages.half_lines(d, k)
        lines = collections.Counter(l)
        dup = sum(v - 1 for v in lines.values() if v > 1)
        living = collections.Counter(json.loads(x)["generation"] for x in l if json.loads(x).get("death") is None)
        alive = {e["season"]: e["alive"] for e in hist if e["population"] == k and e["season"] <= 59}
        mism = [s for s in alive if living.get(s, 0) != alive[s]]
        print(f"{name} {k:12s}: {len(h)} history rows, {len(l)} lineage lines, duplicate lines {dup},"
              f" living rows != alive at {len(mism)} seasons; alive59 before refill {stages.alive_before_refill(hist, k)}, last {stages.last_alive(hist, k)}")
# 3. the side-effect table's founders and solvency against the readout's, on real halves
for name in ("stage0-c0-p030-U-L-129001-S", "stage0-c0-p030-U-L-129002-S", "stageP-c0-p030-U-L-129004-S"):
    d = os.path.join(R, name)
    for k in (H, D):
        fx = stages.side_effects(d, k)
        n14, s14 = _readout_solvency(d, k, 14)
        n11, s11 = _readout_solvency(d, k, 11)
        print(f"{name} {k:12s}: PR founders {fx['founders']:2d} solvency {stages._fmt(fx['solvency'])}"
              f" | readout-def founders {n14:2d} solvency 0-14 {stages._fmt(s14)} (0-11: {stages._fmt(s11)})")
