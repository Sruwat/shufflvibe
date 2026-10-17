# The screens — SHUFFL in Line-Up. **Thirty-two**

**Thirty-two screens, rendered at 3x.** They are the app as `VIEW_FLOW.md` describes it after the architectural
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
| 08 | `08_room_player.png` | **The room player, drawn in the state the dropped gate created.** A room that **would have been hidden** before 2026-10-08, shown with an amber label instead. The ring, the room line, the read of you in it, the host’s description, and the plan in the host’s theme. |
| 09 | `09_capsule_waiting.png` | **The capsule, waiting.** The join screen goes blank until every member has drawn. The outstanding DPs stay dim and drop off. |
| 10 | `10_plan_card.png` | **The plan card.** Poster, door times, two lines per person — including **“this is your line”**, which only the merge’s provenance makes sayable. **Redrawn 2026-10-05:** *Regenerate a stop* became **Change a stop**. |
| 11 | `11_active_plan.png` | **Active plan. Rebuilt 2026-10-07.** **Not a map** — the next stop is the hub, with distance rings and the night chaining off. Everyone sits at their **ring and compass sector**, snapped to eight sectors and rounded distances on purpose. |
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
| 29 | `29_inside_a_room.png` | **Inside a room you have joined.** The blend style at the centre with everyone’s icon around it, the room washed in its own colour, the plan with whose line each stop came from. **No match number** — that question is answered. |
| 30 | `30_customise_room.png` | **Customise your room.** The name, a description that goes on the room card, and the plan card’s theme. The room’s own colour stays the blend’s. |
| 31 | `31_friends_activity.png` | **What your friends are up to.** Rooms they are in, rooms they hosted, and what they are considering right now — with the safety case on the screen. |
| 32 | `32_venue_pros_cons.png` | **Pros and cons on a venue.** What fits and what does not, read against the shape drawn tonight and the preferences — **never the vibe**. |

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

## Rebuilt 2026-10-07 — the two reads on screen 08

**The room player showed four numbers and no sentences.** A match ring, a disturbance line, a
blend-style colour and a two-word chemistry chip — **all of which say how well you fit, and none of
which says what the room is.** Somebody deciding whether to join is asking the second question.

It now carries both generated reads, in this order: **the ring, then what the room is, then what you
would be in it.** The standalone disturbance line is gone — *“you would barely change this room”* is
the headline of the second read rather than a footnote under the first.

**Regenerated from live engine output, 2026-10-07.** Every string on it now comes from the
simulations rather than from a mockup: the room vector is a real `chem4.room()` over four quiet
talkers, the sentence is `roomline.room_line()`, and the headline and three lines are
`roomfit.read()` for a viewer who wants a bit more go than they do. **The headline changed when the
disturbance bands were re-cut** - it had read *you would barely change it* against bands that no
longer exist.

**To make room**, the music card and the transport controls merged into the people row: the host's
track sits as a thumbnail with one play button, still muted. Nothing was cut.

## Added 2026-10-07 — inside a room

**Screen 08 is the room before you join. This is the room once you are in, and the difference is the
point.** Everything on 08 that was a number — the match ring, the fit read, *request to join* — is
gone, because all of it answered a question you have now answered.

**The blend style takes the centre of the screen**, with every member's icon arranged around it and
the chemistry chip beneath, washing the background in the room's own colour. That is
`VIEW_FLOW.md`'s own description and it is the only element here that is about **the group** rather
than about the night. It is also the room's identity rather than its plan: it updates when people
join, while the plan does not.

**The plan is the thing everyone joined for**, so it keeps the per-stop provenance — *Zoya — this is
your line* — which only the merge makes sayable.

**And the one generated sentence stays.** *This room came to talk, and nobody is trying to push it
harder.* It described the room when you were deciding and it still describes it now; it is the only
read that survives joining.

## Rebuilt 2026-10-07 — the room, and the plan

**29 lost its plan list and both its buttons.** The plan is **one `View plan` button** because it is
settled and the room is for the people; the two buttons were replaced by **a single microphone**,
muted until tapped, with a ring on an icon showing who is speaking. **No camera, deliberately** —
written into `VIEW_FLOW.md` as a decision rather than left as a default, because the pressure to add
video will come from people who have not thought about who is in a public room at midnight.

**And the room now has an ending.** The host locks the plan, the room closes, the group chat is
created named after it, and the active plan appears in the bottom bar. **The chat is not made when
the room is hosted** — so a room that never settles never produces one, and nobody is left in a group
they did not go out with.

**11 shows nobody's position at all, and is not a map.** The first version drew everyone's icon on a
map; the second kept the map and swapped icons for distances; **the third dropped the map.** The night
is the rising chain of stops the user drew, with an approach lane into stop one, and each member
placed on that lane by **how far they are**. A dot on an abstract diagram could be anywhere in the
city, so there is no position to leak and **no Maps SDK in the app at all**.

**Superseded note — 11 shows no one's position but your own.** The first version put everybody's icon on the map; the
user replaced it with **how far each person is from the next stop**, which answers *is everyone
nearly there* without telling a room of five — which may include strangers — exactly where somebody
is standing. **It also keeps the privacy rule that was already in the flow doc**, which the first
version had reversed.

## Added 2026-10-08 — three from the MVP list

**Customising a room (30)** is three things and a deliberate fourth absence. Name, description, and
the **plan card's theme** — previewed live. **The room's own colour is not editable**: it comes from
the blend and it is the room's identity rather than its decoration. Music is shown greyed with its
reason rather than hidden, because an absent feature with a stated cause reads as a decision.

**Screen 08 carries the result**: the host's description sits above the plan, and **the plan is a
themed division inside the room card** rather than beside it, which is what the MVP list asks for.

**What your friends are up to (31)** is new to the spec set entirely. Rooms they are in, rooms they
hosted, and **what they are considering right now**. **The dashed note is the feature rather than a
footnote** — rooms and venues only, never a position, never a search, never a venue merely scrolled
past, and the off switch named on the screen.

**Pros and cons (32)** reads against **the shape drawn tonight and the stated preferences, never the
vibe** — and says so on the screen, because the request was phrased as *according to your vibe* and
§0 of `VENUE_DATABASE_V1.md` forbids exactly that. Green is what fits; **amber is never a warning
off**, it is the thing you would otherwise find out at the door.

## Redrawn 2026-10-08 — the room that would have been hidden

**The join gates came off because at launch volume they delete the list rather than filter it** — the
70% similarity gate alone cuts 78% of rooms, and 55% of users would see an empty screen. So screen
08 is now drawn **as a room that fails the per-member `FLOOR` check**: one that nobody would have
been shown a week ago.

**What the gate would have said is an amber label, and the room is shown anyway.**

> **NOTHING HERE IS PITCHED AT YOUR NIGHT**
> Not one of these three stops is close to the shape you drew. **You can still join** — you would
> just be going to their night rather than yours.

**`Request to join` stays live.** That is the whole content of the change: the app says what it
knows and the person decides. **It is the same move as screen 18**, where the talk floor became a
warning rather than a veto and both buttons stayed live — and like 18, it is drawn in the warning
state because the warning is the part a developer could get wrong.

**The clean state differs by the absence of one block.** A room that suits you simply has no amber
card, and the rest of the screen is identical.

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

## Added 2026-10-10 — the flow change (entry 190)

**Eleven new screens and two rebuilt.** The Host button, the host room and the separate *Join with
friends* door are gone; going out with people you know is one flow with **one person holding the
wheel**, and a night can now be **built by hand**.

| | |
|---|---|
| **33** | **Add friends to your night.** The friend list carries the three things that decide whether somebody can come — **today's vibe**, a **presence dot**, and **whether they have drawn**. Zoya has not played at all and is still addable, with the five-minute gate living on the invite rather than on a grey row. The footer states the price: **nothing can be browsed until every one of them has drawn** |
| **34** | **Name this gathering.** One field naming three things — the room, the status bar and the chat. **The chat is created here and the user never sees it happen** |
| **35** | **The gathering, waiting.** Screen 09 reborn, and the load-bearing one. Both timers are visible and they differ on purpose: **no vibe runs a five-minute clock, no skeleton has no clock at all** |
| **36** | **The capsule room** — what the four people who are not driving see. The blend style, the mic, **Request the wheel**, and a card saying what the holder is doing right now |
| **37** | **The mirror.** *Rhea is viewing Summer House*, with her full payload including the per-member warning, and *Rhea selected Raasta for your 21:00* as a toast. Everything minimises into **View updates** |
| **38** | **A request for the wheel.** The copy has to say what the holder loses, because the name alone does not |
| **39** | **Minimised, without the wheel.** Drawn as specified, **including the part that is wrong** — it is a dead end, and saying so on the screen is the point |
| **40** | **Build my own night, empty.** Four meters, two readouts, one dashed circle |
| **41** | **The venue search.** Our own admitted database only, and the **closed-at-that-hour** case drawn as a soft block with the reason stated |
| **42** | **Three places in.** The meters read as **spans**, the arc as a sparkline, the stop count against the window |
| **43** | **The built night.** A plan card with **no skeleton behind it**, and the card says so |

**Rebuilt:** **03**, the whole SHUFFL screen in its new order, and **02**, which blurs it.

**Three things in this set are arguments rather than decoration.**

**The meters are bands and never numbers** (40, 42, 43). The lexicon's mean error is **7.1 points**
and `FOCUS` and `GAMES` have no low-keyword list at all, so a numeral would be a precision claim we
cannot back. Each one is also a **span across the stops** rather than a level, because **the mean of a
rising night equals the mean of a falling one**.

**Every DP on screen 03 is full colour**, and that is not a styling choice. The screen cannot be
reached until all four have drawn — the grey-DP state is **35**, and it is locked. This is what
keeps `SKELETON_MERGE_V1.md` §6 intact: ranking against people who have merely been *invited*
would mean inventing a shape for somebody who has not drawn one, and gating the screen makes
**invited and drawn the same set** by the time anything is ranked.

**Rooms sit above the user's own night on 03**, which is a bet rather than a layout.
`MVP_INSTRUCTIONS.md` calls the stop list the core loop and MVP question 3 asks whether drawing beats
filtering; this partly answers it before it is measured. **Watch whether anybody scrolls past the room
list at all.**

### Retired by this set

**05** host, **06** host room, **07** join place-or-people. The PNGs stay in the repo as history —
the Place-or-People toggle itself survives behind **See all rooms**, but the screen it lived on does
not. **09** is not retired after all: it comes back as **35**.

## Added 2026-10-12 — the waiting screen and proposals (entry 191)

**Entry 190 left the no-wheel screen as a blank page and two buttons and called it the first thing
owed. This is the answer, and it is better than the read-only floor I proposed.**

| | |
|---|---|
| **39** | **rebuilt — the waiting screen.** Three carousels (rooms, venues, **nights**), three to five deep, each with a **Refresh**. *“You don't have the wheel”* drops to the bottom |
| **44** | **the same screen, locked**, until everybody invited has drawn |
| **45** | **a proposal, from the member's side** — the holder's view with every control replaced by **Propose** |
| **46** | **the proposals panel** — the holder's side, with dedupe and the preset warning |
| **47** | **a friend who had not opened the app** — deck, then this, then the room |

**03** gains a **3 PROPOSED** chip beside the filters.

**Everything in the carousels is ranked against the whole group's merged skeleton, never against the
person looking.** That is the point of the screen rather than a detail of it: four people see the same
shelf, so proposing from it is a conversation rather than five private searches. It is also why the
match number on **45** is headed **THE GROUP IN THIS ROOM** — two people must not look at the
same card and see different numbers.

**Propose adds a verb, not a second driver.** The wheel exists because somebody has to decide, and the
objection to it was that the other four had nothing to do. One button answers that without
reintroducing the thing that made co-hosts incoherent.

**44 is the screen that makes the ranking honest.** Nothing can be ranked until everybody has drawn,
because ranking against a member who has told the app nothing would mean inventing a shape for them
— `SKELETON_MERGE_V1.md` §6. **The capsule room is deliberately not locked** and the status
bar stays live under the overlay, because people can talk while they wait. **And leaving is the
deadlock exit:** if the last undrawn member goes, the lock lifts by itself, which is why the skeleton
gate correctly has no timer.

**46 carries the one warning this mechanism needs.** A preset that the holder accepts **replaces the
night everybody drew** and loses stop provenance with it. Silently discarding four people's drawings
is the only way this feature could do real damage, so the card says so before the button.

## Added 2026-10-12 — the invite has three answers (entry 192)

| | |
|---|---|
| **48** | **An invite.** *“Rhea has invited you to their night”*, with **Accept**, **Decline**, and a **cross** to ignore |
| **49** | **The locked home screen** — where declining lands you |

**The old invite had two answers, yes and silence.** Accepting dropped you into the room with the
deck over a blurred background, and there was no way to say no. **Decline is the thing that was
missing**, and it frees both sides: the invitee gets their evening back, and the room's lock lifts at
once instead of waiting out a countdown on somebody who already knows the answer. **The cross is a
third thing again** — *not now* — and returns the invite to the notifications bar with the
five-minute clock still running.

**48's card above the buttons is the load-bearing line:** an invite has to say what accepting costs.
**The vibe and the shape, and never the window, the distance or the budget**, which belong to whoever
started the night (`SKELETON_MERGE_V1.md` §1).

**49 is not a new screen, only a newly reachable one.** It is the state a returning user without
today's vibe already sees. *The user's reason for routing Decline here: “declining the request
should lead the user to somewhere and not the swipe game directly since it may be that they don't
want to use the app at the moment.”* **So it asks for nothing and offers one thing.** The
declined invite stays in the bar with its outcome on it rather than vanishing — an answered
invite is a record, not a deletion. **Messages, profile and settings stay live**, because somebody who
just declined may want to turn off the notification that brought them there.

**One line on 49 is a decision made visible:** *“there is no timer on it.”* The five-minute
clock is a **response** clock and stops the moment the deck opens, so the deck is never raced —
which matters because card latency feeds firmness, the daily name and the merge, and the card screen
may never mention time.

## Added 2026-10-13 — the expired invite (entry 193)

| | |
|---|---|
| **50** | **An invite that ran out**, with all three endings in the bar beside it |

**An expired invite does not vanish.** A row that disappears leaves the person wondering whether they
imagined it, and a row that stays but does nothing is worse — so it expands and says what
happened, whether the host knows, and what is still possible. **Find the room is live only because
this night went public**; a night that never does carries the message button alone rather than a
button that would do nothing.

**The live row counts down in the open, and that is the opposite of the rule on the card screen.**
Both are right. In the deck the clock measures **the user's own reaction time**, which feeds firmness,
the daily name and the merge — so showing it corrupts the measurement. In the bar it measures
**how long four other people are waiting**, and changing how fast somebody answers that is the whole
point. **A countdown is honest where it is about somebody else's evening and corrupting where it is
about your own.**

## Changed 2026-10-13 — notifications (entry 194)

| | |
|---|---|
| **01** | **three notifications and a See all**, replacing two rows that advertised **co-hosts** and **capsules** — both retired by entry 190. Its status bar also still read *“2/5 skeletons”*, the retired co-host counter |
| **49** | the same three-and-See-all pattern on the locked home screen |
| **50** | **rebuilt as the notifications screen** — scrollable, over the home screen, split into **waiting on you** and **earlier tonight**. The expired invite expands here |

**Anything with a running clock pins to the top and is never the row that gets cut.** Strict recency
would let three friend requests push a live invite off the home screen, and that is the one row with
five minutes to run and four people waiting on it. **Same precedence idea as the status bar**:
recency is the default ordering, never the rule that decides what disappears.

**And a note on how the stale rows survived.** Screen 01 was in neither redraw set, so it kept showing
retired concepts through two rounds. **A retirement is finished when nothing in the drawn set still
shows it**, not when the flow doc says so.

## Swept 2026-10-13 — ten screens carrying things that no longer exist (entry 195)

**Four screens are retired and now say so on the screen itself**, not only in the caption, because
PNGs get passed around alone: **05** Host, **06** the host room, **07** Join / Place-or-People (all
entry 190) and **09** the capsule waiting screen (superseded by **35**). Their captions say what
survived the retirement — the request-to-join queue outlived 05, the Place-or-People toggle
outlived 07, the locked-until-everyone-draws rule outlived 09.

**Six live screens were corrected:**

| | |
|---|---|
| **04** | dropped *“Or select from presets”*, which moved off this screen on 2026-10-06 |
| **12** | two chat previews referencing the retired **Recreate** button and the plan-as-a-photo-message |
| **14**, **15** | user-facing copy still saying **capsule** where it now says **the group** |
| **18** | *“Build my night”* → *“Build around this”*, which no longer collides with **Build my own night** |
| **27** | *“Ask Aarav to change this”* → **Propose another**, and *“because the room is”* → *“because he has the wheel”* |

**A keyword pass found almost none of this.** The retired vocabulary had mostly gone with the screens
that used it; what remained was semantic — screens that never say a retired word and simply assume
retired behaviour. **Reading the rendered text of every pre-entry-190 screen is what found them.**

**And the pattern worth keeping:** the screens that go stale are the ones a change is *not* about.
They inherit a retirement without ever being edited by it, so they are never in the redraw set.

## Added 2026-10-13 — confidence marks, and CROWD on two slots (entry 196)

| | |
|---|---|
| **51** | **Seven ways to mark a band whose value came from the venue's type** rather than from its reviews |
| **52** | **The meter block with both decisions applied** — CROWD split, two hollow bands |

**The problem 51 exists for:** a band read from forty review mentions and a band read from a
hand-written type prior **render identically**. Every row on 51 shows the same value.

**C is the instructive failure.** Widening a band is the textbook way to draw uncertainty, and it is
unusable here because **width already means the span across the stops**. Two meanings cannot share
one visual channel, and the span earns it. **G is the most informative and the hardest to explain**,
so it is held rather than rejected.

**52 shows CROWD splitting and nothing else splitting.** How full a room is changes with the hour and
the day; how loud it is does not nearly as much — a club is a club at nine and at one, it is
simply empty at nine. **The slots are not new machinery**: `VENUE_DATABASE_V1` §2 already has
`base` + `slots` by day and hour range. What changes is authoring two rather than thirty.

## Rebuilt 2026-10-13 — the meters stop being factors (entry 198)

**40, 41, 42, 43 and 52.** The meter set had been the factor set because the factor set was what we
had, not because a factor is a good thing to show somebody.

| | |
|---|---|
| **meters** | how loud &middot; how busy &middot; how it looks &middot; how dressed up &middot; what it costs |
| **readouts** | how late it runs &middot; how far it travels &middot; the arc |
| **badges** | a live act &middot; a floor &middot; outdoors &middot; a proper meal &middot; something to play |

**`TALK` and `MOVE` came off the block** — they describe a room rather than a night, and entry
197 had already measured them as read from the venue's type rather than its reviews **78%** and
**96%** of the time. **They are unchanged everywhere else in the app.**

**`HERIT` was proposed and dropped the same day.** *How antique* is well evidenced — age is
narrated — but almost everything admitted in South Delhi is new, so the meter would sit pinned
at one end for most nights. **`SCEN` replaces it**, and the reason generalises: **a factor with only
one working direction is a badge, not a scale.** `FOCUS` and `GAMES` have no low keyword list at all;
`SCEN` can say *not much* as well as *a lot*, and only because the Kwality test forced that list open.

**Three readouts are exact** — how late, how far, what it costs come from hours, coordinates and
price level rather than reviews, **so they never carry the hollow mark**.

**And one correction to the drawing before it:** `CROWD`'s two slots are **one row, not two**. Each
stop takes the value for its own hour and day and the span is taken afterwards — the split lives
in the data, not on the screen.

## Added 2026-10-14 — the dormant plan, insights and the ditch (entry 201)

| | |
|---|---|
| **53** | **The plan, dormant** — stops with pros and cons, members, a countdown, and **Ditch** |
| **54** | **Plan insights** — where to sit, who needs what and where, and the drink of the night |
| **55** | **A ditch**, and the host's three ways on, in the group chat |

**11** gains the **Plan Insights** button above the directions. **17** and **18** lose the **Menu**
row and the drink recommendation — **dish and drink are cut from the MVP** (we hold no menu data
for any venue and nothing fetches it).

**53 is the answer to entry 200's finding.** The lock settles a night rather than starting one, so
this screen holds the hours between and **reads rather than tracks**. The user distance figure and
the directions appear when the plan does.

**54 is mostly a consolidation and that is the point** — the seating suggestion and the
who-needs-what lines already existed **per stop on the plan card**. Gathering them lets them read
across the whole night. **The drink of the night is one per plan, never per venue**: it claims
nothing about any bar, which is why it survived the cut.

**55 carries the only thing that can reopen a locked plan.** Host to fill the gap **turns the plan
back into a room** — voice on, joiners in the chat, a second lock. Rebuild **keeps the skeletons
and throws away the night**. The lock is reversible exactly once, by the host, after a ditch, before
the night starts.
