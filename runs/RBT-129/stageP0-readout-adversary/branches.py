"""Adversary: expected ckpt branches for the P-0 lanes vs git ls-remote, without stages.py."""
import json,glob,sys,re
from collections import Counter
refs={l.split()[1].replace('refs/heads/ckpt/','') for l in open(sys.argv[1])}
jobs=[json.loads(l) for p in sorted(glob.glob('runs/RBT-129/lanes/P-0/host*.jsonl')) for l in open(p) if l.strip()]
lab=lambda d:'rbt-129-'+d.split('runs/RBT-129/',1)[1].strip('/').replace('/','-')
want={lab(j['dir']) for j in jobs}
units={tuple(j['name'].split('/')[1:3]) for j in jobs if j['name'].startswith('P/')}
want|={f'rbt-129-stageP-{p}-{s}-record' for p,s in units}
print('lane jobs',len(jobs),'| pilot units',len(units),'| expected branches',len(want))
miss=sorted(w for w in want if w not in refs); print('missing',len(miss),miss[:5])
extra=sorted(r for r in refs if r.startswith(('rbt-129-stage0','rbt-129-stageP')) and r not in want)
print('stage0/P branches not in the P-0 lanes:',len(extra),dict(Counter(re.sub(r'.*-(unit|prize|steps2|steps)$',r'\1',e) for e in extra)))
