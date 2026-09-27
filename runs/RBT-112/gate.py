"""RBT-112's launch gate, pinned to RBT-106's registered H readout (PREREGISTRATION.md §7.1; adversary F11, ruling 03:32).

What is read: the output of RBT-106's own `runs/RBT-106/readout.py` (unchanged), section "## Pair H: HU (uniform) against
HP (patchy)", and in it exactly two lines, as that script prints them (its l. 199 and 234):
  HELD: HU <nU>, HP <nP>;  paired log-excess ...     field nU: #HELD(HU) over RBT-106's usable HU-HP pairs
  VERDICT H: <label> ...                              label: VOID / SUPPORTED / FALSIFIED-a / FALSIFIED-b / NOT DECIDED
#HELD(HU) is RBT-106's number, not RBT-112's (RBT-112's HU count, over HU-HZ pairs, is the readout's, not the gate's).
The text is RBT-106's committed readout output if a path is given; otherwise RBT-106's readout.py is run here, unchanged.

The rule (every H verdict covered; no branch is left to judgement):
  WAIT    the H section prints NOT READ (an H arm has not finished), or has no VERDICT H line: H has not read.
  LAUNCH  VERDICT H is not VOID and nU <= 2, whatever the label (SUPPORTED, FALSIFIED-b or NOT DECIDED): in the uniform
          world the default operator's arms did not hold the compass, which is HZ's premise.
  CLOSE   VERDICT H is not VOID and nU >= 3 (FALSIFIED-a always is, nU >= 5): the uniform world already holds it under
          the default operator; RBT-112 is not needed.
  VOID    H is VOID: the premise is read from the HU arms alone, with RBT-106's own files and parsers (its readout.py,
          imported).  An HU arm counts if viable, on x86_64, of c872e80's code (RBT-106's commit record) and passing
          analyse.py's positive control (its install control is not required: F13); HELD as RBT-106 reads it (held-300,
          held-599, k_planted > B).  LAUNCH iff at least 7 HU arms count and at most 2 of them are HELD; otherwise CLOSE
          (unread).
  Ambiguous text (the H section missing, or its HELD line absent, duplicated or unparseable while a VERDICT H line is
  present): the given file is set aside, RBT-106's readout.py is run here unchanged and read by the same rule; if that
  is still ambiguous, the VOID branch's HU-arms-alone rule decides.

Usage: gate.py [RBT106_READOUT_TXT]   -> prints GATE: WAIT | LAUNCH | CLOSE, with the line and field read
"""
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)
HU_MAX = 2
MIN_USABLE = 7


def h_section(text):
    m = re.search(r"^## Pair H: HU \(uniform\) against HP \(patchy\).*?(?=^## |\Z)", text, re.M | re.S)
    if m:
        return m.group(0)
    # RBT-106's readout prints VERDICT H after the pair's lines; take the text up to it if the header was lost
    return None


def parse(text):
    """('WAIT'|'READ'|'AMBIGUOUS', label, nU)."""
    sec = h_section(text)
    if sec is None:
        return ("AMBIGUOUS", None, None)
    if re.search(r"^NOT READ:", sec, re.M):
        return ("WAIT", None, None)
    v = re.findall(r"^VERDICT H: (VOID|SUPPORTED|FALSIFIED-a|FALSIFIED-b|NOT DECIDED)", sec, re.M)
    if not v:
        return ("WAIT", None, None)
    if len(v) > 1:
        return ("AMBIGUOUS", None, None)
    h = re.findall(r"^HELD: HU (\d+), HP (\d+);", sec, re.M)
    if v[0] == "VOID":
        return ("READ", "VOID", int(h[0][0]) if len(h) == 1 else None)
    if len(h) != 1:
        return ("AMBIGUOUS", v[0], None)
    return ("READ", v[0], int(h[0][0]))


def decide(label, nU):
    if label == "VOID":
        return None
    return "LAUNCH" if nU <= HU_MAX else "CLOSE"


def hu_alone(seeds=SEEDS):
    """The VOID branch: (LAUNCH|CLOSE, counted, held) from the HU arms alone, with RBT-106's parsers."""
    spec = importlib.util.spec_from_file_location("rbt106_readout_gate", os.path.join(ROOT, "runs", "RBT-106", "readout.py"))
    r106 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r106)
    counted = held = 0
    for s in seeds:
        d = os.path.join(ROOT, "runs", "RBT-106", f"HU-{s}")
        side = r106.side(d) if os.path.isdir(d) else None
        ok, _ = r106.platform_ok(d)
        a = r106.rbt102(d)
        c = r106.commit(d)
        if side and side["viable"] and ok and a and a.get("pc_pass") and c and c["tree"] == r106.REF_TREE:
            counted += 1
            h3, h5 = r106.held(d, 300), r106.held(d, 599)
            held += bool(h3 and h5 and h3["held"] and h5["held"])
    return ("LAUNCH" if counted >= MIN_USABLE and held <= HU_MAX else "CLOSE"), counted, held


def run_readout():
    return subprocess.run([sys.executable, os.path.join(ROOT, "runs", "RBT-106", "readout.py"), "--pairs", "H"],
                          cwd=ROOT, capture_output=True, text=True).stdout


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    text = open(src).read() if src else run_readout()
    state, label, nU = parse(text)
    how = src or "RBT-106 readout.py --pairs H, run here"
    if state == "AMBIGUOUS" and src:
        print(f"# {src}: the H section is ambiguous; RBT-106's readout.py is run here unchanged instead")
        text, how = run_readout(), "RBT-106 readout.py --pairs H, run here (the given file was ambiguous)"
        state, label, nU = parse(text)
    print(f"# RBT-112 gate: read from {how}")
    if state == "WAIT":
        print("GATE: WAIT (RBT-106's H has not read: NOT READ, or no VERDICT H line)")
        return
    if state == "AMBIGUOUS" or label == "VOID":
        g, counted, held = hu_alone()
        why = "H is VOID" if label == "VOID" else "the H readout is ambiguous"
        print(f"{why}: HU arms alone, {counted} counted (viable, x86_64, c872e80, analyse.py control), {held} HELD "
              f"(LAUNCH iff >= {MIN_USABLE} counted and <= {HU_MAX} HELD)")
        print(f"GATE: {g}")
        return
    print(f"VERDICT H: {label}; line 'HELD: HU nU, HP nP': nU = {nU} (LAUNCH iff nU <= {HU_MAX}, whatever the label)")
    print(f"GATE: {decide(label, nU)}")


if __name__ == "__main__":
    main()
