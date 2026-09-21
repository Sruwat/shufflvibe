# Card set V10 — six preference cards, seven vibe factors with two cards each

**Supersedes `CARD_SET_V9_IMAGE.md`** (2026-09-17). Two decks now. The wording under each card is
what the *image* has to convey — it is not caption text. Images are placeholders until the final
set is decided (`REMINDERS.md`). `CARD_READABILITY.md`'s five rules apply to every card here.

---

# 1. The preference deck — onboarding, once

Shown before the vibe deck, on the person's first day, and again only if they choose to redo it
from the profile. One card per preference; no second card — importance is not ambiguous the way a
scene is. The screen before it:

> **Swipe on the following things on the basis of how important they are to you in a place.**

The four swipes, same gestures and colours as the vibe deck, **reworded for importance**:

| swipe | label | colour | score | means |
|---|---|---|---|---|
| up | **The whole point** | gold | 88 | fine as the sole focus of a night |
| right | **Nice to have** | green | 62 | |
| left | **Don't mind** | grey | 38 | |
| down | **Don't care** | red | 12 | irrelevant — *not* an aversion |

Each card is **the thing itself**, plainly, with nothing else competing for the eye:

| id | Preference | The image conveys |
|---|---|---|
| `P-FOOD` | `FOOD` | a plate that is clearly the point — a full table, the food in focus, nothing else in the frame |
| `P-LIVE` | `LIVE` | a band or an act on a small stage, lit, a few heads in front — the performance is the room |
| `P-POL` | `POL` | a polished room — good light, dressed people, a bar that has been designed |
| `P-POL-S` | `POL` sense | **an image pair, tap one:** a suits-and-dresses room · a streetwear-and-sneakers room — *"which of these is dressed-up, to you?"* — answer `classy` / `current`; a third tile *both* |
| `P-SCEN` | `SCEN` | a beautiful room or terrace, the look doing all the work — the eye goes to the place, not to people |
| `P-NOV` | `NOV` | an unmarked door, a lane, a place none of you has been — the image is *not knowing what is inside* |
| `P-HERIT` | `HERIT` | old stone, a courtyard, a building that has been there far longer than anyone in it |

Seven taps, one of them a pair. Three minutes. Stored on the profile; editable any time.

---

# 2. The vibe deck — every day

Seven factors, each with an **A** card and a **B** card, both poles present in each image so that
a swipe toward either end reads as a want. The adaptive rule (`ASSESSMENT_ENGINE.md` §2.2)
stands: an extreme swipe ends the factor, a mild one adds the B card at least three positions
later. Seven to fourteen cards. Swipes: **LOVE / UP FOR IT / NOT FOR ME / HARD PASS** — a hard
pass on a vibe card is a firm *low pole*, and it is a want.

| id | Factor | Card A conveys | Card B conveys |
|---|---|---|---|
| `V-ENRG-A` | `ENRG` | a night that is clearly *building* — the room at eleven, fuller than at nine, heading somewhere | the same room at one, still going, nobody leaving |
| `V-ENRG-B` | | a calm night — low light, a slow room, the night at its level and staying there (the low pole shown as a *want*) | |
| `V-AFFIL-A` | `AFFIL` | your own people at your own table, the rest of the room out of focus | strangers at the bar, two of them turning to talk to you — the room, not the table |
| `V-AFFIL-B` | | a booth, the door closed behind you | the floor, the crowd, everyone facing out |
| `V-CROWD-A` | `CROWD` | the fullest room in the city, and you are in it | a near-empty room, three tables, yours |
| `V-CROWD-B` | | a queue at the door, and you want to be inside | a place you have to yourself |
| `V-TALK-A` | `TALK` | a table where everyone is mid-sentence — the night *is* the conversation | speakers, bass, nobody trying to talk |
| `V-TALK-B` | | leaning in to hear a story | mouthing across a dance floor |
| `V-ROAM-A` | `ROAM` | three places in one night — a door, a road, another door | one place, coats off, all night |
| `V-ROAM-B` | | the car between stops, the next place lit ahead | a table you never leave |
| `V-MOVE-A` | `MOVE` | on your feet — a floor, a lawn, people moving | sat down, settled, no intention of standing |
| `V-MOVE-B` | | a dance floor from inside it | the deepest seat in the house |
| `V-GAMES-A` | `GAMES` | a pool table, darts, a bowling lane — something to play, mid-game | nothing to fiddle with, just the table and the people |
| `V-GAMES-B` | | an arcade bar, a scoreboard, a turn being taken | a bar with nothing on the table but drinks |

For the two-ended factors each card *shows both poles* — one in focus, one implied — so that
*love* and *hard pass* both read as choosing a side rather than approving or rejecting a
picture. `GAMES` is the exception in spirit: its low pole is weak (`FACTORS_V5.md` §2), so its
cards lean on the high pole and a hard pass reads as "not tonight".

**Retired cards:** everything under `FOOD`, `LIVE`, `HERIT`, `NOV`, `SCEN`, `POL` in V9 — those are
now preference cards, once. `PLAY`'s cards are replaced by `GAMES` and `MOVE`.

---

# 3. The reveal, and the profile

After the vibe deck: **Your vibe today is — [Name]** (`VIBE_NAMES_V4.md`), then the description.
No badges on the reveal. On the profile: the name, then the badges, then the preferences as an
editable row of six.

---

# 4. QA

Same as V9: for each card, the share of people who swipe it opposite to their other card for the
factor (`ASSESSMENT_ENGINE.md` §6.4 once latency is validated; pair disagreement before). The
new factors' cards have no history; watch `TALK` and `ROAM` especially — they are the ones a
picture may fail to carry.
