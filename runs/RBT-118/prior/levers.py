"""RBT-118 prior (EXPLORATORY, descriptive only): body-model levers of each fauna's living population, from ckpt restores.

    python runs/RBT-118/prior/levers.py [--scratch DIR] [--workers N] > runs/RBT-118/prior/levers.txt

For every default-world history with random founders whose checkpoint branch exists (RBT-90's ten seeds, RBT-105's
sixteen replicate holistic histories (b1, b2) on RBT-90's founders (its b0 is RBT-90's own), RBT-107's twenty fresh base seeds), this
restores ``ckpt/<label>`` (MANIFEST + run.tar.gz.part*) into a scratch directory, reads ``lineage.jsonl`` and the
genomes, and writes one row per (run, snapshot season, fauna) to ``levers.tsv``:

- **alive**: individuals with a lineage row at that season;
- **mass, sum_gear, gear_per_4mass, ball_share**: RBT-113's probe_gear.py measures (model build only, no simulation):
  body mass after the mass budget, the summed torque-motor gear, its ratio to 4 x mass (the designed body's is 1.76),
  and the share of that gear on ball-joint DOFs; means over the living population;
- **food, work_kj, path**: the lineage's own per-season log, averaged over the living population and over the
  WINDOW seasons ending at the snapshot (items eaten, actuator work in J; the world charges 0.03 per kJ, and path length in m).  Path is the only
  committed coverage proxy; it is NOT RBT-113's cells-covered measure (probe_food.py), which needs replays.

Snapshots are fixed: seasons 0, 59, 299, 599, and the run's last.  Nothing is fitted here; relate.py describes.
Scratch is deleted run by run (``--keep`` keeps it).  Nothing under rabbitstew/ is changed.
"""
import argparse
import glob
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import EvolutionConfig, generation_sim  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

KINDS = ("holistic", "conventional")
SNAPS = (0, 59, 299, 599)
WINDOW = 20

LABELS = ([f"rbt-90-{s}" for s in (1, 2, 3, 4, 7, 801, 804, 805, 806, 807)]
          + [f"rbt-105-{s}-b{b}" for s in (1, 2, 4, 804, 805, 806, 807) for b in (1, 2)] + ["rbt-105-7-b1", "rbt-105-7-b2"]
          + [f"rbt-107-fresh-base-{s}" for s in range(11, 31)])
#: the committed run directory each label's season table lives in (its config.json is read from there when present)
COMMITTED = {**{f"rbt-90-{s}": f"runs/RBT-90/forage-{s}" for s in (1, 2, 3, 4, 7, 801, 804, 805, 806, 807)},
             **{f"rbt-105-{s}-b{b}": f"runs/RBT-105/forage-{s}-b{b}" for s in (1, 2, 4, 7, 804, 805, 806, 807) for b in (1, 2)},
             **{f"rbt-107-fresh-base-{s}": f"runs/RBT-107/fresh/base-{s}" for s in range(11, 31)}}


def gear(g, sc):
    """RBT-113 readout-adversary probe_gear.py's gear(), verbatim in effect: (sum gear, ball-joint gear, body mass)."""
    sim = S.Simulation([g], sc, spawns=S.spawn_layout(1, sc, 2131))
    m = sim.model
    tot = ball = 0.0
    for a in range(m.nu):
        if m.actuator_biastype[a] != 0:
            continue
        j = m.actuator_trnid[a, 0]
        k = int(np.argmax(np.abs(m.actuator_gear[a, :3])))
        isball = m.jnt_type[j] == mujoco.mjtJoint.mjJNT_BALL
        gv = abs(m.actuator_gear[a, k])
        tot += gv
        ball += gv if isball else 0.0
    return tot, ball, float(m.body_mass[1:].sum())


def _measure(args):
    path, cfg = args
    sc = generation_sim(EvolutionConfig.from_dict({k: v for k, v in cfg.items() if k != "ecology"}), 1131)
    try:
        return path, gear(Genotype.load(path), sc)
    except Exception as e:  # a genome that will not build is reported, not dropped silently
        return path, ("error", repr(e))


def restore(label, scratch):
    ref = f"ckpt/{label}"
    subprocess.run(["git", "-C", ROOT, "fetch", "-q", "--depth", "1", "origin", f"{ref}:refs/remotes/origin/{ref}"], check=True)
    names = subprocess.run(["git", "-C", ROOT, "ls-tree", "--name-only", f"origin/{ref}"], check=True, capture_output=True, text=True).stdout.split()
    manifest = subprocess.run(["git", "-C", ROOT, "show", f"origin/{ref}:MANIFEST"], check=True, capture_output=True, text=True).stdout
    blob = b"".join(subprocess.run(["git", "-C", ROOT, "show", f"origin/{ref}:{n}"], check=True, capture_output=True).stdout
                    for n in sorted(x for x in names if x.startswith("run.tar.gz.part")))
    dest = os.path.join(scratch, label)
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as t:
        t.extractall(dest, filter="data")
    top = [d for d in os.listdir(dest) if os.path.isdir(os.path.join(dest, d))]
    return os.path.join(dest, top[0]), manifest.split()


def lineage(run_dir):
    alive = defaultdict(lambda: defaultdict(list))  # season -> kind -> rows
    with open(os.path.join(run_dir, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("death"):
                continue
            alive[r["generation"]][r["population"]].append(r)
    return alive


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=os.environ.get("RBT118_SCRATCH", "/tmp/rbt118-scratch"))  # never under runs/: a restored config.json would be admitted by .gitignore
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    labels = a.only or LABELS
    out = os.path.join(HERE, "levers.tsv")
    done = set()
    if os.path.exists(out):
        done = {l.split("\t")[0] for l in open(out).read().splitlines()[1:]}
    else:
        with open(out, "w") as f:
            f.write("label\tcommitted\tseason\tfauna\talive\tmass\tsum_gear\tgear_per_4mass\tball_share\tfood\twork_j\tpath\tbuild_errors\n")
    print("# RBT-118 prior, levers.py: EXPLORATORY, descriptive only")
    for label in labels:
        if label in done:
            print(f"{label}: already in levers.tsv, skipped")
            continue
        run_dir, manifest = restore(label, a.scratch)
        cfg = json.load(open(os.path.join(run_dir, "config.json")))
        committed = COMMITTED[label]
        cc = os.path.join(ROOT, committed, "config.json")
        same_cfg = (json.load(open(cc)) == cfg) if os.path.exists(cc) else None
        al = lineage(run_dir)
        last = max(al)
        snaps = sorted({s for s in SNAPS if s <= last} | {last})
        paths = {}
        for s in snaps:
            for kind in KINDS:
                for r in al[s][kind]:
                    p = os.path.join(run_dir, kind, "genomes", f"{r['name']}.json")
                    paths[p] = cfg
        with ProcessPoolExecutor(a.workers) as ex:
            meas = dict(ex.map(_measure, list(paths.items()), chunksize=8))
        rows = []
        for s in snaps:
            for kind in KINDS:
                living = al[s][kind]
                ms = [meas[os.path.join(run_dir, kind, "genomes", f"{r['name']}.json")] for r in living]
                errs = sum(1 for m in ms if m[0] == "error")
                ms = np.array([m for m in ms if m[0] != "error"], float).reshape(-1, 3)
                win = [r for t in range(max(0, s - WINDOW + 1), s + 1) for r in al[t][kind]]
                def f(k):  # rows written before a field existed lack it: averaged over the rows that carry it
                    v = [float(r[k]) for r in win if r.get(k) is not None]
                    return f"{np.mean(v):.4f}" if v else ""
                if len(ms):
                    tot, ball, mass = ms[:, 0], ms[:, 1], ms[:, 2]
                    vals = f"{mass.mean():.3f}\t{tot.mean():.2f}\t{(tot / (4 * mass)).mean():.3f}\t{ball.sum() / max(tot.sum(), 1e-9):.3f}"
                else:
                    vals = "\t\t\t"
                rows.append(f"{label}\t{committed}\t{s}\t{kind}\t{len(living)}\t{vals}\t{f('food')}\t{f('work')}\t{f('path')}\t{errs}")
        with open(out, "a") as fo:
            fo.write("\n".join(rows) + "\n")
        print(f"{label}: MANIFEST {' '.join(manifest[1:4])}; last season {last}; config equals committed: {same_cfg}; "
              f"{len(paths)} genomes built; build errors {sum(1 for m in meas.values() if m[0] == 'error')}")
        if not a.keep:
            shutil.rmtree(os.path.join(a.scratch, label), ignore_errors=True)
            subprocess.run(["git", "-C", ROOT, "update-ref", "-d", f"refs/remotes/origin/ckpt/{label}"])
    if not a.keep:
        shutil.rmtree(a.scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
