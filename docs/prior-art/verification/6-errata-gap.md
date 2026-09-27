# 6 — Errata check (paper 5 §0 + External sources; paper 7 §7) and 2025–2026 gap probe

Checked 2026-09-27 (UTC). Sources: arXiv abstract/HTML pages, Crossref REST API, PubMed E-utilities,
Semantic Scholar API, author pages (karlsims.com, tomray.me, shinyverse.org/larryy, faculty.hampshire.edu/lspector),
Swarthmore course pages. dblp returned a bot-challenge page and MIT Press (direct.mit.edu) returned 403 throughout,
so neither was used directly.

Line numbers: `P5` = docs/paper-5-the-blind-forager.md, `P7` = docs/paper-7-five-instruments.md.

---

## ERRATA

### E1. "Miconi (2011)" is the wrong author — the paper is Baptista & Costa (2011). SEVERITY: HIGH
- **P5:45** "open-ended foraging with no explicit fitness has its own line (Miconi, 2011; Utimula, 2025)"
- **P5:456** "Miconi, T. (2011). The evolution of foraging in an open-ended simulation environment. *EPIA 2011*, LNCS, Springer. doi:10.1007/978-3-642-24769-9_10"
- **Source:** the DOI resolves to Tiago Baptista & Ernesto Costa, "The Evolution of Foraging in an Open-Ended
  Simulation Environment", *Progress in Artificial Intelligence* (EPIA 2011), LNCS, pp. 125–137. Crossref and
  Semantic Scholar agree on the authors. Thomas Miconi is not an author. The paper's description ("evolving the agents'
  brain (a rule list) without any explicit fitness function … agents do evolve sustainable foraging behaviors")
  does support the *claim*, so only the attribution needs fixing. The LNCS volume should be 7026 (from ISBN
  978-3-642-24768-2), but I could not open dblp or Springer to confirm the number.
- **Links:** https://api.crossref.org/works/10.1007/978-3-642-24769-9_10 ;
  https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/978-3-642-24769-9_10?fields=title,authors
- **Fix:** "Baptista & Costa, 2011" in the text. The reference should read: Baptista, T. & Costa, E. (2011). The evolution of foraging in an
  open-ended simulation environment. *EPIA 2011*, LNCS, Springer, 125–137. doi:10.1007/978-3-642-24769-9_10.
  Also check whether "Miconi (2011)" appears anywhere else (for example RBT-71 notes or citations-check.txt).

### E2. Utimula (2025) is not a foraging paper. SEVERITY: MEDIUM
- **P5:45** cites Utimula (2025) as part of the line of "open-ended foraging with no explicit fitness".
- **Source (PubMed 39898762 abstract):** a "guideless" model in which Tierra- and CA-like cells move in 3-D space, with
  "no predefined fitness function or form that qualifies as a living creature". It produces dumbbell-shaped and
  reticulated creatures and focuses on reproduction and development. Foraging is not mentioned.
  The "fitness-free, grows morphology" description at P5:69–70 is correct. The "foraging" grouping at P5:45 is not.
- **Link:** https://pubmed.ncbi.nlm.nih.gov/39898762/
- **Fix:** move Utimula to the fitness-free morphology sentence, or reword to "open-ended evolution with no explicit fitness".

### E3. Paper 7 attributes morphological innovation protection to Cheney et al. 2016 (already known). SEVERITY: MEDIUM
- **P7:781–783** "Cheney, Bongard, SunSpiral & Lipson (2016) … give the canonical account … and propose morphological innovation protection."
- **Source:** morphological innovation protection is proposed in Cheney et al. 2018, *J. R. Soc. Interface* 15(143):20170937
  (arXiv 1706.06133 abstract: "morphological innovation protection … temporarily reduces selection pressure on recently
  morphologically-changed individuals"). The 2016 ALIFE abstract diagnoses premature morphological convergence and
  proposes nothing. P5:55–56 and P5:466–467 already have this right.
- **Links:** https://arxiv.org/abs/1706.06133 ; https://doi.org/10.1098/rsif.2017.0937

### E4. Mertan & Cheney: "reach unreachable pairs … and then discard them" joins two separate findings. SEVERITY: MEDIUM (interpretive)
- **P5:58–60** "the co-optimisers reach morphology-controller pairs that fixed-morphology optimisation cannot, and then
  discard them, 'regularly undervalu[ing] individuals with newly mutated bodies.'"
- **P7:786–788** "finds co-optimisation reaches pairs that fixed-morphology optimisation cannot, while the search discards them."
- **Source (arXiv 2508.17464 abstract):** the abstract reports two separate results.
  - (a) The search "gets stuck on morphologies one mutation away from better ones, because it regularly undervalues individuals with newly mutated bodies and eliminates promising morphologies".
  - (b) "*On the other hand*, co-optimizing … creates useful goal-switching, yielding morphology-controller pairs whose performance cannot be reached by optimizing the controller alone."
  
  Asked directly, the HTML full text does *not* say that the goal-switching pairs from (b) are later discarded. They are presented as a benefit.
  What gets discarded is "promising morphologies" and "offspring that would have been selected if their true fitness were known".
- **Link:** https://arxiv.org/abs/2508.17464 ; https://arxiv.org/html/2508.17464
- **Fix:** for example: "co-optimisation reaches pairs that fixed-morphology optimisation cannot, yet it also regularly
  undervalues newly mutated bodies and eliminates promising morphologies." The quotation itself is fine (see OK list).

### E5. The Mertan & Cheney venue is out of date: the paper is now published. SEVERITY: LOW
- **P5:57** "(2025)". **P5:453** "*Artificial Life*, accepted; extended from ALIFE 2025. arXiv:2508.17464". **P7:784–785** lists no authors, only the title and "(2025)".
- **Source:** the arXiv comment reads "Author's accepted manuscript accepted for publication in *Artificial Life* journal;
  extended version of conference paper presented at ALIFE 2025" (v2, 2026-08-12). Crossref now lists it as
  published online 2026-09-04: *Artificial Life*, doi:10.1162/ARTL.a.476 (pp. 1–20 in the online-first record, no volume or issue yet).
- **Links:** https://arxiv.org/abs/2508.17464 ; https://api.crossref.org/works/10.1162/ARTL.a.476
- **Fix:** Mertan, A. & Cheney, N. (2026). … *Artificial Life* (advance online). doi:10.1162/ARTL.a.476. Extended from ALIFE 2025;
  arXiv:2508.17464 (2025). P7 should name the authors in the text.

### E6. The Chaumont & Adami entry is incomplete. SEVERITY: LOW
- **P5:450** gives only the journal and DOI.
- **Source (Crossref):** *Genetic Programming and Evolvable Machines* 17(4): 359–390 (online 2016-06-07, issue Dec 2016).
- **Link:** https://api.crossref.org/works/10.1007/s10710-016-9270-z

### E7. The Chromaria entry has no pages or DOI. SEVERITY: LOW
- **P5:461** "*Proc. ALIFE 14*, MIT Press."
- **Source (Crossref):** *Artificial Life 14: Proceedings of the Fourteenth International Conference …*, MIT Press, 793–800.
  doi:10.7551/978-0-262-32621-6-ch128. The venue itself is correct.

### E8. Page-number conflicts between records (not errors in the paper, but worth knowing). SEVERITY: LOW / NOTE
- **Sims 1994b (P5:460)**, ALife IV pp. 28–39: **confirmed** by the footer of the author's own PDF ("Artificial Life IV
  Proceedings, ed. by R. Brooks & P. Maes, MIT Press, 1994, pp28-39"). Crossref's MIT Press digital-chapter record
  (10.7551/mitpress/1428.003.0007) gives 26–32. That is the digital edition's pagination. Keep 28–39.
- **Adami & Brown 1994 (P5:448)**, 377–381: this is the conventional citation (it appears in secondary bibliographies). The
  Crossref MIT Press digital-chapter record (10.7551/mitpress/1428.003.0049) gives 373–377. Given the Sims precedent,
  that record is probably digital pagination too, but I found no printed-page scan. Treat 377–381 as conventional and unconfirmed against print.
- **Utimula (P5:463)**: PubMed and Crossref carry a publication date of "2024 Feb 25" alongside 31(1):31–64, but the record's
  copyright line is "© 2025", PubMed entrez is 2025-02-03, and vol. 31 is the 2025 volume. The citation "(2025) 31(1):31–64" is right.
  If a reference manager shows 2024, that is a metadata error in the source. DOI 10.1162/artl_a_00466 is missing from P5:463 and could be added.

---

## CONFIRMED-OK claims

| Claim (location) | Verified against |
|---|---|
| Mertan & Cheney authors, title, arXiv 2508.17464 (P5:453, P7:784) | arXiv abs page |
| "1,305,840" voxel designs (P5:57, P7:786) | abstract: "a design space of 1,305,840 voxel-based soft robots" (all viable morphologies in the design space) |
| Quote "regularly undervalu[ing] individuals with newly mutated bodies" (P5:59–60) | abstract: "it regularly undervalues individuals with newly mutated bodies". The bracketed change is legitimate |
| Mertan & Cheney venue "Artificial Life, extended from ALIFE 2025" (P5:453) | arXiv comments field. Now superseded by the published record (E5) |
| Cheney et al. 2016: ALIFE 2016, MIT Press, 226–233; four authors (P5:451) | Crossref 10.7551/978-0-262-33936-0-ch042; Semantic Scholar |
| Cheney 2016 "morphology converges before the controller has caught up" (P5:53–54) | abstract: "premature convergence of the morphology (compared to the convergence point of optimizing controllers)" |
| Cheney 2016 "a body mutation is punished because the controller co-adapted to the old body no longer fits" (P5:54–55) | **Supported, but not by the abstract.** The abstract only names "a more fundamental problem … cemented in the theory of embodied cognition". Mertan & Cheney 2024 (arXiv 2402.09231, HTML) attribute the argument to [3] = Cheney 2016: "the brain and the body become more and more specialized for each other, making the overall performance … very sensitive to changes in either component", and "Cheney et al. [3] provides an embodied cognition perspective". The explicit "morphological changes adversely impact sensorimotor control" wording is from the 2018 abstract. The 2016 full text returned 403, so this rests on a secondary attribution by the same author. Acceptable. For safety, cite both 2016 and 2018 for the second half |
| Cheney et al. 2018, J R Soc Interface 15(143):20170937, MIP (P5:55–56, 452) | Crossref; arXiv 1706.06133 |
| Sims 1994a SIGGRAPH '94, 15–22 (P5:459) | Crossref 10.1145/192161.192167 |
| Sims 1994b Artificial Life 1(4):353–372 (P5:460) | Crossref 10.1162/artl.1994.1.4.353 |
| Division Blocks, GECCO 2007, 316–323, doi 10.1145/1276958.1277019 (P5:462) | Crossref; author page |
| Division Blocks "by natural selection" and energy "from a simulated sun" (P5:42–43) | author page abstract: "evolve, along with the blocks, by natural selection … all energy derives ultimately from a simulated sun via photosynthesis" |
| Geb "first such system to pass Bedau and Packard's activity statistics as unbounded" (P5:40–41) | Channon abstract: "Geb exhibits unbounded evolutionary activity, making it the first autonomous artificial system to pass this test". (This is the author's own claim. "Such system" is a fair gloss of "autonomous artificial system".) |
| Channon 2001, ECAL 2001 LNCS 2159, doi 10.1007/3-540-44811-X_45 (P5:449) | Crossref (pp. 417–426, which could be added) |
| Chromaria: the first condition is a minimal criterion for reproduction (P5:43–44) | Semantic Scholar abstract (four conditions, Chromaria built to test them), plus secondary summaries listing condition (1) as "individuals must meet a minimal criterion in order to reproduce" |
| Adami & Brown 1994, ALife IV, MIT Press; Avida gives Tierra-like systems 2-D geometry (P5:38–39, 448) | arXiv adap-org/9405003 ("to appear in the Proc. of 'Artificial Life IV', MIT Press"; "two-dimensional geometry"). Pages: see E8 |
| Ofria & Wilke 2004, Artificial Life 10(2):191–229 (P5:457) | Crossref |
| Ray 1991, Artificial Life II, Addison-Wesley, 371–408 (P5:458) | tomray.me/pubs (author page). The author page gives SFI series "vol. XI" |
| Yaeger 1994, Artificial Life III, Addison-Wesley, 263–298 (P5:464) | shinyverse.org/larryy/Polyworld.html (author page) |
| Miconi & Channon 2006, ALIFE X, MIT Press, 255–261; a near-exact reimplementation of Sims (P5:46, 454) | secondary bibliographies and ResearchGate summary ("nearly exact reimplementation"). There is no Crossref record, and the paper was not opened. Same status as the paper already reports |
| Evosphere, CEC 2008, IEEE 4631212; "microplanet"; fighting and damage (P5:47–48, 455) | Crossref 10.1109/cec.2008.4631212 (pp. 3066–3073, which could be added); the IEEE abstract via search summary ("evolve freely on the surface of a 'microplanet'"). "No fitness function" matches the abstract's framing against "explicit, human-defined fitness functions" |
| Chaumont & Adami: explicit, staged fitness; co-evolved bodies; no designed body (P5:68–69) | arXiv 1112.5116 abstract ("evolutionary 'staging' … a particular fitness function … progressively altered") |
| Utimula: fitness-free, grows morphology (P5:69–70); Artificial Life 31(1):31–64 | PubMed 39898762 |

### 2005 proposal bibliography (claims supplied in the brief. The PDF could not be text-extracted here because poppler is absent and pypdf is broken)
| Claim | Result |
|---|---|
| Bongard & Paul 2001, "Making evolution an offer it can't refuse: morphology and the extradimensional bypass", ECAL 2001, LNCS 2159 | **OK.** Crossref 10.1007/3-540-44811-x_43, pp. 401–412. Same ISBN (3540425675) as Channon's LNCS 2159 chapter |
| Bongard & Paul 2000 SAB, "Investigating morphological symmetry and locomotive efficiency using virtual embodied evolution" | **OK.** MIT Press *From Animals to Animats 6* chapter exists (direct.mit.edu record, CiNii). Secondary citations give pp. 420–429 |
| Pollack, Lipson, Hornby, Funes 2001, Artificial Life 7(3) | **The proposal's "7:215–23" is CORRECT.** Crossref 10.1162/106454601753238627: "Three Generations of Automatically Designed Robots", *Artificial Life* 7(3):215–223. The brief's suggested 225–251 is wrong |
| Funes & Pollack 1997, ECAL, "Computer evolution of buildable objects", pp. 358–367 | **OK (secondary).** Husbands & Harvey (eds), *Fourth European Conference on Artificial Life*, MIT Press, 358–367, as cited in secondary literature. No Crossref record |
| Dellaert & Beer 1994, ALife IV | **OK.** Crossref 10.7551/mitpress/1428.003.0028, "Toward an Evolvable Model of Development for Autonomous Agent Synthesis", *Artificial Life IV* (digital pp. 239–250) |
| Balakrishnan & Honavar 1996, GP-96, "On sensor evolution in robotics" | **OK (secondary).** Proc. 1st Annual Conf. on Genetic Programming, MIT Press, pp. 455–460 (as cited in MDPI *Sensors* 25(3):725, 2025) |
| Ray 2000, "Aesthetically evolved virtual pets", ALife VII workshop | **OK.** The author page gives the *Artificial Life 7 Workshop Proceedings* (2000), pp. 158–161. The journal version is *Leonardo* 34(4):313–316 (2001) |
| Stober & Gold 2003, Swarthmore project URL | **OK.** https://www.cs.swarthmore.edu/~meeden/cs81/s03/projects/stober-gold.pdf returns HTTP 200 (PDF, 621 KB). The course syllabus (…/s03/syllabus.html) lists "Jeremy Stober and Jonah Gold. Evolvable morphologies for robot [controllers]". I could not text-extract the PDF (custom font encoding) |
| (Also) Salmon 2003 URL in docs/origins/README.md | OK: HTTP 200, and the syllabus lists "Branen Salmon. Embodied evolution in a morphologically heterogeneous population of robots." |

---

## GAP PROBE (2025–2026 refresh)

**Window:** searches ran 2026-09-27 from 20:37:48Z to 20:40:04Z UTC (WebSearch). I did not log a separate timestamp for each query.
Order below is execution order. Follow-up record fetches (arXiv abs pages, PubMed, Crossref) are interleaved with the searches.

1. `fixed morphology versus evolved morphology open-ended evolution artificial ecosystem energy reproduction 2025 2026 arXiv`
2. `body-brain co-evolution artificial ecosystem no fitness function energy metabolism reproduction robots 2026`
3. `"hand-designed" robot body baseline versus co-evolved bodies same environment natural selection artificial life 2025`
4. `ALIFE 2026 conference proceedings evolved virtual creatures ecosystem morphology evolution natural selection`
5. `embodied evolution robot swarm morphology evolution decentralized reproduction energy 2025 2026 paper`
6. `"morphological evolution" "without a fitness function" OR "no explicit fitness" virtual creatures 2025 2026`
7. `brain-body co-optimization 2026 arXiv morphology controller new benchmark results follow-up Mertan Cheney`
8. `LLM-designed robot morphology 2025 2026 RoboMorph Text2Robot large language model robot design evolution`
9. `GECCO 2026 evolutionary robotics morphology evolution population ecology fixed body comparison paper`
10. `Artificial Life journal 2026 evolving creatures morphology open-ended ecology foraging energy MuJoCo`
11. `heritability lifetime reproductive success artificial life simulation evolved agents parent-offspring regression 2025`
12. `EvoStar 2026 EvoApplications robot morphology evolution artificial life ecosystem paper`
13. `Nature OR Science 2025 2026 evolving robot bodies and brains simulation natural selection population ecology study`
14. `"fixed morphology" agents compete with "evolving morphology" agents shared environment resource competition reproduction simulation`
15. `arXiv 2025 2026 open-ended evolution 3D physics creatures energy food reproduction population no fitness morphology neural network simulation`
16. `"designed" robot versus "evolved" robots artificial ecology "realised" OR "realized" energy intake comparison evolutionary robotics 2025`
17. `Text2Robot evolutionary robot design from text descriptions arXiv ICRA 2025`

### Relevant hits (each checked against its own record)

- **Bejjani, Van Amburg, Wang, Su, Pratt, Mazloumi, Khoshnevis, Kakade, Brantley & Walsman (2025). "The Emergence of Complex
  Behavior in Large-Scale Ecological Environments." arXiv:2510.18221 (v1 2025-10-21, v3 2025-12-12).** This is the closest new hit
  on the fitness-free side. Agents "have no explicit rewards or learning objectives but instead evolve over time according to
  reproduction, mutation, and selection". The paper studies how physical scale and population size shape emergent behaviour. The abstract does not
  mention evolved morphology, and there is no designed-body comparison and no yield comparison.
- **Mertan & Cheney (2025). "Controller Distillation Reduces Fragile Brain-Body Co-Adaptation and Enables Migrations in
  MAP-Elites." arXiv:2504.06523, GECCO 2025 (Complex Systems track, full paper).** A follow-up to the fragile co-adaptation line:
  body mutations that move offspring into new niches "break the robots' fragile brain-body co-adaptation". "Pollination"
  (distilled generalist controllers) increases successful body mutations and migrations. It uses an explicit objective (QD) and no ecology.
  Directly relevant to strand 1 and its argument that the problem lies in the search, and a candidate citation beside the 2016/2018/2025 papers.
- **Song, Yang, Xu, Wen, Peng, Li, Zhou & Yao (2026). "Shaping the Evolutionary Dynamics of Robot Morphology via Adaptive
  Control Learning." arXiv:2608.23100 (2026-08-24).** This is independent support for the same point: "Premature fitness evaluation
  systematically underestimates true potential and biases selection towards fast learners" (voxel soft robots). It is
  co-design with explicit evaluation, has no fixed-body baseline and no ecology.
- **Wang, Li, Guo & Kriegman (2026). "ECo-MoE: Embodiment-Conditioned Mixture of Experts Increases the Evolvability of
  Robots." arXiv:2605.24225 (2026-05-22).** Embodiment-gated expert controllers that preserve sensorimotor knowledge across
  evolving body plans. Explicit goal-directed objective, no ecology, no fixed-body comparison.
- **Wang, Chen, Zhang, Yin, Chang, Li, Wang & Wang (2025). "Embodied Co-Design for Rapidly Evolving Agents: Taxonomy, Frontiers,
  and Challenges." arXiv:2512.04770 (v2 2025-12-17).** A survey of 100+ co-design studies. Its "Open-Ended Co-Design" section
  (IV-D, read in the HTML) covers only POET-style brain-body-environment co-evolution (POET, Stensby et al., MECE, LLM-POET)
  and developmental evolution. It names no fitness-free ecology with a designed body. Useful as evidence that the survey
  literature does not occupy the configuration.
- **Finn & Bräunl (2026). "An Open and Accessible Platform for Evolving Virtual Creatures." *Artificial Life* 32(1):23–45,
  doi:10.1162/ARTL.a.457 (PubMed 42518294).** The Simsulator: a Unity/DOTS Sims-style evolved-creature platform for 10,000+ agents.
  A platform paper with no fitness-free economy and no designed-body comparison.
- **Hein & Bongard (2026). "Environmental resilience via morphological diversity within machines." arXiv:2608.02395.**
  Composite machines built from morphologically diverse sub-agents. No ecology, reproduction or energy economy. Not a counter-example.
- **Huang, Guo, Zhang, Ji & Liu (2024). "CompetEvo: Towards Morphological Evolution from Competition." IJCAI 2024,
  arXiv:2405.18300.** (This is before the 2025 window, but it was surfaced by query 14 and is close in *form*.) Morph-evolving agents
  fight fixed-morph agents in the same arena and "obtain advantages in combat" over them. It is a ranked, zero-sum
  combat task, not a fitness-free foraging economy, and compares no income or heritability. If anything it resembles the
  *arena* configuration of papers 1–4. Worth citing as the contrast case.
- **LLM-driven design:** RoboMorph (Qiu et al., arXiv:2407.08626; ICLR 2025 workshop per ML Anthology. A search summary
  said ICRA 2026, which I did not confirm) and Text2Robot (Ringel, Charlick, Liu, Xia & Chen, ICRA 2025, pp. 5789–5797,
  doi:10.1109/ICRA55743.2025.11128168). Both are explicit-objective design optimisers with no ecology. Not counter-examples.
- **de Pinho & Sinapayen (2026). "A speciation simulation that partly passes open-endedness tests." arXiv:2603.01701.**
  Bedau-Packard activity statistics on ToLSim. Not embodied and no morphology. Relevant only as a modern Geb-style activity-test paper.
- Nothing relevant surfaced for GECCO 2026 (accepted-papers page not indexed in results), EvoStar 2026 (only
  Rossi, Nielsen & Iacca on distributed VSR controllers, per a search summary I did not verify), Nature/Science 2025–2026, or
  heritability of lifetime yield in artificial life (hits were wild-population quantitative genetics and AEGIS, a
  life-history IBM with no embodiment).

### Verdict
**The configuration is still unoccupied as far as this probe can see.** In 17 fresh queries plus record fetches I found no 2025–2026
paper (and none earlier beyond what the 2026-09-14 probe listed) that places a designed or fixed body and co-evolved bodies
in the *same* fitness-free, energy/reproduction-driven economy and compares realised income. I also found none that reports
parent-offspring heritability of lifetime yield beside the heritability of a competitive score.

The nearest new neighbours each lack a key element:
- Bejjani et al. 2025: fitness-free ecology, but no morphology and no designed body.
- CompetEvo 2024: fixed-morph against evolving-morph in one arena, but ranked combat, not a fitness-free economy.
- Mertan & Cheney GECCO 2025 and Song et al. 2026: fragile co-adaptation and undervaluation of new bodies, under explicit objectives.

Caveats: this was about two and a half minutes of search wall-clock (plus fetches). It is not systematic. dblp and MIT Press were unreachable,
and the ALIFE 2026 and GECCO 2026 proceedings were not browsed paper by paper.

**Suggested additions to the related work:** Mertan & Cheney 2025 (GECCO, arXiv:2504.06523), Bejjani et al. 2025 (arXiv:2510.18221) and CompetEvo (IJCAI 2024).

---

## UNVERIFIED

- **Cheney et al. 2016 full text**: direct.mit.edu returned 403 on both the HTML and the PDF. The co-adaptation half of P5:54–55 rests on the
  abstract plus Mertan & Cheney 2024's attribution (see OK table).
- **Adami & Brown printed page range** (377–381 vs Crossref digital 373–377): not checked against a print scan.
- **Miconi & Channon 2006 (ALIFE X, 255–261)**: no Crossref or DOI record. Checked only against secondary bibliographies and a ResearchGate summary.
- **Evosphere abstract wording**: IEEE Xplore not fetched directly. "Microplanet" was confirmed via the search-engine rendering of the IEEE abstract and the
  ResearchGate record.
- **Baptista & Costa LNCS volume number (7026)**: inferred from the ISBN only.
- **2005 proposal text itself**: I could not extract the PDF (no pdftotext/poppler; pypdf crashes on a cryptography import), so the
  proposal's bibliography was checked using the claims as given in the brief, not the PDF's own wording.
- **Funes & Pollack 1997 pages, Balakrishnan & Honavar pages, Bongard & Paul 2000 pages**: secondary citations only.
- **RoboMorph's venue** (ICLR 2025 workshop vs ICRA 2026) and **the EvoStar 2026 Rossi et al. title**: taken from search summaries, not confirmed on the records.
