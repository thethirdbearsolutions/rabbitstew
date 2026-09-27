# Topic A: embodied evolution and open-ended evolution in ecologies

Verification sources: the Crossref REST API (api.crossref.org) was queried for each item and returned the DOI record with authors, title, venue, year, volume/pages. Abstracts come from the publisher (via the Crossref/OpenAlex abstract fields), HAL, the authors' lab pages or the PDF itself. "Verified" means the bibliographic fields below match a primary record. Summaries use only the abstract (or the full text where noted).

Checked 2026-09-27.

---

## 1. Embodied evolution: the origin papers

### Watson, Ficici & Pollack (1999), CEC
**Citation:** Watson, R. A., Ficici, S. G., & Pollack, J. B. (1999). Embodied evolution: Embodying an evolutionary algorithm in a population of robots. In *Proceedings of the 1999 Congress on Evolutionary Computation (CEC99)*, pp. 335–342. IEEE. https://doi.org/10.1109/CEC.1999.781944
**Records:** Crossref DOI record (it misspells the second author as "Ficiei" and has no year). The authors' lab page http://demo.cs.brandeis.edu/papers/author.html confirms 1999, the editors (Angeline, Michalewicz, Schoenauer, Yao, Zalzala) and pp. 335–342. Author PDF: http://www.demo.cs.brandeis.edu/papers/ee_cec99.pdf
**Summary:** This paper introduces Embodied Evolution (EE). The evolutionary algorithm is spread across a population of physical robots that reproduce with one another while they sit in the task environment. The authors present this as a way around the simulate-and-transfer problem, and as a way to cut evaluation time by running robots in parallel. With eight real robots, the evolved controllers compared well with hand-designed ones on "a simple task".

### Watson, Ficici & Pollack (2002), Robotics and Autonomous Systems
**Citation:** Watson, R. A., Ficici, S. G., & Pollack, J. B. (2002). Embodied Evolution: Distributing an evolutionary algorithm in a population of robots. *Robotics and Autonomous Systems*, 39(1), 1–18. https://doi.org/10.1016/S0921-8890(02)00170-7
**Records:** Crossref DOI record, plus the authors' lab page (http://demo.cs.brandeis.edu/papers/long.html#ee_journal). The lab page gives the abstract of the preprint, Brandeis Tech Report CS-00-208 (2000).
**NOTE:** The journal title is "**Distributing** an evolutionary algorithm…", not "Embodying…". Only the CEC 1999 paper uses "Embodying".
**Summary (from the TR abstract that the lab page gives for the journal version):** The evolutionary algorithm is fully decentralized and asynchronous. Robots broadcast mutated genes to nearby robots at a rate set by their own fitness, and they accept incoming genes with a probability that rises as their fitness falls (the Probabilistic Gene Transfer Algorithm). The authors argue this scales naturally to large numbers of robots and suits collective robotics and ALife. With eight robots, EE-evolved controllers beat a hand-designed controller. (Note: in this paper robots still compute a local, task-defined fitness/energy score. This is not fitness-free, ecological selection.)

### Ficici, Watson & Pollack (1999), EWLR
**Citation:** Ficici, S. G., Watson, R. A., & Pollack, J. B. (1999). Embodied evolution: A response to challenges in evolutionary robotics. In J. L. Wyatt & J. Demiris (Eds.), *Proceedings of the Eighth European Workshop on Learning Robots* (EWLR-8), pp. 14–22.
**Records:** No DOI exists. Verified from the authors' own publication list, which gives the full citation and abstract: http://demo.cs.brandeis.edu/papers/long.html#ewlr8 (PDF linked there as `ewlr8.pdf`).
**Summary:** This is the companion workshop paper that introduces EE as "a new methodology for conducting evolutionary robotics", using physical robots that evolve by reproducing with one another in the task environment. It frames EE as a response to problems the ER community had raised: transfer from simulation, evaluation time and scalability. It also reviews the first experimental results and discusses EE's advantages and limitations.

### Salmon (2003), Swarthmore CS81 project
**Citation:** Salmon, B. (2003, May 19). *Embodied evolution in a morphologically heterogeneous population of robots*. Course project paper, CS81 (Adaptive Robotics), Swarthmore College. https://www.cs.swarthmore.edu/~meeden/cs81/s03/projects/salmon.pdf
**Records:** Fetched and read in full (8 pp., 145 KB PDF, text extracted locally). The author's full name is **Branen Salmon**. There is no DOI; this is an unpublished student paper on the course site.
**Summary:** Salmon's abstract describes this as a *position paper about a work in progress*, not an experimental report: "This paper details the motivations behind an experimental work in progress." It argues for combining "holistic" evolution (co-evolving controller and morphology, citing Sims, Hornby & Pollack, and Bongard & Paul) with Watson/Ficici/Pollack-style embodied evolution (distributed, asynchronous gene transfer with no central evaluator). It claims three benefits for the combination. Stability should emerge by itself, because gene transfers are accepted only when fitness drops. Adaptation to environmental change should be fast. And incremental neuromorphological complexity should arise without hand-staged fitness functions. **No results are reported.** Cite it as a proposal or early articulation, not as evidence.

---

## 2. Environment-driven embodied evolution (Bredeche, Haasdijk, Eiben)

### Bredeche & Montanier (2010), PPSN XI
**Citation:** Bredeche, N., & Montanier, J.-M. (2010). Environment-driven embodied evolution in a population of autonomous agents. In *Parallel Problem Solving from Nature – PPSN XI*, LNCS 6239, pp. 290–299. Springer. https://doi.org/10.1007/978-3-642-15871-1_30
**Records:** Crossref DOI record (pp. 290–299). The HAL record, with abstract, is https://inria.hal.science/inria-00506771v1
**Summary:** This paper introduces mEDEA (minimal Environment-driven Distributed Evolutionary Adaptation). A fixed-size population of agents faces unknown and possibly changing environments. There is no task fitness. The algorithm has to cope with "the implicit fitness function hidden in the environment". Genomes spread by local broadcast, and the successful ones are those that get passed on the most. mEDEA is shown to adapt in unknown environments and to be robust to abrupt, possibly lethal changes.

### Bredeche, Montanier, Liu & Winfield (2012), MCMDS
**Citation:** Bredeche, N., Montanier, J.-M., Liu, W., & Winfield, A. F. T. (2012). Environment-driven distributed evolutionary adaptation in a population of autonomous robotic agents. *Mathematical and Computer Modelling of Dynamical Systems*, 18(1), 101–129. https://doi.org/10.1080/13873954.2011.601425
**Records:** Crossref DOI record (vol. 18, issue 1, pp. 101–129, Feb 2012; published online 2011).
**Summary:** This is the journal treatment of mEDEA. The algorithm copes with the environment's implicit fitness and is robust to abrupt, unforeseen changes. The paper studies how the population comes to agree on particular behavioural strategies, with attention to algorithmic stability. It also reports a real-world implementation on 20 e-puck robots.

### Haasdijk, Bredeche & Eiben (2014), PLoS ONE
**Citation:** Haasdijk, E., Bredeche, N., & Eiben, A. E. (2014). Combining environment-driven adaptation and task-driven optimisation in evolutionary robotics. *PLoS ONE*, 9(6), e98466. https://doi.org/10.1371/journal.pone.0098466
**Records:** Crossref DOI record, with the abstract from the publisher.
**Summary:** Embodied-evolution robots have to meet two sets of requirements: *viability*, meaning they keep operating in the environment, and *usefulness*, meaning they do the user's task. The proposed MONEE framework splits these across the two selection stages. Survivor selection is driven by the environment, and parent selection is driven by task performance. In swarms of 100 simulated e-pucks, MONEE promotes task-driven behaviour without hurting environmental adaptation. A "market mechanism" extension balances pressure across multiple tasks.

### Bredeche, Haasdijk & Prieto (2018), Frontiers review
**Citation:** Bredeche, N., Haasdijk, E., & Prieto, A. (2018). Embodied evolution in collective robotics: A review. *Frontiers in Robotics and AI*, 5, 12. https://doi.org/10.3389/frobt.2018.00012 (open access, also at PMC7806005)
**Records:** Crossref DOI record (vol. 5, article 12, 22 Feb 2018), with the abstract.
**Summary:** This review defines embodied evolution (online, distributed evolution within a robot collective) and describes its underlying concepts and mechanisms. It surveys the field from about 2000 onwards. It identifies a shift away from EE as a parallel search method in small groups (fewer than 10 robots) and towards EE as online distributed learning of collective behaviour in swarm-like groups. It closes with applications and open questions.

### Montanier, Carrignon & Bredeche (2016), Frontiers (added, relevant pitfall)
**Citation:** Montanier, J.-M., Carrignon, S., & Bredeche, N. (2016). Behavioral specialization in embodied evolutionary robotics: Why so difficult? *Frontiers in Robotics and AI*, 3, 38. https://doi.org/10.3389/frobt.2016.00038
**Records:** Crossref DOI record, with the abstract via OpenAlex.
**Summary:** The task is foraging with two limited resources. The paper shows that behavioural specialization (division of labour) is unlikely to evolve under embodied evolution in general. It needs very sparse communication between robots, and specialization into groups of similar size. Larger populations and selection schemes that favour exploration over exploitation also help. This explains why existing EE algorithms are limited at learning efficient division of labour.

### Eiben et al. (2013), Triangle of Life (ECAL 2013)
**Citation:** Eiben, A. E., Bredeche, N., Hoogendoorn, M., Stradner, J., Timmis, J., Tyrrell, A. M., & Winfield, A. (2013). The Triangle of Life: Evolving robots in real-time and real-space. In *Advances in Artificial Life, ECAL 2013*, pp. 1056–1063. MIT Press. https://doi.org/10.7551/978-0-262-31709-2-ch157
**Records:** Crossref DOI record (a duplicate DOI with a 10.1162 prefix also exists), with the abstract.
**Summary:** This paper proposes a generic conceptual framework for fully embodied evolution in which robots actually reproduce. The cycle is built around the conception of a new robot organism, followed by its development ("morphogenesis") and then its lifetime of operation, learning and mating. The framework is meant to be independent of hardware and reproduction mechanism, and to guide the evolution of morphology and controller in real time and real space. A SYMBRION modular-robot case study realises fragments of it.

---

## 3. Open-ended evolution: position papers and theory

### Taylor et al. (2016), Artificial Life 22(3)
**Citation:** Taylor, T., Bedau, M., Channon, A., Ackley, D., Banzhaf, W., Beslon, G., Dolson, E., Froese, T., Hickinbotham, S., Ikegami, T., McMullin, B., Packard, N., Rasmussen, S., Virgo, N., Agmon, E., Clark, E., McGregor, S., Ofria, C., Ropella, G., Spector, L., Stanley, K. O., Stanton, A., Timperley, C., Vostinar, A., & Wiser, M. (2016). Open-ended evolution: Perspectives from the OEE workshop in York. *Artificial Life*, 22(3), 408–423. https://doi.org/10.1162/ARTL_a_00210
**Records:** Crossref DOI record, with the abstract.
**Summary:** This paper reports on the first OEE workshop (ECAL 2015, York). It reaches two main conclusions. The first is *pluralism*: there is more than one interesting kind of OEE. The second is that observable *hallmarks* of OEE need to be kept apart from the hypothesised *mechanisms* that produce them. It lists the hallmarks and mechanisms that were discussed and the systems linked to each.

### Stanley, Lehman & Soros (2017), O'Reilly Radar
**Citation:** Stanley, K. O., Lehman, J., & Soros, L. (2017, December 19). Open-endedness: The last grand challenge you've never heard of. *O'Reilly Radar*. https://www.oreilly.com/radar/open-endedness-the-last-grand-challenge-youve-never-heard-of/
**Records:** Fetched from the publisher's page, which confirms the authors and the date. This is not peer-reviewed.
**Summary:** The essay argues that open-endedness, a process that keeps inventing new complexity indefinitely, is a grand challenge on the scale of AI, and that current algorithms quickly run out of novelty. It says open-ended systems must *expand the space of possibilities* rather than just search inside it. It repeats the Chromaria-style conditions: individuals must meet a minimal criterion before they reproduce, and new individuals must create new ways for others to meet that criterion (illustrated by giraffes and trees).

### Packard et al. (2019), Artificial Life 25(2)
**Citation:** Packard, N., Bedau, M. A., Channon, A., Ikegami, T., Rasmussen, S., Stanley, K. O., & Taylor, T. (2019). An overview of open-ended evolution: Editorial introduction to the Open-Ended Evolution II special issue. *Artificial Life*, 25(2), 93–103. https://doi.org/10.1162/artl_a_00291
**Records:** Crossref DOI record, with the abstract. (The companion OEE-I editorial is a different paper: *Artificial Life* 25(1), 1–3, doi:10.1162/artl_e_00282. Do not mix them up.)
**Summary:** This paper introduces the second of two special issues on OEE and open-endedness and gives an overview of the contents of both. Most of the work came from the OEE workshop at ALIFE 2018 (Tokyo) and the two earlier OEE workshops. It frames OEE as life's creative productivity, which evolution generates dynamically.

### Soros & Stanley (2014), Chromaria (ALIFE 14)
**Citation:** Soros, L. B., & Stanley, K. O. (2014). Identifying necessary conditions for open-ended evolution through the artificial life world of Chromaria. In *Artificial Life 14: Proceedings of the Fourteenth International Conference on the Synthesis and Simulation of Living Systems*, pp. 793–800. MIT Press. https://doi.org/10.7551/978-0-262-32621-6-ch128
**Records:** Crossref DOI record. The abstract was confirmed verbatim on the UCF STARS repository: https://stars.library.ucf.edu/scopus2010/9117/
**Summary:** The paper proposes four conditions that are necessary for open-ended evolution. (1) Individuals must meet a minimal criterion to reproduce. (2) Evolving individuals should create new opportunities to meet that criterion. (3) Individuals should decide for themselves how to interact with the world. (4) The representation should not cap phenotypic complexity. Chromaria is a world designed to test these conditions, and it stagnates when any one of them is removed.

### Brant & Stanley (2017), Minimal criterion coevolution (GECCO 2017)
**Citation:** Brant, J. C., & Stanley, K. O. (2017). Minimal criterion coevolution: A new approach to open-ended search. In *Proceedings of the Genetic and Evolutionary Computation Conference (GECCO '17)*, pp. 67–74. ACM. https://doi.org/10.1145/3071178.3071186
**Records:** Crossref DOI record (its title field reads only "Minimal criterion coevolution"; the full title is given in the ACM record), with the abstract.
**Summary:** In nature, divergence is driven by one constraint: survive long enough to reproduce. MCC copies this. Two populations, maze-navigating agents and mazes, coevolve, and each must meet a minimal criterion set by the other. There is no novelty metric and no archive. In a single run, MCC produces a wide range of maze topologies of growing complexity, together with successful solutions.

### Lehman & Stanley (2011a), Evolutionary Computation 19(2)
**Citation:** Lehman, J., & Stanley, K. O. (2011). Abandoning objectives: Evolution through the search for novelty alone. *Evolutionary Computation*, 19(2), 189–223. https://doi.org/10.1162/EVCO_a_00025
**Records:** Crossref DOI record, with the abstract.
**Summary:** Objective functions can be deceptive and steer search into dead ends. Novelty search rewards behavioural novelty only and ignores the objective. Because many genomes collapse onto the same behaviour, searching for novelty is feasible. In deceptive maze and biped tasks it beats objective-based search, and the paper offers it as a new view of open-endedness.

### Lehman & Stanley (2011b), GECCO 2011
**Citation:** Lehman, J., & Stanley, K. O. (2011). Evolving a diversity of virtual creatures through novelty search and local competition. In *Proceedings of the 13th Annual Conference on Genetic and Evolutionary Computation (GECCO '11)*, pp. 211–218. ACM. https://doi.org/10.1145/2001576.2001606
**Records:** Crossref DOI record, with the abstract.
**Summary:** In virtual worlds, evolving creatures "tend to converge to a single morphology because selection therein greedily rewards the morphology that is easiest to exploit". Novelty search with local competition (NSLC) pairs a morphological novelty objective with a reward for beating morphologically similar individuals. It finds more functional morphological diversity within one run than global competition does.

---

## 4. Artificial ecologies (re-confirmed)

### Ray (1991), Tierra
**Citation:** Ray, T. S. (1991). An approach to the synthesis of life. In C. G. Langton, C. Taylor, J. D. Farmer, & S. Rasmussen (Eds.), *Artificial Life II* (Santa Fe Institute Studies in the Sciences of Complexity, Vol. XI), pp. 371–408. Addison-Wesley.
**Records:** The author's own publication list, http://tomray.me/pubs/ (PDF: http://tomray.me/pubs/alife2/Ray1991AnApproachToTheSynthesisOfLife.pdf). There is no DOI.
**Summary:** This is the original Tierra paper. Self-replicating machine-code programs compete for CPU time and memory, and evolution arises by natural selection with no fitness function. Parasites, hyper-parasites and other ecological dynamics emerge. (Summary from general knowledge of the paper; only the record was fetched, not the PDF text.)

### Yaeger (1994), PolyWorld
**Citation:** Yaeger, L. S. (1994). Computational genetics, physiology, metabolism, neural systems, learning, vision, and behavior or PolyWorld: Life in a new context. In C. G. Langton (Ed.), *Artificial Life III* (SFI Studies in the Sciences of Complexity, Proc. Vol. XVII), pp. 263–298. Addison-Wesley.
**Records:** The author's PolyWorld page, https://shinyverse.org/larryy/Polyworld.html, gives the citation and pages. There is no DOI. (The "Proc. Vol. XVII" series number is the standard SFI numbering and was not shown on that page. Drop it if you want to stay strictly within the record.)
**Summary:** PolyWorld is a computational ecology. Organisms with genetically specified neural architectures and Hebbian learning perceive the world through vision, spend energy, eat, fight, mate and reproduce. Success depends on survival and reproduction in the world rather than on an explicit fitness function, although a fitness-driven GA can be switched on when the population is too small. Behaviours such as foraging and flocking emerge.

### Channon (2001), Geb
**Citation:** Channon, A. (2001). Passing the ALife test: Activity statistics classify evolution in Geb as unbounded. In J. Kelemen & P. Sosík (Eds.), *Advances in Artificial Life: ECAL 2001*, LNCS 2159, pp. 417–426. Springer. https://doi.org/10.1007/3-540-44811-X_45
**Records:** Crossref DOI record (pp. 417–426), plus the dblp record https://dblp.uni-trier.de/rec/conf/ecal/Channon01.html and the author PDF http://www.channon.net/alastair/geb/ecal2001/channon_ad_ecal2001.pdf. (The editors and LNCS volume number are standard for ECAL 2001 but were not shown in the Crossref fields that were checked. Confirm them before print.)
**Summary:** Bedau and Packard's evolutionary activity statistics are applied to Geb, an artificial world in which neural-network agents evolve under natural (biotic) selection with no fitness function. Geb shows unbounded evolutionary activity, making it the first autonomous artificial system to pass this "ALife test".
**Related (verified):** Channon, A. (2019). Maximum individual complexity is indefinitely scalable in Geb. *Artificial Life*, 25(2), 134–144. https://doi.org/10.1162/artl_a_00285. Maximum individual complexity is asymptotically bounded when either world size or neuron cap is scaled alone. It grows without bound only when both are scaled together, and even then only logarithmically.

### Spector, Klein & Feinstein (2007), Division Blocks
**Citation:** Spector, L., Klein, J., & Feinstein, M. (2007). Division blocks and the open-ended evolution of development, form, and behavior. In *Proceedings of the 9th Annual Conference on Genetic and Evolutionary Computation (GECCO '07)*, pp. 316–323. ACM. https://doi.org/10.1145/1276958.1277019
**Records:** Crossref DOI record, with the abstract.
**Summary:** Division Blocks are physically simulated 3D blocks that grow, shrink, divide, form joints, exert forces and exchange resources. They are controlled by recurrent neural networks that evolve by natural selection. Energy is approximately conserved and ultimately comes from a simulated sun through photosynthesis. Early runs reliably show cooperative resource transactions emerging.

### Miconi (2008), Evosphere
**Citation:** Miconi, T. (2008). Evosphere: Evolutionary dynamics in a population of fighting virtual creatures. In *2008 IEEE Congress on Evolutionary Computation (IEEE World Congress on Computational Intelligence)*, pp. 3066–3073. IEEE. https://doi.org/10.1109/CEC.2008.4631212
**Records:** Crossref DOI record, with the abstract.
**Summary:** The paper starts from the claim that evolution driven by an explicit fitness function is less creative than natural evolution, and proposes a classification of evolutionary systems by how creative they are. Evosphere is a "microplanet" on which a population of 3D physically simulated creatures interact, fight and evolve freely. The paper shows that natural selection and adaptive evolution set in. Reproductively isolated species enrich the dynamics and create simple inter-species feedbacks.

### Chaumont & Adami (2016), GPEM
**Citation:** Chaumont, N., & Adami, C. (2016). Evolution of sustained foraging in three-dimensional environments with physics. *Genetic Programming and Evolvable Machines*, 17(4), 359–390. https://doi.org/10.1007/s10710-016-9270-z
**Records:** Crossref DOI record, with the abstract.
**Summary:** The paper opens: "Artificially evolving foraging behavior in simulated articulated animals has proved to be a notoriously difficult task." Morphology and controller are co-evolved with an explicit, staged fitness function, and food placement is randomised gradually across generations. The best evolved foragers reach multiple food sources more than 90% of the time. An organism's efficiency at reaching the first food source does not predict how well it finds later ones. (Directly relevant to Rabbitstew. This paper needed explicit, staged fitness to get goal-directed foraging in 3D physics.)

### Utimula (2025), Artificial Life 31(1)
**Citation:** Utimula, K. (2025). Guideless artificial life model for reproduction, development, and interactions. *Artificial Life*, 31(1), 31–64. https://doi.org/10.1162/artl_a_00466
**Records:** Crossref DOI record (vol. 31, issue 1, pp. 31–64; Crossref's "issued" date is the online-first date in 2024, and the issue is Feb 2025), with the abstract. The issue page is https://direct.mit.edu/artl/issue/31/1
**Summary:** Tierra-like and cellular-automaton models capture reproduction and interaction but have little morphological or behavioural freedom. Sims-style creatures have that freedom but depend on predefined fitness. The proposed model puts Tierra and CA mechanisms inside cells that move freely in 3D, with "no predefined fitness function or form that qualifies as a living creature". It is a proof-of-concept of reproduction, development and interaction.

---

## 5. Physically embodied morphology evolution and environmental influence

### Auerbach & Bongard (2014), PLoS Comput Biol
**Citation:** Auerbach, J. E., & Bongard, J. C. (2014). Environmental influence on the evolution of morphological complexity in machines. *PLoS Computational Biology*, 10(1), e1003399. https://doi.org/10.1371/journal.pcbi.1003399
**Records:** Crossref DOI record, with the abstract.
**Summary:** Virtual organisms are evolved for locomotion, and their morphological complexity is measured with an information-theoretic metric. Selection for locomotion drives morphological complexity up beyond chance, so the trend is driven, not passive. When complexity carries a cost, more complex environments evolve more complex bodies than simple ones do. In some niches selection favours simpler body plans instead.

### Miras & Eiben (2019), GECCO 2019
**Citation:** Miras, K., & Eiben, A. E. (2019). Effects of environmental conditions on evolved robot morphologies and behavior. In *Proceedings of the Genetic and Evolutionary Computation Conference (GECCO '19)*, pp. 125–132. ACM. https://doi.org/10.1145/3321707.3321811
**Records:** Crossref DOI record, with the abstract.
**Summary:** Populations of modular robots are evolved in different environments and mapped into a space of morphological and behavioural descriptors. Surprisingly, environments that look quite different to humans can lead to the same regions of that space. The authors conclude that showing the environment's "firm impact" on evolved morphology is harder in evolutionary robotics than people usually assume.

### Lessin, Fussell & Miikkulainen (2013), GECCO 2013
**Citation:** Lessin, D., Fussell, D., & Miikkulainen, R. (2013). Open-ended behavioral complexity for evolved virtual creatures. In *Proceedings of the 15th Annual Conference on Genetic and Evolutionary Computation (GECCO '13)*, pp. 335–342. ACM. https://doi.org/10.1145/2463372.2463411
**Records:** Crossref DOI record, with the abstract (truncated in OpenAlex).
**Summary:** Nineteen years after Sims (1994), evolved virtual creatures had shown no clear increase in behavioural complexity beyond light-following. The paper sets out to break this ceiling by building up behaviour step by step: skills are evolved in isolation and then composed by human-designed syllabus. (Only the problem statement is in the retrieved abstract. The syllabus method is from general knowledge of the paper.)

### Stanton & Channon (2013), ECAL 2013
**Citation:** Stanton, A., & Channon, A. (2013). Heterogeneous complexification strategies robustly outperform homogeneous strategies for incremental evolution. In *Advances in Artificial Life, ECAL 2013*, pp. 973–980. MIT Press. https://doi.org/10.7551/978-0-262-31709-2-ch145
**Records:** Crossref DOI record, with the abstract.
**Summary:** The paper uses the term *environmental complexification* for increasing the difficulty of the problem domain. On a 3D agent obstacle task, "homogeneous" schedules (showing hard tasks directly, or ramping difficulty linearly) fail through loss of gradient or through temporally local over-fitting. "Heterogeneous" schedules that present many difficulties at once, including oscillating ones, outperform them on every metric.

### Stanton & Channon (2015), ECAL 2015
**Citation:** Stanton, A., & Channon, A. (2015). Incremental neuroevolution of reactive and deliberative 3D agents. In *Proceedings of the European Conference on Artificial Life (ECAL 2015)*, pp. 341–348. MIT Press. https://doi.org/10.7551/978-0-262-33027-5-ch063
**Records:** Crossref DOI record, with the abstract.
**Summary:** Fixed-morphology quadrupeds are evolved in 3D rigid-body physics. Locomotion is bootstrapped incrementally, and a tournament-based coevolutionary algorithm then solves progressively harder deliberative tasks. The agents show a range of intricate, lifelike behaviours used together. (Morphology is fixed and selection is tournament-based, so this is not an ecology.)

### Bibliographic record verified, not summarised (no abstract retrieved)
- Steyven, A., Hart, E., & Paechter, B. (2016). Understanding environmental influence in an open-ended evolutionary algorithm. In *PPSN XIV*, LNCS 9921, pp. 921–931. https://doi.org/10.1007/978-3-319-45823-6_86 (Crossref record. The LNCS volume number is from the PPSN XIV series and was not in the Crossref fields that were checked.)
- Ventrella, J. (1994). Explorations in the emergence of morphology and locomotion behavior in animated characters. In *Artificial Life IV*, pp. 432–437. MIT Press. https://doi.org/10.7551/mitpress/1428.003.0059 (Crossref record.)
- Ventrella, J. (1998). Designing emergence in animated artificial life worlds. In *Virtual Worlds* (LNCS), pp. 143–155. https://doi.org/10.1007/3-540-68686-X_14 (Crossref record. The LNCS volume was not confirmed.)

---

## UNVERIFIED / NOT INCLUDED

- **"Embodying an evolutionary algorithm…" as the 2002 RAS title**: this is wrong. The RAS 39(1) title is "Embodied Evolution: **Distributing** an evolutionary algorithm in a population of robots". The corrected version is verified above.
- **Stanley et al., "Evolving morphologies with CPPN-NEAT and ecological…"**: no such paper was found. Do not cite it.
- **"Evolving virtual creatures in open-ended environments"** (exact title): not searched to a primary record, and no match came up in the Crossref queries. Leave it out unless someone supplies an exact citation.
- **Nichele (physics-ecology morphology work)**: not searched to a primary record, because there was no specific paper to check. Unverified.
- **ALIEN (Artificial Life Environment)**: this is a software project, not a peer-reviewed paper. No citation was verified.
- **Lenia**: the record was found (Chan, B. W.-C. (2019). Lenia: Biology of artificial life. *Complex Systems*, 28(3), 251–286. https://doi.org/10.25088/ComplexSystems.28.3.251), but it is left out on relevance grounds. It is a continuous cellular automaton with no evolved embodied agents and no physics bodies.
- **Details not fully confirmed** (the rest of each citation is verified): Yaeger's SFI "Proc. Vol. XVII" series number; the ECAL 2001 editors and LNCS 2159 for Channon; the LNCS volume numbers for Steyven 2016 and Ventrella 1998. The DOI, pages and year are confirmed in each case.
- **Ray 1991 and Lessin 2013 summaries**: these partly rely on general knowledge beyond the retrieved text (flagged in each entry).

---

## What this literature says about the pitfalls of embodied and ecological evolution

This literature consistently finds that removing the explicit fitness function does not remove selection. Selection moves into the environment, where it is **implicit, weak and aimed at whatever keeps a lineage reproducing most cheaply**. That is often not what the designer had in mind. Bredeche and Montanier's mEDEA is built around "the implicit fitness function hidden in the environment". Its successful genomes are the ones that spread the most, which in practice means moving around and meeting other robots. Haasdijk, Bredeche and Eiben (2014) treat environment-driven *viability* and task-driven *usefulness* as separate requirements and wire them into different selection stages (MONEE), because environmental pressure alone does not reliably produce useful behaviour. Lehman and Stanley (2011b) note that creatures in virtual worlds converge because selection "greedily rewards the morphology that is easiest to exploit". Rabbitstew's "blind mower" result (covering ground beats perceiving) is a clear case of this greedy exploit. Where foraging reliably emerged in 3D physics, it needed an explicit, staged fitness function and food positions randomised gradually (Chaumont & Adami 2016, who call the task "notoriously difficult"). Stanton and Channon (2013) show that *how* environmental difficulty is scheduled matters: ramping it or jumping straight to hard tasks loses the gradient. Montanier et al. (2016) show that even behavioural specialization is unlikely to emerge under embodied evolution without specific interaction structure.

On what makes such worlds produce complexity, the OEE literature suggests the fix is in the world's structure, not in adding back an objective. Soros and Stanley (2014) and Brant and Stanley (2017) argue for a *minimal criterion* for reproduction together with a world in which organisms create new opportunities for one another, meaning other agents are part of the environment. They also call for agents that decide their own interactions and a representation that does not cap complexity. Worlds lacking any one of these stagnate. Auerbach and Bongard (2014) find that the environment decides whether complexity pays: complex environments select for complex bodies only when complexity has a cost, and simple ones select for simplicity. Miras and Eiben (2019) warn that environments humans see as different may not differ in their selective effect. Channon (2019) shows that even an open-ended ecology like Geb grows maximum complexity only logarithmically, and only when population size and the neural cap are scaled together. Taylor et al. (2016) caution against confusing observable hallmarks of open-endedness with the mechanisms behind them.

The implication for Rabbitstew: if perception is to evolve, the world has to make perception pay more than covering ground does. Possible ways to do that are patchy or moving food, food that runs out, or other agents (predators, competitors, mates) whose positions matter. Alternatively, a task-driven parent-selection channel could be added alongside environment-driven survival, in the style of MONEE.
