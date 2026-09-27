# Body–brain (morphology–control) co-evolution after Sims (1994): verified citations

Verification date: 2026-09-27. "Verified" means a real record (DOI/publisher page, proceedings page, arXiv, PubMed/PMC, dblp, or author publication page) was loaded or returned in search results, and authors/year/title/venue were confirmed from it. Page numbers and DOIs are given only where seen on a record. Summaries are based on the abstract or the equivalent the record showed; where I only saw a search-result summary of the abstract, I say so.

Key: **[CMP]** = the paper runs an explicit comparison between an evolved/co-optimised body and a fixed body (or the reverse: a fixed controller), which is the question this review cares about.

---

## A. Foundations (1994–2006)

### 1. Sims, K. (1994a). Evolving virtual creatures. *Proceedings of SIGGRAPH '94 (21st Annual Conference on Computer Graphics and Interactive Techniques)*, pp. 15–22. ACM. DOI: 10.1145/192161.192167
- Record: https://dl.acm.org/doi/10.1145/192161.192167 (also GP bibliography: https://gpbib.cs.ucl.ac.uk/gp-html/Sims_1994_evc.html)
- Verified via: ACM DL record and GP-bib entry in search results (title, venue, pages, DOI).
- Summary: A genetic algorithm generates both the morphology of 3D virtual creatures (blocks joined in a physics simulation) and the neural circuitry that drives their muscle forces. Both are encoded with one directed-graph genetic language. Different fitness functions produced swimming, walking, jumping and light-following. This is the canonical demonstration of evolving body and brain together. It does not compare against a fixed body.

### 2. Sims, K. (1994b). Evolving 3D morphology and behavior by competition. *Artificial Life*, 1(4), 353–372. DOI: 10.1162/artl.1994.1.4.353
- Records: https://direct.mit.edu/artl/article-abstract/1/4/353/2234/ ; dblp https://dblp.org/rec/journals/alife/Sims94.html ; author PDF https://www.karlsims.com/papers/alife94.pdf. The same work also appears as a chapter in *Artificial Life IV* (MIT Press, 1994): https://direct.mit.edu/books/edited-volume/4681/chapter-abstract/214598/
- Verified via: MIT Press journal page and dblp in search results.
- Summary: Creatures compete one-on-one for control of a shared resource in a physically simulated world, and winners receive higher fitness. Morphology and the neural controller are both genetically determined, so they "adapt to each other as they evolve simultaneously." The paper reports co-evolutionary arms races between strategies. There is no fixed-body comparison.

### 3. Lipson, H. & Pollack, J. B. (2000). Automatic design and manufacture of robotic lifeforms. *Nature*, 406, 974–978. DOI: 10.1038/35023115
- Records: https://www.nature.com/articles/35023115 ; PubMed https://pubmed.ncbi.nlm.nih.gov/10984047/
- Verified via: Nature and PubMed records in search results.
- Summary: Simple electromechanical machines (bars, linear actuators, artificial neurons) were evolved in simulation for locomotion. The fittest designs were then fabricated automatically with rapid-prototyping technology and worked in reality. This is the first body+brain evolution to be carried through to physical robots with minimal human intervention. There is no fixed-body baseline.

### 4. Pollack, J. B., Lipson, H., Hornby, G. S. & Funes, P. (2001). Three generations of automatically designed robots. *Artificial Life*, 7(3), 215–223. DOI: 10.1162/106454601753238627
- Records: https://direct.mit.edu/artl/article/7/3/215/2377/ ; PubMed https://pubmed.ncbi.nlm.nih.gov/11712955/ ; ACM https://dl.acm.org/doi/10.1162/106454601753238627
- Verified via: MIT Press, PubMed and ACM records in search results.
- Summary: A position and review paper arguing that robot morphology and controller should evolve at the same time. It covers three generations of the group's work: evolved static structures (LEGO), evolved and automatically manufactured dynamic machines (the GOLEM project), and modular robots designed through a generative, DNA-like encoding.

### 5. Hornby, G. S. & Pollack, J. B. (2001). Body-brain co-evolution using L-systems as a generative encoding. *Proceedings of the Genetic and Evolutionary Computation Conference (GECCO-2001)*, pp. 868–875.
- Records: Semantic Scholar https://www.semanticscholar.org/paper/c4c7028456bd69353f96bbe9826fd1b256950394 ; BibSonomy https://www.bibsonomy.org/publication/13c52c45d51ce394928109759f82dcd9
- Verified via: bibliographic records in search results (authors, title, venue, pages). I did not load the publisher page.
- Summary: Body and controller are co-evolved using one L-system as a common generative encoding. This links the controller genotype to the body parts it controls. The resulting creatures have an order of magnitude more parts, and more regularity, than earlier evolved creatures.

### 6. Hornby, G. S. & Pollack, J. B. (2002). Creating high-level components with a generative representation for body-brain evolution. *Artificial Life*, 8(3), 223–246.
- Records: https://direct.mit.edu/artl/article-abstract/8/3/223/2398/ ; PubMed https://pubmed.ncbi.nlm.nih.gov/12537684/ ; IEEE Xplore https://ieeexplore.ieee.org/document/6791131/
- Verified via: MIT Press and PubMed records in search results.
- Summary: Defines "generative representations," which reuse genotype elements during development, and introduces GENRE, a system that evolves morphology and neural controller together. On a locomotion task, GENRE is compared against a non-generative (direct) encoding. The generative representation produced robots of significantly higher fitness, faster. The comparison is between encodings, not between evolved and fixed bodies.

### 7. Paul, C. & Bongard, J. C. (2001). The road less travelled: morphology in the optimization of biped robot locomotion. *Proceedings of the IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS 2001)*, vol. 1, pp. 226–232.
- Record: IEEE Xplore https://ieeexplore.ieee.org/document/973363/ (seen in search results); ResearchGate entry.
- Verified via: IEEE Xplore document page in search results. The DOI was not seen.
- Summary (from the search-result description; I did not read the full abstract): A 5-link simulated biped's recurrent neural controller was optimised together with morphological parameters (mass distribution) by a genetic algorithm. Secondary sources summarise the result as indicating that controller and morphology should be co-evolved to get fitter walkers. **[CMP, partial]** Treat any stronger claim, such as a formal fixed-body baseline, as needing a check of the full text.

### 8. Pfeifer, R. & Bongard, J. (2006). *How the Body Shapes the Way We Think: A New View of Intelligence*. Cambridge, MA: MIT Press.
- Records: https://direct.mit.edu/books/book/2035/ ; https://mitpress.mit.edu/9780262537421/how-the-body-shapes-the-way-we-think/
- Verified via: MIT Press book pages in search results.
- Summary: A book, not an experiment. It argues that cognition is constrained and enabled by embodiment (morphology and materials), under the heading "understanding by building." It provides the theoretical basis, including morphological computation and body–brain coupling, that later co-optimisation papers cite when they argue for designing the body and the brain together.

---

## B. Bongard / Cheney / Lipson line (2010–2025)

### 9. Auerbach, J. E. & Bongard, J. C. (2010). Evolving CPPNs to grow three-dimensional physical structures. *Proceedings of GECCO 2010* (Portland, OR). DOI: 10.1145/1830483.1830597
- Records: ACM https://dl.acm.org/doi/10.1145/1830483.1830597 ; author PDF via CORE https://files.core.ac.uk/download/pdf/148000424.pdf
- Verified via: ACM DL record in search results. Pages were not seen.
- Summary: Uses CPPN-NEAT as a generative encoding to grow 3D physical structures that capture the close relationship between function and form. It extends earlier CPPN work in which robot morphology and control were evolved together.

### 10. Auerbach, J. E. & Bongard, J. C. (2012). On the relationship between environmental and morphological complexity in evolved robots. *Proceedings of GECCO 2012*, pp. 521–528.
- Records: dblp https://dblp.org/rec/conf/gecco/AuerbachB12.html ; ResearchGate entry.
- Verified via: dblp record in search results.
- Summary: Tests the hypothesis that a robot's body and brain should scale with the complexity of its task environment, a relationship the authors note was less understood than the control–morphology link. It is a precursor to item 11.

### 11. Auerbach, J. E. & Bongard, J. C. (2014). Environmental influence on the evolution of morphological complexity in machines. *PLoS Computational Biology*, 10(1), e1003399. DOI: 10.1371/journal.pcbi.1003399
- Records: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003399 ; PMC https://ncbi.nlm.nih.gov/pmc/articles/PMC3879106
- Verified via: PLOS and PMC records in search results.
- Summary: Combines a method for evolving virtual organisms (body and control) with an information-theoretic measure of morphological complexity. Selection for locomotion drove morphological complexity to increase beyond chance, which the authors read as a driven rather than passive trend. When complexity carried a cost, more complex environments produced more complex bodies.

### 12. Bongard, J. (2011). Morphological change in machines accelerates the evolution of robust behavior. *PNAS*, 108(4), 1234–1239. DOI: 10.1073/pnas.1015390108 **[CMP]**
- Records: https://www.pnas.org/doi/10.1073/pnas.1015390108 ; PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC3029735/ (loaded)
- Verified via: PMC full-text page (loaded).
- Summary: Controllers for phototaxis were evolved on simulated quadrupeds and hexapods under five regimes. The key control condition was a **fixed (upright, legged) morphology**. The main treatment was a body plan that changed from anguilliform (legless) to legged, both within a lifetime and over evolutionary time. Robots whose morphology changed found successful gaits significantly faster (for hexapods, in all five task environments). Their final controllers were also more robust to perturbation than those evolved on the fixed body. This is the clearest early controlled comparison of changing versus fixed bodies. Note that the body change is a scheduled developmental trajectory, not open-ended morphological search.

### 13. Lehman, J. & Stanley, K. O. (2011). Evolving a diversity of virtual creatures through novelty search and local competition. *Proceedings of GECCO '11*, pp. 211–218. DOI: 10.1145/2001576.2001606
- Record: ACM https://dl.acm.org/doi/10.1145/2001576.2001606
- Verified via: ACM DL record in search results.
- Summary: Body+brain creature evolution tends to converge on one morphology because selection greedily rewards whichever body is easiest to exploit. Novelty search combined with local competition, as a multi-objective search, yielded a wide diversity of well-adapted creatures within a single run. This is an early diagnosis of the morphological premature-convergence problem.

### 14. Cheney, N., MacCurdy, R., Clune, J. & Lipson, H. (2013). Unshackling evolution: evolving soft robots with multiple materials and a powerful generative encoding. *Proceedings of GECCO '13* (Amsterdam). DOI: 10.1145/2463372.2463404
- Records: ACM https://dl.acm.org/doi/pdf/10.1145/2463372.2463404 ; Dryad data record https://datadryad.org/dataset/doi:10.5061/dryad.m3s84 (loaded) ; author PDF https://jeffclune.com/publications/2013_Softbots_GECCO.pdf
- Verified via: Dryad record (loaded), which gives the article citation and DOI, plus the ACM entry in search results. Pages were not seen.
- Summary: The authors argue that evolved morphologies hit a "complexity ceiling" because they were built from rigid primitives. They evolve voxel-based soft robots from multiple materials using a CPPN generative encoding. CPPNs evolved faster robots than a direct encoding and produced more natural-looking morphologies. Adding materials improved performance, and different cost functions raised complexity without hurting locomotion. (Actuation here is a global phase-offset pattern, not a separately learned controller.)

### 15. Bongard, J. C., Bernatskiy, A., Livingston, K., Livingston, N., et al. (2015). Evolving robot morphology facilitates the evolution of neural modularity and evolvability. *Proceedings of GECCO 2015* (Madrid). DOI: 10.1145/2739480.2754750 **[CMP]**
- Records: ResearchGate https://www.researchgate.net/publication/289455529 ; author PDF https://meclab.w3.uvm.edu/papers/2015_GECCO_Bongard.pdf (downloaded but not text-extractable in my environment)
- Verified via: DOI, title and the first four authors as returned in search results (ResearchGate/academia.edu). The full author list was not confirmed, so this item is cited as "et al."
- Summary (from the abstract text returned in search): Simulated robot arms (two- versus three-fingered grippers) were evolved to move objects onto ledges, **with morphology co-evolved versus held fixed**. Modular controllers evolved only when (1) morphology co-evolved with control, (2) fitness selected for the behaviour, and (3) fitness also selected for conservative, robust behaviour. Robots with evolved morphology showed significantly better grasping, higher neural modularity and more behavioural conservatism than fixed-morphology robots.

### 16. Cheney, N., Bongard, J., SunSpiral, V. & Lipson, H. (2016). On the difficulty of co-optimizing morphology and control in evolved virtual creatures. *Proceedings of ALIFE 2016 (Fifteenth International Conference on the Synthesis and Simulation of Living Systems)*, pp. 226–233. MIT Press. DOI: 10.1162/978-0-262-33936-0-ch042
- Records: https://direct.mit.edu/isal/proceedings/alif2016/28/226/99427 ; PDF https://direct.mit.edu/isal/proceedings-pdf/alif2016/28/226/2325909/978-0-262-33936-0-ch042.pdf
- Verified via: MIT Press proceedings page in search results (the page returned 403 to direct fetch). Pages and DOI are from the search record.
- Summary: Argues that the evolved-virtual-creatures field has stagnated in complexity since Sims. It proposes a fundamental cause rooted in embodied cognition: morphological mutations disrupt behaviour more than controller mutations do. It reproduces the finding that morphology converges prematurely, relative to when controllers converge, under simultaneous optimisation.

### 17. Cheney, N., Bongard, J., SunSpiral, V. & Lipson, H. (2018). Scalable co-optimization of morphology and control in embodied machines. *Journal of the Royal Society Interface*, 15(143), 20170937. DOI: 10.1098/rsif.2017.0937
- Records: https://royalsocietypublishing.org/rsif/article/15/143/20170937/35866/ ; arXiv https://arxiv.org/abs/1706.06133 (loaded)
- Verified via: arXiv abstract page (loaded) and the Royal Society record in search results (volume, issue, article number, DOI).
- Summary: Starts from the observation that in AI and robotics the body plan is "usually designed by hand, and control policies are then optimized for that fixed design," whereas biology co-evolves them. The paper introduces **morphological innovation protection**, which temporarily reduces selection pressure on individuals whose morphology has just changed so the controller can re-adapt. This avoids morphological premature convergence and reaches similar high-fitness bodies from widely varying starts. Per the paper, the standard greedy method reached roughly 21.7 voxels travelled versus about 32.0 with protection. It also found an asymmetry: protecting body innovations helps, protecting brain innovations does not. **Caveat:** I could not confirm from the abstract or accessible text that this paper includes a fixed, hand-designed-morphology baseline. Its comparison is co-optimisation with versus without protection.

### 18. Kriegman, S., Cheney, N. & Bongard, J. (2018). How morphological development can guide evolution. *Scientific Reports*, 8, 13934. DOI: 10.1038/s41598-018-31868-7
- Records: https://www.nature.com/articles/s41598-018-31868-7 ; PubMed https://pubmed.ncbi.nlm.nih.gov/30224743/ ; arXiv https://arxiv.org/abs/1711.07387 (loaded)
- Verified via: arXiv abstract (loaded) and the Nature/PubMed records in search results.
- Summary: When body and control co-evolve with morphological development, evolution favours body plans that are robust to controller changes. These bodies become genetically assimilated while controllers keep evolving, a process the authors call "differential canalization" (a refinement of the Baldwin effect). The authors suggest such bodies may also transfer better from simulation to reality.

### 19. Bernatskiy, A. & Bongard, J. (2018). Evolving morphology automatically reformulates the problem of designing modular control. *Adaptive Behavior*, 26(2), 47–64. DOI: 10.1177/1059712318762807
- Records: SAGE https://journals.sagepub.com/doi/10.1177/1059712318762807 ; ACM https://dl.acm.org/doi/10.1177/1059712318762807 ; APA PsycNet record.
- Verified via: SAGE/ACM records in search results (the SAGE page returned 403 to direct fetch). Volume, issue and pages are from the search-result citation.
- Summary: Some design (morphological) variables determine whether the control task on the remaining variables is inherently modular. Evolutionary search can find modularity-inducing morphologies and so make the later search for modular, high-fitness controllers easier. In short, evolving the body can make the brain problem easier.

### 20. Powers, J., Grindle, R., Kriegman, S., Frati, L., Cheney, N. & Bongard, J. (2020). Morphology dictates learnability in neural controllers. *Proceedings of ALIFE 2020*, pp. 52–59. DOI: 10.1162/isal_a_00243 **[CMP, morphology-variant]**
- Records: https://direct.mit.edu/isal/proceedings/isal2020/32/52/98460 ; arXiv https://arxiv.org/pdf/1910.07487
- Verified via: MIT Press proceedings record in search results.
- Summary: Shows that a morphological design choice, sensor placement, reshapes the controller's loss landscape. It can expand or shrink the weight regions that solve each task, which changes how much catastrophic forgetting occurs across tasks. The evidence is that the body, not only the learning algorithm, determines how learnable a controller is.

### 21. Mertan, A. & Cheney, N. (2024). Investigating premature convergence in co-optimization of morphology and control in evolved virtual soft robots. In *Genetic Programming: EuroGP 2024*, LNCS 14631, pp. 38–55. Springer. DOI: 10.1007/978-3-031-56957-9_3 **[CMP, reverse direction]**
- Records: Springer https://link.springer.com/chapter/10.1007/978-3-031-56957-9_3 ; arXiv https://arxiv.org/abs/2402.09231 and HTML (loaded)
- Verified via: arXiv abstract and HTML (loaded), plus the Springer record in search results.
- Summary: Compares brain-body co-optimisation (learnable, sensory-feedback controllers) with morphology-only evolution under a **fixed open-loop controller**, across two morphology spaces and two environments. Fixed-controller runs found significantly better solutions (all P<0.005) and converged faster. Bodies found with fixed controllers, once re-paired with newly optimised learnable controllers, beat co-optimised solutions in 3 of 4 settings. High-performing regions of morphology space therefore exist but are not found during co-optimisation.

### 22. Mertan, A. & Cheney, N. (2025). Evolutionary brain-body co-optimization consistently fails to select for morphological potential. arXiv:2508.17464 (v1 24 Aug 2025; v2 12 Aug 2026). **[CMP]**
- Record: https://arxiv.org/abs/2508.17464 and HTML https://arxiv.org/html/2508.17464 (both loaded)
- Verified via: arXiv abstract and HTML (loaded). No peer-reviewed venue was seen, so cite as a preprint.
- Summary: The authors map the full morphology–fitness landscape by training controllers for all 1,305,840 voxel robots in a design space. Evolutionary co-optimisation does not consistently find near-optimal bodies; it undervalues newly mutated bodies and discards promising morphologies that are one mutation from better ones. Co-optimisation does produce useful goal-switching: for 2 of the 5 best morphologies, optimising a controller from scratch **on the fixed body** under a matched budget was very unlikely (<0.01) to match the controller found by co-optimisation. There is no comparison against a hand-designed body.

---

## C. Eiben group and real-world evolution

### 23. Eiben, A. E., Bredeche, N., Hoogendoorn, M., Stradner, J., Timmis, J., Tyrrell, A. M. & Winfield, A. (2013). The Triangle of Life: evolving robots in real-time and real-space. *Proceedings of ECAL 2013 (12th European Conference on the Synthesis and Simulation of Living Systems)*, pp. 1056–1063. MIT Press.
- Records: VU Amsterdam https://research.vu.nl/en/publications/the-triangle-of-life-evolving-robots-in-real-time-and-real-space/ ; author PDF https://www.cs.vu.nl/~gusz/papers/2013-Eiben-etal-Triangle-of-Life.pdf
- Verified via: VU research-portal record in search results.
- Summary: A conceptual framework for systems in which physical robots reproduce, with a cycle of birth (morphogenesis), infancy (learning a controller for the new body) and mature life (reproduction). The infant-learning stage is the group's answer to the body–brain mismatch in offspring.

### 24. Eiben, A. E. & Smith, J. (2015). From evolutionary computation to the evolution of things. *Nature*, 521, 476–482. DOI: 10.1038/nature14544
- Records: https://www.nature.com/articles/nature14544 ; PubMed https://pubmed.ncbi.nlm.nih.gov/26017447/
- Verified via: Nature/PubMed records in search results.
- Summary: A review arguing that evolutionary computation is entering a phase of evolution in physical hardware ("the Evolution of Things"), including robots whose bodies and brains evolve. It is a perspective piece with no experiments.

### 25. Jelisavcic, M., Glette, K., Haasdijk, E. & Eiben, A. E. (2019). Lamarckian evolution of simulated modular robots. *Frontiers in Robotics and AI*, 6:9. DOI: 10.3389/frobt.2019.00009
- Record: PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC7805734/ (loaded)
- Verified via: PMC page (loaded).
- Summary: In body+brain evolution each newborn needs a learning period to fit its controller to its new body. Letting offspring inherit parents' learned controllers (Lamarckian inheritance, using a CPPN-parameterised CPG controller that transfers across bodies) gave clear performance gains, especially under tight learning budgets. The benefit correlated with parent–offspring morphological similarity, and the controller regime changed which bodies evolved.

### 26. Miras, K., De Carlo, M., Akhatou, S. & Eiben, A. E. (2020). Evolving-controllers versus learning-controllers for morphologically evolvable robots. In *Applications of Evolutionary Computation (EvoApplications 2020)*, LNCS 12104, pp. 86–99. Springer. DOI: 10.1007/978-3-030-43722-0_6
- Record: VU research portal https://research.vu.nl/en/publications/evolving-controllers-versus-learning-controllers-for-morphologica/ (loaded)
- Verified via: VU record (loaded).
- Summary: With bodies evolving, the paper compares controllers that are only inherited and evolved against inherited controllers refined by lifetime learning. Learning gave different fitness levels and also different, larger bodies, so changes to the brain regime feed back into body evolution.

### 27. Luo, J., Stuurman, A. C., Tomczak, J. M., Ellers, J. & Eiben, A. E. (2022). The effects of learning in morphologically evolving robot systems. *Frontiers in Robotics and AI*, 9, 797393. DOI: 10.3389/frobt.2022.797393
- Records: PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC9197197/ (loaded) ; arXiv https://arxiv.org/abs/2111.09851
- Verified via: PMC page (loaded).
- Summary: Evolution plus infant learning (Triangle of Life) greatly increased task performance and reduced generations to a fitness level, compared with evolution alone, for modular robots doing targeted locomotion. Evolved morphologies differed even though learning acted only on the controller. The "learning delta" grew over generations, indicating that learnability itself was selected for.

### 28. Nygaard, T. F., Samuelsen, E. & Glette, K. (2017). Overcoming initial convergence in multi-objective evolution of robot control and morphology using a two-phase approach. In *Applications of Evolutionary Computation (EvoApplications 2017)*, LNCS 10199, pp. 825–836. Springer. DOI: 10.1007/978-3-319-55849-3_53
- Records: Springer https://link.springer.com/chapter/10.1007/978-3-319-55849-3_53 ; Glette publication list https://www.mn.uio.no/ifi/english/people/aca/kyrrehg/publications/ (loaded)
- Verified via: the author's publication list (loaded) and the Springer record in search results.
- Summary (from the abstract text returned in search): Co-evolving morphology and control enlarges and roughens the search space, which often causes early convergence on sub-optimal body–controller pairs. The proposed two-phase method first evolves morphology and controller freely, then locks the morphology and re-evolves only the controller.

### 29. Nygaard, T. F., Martin, C. P., Samuelsen, E., Torresen, J. & Glette, K. (2018). Real-world evolution adapts robot morphology and control to hardware limitations. *Proceedings of GECCO 2018*, pp. 125–132. ACM. DOI: 10.1145/3205455.3205567
- Records: Glette publication list (loaded) ; arXiv https://arxiv.org/abs/1805.03388 (loaded) ; ACM https://dl.acm.org/doi/10.1145/3205455.3205567
- Verified via: arXiv abstract (loaded) and the author list (loaded).
- Summary: Multi-objective evolution of both control and morphology (leg lengths) on a physical quadruped, with evaluations in the real world. Real-world co-optimisation proved feasible with relatively few evaluations. When hardware was constrained by lowering supply voltage, evolution adapted both body and control and kept comparable performance at low and moderate speeds. The abstract does not report a control-only comparison.

### 30. Nygaard, T. F., Martin, C. P., Howard, D., Torresen, J. & Glette, K. (2021). Environmental adaptation of robot morphology and control through real-world evolution. *Evolutionary Computation* (MIT Press). DOI: 10.1162/evco_a_00291
- Records: arXiv https://arxiv.org/abs/2003.13254 (loaded) ; author page https://www.mn.uio.no/ifi/english/people/aca/kyrrehg/publications/nygaard-ecj2021-abstract.html (loaded) ; PubMed https://pubmed.ncbi.nlm.nih.gov/34623424/
- Verified via: arXiv abstract and author page (loaded). Volume and issue were not seen on a record.
- Summary: Control and body of a self-reconfiguring quadruped were co-optimised entirely in the real world across different surfaces. This found diverse, high-performing morphology–controller pairs specialised to each surface, and solutions transferred to unseen terrains. **Correction to the brief:** this is the *Evolutionary Computation* paper; the *Nature Machine Intelligence* paper is item 31.

### 31. Nygaard, T. F., Martin, C. P., Torresen, J., Glette, K. & Howard, D. (2021). Real-world embodied AI through a morphologically adaptive quadruped robot. *Nature Machine Intelligence*, 3(5), 410–419. DOI: 10.1038/s42256-021-00320-3 **[CMP]**
- Records: https://www.nature.com/articles/s42256-021-00320-3 ; author page https://www.mn.uio.no/ifi/english/people/aca/kyrrehg/publications/nygaard-nmi2021-abstract.html (loaded; citation only)
- Verified via: the author publication list (loaded) and the Nature and ANU records in search results.
- Summary: Robots "are traditionally bound by a fixed morphology... limited to adapting only their control strategies." A quadruped that can change its leg lengths in the field, driven by an algorithm that switches to the most energy-efficient body for the sensed terrain, showed substantial improvements over a **non-adaptive (fixed-morphology)** approach outdoors. This is a real-world comparison of an adaptive body against a fixed one. The adaptive body is chosen from a pre-learned model rather than co-evolved online.

---

## D. ML co-design / brain–body co-optimisation (2019–2022)

### 32. Ha, D. (2019). Reinforcement learning for improving agent design. *Artificial Life*, 25(4), 352–365. DOI: 10.1162/artl_a_00301 **[CMP: direct hand-designed-body baseline]**
- Records: https://direct.mit.edu/artl/article/25/4/352/93262/ ; arXiv https://arxiv.org/abs/1810.03779 (loaded) ; project page https://designrl.github.io/ (loaded)
- Verified via: arXiv abstract and project page (loaded), plus the MIT Press record in search results.
- Summary: Body parameters (leg lengths and widths) of OpenAI Gym agents are learned jointly with the policy and compared directly with the **original hand-designed body trained with the same method**. On BipedalWalker the learned body scored 359 against 347 for the fixed body. On BipedalWalkerHardcore it scored 335 ± 37 against 313 ± 53, and solved the task in about 12 h (under 1,400 generations) rather than about 40 h (4,600 generations). With a reward for less material, the agent kept high scores using only 8% of the original leg area on the easy task (27% on the hard task). This is the cleanest published side-by-side comparison against a hand-designed body, though it covers parametric body variation only (topology is fixed).

### 33. Wang, T., Zhou, Y., Fidler, S. & Ba, J. (2019). Neural Graph Evolution: towards efficient automatic robot design. *ICLR 2019*. arXiv:1906.05370
- Records: arXiv https://arxiv.org/abs/1906.05370 (loaded) ; OpenReview PDF https://openreview.net/pdf/7d15fa3b496856b30bd4fb1cfe3ae4f4ccba6d01.pdf
- Verified via: arXiv abstract (loaded; lists ICLR 2019).
- Summary: Evolutionary search over robot graph structures, with graph neural network policies whose skills pass from parent to child designs to cut evaluation cost, plus uncertainty-aware mutation. It discovered plausible bodies such as a fish with side-fins and tail and a cheetah-like runner, within a day on one 64-core machine. The abstract does not state a fixed-body baseline.

### 34. Pathak, D., Lu, C., Darrell, T., Isola, P. & Efros, A. A. (2019). Learning to control self-assembling morphologies: a study of generalization via modularity. *Advances in Neural Information Processing Systems 32 (NeurIPS 2019)*. arXiv:1902.05546 **[CMP vs static]**
- Record: https://proceedings.neurips.cc/paper/2019/hash/c26820b8a4c1b3c2aa868d6d57e14a79-Abstract.html (loaded)
- Verified via: NeurIPS proceedings page (loaded).
- Summary: Primitive limb agents learn to link into composite bodies and to coordinate control, with a policy architecture that mirrors the emergent body. Compared with static and monolithic baselines, the self-assembling agents generalised better to test-time changes in environment and body structure.

### 35. Schaff, C., Yunis, D., Chakrabarti, A. & Walter, M. R. (2019). Jointly learning to construct and control agents using deep reinforcement learning. *2019 International Conference on Robotics and Automation (ICRA)*. DOI: 10.1109/ICRA.2019.8793537
- Records: ACM/IEEE https://dl.acm.org/doi/abs/10.1109/ICRA.2019.8793537 ; arXiv https://arxiv.org/abs/1801.01432 (loaded)
- Verified via: arXiv abstract (loaded) and the DOI record in search results. Pages were not seen.
- Summary: Keeps a distribution over designs and trains one design-conditioned RL policy, shifting the distribution toward better designs until design and policy converge together. On legged locomotion it found novel designs and gaits, "outperforming baselines in both performance and efficiency." The abstract does not specify whether the baselines include the fixed hand-designed body.

### 36. Luck, K. S., Ben Amor, H. & Calandra, R. (2019). Data-efficient co-adaptation of morphology and behaviour with deep reinforcement learning. *Conference on Robot Learning (CoRL 2019)*, PMLR vol. 100.
- Records: PMLR https://proceedings.mlr.press/v100/luck20a.html ; ML Anthology https://mlanthology.org/corl/2019/luck2019corl-dataefficient/
- Verified via: PMLR/ML Anthology records in search results. Pages were not seen.
- Summary (from the abstract text returned in search): Uses soft actor-critic to co-adapt a robot's morphology and controller efficiently. Previously tested bodies and behaviours are reused to estimate how well new candidate morphologies will perform.

### 37. Zhao, A., Xu, J., Konaković-Luković, M., Hughes, J., Spielberg, A., Rus, D. & Matusik, W. (2020). RoboGrammar: graph grammar for terrain-optimized robot design. *ACM Transactions on Graphics*, 39(6) (SIGGRAPH Asia 2020). DOI: 10.1145/3414685.3417831
- Record: ACM https://dl.acm.org/doi/10.1145/3414685.3417831 ; MIT DSpace entry.
- Verified via: ACM DL record in search results.
- Summary: A graph grammar of physically realisable robot assemblies can express hundreds of thousands of designs. Graph Heuristic Search, which learns to predict the best reachable performance of partial designs, finds robots optimised for given terrains, with a controller optimised for each candidate design.

### 38. Gupta, A., Savarese, S., Ganguli, S. & Fei-Fei, L. (2021). Embodied intelligence via learning and evolution. *Nature Communications*, 12, 5721. DOI: 10.1038/s41467-021-25874-z
- Records: https://www.nature.com/articles/s41467-021-25874-z ; arXiv https://arxiv.org/abs/2102.02202 (loaded) ; EconPapers record (vol. 12, DOI)
- Verified via: arXiv abstract (loaded) and the Nature/EconPapers records in search results.
- Summary: DERL (deep evolutionary reinforcement learning) evolves morphologies in the UNIMAL space, with each body learning its controller by RL from low-level sensing. Complex environments evolved bodies that learn new tasks faster. Evolution rapidly selected bodies that learn faster, so behaviours learned late in ancestors appear early in descendants, a "morphological Baldwin effect." The selected bodies were more physically stable and energy efficient. No comparison against a hand-designed body appears in the abstract.

### 39. Bhatia, J., Jackson, H., Tian, Y., Xu, J. & Matusik, W. (2021). Evolution Gym: a large-scale benchmark for evolving soft robots. *Advances in Neural Information Processing Systems 34 (NeurIPS 2021)*. **[CMP vs hand-designed]**
- Record: https://proceedings.neurips.cc/paper/2021/hash/118921efba23fc329e6560b27861f0c2-Abstract.html (loaded)
- Verified via: NeurIPS proceedings page (loaded; full abstract).
- Summary: The first large benchmark for co-optimising design and control of voxel soft robots (32 locomotion and manipulation tasks), with baselines that combine design optimisation (GA, Bayesian optimisation, CPPN-NEAT) and deep RL (PPO). Robots evolved from scratch "often grow to resemble existing natural creatures while outperforming hand-designed robots." All tested algorithms failed on the hardest tasks.

### 40. Yuan, Y., Song, Y., Luo, Z., Sun, W. & Kitani, K. (2022). Transform2Act: learning a transform-and-control policy for efficient agent design. *ICLR 2022* (oral). arXiv:2110.03659
- Records: arXiv https://arxiv.org/abs/2110.03659 (loaded) ; ICLR https://iclr.cc/virtual/2022/oral/6197
- Verified via: arXiv abstract (loaded).
- Summary: A single conditional policy first takes "transform" actions that edit the skeleton and joint attributes, then control actions on the new body, using a graph-based policy with message passing so it handles variable numbers of joints. Joint optimisation with experience shared across designs beat prior co-design methods in speed and final performance, and discovered giraffe-, squid- and spider-like designs.

---

## E. Other relevant items

### 41. Stensby, E. H., Ellefsen, K. O. & Glette, K. (2021). Co-optimising robot morphology and controller in a simulated open-ended environment. In *Applications of Evolutionary Computation (EvoApplications 2021)*, LNCS 12694, pp. 34–49. Springer. DOI: 10.1007/978-3-030-72699-7_3
- Records: Springer https://link.springer.com/chapter/10.1007/978-3-030-72699-7_3 ; arXiv https://arxiv.org/abs/2104.03062 (loaded)
- Verified via: arXiv abstract (loaded) and the Springer record in search results.
- Summary: Uses POET to evolve environments open-endedly as an indirect way to counter premature morphological convergence in co-optimisation. Agent populations co-optimised in POET-generated environments showed more morphological diversity than those in hand-crafted environment curricula, with good quality. The comparison is between environments, not bodies.

### 42. Joachimczak, M., Suzuki, R. & Arita, T. (2016). Artificial metamorphosis: evolutionary design of transforming, soft-bodied robots. *Artificial Life*, 22(3), 271–298.
- Record: MIT Press https://direct.mit.edu/artl/article/22/3/271/2848/
- Verified via: MIT Press record in search results.
- Summary: Soft-bodied animats develop from a single cell by a developmental model. They evolve a larval form for one environment (aquatic) and then metamorphose, adding or removing cells and modifying the controller, into an adult form for a second environment (terrestrial). This shows body+brain co-design across a within-life body transformation.

---

## UNVERIFIED / NOT CONFIRMED

- **Cheney et al. 2018 "fixed-morphology baseline"**: the brief says this paper has one. I could not confirm it from the abstract, the Royal Society page (403) or the arXiv PDF (not extractable here). What I did confirm is a comparison of co-optimisation with versus without morphological innovation protection (and controller protection). Check the full text before citing a fixed-body baseline.
- **Bongard et al. 2015 (GECCO) full author list and page numbers**: only Bongard, Bernatskiy, K. Livingston and N. Livingston were confirmed, plus the DOI. Search snippets suggested "Long" and "Smith" as further authors but the record did not confirm them, so cite as "et al." until checked against ACM.
- **Paul & Bongard 2001**: the IEEE Xplore page was confirmed but I did not read the abstract text. The claim that it shows co-evolution beats a fixed body rests on secondary descriptions. The DOI was not seen.
- **Page numbers not seen** (do not add): Auerbach & Bongard 2010; Cheney et al. 2013; Schaff et al. 2019; Luck et al. 2019; Pathak et al. 2019; Wang et al. 2019; Nygaard et al. 2021 (*Evolutionary Computation* volume and issue).
- **Search results mentioning an unnamed study** ("co-evolving condition vs a fixed condition where morphological characteristics were hand-designed... co-evolved condition significantly better"): these came from a search-engine summary with no identifiable record. I could not trace it to a specific paper, so it is not cited. It may correspond to Bongard et al. 2015 (item 15) or to the survey arXiv:1702.02934, but this is unconfirmed.
- **Not searched / not verified in this pass**: Jelisavcic et al. 2017 real-world evolution of robot morphologies; Lan et al. (Eiben group); the Eiben-group ARE / "robot baby" papers; Eiben-group "morphological intelligence" papers; Stanton & Channon; Hupkes et al. (Revolve).
- **Soft yet effective robots via holistic co-design** (Stölzle, Pagliarani, Stella, Hughes, Laschi, Rus, Cianchetti, Della Santina, Zardini, arXiv:2505.03761, April 2025): arXiv record loaded. It is a **perspective paper with no fixed-vs-co-design experiment**, so it is noted here rather than cited as evidence.

---

## Has anyone run the side-by-side "holistic vs conventional" comparison properly, and what did they find?

**Partly, in narrow settings. No study found here runs the full comparison at scale with open-ended body topology.** The cleanest head-to-head against a genuinely hand-designed body is **Ha (2019)**. The same RL/ES pipeline was run on the stock BipedalWalker body and on a jointly learned body. The learned body scored modestly higher (359 vs 347; 335 vs 313 on Hardcore) and solved Hardcore about 3× faster. However, only leg dimensions varied, not topology. **Bhatia et al. (2021, Evolution Gym)** report co-evolved soft robots "outperforming hand-designed robots" across a benchmark suite, though as a benchmark observation rather than a controlled study. **Bongard (2011)** and **Bongard et al. (2015)** ran controlled evolved-vs-fixed body treatments. Changing or evolved bodies produced faster acquisition, more robust behaviour, and more modular, conservative controllers than fixed bodies. **Nygaard et al. (2021, *Nature Machine Intelligence*)** showed a real-world morphologically adaptive quadruped beating a non-adaptive (fixed-body) configuration on energy efficiency across terrains.

The more recent, careful work by the co-optimisation community complicates the picture:
- Joint body+brain search is hard. Bodies converge prematurely (**Cheney et al. 2016, 2018**; **Nygaard et al. 2017**; **Stensby et al. 2021**).
- Holding the controller fixed can find better bodies than co-optimisation does (**Mertan & Cheney 2024**).
- Exhaustive landscape mapping shows co-optimisation reliably misses the best morphologies. Yet for some bodies it produces controllers that controller-only optimisation on that fixed body cannot match (**Mertan & Cheney 2025**).

On the evidence verified here, co-design reliably matches or beats a fixed body when the body space is small or parametric (Ha; Bongard 2011; Nygaard 2021 NMI). In open-ended topology spaces, the potential advantage is real but current algorithms waste much of it. Remedies include innovation protection, learning or Lamarckian inheritance (**Cheney 2018**; **Jelisavcic 2019**; **Luo 2022**), and environment curricula. A properly controlled comparison against strong, expert hand-designed bodies with matched compute across multiple tasks does not appear in the verified set.
