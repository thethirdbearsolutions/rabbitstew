"""RBT-131 design adversary: re-run the checkpoint sweep independently on 20 random ckpt/* branches (random.seed(131)),
comparing member *names* in order, not only counts:  <kind>/final/NNN.json's "name" at index i against
state.json's populations[kind][i]["name"] (ecology runs), and noting whether platform.json exists and records resumes.

    python runs/RBT-131/design-adversary/probe_ckpt_sample.py > runs/RBT-131/design-adversary/probe_ckpt_sample.txt
Reads only.
"""
import io, json, os, random, re, shutil, subprocess, tarfile, tempfile

REMOTE = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout.strip()
MEMBER = re.compile(r"^(.+)/([^/]+)/final/(\d+)\.json$")
allb = sorted(l.split()[1][len("refs/heads/"):] for l in subprocess.run(["git", "ls-remote", "origin", "refs/heads/ckpt/*"], capture_output=True, text=True, check=True).stdout.splitlines())
random.seed(131)
pick = sorted(random.sample(allb, 20))
print(f"# {len(allb)} ckpt branches; sample of 20 (random.seed(131))")
tot = {"runs": 0, "eco_with_final": 0, "name_mismatch": 0, "platform": 0, "resumes": 0}
for b in pick:
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "init", "-q", "--bare", tmp], check=True)
        subprocess.run(["git", "-C", tmp, "fetch", "-q", "--depth", "1", REMOTE, f"+refs/heads/{b}:refs/heads/x"], check=True)
        names = subprocess.run(["git", "-C", tmp, "ls-tree", "--name-only", "x"], capture_output=True, text=True, check=True).stdout.split()
        blob = b"".join(subprocess.run(["git", "-C", tmp, "cat-file", "blob", f"x:{p}"], capture_output=True, check=True).stdout
                        for p in sorted(n for n in names if n.startswith("run.tar.gz.part")))
    finally:
        shutil.rmtree(tmp)
    runs = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for m in tar.getmembers():
            if not m.isfile():
                continue
            hit = MEMBER.match(m.name)
            if hit:
                runs.setdefault(hit.group(1), {}).setdefault("final", {}).setdefault(hit.group(2), {})[int(hit.group(3))] = json.load(tar.extractfile(m)).get("name")
            elif os.path.basename(m.name) in ("state.json", "config.json", "platform.json"):
                runs.setdefault(os.path.dirname(m.name), {})[os.path.basename(m.name)] = json.load(tar.extractfile(m))
    for d, r in sorted(runs.items()):
        if "final" not in r and "state.json" not in r:
            continue
        tot["runs"] += 1
        cfg, st, plat = r.get("config.json") or {}, r.get("state.json"), r.get("platform.json")
        eco = "ecology" in cfg
        tot["platform"] += plat is not None
        nres = len(plat.get("resumes", [])) if isinstance(plat, dict) else 0
        tot["resumes"] += nres > 0
        out = []
        for kind, files in sorted(r.get("final", {}).items()):
            got = [files[i] for i in sorted(files)]
            if eco and st is not None:
                want = [m["name"] for m in st["populations"].get(kind, [])]
                ok = got == want and sorted(files) == list(range(len(files)))
                tot["name_mismatch"] += not ok
                out.append(f"{kind}: final {len(got)} state {len(want)} names-in-order-equal {ok}")
            else:
                out.append(f"{kind}: final {len(got)} (arena, population_size {cfg.get('population_size')})")
        if eco and r.get("final"):
            tot["eco_with_final"] += 1
        print(f"{b} {d} eco={eco} platform.json={'yes' if plat is not None else 'no'} resumes={nres} | " + ("; ".join(out) or "no final/"))
print(f"# {tot['runs']} run directories; {tot['eco_with_final']} ecology runs with a final/; {tot['name_mismatch']} kind-level name mismatches; "
      f"{tot['platform']} with platform.json; {tot['resumes']} recording a resume")
