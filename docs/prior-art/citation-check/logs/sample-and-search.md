# Random-sample script and novelty-search queries (RBT-122 citation check, 2026-09-27)

## Random sample (Python 3.11)

```python
import re, random
L = open('docs/prior-art/REVIEW.md').read().split('\n')   # at 6513164
s = L.index('## 1. Body–brain co-evolution after Sims'); e = L.index('## 8. Errata to our own papers')
ents = [(i+1, m.group(1)) for i in range(s, e)
        for m in [re.match(r'^- \*\*(.+?)\*\*', L[i])]
        if m and re.search(r'\(\d{4}[a-z]?\)|et al\.', m.group(1))]          # 103 entries
load = ['Sims','Conrad, M. (1990)','Bongard, J. C. & Paul, C. (2001)','Watson, R. A., Ficici, S. G. & Pollack, J. B. (1999)',
        'Lehman, J., Clune','Bredeche, N., Haasdijk','Taylor, T. & Massey','Krčah','Auerbach','Cheney, N., MacCurdy',
        'Mühlenbein','Bedau','Channon, A. (2006)','Channon, A. (2024)','Williams','Nygaard, T. F., Martin, C. P., Torresen']
pool = [x for x in ents if not any(x[1].startswith(k) for k in load)]   # 87 entries
random.seed(122); pick = sorted(random.sample(pool, 15))
```

Output: lines 122, 139, 170, 222, 230, 241, 270, 291, 367, 370, 412, 455, 466, 467, 519.

## Novelty-search queries (WebSearch unless marked)

**C1 (evolved against hand-designed body):**
- "co-design morphology versus fixed hand-designed morphology matched compute benchmark multiple tasks 2024"
- "brain-body co-design benchmark "hand-designed" baseline outperform evolved morphology same budget"
- "evolved versus designed robot morphology comparison matched evaluations multiple environments "fixed morphology" baseline Evolution Gym 2025"
- ""fixed morphology" OR "default morphology" baseline "same number of" environment steps co-design MuJoCo transform2act BodyGen"

**C2 (fitness-free economy):**
- "open-ended artificial life ecosystem evolved morphology energy foraging no fitness function virtual creatures 2025"
- "Bejjani 2025 evolution morphology artificial life"
- "ecosystem simulation evolving morphology agents compete energy "hand-designed" species introduced artificial life 2024 OR 2025 OR 2026"

**C3 (realised heritability):**
- "realised heritability artificial selection experiment evolutionary robotics virtual creatures divergent selection lines"
- ""random selection" control lines "realized heritability" digital organisms OR Avida OR "evolutionary robotics" artificial selection experiment"
- Crossref `query=realized heritability robot evolution`

**C4 (extradimensional bypass):**
- ""extradimensional bypass" robot morphology evolution"
- ""extradimensional bypass" 2020..2026 soft robot OR morphology OR "virtual creatures""
- ""extradimensional bypass" Paul 2005 OR Inden OR neuroevolution test morphology added dimensions"
- Crossref "extradimensional bypass", from 2015: no evolutionary-computation hits

**C5 (measurement bugs):**
- "catalogue of evaluation bugs reinforcement learning benchmarks measurement errors bugs reported results evolutionary computation"
- "empirical study of bugs in reinforcement learning evaluation code taxonomy reward logging metric bugs 2023 2024"
- "errors in benchmark function implementations evolutionary computation CEC benchmark bug discovered results invalid"

**Records for the hits:**
- arXiv abstract pages, in `novelty-neighbours-arxiv.txt`;
- Crossref for Pagliuca & Nolfi (doi:10.1177/1059712321994685, *Adaptive Behavior* 30(3): 245–255).
