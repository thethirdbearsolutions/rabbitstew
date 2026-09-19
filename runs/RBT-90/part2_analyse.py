"""RBT-90 part 2: every per-seed instrument pass on one finished arm, in the order the pre-registration names.

Nothing here is new: each step is another ticket's committed script, run unmodified, its stdout
written straight to a .txt beside the arm (never through grep: it block-buffers, runs/README.md).

    python runs/RBT-90/part2_analyse.py SEED [ARM_DIR]

  seasons.txt, lineage-last.txt   RBT-71's summarise(): what the run owes the repository
  oscillator.txt                  RBT-84 oscillator_rate.py: linked-oscillator rate at birth and among distinct bests
  descent.txt                     RBT-84 descent.py: the champion's whole descent DAG (every parent followed)
  lab.txt                         scripts/forage_lab.py at n = 64: every unit lesion, the power line, the
                                  champion against its own gait (RBT-38's instrument, RBT-39's null)
  subsystems.txt                  RBT-84 champion_subsystems.py at n = 64: whole subsystems and the lab's two
                                  most costly units, each with a paired t
  topunit.txt                     RBT-84 adversary_topunit.py: the two most costly units on the same 64 paired
                                  seeds, which is what decides whether the drive KIND is resolvable
  power.txt                       RBT-39 power_ladder.py at n = 64: the gait null's positive control on this
                                  champion's own body, in whole items planted on its path

The champion is the last saved best, best_gen0590.json, as in RBT-84.
"""
import importlib.util
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
# the pre-registered values; the environment overrides exist for the smoke test on a throwaway run only
GEN, N = int(os.environ.get("PART2_GEN", 590)), int(os.environ.get("PART2_N", 64))


def run(out, *cmd, cwd=ROOT):
    """One instrument, its stdout to `out`, its stderr beside it (MuJoCo warnings; bulk, not committed).
    A step that exits non-zero is recorded in its own readout and the pass continues, so one
    champion an instrument cannot read does not cost the other instruments their rows."""
    with open(out, "w") as f, open(str(out) + ".err", "w") as err:
        status = subprocess.run([sys.executable, *map(str, cmd)], stdout=f, stderr=err, cwd=cwd).returncode
        if status:
            f.write(f"\nSTEP FAILED: exit status {status}; see {pathlib.Path(out).name}.err (not committed) for the traceback\n")
    print(f"wrote {out}" + (f"  (STEP FAILED, exit {status})" if status else ""), flush=True)


def top_units(lab_text, k=2):
    """The lab's k most costly single-unit lesions, from its closing 'costs' lines."""
    return [int(m) for m in re.findall(r"^\s+lesion:(\d+)\s+costs", lab_text, flags=re.M)][:k]


def main(seed, arm=None):
    arm = pathlib.Path(arm).resolve() if arm else ROOT / "runs" / "RBT-90" / f"forage-{seed}"
    rel = arm.relative_to(ROOT) if arm.is_relative_to(ROOT) else arm
    spec = importlib.util.spec_from_file_location("measure", ROOT / "runs" / "RBT-71" / "measure.py")
    measure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(measure)
    measure.summarise(str(arm))
    print(f"wrote {arm}/seasons.txt and lineage-last.txt", flush=True)
    run(arm / "oscillator.txt", "runs/RBT-84/oscillator_rate.py", rel, "holistic")
    run(arm / "descent.txt", "runs/RBT-84/descent.py", rel, "holistic")
    run(arm / "lab.txt", "scripts/forage_lab.py", rel, "holistic", GEN, N, 120)
    units = top_units((arm / "lab.txt").read_text())
    run(arm / "subsystems.txt", "runs/RBT-84/champion_subsystems.py", rel, "holistic", GEN, N, 120, *[f"lesion:{u}" for u in units])
    if len(units) == 2:
        # adversary_topunit.py also writes docs/runs/RBT-84-adversary-topunit.txt relative to its cwd, which from the
        # repository root is RBT-84's committed readout; run it from a scratch directory so that file is never touched
        run(arm / "topunit.txt", ROOT / "runs/RBT-84/adversary_topunit.py", arm, "holistic", GEN, units[0], units[1], N, cwd=tempfile.mkdtemp(prefix="rbt90-topunit-"))
    run(arm / "power.txt", "runs/RBT-39/power_ladder.py", rel, "holistic", GEN, N, 200, 6)


if __name__ == "__main__":
    main(int(sys.argv[1]), *sys.argv[2:3])
