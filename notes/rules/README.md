# Official rules (archived)

This folder stores **downloaded / transcribed** rule sources for SM64 TAS and RTA work.

| File | Source |
|------|--------|
| `tasvideos-MovieRules.md` | [tasvideos.org/MovieRules](https://tasvideos.org/MovieRules) (summary + key quotes) |
| `tasvideos-MovieRules-raw.txt` | Full page text dump |
| `tasvideos-Mupen-raw.txt` | [EmulatorResources/Mupen](https://tasvideos.org/EmulatorResources/Mupen) |
| `speedrun-com-categories.txt` | SRC API categories for `o1y9wo6q` |
| `speedrun-com-variables.txt` | SRC API platform/codes variables |
| `../rules-and-decomp.md` | **Combined guide**: rules + decomp optimization notes |

**Refresh (from repo root):**

```bash
# TASVideos (HTML → text; may need re-scrape if Cloudflare blocks)
curl -sL "https://tasvideos.org/MovieRules" -o /tmp/mr.html
# SRC API (stable JSON)
curl -sL "https://www.speedrun.com/api/v1/games/o1y9wo6q/categories" -o notes/rules/speedrun-com-categories.json
curl -sL "https://www.speedrun.com/api/v1/games/o1y9wo6q/variables" -o notes/rules/speedrun-com-variables.json
```

Always re-check live pages before submitting a run; rules change.
