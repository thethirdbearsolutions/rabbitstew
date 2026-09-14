import sys, numpy as np
rows=[]
for l in sys.stdin:
    p=[x.strip() for x in l.strip().strip('|').split('|')]
    if len(p)<5: continue
    try: rows.append((int(p[0]), float(p[2]), float(p[3]), float(p[4])))
    except ValueError: continue
g=np.array([r[0] for r in rows]); R=np.array([r[1] for r in rows])
fl=np.array([r[2] for r in rows]); dv=np.array([r[3] for r in rows])
print(f"n={len(g)} parents, generations {g.min()}..{g.max()}")
def spear(x,y):
    rx=np.argsort(np.argsort(x)).astype(float); ry=np.argsort(np.argsort(y)).astype(float)
    rx-=rx.mean(); ry-=ry.mean()
    d=np.sqrt((rx**2).sum()*(ry**2).sum()); return (rx*ry).sum()/d if d else np.nan
def pp(x,y,n=100000,seed=3):
    rng=np.random.default_rng(seed); o=spear(x,y); yy=np.asarray(y,float).copy(); c=0
    for _ in range(n):
        rng.shuffle(yy)
        if abs(spear(x,yy))>=abs(o): c+=1
    return o,(c+1)/(n+1)
for lbl,m in (("ALL",g>=0),("drop gen10",g>10),("gens>=100",g>=100),("gens>=200",g>=200)):
    o,q=pp(g[m],dv[m]); print(f"  mean_dev vs generation  {lbl:11s} n={m.sum():2d}  rho={o:+.3f}  p={q:.4f}")
o,q=pp(R,fl); print(f"\n  ARTIFACT flip vs R_parent  rho={o:+.3f}  p={q:.4f}")
o,q=pp(R,dv); print(f"  ARTIFACT dev  vs R_parent  rho={o:+.3f}  p={q:.4f}")
los=[spear(np.delete(g,i),np.delete(dv,i)) for i in range(len(g))]
print(f"\n  leave-one-out rho range: {min(los):+.3f} .. {max(los):+.3f}")
early=dv[g<300]; late=dv[g>=300]
print(f"\n  mean deviation: gens<300 {early.mean():.1f} deg (n={len(early)})  gens>=300 {late.mean():.1f} deg (n={len(late)})")
rng=np.random.default_rng(1); obs=early.mean()-late.mean(); pool=np.concatenate([early,late]); c=0
for _ in range(100000):
    rng.shuffle(pool)
    if abs(pool[:len(early)].mean()-pool[len(early):].mean())>=abs(obs): c+=1
print(f"  difference {obs:+.1f} deg, permutation p={(c+1)/100001:.4f}")
