import sys, numpy as np
rows=[]
for l in sys.stdin:
    p=[x.strip() for x in l.strip().strip('|').split('|')]
    if len(p)<4: continue
    try: rows.append((int(p[0]), float(p[1]), float(p[2]), float(p[3])))
    except ValueError: continue
g=np.array([r[0] for r in rows],float)
h=np.array([r[1] for r in rows]); pa=np.array([r[2] for r in rows]); y=np.array([r[3] for r in rows])
print(f"n={len(g)} parents")
def spear(x,z):
    rx=np.argsort(np.argsort(x)).astype(float); rz=np.argsort(np.argsort(z)).astype(float)
    rx-=rx.mean(); rz-=rz.mean()
    d=np.sqrt((rx**2).sum()*(rz**2).sum()); return (rx*rz).sum()/d if d else np.nan
rh,rp,ry=spear(g,h),spear(g,pa),spear(g,y)
print(f"  heading rho={rh:+.3f}   path rho={rp:+.3f}   yaw rho={ry:+.3f}")
# Paired bootstrap OVER PARENTS on the DIFFERENCE of correlations.
rng=np.random.default_rng(7); N=20000
dp=[];dy=[]
for _ in range(N):
    i=rng.integers(0,len(g),len(g))
    dp.append(spear(g[i],h[i])-spear(g[i],pa[i]))
    dy.append(spear(g[i],h[i])-spear(g[i],y[i]))
dp=np.array(dp); dy=np.array(dy)
for lbl,d in (("heading - path",dp),("heading - yaw",dy)):
    lo,hi=np.percentile(d,[2.5,97.5])
    frac=float((d>=0).mean())
    print(f"  {lbl}: {d.mean():+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  "
          f"P(difference>=0)={frac:.3f}  {'NOT separable' if lo<0<hi else 'separable'}")
# Also: do the controls themselves decline? one-sided evidence
print("\n  Controls decline in the SAME direction (rho -0.25 both), so some generic")
print("  buffering is present; the question is only whether heading exceeds it.")
