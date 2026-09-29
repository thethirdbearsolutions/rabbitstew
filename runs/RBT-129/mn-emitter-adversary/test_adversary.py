"""RBT-129 L1 adversary: probes of PR #500's gated M/N emitter (``stages.py`` at the PR head).

    git worktree add /tmp/pr500 ebcd38654fb90f1dc967ddea3fc023276553dde0
    cd /tmp/pr500 && PR500=/tmp/pr500 python -m pytest <this file> -q -p no:cacheprovider

The tests import ``stages`` and the PR's own test helpers from $PR500 (skipped when it is unset).  Each test states
whether it CONFIRMS the PR or shows a HOLE; a HOLE test passes when the hole is there (it documents it) and names the
fix.  Nothing here runs a sweep arm: tiny non-sweep worlds only, as in the PR's tests.
"""
import json
import os
import sys

import pytest

PR = os.environ.get("PR500")
if not PR:
    pytest.skip("set PR500 to a checkout of PR #500's head", allow_module_level=True)
sys.path.insert(0, os.path.join(PR, "runs", "RBT-129", "launch"))
sys.path.insert(0, os.path.join(PR, "tests"))
import blocks  # noqa: E402
import stages  # noqa: E402
from test_rbt129_mn import TINY_ARGV, _rank, _s60, _salts, tiny  # noqa: E402,F401
from test_rbt129_launch import fair_check, repo_tmp, surface_clearance  # noqa: E402,F401

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC  # noqa: E402

H, D = HOLISTIC, CONVENTIONAL


# --- open question (4): "alive at 59" and "alive at 59 before refill" are the same test of extinction ---------------

def test_confirm_booked_and_before_refill_extinction_agree_in_the_ecology(tmp_path, tiny):
    """CONFIRMS (and answers OQ4): in ``Ecology.step`` breeders are drawn from the season's survivors, and a parent
    pays birth_cost but does not die until a later season, so births > 0 implies alive - births > 0.  Hence
    alive > 0 <=> alive - births > 0 for every row: the two readings of "both faunas alive at season 59" never differ.
    (The PR's README says they differ "when a fauna's every survivor dies in season 59 after breeding"; that cannot
    happen.)  Checked here on a tiny run with starvation, and on all 8,584 census history rows in g0_independent.txt."""
    rows = 0
    for j in (1, 2, 3):
        unit = _s60(tiny, tmp_path, j, 0, 0)
        for e in stages._history(os.path.join(unit, "ckpt60")):
            rows += 1
            assert not (e["births"] > 0 and e["alive"] - e["births"] <= 0)
            assert (e["alive"] > 0) == (e["alive"] - e["births"] > 0)
        hist = stages._history(os.path.join(unit, "ckpt60"))
        assert stages.valid_at_merge(os.path.join(unit, "ckpt60")) == all(
            stages.alive_before_refill(hist, k) > 0 for k in stages.FAUNAS)
    assert rows > 0


# --- open question (1): N's eligibility, read literally, is not the PR's --------------------------------------------

def test_hole_n_eligibility_is_the_m_gate_not_item_2_alone():
    """HOLE (MUST 1, a ruling): item 2 ("N runs only where census g0 <= 0.8 ... with the same seed rule as M") does not
    repeat item 1's "designed fauna not FOUNDING-FAIL" clause.  The PR makes N a subset of M-eligible points.  On the
    real census this moves an N slot: read alone, item 2 gives c1-p030-PW-L (g0 0.525, designed FOUNDING-FAIL) the
    third N slot, where the PR gives c1-p010-PW-L.  The PR's reading is the better one (N is the point's null for M's
    share call, which needs M), but T5 does not say it; it must be ruled before any S60 is read."""
    g = {"c0-p080-PW-G": 0.329, "c1-p030-PW-G": 0.434, "c0-p030-PW-G": 0.458, "c1-p030-PW-L": 0.525,
         "c2-p010-PW-G": 0.535, "c1-p010-PW-L": 0.543}
    rank = [{"point": p, "g0": v, "designed_ff": p == "c1-p030-PW-L", "anchor": p in blocks.ANCHORS,
             "m_ok": p not in blocks.ANCHORS and p != "c1-p030-PW-L", "n_ok": p not in blocks.ANCHORS and p != "c1-p030-PW-L"}
            for p, v in g.items()]
    gate = stages.mn_gate(rank, {r["point"]: {j: True for j in range(1, 9)} for r in rank if r["m_ok"]})
    pr_n = [r["point"] for r in gate if r["n"]]
    literal = [p for p, v in sorted(g.items(), key=lambda x: x[1]) if v <= 0.8 and p not in blocks.ANCHORS][:4]
    assert pr_n == ["c0-p080-PW-G", "c0-p030-PW-G", "c2-p010-PW-G", "c1-p010-PW-L"]
    assert literal == ["c0-p080-PW-G", "c0-p030-PW-G", "c1-p030-PW-L", "c2-p010-PW-G"]
    assert pr_n != literal


def test_confirm_a_freed_m_slot_also_frees_the_n_slot():
    """CONFIRMS the PR's default for OQ1 (N follows M's admission), and shows what the alternative reading does: with
    N's 4 slots fixed to the 4 lowest N-eligible points, a point with no valid seed would hold an N slot and run
    nothing, so only 3 N points would run."""
    rank = _rank([0.3, 0.4, 0.5, 0.6, 0.7])
    valid = {r["point"]: {j: r["point"] != "p01" for j in range(1, 9)} for r in rank}
    gate = stages.mn_gate(rank, valid)
    assert [r["point"] for r in gate if r["n"]] == ["p00", "p02", "p03", "p04"]
    fixed = [r["point"] for r in rank if r["n_ok"]][:4]
    assert [p for p in fixed if any(valid[p].values())] == ["p00", "p02", "p03"]


# --- open question (3): the threshold rescale -------------------------------------------------------------------------

def test_hole_the_rescale_sentence_is_not_implemented_and_not_ruled():
    """HOLE (MUST 2, a ruling): DESIGN 5.2 keeps "If the pilot's M arms find the real drift ... far from the replica's
    (4.1), the gate's thresholds are rescaled by the same ratio before Stage 1", and the readout measured r = 1.53.
    T5 (written after r was known, with precedence) and its 171 / 320 use 1.0 / 0.8, and so does the PR; 4.1 says
    "the thresholds ... may not" change.  The two readings give different gates at Stage 1:"""
    assert (stages.GATE_M_G0, stages.GATE_N_G0) == (1.0, 0.8)
    g = [0.329, 0.458, 0.535, 0.543, 0.554, 0.666, 0.680, 0.818, 0.934, 0.938]  # the 10 M-eligible points' g0
    r = 1.530
    assert sum(x <= 1.0 for x in g) == 10 and sum(x <= 0.8 for x in g) == 7
    assert sum(x <= 1.0 / r for x in g) == 5 and sum(x <= 0.8 / r for x in g) == 2  # divided: M 5 points, N 2
    assert sum(x <= 1.0 * r for x in g) == 10 and sum(x <= 0.8 * r for x in g) == 10  # multiplied: N at every M point


# --- guards ------------------------------------------------------------------------------------------------------------

def test_hole_a_ksalt_void_on_an_extinct_unit_is_not_refused(tmp_path, tiny):
    """HOLE (SHOULD): ``s60_state`` returns False for a unit with EXTINCT.txt before it reads KSALT.txt, so a VOID
    K-SALT (F7: "RBT-129c's stream claim is re-opened") at an M-eligible point is passed over silently when S also went
    extinct pre-merge.  The lane itself already stopped loudly on the VOID (run_job), so this is a second line only;
    the check should come first."""
    unit = os.path.join(str(tmp_path), "stage1", "tiny", "129002")
    os.makedirs(unit)
    with open(os.path.join(unit, stages.EXTINCT), "w") as f:
        f.write("EXTINCT pre-merge at season 12: ...\n")
    with open(os.path.join(unit, stages.KSALT_FILE), "w") as f:
        f.write("KSALT VOID: ...\n")
    assert stages.s60_state(str(tmp_path), "tiny", 2, (1, 0), TINY_ARGV) is False  # no refusal


def test_confirm_a_ksalt_void_at_a_live_unit_refuses_the_whole_emission(tmp_path, tiny):
    unit = _s60(tiny, tmp_path, 3, 2, 0)
    with open(os.path.join(unit, stages.KSALT_FILE), "w") as f:
        f.write("KSALT VOID: the designed half differs\n")
    with pytest.raises(SystemExit) as e:
        stages.s60_state(str(tmp_path), "tiny", 3, (2, 0), TINY_ARGV)
    assert e.value.code == 8


def test_confirm_every_refusal_writes_no_lane(repo_tmp, fair_check, monkeypatch, tmp_path):
    """CONFIRMS: each of the gate's refusals (screen gate, launch record missing / other salts, an S60 not done, a
    ckpt60 at other salts, a K-SALT not PASS) raises before ``emit_lanes``, so lanes/1-MN is never written."""
    lanes = repo_tmp / "lanes" / "1"
    pairs = lambda s: " ".join(f"{stages.seed(j)}:{a}/{b}" for j, (a, b) in sorted(s.items()))
    good = f"fair --fair\neat {' '.join(blocks.EAT_RULED)}\nsalts {pairs(_salts())}\n"
    rank = _rank([0.5])
    rank[0]["point"] = "c1-p010-PW-L"
    monkeypatch.setattr(stages, "gate_rank", lambda root: rank)
    cases = []
    cases.append(("screen gate", lambda: monkeypatch.setattr(stages, "screen_gate", lambda root: stages._refuse("x", 8))))

    def no_launch():
        monkeypatch.setattr(stages, "screen_gate", lambda root: _salts())
        if (lanes / "launch.txt").exists():
            (lanes / "launch.txt").unlink()
    cases.append(("no launch.txt", no_launch))

    def other_salts():
        monkeypatch.setattr(stages, "screen_gate", lambda root: _salts(j2=(1, 0)))
        lanes.mkdir(parents=True, exist_ok=True)
        (lanes / "launch.txt").write_text(good)
    cases.append(("launch.txt at other salts", other_salts))

    for what, v in (("S60 not done", None), ("ckpt60 at other salts", "refuse"), ("K-SALT not PASS", "refuse")):
        def s60(v=v):
            monkeypatch.setattr(stages, "screen_gate", lambda root: _salts())
            lanes.mkdir(parents=True, exist_ok=True)
            (lanes / "launch.txt").write_text(good)
            monkeypatch.setattr(stages, "s60_state", lambda *a: stages._refuse("x", 8) if v == "refuse" else None)
        cases.append((what, s60))
    for what, arrange in cases:
        arrange()
        with pytest.raises(SystemExit) as e:
            stages.main(["mn-emit", "--fair=--fair", "--root", str(repo_tmp)])
        assert e.value.code == 8, what
        assert not (repo_tmp / "lanes" / stages.MN_LANES).exists(), what


def test_hole_a_hand_added_m_fork_passes_the_lane_checks(tmp_path):
    """HOLE (SHOULD): lanes/1-MN/launch.txt records only "point:Mk/Nk" per admitted point.  A fork job added by hand at
    a point or seed the gate did not admit, with the right salts, passes ``check_lane_salts`` and ``check_lane_blocks``
    (forks have no block), so ``run_lane`` would run it.  Fresh jobs are held to their blocks (L1 of the launch
    adversary); M/N forks should be held to the gate's admitted (point, seed, arm) list the same way."""
    launch = {"fair": "--fair", "eat": " ".join(blocks.EAT_RULED), "salts": "129001:0/0 129002:1/0",
              "admitted": "c0-p080-PW-G:M8/N8"}
    rogue = {"job": "fork", "name": "1/c2-p030-U-G/129002/M", "seed": 129002, "salts": [1, 0],
             "src": str(tmp_path / "stage1/c2-p030-U-G/129002/ckpt60"), "dir": str(tmp_path / "stage1/c2-p030-U-G/129002/M"),
             "set": {"merge_after": 60, "pooled_capacity": 120}}
    stages.check_lane_salts([rogue], launch)
    stages.check_lane_blocks([rogue], launch)  # no fresh job, nothing to check


def test_confirm_the_s60_read_is_the_season_59_state_only(tmp_path, tiny):
    """CONFIRMS (item 2, no-peek): what ``s60_state`` returns depends only on ckpt60's season-59 counts (and the
    unit's pre-merge EXTINCT.txt): S's own directory, run on past the merge, is never read.  Here S is run on to
    season 5 and then deleted; the gate's answer is unchanged."""
    unit = _s60(tiny, tmp_path, 5, 0, 0)
    before = stages.s60_state(str(tmp_path), "tiny", 5, (0, 0), TINY_ARGV)
    stages.run_job({**tiny, "job": "resume", "name": "1/tiny/129005/S", "dir": f"{unit}/S", "seed": 129005, "seasons": 5})
    assert stages.s60_state(str(tmp_path), "tiny", 5, (0, 0), TINY_ARGV) == before
    import shutil
    shutil.rmtree(os.path.join(unit, "S"))
    assert stages.s60_state(str(tmp_path), "tiny", 5, (0, 0), TINY_ARGV) == before


# --- cost ---------------------------------------------------------------------------------------------------------------

def test_confirm_the_cost_figures():
    """174 / 326 is 80 M + 32 N arms at 240 seasons; 171 / 320 is T5's 12 x 8 M at 240 plus 4 x 8 N at 0.57 core-h an
    arm at 20 core-s (founding_expect.py line 194).  The emitter's bound is the honest one; the difference is +3 / +6."""
    ub = stages._core_h(80 + 32)
    assert (round(ub[0]), round(ub[1])) == (174, 326)
    t5 = tuple(96 * 240 * c / 3600 + 32 * 0.57 * c / 20 for c in stages.MN_CORE_S)
    assert (round(t5[0]), round(t5[1])) == (171, 320)
    n_t5, n_pr = 32 * 0.57 / 20 * 3600, 32 * 240  # N arm-seasons: the disclosure's basis against the arms emitted
    assert round(n_pr / n_t5, 2) == 2.34
