# Opening screen — instructions

**Status: locked, 2026-10-17.** Supersedes nothing. Decision log: `decisions/DECISIONS.md` entry 210
(the animation) and entry 209 (the marks it is built from).

This document is addressed to whoever builds the splash screen. It covers what the animation is,
the exact resting geometry, the timing of every moving part, the three things that must not be
changed, and how the screen behaves when the app is slow, fast, or the user has asked for less
motion.

---

## 1. What the user sees

The app opens on a dark screen. **Two cards sit stacked square-on in the middle, under a white
disc.** They fan apart and swipe outward — pink to the left, cyan to the right — and as they
separate, **SH comes out from behind the pink card and FFL from behind the cyan.** The disc turns
the whole time and is the last thing to stop. What is left is the wordmark.

It runs **1400 ms**.

**This is the product's own gesture performed once.** A swipe outward from a room in the middle is
what the user does in the swipe game and what the app does when it splits a deck. The screen is
showing the mechanic before the user has done it once; the resting wordmark is the record of that
gesture having happened — two cards thrown apart, trails still visible, a room left in the middle.

Reference render: `design/brand/SHFFL_opening.gif`
Keyframes and timing table as an image: `design/brand/shffl_opening_animation.png`
Editable source of both: `design/brand/shffl_opening_animation_gen.py`

---

## 2. The resting state — exact geometry

Everything below is in a **498 × 140 user-coordinate box**. Scale the whole box to fit; do not
re-space anything inside it. The gaps either side of the mark are an **optical** 10, arrived at by
eye against the cap height, not a measured 10 — so they are correct only at these numbers.

### Type

| | |
|---|---|
| Face | Bebas Neue, regular |
| Size | 102 |
| Tracking | `0.14em` |
| Fill | `#FBFAFF` on dark, `#1A1A22` on light |
| `SH` | anchored x = 0, baseline y = 104 |
| `FFL` | anchored x = 322, baseline y = 104 |

### The mark

All of it inside a group translated to **`(110, 0)`**. Coordinates below are local to that group.

| Element | Transform | Shape | Fill |
|---|---|---|---|
| Left ghost | `translate(24,39) rotate(-13)` | rect 47 × 68, r 8 | `#FF2E7A` at 32% |
| Left card | `translate(0,47) rotate(-26)` | rect 47 × 68, r 8 | `#FF2E7A` |
| Right ghost | `translate(180,39) rotate(13) translate(-47,0)` | rect 47 × 68, r 8 | `#24E0FF` at 32% |
| Right card | `translate(204,47) rotate(26) translate(-47,0)` | rect 47 × 68, r 8 | `#24E0FF` |
| Disc rim | circle at `(102,67)`, r 33 | | `#060609` on dark, `#1A1A22` on light |
| Disc face | circle at `(102,67)`, r 26 | | `#FBFAFF` |
| Crowd | `translate(102,67) scale(0.79)` | 8 circles, r 5.4 | `#060609` on dark, `#1A1A22` on light |

**The crowd:** eight circles of **identical radius**, evenly spaced on a ring of radius 18, the first
at −90° and every 45° after. **The centre stays empty.**

Two properties of the crowd are load-bearing and are explained in entry 209: **the radii must all be
the same** (varying them produces the clustered-irregular-holes pattern that triggers trypophobia),
and **the centre must stay open** (a filled crowd becomes a blob once the gaps close at small sizes,
whereas a ring keeps a visible hole long after the individual circles have merged).

### Paint order, bottom to top

1. `SH`, `FFL`
2. both ghosts
3. both cards
4. disc rim, disc face, crowd

**The letters are at the bottom.** This matters — see §4.

---

## 3. The animation

Total **1400 ms**. Every track eases with **ease-out cubic**, `f(x) = 1 − (1 − x)³`: fast away from
the centre, slow into rest, which is how a swiped card actually behaves.

| Track | Starts | Ends | From | To |
|---|---|---|---|---|
| Card travel | 0 ms | 980 ms | +66 left card, −66 right card | 0 |
| Card fan | 0 ms | 980 ms | 0° | −26° left, +26° right |
| Card scale | 0 ms | 980 ms | 0.88 | 1.00 |
| Ghost travel | 0 ms | 1120 ms | +66 left ghost, −66 right ghost | 0 |
| Ghost fan | 0 ms | 980 ms | 0° | −13° left, +13° right |
| Letters, position | 310 ms | 1260 ms | centred on `(212, 67)` | rest |
| Letters, scale | 310 ms | 1260 ms | 0.12 | 1.00 |
| Letters, opacity | 310 ms | 550 ms | 0 | 1 |
| Crowd rotation | 0 ms | 1400 ms | −320° | 0° |
| Disc scale | 0 ms | 560 ms | 0.74 | 1.00 |

**Card travel** is a translation on the x axis only, applied *outside* the card's own
rotate/scale — so the card slides horizontally while turning in place, rather than swinging on an
arc.

**Letters** scale and translate together about their own optical centre: `SH` about `(50, 67)`,
`FFL` about `(410, 67)`. Both grow from the disc's centre at `(212, 67)` outward to rest.

**Crowd rotation** turns only the eight circles, about `(102, 67)` in mark coordinates. **The disc
itself does not rotate** — it is a circle, so rotating it would do nothing visible and would cost a
layer.

### Easing, if your framework wants a cubic-bézier

`cubic-bezier(0.215, 0.61, 0.355, 1)` is ease-out-cubic. Use the same curve on every track; the
staggered start times are what create the sequence, not different curves.

---

## 4. Three things that must not change

**4.1 — The letters are painted behind the cards. No masks, no clipping paths.** They start at 12%
scale sitting underneath a card and grow and travel outward until they clear its edge. **Separation
alone is what reveals them.** If they are drawn on top and faded in instead, the screen stops reading
as cards leaving something behind and starts reading as a logo assembling itself, and no amount of
timing adjustment recovers it.

**4.2 — The ghost finishes 140 ms after the card it trails.** Give the two identical timing and the
pair reads as one thick card. **The trail only becomes a trail when it is late.** This is the single
cheapest effect on the screen and the easiest to lose by "tidying up" the numbers.

**4.3 — The crowd's rotation ends last**, 140 ms after everything else has settled. The mark arrives
and *then* quietly stops, rather than every track landing on the same beat. Landing everything
together makes it feel like a slideshow transition.

**And nothing bounces.** No spring, no overshoot, no elastic easing. An overshoot makes the cards
look light; these are meant to have weight.

---

## 5. Behaviour

**5.1 — The animation must never gate the app.** Play it over whatever launch work is happening. If
the app is ready before 1400 ms, let the animation finish — cutting it halfway is worse than a short
wait. If the app is *not* ready at 1400 ms, hold the resting wordmark and show whatever loading
state the design calls for; do not loop the animation.

**5.2 — Tap to skip.** A tap at any point jumps to the resting state immediately. This is for the
user opening the app for the fiftieth time, and it should not animate the skip — snap.

**5.3 — Reduced motion.** If the OS reports *Reduce Motion* (`prefers-reduced-motion` on web,
`UIAccessibility.isReduceMotionEnabled` on iOS, `ANIMATOR_DURATION_SCALE` 0 on Android), **show the
resting wordmark with a 200 ms opacity fade and nothing else.** No travel, no rotation, no scale.
This is not optional.

**5.4 — Cold start only.** The animation plays when the app launches from cold. Returning from
background goes straight to wherever the user was.

---

## 6. Implementation notes

**Build it from vectors, not from a video or a frame sequence.** Every element is a rounded rect, a
circle or a text run, and the whole thing is nine animated properties. A Lottie file or an MP4 would
be larger, would need a separate asset per ground, and would stop you honouring §5.2 and §5.3.

- **React Native** — `react-native-svg` for the shapes, `react-native-reanimated` for the tracks.
  Drive one shared `progress` value from 0 to 1 over 1400 ms and derive every track from it with
  `interpolate`, so the stagger is arithmetic rather than nine separate timings to keep in sync.
- **iOS** — `CAShapeLayer` per element inside one container layer, `CABasicAnimation` per track, all
  on a single `CAAnimationGroup` with `duration = 1.4` and a
  `CAMediaTimingFunction(controlPoints: 0.215, 0.61, 0.355, 1)`.
- **Android** — `ValueAnimator` 0→1 over 1400 ms, derive each track, draw to a `Canvas` or use
  `VectorDrawable` with `AnimatedVectorDrawable`.
- **Web** — inline SVG with CSS `@keyframes` on each group.

**The text must be real Bebas Neue, bundled.** If the face is unavailable at launch, the system
fallback will be a different width and the optical gaps will be wrong. Either bundle the font or
**ship `SH` and `FFL` as outlined paths** — outlines are the safer choice for a splash screen,
because they cannot fail to load and the screen has no other text on it.

---

## 7. Assets

All in `design/brand/`.

| File | What it is |
|---|---|
| `SHFFL_opening.gif` | The animation, 760 px, 26 frames — reference, not for shipping |
| `shffl_opening_animation.png` | Six keyframes plus the timing table |
| `shffl_opening_animation_gen.py` | Generator for both; the maths of every track |
| `SHFFL_wordmark_for-dark-backgrounds.png` | Resting wordmark, transparent, 3785 × 639 |
| `SHFFL_wordmark_for-light-backgrounds.png` | Same, ink type and dark disc rim |
| `shffl_wordmark.png` | The wordmark sheet: both grounds, both faces, down in size |

---

## 8. Known issues

**The cyan card weakens badly on paper-white.** `#24E0FF` collapses toward black against a light
ground. The opening screen is dark so this does not bite here, but **the light-ground cut of the
wordmark is a separate file, not a filter**, and the problem is unresolved rather than fixed. It is
inherited from the palette, not introduced by this screen.

**The crowd is illegible below about 230 px of wordmark width.** By 150 px it is a dark dot between
two cards. The cards and letters survive all the way down, so the name still reads — but do not use
the wordmark anywhere the mark is expected to be countable.

**The chameleon is the app icon, not this.** See entry 209. The icon the user taps and the screen
that opens are deliberately different marks; the chameleon is cropped to the head (casque, turret
eye, open mouth, tongue leaving frame) and does not appear on the opening screen at all. **Whether
the two should ever appear together, and in what palette, is still open** — entry 209 §4.
