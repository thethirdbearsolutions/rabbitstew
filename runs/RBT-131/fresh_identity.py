"""RBT-131: a fresh run leaves the same bytes with and without the fix, every file (platform.json aside).

    python runs/RBT-131/fresh_identity.py CODE_ROOT OUT_DIR > digests.txt

Runs four test-sized fresh ecologies with the ``rabbitstew`` package imported from CODE_ROOT (a checkout of the pre-fix
commit or of this branch) and prints the sha256 of every file each leaves, sorted.  ``platform.json`` is left out: it
records the checkout's sha and dirty flag, which differ by construction.  Diff the two outputs; they must be equal.
The configurations are the tests' own (tests/test_ecology_switches.py): a plain run, a run with a cull (the population
shrinks inside the run), a breeding run with deaths, and a merge-null run (a fauna goes to zero at the merge).
"""
import hashlib
import os
import sys

root, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests"))

from rabbitstew.ecology import Ecology  # noqa: E402
from rabbitstew.evolution import HOLISTIC  # noqa: E402
import rabbitstew  # noqa: E402
from test_ecology_switches import _breeding_eco, _eco, _evo  # noqa: E402

assert os.path.abspath(rabbitstew.__file__).startswith(os.path.abspath(root)), rabbitstew.__file__

RUNS = {
    "plain": (_evo(), _eco(seasons=4, capacity=6)),
    "cull": (_evo(), _eco(seasons=4, capacity=6, cull_at=2, cull="holistic=3,conventional=2")),
    "breeding": (_evo(11, 1.5), _breeding_eco(seasons=6)),
    "merge_null": (_evo(11, 1.5), _breeding_eco(seasons=6, merge_after=3, merge_null=HOLISTIC)),
}
for name, (evo, eco) in RUNS.items():
    d = os.path.join(out, name)
    Ecology(evo, eco, out_dir=d, log=None).run()
    for dirpath, _, files in sorted(os.walk(d)):
        for fn in sorted(files):
            if fn == "platform.json":
                continue
            p = os.path.join(dirpath, fn)
            print(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.relpath(p, out)}")
