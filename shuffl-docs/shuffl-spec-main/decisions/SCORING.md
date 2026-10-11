# The scoring index

**SHUFFL has seven scorers, not one.** That is the answer to "where is the scoring algorithm" — it
is pushed, in full, but it is seven things and nothing said so until now.

Each row below: what goes in, what comes out, where the rules are written, and which file you can
run to see them work.

| # | what it scores | in | out | the rules | run it |
|---|---|---|---|---|---|
| 1 | **a person's daily factors** | swipes, timings | six factors 0–100, firmness, flags | `ASSESSMENT_ENGINE.md` §2, §4–§6, §9, §10 | `simulations/assess.py` |
| 2 | **the daily name** | the six factors | two words, or one | `VIBE_NAMES_V5.md` §3 | `assess.py`, `namesim.py` |
| 3 | **a room's identity, match, disturbance** | the members' factors | a room vector, splits, match %, disturbance | `CHEMISTRY_V4.md` | `chem4.py` |
| 4 | **what two people would be like** | two people's factors | a headline and three or four lines | `MVP_INSTRUCTIONS.md` §4, `CHEMISTRY_LINES_V1.md` | `pairchem.py` |
| 5 | **merging several drawn nights** | everyone's skeletons | one skeleton, or an offer of two rooms | `SKELETON_MERGE_V1.md` | `skelmerge.py` |
| 6 | **a venue's factors** | 5 reviews, 2 summaries, the venue's own fields | 11 scores + "not its thing" flags | `VENUE_DATABASE_HOW_TO.md`, `VENUE_DATABASE_V1.md` §5.8 | `lexicon.py`, `pipeline.py` |
| 7 | **which venues to offer at a stop** | the merged skeleton, the venues, the preferences | 5–10 venues in order | `VENUE_DATABASE_V1.md` §4, §4b | `select3.py`, `prefgate.py` |

Every file above is in `simulations/` and runs on its own with no arguments and no API key, except
`pipeline.py`, which needs a Places key for two of its three stages.

---

## The one thing that is easy to get wrong

**Scorers 1–5 are about people. Scorers 6–7 are about places. They never touch.**

A person's `ENRG` is how they are tonight. A venue's `ENRG` is how loud the room is. Same word, two
different things, and mixing them is the mistake the architecture was rebuilt to prevent. The vibe
never picks a venue; the skeleton does.

If you are implementing and find yourself reading a person's factor score to choose a bar, something
has gone wrong — see `VENUE_DATABASE_V1.md` §0.

---

## 1. A person's daily factors

**`simulations/assess.py`** — new 2026-10-06, and the one that was missing.

The path: swipes → a score per factor → firmness → rescaling → the name.

- **Each swipe is a number.** Love 88, up for it 62, not for me 38, hard pass 12.
- **A factor's score is the mean of its cards.** That is the whole rule, and it reproduces the
  four-row table in §2.2 exactly: up-then-love is 75, up-then-up is 62, up-then-not is 50, and
  up-then-hard-pass is 37 and gets flagged as a broken pair.
- **The deck adapts.** An extreme answer ends a factor; a mild one adds a second card at least three
  positions later. Six cards for somebody decisive, twelve for somebody mild on everything, about
  nine for most.
- **An unanswered factor stays undefined.** Never substitute 50 — that is a real neutral and this is
  an absence of data.
- **Rescaling moves each person a third of the way** toward the population centre and spread. Full
  strength was tested and made retakes 37% *less* repeatable.

Two things the module makes explicit that the spec's pseudocode does not:

**A single "not for me" is never a refusal.** The spec's one-liner reads `all(swipe == 'not')`,
which is only right for a *finished* factor — a lone "not" queues a second card rather than ending
anything. The prose says so; the code did not.

**A second card must land after its own first card.** Inserting B cards shifts the deck, and
measuring from the original index put the last factor's B card before its A card. Checked
exhaustively across all 4,096 possible decks.

## 2–5. The people scorers

`namesim.py` (20,000 synthetic people, used to set `SECOND_MIN`), `chem4.py`, `pairchem.py` and
`skelmerge.py` all run standalone and print their own workings.

The numbers to distrust first, flagged in their own specs: `FOCUS` pull **0.80** in `chem4.py`,
which is the most aggressive claim in the chemistry model and is a judgement rather than a
measurement, and `SPLIT_COST` **35**.

## 6–7. The place scorers

`VENUE_DATABASE_HOW_TO.md` covers these end to end, plainly. In short: factor scores come from
counting descriptive words across five reviews and two summary sentences, mixed with what the venue
type suggests; the venue's own listing fields beat anything inferred from words; and the stop list
is ranked by how close a venue is to the shape the user drew, with preferences ordering what is left.

---

## What is still only on paper

**Latency firmness** (§6.2) is implemented in `assess.py` but has never run on real timings. It
needs `card_baseline` and `position_baseline`, which are running averages across all users and do
not exist until there are users. Until then the name's tie-break falls back to score alone, which is
what `first_factor` does when the latency map is empty.

**The population mean and spread** used by rescaling are the same kind of running average. At seven
users the error is about 5 points a factor; at 300 it is about 1.

**`CARD_SET_V11`** — there are still no card images specified for `FOCUS` and `SPONT`. The scoring
works; the two cards that feed it do not exist yet.
