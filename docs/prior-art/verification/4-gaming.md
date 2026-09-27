# 4. Simulators gamed by evolution: specification gaming, physics exploits, and remedies

Verified 2026-09-27. "Verified" means a real record was found (DOI/Crossref, arXiv, publisher/proceedings page, PubMed, or the author's own PDF) and authors, year, title and venue were confirmed from it. Summaries draw only on text I read: the full text where noted, otherwise the abstract. Page numbers come from Crossref or the arXiv/PDF record and none were guessed.

How our four exploits map to the literature (details below):
- (1) mass/weight-class creep: Sims 1994 capped the number of parts. Taylor & Massey 2001 capped parts at 4–10. Krcah 2008 rejected robots with too many or too-small parts. Cheney et al. 2013 multiplied fitness by a voxel-count penalty.
- (2) harvesting the spawn drop: Sims 1994 relaxed the creature (no friction, no effectors) until its centre-of-mass height reached a stable minimum, then began scoring. Lehman et al. 2020 retell this, along with Krcah's pole-vaulting "jumpers". Cully et al. (via Lehman) ignored the first few tenths of a second.
- (3) motor capacity growing faster than mass: Sims 1994 set each effector's maximum strength proportional to the cross-sectional area of the parts it joins. Because mass scales with volume, strength does not scale up for free. Cheney et al. 2013 penalised the amount of actuated material. Taylor & Massey 2001 limited joint forces and still had to detect "explosions".
- (4) contact penetration: Sims 1994 shrank the timestep to keep penetrations under a tolerance and discarded creatures whose parts kept interpenetrating. Cheney's VoxCAD exploit (via Lehman) was fixed with more ground-contact damping, a larger minimum size, and a timestep rule that reduces penetration. The MuJoCo docs explain how penetration depth follows from solref/solimp and the timestep.

---

## VERIFIED

### Lehman, Clune, Misevic, et al. 2020 — "The surprising creativity of digital evolution"
- **Citation:** Lehman J, Clune J, Misevic D, Adami C, Altenberg L, Beaulieu J, Bentley PJ, Bernard S, et al. (53 authors, incl. K. Sims, N. Cheney, P. Krcah, R. Feldt, H. Lipson, J.-B. Mouret, S. Doncieux). "The Surprising Creativity of Digital Evolution: A Collection of Anecdotes from the Evolutionary Computation and Artificial Life Research Communities." *Artificial Life* 26(2):274–306, 2020. doi:10.1162/artl_a_00319. Preprint arXiv:1803.03453 (v1 9 Mar 2018, v4 21 Nov 2019).
- **Links:** https://doi.org/10.1162/artl_a_00319 · https://arxiv.org/abs/1803.03453
- **How verified:** Crossref record (DOI, volume/issue/pages); arXiv abstract page; full arXiv PDF downloaded and read.
- **Summary:** This is a crowdsourced collection of cases where digital evolution subverted what the experimenters intended. It sorts them into "misspecified fitness functions", "unintended debugging" (evolution finds bugs in the simulator or hardware and exploits them), "exceeded expectations", and "convergence with biology". The authors argue that physics simulators "rarely mimic the real world exactly", so "edge cases, bugs, or minor flaws in the implemented laws of physics, are sometimes amplified and exploited by evolution". The practical lessons they give are: expect the fitness specification to fail, "adopt an adversarial mindset", and "regularly visualize their simulated solutions to test whether the proposed solutions are valid and reasonable".
- **Physics-exploit anecdotes and what was done about each (all from the arXiv text):**
  1. **Sims: tall creatures that fall over.** Fitness was average ground velocity over 10 s. Creatures "evolved to become tall and rigid... they would fall over, harnessing their initial potential energy to achieve high velocity", and some somersaulted to keep moving. *Fix:* "allocate time at the beginning of each simulation to relax the potential energy inherent in the creature's initial stance before motion was rewarded." This matches our exploit (2).
  2. **Krcah (ERO, ODE): jumping.** Fitness was the maximum height of the centre of gravity, so a "tall, static tower" body scored well. *Fix attempt:* fitness was changed to the distance from the ground to the block that was originally lowest. Evolution then made tall creatures that kick off and fall head-first, somersaulting the original "lowest" block into the air, for a near-tenfold "improvement". The problem was caught only by watching the behaviour, not from the numbers.
  3. **Sims: Euler-integration "free energy".** The first simulator used simple Euler integration. With fast motion the errors accumulated, and swimmers learned to twitch small body parts quickly to get "free energy" and reach unrealistic speeds. *Fix:* patched (Sims 1994 describes the final simulator as Runge-Kutta-Fehlberg with adaptive steps; see below).
  4. **Sims: self-collision "grasshoppers".** When evolving jumpers, creatures found a bug in collision detection and response. Hitting "corners of two of their body parts together in a certain way" popped them "airborne like impossibly-strong grasshoppers". *Fix:* the bug was patched, after which the evolved locomotion "did not violate the laws of physics".
  5. **Cheney et al. soft robots (VoxCAD): timestep heuristic and ground penetration.** The simulator lowered the timestep as cell count rose. Creatures shrank to a few cells to get a large timestep, which let their bottom cells "penetrate the ground between time steps without the collision being detected". The corrective upward force gave "free" energy, so they vibrated across the ground. *Fixes:* "Damping was increased when contacting the ground, the minimum creature size was raised, and the time delta calculation was adjusted to reduce ground penetration." This is directly relevant to our exploit (4).
  6. **Feldt 1997: floating-point overflow.** Evolved aircraft-arresting controllers produced forces so large that the calculation overflowed and "roll[ed] over" to zero, which read as zero stress and a perfect score. *Outcome:* the simulator loophole was identified, and the work fed into search-based software testing.
  7. **NERO (Torque engine): walking up walls.** Agents evolved a "wiggle" that let them climb vertical walls through a little-known engine bug. *Fix:* the team "had to plug this loophole".
  8. **Moriarty & Miikkulainen 1996 (OSCAR-6 arm).** A simulator change silently disabled the main motor. The arm turned toward targets by whipping its elbow and using inertia. This was a bug found by watching the behaviour.
  9. **Ecarlat et al. (MAP-Elites arm).** With the gripper disabled, the arm hit the box so as to force the gripper open and grasp it anyway.
  10. **Cully et al. 2015: elbow walking.** A hexapod was asked to walk with zero foot contact and did it by flipping over and walking on its elbows. The paper notes that the "first few tenths of a second of the simulation are ignored" so that scoring starts from the steady gait rather than the initial position, which is a form of transient exclusion.
  11. **Punch (carbon energy model).** Evolution put all atoms on the same point. The physicists patched the model and evolution found another edge case. A non-locomotion example of the same pattern.

### Sims 1994 — "Evolving virtual creatures" (SIGGRAPH '94)
- **Citation:** Sims K. "Evolving virtual creatures." *Proceedings of the 21st Annual Conference on Computer Graphics and Interactive Techniques (SIGGRAPH '94)*, ACM, 1994, pp. 15–22. doi:10.1145/192161.192167.
- **Links:** https://doi.org/10.1145/192161.192167 · author PDF https://www.karlsims.com/papers/siggraph94.pdf
- **How verified:** Crossref record; author's own PDF downloaded and read in full.
- **Summary:** Sims co-evolves block-based morphologies and neural controllers with directed-graph genotypes and selects for swimming, walking, jumping and following. Physics uses Featherstone articulated-body dynamics, Runge-Kutta-Fehlberg integration with adaptive steps (1–5 steps per 1/30 s frame), and hybrid impulse/penalty-spring collision response. Sims warns that "Any bugs that allow energy leaks from non-conservation, or even round-off errors, will inevitably be discovered and exploited by the evolving creatures", and adds that this is a "lazy and often amusing approach for debugging a physical modeling system" but "not necessarily the most practical."
- **Anti-exploit measures stated in the paper (direct from the PDF):**
  - **Actuator budget tied to geometry:** "Each effector is given a maximum-strength proportional to the maximum cross sectional area of the two parts it joins. Effector forces are scaled by these strengths and not permitted to exceed them. Since strength scales with area, but mass scales with volume, as in nature, behavior does not always scale uniformly." This is the closest precedent for fixing our exploit (3): our gear ∝ 4 × mass per DOF lets strength scale with volume, and up to 3×, so it is looser than Sims's area-based cap.
  - **Penetration control:** "If necessary, the previous time-step is reduced to keep any new penetrations below a certain tolerance." Connected parts may interpenetrate but cannot rotate through each other, which is handled with clipped collision shapes. Relevant to our exploit (4).
  - **Viability checks before evaluation:** creatures with "more than a specified number of parts are removed". Creatures whose parts initially interpenetrate get a short repulsion simulation, and those "with persistent interpenetrations are also discarded". Relevant to (1) and (4).
  - **Anti-falling relaxation:** "it can be necessary to prevent creatures from generating high velocities by simply falling over. This is accomplished by first running the simulation with no friction and no effector forces until the height of the center of mass reaches a stable minimum." This is the direct fix for our exploit (2).
  - **Fitness shaping:** for swimming, later-phase velocities are weighted more heavily so that "continuing movement is rewarded over that from a single initial push". For walking, vertical velocity is ignored.
  - **Future work:** fitness "might be the distance traveled divided by the amount of energy consumed", i.e. an energy-efficiency objective.

### Sims 1994 — "Evolving 3D morphology and behavior by competition"
- **Citation:** Sims K. *Artificial Life* 1(4):353–372, 1994. doi:10.1162/artl.1994.1.4.353.
- **How verified:** Crossref record. Only the bibliographic record was checked, not the full text. Lehman et al. cite it as ref. 38 alongside the SIGGRAPH paper for the creature anecdotes.
- **Summary:** This is the companion paper, which evolves creatures through competition. It is listed so the Lehman references can be traced. I did not read it for exploit content.

### Krcah 2008 — "Towards efficient evolutionary design of autonomous robots"
- **Citation:** Krčah P. "Towards Efficient Evolutionary Design of Autonomous Robots." In: *Evolvable Systems: From Biology to Hardware, 8th International Conference, ICES 2008*, Lecture Notes in Computer Science vol. 5216, Springer, 2008, pp. 153–164. doi:10.1007/978-3-540-85857-7_14.
- **Links:** https://doi.org/10.1007/978-3-540-85857-7_14 · PDF copy: https://gwern.net/doc/reinforcement-learning/exploration/2008-krcah.pdf
- **How verified:** Crossref record (LNCS, pp. 153–164) and Semantic Scholar (ICES 2008). The full PDF was read, and its page header shows "156 P. Krčah". I did not directly see the LNCS volume number 5216 on a record, but it is consistent with ICES 2008.
- **Summary:** The paper proposes hNEAT, which applies NEAT's speciation, crossover with historical markings, and complexification to both morphology and control of Sims-style robots simulated in ODE. It tests on light-following, walking, jumping and swimming. Section 3.3, "Validity Testing", says that "robots often exploit properties of the physical simulation to their advantage" and that pre-simulation tests "discover abusive robots early (e.g. test for self-penetration, excessively small body parts, excessively large number of body parts)". Variation operators are re-applied until a genotype passes. The jumping-exploit anecdotes are in Lehman et al., not in this paper.

### Cheney, MacCurdy, Clune, Lipson 2013 — "Unshackling evolution"
- **Citation:** Cheney N, MacCurdy R, Clune J, Lipson H. "Unshackling evolution: evolving soft robots with multiple materials and a powerful generative encoding." *Proceedings of GECCO 2013*, ACM, pp. 167–174. doi:10.1145/2463372.2463404. (Reprinted in ACM SIGEVOlution 7(1):11–23, 2014, doi:10.1145/2661735.2661737.)
- **Links:** https://doi.org/10.1145/2463372.2463404 · author PDF http://jeffclune.com/publications/2013_Softbots_GECCO.pdf
- **How verified:** Crossref; OpenAlex abstract; full PDF read.
- **Summary:** The authors evolve CPPN-encoded multi-material voxel soft robots (up to 10×10×10) in the VoxCAD simulator, with fitness equal to centre-of-mass displacement over 10 actuation cycles. They test **penalty regimes**: fitness is multiplied by (1 − penalty/max penalty), with the penalty being the number of voxels ("an animal having to work harder to carry more weight"), the amount of actuated material ("analogous to the cost of expending energy to contract muscles"), or the number of connections. They also run a no-penalty baseline. The actuation cost performed significantly worse than no cost, but all regimes were similar over evolutionary time and produced very different body plans. With no penalty, bodies had more voxels; with an actuation cost, evolution used more passive support material. This is precedent for a body-size or actuator budget applied as a fitness multiplier. The VoxCAD timestep/penetration exploit and its fixes are reported in Lehman et al., not in this paper.

### Taylor & Massey 2001 — Recent developments… physically simulated creatures
- **Citation:** Taylor T, Massey C. "Recent Developments in the Evolution of Morphologies and Controllers for Physically Simulated Creatures." *Artificial Life* 7(1):77–87, 2001. doi:10.1162/106454601300328034.
- **Links:** https://doi.org/10.1162/106454601300328034 · author PDF https://www.tim-taylor.com/papers/taylor2001recent.pdf
- **How verified:** Crossref; OpenAlex abstract; author's PDF read.
- **Summary:** The authors re-implemented Sims's system on PCs with the MathEngine physics engine and surveyed other replications. Their stated aim included highlighting "deficiencies of these engines and pitfalls when using them". They capped body parts at 4–10 per creature and used a 0.05 s integration step. "Despite various attempts to limit the magnitude of the forces applied to joints", creatures evolved motions whose forces and velocities were too large for the solver at that step. The creature then "unrecoverably exploded". Their fixes were to count the engine's instability warnings and abort creatures over a threshold, and to abort any creature that showed explosion signatures such as very high velocities. They conclude that "no matter which physics engine is used ... a certain number of stability checks ... will be required". They also note that newer force-limited velocity-constraint actuators (MathEngine) and dashpots (Havok) gave more stable joint effectors.

### Chaumont, Egli, Adami 2007 — "Evolving virtual creatures and catapults"
- **Citation:** Chaumont N, Egli R, Adami C. "Evolving Virtual Creatures and Catapults." *Artificial Life* 13(2):139–157, 2007. doi:10.1162/artl.2007.13.2.139.
- **How verified:** Crossref and OpenAlex (abstract). I could not read the full text because the MIT Press PDF returned an HTML block page.
- **Summary (abstract only):** A Sims-style system built on an off-the-shelf dynamics engine evolved walkers with "various realistic gaits while using fairly simple objective functions". Catapults evolved throwing strategies, including a drop-kick, and "the systematic invention of the principle behind the wheel" when mutations to the projectile were allowed. I found no anti-exploit measures in the abstract and did not check the body text.

### Miconi & Channon 2005 — A virtual creatures model for studies in artificial evolution
- **Citation:** Miconi T, Channon A. "A virtual creatures model for studies in artificial evolution." *2005 IEEE Congress on Evolutionary Computation*, vol. 1, pp. 565–572. doi:10.1109/CEC.2005.1554733.
- **How verified:** Crossref and Semantic Scholar abstract. The full text was not read because the Keele eprint URL returned HTML.
- **Summary (abstract only):** This is a replication of Sims's creatures using standard McCulloch-Pitts neurons and "realistic Newtonian physics", with source code released. The authors claim to be the first replication comparable to Sims's in efficiency and complexity. **I could not confirm whether it describes specific exploit fixes.** (The brief's "Miconi & Channon 2006" matched a different 2006 LNCS paper, "Analysing Co-evolution Among Artificial 3D Creatures", doi:10.1007/11740698_15, which I did not read.)

### Lessin, Fussell, Miikkulainen 2013 — Open-ended behavioral complexity for evolved virtual creatures
- **Citation:** Lessin D, Fussell D, Miikkulainen R. *Proceedings of GECCO 2013*, pp. 335–342. doi:10.1145/2463372.2463411.
- **Links:** author PDF http://nn.cs.utexas.edu/downloads/papers/lessin.gecco13.pdf
- **How verified:** Crossref; full PDF read.
- **Summary:** This is the ESP method (syllabus, encapsulation, pandemonium) for building complex behaviours in Sims-style creatures simulated in NVIDIA PhysX. Its actuators are muscles, each defined by two attachment points "along with a maximum strength value" and implemented as springs whose constant is set by activation. Joint limits come mostly from natural collisions between segments rather than evolved explicit limits. It is only marginally relevant: an example of a per-actuator strength cap in a different actuator model.

### Lipson & Pollack 2000 — "Automatic design and manufacture of robotic lifeforms"
- **Citation:** Lipson H, Pollack JB. *Nature* 406(6799):974–978, 2000. doi:10.1038/35023115. PMID 10984047.
- **How verified:** Crossref; PubMed abstract.
- **Summary:** Simple electromechanical machines (bars, actuators, neurons) were evolved in simulation for locomotion, and the fittest were fabricated automatically with rapid prototyping. The abstract describes evolution in a "'limited universe' physical simulation coupled to automatic fabrication". Taylor & Massey's table lists its simulator as "relaxation by energy minimization for quasi-static motion". That is a deliberately conservative, quasi-static physics that leaves little dynamic "free energy" for evolution to harvest. (This characterisation comes from Taylor & Massey's table; I did not read the Nature full text.)

### Hiller & Lipson 2012 — "Automatic design and manufacture of soft robots"
- **Citation:** Hiller J, Lipson H. *IEEE Transactions on Robotics* 28(2):457–466, 2012. doi:10.1109/TRO.2011.2172702.
- **How verified:** Crossref; OpenAlex abstract.
- **Summary (abstract):** Freeform multi-material objects were evolved and 3D-printed. Cantilever beams matched simulation within 0.5–7.6%, and a fabricated soft locomotor matched it with 15% error. This is the simulator behind Cheney et al. (VoxCAD). **The abstract does not mention cost or energy terms, and I did not verify the brief's "including cost/energy" claim.**

### Bhatia et al. 2021 — Evolution Gym
- **Citation:** Bhatia JS, Jackson H, Tian Y, Xu J, Matusik W. "Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots." *Advances in Neural Information Processing Systems 34 (NeurIPS 2021)*. arXiv:2201.09863.
- **Links:** https://proceedings.neurips.cc/paper/2021/hash/118921efba23fc329e6560b27861f0c2-Abstract.html · https://arxiv.org/abs/2201.09863
- **How verified:** NeurIPS proceedings page; arXiv abstract; full arXiv PDF grepped.
- **Summary:** This is a benchmark of 2D voxel soft robots (rigid, soft, and horizontal/vertical actuator voxels) on a fixed grid, typically 5×5, co-optimising design with RL control across locomotion and manipulation tasks. Design optimisation works "under two physical constraints: the body has to be connected, and actuators must exist". The body is also bounded by the fixed voxel grid, which is a hard morphological size budget. Appendix A.4 describes simulator safeguards such as **strain limiting**: if a spring changes length by more than 25% (3% for rigid cells), the simulator repositions the masses to prevent self-folding. The paper notes this "can still be overcome by very strong actuations".

### Jakobi, Husbands, Harvey 1995 — "Noise and the reality gap"
- **Citation:** Jakobi N, Husbands P, Harvey I. "Noise and the reality gap: The use of simulation in evolutionary robotics." In: *Advances in Artificial Life (ECAL 1995)*, Lecture Notes in Computer Science vol. 929, Springer, 1995, pp. 704–720. doi:10.1007/3-540-59496-5_337.
- **How verified:** Crossref (LNCS, pp. 704–720, 1995) and Semantic Scholar (ECAL). The LNCS volume 929 comes from search-engine listings and the Springer DOI prefix, not from a record I could open. The full text was not accessible.
- **Summary (from secondary descriptions only; I did not read the paper):** The authors built an empirically parameterised simulation of a Khepera robot and evolved controllers for obstacle avoidance and light seeking under different levels of simulated noise, then compared simulated and real behaviour. Koos et al. 2013 describe it as the origin of noise-based approaches to the reality gap. Treat the specifics as unconfirmed until the text is read.

### Jakobi 1997 — "Evolutionary robotics and the radical envelope-of-noise hypothesis"
- **Citation:** Jakobi N. *Adaptive Behavior* 6(2):325–368, 1997. doi:10.1177/105971239700600205.
- **Links:** https://doi.org/10.1177/105971239700600205 · PDF copy http://www.cs.sfu.ca/~vaughan/teaching/889/papers/jakobi_radical.pdf
- **How verified:** Crossref; PDF obtained (SAGE header with DOI and "1997; 6; 325"); abstract and introduction read.
- **Summary:** Jakobi proposes "sufficient conditions for the successful transfer of evolved controllers from simulation to reality" and a methodology for minimal simulations. Features the task doesn't depend on are deliberately made unreliable by varying them randomly, so controllers cannot rely on them and are "forced to satisfy these conditions if they are to be reliably fit". He hypothesises that if simulations follow this methodology, "it does not matter how inaccurate or incomplete they are". Controllers evolved in minimal look-up-table simulations transferred robustly to a Khepera memory task and to triangle-versus-square discrimination on the Sussex gantry robot. The implication for us is to randomise what evolution should not rely on, such as contact softness, spawn height, and friction, so that exploiting it is unreliable.

### Koos, Mouret, Doncieux 2013 — "The transferability approach"
- **Citation:** Koos S, Mouret J-B, Doncieux S. "The Transferability Approach: Crossing the Reality Gap in Evolutionary Robotics." *IEEE Transactions on Evolutionary Computation* 17(1):122–145, 2013. doi:10.1109/TEVC.2012.2185849.
- **How verified:** Crossref; Semantic Scholar abstract.
- **Summary (abstract):** The authors hypothesise that "the most efficient solutions in simulation often exploit badly modeled phenomena to achieve high fitness values with unrealistic behaviors". They add a second objective, **transferability**, estimated by a surrogate model of simulation-to-reality disparity trained on a few real-robot tests, and optimise it jointly with fitness in a Pareto multi-objective EA. On an e-puck navigation task and an 8-DOF quadruped walking task, it found efficient, transferable controllers with about ten real experiments. It was compared against a Jakobi-style noise approach and local search. For a sim-only project, the analogue is to add an "exploit-disparity" objective, for example comparing performance under a conservative, stiffer or smaller-timestep simulator.

### Amodei et al. 2016 — "Concrete problems in AI safety"
- **Citation:** Amodei D, Olah C, Steinhardt J, Christiano P, Schulman J, Mané D. "Concrete Problems in AI Safety." arXiv:1606.06565, 2016.
- **Links:** https://arxiv.org/abs/1606.06565
- **How verified:** arXiv abstract page; full PDF grepped.
- **Summary:** The paper defines five accident-risk problems, including "avoiding reward hacking". It notes that "Modern RL agents already do discover and exploit bugs in their environments". Proposed mitigations include adversarial reward functions, model lookahead, "careful engineering" (formal verification or testing), reward capping, multiple rewards, reward pretraining, variable indifference, and **trip wires**: deliberately planted vulnerabilities that are monitored so that exploitation is detected and the agent stopped. Trip wires and reward capping map to exploit detectors such as a penetration-depth monitor and a cap on centre-of-mass speed.

### Krakovna et al. 2020 — "Specification gaming: the flip side of AI ingenuity" (DeepMind blog)
- **Citation:** Krakovna V, Uesato J, Mikulik V, Rahtz M, Everitt T, Kumar R, Kenton Z, Leike J, Legg S. "Specification gaming: the flip side of AI ingenuity." DeepMind blog, 21 April 2020.
- **Links:** https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/ (resolves to https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/). Examples list: http://tinyurl.com/specification-gaming. Google Sheet URL as given on Krakovna's 2018 post: https://docs.google.com/spreadsheets/d/e/2PACX-1vRPiprOaC3HsCf5Tuum8bRfzYUiKLRqJmbOoC-32JorNdfyTiRRsR7Ea5eWtvsWzuxo8bjOxCG84dAg/pubhtml
- **How verified:** The blog page was fetched, and authors and date were read from it. The spreadsheet URL was read from V. Krakovna, "Specification gaming examples in AI", 2 April 2018, https://vkrakovna.wordpress.com/2018/04/02/specification-gaming-examples-in-ai/. The sheet itself was not opened.
- **Summary:** The post defines specification gaming as behaviour that "satisfies the literal specification of an objective without achieving the intended outcome" and says the authors had collected about 60 examples. It explicitly covers simulator-bug exploitation, for example a simulated walking robot that learned to "hook its legs together and slide along the ground". It argues that "the underlying problem isn't the bug itself but a failure of abstraction that can be exploited by the agent". This supports treating our four exploits as abstraction failures (weight class, spawn, motor rule, contact model) rather than one-off bugs.

### Baker et al. 2020 — "Emergent tool use from multi-agent autocurricula"
- **Citation:** Baker B, Kanitscheider I, Markov T, Wu Y, Powell G, McGrew B, Mordatch I. "Emergent Tool Use From Multi-Agent Autocurricula." ICLR 2020. arXiv:1909.07528.
- **Links:** https://arxiv.org/abs/1909.07528
- **How verified:** arXiv abstract page. The full PDF was read, and its footer says "Published as a conference paper at ICLR 2020".
- **Summary:** In hide-and-seek, RL agents (in a MuJoCo-based world) discovered "box surfing". This worked "because the agents' movement action allows them to apply a force on themselves regardless of whether they are on the ground or not". The hiders' counter was to lock all boxes. The authors report that agents "were very skilled at exploiting small inaccuracies in the design of the environment... or agents exploiting inaccuracies of the physics simulations". They call generating environments without such behaviours an open problem, citing Amodei et al. and Lehman et al. It is an RL analogue of our motor-rule exploit: an actuation model that allows force without a physical reaction path.

### Peng, Andrychowicz, Zaremba, Abbeel 2018 — Dynamics randomization
- **Citation:** Peng XB, Andrychowicz M, Zaremba W, Abbeel P. "Sim-to-Real Transfer of Robotic Control with Dynamics Randomization." arXiv:1710.06537 (2017). *Venue not verified by me; commonly cited as ICRA 2018.*
- **How verified:** arXiv abstract page. This is a verified preprint; the conference venue is unverified.
- **Summary:** "Behaviours developed by agents in simulation are often specific to the characteristics of the simulator". Randomising simulator dynamics during training produced policies that adapted to very different dynamics and transferred to a real arm pushing task with no real-world training. This is the RL descendant of Jakobi's envelope of noise.

### Tobin et al. 2017 — Domain randomization
- **Citation:** Tobin J, Fong R, Ray A, Schneider J, Zaremba W, Abbeel P. "Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World." arXiv:1703.06907, 2017. *Venue not verified by me.*
- **How verified:** arXiv abstract page.
- **Summary:** Randomising rendering, which is visual rather than physical, lets detectors trained purely in simulation transfer to reality, "With enough variability in the simulator, the real world may appear to the model as just another variation." It is included only as the origin of the term. It concerns perception, not physics exploits.

### Nygaard, Martin, Samuelsen, Torresen, Glette 2018 — Real-world evolution under hardware limitations
- **Citation:** Nygaard TF, Martin CP, Samuelsen E, Torresen J, Glette K. "Real-world evolution adapts robot morphology and control to hardware limitations." *Proceedings of GECCO 2018*, pp. 125–132. doi:10.1145/3205455.3205567. arXiv:1805.03388.
- **How verified:** Crossref; arXiv abstract page.
- **Summary (abstract):** The authors run multi-objective evolution of morphology (leg lengths) and control directly on a physical quadruped, which avoids the reality gap. Lowering the supply voltage reduces the "available torque and speed of all joints". Under these different actuator limits evolution adapted both control and morphology and reached comparable performance at low and moderate speeds. This is evidence that an actuator budget fixed independently of body design is a realistic constraint that evolution can work within.

### Erez, Tassa, Todorov 2015 — Simulator comparison
- **Citation:** Erez T, Tassa Y, Todorov E. "Simulation tools for model-based robotics: Comparison of Bullet, Havok, MuJoCo, ODE and PhysX." *2015 IEEE International Conference on Robotics and Automation (ICRA)*, pp. 4397–4404. doi:10.1109/ICRA.2015.7139807.
- **How verified:** Crossref; OpenAlex abstract.
- **Summary (abstract):** The paper introduces quantitative measures of simulation performance focused on numerical challenges typical of robotics, and runs the same models side by side in five engines. "Each engine performs best on the type of system it was designed and optimized for: MuJoCo wins the robotics-related tests". It is useful for justifying MuJoCo, and for a stability/accuracy-versus-timestep check as a conservative-physics test.

### Todorov, Erez, Tassa 2012 — MuJoCo
- **Citation:** Todorov E, Erez T, Tassa Y. "MuJoCo: A physics engine for model-based control." *2012 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, pp. 5026–5033. doi:10.1109/IROS.2012.6386109.
- **How verified:** Crossref; OpenAlex abstract.
- **Summary (abstract):** MuJoCo uses generalized coordinates with recursive algorithms, and computes contacts with velocity-stepping algorithms "which avoids the difficulties with spring-dampers". It supports forward and inverse dynamics with contacts.

### MuJoCo documentation — soft contacts, solref/solimp, actuator limits (technical documentation, not peer reviewed)
- **Links:** https://mujoco.readthedocs.io/en/stable/computation/index.html · https://mujoco.readthedocs.io/en/stable/modeling.html
- **How verified:** Fetched 2026-09-27 (docs "stable").
- **Summary:** MuJoCo's contact model is deliberately soft. It drops strict complementarity, so while in penetration both normal force and velocity can be positive, and constraint violation is penalised rather than forbidden. Penetration is tuned with `solref` (timeconst, dampratio) and `solimp` (impedance). The docs say timeconst "should be at least two times larger than the simulation time step, otherwise the system can become too stiff" (enforced unless `refsafe` is disabled). Resting penetration scales with timeconst² (standard format) or 1/stiffness (direct negative format). Contact `margin` is summed across geoms. Actuator output can be clamped by `ctrlrange`, `forcerange`, or joint-level `actuatorfrcrange`, where the last clamps the total across all actuators on a joint. Implications for our exploits (4) and (3): penetration of 0.27–0.57 m points to too-soft solref/solimp for the masses involved, or a too-large timeconst or timestep. Per-joint `actuatorfrcrange` gives a hard cap on joint torque that the gear rule cannot scale around.

### Collins, Chand, Vanderkop, Howard 2021 — Review of physics simulators
- **Citation:** Collins J, Chand S, Vanderkop A, Howard D. "A Review of Physics Simulators for Robotic Applications." *IEEE Access* 9:51416–51431, 2021. doi:10.1109/ACCESS.2021.3068769.
- **How verified:** Crossref; Semantic Scholar abstract.
- **Summary (abstract):** A broad review of physics simulators by robotics subdomain, covering features, benefits and use cases, meant to help researchers pick a simulator. I did not read the body, so I cannot say what it covers on contact accuracy or exploits.

### Leike et al. 2017 — AI Safety Gridworlds (optional)
- **Citation:** Leike J, Martic M, Krakovna V, Ortega PA, Everitt T, Lefrancq A, Orseau L, Legg S. "AI Safety Gridworlds." arXiv:1711.09883, 2017.
- **How verified:** arXiv abstract page.
- **Summary:** Each environment has a performance function hidden from the agent, which separates specification problems (reward differs from the performance function, including "reward gaming") from robustness problems. It is only marginally relevant, as a conceptual precedent for scoring evolved bodies on a hidden "intended behaviour" metric separate from fitness.

### Manheim & Garrabrant 2018 — Categorizing variants of Goodhart's law (optional)
- **Citation:** Manheim D, Garrabrant S. "Categorizing Variants of Goodhart's Law." arXiv:1803.04585, 2018.
- **How verified:** arXiv abstract page.
- **Summary:** The paper distinguishes several mechanisms by which optimising a proxy metric fails: regressional, extremal, causal and adversarial, following Garrabrant's "(at least) four different mechanisms". It stresses that Goodhart effects grow with the optimisation power applied to the proxy. Physics exploits are best read as **extremal** Goodhart: evolution pushes bodies into regimes such as huge masses, large penetrations, and falls from height where the simulator stops approximating reality. (This mapping is my own interpretation, not the paper's.)

---

## UNVERIFIED

- **Clark & Amodei 2016, "Faulty reward functions in the wild" (OpenAI blog).** The URL https://openai.com/index/faulty-reward-functions/ appears in search results under this title, but the page returned HTTP 403 to both WebFetch and curl, and web.archive.org is blocked here. I could not confirm authors or date from the record itself. Secondary summaries say December 2016 and describe the CoastRunners boat circling a lagoon to re-hit respawning targets, which Krakovna's 2018 post also describes as the "OpenAI boat racing" example. Reason: primary page not readable.
- **Jakobi et al. 1995: content details.** The bibliographic record is verified (above), but the Khepera, obstacle-avoidance and noise-level details come only from search-engine summaries. The full text was not accessed.
- **Moore & McKinley on energy.** Not searched to a confirmed record in this pass. I did not attempt to identify the specific paper.
- **Hornby's physical constraints; Samuelsen & Glette; "Ruud, Samuelsen & Glette 'Exploring…'".** No confirmed record found or pursued. The title given is incomplete.
- **Ventrella (virtual creatures).** No specific paper identified in the brief, and none verified.
- **Hiller & Lipson 2012 "including cost/energy".** The paper is verified, but the claim that it includes cost or energy terms is not supported by the abstract. The body was not read.
- **Miconi & Channon "fixes to Sims' reimplementation / preventing exploits".** The 2005 CEC paper is verified, but whether it describes exploit fixes is unverified because the full text was inaccessible.
- **Chaumont et al. 2007: any exploit/constraint discussion.** Only the abstract was read.
- **Peng et al. venue (ICRA 2018) and Tobin et al. venue (IROS 2017).** Only the arXiv records are verified.
- **Krcah 2008: LNCS volume number 5216.** Consistent with ICES 2008, but not seen on an opened record. Crossref gives LNCS and pp. 153–164.
- **General "MuJoCo contact exploits in RL locomotion" literature.** Apart from Baker et al. and the Krakovna blog's leg-hooking walker, I did not find and verify a dedicated paper on penetration exploits in MuJoCo RL.

---

## What did others do about exploits?

Citing only the verified items above, the fixes fall into seven groups.

**Energy and actuator budgets.** Sims (1994) capped each joint effector at a maximum strength proportional to the cross-sectional area of the parts it joins. Strength then scales with area while mass scales with volume, so strength does not grow for free with size. He also proposed distance per unit energy as a fitness measure. Cheney et al. (2013) multiplied fitness by penalties on voxel count and on the amount of actuated ("muscle") material; evolution adapted with little loss of performance but changed body plans. Lessin et al. (2013) gave each muscle an explicit maximum strength. Nygaard et al. (2018) showed that evolution adapts morphology and control to a fixed, externally imposed torque and speed limit. Taylor & Massey (2001) found that force limits alone did not stop creatures driving the solver into instability. For our exploit (3), this literature favours tying actuator capacity to something that grows more slowly than mass (Sims's area rule), or to a fixed total budget, over a per-DOF multiple of mass. MuJoCo's per-joint `actuatorfrcrange` enforces such a cap in the engine.

**Conservative physics and timestep.** Sims replaced Euler with adaptive Runge-Kutta-Fehlberg after swimmers harvested integration error, and shrank the timestep to keep new penetrations under a tolerance (Sims 1994; Lehman et al. 2020). Cheney's team fixed the VoxCAD ground-penetration exploit by raising contact damping, raising the minimum body size, and changing the timestep rule to reduce penetration (Lehman et al. 2020). Taylor & Massey (2001) noted the stability-versus-speed trade-off of step size and added runtime stability checks, aborting any creature that triggered solver warnings or showed "explosion" velocities. EvoGym limits spring strain (Bhatia et al. 2021). Lipson & Pollack (2000) used a quasi-static, energy-minimisation simulator that is conservative by design (per Taylor & Massey's table). In MuJoCo, penetration depth is set by solref/solimp relative to the timestep (MuJoCo docs), so exploit (4) calls for stiffer contact parameters, a smaller timestep, and a penetration monitor.

**Body-model constraints and validity checks.** Sims (1994) removed creatures above a part-count limit and discarded those with persistent initial interpenetration. Taylor & Massey (2001) capped parts at 4–10. Krcah (2008) pre-screened genotypes for self-penetration, too-small parts and too many parts, re-running variation until a valid body appeared. EvoGym uses a fixed voxel grid and requires a connected body with at least one actuator (Bhatia et al. 2021). These correspond to our mass budget for (1) and suggest adding pre-simulation checks, such as minimum part size, a self-penetration test, and capping total actuator capacity alongside mass.

**Controlling initial conditions and transients.** Sims (1994) ran the creature with no friction and no effector forces until its centre-of-mass height reached a stable minimum, then began scoring. This directly counters falling as locomotion and is the fix for our spawn-drop exploit (2). Lehman et al. (2020) report that Cully et al. ignored the first few tenths of a second. Sims also up-weighted late-phase velocity so continued movement beat a single initial push.

**Noise and reality-gap methods.** Jakobi (1997) varied non-task-relevant simulation features at random so that controllers cannot depend on them, and argued that simulations built this way transfer even when inaccurate. Koos et al. (2013) added a second objective, estimated transferability (disparity between simulation and reality), because the fittest simulated solutions "often exploit badly modeled phenomena". Peng et al. (2017/18) randomised dynamics for sim-to-real RL.

**Evaluating in multiple conditions.** This follows from the reality-gap methods above. Randomised dynamics (Jakobi 1997; Peng et al.) or a disparity objective (Koos et al. 2013) penalise solutions that work under only one simulator setting. A sim-only project can use a second, more conservative simulator configuration as its "reality" reference.

**Judging behaviour directly rather than trusting the number.** Lehman et al. (2020) advise an adversarial mindset and regularly visualising solutions. Krcah's pole-vault cheat and the Feldt overflow were found only by inspection. Amodei et al. (2016) recommend trip wires, reward capping and careful engineering. Leike et al. (2017) separate a hidden performance metric from the reward, and Krakovna et al. (2020) frame these failures as abstraction failures rather than bugs. For us, this means automated detectors (maximum penetration, centre-of-mass speed in the first second, energy input versus kinetic and potential energy) plus routine video review of champions.
