# 6COM2012 – Worksheet 1: Co-existing Agents

Pure Python (3.8+), **no external packages**. Grid worlds with agents:

* **Part 1** – 3×3 wrap-around world, 3 agents, conflicts are cancelled moves
* **Part 2** – 5×5 "Platform Royal", agents push each other, losers fall off
* **Challenge** – an intentionally antagonistic `Hunter` agent that clears the platform

## Project layout

```
worksheet1/
├── main.py                  command-line entry point
├── requirements.txt         (nothing to install)
├── worksheet/               reusable library
│   ├── geometry.py          positions, directions, nearest-edge helpers
│   ├── agent.py             Agent + Event data classes
│   ├── patterns.py          movement patterns (clockwise, diamond, left, random, Hunter)
│   ├── worlds.py            GridWorld base, WrapWorld (Part 1), PushWorld (Part 2)
│   ├── render.py            ASCII drawing of the grid
│   └── analysis.py          conflict statistics + cycle detection
├── experiments/
│   ├── part1.py             Part 1 set-up, run and report
│   └── part2.py             Part 2 scenarios (3 runs), run and report
└── tests/                   25 unit tests
```

Coordinates are `(row, col)`; `(0, 0)` is the **top-left** corner.

## Step-by-step: run it

1. **Part 1:** `python main.py part1`
2. **Part 2:** `python main.py part2`
3. **Challenge:** `python main.py part2 --hunter`
4. **Everything at once:** `python main.py all`

### Useful options

| Command | Effect |
|---|---|
| `python main.py part1 --steps 80` | run longer |
| `python main.py part1 --show` | draw the grid after every step |
| `python main.py part1 --start-order Left,Clockwise,Diamond` | change who enters first (t = 0, 2, 4) |
| `python main.py part1 --move-order Left,Diamond,Clockwise` | change who moves first each round |
| `python main.py part1 --retry-blocked` | blocked agent waits and retries the same move (leads to deadlock!) |
| `python main.py part2 --show` | draw the 5×5 grid every step |
| `python main.py part2 --quiet` | hide the push/removal log, show only results |

## Results with the default settings

**Part 1 (50 steps):** 25 conflicts. A short transient (first repeated state after step 31) is followed by an
**8-step cycle with 2 conflicts per cycle**, and in that cycle it is always `Left` that gets blocked
(by `Diamond` at (0,0), by `Clockwise` at (0,1)). Because the system is deterministic and finite, conflicts must eventually become periodic.

**Part 2 (100 steps, 4 agents):**

| Run | Remaining | Who |
|---|---|---|
| 1 | 2 | Clockwise, Diamond |
| 2 | 1 | Clockwise |
| 3 | 1 | Diamond |

**With the Hunter (5 agents):** 1 remains in all three runs (the Hunter).

Your own numbers should match these exactly, since every run is deterministic.
