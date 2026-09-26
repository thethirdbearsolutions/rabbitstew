import sys, runpy, os
opened = set()
def hook(ev, args):
    if ev == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        opened.add(os.path.relpath(os.fspath(args[0])))
sys.addaudithook(hook)
script = sys.argv[1]; sys.argv = sys.argv[1:]
so = sys.stdout; sys.stdout = open(os.devnull, "w")
try:
    runpy.run_path(script, run_name="__main__")
finally:
    sys.stdout = so
    for p in sorted(opened):
        if "site-packages" not in p and "/lib/python" not in p and not p.endswith(".pyc"):
            print(p)
