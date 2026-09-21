# Simulations

Python 3, no dependencies. Each file is the rules of its day run on imaginary rooms and a small
venue pool; the traces they print are the ones quoted in `decisions/DECISIONS.md`.

| File | Model | Status |
|---|---|---|
| `design3.py` | Chemistry V2 on the designed night: one-way energy, the talk floor, Table and Floor, Common Ground, stop durations, the tags (`specs/CHEMISTRY_V2.md`) | **current** |
| `examples.py` | one room per chemistry state, plus the band, friends and solo, on `design2.py` | current |
| `design2.py` | `design.py` plus the extremes-only bend rule (§14.3.1a, 2026-09-18) | **current** |
| `design.py` | the designed night: every member's top vibe factor at every stop, maximin over types, a strong #2 standing in for a firmly opposed top, no debt, no dedicated stops; chemistry from how the design went (§14.3 v4, 2026-09-18) | **current** |
| `compose.py` | compose-first, then compromise on a collision (§14.3 v3, superseded the same day) | history |
| `splitsim.py` | the split factor set — seven vibe axes, ten venue types, the ROAM negotiation, a fill stage on six preferences; now Phase B of `compose.py` | current (as Phase B) |
| `friendsim.py` | debt / payback across stops, overall firmness, friend mode, on the ten-factor scale (§13.4c, §13.8, §13.9) | history |
| `joinsim.py` | the joiner's gate and match, room-level payback and chemistry, on the ten-factor scale (§13.6) | history |
| `debtsim.py` | the first debt / payback model (§13.4c as of 2026-09-17 morning) | history |

Run one with `python design3.py`. Add a room at the bottom of the file to try a scenario; the
venue pool is small and authored, so a preference that goes un-had is as often a gap in the pool
as a rule.
