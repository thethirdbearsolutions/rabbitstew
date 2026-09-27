"""RBT-113 design-adversary probe: the resume test covers the down line only; the control line is the one line
whose pool draws from the population stream.  Also: Z + salt + control resumes byte for byte."""
import sys, os
sys.path.insert(0, os.path.join(os.environ["RBT113_TREE"], "tests"))
import pytest
from test_rbt113 import _solo_run, _sha
from rabbitstew.evolution import Experiment


@pytest.mark.parametrize("extra", [[], ["--global-bias-sigma", "0", "--holistic-stream-salt", "1"]])
def test_control_line_resumes_byte_for_byte(tmp_path, extra):
    _solo_run(tmp_path / "full", "control", extra, gens=3)
    _solo_run(tmp_path / "cut", "control", extra, gens=2, loco=3)
    Experiment.resume(str(tmp_path / "cut"), generations=3, log=None).run()
    for f in ("lineage.jsonl", "state.json", "history.json"):
        assert _sha(tmp_path / "cut" / f) == _sha(tmp_path / "full" / f), f
