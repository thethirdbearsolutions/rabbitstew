"""RBT-102 adversary, probe 2: can RBT-102's instrument see a carrier at all?

"Zero carriers" is evidence only if the pipeline RBT-102 ran says yes on genomes that carry the
structure. RBT-102's own positive control installs RBT-87's motif into 20 window genomes per arm and
calls `sr.motif_units` on them directly. This probe goes further in three ways:

  (a) NATURAL CARRIERS, not installs. RBT-91's drift arrivals are the only genomes known to carry
      the routed structure without having it written in. They are regenerated exactly (RBT-91's
      seeding: SeedSequence([MASTER_SEED, crc32(pool), k, i]), parent pool[i % len(pool)], 19
      `mutate_controller` steps, add 0.15, rem 0.1), saved to JSON, and read back through
      `analyse.read_genome` -- RBT-102's own reader -- under the PART-2 arm's SimConfig, not the
      pool's. If part 2's synthesis differed from W4b-801's / P-801's in anything the predicate
      touches, this is where it would show.
  (b) RBT-97's P-801 route: RBT-87's motif installed on P-801's best_gen0590 at sub-paying and
      paying w, both signs, through the same reader under the part-2 SimConfig.
  (c) THE WHOLE PIPELINE, END TO END. A copy of a restored part-2 arm in which the genome files of
      24 individuals alive in the window are overwritten -- 12 with RBT-87's motif installed at
      w = 1 (sub-paying: the regime RBT-102 asks about), 12 with natural RBT-91 drift carriers --
      and `runs/RBT-102/analyse.py` is run on it UNMODIFIED, probe on. It must report the planted
      individuals as carriers, in the right seasons, move X off zero, and sign them.

It also records (d) how often RBT-91's PARENTS already wire wheel noses into a global unit, for the
comparison in probe 3.

    python runs/RBT-102/adversary/detect.py runs/RBT-90/forage-4 SCRATCH_DIR
"""
import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(ROOT)
_argv, sys.argv = sys.argv, ["analyse.py"]
_s = importlib.util.spec_from_file_location("an", os.path.join(ROOT, "runs", "RBT-102", "analyse.py"))
an = importlib.util.module_from_spec(_s)
_s.loader.exec_module(an)
sys.argv = _argv
sr, ra = an.sr, an.ra
rbt78 = sr.rbt78
_g = importlib.util.spec_from_file_location("gm", os.path.join(ROOT, "scripts", "genotype_motif.py"))
gm = importlib.util.module_from_spec(_g)
_g.loader.exec_module(gm)

from dataclasses import replace
from rabbitstew.genetics import mutate_controller
from rabbitstew.genotype import Genotype
from rabbitstew.synthesis import synthesize

N_PER_POOL = 12


def drift_hits():
    """RBT-91's committed arrival indices, from its committed readout."""
    txt = open("docs/artifacts/RBT-91-drift-baseline.txt").read()
    hits = {}
    for pool, i in re.findall(r"^\s+(W4b-801-bests|P-801-final60) lineage (\d+):", txt, re.M):
        hits.setdefault(pool, []).append(int(i))
    return hits


def regenerate(label, i, k=19, add=0.15, rem=0.1):
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=add, remove_link_rate=rem)
    rng = np.random.default_rng(np.random.SeedSequence([rbt78.MASTER_SEED, zlib.crc32(label.encode()), k, i]))
    g = pool[i % len(pool)]
    for _ in range(k):
        g = mutate_controller(g, rng, mcfg)
    return g, cfg


def nose_links(ph):
    noses = sr._wheel_noses(ph)
    w = {}
    for s, d, x in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + x
    one = both = False
    for k, ui in enumerate(ph.units):
        if ui.part is not None or ui.unit.kind == "sensor":
            continue
        a, b = w.get((noses[0], k), 0.0), w.get((noses[1], k), 0.0)
        one |= a != 0.0 or b != 0.0
        both |= a != 0.0 and b != 0.0
    return one, both


def main():
    arm, scratch = sys.argv[1].rstrip("/"), sys.argv[2]
    os.makedirs(scratch, exist_ok=True)
    arm_cfg = json.load(open(os.path.join(arm, "config.json")))
    an._init(arm_cfg["sim"])
    print("# RBT-102 adversary probe 2: can the instrument see a carrier?\n")
    print(f"reader: runs/RBT-102/analyse.py read_genome, under {arm}'s SimConfig (part 2)\n")

    # (a) natural drift carriers
    hits = drift_hits()
    print("## (a) RBT-91's drift arrivals, regenerated and read by RBT-102's reader\n")
    print(f"  committed arrivals parsed: " + ", ".join(f"{p} {len(v)}" for p, v in hits.items()))
    print("| pool | lineage | predicate, pool's own SimConfig | read_genome, part-2 SimConfig | whole-brain a | links-alone a |")
    print("|---|---|---|---|---|---|")
    natural = []
    tot = own_ok = part2_ok = 0
    for label, idx in hits.items():
        for i in idx[:N_PER_POOL]:
            g, cfg = regenerate(label, i)
            own = bool(sr.motif_units(synthesize(g, cfg.sim.synthesis)))
            p = os.path.join(scratch, f"drift-{label}-{i}.json")
            g.save(p)
            _, carrier, _, wa, la = an.read_genome(p)
            tot += 1
            own_ok += own
            part2_ok += carrier
            natural.append(p)
            print(f"| {label} | {i} | {'YES' if own else 'no'} | {'YES' if carrier else 'no'} | "
                  f"{wa if wa is None else f'{wa:+.4f}'} | {la if la is None else f'{la:+.4f}'} |")
    print(f"\n  regenerated {tot}: predicate YES on its own synthesis {own_ok}/{tot}; "
          f"RBT-102's reader under part 2's SimConfig YES {part2_ok}/{tot}")
    same = json.dumps(rbt78._load("P-801-final60")[0].sim.synthesis.__dict__, default=str, sort_keys=True) == \
        json.dumps(an.SIM.synthesis.__dict__, default=str, sort_keys=True)
    print(f"  P-801's synthesis config identical to part 2's: {same}")

    # (b) RBT-97's route: the motif installed on P-801
    print("\n## (b) RBT-87's routed motif installed on P-801 best_gen0590 (RBT-97 item 5), part-2 reader\n")
    p801 = Genotype.load("runs/RBT-19/P-801/conventional/best_gen0590.json")
    ok = n = 0
    row = []
    for w in (0.25, 1.0, 8.0, 16.0):
        for sign in (+1.0, -1.0):
            p = os.path.join(scratch, f"p801-w{w}-{sign:+.0f}.json")
            gm.install(p801, w, sign=sign).save(p)
            _, carrier, _, wa, _ = an.read_genome(p)
            ok += carrier
            n += 1
            row.append(f"w={w:g}{'+' if sign > 0 else '-'}: {'YES' if carrier else 'no'} (a {wa:+.3f})")
    bare = os.path.join(scratch, "p801-bare.json")
    p801.save(bare)
    print("  " + "; ".join(row))
    print(f"  detected {ok}/{n}; bare P-801 best_gen0590: {'YES' if an.read_genome(bare)[1] else 'no'}")

    # (c) the whole pipeline, end to end, on a planted copy of a real arm
    print("\n## (c) analyse.py, unmodified, on a copy of the arm with 24 planted carriers\n")
    dst = os.path.join(scratch, "planted-" + os.path.basename(arm))
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.join(dst, "conventional"))
    for f in ("config.json", "state.json", "lineage.jsonl"):
        shutil.copy(os.path.join(arm, f), dst)
    shutil.copytree(os.path.join(arm, "conventional", "genomes"), os.path.join(dst, "conventional", "genomes"))
    alive = {}
    for line in open(os.path.join(arm, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] == "conventional" and "death" not in r:
            alive.setdefault(r["generation"], []).append(r["name"])
    window = sorted({n for s, v in alive.items() if 300 <= s <= 599 for n in v})
    rng = np.random.default_rng(1020)
    pick = list(rng.choice(window, size=24, replace=False))
    planted_seasons = set()
    for j, name in enumerate(pick):
        tgt = os.path.join(dst, "conventional", "genomes", f"{name}.json")
        if j < 12:
            g = gm.install(Genotype.load(tgt), 1.0, sign=+1.0 if j % 2 else -1.0)
        else:
            g = Genotype.load(natural[j - 12])
        g.name = name
        g.parents = Genotype.load(tgt).parents
        g.save(tgt)
        planted_seasons |= {s for s, v in alive.items() if name in v}
    exp_X = np.mean([sum(n in pick for n in alive[s]) / len(alive[s]) for s in sorted(alive) if 300 <= s <= 599])
    print(f"  planted: 12 installs at w = 1 (sub-paying), 12 natural RBT-91 drift carriers; "
          f"seasons touched {len(planted_seasons)}; expected window X {100 * exp_X:.4f}%")
    out = subprocess.run([sys.executable, "runs/RBT-102/analyse.py", dst, "--procs", "4"],
                         capture_output=True, text=True)
    open(os.path.join(scratch, "planted-analyse.txt"), "w").write(out.stdout + out.stderr)
    summ = json.loads(out.stdout.strip().splitlines()[-1][len("SUMMARY "):])
    print(f"  analyse.py exit {out.returncode}; its SUMMARY: X {100 * summ['X']:.4f}%, seasons with a carrier "
          f"{summ['seasons_any']}, carriers born {summ['carriers_born']} (de novo {summ['de_novo']}), window "
          f"carriers {summ['window_carriers']}, compass {summ['compass']}, ANTI {summ['anti']}, undetermined "
          f"{summ['undetermined']}, positive control {summ['pc_detected']}/{summ['pc_total']}")
    good = summ["window_carriers"] == 24 and abs(summ["X"] - exp_X) < 1e-12 and summ["seasons_any"] == len(planted_seasons)
    print(f"  end-to-end: {'PASSED' if good else 'FAILED'} (24 window carriers expected, X and seasons as planted)")

    # (d) do RBT-91's parents already wire noses into the global brain?
    print("\n## (d) RBT-91's parents against part-2 founders: wheel noses into a global unit\n")
    for label in rbt78.POOLS:
        cfg, pool = rbt78._load(label)
        f = [nose_links(synthesize(g, cfg.sim.synthesis)) for g in pool]
        print(f"  {label}: {len(pool)} parents; >= 1 nose into a global unit {sum(x[0] for x in f)}; "
              f"both noses into one global unit {sum(x[1] for x in f)}")
    founders = [p for p in glob.glob(os.path.join(arm, "conventional", "genomes", "c0-*.json"))]
    f = [nose_links(synthesize(Genotype.load(p), an.SIM.synthesis)) for p in founders]
    print(f"  part-2 founders ({arm}): {len(f)}; >= 1 nose into a global unit {sum(x[0] for x in f)}; "
          f"both noses into one global unit {sum(x[1] for x in f)}")


if __name__ == "__main__":
    main()
