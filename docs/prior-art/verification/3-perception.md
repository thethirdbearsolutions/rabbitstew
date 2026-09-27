# 3. Evolution of perception and chemotaxis in evolved agents

Verification method: each VERIFIED item was matched against a registry record: Crossref DOI metadata, which gives authors, year, title, venue, volume and pages. Abstracts come from OpenAlex, PubMed or Semantic Scholar, whichever returned one for that DOI. Summaries are grounded in those abstracts. Where no abstract could be retrieved, the entry says so, and the summary stays at the level of what the record confirms. Page numbers are given only where the registry record supplied them.

---

## VERIFIED

### Foundations: Braitenberg vehicles and evolved dynamical agents

**Braitenberg, V. (1984). *Vehicles: Experiments in Synthetic Psychology*. Cambridge, MA: MIT Press (Bradford Books). x + 152 pp. ISBN 0-262-02208-7.**
- Link: https://openlibrary.org/isbn/0262022087 (paperback reissue ISBN 0-262-52112-1: https://mitpress.mit.edu/9780262521123/vehicles/)
- How verified: Open Library record built from Library of Congress MARC data: title, author Valentino Braitenberg, MIT Press, Cambridge MA, 1984, LC class QP356 .B74 1984.
- Summary: This is a book of thought experiments that builds a series of hypothetical vehicles of increasing complexity. It starts with direct, crossed or uncrossed sensor-to-motor wiring, which produces approach and avoidance of a stimulus source. It is the origin of the "two-sensor compass" design: with two laterally placed sensors and crossed or uncrossed excitatory links, the vehicle steers up or down a gradient. With one sensor it can only speed up or slow down, not steer. (There is no formal abstract. The description follows the MIT Press and Open Library descriptions of the book's content.)

**Beer, R. D., & Gallagher, J. C. (1992). Evolving dynamical neural networks for adaptive behavior. *Adaptive Behavior*, 1(1), 91–122.**
- DOI: https://doi.org/10.1177/105971239200100105
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: The paper shows that continuous-time recurrent neural networks (CTRNNs) evolved with a genetic algorithm can serve as agent controllers. The authors stress that only an overall performance measure has to be specified, not the motor trajectories. The evolved controllers include a **chemotaxis controller that switches between different strategies depending on environmental conditions**, and a locomotion controller that uses sensory feedback when it is available but still works without it. This is an early demonstration that evolution finds chemotaxis when fitness directly rewards reaching a chemical source.

**Beer, R. D. (1996). Toward the evolution of dynamical neural networks for minimally cognitive behavior. In P. Maes et al. (Eds.), *From Animals to Animats 4: Proceedings of the 4th International Conference on Simulation of Adaptive Behavior* (pp. 421–429). MIT Press.**
- DOI: https://doi.org/10.7551/mitpress/3118.003.0051 (also IEEE Xplore: https://ieeexplore.ieee.org/document/6291905)
- How verified: Crossref record (container "From Animals to Animats 4", 1996, pp. 421–429). Abstract via OpenAlex.
- Summary: The paper proposes studying "minimally cognitive behavior" in simple model agents. It sketches an agent with a ray-based visual sensor array. Preliminary experiments evolve dynamical neural networks for visually guided orientation, object discrimination, and accurate pointing at objects in the field of view.

**Beer, R. D. (2003). The dynamics of active categorical perception in an evolved model agent. *Adaptive Behavior*, 11(4), 209–243.**
- DOI: https://doi.org/10.1177/1059712303114001
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: A CTRNN "nervous system" is evolved with a GA so that the agent catches circles and avoids diamonds. The best agent is analysed at three levels: the coupled brain/body/environment system, the agent–environment interaction, and the neuronal properties. A key point is that perception here is *active*: the agent's own scanning movements generate the sensory differences it categorizes. The paper argues that this challenges traditional notions of representation.

### Evolved chemotaxis and klinotaxis

**Izquierdo, E. J., & Lockery, S. R. (2010). Evolution and analysis of minimal neural circuits for klinotaxis in *Caenorhabditis elegans*. *Journal of Neuroscience*, 30(39), 12908–12917.**
- DOI: https://doi.org/10.1523/JNEUROSCI.2606-10.2010 (open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC3422662)
- How verified: Crossref record. Abstract via Semantic Scholar/OpenAlex.
- Summary: An evolutionary algorithm generated neural networks that perform klinotaxis, in which heading tracks the line of steepest ascent of a chemical gradient during sinusoidal locomotion. Inputs and outputs were constrained to match the worm's klinotaxis network. A minimal circuit of an ON-OFF pair of chemosensory neurons plus a pair of neck motor neurons was sufficient for realistic klinotaxis. Dynamical analysis of 77 evolved networks revealed a novel orientation mechanism. This matters for the project because klinotaxis needs only **one** sensor: the undulating body samples the gradient over time, so no two-sensor spatial comparison is required.

**Izquierdo, E. J., & Beer, R. D. (2013). Connecting a connectome to behavior: An ensemble of neuroanatomical models of *C. elegans* klinotaxis. *PLoS Computational Biology*, 9(2), e1002890.**
- DOI: https://doi.org/10.1371/journal.pcbi.1002890 (PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3567170)
- How verified: Crossref record. Abstract via Semantic Scholar/OpenAlex.
- Summary: The authors extract a minimal salt-klinotaxis circuit from the *C. elegans* connectome, running from chemosensory neurons to neck motor neurons. An evolutionary algorithm fits the unknown electrophysiological parameters so that the model reproduces the animal's behaviour. Multiple runs produce an ensemble of distinct circuits that all perform klinotaxis. The paper analyses the best mechanism and proposes experiments to discriminate between the alternatives.

**Goldstein, R. A., & Soyer, O. S. (2008). Evolution of taxis responses in virtual bacteria: Non-adaptive dynamics. *PLoS Computational Biology*, 4(5), e1000084.**
- DOI: https://doi.org/10.1371/journal.pcbi.1000084
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: Virtual bacteria with mutable biochemical pathways evolve taxis in a virtual environment. Selection favours cells that localize to favourable conditions. Under most conditions, "non-adaptive" dynamics evolve, in which tumbling probability is coupled directly to increasing stimulus. The E. coli-style adaptive dynamics evolve only when there is **stimulus scarcity and fluctuations** during evolution. Effective taxis can be mediated by as few as two components. The environment's statistics, not only the task, determine which sensing machinery evolves.

### Sensor and morphology co-evolution

**Cliff, D., Husbands, P., & Harvey, I. (1993). Explorations in evolutionary robotics. *Adaptive Behavior*, 2(1), 73–110.**
- DOI: https://doi.org/10.1177/105971239300200104 (Crossref lists the author order as Cliff, Husbands, Harvey)
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: This is the methodological manifesto of the Sussex group: evolve noise-tolerant, recurrent dynamical neural networks incrementally, mostly in simulation. Preliminary experiments evolve visually guided robots. Notably, **"robust visually guided control systems evolve from evaluation functions that do not explicitly require monitoring visual input."** Vision evolved because the task, getting to the centre of a room, could not be done well without it, not because fitness rewarded looking.

**Harvey, I., Husbands, P., & Cliff, D. (1994). Seeing the light: Artificial evolution, real vision. In D. Cliff et al. (Eds.), *From Animals to Animats 3: Proceedings of the 3rd International Conference on Simulation of Adaptive Behavior* (pp. 392–401). MIT Press.**
- DOI: https://doi.org/10.7551/mitpress/3117.003.0058
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: This paper uses a specialised gantry robot with a real camera, so control is evolved in the real world. **Dynamical recurrent networks and visual sampling morphologies, meaning which pixels or receptive fields the robot samples, are evolved concurrently** for simple visually guided tasks. Some evolved controllers generalised to harder versions of the task. It is a direct precedent for co-evolving sensor placement with the controller.

**Balakrishnan, K., & Honavar, V. (2001). Evolving neuro-controllers and sensors for artificial agents. In M. Patel, V. Honavar, & K. Balakrishnan (Eds.), *Advances in the Evolutionary Synthesis of Intelligent Agents* (pp. 109–152). MIT Press.**
- DOI: https://doi.org/10.7551/mitpress/1129.003.0007
- How verified: Crossref record for the chapter (authors, title, pages 109–152) and for the book (editors Patel, Honavar, Balakrishnan; 2001). No abstract was available from Crossref, OpenAlex or Semantic Scholar.
- Summary (limited): This is a book chapter on the joint evolution of neurocontrollers **and sensors** (sensor configuration) for artificial agents. It is the consolidated version of the authors' 1996 work. I could not retrieve an abstract, so the specific results are unconfirmed. Cite it for the fact that sensors and controllers were co-evolved, not for particular findings.

**Balakrishnan, K., & Honavar, V. G. (1996). Experiments in evolutionary synthesis of robotic neurocontrollers. In *Proceedings of the Thirteenth National Conference on Artificial Intelligence (AAAI-96)*, p. 1378 (student abstract).**
- Links: https://cdn.aaai.org/AAAI/1996/AAAI96-229.pdf ; https://mlanthology.org/aaai/1996/balakrishnan1996aaai-experiments/
- How verified: The PDF is hosted on the AAAI proceedings CDN, and ML Anthology gives authors, title, AAAI 1996, and page 1378. The PDF is a scanned image, and I could not extract its text.
- Summary (limited): This is a one-page AAAI-96 abstract on evolutionary synthesis of neurocontrollers for a robot. Search-engine snippets describe a box-pushing, arena-clearing task, but I could not read that in the document itself. Treat the content as unconfirmed.

**Liese, A., Polani, D., & Uthmann, T. (2001). A study of the simulated evolution of the spectral sensitivity of visual agent receptors. *Artificial Life*, 7(2), 99–124.**
- DOI: https://doi.org/10.1162/106454601753138961
- How verified: Crossref record. Abstract via OpenAlex. This is the real record for the prompt's garbled "Liese, Polani, Uthmann 2001 ... simultaneous evolution of morphology and control". That title does not exist; see UNVERIFIED.
- Summary: A GA co-evolves the **spectral sensitivity of agents' visual receptors** together with their control, in a continuous virtual world. The GA finds a balance between **sensor cost and task performance**. Evolved sensitivities come to match the emission spectrum of target objects, and the ability to evolve sensors significantly helps agents adapt to their task. The paper shows sensors being tuned to exactly the signal that pays, under an explicit cost.

**Dautenhahn, K., Polani, D., & Uthmann, T. (2001). Guest editors' introduction: Special issue on sensor evolution. *Artificial Life*, 7(2), 95–97.**
- DOI: https://doi.org/10.1162/106454601753138952
- How verified: Crossref record. No abstract, since it is an editorial.
- Summary: This is the editorial introducing the *Artificial Life* special issue devoted to sensor evolution. It is useful as an entry point to that literature, and it contains the Liese et al. paper above.

**Gupta, A., Savarese, S., Ganguli, S., & Fei-Fei, L. (2021). Embodied intelligence via learning and evolution. *Nature Communications*, 12(1). (Article number not confirmed; cite by DOI.)**
- DOI: https://doi.org/10.1038/s41467-021-25874-z (arXiv: https://arxiv.org/abs/2102.02202)
- How verified: Crossref record (vol. 12, issue 1). Abstract via Semantic Scholar/OpenAlex.
- Summary: DERL evolves agent morphologies whose controllers are learned by RL, across locomotion and manipulation tasks in increasingly complex terrains. The authors report three results: **environmental complexity fosters "morphological intelligence"**, meaning bodies that make new tasks easier to learn; there is a morphological Baldwin effect; and evolution selects more stable, energy-efficient bodies. It is relevant as evidence that the *world*, not just the task, shapes what evolved bodies carry. Note that DERL morphologies are mainly about limbs, not sensors.

**Tiwary, K., Young, A., Tasneem, Z., Klinghoffer, T., Dave, A., Poggio, T., Nilsson, D.-E., Cheung, B., & Raskar, R. (2025). What if eye...? Computationally recreating vision evolution. *Science Advances*, 11(51).**
- DOI: https://doi.org/10.1126/sciadv.ady2888 (preprint: https://arxiv.org/abs/2501.15001)
- How verified: Crossref record (Science Advances, 2025-12-19, vol. 11, issue 51). Abstract via Semantic Scholar/OpenAlex. Crossref gives no article number, and I have not invented one.
- Summary: Eyes and behaviours are co-evolved in embodied RL agents. The paper reports that **task-specific selection drives bifurcation in eye evolution**, with different tasks yielding different eye types. It also finds that optical innovations such as lenses emerge to resolve the trade-off between light collection and spatial precision, and that scaling laws link visual acuity to neural processing. It is the most direct modern example of perception evolving from scratch because the task demanded it.

**Klyubin, A. S., Polani, D., & Nehaniv, C. L. (2004). Organization of the information flow in the perception-action loop of evolved agents. In *Proceedings of the 2004 NASA/DoD Conference on Evolvable Hardware* (pp. 177–180). IEEE.**
- DOI: https://doi.org/10.1109/EH.2004.1310828 (author copy: https://uhra.herts.ac.uk/id/eprint/13231/1/101988.pdf)
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: Finite-state-automaton controllers are evolved for an information-acquisition task in a simple world. The authors then use information theory to analyse how evolution organizes sensory acquisition, memory, processing and action. Evolved schemes are compared with ideal extraction under the Information Bottleneck principle. The paper frames sensor evolution as selection for acquiring the information that is *relevant to action*.

**Klyubin, A. S., Polani, D., & Nehaniv, C. L. (2005). Empowerment: A universal agent-centric measure of control. In *2005 IEEE Congress on Evolutionary Computation* (Vol. 1, pp. 128–135).**
- DOI: https://doi.org/10.1109/CEC.2005.1554676
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: This paper defines empowerment as the information-theoretic channel capacity from an agent's actuators to its own future sensor states, proposed as a task-independent utility. Two simple experiments show that **empowerment can drive sensor–actuator evolution**. This is relevant as a candidate intrinsic incentive for sensing when the extrinsic reward (food yield) does not reward it.

### Navigation, homing, and ER methodology

**Dale, K., & Collett, T. S. (2001). Using artificial evolution and selection to model insect navigation. *Current Biology*, 11(17), 1305–1316.**
- DOI: https://doi.org/10.1016/S0960-9822(01)00418-3 ; PubMed PMID 11553323
- How verified: Crossref and PubMed records. Abstract via PubMed.
- Summary: Neural controllers are evolved for simulated "animats" with thrust and torque motors, a compass, and visual sensors. Selection rewards precision in reaching a goal defined by a visual landmark. Animats that could move sideways converged on strategies like those of bees and wasps: aim at the landmark, then hold a fixed body orientation and keep the landmark at a fixed retinal position. The authors conclude that insect strategies are adaptations to the demands of the task, not artefacts of evolutionary history. Here the sensors were *given*, and evolution discovered how to use them.

**Floreano, D., & Mondada, F. (1996). Evolution of homing navigation in a real mobile robot. *IEEE Transactions on Systems, Man, and Cybernetics, Part B*, 26(3), 396–407.**
- DOI: https://doi.org/10.1109/3477.499791 (author copy: http://infoscience.epfl.ch/record/63879)
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: A discrete-time recurrent network is evolved entirely on a physical Khepera robot. The result is a set of behaviours for locating a battery charger and periodically returning to it. Homing emerged when design constraints from an earlier experiment were lifted. It relies on an internal, not pre-designed, topographic map that picks a trajectory based on location and remaining energy. The **energy/recharge ecology** is what made sensing the charger and navigating to it pay.

**Floreano, D., & Mondada, F. (1994). Automatic creation of an autonomous agent: Genetic evolution of a neural-network driven robot. In *From Animals to Animats 3* (pp. 421–430). MIT Press.**
- DOI: https://doi.org/10.7551/mitpress/3117.003.0061
- How verified: Crossref record (authors, title, container, 1994, pp. 421–430). No abstract was retrievable.
- Summary (limited): This is the SAB-94 paper on evolving a neural controller directly on a real robot, the preliminary experiment that the 1996 paper builds on. I did not retrieve an abstract, so cite it for priority rather than for specific results.

**Nolfi, S., & Floreano, D. (2000). *Evolutionary Robotics: The Biology, Intelligence, and Technology of Self-Organizing Machines*. Cambridge, MA: MIT Press.**
- DOI: https://doi.org/10.7551/mitpress/2889.001.0001
- How verified: Crossref monograph record (Nolfi, Floreano, MIT Press, 2000-11-06). Book description via OpenAlex.
- Summary: This is the standard textbook of ER. It presents a sequence of empirical experiments of increasing complexity: robots with genetically specified controllers "move, look around, manipulate" and are selected on task performance. Topics include the co-evolution of body and brain. Its descriptive blurb does not itemize chapters, so check specific chapter claims about sensor evolution against the book itself.

**Nolfi, S. (1997). Evolving non-trivial behaviors on real robots: A garbage collecting robot. *Robotics and Autonomous Systems*, 187–198 (volume/issue not returned by Crossref; cite by DOI).**
- DOI: https://doi.org/10.1016/S0921-8890(97)00038-9
- How verified: Crossref record (authors, title, journal, 1997, pp. 187–198). Crossref did not return volume and issue in my query. Volume 22(3–4) is not confirmed, so cite it by DOI. No abstract is available. The Semantic Scholar machine-generated TLDR says the method "canalizes" evolution toward a non-trivial behaviour sequence.
- Summary (limited): A Khepera with a gripper is evolved to find "garbage" objects, pick them up and carry them out of an arena. This is the garbage-collecting task the prompt refers to. Verify details against the paper before citing specifics.

**Nelson, A. L., Barlow, G. J., & Doitsidis, L. (2009). Fitness functions in evolutionary robotics: A survey and analysis. *Robotics and Autonomous Systems*, 57(4), 345–370.**
- DOI: https://doi.org/10.1016/j.robot.2008.09.009
- How verified: Crossref record. No abstract was accessible because it is elided by the publisher. Summary based on the Semantic Scholar TLDR.
- Summary: This is a survey of ER research organized by how much a-priori task knowledge the fitness function encodes, from behavioural and tailored functions to "aggregate" functions that reward only task completion. The authors want to identify methods that yield the most novel control with the least designer knowledge. This is the standard reference for the tension between sparse, aggregate fitness, which leads to bootstrap problems, and shaped fitness, which injects the designer's answer.

**Mouret, J.-B., & Doncieux, S. (2009). Overcoming the bootstrap problem in evolutionary robotics using behavioral diversity. In *2009 IEEE Congress on Evolutionary Computation* (pp. 1161–1168).**
- DOI: https://doi.org/10.1109/CEC.2009.4983077 (open access: https://hal.science/hal-00473147)
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: The paper defines the bootstrap problem: if the whole initial population performs equally poorly, there is no fitness gradient. It proposes **behavioural diversity**, a behaviour-space distance used as an extra objective in multi-objective optimization, to keep exploring until some individual gets non-minimal fitness. The test case is a **light-seeking** (phototactic) mobile robot, with results comparable to incremental multi-subgoal evolution.

**Silva, F., Duarte, M., Correia, L., Oliveira, S. M., & Christensen, A. L. (2016). Open issues in evolutionary robotics. *Evolutionary Computation*, 24(2), 205–236.**
- DOI: https://doi.org/10.1162/EVCO_a_00172 (preprint: http://home.iscte-iul.pt/~alcen/pubs/preprint_openissues.pdf)
- How verified: Crossref record. Abstract via OpenAlex. **Note:** the author list is five authors, not the "Silva, Christensen, Correia" given in the prompt.
- Summary: This is a review of the obstacles to ER as an engineering method: simulation versus real hardware, and three evolutionary-computation issues. Those issues are (1) the bootstrap problem, (2) deception, and (3) genomic encoding and genotype–phenotype mapping for complex tasks. It also criticises the lack of standard research practices.

### Theory and biology

**Nilsson, D.-E., & Pelger, S. (1994). A pessimistic estimate of the time required for an eye to evolve. *Proceedings of the Royal Society B: Biological Sciences*, 256(1345), 53–58.**
- DOI: https://doi.org/10.1098/rspb.1994.0048
- How verified: Crossref record. Authors confirmed via Semantic Scholar. Abstract via OpenAlex.
- Summary: If selection *constantly* favours an increase in detectable spatial information, a light-sensitive patch can turn into a focused lens eye through **continuous small improvements**. Even with pessimistic assumptions, this takes only a few hundred thousand years. The key premise is that every intermediate step pays. That is exactly what the two-sensor "compass" lacks when a lone sensor makes the robot spin.

**Viswanathan, G. M., Buldyrev, S. V., Havlin, S., da Luz, M. G. E., Raposo, E. P., & Stanley, H. E. (1999). Optimizing the success of random searches. *Nature*, 401(6756), 911–914.**
- DOI: https://doi.org/10.1038/44831 ; PubMed PMID 10553906
- How verified: Crossref and PubMed records. Abstract via PubMed.
- Summary: The paper studies a forager that can detect targets only in its limited vicinity. When targets are **sparse and revisitable**, an inverse-square power-law (Lévy) distribution of flight lengths is optimal, and foraging data from several insect, mammal and bird species fit that prediction. This shows that "blind" statistical search strategies can be optimal when cues are only short-range. The observed "blind mower" is a related, not identical, strategy: in its world, yield is linear in area swept.

**Kussell, E., & Leibler, S. (2005). Phenotypic diversity, population growth, and information in fluctuating environments. *Science*, 309(5743), 2075–2078.**
- DOI: https://doi.org/10.1126/science.1114383 ; PubMed PMID 16123265
- How verified: Crossref and PubMed records. Abstract via PubMed.
- Summary: Organisms in fluctuating environments can adapt by **sensing followed by response** or by stochastic phenotype switching. **Switching (no sensing) is favoured when the environment changes infrequently.** The paper relates long-term growth rate to the information available about the environment. It gives a formal statement that sensing pays only when the environment varies enough, and on the right timescale, to cover its cost.

**Stephens, D. W. (1991). Change, regularity, and value in the evolution of animal learning. *Behavioral Ecology*, 2(1), 77–89.**
- DOI: https://doi.org/10.1093/beheco/2.1.77
- How verified: Crossref record. Abstract via OpenAlex.
- Summary: The model asks when learning (tracking the environment) evolves as a function of change, regularity and value. Learning is favoured by *within-lifetime* persistence combined with some change. It does not evolve when the environment is almost fixed. Learning is "most useful when all the alternatives to learning yield about the same payoff." By analogy, if a fixed blind strategy already captures most of the payoff, information-tracking has little marginal value. This is a paper about learning, so apply it to sensing by analogy only.

**Mandik, P., Collins, M., & Vereschagin, A. (2007). Evolving artificial minds and brains. In *Mental States, Vol. 1: Evolution, Function, Nature* (Studies in Language Companion Series 92, pp. 75–94). John Benjamins.**
- DOI: https://doi.org/10.1075/slcs.92.07man
- How verified: Crossref record (chapter 5, pp. 75–94, 2007). Abstract via OpenAlex. **Note:** the year is 2007, not 2003. The volume editors were not in the retrieved record.
- Summary: This is a philosophy-of-mind chapter that uses simulations of evolved neural-network controllers to argue that evolved representations must carry information about the environment and be appropriately isomorphic to environmental states. Its main interest is conceptual. I included it only because it verified. It is optional for the review.

---

## UNVERIFIED

- **Balakrishnan, K., & Honavar, V. (1996). "On sensor evolution in robotics." *Genetic Programming 1996: Proc. 1st Annual Conference* (pp. 455–460), MIT Press.** I found it only as a citation in other papers' reference lists (e.g. the 2025 *Sensors* "Metasensor" paper). I found no DOI, dblp entry (dblp blocked my access), publisher page or author page. It very likely exists, but it does not meet the verification bar. Use the 2001 MIT Press chapter above instead.
- **Mark, A., Polani, D., & Uthmann, T. (1998). "A framework for sensor evolution in a population of Braitenberg vehicle-like agents." *Artificial Life VI* (pp. 428–432).** A Semantic Scholar record confirms the authors (A. Mark, D. Polani, T. Uthmann), the year 1998 and the title (tagged "(poster)"). But the record has **no venue**, and I found no proceedings DOI or publisher page. The ALIFE VI venue and pages come only from secondary citations. The description of the XRaptor 2-D world with Braitenberg-like agents that evolve the number and characteristics of "eyes" also comes only from search snippets. Partially verified: do not cite the venue or pages without checking.
- **"Liese, Polani, Uthmann 2001 — A study of the simultaneous evolution of morphology and control in artificial sensorimotor systems."** No such title found. The real paper by these authors in 2001 is "A study of the simulated evolution of the spectral sensitivity of visual agent receptors" (*Artificial Life* 7(2)), listed as VERIFIED above.
- **Mandik 2003 (single-author).** No 2003 record was found. The verified item is the 2007 Mandik, Collins and Vereschagin chapter above.
- **"Evolving eyes" / "evolution of vision in digital organisms" / Jaderberg / Tosik / Baradad 2022.** No record matching these was found. The verified modern work on computationally evolving eyes is Tiwary et al. 2025 (above).
- **Avida "evolution of phototaxis / chemotaxis / sensing" (e.g. Goldsby).** I found no specific paper matching that description. The search surfaced Grabowski et al. on odometric behaviour (PLOS ONE) and Avida foraging work, but I did not verify any of these, so none is cited.
- **Patchy-resource simulation papers showing that environmental structure made sensing evolve (Todd & Miller; "evolution of search strategies in patchy environments").** No suitable, specific paper was verified in the time available. Search hits, such as ideal-free-distribution animats (arXiv 1112.3574) and swarming via signalling (PLOS ONE 2016), were not checked against the claim. The verified items that make the environmental-structure argument are Goldstein & Soyer 2008 (scarcity and fluctuation shape evolved taxis dynamics), Kussell & Leibler 2005, Stephens 1991 and Floreano & Mondada 1996.
- **Nolfi & Floreano 2000 claims about specific chapters on sensor evolution.** The book itself is verified, but the chapter contents are not.

---

## Why perception is hard to evolve, and what worlds/incentives made it evolve in others' work

In the verified literature, perception evolves reliably when three conditions hold. First, the world makes the sensed signal *decision-relevant*. Second, the fitness landscape rewards partial sensing. Third, the sensor is supplied by design or can be tuned incrementally.

Most classic successes provided the sensor morphology and rewarded an outcome that is impossible without it. Examples include reaching a chemical source (Beer & Gallagher 1992) and catching or avoiding objects by category (Beer 1996, 2003). Others include reaching a landmark-defined goal with a compass and eyes (Dale & Collett 2001), finding and returning to a charger before energy runs out (Floreano & Mondada 1996), and getting to a room's centre (Cliff, Husbands & Harvey 1993). Where sensors themselves were evolved, the sensor search space was smooth and each step paid. Examples are visual sampling morphology co-evolved on a real camera robot (Harvey, Husbands & Cliff 1994), receptor spectral sensitivity traded against explicit sensor cost (Liese, Polani & Uthmann 2001), and eye types that diverge according to task (Tiwary et al. 2025). This echoes the Nilsson & Pelger (1994) premise that an eye evolves quickly only if "selection constantly favours an increase" in detectable information.

Chemotaxis in particular can avoid the two-sensor valley entirely. Evolved *C. elegans* klinotaxis uses an ON/OFF pair of neurons driven by a single sensory input, with body undulation doing the spatial sampling (Izquierdo & Lockery 2010; Izquierdo & Beer 2013). In evolved virtual bacteria, a two-component pathway suffices, and which dynamics evolve depends on stimulus scarcity and fluctuation (Goldstein & Soyer 2008).

The theory literature explains the "blind mower". Sensing is favoured over fixed or stochastic strategies only when the environment varies enough, and on the right timescale, to repay it (Kussell & Leibler 2005). Information-tracking is least valuable when the uninformed alternatives already yield about the same payoff (Stephens 1991). When cues are only short-range and targets are sparse, blind statistical search can be optimal (Viswanathan et al. 1999). A world whose yield is linear in area swept is exactly such a world. The ER methodology literature adds that when the initial population has no gradient toward a capability, evolution stalls. This is the bootstrap problem (Nelson, Barlow & Doitsidis 2009; Silva et al. 2016). Mouret & Doncieux (2009) addressed it for a light-seeking robot with behavioural-diversity objectives. Klyubin, Polani & Nehaniv (2005) proposed empowerment as a task-independent drive for sensor–actuator evolution.

Taken together, the incentives that made perception evolve in others' work are:
- (a) food or goals that are sparse, moving or clustered, so that where you go matters more than how much ground you cover;
- (b) a reward that cannot be collected by coverage alone, such as a single source, a return trip or an energy deadline;
- (c) sensing mechanisms whose minimal version already helps: single-sensor temporal gradient sampling rather than a bilateral pair;
- (d) explicit diversity or intrinsic-information pressure to cross valleys that the extrinsic reward does not.
