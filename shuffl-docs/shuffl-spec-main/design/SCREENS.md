# The screens — SHUFFL in Line-Up. **Twenty-eight**

**Twenty-eight screens, rendered at 3x.** They are the app as `VIEW_FLOW.md` describes it after the architectural
split, the factor change and the three flow changes of 2026-09-30. The look is `THEME_LINEUP.md`, unchanged:
the cover art is the poster, glow is spent only on what is live, Bebas Neue names things and Instrument Sans
explains them, door times sit left in mono.

Open `screens.html` to see all eighteen side by side with their captions.

| | screen | what it is showing |
|---|---|---|
| 01 | `01_home.png` | **Home, the social hub.** People search, stories, the invites waiting on you, what your friends are up to, posts. No venues anywhere. |
| 02 | `02_shuffl_locked.png` | **The SHUFFL screen, blurred.** What Play opens. The blur *is* the empty state — the user sees the shape of what they are about to get. **Redrawn 2026-10-05:** it was blurring three chosen venues and a *what’s poppin* shelf, which is the model the MVP cut. |
| 03 | `03_shuffl.png` | **The SHUFFL screen. Redrawn 2026-10-05, again 2026-10-06.** Search, Host and Join; the shape as a list of stops; **`Build this night` and `Redraw skeleton`**; **the preset shelf**; suggested venues. |
| 04 | `04_skeleton_game.png` | **The skeleton game.** X is stops, Y is energy, circle size is crowd — and the circles fill with figures of people. The live preview above each circle reads the venue type. |
| 05 | `05_host.png` | **Host.** A venue search, **Host tonight's plan** and **Host with co-hosts**, five venues by match. Neither button asks for a skeleton again. |
| 06 | `06_host_room.png` | **The host room, waiting on skeletons.** Create Plan greyed at **3/5**, and the member list showing DREW / DRAWING / NOT IN YET with the remove cross. |
| 07 | `07_join_place_or_people.png` | **Place or People** — the fifth filter, and the only one that changes the order rather than the set. |
| 08 | `08_room_player.png` | **The room player.** The match as a ring, the blend style washing the screen, the line-up with a per-person reason, the disturbance line, the host's music. |
| 09 | `09_capsule_waiting.png` | **The capsule, waiting.** The join screen goes blank until every member has drawn. The outstanding DPs stay dim and drop off. |
| 10 | `10_plan_card.png` | **The plan card.** Poster, door times, two lines per person — including **“this is your line”**, which only the merge’s provenance makes sayable. **Redrawn 2026-10-05:** *Regenerate a stop* became **Change a stop**. |
| 11 | `11_active_plan.png` | **Active plan.** The stops on a map with the group as a cluster, never a person. Live location off by default. |
| 12 | `12_messages.png` | **Messages.** DMs, group chats, a search through them. Stories and notifications are gone to Home. |
| 13 | `13_profile.png` | **Profile.** Today's V5 name as the hero, seven badges, seven preference rows, the overall going-out type. |
| 14 | `14_capsule_approval_member.png` | **The capsule's room approval, the member's side.** The creator's live room view pushed to everyone else, headed *"Nitya is viewing this room"*, with swipe to approve or decline. |
| 15 | `15_capsule_approval_creator.png` | **The same moment, the creator's side.** The room blurs behind the box, the undecided DPs drop off as people answer, and minimising sends the wait to the status bar. |
| 16 | `16_two_rooms.png` | **The two-rooms offer.** Fires when two drawings correlate below −0.50 and both span 20 points. The two arcs crossing, the flat line nobody drew, and the two ways out. |
| 17 | `17_venue.png` | **The venue screen.** The recommendation carries the user's V5 name and a match number; stories are in-app only; the donut is who actually goes. **Go here** and **Find rooms** stay pinned over a fade as the page scrolls. |
| 18 | `18_go_here_card.png` | **The Go-here card, in its warning state.** Two lines per person, the unservable one in amber *inside* the list, and the warning block under it. Both buttons stay live. |
| 19 | `19_stop_list.png` | **The stop list — the core loop of the first release.** The stop restated in the user’s own words, then the venues that fit it **and are open at that hour**. One row is gold. |
| 20 | `20_gold_offer.png` | **The gold offer.** ₹865, one person per slot, two hours left — and the three conditions, the first of which is already met. |
| 21 | `21_gold_capture_photos.png` | **The capture, photos.** The verification warning **before anything else**, then live camera only, three framings. |
| 22 | `22_gold_capture_swipes.png` | **The capture, swipes.** Compulsory, one factor card at a time, about the room they are standing in **right now**. |
| 23 | `23_gold_verified.png` | **Verified and paid.** The money, and the slot moving from *estimated by its venue type* to **measured**. |
| 24 | `24_gold_in_search.png` | **Gold in search.** The same chip a stop list uses. The number is **a fit against tonight's shape, not a vibe score**, and **gold marks a venue without ranking one**. |
| 25 | `25_gold_failed.png` | **The verification failure.** Never accuses, gives the rate in plain words, and **puts the slot back on the board and says so**. |
| 26 | `26_gold_in_room_plan.png` | **Gold inside a room's plan.** The third surface — and the only one where **the screen is shared and the reward is not**. |
| 27 | `27_member_stop_list.png` | **The member's stop list, read-only.** Screen 19 with the decision removed and nothing else. |
| 28 | `28_preset_opened.png` | **A preset, opened.** Its shape, and **one button** — `Choose venues`. Lock, Host and Find rooms come after, on the finished plan card. |

## The three redrawn on 2026-10-05 — the MVP cut

**`MVP_INSTRUCTIONS.md` §2.2 retired the plan generator**, and three screens were built on it. The flow doc was
updated first (`VIEW_FLOW.md`, the SHUFFL screen and a new **stop list** section); these three follow it.

| | what changed, and why |
|---|---|
| **03** | **The whole middle of the screen.** It showed a generated line-up — three named venues against three times — under *Give me something else* and *Reset*. It now shows **the shape the user drew**, one row per stop, each carrying **the count of venues that fit it and are open at that hour**: *a big loud bar · you can still hear each other · 10 places*. **Nothing is picked yet**, and the chip says so. *Give me something else* is gone with the generator; *Reset* stays, because resetting the **shape** still means something. **What’s poppin** is deferred (it needs events) and **heatmaps** are gated at 20 distinct users, so both come off the screen — suggested venues grows to three rows in their place. |
| **02** | The locked state blurs screen 03, so it was blurring the old model. Same change, behind the blur. |
| **10** | One control. **“↻ Regenerate a stop” became “⇆ Change a stop”** — it reopens that stop’s list rather than asking the app for a different answer. A refresh glyph on a card whose venues the user chose is a promise the app can no longer keep. |

**The fifteen others were checked and left alone.** The social half — rooms, capsules, the approval pair, the
two-rooms offer, messages, profile, the active plan — ships exactly as drawn (`MVP_INSTRUCTIONS.md` §2.4).

**Screen 17 was checked and needs no change.** The 2026-10-01 note about the recommendation rendering in live
magenta rather than green was resolved **in the flow doc's favour of the screen** — the doc now says *the app's
live colour*, so the two agree and the screen was already right.

## The five added on 2026-10-05 — the stop list and the gold promotion

**Both were named as missing in the 10-05 audit and both ship**, so neither could stay undrawn.

**19 is the one that was most overdue.** `MVP_INSTRUCTIONS.md` §2.2 made it the core loop in October and screen 03
had been pointing at it three times with nothing to point to. Three things it does that the old generated plan did
not: it **restates the stop in the user's own words** — *“a big loud bar · you can still hear each other”* — so they
can tell whether the list is answering the right question, and **never shows a factor score**; it says **open at
22:30** in the header, because opening hours are the one field the screen cannot work without; and its footer
states the only claim the app is making, which is that **nothing here is booked**.

**20–23 are the promotion end to end**, and the order of 21 is the part to keep. **The warning comes before the
camera**, not after the photos and not beside the reward — it sets the terms while the user has invested nothing,
which is the only moment it reads as fair rather than as an accusation. Then **live camera only**, with the reason
stated in one line rather than enforced silently: *a photo from another night is evidence about another night.*

**22 carries the fact that decides the whole design.** The swipes are compulsory and **the swipes are what gets
stored** — the photographs only corroborate them. A build that treated the photos as the data and the swipes as a
flourish would have the thing backwards.

**23 states the payoff twice**, because there are two: the money, and **the slot moving from *estimated from its
venue type* to *measured***. The last line is the gamble made explicit — *you were the only capture for this slot;
nobody else was asked.*

**`#FFC247` is artwork-only everywhere else in `THEME_LINEUP.md`. Gold is the single exception**, and it reads
precisely because nothing else in the chrome uses it.

**The failure state is one screen different and is not drawn:** *“We couldn't verify this one — try again at your
next stop.”* It fires about **1.4%** of the time (`GOLD_PROMOTION_V1.md` §4b) and, with one capture per slot, it is
the only check on the data — **load-bearing and fallible at once**, which is why the copy may never accuse.

## The two added after the 10-05 review — and who picks in a room

**24 carries one rule that is easy to get wrong and expensive to get wrong.** A gold venue appears gold in search
exactly as it does in a stop list — same chip, same ₹865, same countdown — **but gold never moves it up the
ranking.** Summer House is first because it fits best, and the dashed note on the screen says so in the product's
own voice. **The moment gold ranks a venue, the fit number stops being true and the screen is advertising.** The
other thing the screen keeps straight: the number against a place is a fit against the shape drawn tonight, and
the vibe match lives on the home screen's people search, which is a different number that happens to look alike.

**25 is the most delicate copy in the app.** It fires about **1.4% of the time on captures that are perfectly
genuine**, and with one capture per slot it is the only check on the data — load-bearing and fallible at once.
Four things it does: it **never says the user did anything wrong**, because 1.4% of the time they did not; it
**gives the rate in plain words** rather than hiding a number they would be right to want; it **puts the slot back
on the board and says so**, since a failure that silently consumed the slot is the one outcome nobody would
forgive; and it **says what usually fixes it**, because a retry with no guidance is a second coin toss.

**And it is quiet.** The paid screen spends the gold; this one does not, beyond the single button offering
another. **A failure rendered at the volume of a payment reads as a penalty.**

**In a room, the host picks (decided 2026-10-05).** The merged skeleton gives the stops and **the host opens each
stop's list and chooses**. A vote turns every stop into a negotiation on a night people joined to stop
negotiating; first-to-tap rewards whoever is looking at their phone. **The host already carries the room's three
filters, so this is the same authority applied to the same object rather than a new one.** Members get the stop
list read-only with the host's choice marked and *“Aarav is picking your 22:30”* — **locked out of the decision,
never out of the information** — and `Change a stop` on screen 10 is the host's control alone.

## The last two, 2026-10-05 — and the set is complete

**26 is the only gold surface where the screen is shared and the reward is not**, which is the whole reason it
needed drawing rather than describing. A gold stop renders gold on a plan five people are looking at, so the card
has to say the thing a shared screen leaves ambiguous: **one person per slot means one person, not one room.**
**Without that line a room of five reads the chip as five rewards**, and four of them find out otherwise at the
venue. The `Change a stop` control carries *you are the host* beside it, so the asymmetry is explained where it
is exercised rather than discovered.

**27 is screen 19 with the decision removed and nothing else removed.** The header names who is choosing, the
host's pick is marked, the rest stay visible but dimmed, and **the affordance is a request rather than a greyed
button** — *ask Aarav to change this.* The footer states the rule in one line: **you can see everything Aarav
can; the pick is his because the room is.**

**That completes every screen the MVP ships.** What is still not drawn is listed below, and none of it is on the
release path.

## Added 2026-10-06 — presets, and the two controls

**Screen 03 was missing its primary action.** The stop rows were tappable and the only button was
*Reset*, so the main thing a user does on that screen was a quiet affordance. It now carries
**`Build this night`** — which opens the first stop with no venue, and reads *Continue* once some are
filled — beside **`Redraw skeleton`**, renamed from *Reset* because *Reset* never said what it reset.

**And the presets moved onto it.** They used to be a line of text under the skeleton, where, in the
user's words, they *“get blended into the background with the presence of the skeleton”*. Somebody
mid-draw is concentrating on the drawing. **The same list, seen after you have drawn and named by
things you recognise, reads as an offer rather than as a fallback** — *I do not want this much
control tonight, I want a tried and tested one.* Drawing stays the only way in.

**On the treatment.** Coloured pills were weighed against artwork tiles and the user chose pills. The
glyph texture sits at each pill's **trailing edge**, greyscaled to about 10% brightness at a third
opacity — the first attempt scattered it across the whole pill and it ate the labels. **No preset is
gold:** `#FFC247` already means *there is ₹865 here tonight*, and a gold preset two rows above a gold
venue would collide on the one colour in the app that carries money.

**Screen 28 is the preset opened, and the notable thing is what is absent.** One button, `Choose
venues`. Lock, Host and Find rooms are not there because **there is nothing to lock** — a plan exists
only once every stop has a venue — and they appear on the finished card where they already live.

## What the set is deliberately showing

**The status bar in situ, in four of its eight states** — *2/5 skeletons* on Home, *3/5 skeletons* in the host
room, *awaiting members* on the capsule screen, *live* on the active plan. It is the newest element in the app and
the hardest to understand from prose, because its whole point is that it is the same bar everywhere.

**Two gates, one level apart.** Screen 02 is the SHUFFL gate; the home screen's own vibe gate is the one above it.
Both blur rather than empty, and that is the pattern, not a coincidence.

**The skeleton's two axes doing different jobs.** Screen 04 is the only place in the app where a user states a
quantity rather than a preference, and the figures-of-people fill is what makes the second axis legible without a
label.

## What is still not drawn

- **The swipe game itself** — held deliberately, pending the card images and the identity-factor set.
- **The Go-here card's one-stop state** — one line different from screen 18.
- **Settings, and the onboarding run.**
- **The Go-here card's other state** — the one-stop case, where *Build my night around this* is greyed
  with *"Your night is one place tonight"*. One line different from screen 18.
- **Motion.** Nothing here says what the bar does when a plan locks, or how the blur lifts.

## The three added on 2026-10-01

**The approval is a pair, and drawing only one side would have hidden the point.** The creator sees a blurred
room behind a waiting box; every other member sees *the creator's live view*, headed with their name. The same
moment, two screens, and the second only makes sense once you have seen the first.

**Screen 16 is the one that argues.** It is the only screen in the app that tells the user the model has found a
problem it will not solve for them, so it has to do three things at once: show that the two drawings really are
opposed (the arcs crossing), show what averaging would cost (the flat line, drawn in dead grey, labelled as the
night neither of them drew), and name what the one-night option actually costs — **whose** shape wins, **why**
(the firmer drawing), and what the loser keeps (their preferences, still served at every stop).

**It deliberately recommends the split and still offers the other.** `SKELETON_MERGE_V1.md` §5a says *ask, do not
decide*. A screen that only offered two rooms would be deciding.

## The two added on 2026-10-01 (second pass)

**One deviation from `VIEW_FLOW.md` worth knowing about.** The spec says the recommendation line is *"highlighted
in green"*. Line-Up has no green as chrome — `#24E0FF` and `#FFC247` are artwork-only and there is no green at
all — so the recommendation uses the live magenta instead. It is the right call on the theme's own terms (the
recommendation *is* the primary thing on the screen, which is exactly what the magenta is for), but it is a
deviation and not an oversight. **Change the spec or change the theme, but they currently disagree.**

**Screen 18 is drawn in its warning state rather than its clean one**, because the warning is the part that
changed on 2026-09-30 and the part a developer could get wrong. The treatment to keep: the unservable line sits
**in amber inside the per-person list**, where Bela's vibe line would be, *and* again as a block underneath. Once
in context, once as the question. Putting it only in the block would make it feel bolted on; only in the list
would make it missable.

**Both buttons stay live.** That is the whole content of the 2026-09-30 change — the talk floor is a warning now,
not a veto — and a greyed *Build my night* would silently undo it.

## Audited against `VIEW_FLOW.md`, 2026-10-01

Every screen was checked line by line against the pushed flow doc. **One screen was wrong, the doc was silent on
five things the screens show, and the doc contradicted itself once.** All resolved; the two sets now agree.

| | |
|---|---|
| **the screen was wrong** | the room player had the host's music **playing**. The doc says *muted by default with a speaker toggle*, and the doc is right — a phone cannot start audio without a tap and nobody opening this on the metro should be handed sound. The screen now reads *tap to play* and the music row is marked **muted**. |
| **the doc contradicted itself** | the **duration slider**. Time became a start and an end on 2026-09-30, and a slider that changes the night's length after people have drawn **invalidates every skeleton in the room**. Retired in both places it was specified. |
| **the doc was silent** | the venue recommendation's colour (green → the live colour; the theme has no green as chrome); the host room's **member list** with per-person DREW / DRAWING / NOT IN YET; the capsule card's **who else has decided** row; the **two-rooms screen** itself; the blurred SHUFFL screen's centred prompt; and the filter chip carrying its current values. All six written in. |

**The duration slider is the one worth noticing.** It was not a cosmetic leftover: it is the single control in the
app that could silently break the skeleton merge, and it survived three documents because nobody re-read it after
the window arrived. Drawing the screens is what found it — there was nowhere to put it.
