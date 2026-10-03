"""RBT-124 design adversary: does `python -m rabbitstew.levers` read a line under the physics its run was scored in?

    levers_config.py > levers_config.txt

Writes (to a temp dir, not a run) the config.json a pack run would write -- RBT-113's generation sim with ball_cone =
hinge_range = pi/2 and settle_until_rest 0.01 -- next to a final/ holding the RBT-113 holistic D fixture, then runs
the lever command (a) with no flags, (b) with the flags repeated on the command line.  If the report takes its physics
from the run's config, (a) and (b) agree.
"""
import contextlib
import io
import json
import math
import os
import shutil
import sys
import tempfile
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import world  # noqa: E402

from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.levers import main  # noqa: E402

sc = generation_sim(world.evolution_config("U", "", seed=1), 1131)
sc = replace(sc, settle_until_rest=0.01, settle_max=10.0, world=replace(sc.world, ball_cone=math.pi / 2, hinge_range=math.pi / 2))
tmp = tempfile.mkdtemp()
os.makedirs(os.path.join(tmp, "final"))
shutil.copy(os.path.join(ROOT, "tests", "data", "rbt124", "holistic_D_O1s1_000.json"), os.path.join(tmp, "final", "000.json"))
json.dump({"sim": sc.to_dict()}, open(os.path.join(tmp, "config.json"), "w"))
print("# config.json written with: ball_cone", sc.world.ball_cone, "hinge_range", sc.world.hinge_range, "settle_until_rest", sc.settle_until_rest)
for label, extra in (("(a) no flags", []), ("(b) flags repeated", ["--ball-cone", str(math.pi / 2), "--hinge-range", str(math.pi / 2), "--settle-until-rest", "0.01"])):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main(extra + [f"D={os.path.join(tmp, 'final')}"])
    lines = buf.getvalue().splitlines()
    print(label)
    print("  " + lines[0])
    print("  " + lines[-2])
    print("  " + lines[-1])
shutil.rmtree(tmp)
