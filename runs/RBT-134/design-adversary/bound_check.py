import re,sys
fmax={"tanh":1.0,"sin":1.0,"relu":1.0,"integrate":2*(1-0.9**12),"abs":0.0,"differentiate":0.0,"sign":0.0}
RUNGS=(6.2831,12.5236,24.7145)
for f in sys.argv[1:]:
    rows=[l.split("|")[1:-1] for l in open(f) if l.startswith("| W4b") or l.startswith("| P-801")]
    viol=[];absrows=[]
    fm_abs=dict(fmax,abs=1.0)
    cnt={x:0 for x in RUNGS};cnt2={x:0 for x in RUNGS}
    for r in rows:
        lab,i,fn,bk,bE,asis,com,tanh,bk0,bE0,unit,prod=[c.strip() for c in r]
        asis=abs(float(asis));prod=abs(float(prod))
        if asis>fmax[fn]*prod+1e-9: viol.append((lab,i,fn,bk,asis,prod))
        if fn=="abs": absrows.append((i,bk,asis,prod))
        for x in RUNGS:
            cnt[x]+= fmax[fn]*prod>=x; cnt2[x]+= fm_abs[fn]*prod>=x
    print(f, "n=",len(rows),"bound violations:",len(viol))
    for v in viol: print("   VIOLATION",v)
    print("   abs arrivals (lineage,b_k,|asis|,|prod|):",absrows)
    print("   slope bound as committed:",cnt," | with f'max(abs)=1:",cnt2)
