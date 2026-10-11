> **V4, 2026-09-17.** Two decks: a **preference deck** at onboarding (six plain images of the thing,
> swiped *The whole point / Nice to have / Don't mind / Don't care*, plus one image pair for the
> dressed-up sense) and the daily **vibe deck** (seven factors, 7–14 cards, *Love / Up for it / Not
> for me / Hard pass*). The name comes from the vibe deck; badges from the preferences. Everything
> in V3 about the card screen, Next, Back, the timeout and the pause applies to both decks. The
> current text of every screen is in `VIEW_FLOW.md`; this file is the change record.
>
> **2026-09-18 — the plan card under the designed night.** Removed: the "Eased up on…" note and its
> ⓘ sheet; the payback line ("This one's Neha's — the room owed her the food"); the dedicated-stop
> line ("This one's for Ruchi. Next stop's yours."). Added, per stop: a **stand-in note** ("Aarav's
> here for the crowd tonight; Bela's set on a calm one"), a **to-a-degree note** ("Some energy here
> for Arjun; more at the next stop"), an **absent note** ("No games here for Chetan — nowhere does
> games, a floor and a quiet table at once"). An easy person's line reads "Divit's easy tonight."
> Whole-point preferences the night could not serve get one line at the bottom of the card. The
> chemistry chip appears as soon as a second person is in the room.

# Swipe Game Flow — V4 change record (V3 text below)

Drop-in replacement for the "Swipe Game Flow" section, plus the one-line edits elsewhere in the
document that refer to card counts or tiebreakers. Written in the document's own style. The
backend rules behind every screen are in `ASSESSMENT_ENGINE.md`; nothing here contradicts them.

---

## Swipe Game Flow

**Before the cards:** one screen, one sentence, and a "Let's go" button.

> Swipe how you feel about tonight. Gut call — first reaction wins.
> Not sure? Hit Next and it comes back later.

*Rule for this screen:* it must not mention time, speed, or how many cards there are. Nothing like
"be quick" or "the cards disappear." (There is a silent timer on each card, but the user never
knows it exists — see below. Telling them changes how they answer.)

**The card screen:**

At the top, a thin progress bar. **No number on it** — no "3/14," no "card 3." The bar fills as
factors get resolved and never moves backwards. The number of cards changes depending on how the
user answers, so a count would be wrong the moment it was shown.

In the centre, the card: a full-bleed image. **Images are placeholders for now** — any image, or a
coloured panel with the factor name on it, until the final images are decided. Everything else on
this screen is final. **Images are placeholders for now** — any image, or a
coloured panel with the factor name on it, until the final images are decided. Everything else on
this screen is final.

Around the card, four directions, each marked with a word in a colour. **No emojis anywhere.**

| direction | word | colour |
|---|---|---|
| up | **LOVE** | gold |
| right | **UP FOR IT** | green |
| left | **NOT FOR ME** | grey |
| down | **HARD PASS** | red |

When the user swipes, the card moves in that direction, blurs and shrinks as it leaves, and the
word for that direction enlarges briefly across the screen in its colour, then fades. No emoji
takeover.

Below the card, two buttons: **Back** on the left, **Next** on the right.

- **Next** — "not yet." The card leaves and goes to the back of the deck; it will come round again
  after everything else. Use this when the user doesn't want to answer this one right now.
- **Back** — "show me that again." The previous card returns. The user can swipe it differently or
  swipe it the same way. Either is fine.

**How many cards:**

The deck adapts to the user's answers. Every factor starts with one card. If the user swipes
**Love** or **Hard Pass**, that factor is done. If the user swipes **Up For It** or **Not For Me**,
a second card for that factor — a different angle on the same idea — joins the deck a few cards
later. So a decisive user sees about ten cards; a user who leans mildly on everything sees about
twenty; most people see around fourteen. The user is never told any of this; they just swipe.

(One factor, dressing up, always shows both of its cards regardless of the first swipe. The user
doesn't know this either.)

A factor's two cards are never shown back to back. The second is always at least three cards
after the first, whether it arrived because the first swipe was mild or because the user pressed
Next on it. The one exception: if the first card was the last in the deck (or fewer than three
remain), the second goes at the end — which can make it the very next card. The pair is never
dropped.

**If a card sits with no action for 12 seconds:**

It slides away silently, as if the user had pressed Next, and the next card appears. Nothing is
said and nothing flashes. A user who is actually looking at the screen will never see this happen
— it exists to catch someone who put the phone down.

**If two cards in a row time out:**

The deck pauses and a box appears over it:

> **Are you there?**
> [ Yes ]   [ No, I was away ]

- **Yes** within 5 seconds — the deck carries on. The cards that timed out stay at the back and
  come round later.
- **No, I was away** — the deck goes back to the first card that timed out, with a fresh start.
- Nothing tapped for 5 seconds — the deck goes back to that card and freezes, with a box saying
  **Quiz paused**. It stays frozen until the user taps anywhere.

*Rule for the box:* the copy must never mention time. "Are you there?" is about whether they're
present. Nothing like "you took too long."

**A card the user keeps not answering:**

If a card has been Nexted, come back round, and timed out again, the third time it appears it
stays put — no timeout, and the Next button is disabled for that card. Only swiping or Back will
move it. The user has to answer every card eventually.

**After the last card — the tiebreak, only sometimes:**

Most users go straight from the last card to the reveal. Some — the ones whose top factors are
level and the app couldn't separate — get one more screen first:

> **Last one.** All of these matter to you — but if you could only keep ONE for tonight, which is
> the night?

Underneath, two to four options as tappable tiles, one per tied factor, each a short phrase:

```
The room being packed        How late and loud it gets      The way the place looks
What comes out of the kitchen   Everyone being dressed up   It being somewhere new
Having something to play     The act on stage               The place being old
Who you came with
```

Tap one. That's the answer. *This is a pick, not a rating* — there is no scale, no slider, no
"how much."

(Eventually this screen is one composite image with the tied things in it and the user taps the
region. That image doesn't exist yet. Text tiles until it does.)

**The reveal:**

> **Your vibe today is**
> **[Name]**

The name in big type with the animation — one name of up to three words, built from the top
factor, the second factor if one is close, and a fast refusal if there is one: *Luxury Diner*,
*Quiet Luxury Diner*, *Solo Night Climber* (`VIBE_NAMES_V3.md`). No second line. Below the name,
the vibe's description from the database, personalised with AI.

Then the home screen, everything unlocked.

---

## One-line edits elsewhere in the document

**Onboarding, "Let's get your first vibe!"**
~~Goes straight to vibe swipe game with 28 cards~~ → Goes straight to the vibe swipe game (see
Swipe Game Flow).

**Onboarding, "Looks like your vibe today is:"**
The name is now up to three words (`VIBE_NAMES_V3.md`); there is no second line. (The
"also strong on" line added on 2026-09-15 is withdrawn.)

**After Opening the App, Screen 3 (IF swiped right):**
~~The 18 card swipe game is skipped entirely~~ → The swipe game is skipped entirely.

**After Opening the App, Screen 3 (IF swiped left):**
~~User presented with 18 card swiping game + 2 to 4 tiebreaker cards if the app is not
completely clear about their vibe (Same backend rules to be used as mentioned in the Image
generation document and the play button flow document)~~ → User presented with the swipe game
(see Swipe Game Flow). Backend rules: `ASSESSMENT_ENGINE.md`.

**After Opening the App, Screen 3/4 and 4/5:**
~~completed 18 card swiping game~~ → completed the swipe game (both places).

**Screen 2, "Do you feel the same right now?"**
No change to the screen. One note for the backend: record how long the user takes before
swiping on this screen. A fast "yes" and a slow "yes" mean different things.

**Join Button Flow, "Join Alone" and "Join with Friends"**
~~showing the users only those rooms where the blend style stays above 75% similarity … the rooms
between 60-75% will be listed as "other rooms" and the ones below 60% will automatically be
hidden~~ → A public room already has its plan, so the list filters on whether that plan suits the
user: 70% plan similarity **and** a FLOOR check for this one person against the room's plan. How
much they would change the room's blend is the host's check, applied when the request arrives —
the document already has it there. Same change to the capsule version, with FLOOR run per member.

**Host Button Flow, the plan card's refresh button**
Available only while the room is private. Removed the moment the room is hosted, and it does not
come back. People join a public room because of its plan; a plan that can change after they've
joined isn't the one they agreed to. Hosting freezes the plan; locking freezes the room. The
solo Create flow and the SHUFFL GC's "Recreate" keep their refresh — nobody else depends on those.

**Profile Screen and View Profile Flow, "Your overall group dynamic type"**
Dropped, both places. It was marked (NEW) and derived from agency, which was removed from the
model on 2026-09-04. Nothing measures it and nothing should promise it.

---

## What the front end never does

Collected in one place because each one changes what the backend measures:

- Never shows a timer, countdown, or anything that reads as time.
- Never tells the user to be quick, or that cards disappear.
- Never shows a card count.
- Never uses an emoji on a swipe direction.
- Never shows a factor's two cards back to back.
- Never mentions time in the "Are you there?" box.
