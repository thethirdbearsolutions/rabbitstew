"""RBT-100 (C3) readout: the verdict text carries C3's claim lines, the owner's falsifier wording and the
class-D sentence the rule picks (adversary round 1, F6); deaths split by cause and cohort from committed
lineage-last rows (F1); the own-net table's bound and its reconciliation with history (F3)."""
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(f"rbt100_{name}", ROOT / "runs" / "RBT-100" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


R3 = _load("readout")
OWN = _load("own_table")
DOC = (ROOT / "docs" / "held-out-challenges.md").read_text()


def _norm(s):
    return " ".join(s.split())


def test_quoted_claim_lines_and_statement_are_verbatim_from_the_protocol():
    for q in (R3.CLAIM_C3, R3.CLAIM_C2, R3.UNPERCEIVED):
        assert _norm(q) in _norm(DOC)
    assert "the designed body wins on the held-out challenge" in DOC


def _sentence(lines):
    return next(l for l in lines if l.strip().startswith("sentence:"))


def test_class_d_prints_outlasts_unless_co_evolved_holds_up():
    out = R3.verdict_text("D. designed bankrupt", -0.6, 0.08)
    assert "outlasts a bankrupt comparator" in _sentence(out)
    out = R3.verdict_text("D. designed bankrupt", -0.05, 0.08)
    assert "holds up against the challenge" in _sentence(out)
    assert R3.FORBIDDEN_12 in out and R3.FORBIDDEN_13 in out and R3.CLAIM_C3 in out


def test_class_c_prints_the_owners_falsifier_and_class_a_is_not_the_contest_claim():
    out = "\n".join(R3.verdict_text('C. designed wins -- THE FALSIFIER: "the designed body wins after the shift"', -0.9, 0.08))
    assert "CLASS C: the designed body wins on the held-out challenge." in out
    out = R3.verdict_text("A. co-evolved wins", -0.5, 0.08)
    assert "not the owner's contest claim" in "\n".join(out) and "outlasts, not holds up" in _sentence(out)
    out = R3.verdict_text("A. co-evolved wins", float("nan"), 0.08)  # an unknown R-shift never reads as holds up
    assert "outlasts, not holds up" in _sentence(out)


def test_parse_part1_reads_rbt92s_printed_verdict_block():
    text = ("  r = 0.0771 (the larger);  pre-registered ...\n"
            "  CLASS: D. designed bankrupt\n"
            "  'holds up' needs co-evolved R-shift (recovery) >= -r: -0.5123 against -0.0771 -> does not hold up\n")
    assert R3.parse_part1(text) == ("D. designed bankrupt", 0.0771, -0.5123)


class _Arm:
    def __init__(self, ind, lastrows, last, culled=None):
        self.ind, self.lastrows, self.last, self.culled = ind, lastrows, last, culled or {}


def test_split_deaths_by_cause_and_cohort():
    # T = 10.  a: onset cohort, starves in 12 (last row 11).  b: recruit born 11, starves in 14.  c: onset
    # cohort, dies of age in 15 (age 59 at its last row, 14).  d: alive at the end.  e: culled at T.
    ind = {("conventional", "a"): (0, 11, []), ("conventional", "b"): (11, 13, ["a"]),
           ("conventional", "c"): (-45, 14, []), ("conventional", "d"): (5, 50, []),
           ("conventional", "e"): (2, 9, [])}
    rows = [{"population": "conventional", "name": n, "age": str(a)} for n, a in (("a", 11), ("b", 2), ("c", 59), ("d", 45), ("e", 7))]
    arm = _Arm(ind, rows, last=50, culled={("conventional", 10): ["e"]})
    d = R3.split_deaths(arm, "conventional", 10, 30)
    assert d == {("starved", "<T"): 1, ("starved", ">=T"): 1, ("aged", "<T"): 1, ("aged", ">=T"): 0}
    assert sum(R3.split_deaths(arm, "conventional", 10, 3).values()) == 1  # only a, in [10, 13)


def test_own_table_bounds_the_starved_and_reconciles_with_history(tmp_path):
    # one fauna: x survives seasons 0-2 earning 0.5; y (energy 0.1 after season 0) starves in season 1
    lin = [{"generation": 0, "population": "holistic", "name": n, "parents": [], "energy": e, "age": 1, "last_score": 0.5, "food": 1.0, "work": 1000.0}
           for n, e in (("x", 3.0), ("y", 0.1))]
    lin += [{"generation": g, "population": "holistic", "name": "x", "parents": [], "energy": 3.0, "age": g + 1, "last_score": 0.5, "food": 1.0, "work": 1000.0}
            for g in (1, 2)]
    (tmp_path / "lineage.jsonl").write_text("\n".join(json.dumps(r) for r in lin) + "\n")
    hist = [{"season": s, "population": k, "alive": a, "deaths": d, "total_energy": 3.0 * a}
            for s, a, d in ((0, 2, 0), (1, 1, 1), (2, 1, 0)) for k in ("holistic",)]
    hist += [{"season": s, "population": "conventional", "alive": 0, "deaths": 0, "total_energy": 0.0} for s in range(3)]
    (tmp_path / "history.json").write_text(json.dumps({"history": hist}))
    out, H = OWN.build(str(tmp_path))
    row = {(r[0], r[1]): r for r in out}[(1, "holistic")]
    s, k, alive, eh, ran, st, ag, ns, ub, food, work = row
    assert (ran, st, ag) == (1, 1, 0) and ns == 0.5
    assert abs(ub - (0.5 + (0.25 - 0.1)) / 2) < 1e-12  # the starved one's net is at most 0.25 - 0.1
    assert abs(work - 0.03) < 1e-12
    assert OWN.reconcile(out, H) == (4, 4)
