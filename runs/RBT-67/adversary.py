"""Adversary probe for RBT-67 §2: is the depth-4 path sum a convergent quantity at all?

RBT-67 reports that the realised `a` read back at depth 4 diverges from the installed `a` on
three of fourteen robots, and explains it as "drive effectors in loops with |w| > 1". That is
right and understates it. The path sum is sum_k M^k, which converges only if the recurrent
core's spectral radius is below 1. This measures rho per robot and reports `a` at increasing
truncation depth, so the question becomes whether "realised a" is a property of the circuit or
of where the counting stopped.

Pure linear algebra on committed genotypes. No simulation. Usage: adversary.py
"""
import json, sys, numpy as np, glob, os
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

POOLS = {
 "W4b-801": ("docs/artifacts/RBT-23-W4b-801", "docs/artifacts/RBT-23-W4b-801/conventional/best_gen*.json"),
 "P-801":   ("runs/RBT-19/P-801", "runs/RBT-19/P-801/conventional/best_gen0{000,100,200,300,400,500,590}.json"),
}
P801_GENS = (0,100,200,300,400,500,590)

def rows(label):
    d, pat = POOLS[label]
    cfg = SimConfig.from_dict(json.load(open(f"{d}/config.json"))["sim"])
    files = sorted(glob.glob(pat)) if label == "W4b-801" else [f"{d}/conventional/best_gen{g:04d}.json" for g in P801_GENS]
    for f in files:
        g = Genotype.load(f)
        ph = synthesize(g, cfg.synthesis)
        nose, eff = {}, {}
        for i,u in enumerate(ph.units):
            if u.part in (1,2) and u.unit.kind=="sensor" and u.unit.source=="food": nose[u.part]=i
            if u.part in (1,2) and u.unit.kind=="effector": eff[u.part]=i
        if len(nose)!=2 or len(eff)!=2: continue
        n=len(ph.units); M=np.zeros((n,n))
        for s,dd,w in ph.links: M[dd,s]+=w
        # install the a=64 antisymmetric motif: k = a/2 per link
        k=32.0
        M[eff[1],nose[1]]+=k; M[eff[2],nose[1]]+=k
        M[eff[1],nose[2]]-=k; M[eff[2],nose[2]]-=k
        # recurrent core = non-sensor units (sensors are overwritten each tick, they do not recur)
        core=[i for i,u in enumerate(ph.units) if u.unit.kind!="sensor"]
        rho=float(max(abs(np.linalg.eigvals(M[np.ix_(core,core)]))))
        # a at increasing truncation depth
        a_at=[]
        for depth in (1,2,4,6,8,12):
            s_={}
            for part,si in nose.items():
                v=np.zeros(n); v[si]=1.0; tot=np.zeros(n)
                for _ in range(depth):
                    v=M@v; tot+=v
                    if not v.any(): break
                s_[part]=tot[eff[1]]+tot[eff[2]]
            a_at.append((s_[1]-s_[2])/2.0)
        yield os.path.basename(f), rho, a_at

for label in POOLS:
    print(f"\n=== {label}: a=64 installed; spectral radius of the recurrent core, and a at depth d ===")
    print(f"{'robot':<18} {'rho':>7} | " + " ".join(f"{'d='+str(d):>12}" for d in (1,2,4,6,8,12)))
    for name, rho, a_at in rows(label):
        flag = "  <-- DIVERGES" if rho > 1.0 else ""
        print(f"{name:<18} {rho:7.3f} | " + " ".join(f"{x:12.1f}" for x in a_at) + flag)
