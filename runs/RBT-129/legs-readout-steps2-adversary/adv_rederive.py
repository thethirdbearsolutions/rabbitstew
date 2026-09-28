"""RBT-129 steps2 adversary: independent parse of the 12 steps2 designed.txt files (PR #487)."""
import re,glob,os,statistics as st
T975=[0,12.706,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262,2.228,2.201,2.179,2.160,2.145,2.131,2.120]
T95=[0,6.314,2.920,2.353,2.132,2.015,1.943,1.895,1.860,1.833,1.812,1.796,1.782,1.771,1.761,1.753,1.746]
class stats:
  class t:
    @staticmethod
    def ppf(p,df): return (T975 if p>0.96 else T95)[df]
import sys
S=sys.argv[1]  # dir of <cell>/designed.txt, each restored with scripts/durable.sh restore
# t quantiles tabulated (no scipy); LOO below is on the approximate per-host reconstruction, descriptive only
cells=['c1-p030-U-L','c2-p030-U-L','c1-p030-U-G','c2-p030-U-G','c1-p030-HP-L','c2-p030-HP-L','c1-p030-HP-G','c2-p030-HP-G','c1-p030-PW-L','c2-p030-PW-L','c1-p030-PW-G','c2-p030-PW-G']
prize={}
for l in open('runs/RBT-129/legs-readout/legs_readout.txt'):
    m=re.match(r'\| (c\d-p030-\w+-\w) \| ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\] \| (yes|no) \|',l)
    if m and m.group(1) not in prize: prize[m.group(1)]=(float(m.group(2)),float(m.group(3)),float(m.group(4)),m.group(5))
def tint(x,conf=.95):
    n=len(x); m=st.mean(x); se=st.stdev(x)/n**.5; t=stats.t.ppf(1-(1-conf)/2,n-1); return m,m-t*se,m+t*se
def reading(x,d=0.10):
    if len(x)<2: return 'NOT READABLE'
    m,lo,hi=tint(x); _,l9,h9=tint(x,.90)
    if lo>0: return 'NOSE LEADS'
    if hi<0: return 'SPEED LEADS'
    if l9>-d and h9<d: return 'COMPARABLE'
    return 'TIED, UNRESOLVED'
def lab_from(m,lo,hi,n,d=0.10):
    t95=stats.t.ppf(.975,n-1); t90=stats.t.ppf(.95,n-1); se=(hi-lo)/2/t95
    if lo>0: return 'NOSE LEADS'
    if hi<0: return 'SPEED LEADS'
    if m-t90*se>-d and m+t90*se<d: return 'COMPARABLE'
    return 'TIED, UNRESOLVED'
for c in cells:
    T=open(f'{S}/{c}/designed.txt').read()
    assert f'128 paired seeds from 126000' in T and "# fairness: 'fair'" in T and f'config/{c}/config.json' in T
    sg=re.search(r'direction: (\d+) signed',T).group(1)
    L=re.search(rf'STEP {c} \| nose step w 3 -> 3.4 .*vs per-unit speed \(n (\d+); (\d+) out for > 25% exploded\): ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\] (.*)',T)
    n,k,m,lo,hi,lab=int(L[1]),int(L[2]),float(L[3]),float(L[4]),float(L[5]),L[6].strip()
    # per-host table
    rows={}
    for h,*v in re.findall(r'^\| (O1/\S+) \| '+r' \| '.join([r'([\d.]+)']*12)+r' \| ([\d ]+) \|',T,re.M):
        rows[h]=[float(a) for a in v[:12]]+[list(map(int,v[12].split()))]
    rr={}
    for h,w,rm,rmean in re.findall(r'^\| (O1/\S+) \| (\d) \| ([\d.]+) \| ([\d.]+) \|',T,re.M):
        if w=='3': rr[h]=(float(rm),float(rmean))
    expl=sum(sum(v[12]) for v in rows.values())
    def line(which,drop=None):
        x=[]
        for h,v in rows.items():
            if h==drop: continue
            r=rr[h][which]
            if r<1.10: continue
            w3,w34,sp=v[4],v[5],v[8]
            x.append((w34-w3)-(sp-w3)*0.25/(r-1))
        return x
    med=line(0); mn=line(1)
    rm,rl,rh=tint(med)
    ok=max(abs(rm-m),abs(rl-lo),abs(rh-hi))<=0.01
    loo=sorted(set(reading(line(0,h)) for h in rows if rr[h][0]>=1.10)) 
    mmn=tint(mn)
    P=prize[c]; pays_rule=(P[3]=='yes') and lab in('NOSE LEADS','COMPARABLE')
    print(f"{c}|signed {sg} hosts {len(rows)}|expl {expl}|n {n} k {k} medcnt {sum(1 for h in rr if rr[h][0]>=1.10)}|{m:+.3f} [{lo:+.3f},{hi:+.3f}] {lab} relab={lab_from(m,lo,hi,n)}|prize {P}|PAYS {pays_rule}|recon {rm:+.3f}[{rl:+.3f},{rh:+.3f}] ok={ok} LOO {loo}|meanr n={len(mn)} {mmn[0]:+.3f}[{mmn[1]:+.3f},{mmn[2]:+.3f}] {reading(mn)}")
