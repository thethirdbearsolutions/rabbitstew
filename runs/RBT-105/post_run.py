"""RBT-105: what one finished replicate arm owes the repository, written from its bulk while the bulk is here.

    python runs/RBT-105/post_run.py ARM_DIR SEED K

  seasons.txt, lineage-last.txt   RBT-71's summarise(), as RBT-90 part 2 wrote them (runs/README.md)
  oscillator.txt                  RBT-84 oscillator_rate.py, unmodified: the count part2_readout.py reads
  osc_births.txt                  osc_births.py: the birth-level linked-oscillator rate per block and over 300-599 (R2)
  EXTINCT.txt                     only if the holistic fauna has no best at season 590 (as part2_analyse.py)
  pairing.txt                     the arm against its seed's RBT-90 part 2 arm, from committed files only:
                                  founders' fingerprint (founders-rbt90.txt), the designed-body rows of
                                  seasons.txt, the first season the holistic rows differ; for K = 0 also
                                  seasons.txt and lineage-last.txt byte for byte (the positive control)

Every step is another ticket's script run unmodified, stdout straight to a .txt (never through grep).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
GEN = 590  #: the champion's season, as in RBT-90 part 2
sys.path.insert(0, str(HERE))
import founders  # noqa: E402


def run(out, *cmd):
    with open(out, "w") as f, open(str(out) + ".err", "w") as err:
        status = subprocess.run([sys.executable, *map(str, cmd)], stdout=f, stderr=err, cwd=ROOT).returncode
        if status:
            f.write(f"\nSTEP FAILED: exit status {status}; see {pathlib.Path(out).name}.err (not committed)\n")
    print(f"wrote {out}" + (f"  (STEP FAILED, exit {status})" if status else ""), flush=True)


def rows(path, kind=None):
    lines = pathlib.Path(path).read_text().splitlines()[1:]
    return [l for l in lines if kind is None or l.split("\t")[1] == kind]


def pairing(arm, seed, k):
    """Lines comparing ``arm`` with runs/RBT-90/forage-SEED, over the seasons the arm has."""
    base = ROOT / "runs" / "RBT-90" / f"forage-{seed}"
    ref = {l.split()[0]: l.split(" ", 1)[1] for l in (HERE / "founders-rbt90.txt").read_text().splitlines() if not l.startswith("#")}
    mine = founders.line(arm, str(seed)).split(" ", 1)[1]
    out = [f"arm {arm.name} seed {seed} breed_stream {k} against runs/RBT-90/forage-{seed}"]
    out.append(f"founders (genomes and ages at season 0) identical to the RBT-90 arm: {mine == ref[str(seed)]}")
    a_con, b_con = rows(arm / "seasons.txt", "conventional"), rows(base / "seasons.txt", "conventional")
    out.append(f"designed-body seasons.txt rows identical over the arm's {len(a_con)} seasons: {a_con == b_con[:len(a_con)]}")
    a_hol, b_hol = rows(arm / "seasons.txt", "holistic"), rows(base / "seasons.txt", "holistic")
    first = next((a.split("\t")[0] for a, b in zip(a_hol, b_hol) if a != b), None)
    out.append(f"first season whose holistic seasons.txt row differs: {first if first is not None else 'none'}")
    if k == 0 and len(a_con) == len(b_con):
        for name in ("seasons.txt", "lineage-last.txt"):
            same = (arm / name).read_bytes() == (base / name).read_bytes()
            out.append(f"positive control: {name} byte-identical to the RBT-90 arm's committed file: {same}")
    elif k == 0:  # a shorter arm (the throwaway): its seasons.txt against the same seasons of the committed one
        a_all, b_all = (arm / "seasons.txt").read_text().splitlines(), (base / "seasons.txt").read_text().splitlines()
        out.append(f"positive control, first {len(a_con)} seasons only: seasons.txt rows byte-identical to the RBT-90 arm's: {a_all == b_all[:len(a_all)]}")
    return out


def main(arm, seed, k):
    arm = pathlib.Path(arm).resolve()
    rel = arm.relative_to(ROOT) if arm.is_relative_to(ROOT) else arm
    spec = importlib.util.spec_from_file_location("measure", ROOT / "runs" / "RBT-71" / "measure.py")
    measure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(measure)
    measure.summarise(str(arm))
    print(f"wrote {arm}/seasons.txt and lineage-last.txt", flush=True)
    seasons = json.loads((arm / "config.json").read_text())["ecology"]["seasons"]
    if seasons > GEN and not (arm / "holistic" / f"best_gen{GEN:04d}.json").exists():
        hol = [l.split("\t") for l in rows(arm / "seasons.txt", "holistic")]
        last = max((int(r[0]) for r in hol if int(r[2]) > 0), default=-1)
        (arm / "EXTINCT.txt").write_text(f"no holistic best at season {GEN}; the holistic fauna was last alive at season {last}\n")
        print(f"wrote {arm}/EXTINCT.txt", flush=True)
    run(arm / "oscillator.txt", "runs/RBT-84/oscillator_rate.py", rel, "holistic")
    run(arm / "osc_births.txt", HERE / "osc_births.py", rel)
    (arm / "pairing.txt").write_text("\n".join(pairing(arm, seed, k)) + "\n")
    print(f"wrote {arm}/pairing.txt", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
