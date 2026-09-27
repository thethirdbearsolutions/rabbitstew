"""Probe 6: the core-hour arithmetic (DESIGN §11.2, power.py part 4), re-derived, with the probe cost re-costed from
RBT-116's own per-season figure and staging (PR #400 r7 §9: 0.35 CPU-s per solo season; stage 1 = 4 draws x 2
conditions; stage 2 = 16 draws x 4 conditions, reached by 75% of holistic and every Pioneer; confirmation 16 x 2 for
~10%), and with the M and N arms forked from S at season 60 (K1 already requires them byte-identical to 59).

python3 probe_budget.py
"""
CS = (20.0, 25.0)
SOLO = 0.35  # CPU-s per solo season (RBT-116 §9)


def h(seasons, cs):
    return seasons * cs / 3600.0


def per_member_seasons(frac_stage2):
    screen = 4 * 2
    stage2 = 16 * 4 * frac_stage2
    confirm = 16 * 2 * 0.10
    intact_decoy = 8 * 4  # the design's separate 8-draw intact/decoy/lesion/motors-off battery
    return screen + stage2 + confirm + intact_decoy, screen + stage2 + confirm  # separate battery / shared draws


print("## 1. The design's arithmetic, re-derived")
for cs in CS:
    side = merged = h(300, cs)
    null = 0.5 * h(300, cs) * 0.85
    per_seed = side + merged + null + 0.40
    pilot = 3 * 4 * per_seed + 3 * 0.25
    census = 150 * 3 * h(60, cs) + 12 * 2.0
    s1 = 36 * (8 * per_seed + 0.25)
    s2a = 16 * (8 * per_seed + 0.25)
    s2b = 20 * 8 * per_seed
    tot = pilot + census + s1 + s2a + s2b
    print(f"  @{cs:.0f} core-s: per seed-point {per_seed:.2f}; P {pilot:.0f}, 0 {census:.0f}, 1 {s1:.0f}, 2a {s2a:.0f}, "
          f"2b {s2b:.0f}; total {tot:.0f}; /40 cores = {tot / 40:.0f} h")

print()
print("## 2. Probes per seed re-costed (20 probed members x 2 faunas x 2 time points = 80 members a seed)")
for frac in (0.75, 1.0):
    sep, shared = per_member_seasons(frac)
    for label, s in (("separate intact/decoy battery", sep), ("battery shares STEERS' draws", shared)):
        ch = 80 * s * SOLO / 3600
        print(f"  stage-2 reach {frac:.2f}, {label:30s}: {s:5.1f} solo seasons a member -> {ch:.2f} core-h a seed "
              f"(design: 0.40)")
print("  Planted set per point (design 0.25 core-h): 4 hosts x [(a) 1 + (b) 1 + (c) 1 + (d) 3 + (e) 3 + (f) 1] + motors-off")
hosts = 4 * (1 + 1 + 1 + 3 + 3 + 1) + 1
tune = 4 * (8 + 6 + 6) * 4 * 2  # (b) ~8-cell grid, (c) and (f) 6 variants each, 4 screening draws x 2 conditions
battery = hosts * per_member_seasons(1.0)[1]
g1_scan = 4 * 16 * 16 * 2  # a first paying rung needs G1's rung scan: 4 rungs x 16 hosts x 16 draws x 2 conditions
screen = 64 * 8  # the reachability screen: 64 pool draws x ~8 positive hosts
tot = (tune + battery + g1_scan + screen) * SOLO / 3600
print(f"    ~{tune} tuning + {battery:.0f} battery + {g1_scan} rung scan + {screen} screen solo seasons -> {tot:.2f} core-h a point")

print()
print("## 3. Totals with the re-costed probes (0.47-0.93 core-h a seed; planted set 0.8 core-h a point)")
for cs in CS:
    for probes in (0.47, 0.93):
        for fork in (False, True):
            side = h(300, cs)
            merged = h(240, cs) if fork else h(300, cs)
            null = 0.5 * (h(240, cs) if fork else h(300, cs)) * 0.85
            per_seed = side + merged + null + probes
            plants = 0.8
            pilot = 3 * 4 * per_seed + 3 * plants
            census = 150 * 3 * h(60, cs) + 12 * 2.0
            s1 = 36 * (8 * per_seed + plants)
            s2a = 16 * (8 * per_seed + plants)
            s2b = 20 * 8 * per_seed
            tot = pilot + census + s1 + s2a + s2b
            print(f"  @{cs:.0f} core-s, probes {probes:.2f}, M/N {'forked at 60' if fork else 'from season 0'}: "
                  f"per seed {per_seed:.2f}; total {tot:.0f} core-h")

print()
print("## 4. Wall time: R-B draws on Stage-2a points, so 2b cannot run beside 2a (DESIGN §11.1 step 4)")
for cs in CS:
    per_seed = 2 * h(300, cs) + 0.5 * h(300, cs) * 0.85 + 0.40
    s2a, s2b = 16 * (8 * per_seed + 0.25), 20 * 8 * per_seed
    arm_wall = h(300, cs) / 2  # one arm at WORKERS = 2: the critical path of a stage is at least one arm
    print(f"  @{cs:.0f} core-s: one 300-season arm at 2 workers = {arm_wall:.1f} h wall; 2a then 2b serially adds at least "
          f"{arm_wall:.1f} h of critical path; 2a+2b core-h {s2a + s2b:.0f} unchanged")
