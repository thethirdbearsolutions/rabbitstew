"""Adversary: holistic founding per founder draw (seed) at c0-p030-U-L, seeds 129001-129008
(129001-3 census, 129004 pilot S, 129005-8 the anchor-fallback S 0-59 runs), and at c1-p030-U-L (pilot, 0-299)."""
import json, os
S = os.environ.get('DATA', 'data') + ''
def info(d, upto=59):
    h = json.load(open(f'{d}/history.json'))['history']
    out = []
    for k in ('holistic', 'conventional'):
        last = max([x['season'] for x in h if x['population'] == k and x['alive'] - x['births'] > 0], default=-1)
        a = [x['alive'] - x['births'] for x in h if x['population'] == k and x['season'] == upto]
        out.append(f"{k[:4]} alive@{upto} {a[0] if a else 0:>2} lastlive {last:>3}")
    fh = sorted((json.loads(l)['name'], json.loads(l)['nodes']) for l in open(f'{d}/lineage.jsonl')
                if '"generation": 0,' in l and '"population": "holistic"' in l and '"parents": []' in l)
    return ' | '.join(out) + f" | holistic founders {len(fh)}, node-count sum {sum(n for _, n in fh)}"
for pt in ('c0-p030-U-L',):
    for s in range(129001, 129009):
        d = f'{S}/0/{pt}/{s}/S'
        if not os.path.exists(d): d = f'{S}/P/{pt}/{s}/S'
        print(pt, s, info(d))
for pt in ('c1-p030-U-L', 'c0-p030-U-L', 'c1-p030-PW-G'):
    for s in range(129001, 129005):
        d = f'{S}/P/{pt}/{s}/S'
        if os.path.exists(f'{d}/history.json'): print('pilot', pt, s, info(d, 239))
