"""RBT-106 P1 readout adversary: does `readout.py --no-peek H` (a) reproduce P1-readout.txt, (b) open no HU-*/HP-*
path, and (c) leave every P-pair number exactly as the pre-change readout.py computes it?

  (a) runs the branch's readout.py as `--pairs H,P --no-peek H` in-process, with builtins.open, os.path.exists,
      os.listdir, os.scandir and os.stat wrapped to record every path touched; its stdout is compared byte for byte
      with the committed P1-readout.txt.
  (b) fails if any recorded path contains /HU- or /HP- (the wrappers REFUSE such a path before the call).
  (c) loads the integration-branch readout.py (before the --no-peek diff; given as a file path) as a module and
      calls its pair("P", SEEDS) directly (the P pair only: no H file can be reached from it), under the same
      guard, and compares its output with the new readout's P section minus the lines the diff adds (the
      per-arm usability block and the predictions block).

readout.py's t intervals need scipy (not a declared dependency), so this runs in a scratch venv with scipy; it is
not part of the suite.  Usage: nopeek_check.py OLD_READOUT_PY
"""
import builtins
import contextlib
import importlib.util
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R106 = os.path.dirname(HERE)
TOUCHED = []


def _guard(p):
    s = os.fspath(p) if not isinstance(p, int) else ""
    TOUCHED.append(s)
    if "/HU-" in s or "/HP-" in s or os.path.basename(s).startswith(("HU-", "HP-")):
        raise RuntimeError(f"NO-PEEK VIOLATION: {s}")


_open, _exists, _listdir, _scandir, _stat = builtins.open, os.path.exists, os.listdir, os.scandir, os.stat
builtins.open = lambda p, *a, **k: (_guard(p), _open(p, *a, **k))[1]
os.path.exists = lambda p: (_guard(p), _exists(p))[1]
os.listdir = lambda p=".": (_guard(p), _listdir(p))[1]
os.scandir = lambda p=".": (_guard(p), _scandir(p))[1]


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def main(old_path):
    new = load("readout_new", os.path.join(R106, "readout.py"))
    buf = io.StringIO()
    sys.argv = ["readout.py", "--pairs", "H,P", "--no-peek", "H"]
    with contextlib.redirect_stdout(buf):
        new.main()
    out = buf.getvalue()
    ref = _open(os.path.join(R106, "P1-readout.txt")).read()
    print(f"(a) readout.py --pairs H,P --no-peek H reproduces P1-readout.txt byte for byte: {out == ref}")
    bad = [p for p in TOUCHED if "/HU-" in p or "/HP-" in p]
    dirs = sorted({os.path.basename(os.path.dirname(p)) for p in TOUCHED if p.startswith(R106 + "/")})
    print(f"(b) paths touched: {len(TOUCHED)}, in directories {dirs}; any HU-/HP- path: {bool(bad)}")
    n_before = len(TOUCHED)
    old = load("readout_old", old_path)
    old.HERE = R106   # the old file is loaded from outside runs/RBT-106; its arm_dir() reads HERE at call time
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        old.pair("P", list(old.SEEDS))
    o = buf2.getvalue()
    p_new = out[out.index("## Pair P"):]
    keep, skip = [], False
    for line in p_new.splitlines():
        if line.startswith("usability per arm") or line.startswith("## Registered predictions"):
            skip = True
        elif skip and line.startswith("usable paired seeds"):
            skip = False
        if not skip:
            keep.append(line)
    stripped = "\n".join(keep).rstrip("\n")
    # the diff adds one blank line before "usability per arm"; normalise runs of blank lines on both sides
    norm = lambda t: "\n".join(l for i, l in enumerate(t.splitlines()) if l or (i and t.splitlines()[i - 1])).strip()
    print(f"(c) pre-change readout.py's pair('P') == the new P section minus the added print blocks: {norm(o) == norm(stripped)}")
    bad2 = [p for p in TOUCHED[n_before:] if "/HU-" in p or "/HP-" in p]
    print(f"    old pair('P') touched {len(TOUCHED) - n_before} paths; any HU-/HP- path: {bool(bad2)}")
    if norm(o) != norm(stripped):
        import difflib
        print("\n".join(difflib.unified_diff(norm(o).splitlines(), norm(stripped).splitlines(), "old", "new", lineterm="")))
    return 0 if (out == ref and not bad and not bad2 and norm(o) == norm(stripped)) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
