"""RBT-90 part 2's precondition: the adversary's direction probe on the founders THIS HEAD's ecology draws.

``adversary_direction.py`` run unchanged measures part 1's founders (``default_rng(seed)``); a run on
the integration head founds ``spawn_streams(seed)[HOLISTIC]`` (RBT-95; ``head_founders.py``).  This
wrapper swaps that one line and writes beside part 1's readouts, not over them:

    python runs/RBT-90/head_direction.py SEED      ->  docs/artifacts/RBT-90-head-direction-SEED.txt

Sixty founders, sixteen bouts each, the probe itself imported and untouched.
"""
import importlib.util
import pathlib
import sys
import tempfile

from rabbitstew.evolution import HOLISTIC, initial_population, spawn_streams

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ART = ROOT / "docs" / "artifacts"
spec = importlib.util.spec_from_file_location("ad", ROOT / "runs" / "RBT-90" / "adversary_direction.py")
ad = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ad)

part1_founders = ad.fd.founders


def head_founders(seed):
    evo, _ = part1_founders(seed)  # part 1's config guard, kept
    return evo, list(initial_population(HOLISTIC, evo, spawn_streams(seed)[HOLISTIC]).members)


if __name__ == "__main__":
    seed = int(sys.argv[1])
    ad.fd.founders = head_founders
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="rbt90-dir-"))
    ad.ART = scratch
    ad.main(seed, 60, 16)
    text = (scratch / f"RBT-90-adversary-direction-{seed}.txt").read_text()
    header = (f"Founders: this head's ecology founders for seed {seed}, spawn_streams({seed})[HOLISTIC] (RBT-95), "
              "not part 1's default_rng(seed) population; see RBT-90-head-founders.txt.\n")
    (ART / f"RBT-90-head-direction-{seed}.txt").write_text(header + text)
