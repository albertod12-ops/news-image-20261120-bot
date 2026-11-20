# news-image-20261120-bot

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/albertod12-ops/news-image-20261120-bot/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/albertod12-ops/news-image-20261120-bot/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Friday 20 November 2026: 36 stories, 6 regions, one picture — an entry for the [make.fun bounty](https://make.fun/bounty/news-image-20261120) "Sum up 20 November's world news in one image".

The program is `main.py` (Python 3.13). It copies the finished front page, `entry.png` (1024x1024, under 1 MiB), to the grader's output directory, byte for byte, with no network access and no randomness. Run it twice and both runs write the same bytes.

The front page is built by `draw.py` (Pillow, a world map from `world.geo.json`): a navy masthead, three hero stories with flat-vector illustrations (Cyclone Akvan's landfall in Odisha, Russian missiles striking Kyiv's bridges, COP31's final-day fossil-fuel deadlock), ten small cards with pictures (the AI sell-off, the UK-EU reset deal, the Myanmar genocide ruling reactions, Europe's cost-of-living strikes, Iraq's move on a militia stronghold, Israeli tanks crossing the Gaza truce line, the An-12 crash in Siberia, Sri Lanka's rate hike, the California quake, Mamdani's plan to close Rikers Island), a BY THE NUMBERS strip, a world map with numbered pins, and 23 more stories. Every story happened, or was first reported, on Friday 20 November 2026. Sources: Reuters, AP, AFP, IMD, ICJ, UNFCCC, USGS. Original illustrations.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=rbvcjbg9&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
