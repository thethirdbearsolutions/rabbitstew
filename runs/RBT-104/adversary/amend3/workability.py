"""RBT-104 design adversary, Amendment 3 re-check: can the window readings be regenerated, and does
the readout accept what Amendment 3's peek.py writes?

No arm output is read.  The input is a THROWAWAY run made by this probe: RBT-90 part 2's command,
seed 801, the pre-registered seeded founders (seed_founders.py, digest 78493e74...), --link-scale 8,
8 seasons (an S8-801 in miniature, in a scratch directory).

  1. copy the run, and mark its state.json as finished (season 600) in the copy only, since
     peek.py refuses a window reading on an unfinished arm;
  2. run Amendment 3's peek.py main() with its WINDOW set to (5, 599), so that season 5 takes the
     window path (the arithmetic is peek.py's own; only the season constant is moved);
  3. hand the printed file to Amendment 3's readout.peek() and check it parses, carries k_bare and
     reads HELD on k_planted;
  4. do the same with the launch commit's peek.py output format (no k_bare): readout must refuse it.

Usage: workability.py AMEND3_CHECKOUT MINI_RUN OUT_DIR
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys

amend, mini, out = sys.argv[1], sys.argv[2], sys.argv[3]
here = os.path.join(amend, "runs", "RBT-104")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


run = os.path.join(out, "S8-801-mini")
shutil.rmtree(run, ignore_errors=True)
shutil.copytree(mini, run)
st = json.load(open(os.path.join(run, "state.json")))
real = st["season"]
st["season"] = 600
json.dump(st, open(os.path.join(run, "state.json"), "w"))

peek = load("a3_peek", os.path.join(here, "peek.py"))
peek.WINDOW = (5, 599)
sys.argv = ["peek.py", run, "801", "--season", "5"]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    peek.main()
txt = buf.getvalue()
print(f"# RBT-104 adversary: Amendment 3 window reading, regenerated on a throwaway S8-801 mini-run "
      f"({real} seasons run; state marked finished in a copy)\n")
print("## Amendment 3's peek.py output (window path, season 5)\n")
print(txt)
f = os.path.join(out, "peek-window-a3.txt")
open(f, "w").write(txt)
ro = load("a3_readout", os.path.join(here, "readout.py"))
r = ro.peek(f)
print(f"## readout.peek() on it: {r}")
ok = r is not None and r["k_bare"] is not None and r["above"] == (r["k"] > r["B"])
print(f"   parses, carries k_bare, HELD on k_planted: {'YES' if ok else 'NO'}")
old = [l for l in txt.splitlines() if l.startswith("WINDOW")][0].split("; k_bare")[0]
g = os.path.join(out, "peek-window-launch-format.txt")
open(g, "w").write(old.replace(f"k = {r['k']},", f"k = {r['k'] + r['k_bare']},") + "\n")
print(f"## the launch commit's format (k counted bare-rooted hits, no k_bare): {open(g).read().strip()}")
print(f"   readout.peek() -> {ro.peek(g)}  (must be None: refused)")
