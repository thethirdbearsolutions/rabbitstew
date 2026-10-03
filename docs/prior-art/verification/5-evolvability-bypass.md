# Citations: evolvability / selection-response benchmarks and Conrad's extradimensional bypass

Verification method key:
- **CR**: Crossref API record (`api.crossref.org/works/<DOI>`) matched authors, year, title, venue, volume/pages.
- **PM**: PubMed record (eutils efetch) with abstract.
- **S2**: Semantic Scholar Graph API record (abstract and/or citation contexts).
- **PDF**: I read the full text of the author-hosted PDF.
- **AP**: author's own publication page, or a library catalogue record for books.

Summaries come from the abstract or full text I read. Where a summary relies on an abstract only, it says so.

---

## TOPIC 1: Evolvability, selection response, drift controls

### Digital organisms / ALife platforms

**Lenski, R. E., Ofria, C., Pennock, R. T., & Adami, C. (2003).** The evolutionary origin of complex features. *Nature*, 423(6936), 139–144. https://doi.org/10.1038/nature01568
- Verified: CR + PM (PMID 12736677).
- In Avida, digital organisms evolved complex logic functions (EQU) by building on simpler functions that were also rewarded. When the simpler functions were not rewarded, EQU did not evolve. No single intermediate was essential, and some mutations that were deleterious when they appeared later served as stepping stones. This is the standard "selection is doing the work" demonstration in digital organisms. Its control is a changed reward structure, not neutral lines.

**Ofria, C., & Wilke, C. O. (2004).** Avida: A software platform for research in computational evolutionary biology. *Artificial Life*, 10(2), 191–229. https://doi.org/10.1162/106454604773563612
- Verified: CR + PM (PMID 15107231).
- Describes the Avida platform: self-replicating programs, configurable experimental protocols, and built-in measurement and analysis tools. It is the methods reference for Avida-based experiments.

**Covert, A. W., III, Lenski, R. E., Wilke, C. O., & Ofria, C. (2013).** Experiments on the role of deleterious mutations as stepping stones in adaptive evolution. *PNAS*, 110(34), E3171–E3178. https://doi.org/10.1073/pnas.1313424110
- Verified: CR + PM (PMID 23918358).
- An Avida "knock-out" design: populations in which deleterious mutations were disallowed, compared with controls in which they were allowed. The controls reached higher long-term fitness because deleterious mutations served as stepping stones across fitness valleys. The paper also varied neutral mutations, mutation rate and recombination. It is useful as a model of a counterfactual control arm in digital evolution, and as an Avida valley-crossing result (Topic 2).

### Evolutionary activity statistics and neutral "shadow" controls (evolution vs drift)

**Bedau, M. A., & Packard, N. H. (1992).** Measurement of evolutionary activity, teleology, and life. In C. G. Langton, C. Taylor, J. D. Farmer, & S. Rasmussen (Eds.), *Artificial Life II* (SFI Studies in the Sciences of Complexity, Vol. X, pp. 431–461). Addison-Wesley.
- Verified: AP (Bedau's publication page, https://people.reed.edu/~mab/publications/index.html; that page dates it 1991, while the volume is usually cited as 1992). Also corroborated by a web search. No DOI exists.
- Introduces "evolutionary activity" statistics: cumulative usage counts of components (genotypes or alleles) that persist in the population. The aim is to separate adaptively significant persistence from mere presence. This is the origin of the activity-statistics line of work.

**Bedau, M. A., Snyder, E., Brown, C. T., & Packard, N. H. (1997).** A comparison of evolutionary activity in artificial evolving systems and in the biosphere. In P. Husbands & I. Harvey (Eds.), *Proceedings of the Fourth European Conference on Artificial Life (ECAL97)* (pp. 125–134). MIT Press.
- Verified: AP (Bedau's publication page). No DOI found.
- Compares activity statistics for the artificial systems Evita and Bugs with the fossil record. According to Channon (2024; verified below), this paper "defined the first neutral shadow models". A shadow is a neutral analogue of the system in which reproducing individuals are chosen at random, so persistence cannot be due to adaptive significance. It is used to normalise activity.

**Bedau, M. A., Snyder, E., & Packard, N. H. (1998).** A classification of long-term evolutionary dynamics. In C. Adami, R. Belew, H. Kitano, & C. Taylor (Eds.), *Artificial Life VI* (pp. 228–237). MIT Press.
- Verified: AP (Bedau's publication page). Also listed as SFI Working Paper 98-03-025. No DOI found.
- Proposes a classification of evolving systems into classes such as none, bounded and unbounded evolutionary activity, using activity statistics normalised against neutral models. This became the "ALife test" later applied to Geb. I did not read the full text, so the exact shadow mechanics in this paper are not confirmed. Channon (2024) attributes the first shadow models to Bedau et al. (1997).

**Rechtsteiner, A., & Bedau, M. A. (1999).** A generic neutral model for quantitative comparison of genotypic evolutionary activity. In *Advances in Artificial Life (ECAL 1999)*, LNCS 1674, pp. 109–118. Springer. https://doi.org/10.1007/3-540-48304-7_17
- Verified: CR (title, authors, pages); the LNCS volume number comes from the DOI prefix and ECAL 1999. I could not access the abstract.
- Based on the title and record only: it proposes a system-independent neutral model as a baseline for genotypic evolutionary activity. Treat the content summary as tentative.

**Channon, A. (2001).** Passing the ALife test: Activity statistics classify evolution in Geb as unbounded. In *Advances in Artificial Life (ECAL 2001)*, LNCS 2159, pp. 417–426. Springer. https://doi.org/10.1007/3-540-44811-X_45
- Verified: CR + S2 abstract.
- Applies Bedau–Packard activity statistics to Geb and finds unbounded evolutionary activity, which Channon says makes it the first autonomous artificial system to pass that test. It then identifies two weaknesses in the test itself.

**Channon, A. (2006).** Unbounded evolutionary dynamics in a system of agents that actively process and transform their environment. *Genetic Programming and Evolvable Machines*, 7(3), 253–281. https://doi.org/10.1007/s10710-006-9009-3
- Verified: CR + S2 abstract.
- A detailed application of the Bedau et al. test to Geb. It criticises the test's normalisation method for artificial systems and proposes "component activity normalization" against a neutral shadow. Under the revised test, Geb still shows unbounded dynamics.

**Channon, A. (2024).** A procedure for testing for Tokyo Type 1 open-ended evolution. *Artificial Life*, 30(3), 345–355. https://doi.org/10.1162/artl_a_00430
- Verified: CR + PDF (author's final version at channon.net).
- Sets out a stepwise test for open-ended evolution. Step 2 requires a "shadow" model identical to the real system, run in parallel, "except that whenever selection operates in the real system, random selection should be employed in the shadow". The shadow is reset to the real system at each snapshot. This is the clearest modern statement of a random-selection drift control in ALife. The paper also traces the method's history back to Bedau et al. (1997).

**Channon, A. (2019).** Maximum individual complexity is indefinitely scalable in Geb. *Artificial Life*, 25(2), 134–144. https://doi.org/10.1162/artl_a_00285
- Verified: S2 record + abstract, and the MIT Press page in search results.
- Scales world length and maximum neurons per individual in Geb. Maximum individual complexity is bounded when either parameter is scaled alone, but grows without observed bound when both are scaled together. The paper restates Geb's status under the shadow-normalised activity test.

**Dolson, E. L., Vostinar, A. E., Wiser, M. J., & Ofria, C. (2019).** The MODES toolbox: Measurements of open-ended dynamics in evolving systems. *Artificial Life*, 25(1), 50–73. https://doi.org/10.1162/artl_a_00280
- Verified: CR + S2 abstract. A PeerJ preprint from 2018 also exists.
- Proposes standardised metrics for change, novelty, complexity and ecological potential in evolving systems, with C++ implementations. These are metrics for open-endedness rather than for response to selection. Its "change" metric is a filtered measure of persistent change, and it is related in spirit to a "is anything happening beyond drift" check.

### Quantitative genetics: realised heritability, selection experiments, Price equation

**Falconer, D. S., & Mackay, T. F. C. (1996).** *Introduction to Quantitative Genetics* (4th ed.). Longman. ISBN 0-582-24302-5.
- Verified: AP (WorldCat OCLC 34415160; a book review record on Semantic Scholar lists "Longman, 1996, xv and 464 pages, ISBN 0582 24302 5").
- The standard text for the response-to-selection equation R = h²S and for realised heritability, estimated as cumulative response over cumulative selection differential. It also covers divergent (up/down) selection lines with an unselected control line. Cite the relevant chapter on selection response and realised heritability. I did not verify chapter or page numbers.

**Hill, W. G., & Caballero, A. (1992).** Artificial selection experiments. *Annual Review of Ecology and Systematics*, 23, 287–310. https://doi.org/10.1146/annurev.es.23.110192.001443
- Verified: CR. Crossref also holds a duplicate DOI, 10.1146/annurev.ecolsys.23.1.287. S2 TLDR only; I did not read the text.
- A review of laboratory and field artificial selection experiments, in which strong known selection is applied over short timescales. It covers what such experiments reveal about quantitative-trait genetics, limits to selection, and effects on fitness. This is the reference for the experimental design conventions (replicate lines, controls, realised h²).

**Houle, D. (1992).** Comparing evolvability and variability of quantitative traits. *Genetics*, 130(1), 195–204. https://doi.org/10.1093/genetics/130.1.195
- Verified: CR + PM (PMID 1732160).
- Argues that narrow-sense heritability is usually an inappropriate measure of evolvability, and proposes mean-standardised additive variance (the coefficient of additive genetic variation, CV_A) instead. Fitness components have low h² because of high residual variance, not because of low additive variance. This bears directly on reporting only h² in a foraging-yield benchmark: also report mean-scaled response.

**Hansen, T. F., & Houle, D. (2008).** Measuring and comparing evolvability and constraint in multivariate characters. *Journal of Evolutionary Biology*, 21(5), 1201–1219. https://doi.org/10.1111/j.1420-9101.2008.01573.x
- Verified: CR + PM (PMID 18662244). Note the erratum, J Evol Biol 22(4):913–915 (2009).
- Uses the Lande equation (the multivariate R = Gβ) to derive evolvability, conditional evolvability, autonomy and integration measures from a G matrix. This extends the breeder's-equation logic to multivariate traits.

**Price, G. R. (1970).** Selection and covariance. *Nature*, 227(5257), 520–521. https://doi.org/10.1038/227520a0
- Verified: CR + PM (PMID 5428476).
- The Price equation, which splits change in mean trait into a selection (covariance) term and a transmission term. Altenberg (1994) uses it to analyse evolvability in GP. It is the general framework under which R = h²S is a special case.

### Breeder's equation in evolutionary computation

**Mühlenbein, H., & Schlierkamp-Voosen, D. (1993a).** Predictive models for the breeder genetic algorithm I. Continuous parameter optimization. *Evolutionary Computation*, 1(1), 25–49. https://doi.org/10.1162/evco.1993.1.1.25
- Verified: CR (S2 TLDR only).
- Introduces the Breeder Genetic Algorithm (BGA), which models truncation selection as practised by breeders. It uses response-to-selection models to predict performance on continuous test functions, with evaluations scaling roughly as n ln n.

**Mühlenbein, H., & Schlierkamp-Voosen, D. (1993b).** The science of breeding and its application to the breeder genetic algorithm (BGA). *Evolutionary Computation*, 1(4), 335–360. https://doi.org/10.1162/evco.1993.1.4.335
- Verified: CR. The abstract is summarised in search-result snippets from the ACM DL and MIT Press pages.
- The explicit bridge between quantitative genetics and genetic algorithms. It applies the response-to-selection equation and heritability, including regression estimates of heritability, to analyse and control selection, recombination and mutation in the BGA. **This is the closest EC precedent for estimating h² from R = h²S inside an evolutionary algorithm.**

### Evolvability concepts and measures

**Wagner, G. P., & Altenberg, L. (1996).** Perspective: Complex adaptations and the evolution of evolvability. *Evolution*, 50(3), 967–976. https://doi.org/10.1111/j.1558-5646.1996.tb02339.x (JSTOR: 10.2307/2410639)
- Verified: CR + PM (PMID 28565291).
- Frames evolvability in terms of the genotype–phenotype map and argues that modular (low-pleiotropy) representations make complex adaptation possible. The paper explicitly links the EC "representation problem" to biology.

**Altenberg, L. (1994).** The evolution of evolvability in genetic programming. In K. E. Kinnear Jr. (Ed.), *Advances in Genetic Programming* (Ch. 3, pp. 47–74). MIT Press.
- Verified: GP Bibliography record (gpbib kinnear_altenberg) + author-hosted PDF (dynamics.org/Altenberg/FILES/LeeEEGP.pdf) + an MIT Press chapter DOI record (10.7551/mitpress/1108.003.0008; Crossref lacks author metadata, so I cite it by book and pages).
- Uses Price's covariance and selection theorem to show how selection in GP can favour code blocks for their ability to produce fitter offspring ("evolvability"), not just their current fitness. It predicts a shift from exploration to conservation as populations mature, and proposes operators to manage this.

**Kirschner, M., & Gerhart, J. (1998).** Evolvability. *PNAS*, 95(15), 8420–8427. https://doi.org/10.1073/pnas.95.15.8420
- Verified: CR + PM (PMID 9671692).
- Defines evolvability as the capacity to generate heritable phenotypic variation. It attributes this capacity to properties such as weak linkage, compartmentation, redundancy and exploratory processes, which reduce constraint and let nonlethal variation accumulate.

**Pigliucci, M. (2008).** Is evolvability evolvable? *Nature Reviews Genetics*, 9(1), 75–82. https://doi.org/10.1038/nrg2278
- Verified: CR + PM (PMID 18059367).
- Reviews competing definitions of evolvability and asks whether evolvability evolves by selection or as a by-product. It positions evolvability as a pillar of an extended evolutionary synthesis.

**Reisinger, J., Stanley, K. O., & Miikkulainen, R. (2005).** Towards an empirical measure of evolvability. In *GECCO '05 Workshops* (Proceedings of the 7th Annual Workshop on Genetic and Evolutionary Computation), pp. 257–264. ACM. https://doi.org/10.1145/1102256.1102315
- Verified: CR (S2 TLDR only).
- Proposes measuring a representation's evolvability as its ability to extract invariant structure from a changing fitness function. This gives a basis for controlled experiments on what makes encodings evolvable.

**Lehman, J., & Stanley, K. O. (2013).** Evolvability is inevitable: Increasing evolvability without the pressure to adapt. *PLoS ONE*, 8(4), e62186. https://doi.org/10.1371/journal.pone.0062186 (correction: 10.1371/annotation/f4c5a0f3-cb53-4c05-a84c-f0aead483b77)
- Verified: CR + S2 abstract.
- Shows in simulated models that evolvability can rise under unbiased drift alone. Evolvable genotypes diffuse faster through phenotype space, and niche founders tend to be more evolvable. **This bears on drift controls: drift lines are not "nothing happens" baselines, because evolvability-related properties can still change in them.**

**Tarapore, D., & Mouret, J.-B. (2015).** Evolvability signatures of generative encodings: Beyond standard performance benchmarks. *Information Sciences*, 313, 43–61. https://doi.org/10.1016/j.ins.2015.03.046 (arXiv:1410.4985)
- Verified: CR + S2 abstract.
- Introduces "evolvability signatures", the post-mutation distributions of behavioural change and fitness change, as a benchmark complementary to task performance. Applied to five hexapod-gait encodings, the signatures predicted how quickly each encoding re-adapted after damage (SUPG was best). This is the explicit "beyond performance benchmark" precedent in evolutionary robotics.

**Wilder, B., & Stanley, K. O. (2015).** Reconciling explanations for the evolution of evolvability. *Adaptive Behavior*, 23(3), 171–179. https://doi.org/10.1177/1059712315584166
- Verified: CR (S2 TLDR only).
- Simulates evolution in gene-regulatory networks. It shows that which kind of evolvability is meant changes the dynamics, and argues that nonadaptive mechanisms are the most promising explanations.

**Mengistu, H., Lehman, J., & Clune, J. (2016).** Evolvability search: Directly selecting for evolvability in order to study and produce it. In *GECCO 2016*, pp. 141–148. ACM. https://doi.org/10.1145/2908812.2908838
- Verified: CR + S2 (S2 gives the full subtitle).
- Selects directly on evolvability, measured as the behavioural diversity of an individual's offspring. It produces highly evolvable individuals and makes evolvability easier to study.

**Lehman, J., Wilder, B., & Stanley, K. O. (2016).** On the critical role of divergent selection in evolvability. *Frontiers in Robotics and AI*, 3, 45. https://doi.org/10.3389/frobt.2016.00045
- Verified: CR + S2 abstract. (Found while searching; not on your list.)
- A conceptual review for evolutionary robotics. It argues that realising evolvability requires aligning selection with evolvability, and that divergent (novelty-style) selection is the key mechanism. Note that "divergent selection" here means novelty or diversity pressure, **not** the quantitative-genetics up/down-lines design. Flag this if the paper uses the term.

### Heritability measured in evolving robots / simulated artificial selection with control lines (found while searching)

**De Carlo, M., Ferrante, E., Zeeuwe, D., Ellers, J., & Eiben, A. E. (2023).** Heritability of morphological and behavioural traits in evolving robots. *Evolutionary Intelligence*. https://doi.org/10.1007/s12065-023-00860-0 (arXiv preprint 2110.11187, "Heritability in Morphological Robot Evolution", Oct 2021, which adds G. Meynen as an author)
- Verified: S2 record + abstract (journal, year, authors) and the arXiv abs page for the preprint. Crossref volume and page numbers were not confirmed (S2 lists pages 1–17 with no volume, i.e. online-first).
- Introduces parent–offspring-regression heritability as a tool for comparing genetic representations in robots that co-evolve morphology and control (direct tree encoding vs indirect grammar encoding). It tracks h² over evolution and relates it to the exploration/exploitation balance. **This is the closest robotics precedent for estimating h² of traits in evolved bodies.** It uses regression h², not realised h² from selection lines.

**Williams, H. T. P., & Lenton, T. M. (2007).** Artificial selection of simulated microbial ecosystems. *PNAS*, 104(21), 8918–8923. https://doi.org/10.1073/pnas.0610038104
- Verified: PM (PMID 17517642) + PMC full text (PMC1885603), read via WebFetch.
- Runs artificial ecosystem selection on an individual-based evolutionary simulation, with **"High" lines selected to maximise a trait, "Low" lines selected to minimise it, and a "Random" control line**. Each run had 30 iterations of directed selection followed by 30 of random selection. The authors state that "heritability can be inferred from the observed response to selection… If there were no heritability, no sustained deviation from the control line would have been observed", though they made no direct parent–offspring measurements. **This is the closest found precedent for an up/down/random-control divergent selection design in an artificial-life simulation.**

**Swenson, W., Wilson, D. S., & Elias, R. (2000).** Artificial ecosystem selection. *PNAS*, 97(16), 9110–9114. https://doi.org/10.1073/pnas.150237597
- Verified: CR. This is a biological (laboratory ecosystem) experiment, not ALife.
- The laboratory precedent that Williams & Lenton (2007) simulate: high and low selected lines of microbial ecosystems. The Williams & Lenton full-text summary reports that high and low lines diverged in two of three experiments. I did not open this paper's own abstract.

**Lalejini, A., Dolson, E., Vostinar, A. E., & Zaman, L. (2022).** Artificial selection methods from evolutionary computing show promise for directed evolution of microbes. *eLife*, 11, e79665. https://doi.org/10.7554/eLife.79665
- Verified: S2 record + abstract (eLife vol. 11). I did not confirm the article number via Crossref; it is taken from the DOI suffix.
- An agent-based model of directed microbial evolution comparing EC parent-selection schemes (tournament, lexicase, non-dominated elite) against laboratory elite and top-10% selection. It is a cross-over between EC and artificial selection, but it has no drift-control or h² component.

---

## TOPIC 2: Conrad's extradimensional bypass and later tests

**Conrad, M. (1990).** The geometry of evolution. *BioSystems*, 24(1), 61–81. https://doi.org/10.1016/0303-2647(90)90030-5
- Verified: CR + PM (PMID 2224072). **The DOI is confirmed.**
- Argues that evolvability can itself evolve, through association with reliability or by hitchhiking. Evolving requires a reasonable probability that variation carries a structure from one adaptive peak to another, while staying stable on a peak. Complex organisations with many components and interactions meet the peak-climbing condition more easily. Redundancy plus many weak interactions reconciles the two conditions. This is the source of the "extradimensional bypass": adding dimensions converts isolated peaks into ridges or saddles. Bongard & Paul (2001) cite this paper as ref. [5], "introduced by Conrad".

**Conrad, M. (1979).** Bootstrapping on the adaptive landscape. *BioSystems*, 11(2–3), 167–182. https://doi.org/10.1016/0303-2647(79)90009-1
- Verified: CR + PM (PMID 497367). **This paper exists.**
- The "bootstrap principle of evolutionary adaptability". Gene versions that are functionally equivalent can differ in how amenable they are to further evolution. Features that increase this amenability are costly, but they accumulate by hitchhiking with the adaptations they enable, so populations drift into regions of the landscape that are easier to climb.

**Conrad, M. (1983).** *Adaptability: The Significance of Variability from Molecule to Ecosystem*. Plenum Press, New York. ISBN 0-306-41223-3.
- Verified: AP (Internet Archive catalogue record, archive.org/details/adaptabilitysign0000conr; also a Springer book listing, ISBN 978-1-4615-8329-5). I did not confirm the Springer eBook DOI.
- Conrad's book-length treatment of adaptability, using information-theoretic (conditional-entropy) measures of adaptability across levels of organisation. It is the background to the 1990 geometry argument.

**Bongard, J. C., & Paul, C. (2001).** Making evolution an offer it can't refuse: Morphology and the extradimensional bypass. In J. Kelemen & P. Sosík (Eds.), *Advances in Artificial Life: ECAL 2001*, LNCS 2159, pp. 401–412. Springer. https://doi.org/10.1007/3-540-44811-X_43
- Verified: CR + PDF (full text read, https://meclab.w3.uvm.edu/papers/2001_ECAL_Bongard.pdf) + listed on Bongard's paper page. The editor names come from general knowledge of the LNCS 2159 volume and are not confirmed from the record; drop them if unsure.
- **Setup:** a simulated 5-link, 6-DOF biped (MathEngine physics) with a recurrent neural network controller of 60 synapse weights. A GA with population 300 ran for 300 generations with strong elitism (150 kept), tournament selection, one-point crossover and point mutation. Fitness was forward distance, with early termination on falls or running gaits.
- **Four conditions:** (1) fixed morphology (genome 60), 30 runs; (2) variable morphology, adding 3 segment-radius genes (genome 63), 30 runs; (3) fixed attached mass blocks (genome 60), 20 runs; (4) variable mass blocks, adding 8 block size/position genes (genome 68), 20 runs.
- **Results:** variable-radius populations outperformed fixed-morphology populations on average, despite the larger search space. The evolved morphologies did not converge on any particular or distant mass distribution: the vertical centre of mass of the best agents was spread roughly uniformly over 0.52–0.57. The authors therefore argue that the gain came from reshaped landscape topology, i.e. extradimensional bypasses, rather than from finding a better body. The supporting evidence is one lineage event: a child with 7 control mutations and 1 morphological mutation gained fitness from 15.03 to 23.17, versus 20.87 with the morphological mutation suppressed. With mass blocks, adding 8 morphological parameters gave **no** improvement: only 2 of 20 runs in each condition achieved stable walking.
- **Conclusion:** the right morphological parameters help, but arbitrary ones do not. No formal landscape analysis was done. The bypass explanation is a hypothesis supported by the absence of morphological convergence and by the single mutational example.

**Bongard, J. C., & Paul, C. (2000).** Investigating morphological symmetry and locomotive efficiency using virtual embodied evolution. In J.-A. Meyer et al. (Eds.), *From Animals to Animats 6: Proceedings of SAB 2000* (pp. 420–429). MIT Press. https://doi.org/10.7551/mitpress/3120.003.0045
- Verified: CR + PDF (full text read, https://meclab.w3.uvm.edu/papers/2000_SAB_Bongard.pdf).
- Introduces "Virtual Embodied Evolution" (GA co-evolution of morphology and control in physics simulation). It finds that agents with higher bilateral symmetry tended to locomote more efficiently. The paper does **not** discuss Conrad or the bypass; it is the methodological predecessor of the 2001 paper.

**Bongard, J. (2011).** Morphological change in machines accelerates the evolution of robust behavior. *PNAS*, 108(4), 1234–1239. https://doi.org/10.1073/pnas.1015390108
- Verified: CR + PM (PMID 21220304) + PDF.
- Simulated robots that grow during their lifetime from an eel-like (anguilliform) body into a legged one, with that developmental trajectory evolving so later generations are legged throughout. They evolved gaits for the final legged form faster, and the gaits were more robust, than robots evolved in the legged form only. A string search of the full text found **no mention of Conrad or "bypass"**. It is a related "change the body to make control search easier" result, framed as evolution of development or scaffolding, and should not be cited as a bypass test.

**Cheney, N., Bongard, J., SunSpiral, V., & Lipson, H. (2016).** On the difficulty of co-optimizing morphology and control in evolved virtual creatures. In *Proceedings of the Artificial Life Conference 2016* (pp. 226–233). MIT Press. https://doi.org/10.7551/978-0-262-33936-0-ch042
- Verified: CR + S2 abstract.
- Argues that co-evolving body and brain is fundamentally hard. Because of tight embodied coupling, morphological mutations usually break the tuned controller, which causes premature convergence of morphology. This is the counterpoint to the bypass optimism.

**Cheney, N., Bongard, J., SunSpiral, V., & Lipson, H. (2018).** Scalable co-optimization of morphology and control in embodied machines. *Journal of the Royal Society Interface*, 15(143), 20170937. https://doi.org/10.1098/rsif.2017.0937
- Verified: CR + S2 abstract.
- Proposes "morphological innovation protection", which temporarily reduces selection pressure on individuals whose morphology recently changed so that control can re-adapt. The authors show it avoids local optima and scales co-optimisation. The paper does not use bypass language in its abstract. The implication is that extra morphological dimensions help only if selection lets control catch up.

**Kriegman, S., Cheney, N., & Bongard, J. (2018).** How morphological development can guide evolution. *Scientific Reports*, 8, 13934. https://doi.org/10.1038/s41598-018-31868-7
- Verified: CR (a publisher correction also exists, 10.1038/s41598-018-33706-2) + S2 abstract. **I did not confirm the article number via Crossref; remove it if you need certainty.**
- When embodied agents develop and evolve, evolution finds body plans that are robust to control changes. Those body plans become genetically assimilated, but controllers do not, which lets evolution keep climbing by tinkering with controller development inside permissive bodies.

**Cheney, N., & Lipson, H. (2016).** Topological evolution for embodied cellular automata. *Theoretical Computer Science*, 633, 19–27. https://doi.org/10.1016/j.tcs.2015.06.024
- Verified: CR + S2 abstract.
- Evolves the shape (topology) of a 3D cellular-automaton soft robot under a fixed update rule to produce locomotion. The abstract makes no bypass or extra-dimension test, so it is **not** evidence for or against the bypass.

**Gavrilets, S. (1997).** Evolution and speciation on holey adaptive landscapes. *Trends in Ecology & Evolution*, 12(8), 307–312. https://doi.org/10.1016/S0169-5347(97)01098-7
- Verified: CR + PM (PMID 21238086).
- Argues that the rugged-landscape picture reflects three-dimensional intuition. In high dimensions, fitness landscapes are "holey", with connected ridges of viable genotypes, so Wright's valley-crossing problem "may be non-existent". This is the biological generalisation of Conrad's point.

**Gavrilets, S., & Gravner, J. (1997).** Percolation on the fitness hypercube and the evolution of reproductive isolation. *Journal of Theoretical Biology*, 184(1), 51–64. https://doi.org/10.1006/jtbi.1996.0242
- Verified: CR + PM (PMID 9039400).
- Studies viable/inviable (0/1) fitness on a hypercube. Above a percolation threshold, a giant connected cluster of viable genotypes spans genotype space, so populations can move along it by single substitutions without crossing valleys. Reproductive isolation then arises as a by-product.

**Kauffman, S., & Levin, S. (1987).** Towards a general theory of adaptive walks on rugged landscapes. *Journal of Theoretical Biology*, 128(1), 11–45. https://doi.org/10.1016/S0022-5193(87)80029-2
- Verified: CR + PM (PMID 3431131).
- Theory of adaptive walks (numbers of local optima, walk lengths) on uncorrelated and correlated landscapes. It is the precursor to NK models and includes a "complexity catastrophe" result.

**Wright, S. (1932).** The roles of mutation, inbreeding, crossbreeding and selection in evolution. *Proceedings of the Sixth International Congress of Genetics*, 1, 356–366.
- Verified: AP (CiNii bibliographic records, e.g. https://cir.nii.ac.jp/crid/1373101967230580356). No DOI exists.
- The first public presentation of the adaptive landscape diagram and of shifting-balance theory for crossing between peaks.

**Huynen, M. A., Stadler, P. F., & Fontana, W. (1996).** Smoothness within ruggedness: The role of neutrality in adaptation. *PNAS*, 93(1), 397–401. https://doi.org/10.1073/pnas.93.1.397
- Verified: CR + PM (PMID 8552647).
- RNA folding implies connected neutral networks of sequences with the same structure. Populations diffuse along them, which lets them search wide areas of genotype space while keeping their phenotype. This makes adaptation less sensitive to where it starts.

**Barnett, L. (1998).** Ruggedness and neutrality: The NKp family of fitness landscapes. In C. Adami et al. (Eds.), *Artificial Life VI* (pp. 18–27). MIT Press.
- Verified: author-hosted PDF (users.sussex.ac.uk/~lionelb/.../alife6_paper.pdf, listed in search results) + an ACM DL record (10.5555/286139.286143) from search results. No DOI in Crossref. I did not read the full text.
- Introduces NKp landscapes, which add tunable neutrality to NK landscapes. This separates ruggedness from neutrality.

**Ebner, M., Shackleton, M., & Shipman, R. (2001).** How neutral networks influence evolvability. *Complexity*, 7(2), 19–33. https://doi.org/10.1002/cplx.10021
- Verified: CR (S2 TLDR only).
- Shows that neutral networks in genotype space increase the interconnectivity of the search space and so influence evolvability. Evolvability here means the ability of random variation to sometimes produce improvement.

**Yu, T., & Miller, J. F. (2001).** Neutrality and the evolvability of Boolean function landscape. In *Genetic Programming: EuroGP 2001*, LNCS 2038, pp. 204–217. Springer. https://doi.org/10.1007/3-540-45355-5_16
- Verified: CR (title, authors, pages). The LNCS volume number is inferred from EuroGP 2001; confirm it if needed.
- Adds explicit neutrality to a Boolean-function evolution problem (Cartesian GP style) and reports that neutrality improved evolvability.

**Wagner, A. (2008).** Robustness and evolvability: A paradox resolved. *Proceedings of the Royal Society B*, 275(1630), 91–100. https://doi.org/10.1098/rspb.2007.1137
- Verified: CR + PM (PMID 17971325). Crossref "issued" is 2007 (online); the print issue is January 2008.
- Resolves the robustness vs evolvability tension in RNA. Genotype robustness is antagonistic to evolvability, but phenotype robustness promotes it, because populations spread along large neutral networks and reach more phenotypic variation.

**Weissman, D. B., Desai, M. M., Fisher, D. S., & Feldman, M. W. (2009).** The rate at which asexual populations cross fitness valleys. *Theoretical Population Biology*, 75(4), 286–300. https://doi.org/10.1016/j.tpb.2009.02.006
- Verified: CR + PM (PMID 19285994).
- A full theory of how fast asexual populations cross valleys or plateaus. Large populations can cross even wide valleys quickly when the intermediates are near-neutral. Below a threshold population size, valley crossing becomes rare.

**Wu, N. C., Dai, L., Olson, C. A., Lloyd-Smith, J. O., & Sun, R. (2016).** Adaptation in protein fitness landscapes is facilitated by indirect paths. *eLife*, 5, e16965. https://doi.org/10.7554/eLife.16965
- Verified: CR + PM (PMID 27391790). (Found via citation contexts of Conrad 1990.)
- An empirical map of 20⁴ = 160,000 GB1 variants. Reciprocal sign epistasis blocks many direct adaptive paths, but these traps are circumvented by **indirect paths that gain and later lose mutations**, i.e. by using extra sequence dimensions. **This is the cleanest empirical biological demonstration of extradimensional-bypass-like paths.**

**Papkou, A., Garcia-Pastor, L., Escudero, J. A., & Wagner, A. (2023).** A rugged yet easily navigable fitness landscape. *Science*, 382(6673), eadh3860. https://doi.org/10.1126/science.adh3860
- Verified: CR + S2 abstract; the citation context was obtained via S2.
- Measured more than 260,000 DHFR genotypes under trimethoprim. The landscape is highly rugged, with 514 peaks, yet its highest peaks are reachable through abundant fitness-increasing paths. According to the citation context, the authors report that extradimensional bypasses (indirect paths) do **not** play a major role in making peaks accessible in this landscape, because direct accessibility is already high. This is a useful caveat.

---

## UNVERIFIED / not found / corrections

- **"Bedau et al. 1998 'A comparison of evolutionary activity…' (ECAL 1997)":** the year is wrong in your candidate list. The proceedings paper is **1997** (ECAL97, pp. 125–134), verified as above. A 1998 SFI working paper version (98-03-024) exists, which is likely the source of "1998".
- **Rechtsteiner & Bedau 1999, content:** the record is verified, but the abstract was not accessible, so the summary is inferred from the title only.
- **Bedau, Snyder & Packard 1998, use of "shadow" runs:** the paper is verified, but I could not confirm from its text that it uses neutral shadow runs. Channon (2024) credits Bedau et al. (1997) with the first neutral shadow models. Cite the 1997 paper and/or Channon (2006, 2024) for the shadow method.
- **"Channon's shadow":** confirmed through Channon (2006, GPEM), which uses component-normalised activity against a neutral shadow, and Channon (2024, Artificial Life), which explicitly describes the random-selection shadow. Channon (2001) is verified but its abstract does not mention the shadow.
- **Any Avida or digital-organism experiment with explicit up/down/control selection lines and realised h²:** **none found.** Searches for "artificial selection" plus "Avida" / "digital organisms" / "realized heritability" / "divergent selection" returned nothing matching. The nearest are Williams & Lenton (2007), a simulated-ecosystem model with high/low/random lines and inferred heritability, and De Carlo et al. (2023), regression h² in evolving robots. Absence from searches is not proof of absence.
- **"Extra-dimensional bypass in EC by Lehman?":** no such paper found. Lehman's evolvability papers (2013, 2016) do not test the bypass.
- **Cheney & Lipson "Topological evolution for embodied cellular automata":** verified (TCS 2016) but it **does not test** the bypass.
- **Cheney et al. 2018 "referencing" Conrad or the bypass:** not confirmed. I did not find Conrad or bypass in its abstract and did not check its reference list.
- **Bongard 2011 PNAS as a bypass test:** it cites neither Conrad nor the bypass (full-text search), so do not describe it as a bypass test.
- **"Morphological bypass" as a term:** no papers found using it.
- **Conrad 1983 Springer eBook DOI:** not confirmed. Cite by ISBN and publisher.
- **Page and article numbers I did not verify:** Kriegman et al. 2018 article number (13934); the De Carlo et al. 2023 volume; Falconer & Mackay chapter or page for realised heritability; the ECAL 2001 volume editors.
- **Search-surfaced but not verified (possible leads):** Matsushita, Yokoi & Arai (2006), "Pseudo-passive dynamic walkers designed by coupled evolution of the controller and morphology", *Robotics and Autonomous Systems* 54, 674–685 (S2 record only, no abstract read). Paul (2005), "Sensorimotor control of biped locomotion", *Adaptive Behavior* (a citation context says morphology serves "as an extra-dimensional bypass… enabling faster convergence"; not read). Inden & Jost (2013, ECAL), which argues bypasses probably do not keep pace with search-space growth (context only).
- **Project-internal note (not prior art):** S2 lists "Rabbitstew: a Robot Simulator with Variable Morphologies" (E. G. Jucovy, 2005, Swarthmore CS97) as citing Bongard & Paul (2001) and Conrad. It is this project's own origin proposal (`/home/user/rabbitstew/docs/origins/jucovy-2005-rabbitstew-proposal.pdf`).

---

## (a) Prior art for a divergent-selection / realised-h² benchmark with drift controls in ALife/EC

The components of RBT-113 each have clear precedents, but I found no ALife or EC paper that puts them together. The breeder's equation and heritability were imported into EC by Mühlenbein & Schlierkamp-Voosen (1993a, 1993b), who used R = h²S and regression heritability to predict and control the Breeder GA. The biological template for up/down/control lines and realised heritability is Falconer & Mackay (1996) and Hill & Caballero (1992). Houle (1992) warns that h² alone is a poor measure of evolvability for fitness-like traits because of their high residual variance, so reporting mean-scaled response (CV_A-style) alongside h² is advisable. Hansen & Houle (2008) give the multivariate generalisation.

In ALife, the "is evolution doing work beyond drift" question is answered mainly by Bedau–Packard activity statistics normalised against a **neutral shadow**: a parallel copy of the system with random selection (Bedau & Packard 1992; Bedau et al. 1997; Bedau et al. 1998; Channon 2001, 2006, 2024). That is conceptually the same as RBT-113's neutral-drift control, but it measures component persistence, not trait response. MODES (Dolson et al. 2019) offers related change and novelty metrics.

The closest design match is Williams & Lenton (2007). They ran High, Low and Random-control artificial selection lines on an individual-based evolutionary simulation and inferred heritability from sustained divergence from the control, without estimating h² numerically. The closest robotics match is De Carlo et al. (2023), who estimated parent–offspring-regression h² of morphological and behavioural traits in co-evolving robots to compare encodings. Tarapore & Mouret (2015) likewise argue for evolvability benchmarks "beyond standard performance benchmarks".

Taken together, a benchmark that combines (i) replicated divergent up/down lines, (ii) realised h² from cumulative R/S, (iii) random-selection drift lines, and (iv) a comparison between two body classes (evolved vs designed) appears novel in ALife/EC as far as these searches reach. It can be framed as porting the Falconer/Hill–Caballero protocol into a domain where the drift control has so far been used mostly for activity statistics.

Two cautions from the literature. First, Lehman & Stanley (2013) show that evolvability-related properties can change under pure drift, so drift lines are a control for directional response, not a guarantee that "nothing happens". Second, Covert et al. (2013) show that counterfactual control arms in digital evolution can reveal non-obvious mechanisms, such as deleterious stepping stones.

## (b) Has the extradimensional bypass been tested in evolved robots, and what was found?

Conrad (1990; anticipated in Conrad 1979) proposed that adding dimensions (redundancy, weak interactions) turns isolated peaks into connected ridges. In robotics, the only direct test I found is **Bongard & Paul (2001)**. In a simulated 3D biped, adding three leg/waist radius genes to a 60-weight neural controller genome improved GA performance over control-only evolution (30 vs 30 runs). Evolved morphologies did not converge on a distinctive body, so the authors attributed the gain to bypasses, supported by one dissected mutational event. But adding eight mass-block genes gave **no** benefit (2 of 20 runs succeeded in both conditions). Their own conclusion is that only the "correct" morphological parameters help, and the bypass explanation was never tested with a formal landscape analysis.

Later robotics work does not test the bypass directly and partly cuts against it. Cheney et al. (2016) document premature morphological convergence, because body mutations break tuned controllers. Cheney et al. (2018) need "morphological innovation protection" to make co-optimisation scale. Bongard (2011) and Kriegman et al. (2018) show that morphological change or development over a lifetime can speed and guide evolution of control, but they frame this as scaffolding or development, not as Conrad's bypass. Bongard (2011) does not cite Conrad.

Outside robotics, the bypass idea has empirical support in protein landscapes: indirect paths circumvent sign-epistatic traps in GB1 (Wu et al. 2016). There is also strong theoretical support from high-dimensional holey or neutral-network landscapes (Gavrilets 1997; Gavrilets & Gravner 1997; Huynen et al. 1996; Wagner 2008; Ebner et al. 2001) and from valley-crossing theory and Avida experiments (Weissman et al. 2009; Covert et al. 2013). But Papkou et al. (2023) found that in a rugged DHFR landscape, peaks are reachable mostly by direct paths and bypasses are not a major factor.

**Bottom line:** in evolved robots, the extradimensional bypass has been tested once, directly, with mixed results: a gain for one parameter set and none for another. The later literature suggests that whether extra morphological dimensions help depends on how tightly body and controller are coupled and on how selection treats newly changed bodies.
