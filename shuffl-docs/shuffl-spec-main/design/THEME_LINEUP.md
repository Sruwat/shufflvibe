# Line-Up — the adopted look

**Chosen 2026-09-25.** Eight directions were mocked up as music-service dialects; this is the one. It is a
deliberate hybrid of two of them — the **organisation** of a Spotify-style home (shelves, cover art, a
now-playing bar) with the **eye-catching-ness** of a club flyer (saturation, glow, poster type).

The screens are in `design/lineup/`. Open `lineup.html` to see all three live; the PNGs are rendered at 3x.

---

## The idea in one line

**The cover art *is* the poster.**

In a music app the artwork is a quiet container for a gradient, and the type sits outside it. On a flyer the poster
*is* the type. Here every tile carries its own headline in poster caps — so the shelves stay scannable while each
object in them is eye-catching on its own. That one rule is what makes this a synthesis rather than a compromise
between two looks.

## The three rules that keep it from getting loud

**1. Glow is spent only on what is live.** The ground stays near-black and unlit. Glow lands on exactly three
things: the primary action, the room you are currently on, and the night you are running (the now-playing bar).
Nothing else. Saturation without this rule reads as cheap within about a week.

**2. Type is split by job.** **Bebas Neue** names things — your vibe, room names, venue names in a line-up.
**Instrument Sans** carries anything that has to be *read* — the reason a stop is there, who is in the room, what
the night could not serve. **IBM Plex Mono** is for times and labels. This is how a flyer actually works: the
line-up is display type, the small print is not, and the small print is where this app does its explaining.

**3. Door times sit on the left, in mono.** A music app right-aligns run times; a flyer puts door times in front of
the act. Left-aligned mono reads as both at once, which is the whole point — a SHUFFL plan *is* a tracklist and a
line-up at the same time.

## Palette

| | |
|---|---|
| `#060609` | ink — the ground, deliberately unlit |
| `#131318` | surface — cards and rows |
| `#FF2E7A` | live — the only colour that glows |
| `#24E0FF` `#FFC247` | used **inside artwork only**, never as chrome |
| `#FBFAFF` / `#9C98AE` | text / secondary |

**The accents are not the brand.** Every vibe and every blend style already carries its own colour palette
(`BLEND_STYLE_DATABASE_V3.md`), and that is what fills the artwork. The magenta is the app's; the gradients belong
to whoever's night it is. **This is why the whole look needs no photography at all** — which matters, because
`VIEW_FLOW.md` only permits in-app or licensed media.

## What each screen is doing

**`01_shuffl_screen.png`** — the SHUFFL screen. Your vibe is the hero poster. Host and Join sit directly under it.
*Tonight's line-up* is the auto-generated plan with door times, then Lock it / Shuffle / Custom. *Rooms live now* is
a shelf of poster tiles, each with a live dot and its match percentage on the artwork. *Charts* is where the
heatmaps live now. The now-playing bar carries the locked night.

**`02_room_player.png`** — the room player, 3 of 5. The match is a ring, the room's blend style washes the screen
behind it, the host's DP and music sit under the title, the plan is a line-up with a per-person reason, and the
transport controls are thumb-height at the bottom.

**`03_plan_card.png`** — the plan card. Poster at the top, two lines per person under each stop, the unserved
preference called out on an amber rule, and the two buttons every plan card now carries: **Lock this** and **Host
this**.

## What is not decided here

- The **skeleton game** screen. It is the newest and most important screen in the app and it has no visual yet. The
  waveform treatment from the *Deck* direction is the obvious candidate and does not conflict with this one.
- **Motion.** Nothing here specifies transitions, the live pulse, or what the now-playing bar does when a plan
  locks.
- **Light mode.** There isn't one, and for a nightlife app that is probably correct — but it is a choice, not an
  omission.
