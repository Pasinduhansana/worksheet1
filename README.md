# 6COM2012 – Worksheet 1: Co-existing Agents

Pure Python (3.8+), **no external packages**. Grid worlds with simple agents:

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
└── tests/                   25 unit tests (unittest, no pytest needed)
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

## Step-by-step: validate it

1. **Run the automated tests** (from the `worksheet1` folder):
   ```
   python -m unittest discover -s tests -t . -v
   ```
   Expected last lines: `Ran 25 tests ... OK`.
2. **Check Part 1 by eye** – `python main.py part1 --steps 6 --show`:
   * `C` (Clockwise) appears on the red field `*` at t=0, `D` at t=2, `L` at t=4 → *two time-steps apart*.
   * `C` walks the outer ring, `D` jumps diagonally, `L` moves left and re-enters on the right side → *wrap-around*.
   * Every `CONFLICT` line prints the field and the two agents involved, and the mover stays where it was → *cancelled move*.
3. **Check "do you see a pattern?"** – the summary at the end of `python main.py part1`
   reports when the whole world state first repeats and which conflicts occur in one period.
4. **Check Part 2 by eye** – `python main.py part2 --steps 3 --show`: when an agent moves into another, the other agent shifts one field in the same direction (see `PUSH` lines); `OUT` lines mean an agent left the grid for good.
5. **Check the survivors table** at the end of `python main.py part2` – 3 runs, 100 steps each, with the number of agents remaining.
6. **Check the challenge** – `python main.py part2 --hunter` should leave only `Hunter` in every run.

## Design decisions (worth mentioning in your write-up)

* **Cancelled move = lost move (default).** When a move is cancelled the agent stays, but its pattern still advances. The alternative (`--retry-blocked`) makes an agent wait and retry the same move. With retry, the three agents deadlock around the red field and the world freezes (state period 1) – a nice side-finding.
* **Entering the world.** An agent that wants to enter on the red field while it is occupied is delayed and logged as a conflict.
* **Move order matters.** Agents move one after another within a round; earlier agents win contested fields. `--move-order` lets you test this.
* **Diamond (Part 1).** Counter-clockwise diamond = down-left, down-right, up-right, up-left. On the 3×3 torus this closes after 4 moves: (0,0) → (1,2) → (2,0) → (1,1) → (0,0).
* **Push rule (Part 2).** Pushes chain: pushing an agent that stands in front of another pushes both. A pushed agent that is shoved over the edge is removed for good. The pusher moves into the freed field.
* **Randomness.** The random walker is seeded per scenario, so results are reproducible.
* **Hunter (challenge).** Intentional antagonism through *new capabilities*: it sees all agents and reads each victim's pending move. It targets the agent nearest an edge and stands directly behind it, on the side opposite that edge, then pushes. A purely reactive version got stuck chasing the Diamond agent forever in Run 1; predicting the victim's next position fixed that.

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
