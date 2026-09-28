"""RBT-130 adversary: DESIGN §5.6 item 2, the fork at the merge.  Is an N (or M) arm forked from an S checkpoint (config.json
edited to set merge_after and merge_null, then Ecology.resume) byte-identical to the same arm run straight from season 0?
python runs/RBT-130/adversary/probe_fork.py > runs/RBT-130/adversary/probe_fork.txt"""
import json, os, shutil, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests"))
from test_ecology_switches import _breeding_eco, _evo
from rabbitstew.ecology import Ecology
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC

T = tempfile.mkdtemp()
S = os.path.join(T, "S")
Ecology(_evo(11, 1.5), _breeding_eco(seasons=3, sweep_log=True), out_dir=S, log=None).run()  # S's checkpoint after season 2
for arm, kw in (("M", {}), ("N-holistic", dict(merge_null=HOLISTIC)), ("N-conventional", dict(merge_null=CONVENTIONAL))):
    straight = os.path.join(T, arm + "_straight")
    Ecology(_evo(11, 1.5), _breeding_eco(seasons=7, merge_after=3, sweep_log=True, **kw), out_dir=straight, log=None).run()
    fork = os.path.join(T, arm + "_fork")
    shutil.copytree(S, fork)
    cfg = json.load(open(os.path.join(fork, "config.json")))
    cfg["ecology"].update(merge_after=3, **kw)
    json.dump(cfg, open(os.path.join(fork, "config.json"), "w"), indent=2)
    try:
        Ecology.resume(fork, seasons=7, log=None).run()
    except Exception as exc:
        print(f"{arm:15s} fork FAILS: {type(exc).__name__}: {exc}  (Ecology.resume replaces counter with the checkpoint's, which has no {exc} entry)")
        continue
    same = {n: open(os.path.join(fork, n), "rb").read() == open(os.path.join(straight, n), "rb").read() for n in ("lineage.jsonl", "cohorts.jsonl", "history.json")}
    print(f"{arm:15s} fork (S checkpoint + edited config.json + resume) == straight run: {same}")
