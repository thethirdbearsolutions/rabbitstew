"""Independent verification of the audit's two load-bearing claims.

Written from scratch, not reusing any audit script, because the orchestrator's own
dominant hypothesis (the DC pedestal) was just refuted and nothing here should be
taken on trust.

CLAIM A: the Pioneer's two drive wheels are hinged about their own OUTWARD normals,
         so effector SUM is the steering axis and effector DIFFERENCE is the throttle -
         the transpose of a textbook differential drive.
CLAIM B: a 4-link antisymmetric motif  W[e1,n1]=W[e2,n1]=+w, W[e1,n2]=W[e2,n2]=-w
         (which puts 2w(n1-n2) on the steering axis and exactly zero on the throttle)
         earns roughly +0.9 items against a 1.52 baseline.
"""
import json, numpy as np, mujoco
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN="runs/RBT-23/W4b-801"; GENS=(90,190,290,390,490,550,590); SEEDS=[9000+i for i in range(64)]
cfg=SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])

def units(gen):
    ph=synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), cfg.synthesis)
    nose={}; eff={}
    for i,u in enumerate(ph.units):
        if u.part in (1,2) and u.unit.kind=='sensor' and u.unit.source=='food': nose[u.part]=i
        if u.part in (1,2) and u.unit.kind=='effector': eff[u.part]=i
    return nose,eff

def bout(task):
    gen,seed,cond,w=task
    c=replace(cfg,random_start=True)
    g=Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim=Simulation([g],c,spawns=spawn_layout(1,c,seed)); sim.set_food_seed(seed)
    nose,eff=units(gen); W=sim.brains[0].W
    if cond=='motif':          # antisymmetric: 2w(n1-n2) onto SUM, zero onto DIFFERENCE
        W[eff[1],nose[1]]+=w; W[eff[2],nose[1]]+=w
        W[eff[1],nose[2]]-=w; W[eff[2],nose[2]]-=w
    elif cond=='spike':        # what the compass spike actually installed, matched signs
        W[eff[2],nose[1]]+=w; W[eff[1],nose[2]]+=w
    for _ in range(int(round(c.duration/c.control_dt))): sim.step()
    return (gen,seed,cond,w,float(sim.food_eaten[0]))

if __name__=="__main__":
    # ---- CLAIM A: hinge axes -------------------------------------------------
    g=Genotype.load(f"{RUN}/conventional/best_gen0590.json")
    c=replace(cfg,random_start=True)
    sim=Simulation([g],c,spawns=spawn_layout(1,c,0))
    m,d=sim.model,sim.data; mujoco.mj_forward(m,d); idx=sim.robots[0]
    ax=[]
    for j in idx.joints[1:3]:
        if j>=0: ax.append(d.xaxis[j].copy())
    print("CLAIM A - wheel hinge axes in the world frame")
    for i,a in enumerate(ax): print(f"  wheel {i+1} axis {np.round(a,4)}")
    if len(ax)==2:
        dot=float(np.dot(ax[0],ax[1]))
        print(f"  dot product = {dot:+.4f}   -> {'ANTIPARALLEL: sum steers, difference throttles' if dot<-0.99 else 'parallel: textbook differential drive'}")

    # ---- CLAIM B: does the antisymmetric motif earn food? --------------------
    tasks=[(gn,s,'base',0.0) for gn in GENS for s in SEEDS]
    for w in (8.0,16.0,32.0):
        tasks+=[(gn,s,'motif',w) for gn in GENS for s in SEEDS]
    tasks+=[(gn,s,'spike',32.0) for gn in GENS for s in SEEDS]
    with Pool(4) as p: rows=p.map(bout,tasks,chunksize=16)
    by={(r[0],r[1],r[2],r[3]):r[4] for r in rows}
    def boot(v,draws=20000,seed=5):
        rng=np.random.default_rng(seed); v=np.asarray(v,float)
        m=np.array([rng.choice(v,len(v)).mean() for _ in range(draws)])
        return v.mean(),np.percentile(m,2.5),np.percentile(m,97.5)
    base=float(np.mean([by[(gn,s,'base',0.0)] for gn in GENS for s in SEEDS]))
    print(f"\nCLAIM B - baseline solo yield {base:.3f} items (7 robots x 64 paired seeds)")
    print("| condition | k on steering axis | delta items | 95% CI | robots improved |")
    print("|---|---|---|---|---|")
    for cond,w,k in [('motif',8.0,'+16'),('motif',16.0,'+32'),('motif',32.0,'+64'),('spike',32.0,'~0 (common mode)')]:
        per=[float(np.mean([by[(gn,s,cond,w)]-by[(gn,s,'base',0.0)] for s in SEEDS])) for gn in GENS]
        mu,lo,hi=boot(per)
        print(f"| {cond} w={w:g} | {k} | {mu:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {sum(1 for x in per if x>0)}/7 |")
        if cond=='motif' and w==32.0: print(f"    per-robot: {[round(x,2) for x in per]}")
