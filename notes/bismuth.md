# Notes: Bismuth (bismuth9)

**Role in the community:** Popular explainer of **tool-assisted** Super Mario 64 records for a general audience. Videos break down multi-author collaborative TASes with clear routing chapters, technique names, and “why this looks impossible” intuition — complementary to pannenkoek’s engine-deep dives.

**Primary resources:**
- YouTube: [Bismuth](https://www.youtube.com/@Bismuth9)
- Patreon: https://www.patreon.com/bismuth9
- Twitch: https://www.twitch.tv/bismuth9
- Landmark any% explainer: [SM64 Tool-assisted speedrun WR explained](https://www.youtube.com/watch?v=wjge1bVobN0) (~4:20 era 1-key style routing)
- Ongoing: [120 Star TAS Explained series](https://www.youtube.com/watch?v=XFHMhNjtPmQ) (star-by-star)
- ABC history series: [Complete History of the SM64 A Button Challenge](https://www.youtube.com/playlist?list=PL94lfiY18_CgWGQzweD_aVjsFXiRi6kn5)

---

## What Bismuth’s explainers emphasize (TAS any% / 1-key)

### Route evolution (from the any% explainer framing)
1. **70 stars** — “Bowser demanded it” (keys + star doors as intended gates).
2. **16 stars** — MIPS rabbit clip through the 30-star door.
3. **1 star / 0 stars / 2 keys** — progressive skip discovery.
4. **1 key** — modern pure-speed goal: get the basement key and finish with maximum glitch abuse; almost no “normal” play remains.

Collaborative credit in landmark TASes often includes: **mkdasher, sonicpacker, snark, SilentSlayers, ToT, Tyler_Kehne, Superdavo0001, IsaacA, pannenkoek2012** (research), and many others.

### Signature techniques explained in any% context

| Technique | Bismuth-style takeaway for TASers |
|-----------|-----------------------------------|
| **BLJ** | Long jump multiplies speed by ~1.5; **negative** speed has **no hard cap** → repeated interrupted long jumps build insane reverse speed. |
| **Pause buffering / Pause BLJ** | Pause menu lets you inject extra A presses relative to game time; more BLJs per real second of in-game clock on valid surfaces. |
| **Quarter steps** | Position resolves in substeps; TASes exploit mid-frame collision (clips, precise landings). |
| **Negative jump / speed storage** | Preserve negative or special speed across water exits (e.g. Z to exit water) and stage transitions. |
| **VCUtM elevator BLJ → Castle Grounds** | Build QPU-scale speed in Vanish Cap under the Moat, die to death barrier, retain speed into castle grounds for moat-door / PU setups (classic 0-star / 1-key era tech). |
| **PU door open** | Empty water in PU lets Mario *run* into the moat door (underwater in real map blocks this); fixed camera + R can avoid console freezes historically associated with PUs. |
| **BitFS / BitDW skips** | Extreme movement and clips collapse Bowser stages. |
| **Lag management** | Camera, objects, and text affect frame timing; TASes optimize lag as carefully as movement. |

### 120 Star TAS explainers (series)
- Treat each star as a **mini optimization problem**: entry angle, coin routes, enemy cycles, BLJ vs pure movement, text skip rules.
- Star 1 (BoB) often reintroduces:
  - Optimal running / diving / single-frame dust avoidance
  - Iconic BLJ uses (e.g. chain chomp gate, wing cap skip contexts in other stars)
  - How RTA strats and TAS strats diverge (TAS can use multi-hour setup only when it saves end time; 120 prefers *time*, not A presses)
- Additional notes doc (linked by Bismuth for the 120 series):  
  https://docs.google.com/document/d/1jVsd5qwnA3uR_oPdK-7vuIccVmr_b-4EirMFMsIs6Js/

### ABC history series
- Bridges **pannenkoek-era research** and public understanding: Pannenkoek Revolution → goomba clusters → PU routing → modern 0 A press breakthroughs.
- Useful for this repo when branching into **ABC TASes** vs pure speed categories.

---

## Practical checklist from Bismuth-style analysis

When studying an existing `.m64` / encode:

1. **Identify category constraints** (1-key, 16-star, 70 no BLJ, 120, ABC).
2. **Mark hyperspeed sources** (which BLJ type? elevator? side? pause?).
3. **Mark transition tech** (speed storage through water, painting entries, door clips).
4. **Note region** (J textboxes shorter; many modern any% TASes are **J**).
5. **Compare lag** — a “slower” looking segment may save lag frames globally.
6. **Read submission notes** on TASVideos (authors document frame saves).

---

## Key linked TASes (see `tas/` in this repo)

| Category | TASVideos | Local path |
|----------|-----------|------------|
| 1 Key ~4:18 | [4490M](https://tasvideos.org/4490M) | `tas/full-game/1-key/` |
| 120 Stars ~1:20:41 | [2208M](https://tasvideos.org/2208M) | `tas/full-game/120-stars/` + archive |
| 70 Stars no BLJ | [2062M](https://tasvideos.org/2062M) | `tas/full-game/70-stars-no-blj/` |
| 16 Stars | [6943M](https://tasvideos.org/6943M) | `tas/full-game/16-stars/` |

YouTube encodes (for visual study without emulator):
- 1 Key style explainer source TAS era: see Bismuth’s linked TAS in video descriptions
- 120 Star full: often linked as companion to the star-by-star series (e.g. `mVwQD1jTERA` / TASVideosChannel uploads)

---

## How Bismuth + pannenkoek fit together

| | **pannenkoek2012** | **Bismuth** |
|--|--------------------|-------------|
| Focus | Engine truth, ABC, collision theory | Route narrative, WR explainers, accessibility |
| Best for | “Why does the memory do this?” | “Why did the TAS go here next?” |
| Use in this repo | Mechanics notes, ABC branch | Category routing notes, public WR study |

---

## Ideas inspired by these explainers (also in main README)

- Rebuild a **segmented 1-key** learning TAS with modern Mupen + SM64 Lua Redux overlays.
- Port hard-to-read old `.m64` notes into timestamped markdown per stage.
- Cross-check archive IL WRs against full-game 120 for **inconsistency / improvement** opportunities.
- Automate “BLJ count / pause-BLJ detection” scripts over `.m64` using MupenSharp or a custom parser.
