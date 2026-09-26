# RBT-96 adversary, item 6: the reach of "a seed is an artifact of its platform"

## What RBT-96 established

- **4/4 seeds** (201–204): s0 on the cloud diverges from RBT-85's `base-SEED` on the laptop at generation 0. The configuration is the same byte for byte, and so are the terrain and start seeds. The committed rows show it (`readout.txt` §5).
- On x86, MuJoCo 3.13.0 and 3.14.0 agree for generations 0–2. This rests on the delegate's 12:37 UTC cost comment; the probe was a scratch run and is **not committed**.
- Generation 0 is founders only, and the numpy streams are identical: the terrain draws in `test_salt0_golden.py` equal the committed terrain seeds. So the divergence is in the physics float path. It is not in the RNG.

This is **"these two platforms, arena, every seed tried"**. It is not "any two machines".

## What this adversary adds

1. **x86 container to x86 container reproduces, arena.** This session ran on an Intel Xeon @ 2.80 GHz, x86_64, Python 3.11.15, MuJoCo 3.14.0, numpy 2.4.6. It is not the delegate's container. Here, gen 249's champion round robin, replayed on its own terrain seed, equals `history.json` to 1e-12 in both arms of all four seeds (`champions.txt` section B, "EXACT").
2. **x86 to x86 reproduces, ecology.** This comes from the record, not from a new run. RBT-92's shared-baseline sha256 (`6018e0a9f5ec7965`, seed 801) agrees across at least five cloud sessions: the RBT-92 designer and adversary, RBT-100, and RBT-101 plus its adversary. RBT-84's "across machines" reproduction was also cloud to cloud. **No ecology run has ever been compared between ARM and x86.** The ecology steps the same `mujoco.mj_step`, and income comes from physics. So the platform effect is **untested for the ecology, not refuted**.
3. **No ecology comparison in the programme crosses platforms.** Here is where each arm ran, from ticket launch comments and commit trailers (laptop commits are `Ethan Jucovy -0400` with no `Claude-Session` trailer; cloud commits are `Claude +0000` with the trailer):

| ticket | arms, and the controls cited | platform |
|---|---|---|
| RBT-90 part 2 | 10 forage-SEED arms (seeds 1–4, 7, 801, 804–807) and the workers 1/4 check | cloud x86, one session per seed (coordinator ruling in 8ec1c76). The laptop commits of 09-19 are instruments and head-direction founder files; no readout reads them |
| RBT-92 | shift (session A) and cull20/cull (session B) arms for all 10 seeds; baseline = RBT-90 forage-SEED | cloud x86. The description's "owner's laptop (M4)" was superseded on 09-26 |
| RBT-99 | shift/cull ×10; cull20 and baseline cited from RBT-92/RBT-90 | cloud x86 |
| RBT-100 | founders6→shift→cull ×10; cull20 and baseline cited | cloud x86 |
| RBT-101 | shift→cull ×10; baseline cited | cloud x86 |
| RBT-104 (design) | K = 1 byte-identity against RBT-90 forage-801 | cloud x86; the coordinator's 17:02 condition 3 makes it binding |

**One residual gap.** The members of each pair run in *different* cloud containers. `config.json` records no platform, CPU or MuJoCo version, so "same x86 type" is inferred from repeated agreement, not recorded. The arena replay in (1) and the five-session ecology hash agreement are the evidence that it holds today.

## Consequences

- **"Seed-paired arms must share a platform" holds** as a design rule. It is cheap and correct.
- **"A seed is an artifact of its platform" is established for ARM M4 against x86 in the arena**, and it is plausible for the ecology.
- **Among the cloud's x86 containers it is refuted as far as tested**: arena replay here, and ecology hashes across five sessions.
- **The one comparison it breaks is laptop to cloud**, and within the programme that is **RBT-85 against RBT-96**. RBT-96's §4 reads RBT-85's A/B d (laptop) against this A/A null (cloud). That is a comparison of *spreads across designs*, which is legitimate across platforms. It is not seed-paired. But the seed-level opponent covariate does **not** transfer: seed 201's wheeled side is a runaway on the laptop and a driver on the cloud. So any per-seed juxtaposition of the two tickets (RBT-85 seed X beside RBT-96 seed X) is unpaired.
- **The proposal to record `platform.machine()` and `mujoco.__version__` in `config.json` should go further.** Add the CPU model string and numpy's version too, because the only platform pair shown to diverge differs in the CPU as well as the ISA.
