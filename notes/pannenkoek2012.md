# Notes: pannenkoek2012 (UncommentatedPannen)

**Role in the community:** The definitive deep-dive educator for Super Mario 64 engine mechanics, best known for the **A Button Challenge (ABC)** and the viral “half A-press” series. Work spans commentated and uncommentated technical videos, often multi-hour explorations of a single star or mechanic.

**Primary resources:**
- YouTube: [pannenkoek2012](https://www.youtube.com/@pannenkoek2012) / UncommentatedPannen
- Wiki knowledge base: [Ukikipedia](https://ukikipedia.net/wiki/Main_Page) (community; heavily informed by pannenkoek-style research)
- History of ABC: [Ukikipedia – History of the A Button Challenge](https://ukikipedia.net/wiki/History_of_the_A_Button_Challenge)

---

## Core concepts introduced / popularized

### 1. A presses and “half” A presses
- An **A press** is a discrete press of the jump button, tracked for the ABC (minimize total A presses to complete the game or a star).
- **0.5 A press (“half A press”)** means Mario *enters* the level (or continues) with A already held from a previous context. That half-press can be “shared” across levels in a full-game ABC run, but counts as a full press for IL (individual level) scoring if A must be held at entry.
- Famous example: *Watch for Rolling Rocks* in Hazy Maze Cave completed with **0.5 A presses** (later improved to **0 A presses** with newer tech such as “Mario’s Platform Adventure”).

### 2. Parallel Universes (PUs)
- Floor/ceiling collision casts Mario’s float position to a **signed 16-bit integer** (`short`), range **−32768 … 32767**.
- Positions outside that range **wrap** (integer overflow). Collision is computed as if Mario were still inside the main map’s coordinate window.
- Result: an infinite grid of **phantom copies** of floor/ceiling geometry — **Parallel Universes**.
- PUs typically lack walls, water, and most objects; some special objects (e.g. castle paintings) can still exist.
- **QPU (Quadruple Parallel Universe):** displacement of \(2^{18}\) units (four PUs of \(2^{16}\)). Useful speeds for controlled PU travel are often integer multiples of 1 QPU of speed so Mario “lands” on consistent lattice points.

### 3. Hyperspeed building techniques (ABC toolkit)
| Technique | Idea |
|-----------|------|
| **BLJ** | Unlimited *negative* speed via interrupted long jumps (stairs, slopes, elevators, low ceilings, side BLJs). |
| **HSW (Hyperspeed Walking)** | Build extreme forward speed on certain surfaces over long periods (often hours in early ABC). |
| **Scuttlebug raising** | Manipulate scuttlebug clone/home behavior to raise platforms or create collision useful for routing. |
| **Bully battery** | Bully knockback multiplies speed; used for extreme hyperspeed (e.g. LLL). |
| **Misalignment / HOLP** | Held-object last position and misaligned geometry enable clips and clever object setups. |

### 4. Geometry & collision (video series)
UncommentatedPannen series to internalize:
- **Walls, Floors & Ceilings** (parts 1–3)
- **Wall hitboxes**
- Related: Timestoppa — walls/floors/ceilings **in Parallel Universes**

Key mental model:
- Collision is triangle-based; floors, walls, and ceilings are separate surface types with different rules.
- **Quarter steps:** Mario’s position updates in up to **4 substeps per frame** on ground/air — critical for frame-perfect TASes and understanding how clips/bonks resolve mid-frame.

### 5. Units, speed, and frames
- Game runs at **30 FPS** for gameplay logic (1 frame ≈ 1/30 s).
- **Speed** = units of position change intended per frame (horizontal and vertical are handled differently).
- Horizontal movement has acceleration caps (e.g. air/long jump accelerate toward caps, then often **0.15 u/f** beyond convergent caps for some states).
- Many actions have **absolute** vs **convergent** speed caps (see TASVideos Game Resources / Ukikipedia).

### 6. Philosophical / practical ABC lessons
- **Optimization is multi-layered:** fewer A presses can cost hours of real time (hyperspeed grinding). ABC optimizes button presses, not wall-clock speed.
- **TAS is a research tool:** frame advance, savestates, and RAM tools (STROOP) make theory testable.
- **Engine “bugs” are features:** integer casts, missing speed clamps, and object interaction order are the design space.

---

## Landmark videos (starting list)

| Topic | Video / notes |
|-------|----------------|
| Watch for Rolling Rocks 0.5× A | Classic commentated PU / HSW / scuttlebug primer ([YouTube](https://www.youtube.com/watch?v=kpk2tdsPh0A)) — later outdated by 0 A methods |
| Watch for Rolling Rocks 0 A | 2023 update using newer platform tech |
| Walls / floors / ceilings series | UncommentatedPannen — required reading for TASers |
| A Button Challenge history | Playlist + Ukikipedia history page |

---

## Implications for this TAS project

1. **Use STROOP + Mupen** to observe: position (float), floor-check short coords, horizontal speed, action, camera mode, object slots.
2. When routing any% style speed, prefer **fast hyperspeed** (BLJ, pause-BLJ) over ABC-style multi-hour HSW unless the category demands it.
3. When routing ABC / low A, treat **PU lattice math**, **HOLP**, and **object manipulation** as first-class tools.
4. Always note **region** (J vs U): textboxes, lag, and some glitches differ; many ABC and some any% segments use **Japanese**.

---

## Further reading
- [Ukikipedia – Parallel Universe](https://ukikipedia.net/wiki/Parallel_Universe) (if page title differs, search “Parallel Universe”)
- [TASVideos Game Resources – SM64](https://tasvideos.org/GameResources/N64/SuperMario64)
- Wikipedia: [pannenkoek2012](https://en.wikipedia.org/wiki/Pannenkoek2012)
