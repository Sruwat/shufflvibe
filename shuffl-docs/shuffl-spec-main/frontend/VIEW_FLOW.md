# Front End Final

> Updated 2026-09-15 to match `ASSESSMENT_ENGINE.md`: adaptive four-way swipe deck, Next/Back,
> no card count, no emoji, hard pass in red. The Swipe Game Flow section is rewritten; six
> other lines are edited and marked, and the "group chemistry type" line is dropped from the profile
> and view-profile flows. The Join Alone and Join with Friends room lists are corrected to filter on
> plan suitability only — the blend-style check moves to the host's side, where the document already
> has it. The plan-card refresh button is removed once a room is hosted. Everything else is as it was.
>
> Testing moves to the app itself (a downloadable APK) from 2026-09-16. The Google Forms used
> 2026-09-08 to 09-15 are retired.
>
> **2026-10-05 — the MVP cut (`MVP_INSTRUCTIONS.md`, which outranks this document for scope).**
> **The app no longer generates an outing plan. It offers.** For each stop the user drew, it shows
> **5–10 venues whose factor scores match that stop's shape and which are open at that hour**; the
> user picks one and moves to the next stop. *Give me something else* is retired with the generator
> — there is no plan to regenerate. **Also deferred for the first release:** bands (a venue carries
> one set of scores, not one per hour), *What's poppin tonight* (needs events), and **heatmaps,
> which are gated on 20 distinct users in an area rather than removed**. **And one feature is
> added: the gold promotion** (`GOLD_PROMOTION_V1.md`), which ships from launch and is specified
> below. Everything else in this document stands as the destination.
>
> **2026-09-30 — the factor set splits again** (`FACTORS_V6.md`). The daily deck is **six identity
> factors**: energy, who you face, whether you can talk, whether there's a main event, on your feet,
> and how the plan happens. **Seven preferences** are asked once at onboarding: food, a live act,
> dressed-up, the look, somewhere new, somewhere old, something to play. **How full, how many places
> and where the peak sits left the deck entirely** — the user draws them on the skeleton now.
>
> **2026-09-17 — the factor set is split.** Six preferences (food, a live act, dressed-up, the look,
> somewhere new, somewhere old) are asked once at onboarding as plain images of the thing and live
> in the profile; seven vibe factors (energy, who you face, how full, whether you can talk, how
> many places, on your feet, something to play) are the daily deck. The name comes from the vibe
> deck; badges from the preferences. The plan card shows the stop's type and two lines per person.
>
> **2026-09-19 — chemistry from psychology.** The chip can now be one of twelve tags (Caught the Spark, Table
> and Floor, Common Ground …) before it falls back to the formation words; a Settle-Then-Roam plan shows stop
> durations on the card (“Depot 48, 8 to 11 · then the games pub”).
>
> **2026-09-18 — the designed night.** Every member's top vibe factor is at every stop; nothing is
> eased, owed or paid back, and no stop is one person's. The plan card's notes are now: a stand-in
> note, a to-a-degree note, an absent note (Outing Plan Flow). The ⓘ sheet is gone.
>
> Testing moves to the app itself (a downloadable APK) from 2026-09-16. The Google Forms used
> 2026-09-08 to 09-15 are retired.

## Onboarding Flow

Welcome to [App name]  below it: App Logo, below it: Button saying “Continue”
Brief description of app: [App name] is an interactive personalised experience for you to discover more about places and people catered to you and your own vibe, below that: “Enter the World of [App Name]”; just below that: Sign in Options
“What should we call you?” below that: Text Box to input name
“What do you identify as?” below that: Multiple choice options of pronouns “He/him”, etc.
“First, the things you care about in a place.” Below that, one line: “Swipe on the following things on the basis of how important they are to you in a place.” Below that a “Let’s go” button. This opens the **preference deck** (see Swipe Game Flow, preference deck): **seven cards (2026-09-30)**, each a plain image of the thing — food, a live act, a dressed-up room, a beautiful room, an unmarked door, an old building, **a pool table** — swiped four ways with the labels **The whole point** (gold, up) · **Nice to have** (green, right) · **Don’t mind** (grey, left) · **Don’t care** (red, down). After the dressed-up card, one image pair: “Which of these is dressed-up, to you?” — a suits-and-dresses room, a streetwear room, or “both” — tap one. These answers go to the profile and stay there until the user edits them; they are never asked again on a normal day.
“Now — tonight.” Goes straight to the vibe swipe game (see Swipe Game Flow).
“Looks like your vibe today is: [User’s vibe]” — a two-word going-out identity, e.g. “Peak Front-Rower”, “Locked-In Table-Talker”, or a single name like “Night Climber” (see `VIBE_NAMES_V5.md`); below that, what that vibe says about them
“Your profile is ready for you to set up”; below that, Display profile the same way as described in the Profile Flow below with options to edit an empty dp, empty bio and show everything else according to the only information we have of the user so far which is their first vibe; below that, button to “Skip For Now” to complete their profile later.
## Swipe Game Flow

There are two decks. The **preference deck** is shown once, at onboarding (and again only if the user chooses “Redo my preferences” in the profile): **seven cards (2026-09-30)** plus one image pair, each card a plain image of the thing, swiped **The whole point / Nice to have / Don’t mind / Don’t care**. It uses the same card screen, the same Next and Back, the same progress bar and the same silent timing as the vibe deck below; only the labels and the images differ, and there is no second card per preference. The **vibe deck** is the daily one and is everything that follows.

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

In the centre, the card: a full-bleed image. **Images are placeholders for now** — any image, or a coloured panel with the factor name on it, until the final images are decided. Everything else on this screen is final. **Images are placeholders for now** — any image, or a coloured panel with the factor name on it, until the final images are decided. Everything else on this screen is final.

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

The deck adapts to the user's answers. Every identity factor — **there are six (2026-09-30): energy,
who you face, whether you can talk, whether there's a main event, on your feet or not, and how the
plan happens** — starts with one card. If the user swipes **Love** or **Hard Pass**, that factor is done. If the user swipes
**Up For It** or **Not For Me**, a second card for that factor — a different angle on the same idea
— joins the deck a few cards later. So a decisive user sees **six** cards; a user who leans mildly
on everything sees **twelve**; most people see around **nine**. The user is never told any of this; they
just swipe. A hard pass on a vibe card is not a rejection of the picture — every vibe card shows
two ways a night can go, and a hard pass is choosing the other one firmly.

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
How late and loud it gets        Who you came with         Being able to hear each other
There being a main event         Being on your feet        Deciding it on the night
```

Tap one. That's the answer. *This is a pick, not a rating* — there is no scale, no slider, no
"how much."

**Rewritten 2026-09-30.** The old tiles listed preferences — the kitchen, the act on stage, the
place being old — which predates the 2026-09-17 split and asked the user to break a tie between
things that were never tied. **There are six tiles now, one per identity factor**, and only the
tied ones are shown.

(Eventually this screen is one composite image with the tied things in it and the user taps the
region. That image doesn't exist yet. Text tiles until it does.)

**The reveal:**

> **Your vibe today is**
> **[Name]**

The name in big type with the animation — **two tokens**, built from the top factor and the second
factor if one is close, or a single name if nothing else qualifies: *Peak Front-Rower*, *Locked-In
Table-Talker*, *Night Climber* (`VIBE_NAMES_V5.md`). No second line, and no refusal prefix — both
poles of every factor are wants. Below the name,
the vibe's description from the database, personalised with AI.

Then the home screen, everything unlocked.

---

## What the front end never does

Collected in one place because each one changes what the backend measures:

- Never shows a timer, countdown, or anything that reads as time.
- Never tells the user to be quick, or that cards disappear.
- Never shows a card count.
- Never uses an emoji on a swipe direction.
- Never shows a factor's two cards back to back.
- Never mentions time in the "Are you there?" box.

## After Opening the App

Screen 1:- First Time User: This user would’ve completed the onboarding flow and would’ve played the swipe game and had their vibe assessed and would now enter the home screen with the ability to view all features. They would then click on the play button. Returning User: These users once they open the app enter the home screen and see all features in the homescreen that require a vibe assessment blurred with text over each section saying “Play the swipe game and get your vibe for the day to use this feature”(basically all features except profile settings and messages/social). The user then clicks on the play button to get their vibe and unlock all features. The returning user would need to complete the swipe game before viewing all features since they would be logging in fresh on a new day with their vibe for that day not logged and only the vibe of the previous days logged.
Screen 2:- User clicks on the play button and sees a screen saying “Your most recent vibe is: “XYZ”, below that: “Do you feel the same right now?” below that “Swipe right if yes and Swipe left if no” (Backend note: record how long the user takes before swiping on this screen. A fast “yes” and a slow “yes” mean different things.)
Screen 3 (IF swiped right): The swipe game is skipped entirely. The most recent vibe is reused as today’s vibe and is written to the database as today’s logged vibe (so all vibe gated features unlock exactly as they would after the swipe game). The user is then shown the same vibe reveal screen described in Screen 3/Screen 4 below: “Your vibe today is”, below that the XYZ vibe in big fonts with an animation, below that what the vibe says about their going out type today, personalised using AI.
Screen 3 (IF swiped left): User presented with the swipe game (see Swipe Game Flow). Backend rules: ASSESSMENT_ENGINE.md.
Screen 3/Screen 4 (If swiped left and completed the swipe game): Front End- “Your vibe today is” below that “XYZ vibe in big fonts with an animation”, below that what the vibe says about their going out type today. Description of the vibe is pulled from the database containing the list of vibes and their meaning and personalized using AI according to the user.
Screen 4/Screen 5 (If swiped left and completed the swipe game): After their vibe is displayed the user is taken to the home screen with all the features unblurred and unlocked.

## Play Button Flow

**Rewritten 2026-09-25, revised 2026-09-30.** The play button no longer pops three buttons above the task bar. It
opens the **SHUFFL screen**, and the old Host / Join / Create trio is retired with it — **Create no longer exists at
all**, because hosting now happens from a plan card rather than from an empty room.

**Play does not go straight to the filters (2026-09-30).** It opens the SHUFFL screen **with its features blurred**,
and **tapping any blurred feature is what prompts the unlock sequence** — distance, then time, then budget, then the
skeleton. When the sequence finishes the screen unlocks and the user lands back on the feature they tapped.

**So there are two gating layers, and they are deliberate:**

| gate | unlocked by | what stays visible behind it |
|---|---|---|
| the whole app | the **swipe game** — today's vibe | profile, settings, messages, the social home screen |
| the **SHUFFL screen** | the **filters and the skeleton** | the screen's own layout, blurred, so the user can see what they are about to get |

**What the blurred screen itself shows (2026-10-01):** the screen's own layout behind the blur, and over it, centred
— the label **LOCKED**, the line **“Draw tonight first”** in poster caps, one sentence of what it will cost
(*“Three sliders and a line. Then all of this is yours.”*) and a **Start** button. **The centred prompt and tapping
a blurred feature do the same thing**; the prompt exists because a screen of blurred shapes with no stated way in
is a puzzle, not an invitation.

A user who has played the swipe game but not drawn a skeleton sees a blurred SHUFFL screen. This is the same pattern
as the home screen's vibe gate, one level in, and for the same reason: **show the shape of the thing, then ask for
the one input that fills it.** It also means the app never shows an empty state — the blur *is* the empty state.

**And it is the front-end half of a back-end rule:** the merge counts drawers only and never infers a skeleton from
anybody's cards (`SKELETON_MERGE_V1.md` §6). If nobody has drawn there is genuinely no plan to show, so the blur is
not a nag — it is the truth.

## The SHUFFL Screen

**Reorganised 2026-09-30: this screen is now everything about going out, and the home screen is everything
social.** Top to bottom:

1. **The search bar**, at the very top — **above** Host and Join. It searches **venues, events and heatmaps**.
   Profile search moved to the home screen (see Search Bar Flow).
2. **“Host” and “Join”** side by side.
3. **The shape they drew, as a list of stops — and against each stop, how many places fit it.**
   **(Rewritten 2026-10-05.)** Not a plan. Each row is one stop the user drew: the hour, the shape
   in words (*“a big loud bar — you can still hear each other”*), and **a count of the venues that
   match it and are open then** — *“8 places”*. Tapping a row opens **the stop list** (below), where
   they pick one. **The plan comes into existence as they pick**, stop by stop, and becomes a card
   only once every stop has a venue.
4. **“Build this night” and “Redraw skeleton”**, side by side under the list **(2026-10-06)**.
   **“Build this night” opens the first stop that has no venue yet** and is the primary control on
   the screen — the stop rows are tappable too, but a row is a quiet affordance and the main action
   of a screen should be a button. Once some stops are filled it reads **“Continue”**.
   **“Redraw skeleton”** is the old *Reset*, renamed because *Reset* did not say what it reset.
   **(“Give me something else” is retired, 2026-10-05.** It regenerated a plan from the same
   skeleton, and nothing generates a plan any more. The need it served — *this shape, different
   venues* — is now the stop list itself, which is a list of exactly that.**)**
5. **“Or try a preset” — the preset shelf (2026-10-06).** Four or five presets matched to the user,
   as coloured pills, with **“See all presets”** under them. Specified below.
6. **Suggested venues** — moved here from the home screen. **Ranked against the skeleton, not the
   vibe.**
7. **“What's poppin tonight that fits your shape”** — **deferred for the first release** (it needs an
   events feed we do not have). Kept here as the destination: it ranks against the skeleton the user
   just drew plus their preferences, never the vibe, which is why it can only exist on an unlocked
   SHUFFL screen. **(Renamed 2026-10-01 from “suits your vibe”; deferred 2026-10-05.)**
8. **Heatmaps** — “Explore other vibes”. **Gated, not cut (2026-10-05):** an area renders only once
   **20 distinct users** are in it, which is the number the privacy rule below already requires, so
   the feature turns on when the median active area clears it on a normal Friday. Below that
   threshold a heatmap is either empty or it identifies individuals, and **both failures end at the
   same moment, which is why one threshold governs both.** Collect from day one; ship the switch
   later.

**“Make a custom outing” is retired (2026-09-30).** Every plan is now custom — it is built from a skeleton the user
drew — so a separate button for it described a distinction that no longer exists. The two buttons that replaced it
are the two things a user actually wants at that moment: *this shape, different venues* and *different shape*.

**A filter chip sits top-right** carrying the three parameters' **current values** — *“12km · 8–2 · ₹₹”* — rather
than a bare icon, so the user can see what the plan was built against without opening anything. Tapping it opens
the three, and they can be changed without resetting the skeleton. Changing the **time window invalidates the skeleton and reopens the drawing**
(`SKELETON_MERGE_V1.md` §7) — the other two do not.

**Every outing plan card in the app now carries two buttons: “Lock this” and “Host this”.**
*Lock* sends the plan to the Active Plan Screen exactly as before. *Host* creates a room carrying that plan and
lists it among the available public rooms. This inverts the old order — it used to be host a room, add
co-hosts, create a plan, then host it, with a message telling you to make a plan first. **The plan comes first and
the room is made from it**, so that message is gone.

**The duration slider is retired (2026-10-01).** It survived three documents longer than it should have. The
unlock sequence now collects a **start and an end**, and that window is what every skeleton is drawn inside and
what caps the stop count. A slider that changes the night's length *after* everyone has drawn would invalidate
every drawing in the room "—" it is the one control that can silently break the merge.

**What replaces it in each of the three places it used to live:** on “Build my night around this” and on a
single hosted venue, the night runs inside the window already set; on the SHUFFL screen's automatic plan, the
**filter button** changes the window, and changing it reopens the skeleton. Nothing else needs a length control,
because nothing else sets a length.

### The stop list (2026-10-05) — the core loop of the first release

**This is what the app does instead of building the night.** Tapping a stop row on the SHUFFL screen
opens it.

1. **The stop's shape at the top, in the user's own terms** — the hour, and the line that describes
   what they drew: *“22:30 · a big loud bar — you can still hear each other”*. **The user is never
   shown a factor score or a vector.** The shape is restated so they can tell whether the list below
   is answering the right question.
2. **5–10 venues, ranked by how closely their scores match that stop's shape**, each with the fit
   number, the type, the price band, and the walk or ride from the previous stop. **Only venues open
   at that hour appear** — opening and closing hours are the one field this screen cannot work
   without.
3. **A gold venue in this list renders gold** (see below).
4. **Picking one fills the stop and returns to the list of stops**, where the next empty row is
   highlighted. Picking is reversible: tapping a filled stop reopens its list with the current choice
   marked.
5. **Nothing is scheduled.** The hour on a stop is the hour the user drew, and the venue is open then
   — that is the entire claim. **No stop is anchored to an event, a set time or a table.**
6. **In a room, the host picks (2026-10-05).** The merged skeleton gives the stops; **the host opens each stop's
   list and chooses the venue**, and the plan fills in for everyone as they do it. **The alternatives were a
   first-to-tap race and a vote, and both are worse for the same reason:** a vote turns every stop into a
   negotiation on a night people joined to stop negotiating, and a race rewards whoever is looking at their
   phone. **The host already carries the room's three filters** (`SKELETON_MERGE_V1.md` §1), so picking is the
   same authority applied to the same object rather than a new one.

   **What a member sees instead of the control:** the stop list, read-only, with the host's choice marked and the
   line *“Aarav is picking your 22:30”* — the same push the capsule approval already uses. **Members are not
   locked out of the information, only out of the decision**, which is the distinction that keeps it from feeling
   like a room they are a guest in.

   **`Change a stop` on the plan card is the host's control alone.** A member tapping that stop gets the
   read-only list and, under it, *“ask Aarav to change this”* — never a greyed button with no explanation.

**Why it replaced the generator.** Saying *“this is your 11pm”* is a claim about what a venue is like
at 11pm, and without bands we cannot make it. Saying *“here are eight places that feel like what you
drew, and they are open”* is a claim we can keep. **The second is also the one nobody asked us to
improve on** — a user picking from a list of eight wants options, not an oracle.

**What it needs from the back end:** venue factor scores (`VENUE_DATABASE_V1.md` §5.8, built),
**opening and closing hours (must add)**, and the shape-distance ranking of `OUTING_PLAN_ENGINE.md`
with `SHAPE_GATE` as the cut. Nothing else.

### The preset shelf (2026-10-06)

**A preset is a shape with a name people recognise.** *South Delhi Pub Crawl*, *Foodie's Day Out*,
*The Desert Run*, *Late & Loud*. Picking one fills the skeleton exactly as drawing it would have,
and the user still chooses a venue at every stop. **A preset has never been a generator**, which is
why it survived the MVP cut.

**Where it sits:** on the SHUFFL screen, between *Build this night* and *Suggested venues*. Under
the night you have already drawn, not instead of drawing it.

**Which ones are shown.** Matched to the user's **preferences and their vibe for the day** — high
`FOOD` and high `ENRG` surfaces a *Foodie's Day Out* with several stops in busy popular restaurants.
**Four or five fit the shelf before it wraps**, so the matching has to be opinionated, and
**“See all presets”** sits under the row as the escape hatch. That link is not optional: without it a
mis-read of somebody's factors silently narrows their night and they never find out.

> **This is vibe-to-shape inference, and it is a deliberate exception.** The skeleton exists
> *because* a person's purpose for a night often differs from what their vibe implies, and this
> suggests a shape from the vibe. It is allowed because **offering is not deciding** — drawing and
> *See all* are each one tap away. **Written down as an exception so nobody later “fixes” it by
> making the suggestion stronger.**

**They are time-sensitive, and this needs no new rule.** A *Foodie's Day Out* cannot run at 23:00
because its venues are shut, and **the stop list only ever shows venues open at that hour**. So a
preset appears when its stops can still be served inside the window the user set at unlock, and
drops off when they cannot. Feasibility, not a timetable of what is allowed when.

**The treatment: coloured pills, each carrying a dark glyph texture at its trailing edge** —
greyscaled to about 10% brightness at a third opacity, so it reads as material rather than as icons
and the label stays legible at 11px. **No preset is gold.** `#FFC247` already means *there is ₹865
here tonight*, and a gold preset sitting two rows above a gold venue would collide on the one colour
in the app that carries money.

### A preset, opened (2026-10-06)

**One button, and it is not Lock.** Opening a preset shows **its shape** — the venue type at each
stop and the hours — and a single control: **“Choose venues”**.

**Lock, Host and Find rooms do not appear yet, because there is nothing to lock.** A plan exists
only once every stop has a venue (§`MVP_INSTRUCTIONS` 2.2). So: *Choose venues* → the stop list at
each stop → **the finished plan card**, and the three buttons are on that card, where they already
live for every other plan.

**“Find rooms” on the finished card searches rooms running this preset**, which is a far more legible
search than any score — *four rooms are doing the South Delhi Pub Crawl tonight* is a sentence a
person can act on.

**No extra matching is needed to make that work.** A preset becomes an ordinary plan with a shape
and venues, so the existing room ranking — plan similarity and room chemistry — already surfaces it
to the right people. **A preset must never become a filter on the public rooms list**: at launch
volume there are a handful of live rooms on a Friday, and a third filter stacked on plan similarity
and the per-member `FLOOR` check returns an empty screen.

### Presets do not exist in a room (2026-10-06)

**The only place people draw together is a room somebody hosted with friends, and presets are
excluded there.** Those people are working out the best night *for them as a group*, which is the
one case where the shape genuinely matters and a preset would flatten it.

**Everywhere else the plan is already set before anyone joins** — hosting a preset, hosting a single
venue, building a night around a venue. **So a preset-filled skeleton and a drawn one never meet in
a merge**, which disposes of a problem that would otherwise need solving: `SKELETON_MERGE_V1.md`
resolves opposed drawings by **whose drawing is firmer**, and a tapped preset has no firmness to
measure. The rule removes the collision instead of inventing a number for it.

### Gold venues on the front end (2026-10-05)

**`GOLD_PROMOTION_V1.md` ships with the first release** (`MVP_INSTRUCTIONS.md` §2.6), so gold is part
of the front end from day one. **Three places a venue can appear gold, and they are the three places
a venue appears at all:** in **search**, in a **stop list**, and inside a **room's plan**.

**What gold means to the user:** *a reward is available at this place, tonight, inside the window you
already chose, and only to you.* **One person per slot** — so the state is not “this venue pays”, it
is “this one is yours if you go.” The treatment is the theme's `#FFC247`, which is otherwise
artwork-only; **gold is the single exception to that rule**, and it reads precisely because nothing
else in the chrome uses it.

**The reward line carries the time box and the amount** — *“2 hours left · ₹865”* — and the time box
is stated from the first notification, never discovered at the end.

**The capture opens on arrival**, and only when the venue is in the user's Active Plan with location
on. The order is not interchangeable:

1. **The warning, before anything else.** *“Make sure you complete this carefully — we'll be
   verifying whether what you give us is real.”* It sets the terms before the user has invested
   anything, which is the only point at which it reads as fair rather than as an accusation.
2. **Photos — live camera only.** Wide frame, crowd, bar. **No gallery upload**, because a gallery
   photo is evidence about some other night.
3. **The swipes — compulsory, and the actual data.** Factor cards for the band being captured. They
   are less effort than the photographs and they are what the database stores.
4. **Paid on verification**, with a retry rather than a refusal when it fails: *“We couldn't verify
   this one — try again at your next stop.”* **Verification is wrong about 1.4% of the time
   (`GOLD_PROMOTION_V1.md` §4b), and with one capture per slot it is the only check on the data**, so
   the copy has to hold both facts at once: it is load-bearing, and it is fallible.

**The whole capture must finish inside sixty seconds.** It happens at 23:40 in a bar somebody came to
enjoy, and length is the reason they never do a second one.

**Gold inside a room's plan (2026-10-05).** The third surface, and **the only one where the screen is shared
and the reward is not.** A gold stop renders gold on the plan card, and the card must say what a shared screen
otherwise leaves ambiguous: **one person per slot means one person, not one room.** Nobody else in the room can
see that stop's gold or take it. **Without that line a room of five reads the chip as five rewards**, and four of
them find out otherwise at the venue.

**Gold in search (2026-10-05).** The SHUFFL search bar searches venues, and **a venue carries its gold state
into the results exactly as it carries it into a stop list** — same chip, same ₹865, same countdown. Two things the
results screen has to keep straight: **the number against a place is a fit against the shape the user drew, not a
vibe score** (the home screen's people search is where vibe matches live), and **a gold venue is not promoted up
the ranking.** It sits wherever its fit puts it. **Gold marks a venue; it never ranks one** — the moment gold moves
a venue up a list, the fit number stops being true and the whole screen is advertising.

**The verification failure (2026-10-05).** It fires about **1.4% of the time on captures that are perfectly
genuine** (`GOLD_PROMOTION_V1.md` §4b), and with one capture per slot **it is the only check on the data** — so it
is load-bearing and fallible at once, and the screen has to hold both facts without accusing anybody. Four rules:

1. **It never says the user did something wrong**, because 1.4% of the time they did not. *“This one didn't come
   through clearly enough to count.”*
2. **It gives the rate in plain words** — *about one in seventy genuine captures* — rather than hiding a number the
   user would be right to want.
3. **The slot goes back on the board and says so.** They can take it again the same night if they are still out,
   and somebody else can take it if they are not. **A failure that silently consumed the slot would be the one
   outcome nobody could forgive.**
4. **It says what usually fixes it** — a wider frame, and swipes answered about the room they are standing in
   rather than the night overall — because a retry with no guidance is just a second coin toss.

**And it is quiet.** The paid screen spends the gold; **the failure screen does not**, beyond the one button that
offers another. A failure rendered at the same volume as a payment reads as a penalty.

**What the copy must never do is lead with the reward.** **Gold is something you notice while planning
a night, not a reason to plan one** — and the design already guards it, because the venue has to be in
a plan the user built before the capture can open at all.

## The Unlock Sequence

**Renamed and re-sited 2026-09-30** — this was the Custom Outing Flow, reached from a button. It is now what
**tapping any blurred feature on the SHUFFL screen** opens, and it is the only way the SHUFFL screen unlocks.

Four screens, one at a time, with a Next button at the bottom of each:

1. **Distance** — a slider in km
2. **Time** — **a start time and an end time** (2026-09-30). Not a duration. The two together are the **window**,
   and the window is what every skeleton is drawn inside and what caps the number of stops
   (`SKELETON_MERGE_V1.md` §1)
3. **Budget**
4. **The skeleton** — the skeleton game

**In a room these three filters belong to the room, not to the person.** Whoever opens the plan sets them and
everyone else draws inside them; two skeletons drawn over different windows cannot be merged without inventing a
window neither person chose. A co-host who disagrees gets a **“propose a change”** affordance, which reopens the
filters for the room and asks everyone to redraw.

### Drawn once a night, and the sequence never repeats (2026-09-30)

**The sequence runs once, when the user first taps a blurred feature on the SHUFFL screen. Nothing later in the
night asks for it again.** The skeleton and the three filters are the session's, and every other entry point reads
them rather than re-collecting them:

| the user does this | what they are asked for |
|---|---|
| **Host → “Host tonight’s plan”** | **nothing.** The plan is generated from the skeleton already drawn, the room is made and it is hosted |
| **Host → “Host with co-hosts”** | **nothing** from the host — see the Host flow |
| **accepts a co-host invite** | **the skeleton only.** Never the filters — those are the host's, and they are the room's |
| **Join** | **nothing** if they have drawn; the skeleton if they came straight to Join |
| **accepts a capsule invite** | **the skeleton only** |
| **taps Reset on the SHUFFL screen** | the skeleton only; the filters stay |
| **taps the filter button** | the filters only — and changing the **time window** reopens the skeleton |

**The single reason behind the whole table:** a window belongs to a room and a shape belongs to a person
(`SKELETON_MERGE_V1.md` §1). So anyone joining something somebody else started draws, and is never asked about
distance, budget or time at all.

### The skeleton game

**A grid the user drags a line across. The horizontal axis is stops; the vertical axis is the energy of that stop.**

- Reaching a stop marker on the horizontal axis drops a **circle** on the line — that is one stop.
- Dragging the line up or down between markers says **which way the energy goes**.
- **Press and hold a circle to enlarge it**, as much as they want, to say **how much crowd they would be happy with**
  at that stop. The circle **fills with figures of people as it grows**, so the meaning is legible without a label.
- As each step completes — a drag, or a resize — **a small box appears above that circle showing an image of the
  type of stop the app is reading from the answer**. If it is not what they meant they can change it or start over.
- Next reads the formation and uses the night shape that corresponds to it.

**When it is played (revised 2026-09-30).** Five entry points, and **the skeleton is the only thing any of them
asks for** — the filters are collected once, at the first one, and never again:

1. **At the end of the unlock sequence**, the first time the user taps a blurred feature on the SHUFFL screen.
2. **Whenever they tap Reset** on the SHUFFL screen.
3. **When they accept a co-host invite** — they land on it, and cannot leave it (see the Host flow).
4. **When they accept a capsule invite** — the capsule cannot browse until every member has drawn.
5. **Before a joiner browses rooms**, if they came straight to Join without drawing.

**A joiner draws every time** — a user joins a room once, at most twice, on an average day, so it is not a repeated
cost. **Nobody draws twice in one night unless they ask to**, by tapping Reset.

**Alone**, the formation is the shape of their night. **In a room**, every drawing is merged into one plan by
`SKELETON_MERGE_V1.md`. Three things the front end has to show because that spec produces them:

- **whose line each stop came from** — every stop carries its provenance, so the per-person line under a stop can
  now say *“this is your line”*, which nothing else in the app can say;
- **who has not drawn** — the card names them (*“this is Aarav and Nitya's shape — you haven't drawn yet”*) with a
  button to draw and re-merge, because the merge counts drawers only and never guesses from cards;
- **when two people drew opposite nights** — one building, one front-loading. The app **asks instead of deciding**:
  it offers **two rooms instead of one plan**, because averaging a rising night with a falling one gives a flat
  night neither person drew (`SKELETON_MERGE_V1.md` §5a). **The screen is specified below.**

### The two-rooms offer (2026-10-01)

A full screen, not a toast, because it is the only place in the app where the model tells the user it has found a
problem it **will not** solve for them. Top to bottom:

1. **“You two drew different nights”** in poster caps, under the label *the shapes don't meet*.
2. **Both drawings on one grid**, each in the other person's colour, crossing — the argument, in one glance.
3. **The flat line through the middle, in dead grey**, with one line under the grid: *“Averaging you gives the flat
   line — a night neither of you drew.”* **This is the part that cannot be cut.** Without it the screen is asking
   the user to accept a constraint they have no reason to believe.
4. **Two cards, both live.** *Split into two rooms*, marked **suggested**, with one sentence naming each person's
   night and the note that they can still meet at the first stop. Then *One night, [Name]'s shape*, which says
   **whose** drawing wins, **why** (theirs is the firmer one), what the other person loses in plain words, and
   **what they keep** — their preferences are still served at every stop.
5. **Two buttons**, *Two rooms* and *One night*.

**The consolation line in the second card is load-bearing.** Without it, “one night, her shape” reads as a pure
loss and nobody will ever pick it — which would make the screen a disguised decision rather than a question, and
§5a says *ask, do not decide*.

**Why it exists.** Two reasons, both the user's: **(a)** if a plan the app made does not suit someone, it may not be
the venues — it may be that **the purpose of their night differs from the shape their vibe factors imply**; and
**(b)** a person's shape of the night **changes with the company they are in**, so being in a room is itself a reason
to ask again.

### Or select from presets — **moved off this screen (2026-10-06)**

**There used to be a button here reading “Or select from presets”. It is gone.** The presets now live
on the SHUFFL screen, under the night the user has already drawn — see **The preset shelf** below.

**The user's reason, and it is better than the one this document had:** a button under the skeleton
*“gets blended into the background with the presence of the skeleton”*. Somebody mid-draw is
concentrating on the drawing; a line of small text offering an alternative reads as a fallback for
people who cannot manage. **The same list, seen after you have drawn and named by things you
recognise, reads as an offer** — *I do not actually want this much control over tonight, I want a
tried and tested one.*

**So drawing stays the only way in, and presets are what you notice once you know what drawing
costs you.**
## Host Button Flow

**Rewritten 2026-09-25 — the host is asked what they want to host before a room exists.**

Clicking **Host** opens a screen headed **“What would you like to host?”** with:

- a **search bar** to search venues;
- two buttons directly below it — **“Host tonight’s plan”** and **“Host with co-hosts”**;
- below those, **five suggested venues**, ranked by **how well they fit tonight's drawn shape**
  and the user's preferences — **not by vibe match (2026-10-01)**. The skeleton always exists by
  the time Host is reachable, so a shape-fit number is always available.

**Searching or picking a venue** opens the venue flow, where “Go here” or “Build my night around this”
generates an outing plan card — that venue alone, or that venue with the other stops around it — and that card
carries **Lock this** and **Host this** like any other.

**“Host tonight’s plan”** (renamed from “Make a custom plan”, 2026-09-30) asks for **nothing**. The skeleton is already drawn and the filters are
already set, so the plan is generated from them, **the room is made and it is hosted** in one tap — entering
through Host is a statement of intent, so there is no second one.

**Renamed 2026-09-30 on the user's call.** It used to be “Make a custom plan”, which earned its name when it ran
the custom flow. Now that the flow has already run, the button does exactly what **“Host this”** on the SHUFFL
screen's plan does — so it is named for what it does. Its sibling is renamed to match: **“Host with co-hosts”**.

**“Host with co-hosts”** (renamed from “Make a custom plan with friends”) opens a screen headed **“Add co-hosts”** with a search bar for usernames.

**What happens when they confirm (rewritten 2026-09-30):**

1. **The room is created immediately** and the host is taken into it. The host is not asked for anything else.
2. **Every co-host is sent an invite**, which appears in **the notifications bar on their home screen** (and as a
   phone notification).
3. **A co-host who accepts is taken straight into the room — and lands on the skeleton game.** They are asked for
   the skeleton and **nothing else**: not distance, not budget, not time. Those are the host's, because they are
   the room's.
4. **They cannot leave the skeleton.** Trying to close or back out of it shows:
   > **“To be a co-host for this room you have to draw your skeleton for the night.”**

   The only way out of the screen is to draw, or to leave the room entirely.
5. **The host watches the count.** **Create Plan is greyed and unclickable**, with a counter beside it — **“1/5”**,
   then **“2/5”** — where the denominator is everyone invited including the host, and the numerator is how many have
   **entered the room and finished a skeleton**. Entering without drawing does not count.
6. **Create Plan goes live only at 5/5.** Then the merged skeleton gives the room its stops and the host picks a venue at each one from the stop list, and the Host button
   goes live with it.

**The room shows who has drawn, as a list (2026-10-01).** Under the blend-style card, every invited person gets a
row: their DP, their name, and a status — **DREW** (in the live colour), **DRAWING…**, or **NOT IN YET** for
somebody who has not accepted the invite. The two unfinished states are dimmed, and each carries the **remove
cross** at the end of its row. This is what makes the *n/5* counter legible: the number says how many, the list
says **who**, and without it the host cannot tell whether to wait or to remove.

**The deadlock, and the way out.** One co-host who accepts and never draws would hold the room forever. There is no
timeout on the skeleton — instead **the host removes them**, with the cross on their row (and the one that already
sits above every person's icon in the room). The counter's denominator drops and Create Plan can go live. No new control is needed; the
existing one is pointed at a new problem.

**The host can still change the window before the plan exists.** The filter button is in the host room until Create
Plan is pressed. Changing the **time window invalidates every skeleton drawn so far** and the counter resets to
0/5, because everyone drew inside a window that no longer exists (`SKELETON_MERGE_V1.md` §7). Distance and budget
do not reset anything.

Everything below — the room itself, co-hosts, the blend style and its colour, the chemistry chip, notifications,
requests sorted into Strong Matches and Others, and the lock — is unchanged.

Once a user clicks on the Host button he’s taken to his host room automatically
Top of the screen: The room name (“User X’s Room) which is editable by clicking on it. Just below the room name will be a floating highlighted button saying “Host Room”. Below that, the main section of the room which includes the icons of all the people (so far only the user in the room) represented by their DP and their vibe for the day below that (their username is also written below that but is only visible to other people in the room and not the user itself). The buttons to Mute/Unmute and Open/Close Camera will be present just below this icon. At the bottom of the room is the “Create Plan” button and just above that the Add Co-Hosts button. In the top left corner the music icon to add music and a cross in the top left corner to end/unhost the room. The notifications button to the centre right margin the screen. The background colour of the room will be the colour palette of the vibe of the user.
If clicked on the Add Co-Hosts Button the user is presented with the option to add people from their SHUFFL Contacts.
If the user clicks on the Create Plan Button before adding co-hosts they’ll get a message “The Plan being created is catered just to you since you haven’t added any co-hosts, do you wish to continue?” and then a yes or no button. **(2026-09-30: where co-hosts have been invited, Create Plan is instead greyed with an “n/5” counter and this prompt never appears — see the Host Button Flow.)** The outing plan is generated using the vibes/blend style of the person/people in the room and will pop up in a card covering 75% of the screen in the centre of the screen with the background (the room) blurred. This card will have the refresh button at the bottom to regenerate the plan and a customize button at the top right corner to customize the look of the event plan card. The refresh button is available only while the room is private. It disappears the moment the room is hosted, and does not come back: people join a public room on the basis of its plan, and a plan that can change after they have joined is not the one they agreed to. (The customize button stays — it changes the look of the card, not the plan.) When clicked away, the outing plan will minimize into a “View Plan” button at the bottom the screen and the Add Co-Hosts button and the Create Plan button will disappear. If clicked on the view plan button it opens the same card as mentioned before and with the same features.
If the user clicks on the Host room button it makes the room public and available for people to view in the list of available rooms and join. If the user clicks on the host room button before adding any co-hosts they’ll be given a prompt which will say “You won’t be able to add any of your friends as co-hosts after hosting this room! Continue?” and a Yes or No button. The host room button stays unhighlighted till the user doesn’t click on create plan. If the user clicks on the host room button before clicking on the Create Plan button they’re given a message saying “You must create a plan for other people to see in order to host the room”. After the user hosts the room the “Room is Public” will flash above the view plan button and the Host Room Button will disappear, along with the refresh button on the plan card. Hosting freezes the plan; locking (below) freezes the room.
Once they add co-hosts into the room the background colour of the room will be changed to the blend style of the room that’s created with the users and the co-hosts according to the blend style colour palette as mentioned in the blend style database and the name of the blend style will appear in the centre of the screen, with the room’s chemistry word as a small chip under it — a psychology tag when one fires (Caught the Spark · Running Hot · Slow Burn · Could Go Late · Our Table · Meet the Room · Table and Floor · Packed but Ours · Buzz, Not Noise · Common Ground · On Our Feet · Settle Then Roam), or Something for Everyone when somebody’s reason is absent at a stop, Open Night when nobody brought a top factor, In Sync when no tag fires — see `CHEMISTRY_V4.md` and `BLEND_STYLE_DATABASE_V3.md` (**corrected 2026-10-05: this cited CHEMISTRY_V2, superseded twice**), with the icons of all the users present in the room surrounding it. If the chemistry is Along for the Ride the host also sees one line: “This is mostly [name]’s night — everyone else is easy.” The chip is computed from the members’ vibe factors alone (plan engine §14.3.4) so it appears the moment a second person is in the room, before any plan exists; it freezes with the plan at hosting. As other people join the room when it’s hosted the same process will repeat with the new blend style (if created with the new people, it can also stay the same) being calculated each time and the background colour changing to it and the new blend style name being updated in the centre of the screen. The chemistry chip does not change after hosting — it freezes with the plan (plan engine §13.6.3a). The plan itself does not change when people join a hosted room — the blend style and colour are the room’s identity, the plan is what everyone joined for. The one room without a plan is an Open Night: it is hosted with no plan card, and it stays that way until somebody draws. **(Corrected 2026-10-05: this said the plan *generates* for everyone the moment anyone is firm on anything. Nothing generates a plan — `MVP_INSTRUCTIONS.md` §2.2. An Open Night now fills the way every other room fills: the merged skeleton gives the stops, the host opens each stop’s list and picks, and the card exists once every stop has a venue.)**
If clicked on the notifications button an animation plays with the screen getting covered with the notifications screen emerging from the right margin of the screen. The notifications screen will display. If a person requests to join the room the host/co-hosts will be notified in the notifications button and also for 5 seconds a closable notification will also pop up at the top of the screen. they will see the list of users that have requested to join (their username, dp and vibe for the day) with two buttons “Accept” and “Decline” next to the names.The requests will be sorted into two sections “Strong Matches” and “Others” by the match in the plan engine §13.6.3: add the person (or the whole capsule) to the room, re-run the blend, and read how much they would shift it, how much they add to what the room already is, and whether they fit the room’s chemistry (a “great” match is a Strong Match; “alright” goes under Others; “poor” is not shown in the list at all — the request is declined automatically with a soft message to the requester). If the user is alone in the room the same match is run against the user’s own vibe. If a person has requested to join with a capsule (see below) the host and co-hosts will see all the names like this: Name of the user that created the capsule at the top and “Accept” and “Decline” next to the name and below that branched under the name of the capsule creator the names and DPs of the people in the capsule. If the host/co-host accepts the capsule creator he automatically accepts everyone in the capsule too.  Capsule approval rule, stated explicitly: a capsule request is approved or declined as a single unit. The host/co-host can only Accept or Decline the whole capsule and cannot approve some capsule members while rejecting others, so the Accept/Decline buttons only ever appear next to the capsule creator’s name and never next to the branched names below it.  Once a user/users are let into the room they have a cross just above their name which when clicked removes them in an instant with a simple yes or no prompt, only the host and co-hosts have access to this cross.
Once the user accepts public users into the room a button with a lock icon appears just above the view plan button. If the host (only the host can see and use this button and not the co-hosts) is satisfied with the people in the room he can click on the lock icon and the people in the room are taken to the newly created room GC which will have its home in the messages/social section of the app and the bar just above the task bar — **the status bar (2026-09-30, see The Status Bar)** — will say “[room name]’s outing plan” which when clicked on opens the “active plan screen”. **That bar is live well before this point now**: it carries the room's status, the skeleton counter, the capsule's state and every outstanding approval.

## Join Button Flow

**Rewritten 2026-09-25.** There is no longer a screen asking “Join Alone” or “Join with Friends”.

**Join first asks the user to draw a skeleton** (see the skeleton game). They draw every time — an average user
joins a room once or twice a day, so it is not a repeated cost, and it is what lets the match compare **their shape
against the room's plan** instead of comparing two sets of cards.

**Then the fifth filter: Place or People (2026-09-30).** Before the player opens, the user picks what matters to
them in the rooms they are about to see. It is a two-way toggle and it changes **what the rooms are sorted and
scored by**:

| | the question it asks | the number behind it |
|---|---|---|
| **Place** | *does this room's night suit me?* | `fit` — how well the room's plan serves the skeleton they just drew |
| **People** | *are these my kind of people?* | `match` — how close the room's blended identity is to theirs |

Both numbers already exist (`OUTING_PLAN_ENGINE.md` §13.6.3 v5 and `CHEMISTRY_V4.md` §8.2), so this filter needs no
new engine work. It also settles something the spec had been guessing at: the player used to be ordered by `fit`
because one of the two had to be picked. **Now the user picks.**

**Under People, the card also carries the disturbance line** — *“you would barely change this room”* — when the
room's blend would hardly move if they joined. It is a separate number from the match and it earns its own line:
tested on 4,000 rooms, only about 40% of the best-matched rooms are also the least-disturbed
(`CHEMISTRY_V4.md` §9), so it is telling the user something the percentage does not.

**Then the room player: the five best-matched rooms, back to back**, with **rewind, play and forward**. Each room
fills the screen and carries:

- the **vibe match percentage with that room, at the top**;
- the **host's DP**;
- the **outing plan**;
- the **pros and cons**;
- the **DPs of the other people in the room**;
- a **background in the room's blend style colour**;
- and **the music the host added to the room, playing**. **Muted by default with a speaker toggle**, remembered
  across sessions — a phone cannot start audio without a tap, and somebody opening this on the metro should not
  be handed sound they did not ask for.

*Play* does not join silently: it opens the **“Requesting to Join: [Room Name]”** box, which carries a cancel, and
for a capsule it opens the capsule-approval flow. *Rewind* is disabled on the first room.

**Forward through all five** and those five, together with the other rooms that match the user's vibe, are shown in
**the list format as before**. The five they skipped sit at the bottom of that list under a **“Skipped”** divider.

**“Join with friends” sits in the top right corner of the room list.** Tapping it opens the capsule screen; once
the capsule is created the room list updates to accommodate it.

**The filters live here, on the Join screen, and there are five of them (2026-09-30): distance, budget, venues,
time and Place-or-People.** Age range, duration and filter-by-vibe are retired, and the filters icon is gone from
the home page. See Filter Settings.

The gate and the grading are unchanged (`OUTING_PLAN_ENGINE.md` §13.4a and §13.6.3): a room is hidden unless its
plan suits this user, and the rest are ordered by fit. An Open Night has no plan and no gate, so it never enters the
player — it appears in the list with its “No direction yet” line.

If the user clicks on “Join with Friends” he’s taken to the SHUFFL Capsule screen with the top of the screen saying “Add people to your SHUFFL capsule”; search bar below that; confirm and cancel button at the bottom of the screen. User can use the search bar to search the names of SHUFFL profiles they have added as friends and add them to their “SHUFFL Capsule”.

**Then the join screen goes blank (2026-09-30).** It carries one line:

> **“Waiting for capsule members”**

**Nothing can be browsed until every capsule member has accepted the invite *and* drawn a skeleton.** The reason is
not politeness, it is that there is otherwise **no way to know what kind of night the people in the capsule want**,
and so no way to match the capsule to a room. A capsule's rooms are matched against **the capsule's merged
skeleton** (`SKELETON_MERGE_V1.md`), and a merge counts drawers only — so a capsule with two undrawn members would
be matched as though those two were not coming.

A capsule member's invite appears in **the notifications bar on their home screen**. Accepting takes them to the
**skeleton and nothing else** — not distance, budget or time, which belong to whoever is hosting the room they end
up in, not to the capsule. The blank screen shows **the DPs of the members still outstanding**, and each DP drops
off as that person finishes drawing, so the capsule creator can see what they are waiting for.

**Two things fall out of this and are worth stating.** A member who declines or is removed simply leaves the
capsule and the count drops. And because capsule members now draw, **a capsule can discover it wants two different
nights before it has looked at a single room** — if two members drew opposed arcs, the “two rooms, not one plan”
offer (`SKELETON_MERGE_V1.md` §5a) fires on the capsule itself. That is the earliest and kindest place it could
possibly fire.

**Once every member has drawn**, the creator is taken to the room player as normal — the list of available public rooms that their and their friends’ merged skeleton matches with, the “SHUFFL Capsule” will be visible in the form of a floating capsule with the DPs of the friends the user added in it and “SHUFFL Capsule” written next to it. If the user adds too many members (more than the remaining capacities in all the rooms that match their vibe to any degree) they’re given the message “Sorry, No rooms currently fit your group of [group size]. Try joining with fewer people or host your own room!”. Again the users will only be shown rooms whose event plan has factor scores at least 70% similar to the event plan that would’ve been formed for the people in the capsule and the user, and where every member of the capsule has at least one stop they can live with (the FLOOR check, run per member against the room’s existing plan). How much the capsule would change the room’s blend style is the host’s check, applied when the request arrives, not a filter on this list. Once the user chooses a room to join by clicking on request to join a box pops up saying “Requesting to Join: [Room Name]” below that, “Waiting for Capsule Approval” and just below that the dps of the people in the capsule listed in a row that haven’t approved the room (as people approve the room their dps disappear from this row) and at the bottom of the box a cancel button. If all the people in the capsule approve the room then finally the host of the room is notified of the request of the capsule to join. Once the user creates the SHUFFL capsule and adds their friends into it the friends they added are notified with the notification appearing in **the notifications bar on their home screen (2026-09-30)** at the invites section saying “X user created a capsule and added you into it” and status below saying **“Draw your skeleton”** until they have, then “Searching for rooms”, if clicked on the notification a box will appear that will say “Searching for rooms” with a buffering animation below it. Once the user chooses a room by requesting to join it the friends in the capsule will be notified again with a box popping up in their screen showing the card for the room (event plan with stops and why each stop suits them/doesn’t suit them (pros & cons) with the top of the box saying “X user has requested to join this room with their capsule” and the bottom left of the box saying “Swipe left to decline”, bottom right of the box saying “Swipe right to accept”. If the friend clicks away from this box will minimize into the notifications section of the messages/social screen. The notification in the messages/social screen of the app will still say “X user created a capsule and added you into it” but the status below that will now say “Requested to join [room name], clicking on this notification will open the same box as mentioned just before this with the option to decline/accept. If the friend declines the room, the user that’s searching for rooms will have the box mentioned earlier (the one that displays the Room name and the dps of the people in the capsule that haven’t joined) disappear from the screen and a message displayed at the top of the screen saying “[name of friend that declined] declined this room”. If the friend ignores the notification for more than 3 minutes they are removed from the capsule and the user that created the capsule sees a message at the top of the screen saying “[name of user removed from the capsule] has been removed from the SHUFFL capsule”. If all the users accept the room the host of the room is notified and if they are accepted they enter the room.
At the top of the list of available public rooms will be a search bar where users can search for names of places, so for example if they search for Big Chill the app will shortlist the rooms which have an outing plan that includes big chill in it. The rooms displayed for the users in the list of available public rooms (whether they join alone or with friends are displayed in the following way: Room name first, blend style of the room next to it with the chemistry word as a chip beside the style (e.g. “Big Room, Loud Night · Got Your Back”; an Open Night shows just “Open Night” in grey with the line “No direction yet — whoever joins with one, sets it”), then the dps of 3 people in the room (or 2 or 1 if there are less than 3 but 3 is the maximum) with a + next to it if there are more than 3 people in the room which when clicked on opens a box which displays all the people in the room with just their username and dp (so if there are 5 people in the room the user would see the dp of 3 people with a “+2” next to it which when clicked on would open a box with the list of all 5 people’s usernames and dps). Then finally a view plan button which displays the stops and why each stop is suitable and not suitable to the user viewing the plan (pros & cons) along with a few photos/videos of each stop.
Whenever a user joins a room (alone or with friends) , they see the room name at the top, with a cross in the top left corner to exit the room and the name of the blend style in the centre of the screen with the icons of all the users present in the room surrounding it and a flashing message at the bottom of the screen saying “Waiting for Host to lock the scene” and just above that the view plan button which when clicked on displays the stops and why each stop is suitable and not suitable to the user (pros & cons) along with a few photos/videos of each stop. With the mute/unmute and open/close camera buttons just below their icon.

## Create Button Flow — retired

**Retired 2026-09-25.** Create no longer exists. A plan for one person is the one already sitting on the SHUFFL
screen, and any plan card can be locked or hosted from wherever it was made.

## The Status Bar

**New section, 2026-09-30.** The bar just above the task bar — the one that used to appear only when a plan was
locked and only said “[room name]'s outing plan” — is now **the app's live status line**, and it carries every
state in which the user is waiting on somebody or somebody is waiting on them. It is always one line, it is always
tappable, and **tapping it always opens the thing it is talking about.**

| state | the bar says | tapping it opens |
|---|---|---|
| **hosting, room open** | **“[Room name]: Active”** | the host room |
| **somebody joins** | **flashes “[User] joined [Room name]”**, then settles back to *Active* | the host room |
| **co-hosts invited, skeletons outstanding** | **“[Room name]: 2/5 skeletons”** — the same counter as the Create Plan button | the host room |
| **capsule created, members outstanding** | **“[User]'s capsule: awaiting members”** | the **blank join screen**, with the outstanding DPs |
| **capsule complete** | **“[User]'s capsule: ready to browse”** | the **room player** |
| **capsule has requested a room** | **“[Room name]: awaiting approval from capsule”** | the room, **blurred**, with the approval box over it |
| **request sent to the host** | **“[Room name]: awaiting the host”** | the room with the *Requesting to Join* box |
| **plan locked** | **“[Room name]'s outing plan”** | the **Active Plan Screen** |

**Every box in the app can now be minimised into this bar and reopened from it.** That is the point of the section:
the user is never trapped in a waiting screen, and never loses track of a wait they walked away from. The two boxes
this matters most for are the capsule's room-approval box and the host-approval box, because both can take minutes.

**Precedence, when more than one state is live.** A **locked plan beats everything** — the night is happening, and
that is the only thing the bar should be saying. Below that, **the most recent state wins**, and the displaced one
is still reachable from the screen it belongs to. *(Mine, not specified — the alternative is a stacked or swipeable
bar, which is more honest and worse to use.)*

### The capsule's room approval, in full

When the capsule creator taps **request to join** on a room:

1. **The creator's screen** — the room's details **blur** and a box opens over them:
   > **“Waiting on approval from the capsule”**

   with the DPs of the members who have not yet decided, dropping off one by one, and a cancel button.
   **Minimising the box** sends it to the status bar as *“[Room name]: awaiting approval from capsule”*.
2. **Every other capsule member** gets **the same room view the creator is looking at**, as a pop-up, headed:
   > **“[Capsule creator's name] is viewing this room”**

   with the full room details underneath — the plan, the pros and cons, the people — and **swipe right to approve,
   swipe left to decline**. Clicking away minimises it into their own status bar and their home notifications.

   **It also shows who else has already decided (2026-10-01)** — a row of the other members' DPs, each marked
   **IN** or **WAITING**. Without it, approving a room feels like voting into a void, and the last person to answer
   has no idea they are the last one holding it up.
3. **If every member approves**, the request is sent to the room's host, and the bar changes to *“[Room name]:
   awaiting the host”*.
4. **If one member declines**, the creator's box disappears and a line shows at the top of their screen: *“[Name]
   declined this room”*. The capsule stays intact and browsing resumes where it left off.

**The three-minute removal rule still applies to the capsule invite, not to this.** A member who ignores the
*invite* for three minutes is removed from the capsule; a member who ignores a *room* is simply waited on, because
by then they are committed and the creator can cancel and pick another room.

## Active Plan Screen

If opened the Active Plan Screen after locking the plan (alone or with friends) the full Active Plan Screen opens up: At the top- [The name of the room]’s/ [The name of the vibe]’s plan; below that, a map displaying the stops in the outing plan along with the location of the user and the other people in the room (in case of join/host) in the form of anonymised icons on the map not meant to represent a singular person. Location sharing rules: live location sharing is opt-in and off by default, and the opt-in prompt appears at the moment the plan is locked. Exact location is never shown to users in a public/hosted SHUFFL room; those rooms show approximate group presence only, meaning an area level cluster indicating the group is near a stop, never individual positions. Individual live tracking is not shown to anyone, in public or private rooms. Any user can turn their own location sharing off at any time from the Active Plan Screen or from Settings, and when they do their icon simply drops off the map without notifying the room. When clicked on a stop, the venue’s page opens up [as mentioned in the venue flow] in a small box just above the stop with why this place is suited to the user along with pros & cons and when clicked on this box it expands to cover the whole screen with a cross button in the top right corner of it to close it; below this, the distance to the first stop (“2.3km to Stop 1”); below that the list of people in the room and their vibe written beside it (if host/join)
Once a user enters a location mentioned in the stops in the event plan and open the active plan screen they’ll see a bouncing camera icon next to the stop which would allow them to open the camera and click a photo/video to post to their story
Once the user reaches the last stop on their event plan the “End Plan” button will become active and will appear besides the bar as mentioned earlier above the navigation screen and also at the bottom of the active plan screen once opened.
If clicked on the End Plan button the user will be prompted to give feedback on each of the locations he visited by rating them out of 5 stars. Each stop’s name will pop up on the screen of the user one after the other and will have a slider with markings of 1 star to 5 star and an optional text box below the slider.

## Venue Flow

The Name of the Place at the top and, if the place fits **the shape the user drew tonight**, “[name of the place] is strongly recommended by us for you.” **in the app’s live colour, naming the stop it would be and the fit number** — *“This is your 11pm · 94”*. **(Corrected 2026-10-01: this carried the user’s vibe name and a vibe match number, and the vibe does not score venues. Naming the stop is also simply more useful — it tells the user where this place would land in a night they have already drawn.)** **(Corrected 2026-10-01: this said “highlighted in green”, and the adopted theme has no green as chrome — `#24E0FF` and `#FFC247` are artwork-only by `THEME_LINEUP.md`’s own rule, and there is no green in the palette at all. The recommendation is the primary thing on this screen, which is exactly what the live colour is reserved for.)** Share button next to this to share it to someone in the app DMs (NEW)
Latest images and videos posted by people of the place below that sort of in an instagram stories format. Content rights rule: only two sources may be shown here, (a) content posted by our own users from inside the app, and (b) media we hold a licence or an official API/partner permission for, such as venue owned media, licensed stock, or a permitted maps/venue API. Web and social media images are never scraped. If no in-app content exists for a place and no licensed media is available, fall back to the venue’s own media or a plain branded placeholder rather than pulling random web pictures. All venue stories and photos pass through moderation before they appear, since they routinely contain other people, and any user who appears in a venue story can report it for removal.
Below that, a sort of pie chart of the vibes that visit this place the most
Below that, a list of friends of the user that the user would enjoy this place the most with according to the blend they form with them and whether this place suits that blend.
Below that sticky notes/reviews left by other users for that place in a pinboard format
Below that, the location link for the place
Two buttons at the bottom of the screen over the venue page, side by side, which stay in that position as the user scrolls through the venue page without hiding the content behind it:
**“Go here”** — see the Go-here card below.
**“Find rooms” (2026-09-23)** — public rooms that have *this venue* in their outing plan. It opens the same **room player** as Join Alone (top five, then the list), filtered to rooms whose plan contains this venue, and passing the same gates, grading and filters. It is the same mechanism as searching a place name from the top of the rooms list, surfaced where the user is already looking at the place. If no room is going there tonight the screen says “No rooms going here tonight” and, underneath, offers the nearest thing it can honestly offer: “3 rooms are going to places like it” — rooms whose plan has a stop of the **same venue type in the same area** — never a room that merely scores similarly.
*THIS SCREEN WILL APPEAR EACH TIME A USER CLICKS ON A PLACE IN THE APP*

## Add People Flow

If a user is about to add someone into their SHUFFL Capsule a box will pop up just above the SHUFFL button with a search bar at the top of the box and the list of all their friends on the app along with their vibe for the day besides their name below it. The friends that haven’t completed their swipe game for the day their names will appear at the bottom of the list with a red message saying “Not Completed Swipe” besides their name and the user will be unable to add them.
If a user adds friends into their room as Co-Hosts again a box will pop up this time covering most of the screen with a search bar at the top and they’ll again see the list of all their added friends along with their vibe for the day besides their name but the friends that haven’t completed the game can still be added into the room and they will be notified from their phone’s notification saying “X User has invited you to their room, Open the app and find your vibe today to join” and they will be prompted to complete the swipe game before they can join the room. If they don’t open the app and complete the game within 5 minutes they’ll automatically be removed from the room.

**Two gates, not one (2026-09-30), and only the first has a timer.** The **swipe game** gate is the one above: no
vibe for the day, no entry to the room, and five minutes to comply or be dropped. The **skeleton** gate is the new
one and it sits *inside* the room: a co-host who has entered still has to draw before Create Plan can go live, and
**that gate has no timer at all** — the counter simply sits at *n/5* until they draw or the host removes them with
the cross above their icon. The difference is deliberate: a missing vibe means the app cannot read them at all, so
waiting is pointless; a missing skeleton means the plan is incomplete, and a plan is worth waiting for. As friends join the room the background of the room actively changes to the colour palette of the blend style the users present in the room continue to create. So if the user is alone and a friend joins it will change to the colour of the blend style that they form together and if another friend joins moments after it will change once again to the colour that those 3 form together and so an and so forth. The blend style name will also pop up and change below the room name as people continue to join (the same applies for when the room is hosted and other users join from the list of public rooms).

## Background Colour

The background colour of the room is initially the colour palette for the vibe of the user
As other people continue to be added the background colour keeps changing to the colour palette of the new blend style that’s created with the users in the rooms
## Music Flow

If clicked on the music icon in the top left corner of the room a box will pop up
At the top of the box will be a search bar
Below that, text saying  “These tunes are catered to your vibe today”
Below that, a list of songs that suit their vibe today
Once the user selects a song that song starts playing in the room and represented by a spinning record in the centre of the screen that fades in and out with the view plan button
## Messages Flow

**Reorganised 2026-09-30 — this was the Messages/Social Flow, and the social half moved to the home screen.**
**This screen is now messages and nothing else.** Top to bottom:

1. **A search bar**, searching **through messages** — DMs and group chats, by person, group name or message text.
2. **DMs, Instagram style**, from the user's friends, and the SHUFFL group chats.
3. **The animated SHUFFL button**, top right, which still starts a group — the group-chat flow below is unchanged.

**Moved to the home screen:** the stories rail, the notifications bar (friend requests, room invites, capsule
invites) and the “what your friends are up to” carousel. **Why:** the three-screen split is now clean — **home is
social, SHUFFL is going out, messages are messages** — and a notifications bar buried under a stories rail inside a
DM list was the single most overloaded surface in the app.

Everything below describes the group-chat flow, which is unchanged and still lives here.

*(retained for reference — the stories rail and notifications bar described in the next paragraph now render on the
home screen, not here)*

Below that, notifications bar: Where all the friend requests and active room invites and and everything sit as follows- The capsule invite has been described previously; The room invite will say “X User Invited you to their room [room name” and if the user clicks accept and hasn’t completed their swipe game today, they will be taken to the room and they’ll see the room blurred in the background with the swipe game in the foreground. Once they’ve completed the swipe game the room flow for them will start. If they’ve already completed the swipe game they’ll directly be taken to the room and the room flow will start.
Below that, DMs instagrams style from the user’s friends
Top right corner of the screen just above the stories, an animated SHUFFL button which when clicked on opens a screen. Top of the screen says “SHUFFL with friends” and a list of their friends below that and a continue button at the bottom. Once they’ve selected the friends they want to add and clicked on the continue button they’re then taken to the next screen where they’re prompted to “Name this gathering” and give the group a name. After they’ve done that a gc is created with the group name which is visible in the overall list of dms. Once this gc is opened it has the group name at the top, a message bar at the bottom, and **an insights panel in place of the old Create button (2026-10-06)**.

> **The SHUFFL group chat no longer makes outing plans.** The Create button generated one from everyone's vibes, and it was **the last way a plan could come into existence outside the Play flow**. Since the unlock sequence now collects the filters and the shape after Play, a second generator in the group chat described a path that no longer exists. **No plans, no shapes, no skeletons in a group chat.**

**What a group chat gives instead, and it is the better feature:**

1. **The chemistry of this group** — what the five of you are like on a night out, as a headline and a few lines. This is `CHEMISTRY_V4` run at *n* people rather than two, so it is `MVP_INSTRUCTIONS.md` §4's profile read generalised: **the same engine, no new machinery**, and `chem4.py` already does it at any size. Whose room this would be, where you would split, what you would trade off.

2. **A venue the group would all like**, from **their going-out history and their preferences**. **This needs no skeleton and no hour, because it is not a stop** — it is a statement about a place, not a position in a night, so there is nothing to be open at. It also does not breach §0 of `VENUE_DATABASE_V1.md`: preferences are explicitly how a venue gets chosen, and history is behaviour rather than vibe. **The identity factors still never touch a venue.**

**Cold start, and the honest behaviour.** The venue line needs history, and locked plans already record the venues and areas people went to — but **a group of friends who have just installed the app has none**. In that state the chat shows **chemistry only** and says nothing about venues, rather than guessing from preferences alone and dressing it up as a recommendation. The venue line appears when there is something real behind it. *(This is a judgement call, 2026-10-06, and it is reversible: the alternative is a weaker preference-only line from day one.)*

**What is kept from the old behaviour:** the group is still created the same way — pick friends, name the gathering — it still appears in the DM list, and **the group's preferences are still learned over time**, which now sharpens the insights instead of the plans. **What is gone:** the Create and Recreate buttons, the generated plan as a photo message, *Add to your active plan screen*, and the notification chasing people to get their vibe so a plan can be built. A person who has not played today simply has no vibe in the chemistry read, and the panel says so.
Apart from this a Search Icon will also be present in the top right corner
If clicked on this search icon it opens up a up a search screen with a search bar at the top saying “Add people or Search Places that might suit your group”
Once a user searches the name of a person their profile pops up as normal with a new “Add to [group name]” as a hovering button at the top of the screen. If clicked on it sends an invite to the user: “[user name] has added you to their gc- [gc name]” and then a decline/accept button below that is the same as room invitations in the messages and social of the invited user.
If they search the name of the place, the same venue flow pops up of that place but instead of the pros & cons of the user, the pros & cons for the gc are shown and the vibe score for the gc is shown instead of just the user. A new “Go here” hovering button will be at the top of the venue screen now which when clicked on makes a room with all the people in the GC same as a normal room when a user clicks on “host”. This time with the outing plan in the view plan button only containing the venue they chose and the lock plan button in the same place which when clicked on would not create any GC since the GC already exists and the outing plan would become active in the outing plan screen. The host button will be at the top and the user can choose to host the room for other people to view and join. Once the user clicks on host a new edit icon will appear next to the room name (which would’ve originally been the name of the SHUFFL GC) for the user to change the room name. The blend style of the room originally will be the blend style of the SHUFFL GC but when the room is hosted and other people join the blend style will change to the blend style of the vibes of the other people in the room along with the one’s in the original SHUFFL GC. In this scenario once the plan is locked a new gc will be created with the new room name and with the other people that join once the room is hosted.
So let’s say I make a SHUFFL gc with 3 friends and click on the search icon. I search the name Bohca and the venue name comes up. I click on the venue and in the venue screen I click on “Go here”, a room will be made with the people in the GC and I can choose to host this room for other people to join with the outing plan just containing Bohca.
**The Go-here card (2026-09-23).** “Go here” no longer drops the venue straight into the active plan. It opens a card for that venue first: the venue name and type in plain words, its **pros and cons for the group** in the two-lines-per-person form the plan card uses (a vibe line and a preference line each), the price rating, and the dish and drink recommendation if there is one. Two buttons at the bottom:
**Lock** — the plan is this one venue, and it goes to the Active Plan Screen. This is the old behaviour of “Go here”, unchanged: the room is created from the people in the GC, the host button sits at the top, and the user may host it for others to join.
**“Build my night around this”** — the app generates a full outing plan **with this venue kept as one of the stops** (plan engine §14.6). The card refreshes into the normal plan card with the pinned venue marked by a small pin, and the lock button then locks the whole night. Where the pinned venue falls in the order is decided by its energy, like any other stop — a restaurant opens the night, a club closes it.
Two honest cases the card has to handle rather than hide. **(Revised 2026-09-30.)** If the room's **merged skeleton
is one stop** tonight, “Build my night around this” would produce the same thing as Lock, so the button is greyed
with the line “Your night is one place tonight”. And if the pinned venue sits badly against what somebody in the
group wants — a club when somebody is a firm talker — the card **still says so before the user commits**: “Bela
won't hear anyone here. Build the night around it anyway?”, with the choice left to the user.

**The second case is now a warning and not a veto.** The talk floor was retired on 2026-09-30
(`CHEMISTRY_V4.md` §2) because it protected people from a plan the engine *inferred* for them, and nothing is
inferred any more. The line on the card is the part worth keeping: **tell the user what they are choosing, then let
them choose it.**

## Home Page

If not completed vibe swipe game: Home page features blurred with lock icons and if user clicks on one the app takes them to the vibe swipe game. In the foreground at the top of the screen, an active floating button flashes with the username of the user written on it and beside it a confused/thinking emoji. if they click on the button it will expand and open the Profile screen.
After completing the swipe game: The active floating button will now flash their username and beside it their vibe for the day and the emojis associated with it.
**The filters icon is no longer here (2026-09-25)** — filtering belongs to the Join screen, where it has something to filter.
**Reorganised 2026-09-30 — the home screen is now the social hub.** Top to bottom:

1. **The search bar**, which here searches **profiles** — people. Venue, event and heatmap search moved to the
   SHUFFL screen (see Search Bar Flow).
2. **Stories**, Instagram style, from the people the user follows — moved here from Messages.
3. **The notifications bar** — friend requests, room invites, **co-host invites** and **capsule invites** — moved
   here from Messages. Two of these now take the user somewhere specific when accepted **(2026-09-30)**:
   - a **co-host invite** drops them into the room, **on the skeleton**, which they cannot leave until they draw;
   - a **capsule invite** opens the skeleton, and shows *“Draw your skeleton”* as its status until they have.

   Neither asks for distance, budget or time — those belong to whoever started the thing. Everything else about
   invite behaviour is unchanged and is described in the Messages Flow.
4. **“What your friends are up to”** — the carousel described below.
5. **The user's own posts and their friends' posts.**

**Moved to the SHUFFL screen:** “What's poppin right now that suits your vibe”, suggested venues, and “Explore
other vibes” (the heatmaps). **Everything about a venue is now on one screen and everything about a person is on
the other**, which is also why the search bar had to split in two.
(The following section will only be displayed if the user has added friends): “What your friends are up to:” This section will display the rooms their friends are part of at that moment and if they have active rooms they have hosted themselves. This section will list a carousel of different rooms with each room displayed the following way: “XYZ friend hosted this room” or “XYZ friend joined this room” at the top, room name just below that with the Host name just beside the room name ([room name] by [host name]), blend style of the room just below that highlighted in the font colour of the blend style colour palette of that particular blend style (if a friend has hosted a room there will also be a join button at the bottom to request to join the room only if the room has remaining capacity and the room passes the same gate and match as the public-room list (plan engine §13.4a and §13.6.3); a friend’s Open Night room has no plan and no gate, so its join button always shows, with the “No direction yet — whoever joins with one, sets it” line under the room name; if the user doesn’t pass the gate or the room is at full capacity the join button will not be there). Users can switch off the ability for other people to see this in their “What your friends are up to:” section in the privacy setting in settings.
*(The heatmap section below now renders on the SHUFFL screen, not here. Its privacy rules are unchanged and are
kept here as the canonical statement of them.)*

“Explore other vibes”: (If user clicks on this he’ll be taken to a screen where he’ll be shown the heatmap for his vibe where he’ll be able to view which places other people belonging to his vibe are visiting the most today such as “The party monster heatmap” and below that a button saying “view other heatmaps” which when clicked will show locations on the map where people belonging to other vibes are visiting the most for each vibe one by one below one another in a similar fashion)  Heatmap privacy rules: an area is only rendered on a heatmap once a minimum threshold of distinct users is present in it (threshold tbd, suggested 20 or more), so small groups can never be resolved. Data is displayed at area/neighbourhood level, never at exact venue level, unless a venue clears a much higher user threshold. No individual identity, DP or username is ever exposed on a heatmap, and no icon on a heatmap is tappable through to a person. Users can opt out of contributing their visits to heatmaps from Settings. Heatmap data is aggregated and deliberately delayed (suggested 30 to 60 minutes) rather than live, so the feature can never be used as live tracking.

## Task Bar

Home Button to the left — **the social hub** (2026-09-30)
Play Button in the middle — opens **the SHUFFL screen**
Messages Button to the right — **messages only** (2026-09-30)

## Profile Screen

“[Name]’s vibe profile” at the top
Settings Icon in the top right corner which when clicked opens the Settings Page Flow
Music icon in the top left corner which when clicked on opens the same Add music flow. Once a user clicks on the music that they want to add, each time another user opens their profile they’ll hear that song, with the ability to mute.
Below that, DP which when clicked on opens the stories (instagram style) the user posted recently
Below that, “[vibe for the day] today”, example “Peak Mingler today”
Below that, the user’s **badges** — one for each preference they marked “the whole point”: Foodie, Gig-Goer, Dressed For It (or Hype), Good Eye, First Timer, Old Soul, **Always On The Table (2026-09-30)** — as small chips; none if none.
Below that, **“What I care about in a place”** — a row of **seven (2026-09-30)**: food, a live act, dressed-up, the look, somewhere new, somewhere old, something to play — each showing its current level (The whole point / Nice to have / Don’t mind / Don’t care) and tappable to change it; a “Redo my preferences” link under the row re-runs the preference deck. These never change on their own.
Below that, Bio
Below that, Pinboard, which includes the stories that the user pinned appearing there from any time in their history of using the app.
Below that, “Past Events” and just below that the list of event plans they’ve been a part of listed as buttons row wise in a creative way (tbd). If clicked on any one of these event plan buttons it expands a little to display the stops that that particular event plan had along with the usernames of the people that were a part of it
Below that, their vibe history. This will be a pie chart of the vibes that they had the most
Just below that, “Your Overall Going Out Type Is:” and this will mention their overall going out type
Below that, “Friends you vibe the most with:” , this will list the friends that had the most same/similar vibes as them out of all their friends over the course of the user using the app.

## Search Bar Flow

**Split in two, 2026-09-30.** There are now two search bars with different scopes, matching the screen split:

| where | searches |
|---|---|
| **home screen**, at the top | **people** — profiles |
| **SHUFFL screen**, above Host and Join | **venues, events and heatmaps** |

Heatmaps follow the venues to the SHUFFL search, not the people to the home search — a heatmap is a statement about
places. Everything below applies to both bars; only the result types differ.

Users can use the search bar to look for other users, locations and heatmaps
Once a user clicks on the search bar the screen changes to only occupy the search bar at the top which will now be highlighted and the rest of the screen blank.
As the user begins to type in their search terms the app will start narrowing down the results as is done in other search bars
The results that show up will have a score next to them, and **what the score means depends on what was found (2026-10-01)**. For a **person**, it is the vibe match — how similar their identity factors are to the user's today. For a **place**, it is **not a vibe score at all**: it is how well that venue fits **the shape the user drew tonight**, at the hour it would fall, plus their preferences. The two numbers look alike on screen and come from completely different places, and only the first one is about anybody's vibe. Heatmaps appear as is, with the name of the heatmap mentioned, for example, “The Sunlit Brunch Friends Heatmap”Privacy controls: what other people can see about a user is controlled by that user from Settings, with separate toggles for today’s vibe, their vibe score against the viewer, their overall going out type, their vibe history and their past events. Each toggle can be set to Everyone, Friends only, or Nobody. If a user hides their vibe they still appear in search results, just without a vibe score attached, rather than disappearing from search. These settings apply consistently everywhere the same data surfaces: search results, the Profile Flow, the View Profile Flow, and the “Friends you vibe the most with” section.

## Outing Plan Flow

The main contents of the outing plan card as mentioned earlier in different occasions will appear like this
~~Duration slider just above the card~~ **Retired 2026-10-01 — see the SHUFFL Screen.** The night's length is the
window (a start and an end) set in the unlock sequence, and changing it after people have drawn invalidates their
skeletons, so it cannot live on a card.
Title of the event plan at the top of the card which is editable
“Start off with”, and then the first stop mentioned
Just below the stop is the description of the place
Just below the description is the reason why this place is great for whichever user is viewing the outing plan card
Just below that the reasons why this location favours each person in the group is mentioned, “For X friend there are cocktails for Y friend there are delicious desserts” — **two lines per person** now: a vibe line from the shape of the night (“for Aarav — it builds from here”, “for Bela — you can hear each other”, “for Chirag — something to play”; or, where the street rather than the venue is carrying it, “the street outside is buzzing”) and a preference line from the venue (“the food’s good”, “there’s a set at ten”, “nobody’s been”). The plan engine returns the factor and where it came from; the app turns them into words. Above the per-person lines, the stop’s **type** in plain words — “a games bar”, “a quiet bar”, “a club” — and, when the room is a Settle Then Roam, the stop’s **hours** (“8 to 11”) — along with this a seating suggestion based on the affiliation score of the group, for example, “ask for a seat close to the bar as it matches your group vibe and you’ll be able to socialise more!”. Under the per-person lines, the card can carry up to three short notes per stop, all read straight off how the night was designed (plan engine §14.3 v4) — there is no easing, no ⓘ, no payback and no stop that is one person’s: (1) **a stand-in note**, when somebody’s second-favourite factor is what keeps them present at a stop because the room’s reading went the other way on their top — “Aarav’s here for the crowd tonight; the room’s a calm one” — one line, in plain words; (2) **a to-a-degree note**, when a person’s top factor is present at this stop but not fully — the place is on their side of the middle rather than inside what they asked for — “Some energy here for Arjun; more at the next stop” (the app knows where it *is* fully served, and says so if it is anywhere in the night); (3) **an absent note**, rare, when no kind of place could carry a person’s top factor together with everyone else’s at this stop — “No games here for Chetan — nowhere does games, a floor and a quiet table at once” — plain, never hidden, and never turned into a separate stop for that person. A person with no strong wants tonight (everything of theirs in the middle) gets their vibe line from bend rather than from a top factor: “Divit’s easy tonight.” Whole-point preferences the night could not serve anywhere get one line at the bottom of the card, not under a stop: “No live music tonight — none of the places on this shape has an act.”
Just below that, A price rating similar to google maps like 2 rupee symbols out of 3 for example
Just below that, button to view menu, if the place is food/cocktail centric
Just below that, “Have you been here before?” with a “yes” and “no”. If the user clicks on yes the app will not add any novelty points and if the user clicks on no the app will add up to 5 points for novelty. This will help when the user clicks on regenerate and has to be suggested a new alternative.
Below that, “Stop for/Swing by…etc.” depending on the nature of the plan and then the second stop mentioned
Same things below this stop as the first stop
And so on and so forth
Finally, a regenerate button at the bottom to get a new stop suggestions

## View Profile Flow

If a user views a person’s profile or if a person views the user’s profile this is what they see
Name at the top
Add option at the top right corner to send a friend request
Below that, DP which when clicked on opens the stories (instagram style) the user posted recently
Below that, “[vibe for the day] today”, example Candlelight Romantic today
Below that, Bio
Below that, Pinboard, which includes the stories that the user pinned appearing there from any time in their history of using the app.
Below that, Past Events and just below that the list of event plans they’ve been a part of listed as buttons row wise in a creative way (tbd). If clicked on any one of these event plan buttons it expands a little to display the stops that that particular event plan had along with the usernames of the people that were a part of it
Below that, their overall going out type mentioned
## Settings Flow

Relevant Settings for this app suggested by AI
Privacy settings that must exist (required by the flows above): live location sharing, off by default with a per-plan opt-in; heatmap contribution opt-out; visibility toggles set to Everyone / Friends only / Nobody for past events; story and venue-post visibility plus a report/remove option for stories you appear in; and controls over who can add you to a SHUFFL capsule or invite you to a room.

## Dish/Drink Recommendations

The database of vibes will also contain a fixed recommended dishes/drinks alongside them.
The outing plan is generated for the user and it’s reflected in the active plan screen, after that once the user enters the location of any of the stops in the outing plan a box pops up in his screen that says “you have arrived at [location name] and below that “We strongly recommend you try the [dish name] and wash it down with a [cocktail/mocktail name] for your vibe!” and an Order Now button at the bottom which will take them to the payment gateway allowing them to order it in advance if the restaurant is registered on SHUFFL for business. The dish and drink will be presented side by side in sort of a tabular format with the name and photo of the dish/drink and a description of why it suits their vibe below it and the percentage match score.
This will be done by the program going through the menu for the location and finding the same or similar drink/dish for the vibe of the user as mentioned in the vibes database.
This dish and drink recommendation will now be found by clicking on a new drink and dish emoji next to the stop in the active plan screen which opens up a box that has the “[user’s vibe]’s recommended dish and drink at [location name]’ at the top and a picture of the dish and drink along with its name below that and a description of why it suits their vibe.

## Filter Settings

**Rewritten 2026-09-25, extended 2026-09-30. Five filters, and they live on the Join screen**, not on the home page.
The first three are the same sliders the unlock sequence sets — the Join screen lets a browsing user narrow them
further without redrawing:

1. **Distance** — a slider in km. Only rooms whose plans fall inside the radius are shown.
2. **Budget** — a slider from ₹500 to “no budget”, with ₹25k the last value before it. A room is shown only if
   the user's budget clears **the lowest budget of anyone in it**.
3. **Venues** — filter to rooms whose outing plan contains a particular venue.
4. **Time** — **the start and end window** (2026-09-30). A room is shown only if its window overlaps the user's.
5. **Place or People** (2026-09-30) — the two-way toggle described in the Join Button Flow. Not a filter that
   removes rooms: it changes **what the remaining rooms are sorted by**, `fit` or `match`. It sits with the filters
   because that is where the user is already deciding what they want, and it is the only one of the five that
   changes the order rather than the set.

**Retired:** age range, duration, and filter-by-vibe. The vibe filter went because the gate and the match already
decide which rooms suit a person, and filtering people out by their vibe name did the same job twice and worse.
