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
“First, the things you care about in a place.” Below that, one line: “Swipe on the following things on the basis of how important they are to you in a place.” Below that a “Let’s go” button. This opens the **preference deck** (see Swipe Game Flow, preference deck): six cards, each a plain image of the thing — food, a live act, a dressed-up room, a beautiful room, an unmarked door, an old building — swiped four ways with the labels **The whole point** (gold, up) · **Nice to have** (green, right) · **Don’t mind** (grey, left) · **Don’t care** (red, down). After the dressed-up card, one image pair: “Which of these is dressed-up, to you?” — a suits-and-dresses room, a streetwear room, or “both” — tap one. These answers go to the profile and stay there until the user edits them; they are never asked again on a normal day.
“Now — tonight.” Goes straight to the vibe swipe game (see Swipe Game Flow).
“Looks like your vibe today is: [User’s vibe]” — a two-word shape of a night, e.g. “Peak Mingler”, “Quiet Table-Talker”, or a single name like “Night Climber” (see VIBE_NAMES_V4); below that, what that vibe says about them
“Your profile is ready for you to set up”; below that, Display profile the same way as described in the Profile Flow below with options to edit an empty dp, empty bio and show everything else according to the only information we have of the user so far which is their first vibe; below that, button to “Skip For Now” to complete their profile later.
## Swipe Game Flow

There are two decks. The **preference deck** is shown once, at onboarding (and again only if the user chooses “Redo my preferences” in the profile): six cards plus one image pair, each card a plain image of the thing, swiped **The whole point / Nice to have / Don’t mind / Don’t care**. It uses the same card screen, the same Next and Back, the same progress bar and the same silent timing as the vibe deck below; only the labels and the images differ, and there is no second card per preference. The **vibe deck** is the daily one and is everything that follows.

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

The deck adapts to the user's answers. Every vibe factor — there are seven: energy, who you face,
how full, whether you can talk, how many places, on your feet or not, something to play — starts
with one card. If the user swipes **Love** or **Hard Pass**, that factor is done. If the user swipes
**Up For It** or **Not For Me**, a second card for that factor — a different angle on the same idea
— joins the deck a few cards later. So a decisive user sees seven cards; a user who leans mildly
on everything sees fourteen; most people see around ten. The user is never told any of this; they
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

If a user clicks on the play button at any point, three buttons will pop up above the task bar with each having their own creative animations and lettering: Host, Join or Create.

## Host Button Flow

Once a user clicks on the Host button he’s taken to his host room automatically
Top of the screen: The room name (“User X’s Room) which is editable by clicking on it. Just below the room name will be a floating highlighted button saying “Host Room”. Below that, the main section of the room which includes the icons of all the people (so far only the user in the room) represented by their DP and their vibe for the day below that (their username is also written below that but is only visible to other people in the room and not the user itself). The buttons to Mute/Unmute and Open/Close Camera will be present just below this icon. At the bottom of the room is the “Create Plan” button and just above that the Add Co-Hosts button. In the top left corner the music icon to add music and a cross in the top left corner to end/unhost the room. The notifications button to the centre right margin the screen. The background colour of the room will be the colour palette of the vibe of the user.
If clicked on the Add Co-Hosts Button the user is presented with the option to add people from their SHUFFL Contacts.
If the user clicks on the Create Plan Button before adding co-hosts they’ll get a message “The Plan being created is catered just to you since you haven’t added any co-hosts, do you wish to continue?” and then a yes or no button. The outing plan is generated using the vibes/blend style of the person/people in the room and will pop up in a card covering 75% of the screen in the centre of the screen with the background (the room) blurred. This card will have the refresh button at the bottom to regenerate the plan and a customize button at the top right corner to customize the look of the event plan card. The refresh button is available only while the room is private. It disappears the moment the room is hosted, and does not come back: people join a public room on the basis of its plan, and a plan that can change after they have joined is not the one they agreed to. (The customize button stays — it changes the look of the card, not the plan.) When clicked away, the outing plan will minimize into a “View Plan” button at the bottom the screen and the Add Co-Hosts button and the Create Plan button will disappear. If clicked on the view plan button it opens the same card as mentioned before and with the same features.
If the user clicks on the Host room button it makes the room public and available for people to view in the list of available rooms and join. If the user clicks on the host room button before adding any co-hosts they’ll be given a prompt which will say “You won’t be able to add any of your friends as co-hosts after hosting this room! Continue?” and a Yes or No button. The host room button stays unhighlighted till the user doesn’t click on create plan. If the user clicks on the host room button before clicking on the Create Plan button they’re given a message saying “You must create a plan for other people to see in order to host the room”. After the user hosts the room the “Room is Public” will flash above the view plan button and the Host Room Button will disappear, along with the refresh button on the plan card. Hosting freezes the plan; locking (below) freezes the room.
Once they add co-hosts into the room the background colour of the room will be changed to the blend style of the room that’s created with the users and the co-hosts according to the blend style colour palette as mentioned in the blend style database and the name of the blend style will appear in the centre of the screen, with the room’s chemistry word as a small chip under it — a psychology tag when one fires (Caught the Spark · Running Hot · Slow Burn · Could Go Late · Our Table · Meet the Room · Table and Floor · Packed but Ours · Buzz, Not Noise · Common Ground · On Our Feet · Settle Then Roam), otherwise the formation word (In Sync · Got Your Back · Best of Both · Along for the Ride · Something for Everyone · Open Night) — see CHEMISTRY_V2 and the plan engine §14.3.5b, with the icons of all the users present in the room surrounding it. If the chemistry is Along for the Ride the host also sees one line: “This is mostly [name]’s night — everyone else is easy.” The chip is computed from the members’ vibe factors alone (plan engine §14.3.4) so it appears the moment a second person is in the room, before any plan exists; it freezes with the plan at hosting. As other people join the room when it’s hosted the same process will repeat with the new blend style (if created with the new people, it can also stay the same) being calculated each time and the background colour changing to it and the new blend style name being updated in the centre of the screen. The chemistry chip does not change after hosting — it freezes with the plan (plan engine §13.6.3a). The plan itself does not change when people join a hosted room — the blend style and colour are the room’s identity, the plan is what everyone joined for. The one room without a plan is an Open Night: it is hosted with no plan card, and the moment anyone in it is firm on anything (usually the first decisive joiner) the plan generates for everyone then in the room and freezes exactly as if the room had just been hosted.
If clicked on the notifications button an animation plays with the screen getting covered with the notifications screen emerging from the right margin of the screen. The notifications screen will display. If a person requests to join the room the host/co-hosts will be notified in the notifications button and also for 5 seconds a closable notification will also pop up at the top of the screen. they will see the list of users that have requested to join (their username, dp and vibe for the day) with two buttons “Accept” and “Decline” next to the names.The requests will be sorted into two sections “Strong Matches” and “Others” by the match in the plan engine §13.6.3: add the person (or the whole capsule) to the room, re-run the blend, and read how much they would shift it, how much they add to what the room already is, and whether they fit the room’s chemistry (a “great” match is a Strong Match; “alright” goes under Others; “poor” is not shown in the list at all — the request is declined automatically with a soft message to the requester). If the user is alone in the room the same match is run against the user’s own vibe. If a person has requested to join with a capsule (see below) the host and co-hosts will see all the names like this: Name of the user that created the capsule at the top and “Accept” and “Decline” next to the name and below that branched under the name of the capsule creator the names and DPs of the people in the capsule. If the host/co-host accepts the capsule creator he automatically accepts everyone in the capsule too.  Capsule approval rule, stated explicitly: a capsule request is approved or declined as a single unit. The host/co-host can only Accept or Decline the whole capsule and cannot approve some capsule members while rejecting others, so the Accept/Decline buttons only ever appear next to the capsule creator’s name and never next to the branched names below it.  Once a user/users are let into the room they have a cross just above their name which when clicked removes them in an instant with a simple yes or no prompt, only the host and co-hosts have access to this cross.
Once the user accepts public users into the room a button with a lock icon appears just above the view plan button. If the host (only the host can see and use this button and not the co-hosts) is satisfied with the people in the room he can click on the lock icon and the people in the room are taken to the newly created room GC which will have its home in the messages/social section of the app and a new bar sort of like the active cart in the zomato app just above the task bar will appear which will say “[room name]’s outing plan” which when clicked on opens the “active plan screen”.

## Join Button Flow

If the user clicks on Join they’re taken to the Join screen which just has two buttons adjacent to one another with one saying “Join Alone” and the other saying “Join with Friends”
If clicked on “Join Alone” it takes the user to the list of available public rooms. A public room already has its outing plan, so the only question for this list is whether that plan suits the user. Two checks, both on the user alone — nothing here reads the other members of the room: (1) the room’s plan has factor scores at least 70% similar to the plan that would have been generated for the user’s vibe today, and (2) the plan has at least one stop the user can live with — their worst miss past their own bend at their best stop, the same FLOOR check the plan engine uses, run for this one person against this one plan. Rooms failing either check are hidden — the plan is the gate. Rooms passing both are then graded by the match in the plan engine §13.6.3 — how much the user would shift the room’s blend, how much they add to what the room already is, and whether they fit its chemistry: “great” → “Strong match”, “alright” → “Other rooms”, “poor” → hidden. An Open Night room (nobody in it has a firm opinion yet) has no plan and no gate: it is listed for everyone, and it is the *perfect* match for a user who is firm on five or more factors — they are told “This room’s an open night. You’d be setting the direction.” (The 70% stays as a cheap first filter — decided 2026-09-17; the per-stop check is what actually separates rooms.) How much the user would change the room’s blend style is not this user’s concern at this point; it is the host’s, and it is applied when the host sees the request (see Host Button Flow, notifications).
If the user clicks on “Join with Friends” he’s taken to the SHUFFL Capsule screen with the top of the screen saying “Add people to your SHUFFL capsule”; search bar below that; confirm and cancel button at the bottom of the screen. User can use the search bar to search the names of SHUFFL profiles they have added as friends and add them to their “SHUFFL Capsule”. After the user has clicked confirm after adding their friends they’re taken to the list of available public rooms that their and their friends’ vibes match with, the “SHUFFL Capsule” will be visible in the form of a floating capsule with the DPs of the friends the user added in it and “SHUFFL Capsule” written next to it. If the user adds too many members (more than the remaining capacities in all the rooms that match their vibe to any degree) they’re given the message “Sorry, No rooms currently fit your group of [group size]. Try joining with fewer people or host your own room!”. Again the users will only be shown rooms whose event plan has factor scores at least 70% similar to the event plan that would’ve been formed for the people in the capsule and the user, and where every member of the capsule has at least one stop they can live with (the FLOOR check, run per member against the room’s existing plan). How much the capsule would change the room’s blend style is the host’s check, applied when the request arrives, not a filter on this list. Once the user chooses a room to join by clicking on request to join a box pops up saying “Requesting to Join: [Room Name]” below that, “Waiting for Capsule Approval” and just below that the dps of the people in the capsule listed in a row that haven’t approved the room (as people approve the room their dps disappear from this row) and at the bottom of the box a cancel button. If all the people in the capsule approve the room then finally the host of the room is notified of the request of the capsule to join. Once the user creates the SHUFFL capsule and adds their friends into it the friends they added are notified with the notification appearing in the messages/social section of their app at the invites section saying “X user created a capsule and added you into it” and status below saying “Searching for rooms”, if clicked on the notification a box will appear that will say “Searching for rooms” with a buffering animation below it. Once the user chooses a room by requesting to join it the friends in the capsule will be notified again with a box popping up in their screen showing the card for the room (event plan with stops and why each stop suits them/doesn’t suit them (pros & cons) with the top of the box saying “X user has requested to join this room with their capsule” and the bottom left of the box saying “Swipe left to decline”, bottom right of the box saying “Swipe right to accept”. If the friend clicks away from this box will minimize into the notifications section of the messages/social screen. The notification in the messages/social screen of the app will still say “X user created a capsule and added you into it” but the status below that will now say “Requested to join [room name], clicking on this notification will open the same box as mentioned just before this with the option to decline/accept. If the friend declines the room, the user that’s searching for rooms will have the box mentioned earlier (the one that displays the Room name and the dps of the people in the capsule that haven’t joined) disappear from the screen and a message displayed at the top of the screen saying “[name of friend that declined] declined this room”. If the friend ignores the notification for more than 3 minutes they are removed from the capsule and the user that created the capsule sees a message at the top of the screen saying “[name of user removed from the capsule] has been removed from the SHUFFL capsule”. If all the users accept the room the host of the room is notified and if they are accepted they enter the room.
At the top of the list of available public rooms will be a search bar where users can search for names of places, so for example if they search for Big Chill the app will shortlist the rooms which have an outing plan that includes big chill in it. The rooms displayed for the users in the list of available public rooms (whether they join alone or with friends are displayed in the following way: Room name first, blend style of the room next to it with the chemistry word as a chip beside the style (e.g. “Big Room, Loud Night · Got Your Back”; an Open Night shows just “Open Night” in grey with the line “No direction yet — whoever joins with one, sets it”), then the dps of 3 people in the room (or 2 or 1 if there are less than 3 but 3 is the maximum) with a + next to it if there are more than 3 people in the room which when clicked on opens a box which displays all the people in the room with just their username and dp (so if there are 5 people in the room the user would see the dp of 3 people with a “+2” next to it which when clicked on would open a box with the list of all 5 people’s usernames and dps). Then finally a view plan button which displays the stops and why each stop is suitable and not suitable to the user viewing the plan (pros & cons) along with a few photos/videos of each stop.
Whenever a user joins a room (alone or with friends) , they see the room name at the top, with a cross in the top left corner to exit the room and the name of the blend style in the centre of the screen with the icons of all the users present in the room surrounding it and a flashing message at the bottom of the screen saying “Waiting for Host to lock the scene” and just above that the view plan button which when clicked on displays the stops and why each stop is suitable and not suitable to the user (pros & cons) along with a few photos/videos of each stop. With the mute/unmute and open/close camera buttons just below their icon.

## Create Button Flow

If the user clicks on Create from the play button in the task bar they’ll directly have their outing plan generated just for them using their vibe alone
Once they click it the outing plan will appear in a screen covering the entire screen with a cross in the top left corner to close the screen and go back to the regular homepage.
This Outing Plan Screen will have the background colour of the vibe of the user.
The outing plan will be displayed as normal with the same refresh button, customize button and each stop mentioned along with why it benefits the user’s vibe and photos/videos of the place but with a floating lock button in the bottom
Once the user locks the outing plan in the Outing Plan Screen the same bar sort of like the active cart in the zomato app will appear above the task bar which will say in this case: “[user’s vibe]’s outing plan” which when clicked will open the active plan screen, however if the user doesn’t lock the outing plan and closes the outing plan screen the same bar will say  “[user’s vibe]’s outing plan: Tap to Lock” which when clicked on opens the outing plan screen (not the active plan screen) with the floating lock button, this will be the case until the user has locked the plan.

## Active Plan Screen

If opened the Active Plan Screen after locking the plan (alone or with friends) the full Active Plan Screen opens up: At the top- [The name of the room]’s/ [The name of the vibe]’s plan; below that, a map displaying the stops in the outing plan along with the location of the user and the other people in the room (in case of join/host) in the form of anonymised icons on the map not meant to represent a singular person. Location sharing rules: live location sharing is opt-in and off by default, and the opt-in prompt appears at the moment the plan is locked. Exact location is never shown to users in a public/hosted SHUFFL room; those rooms show approximate group presence only, meaning an area level cluster indicating the group is near a stop, never individual positions. Individual live tracking is not shown to anyone, in public or private rooms. Any user can turn their own location sharing off at any time from the Active Plan Screen or from Settings, and when they do their icon simply drops off the map without notifying the room. When clicked on a stop, the venue’s page opens up [as mentioned in the venue flow] in a small box just above the stop with why this place is suited to the user along with pros & cons and when clicked on this box it expands to cover the whole screen with a cross button in the top right corner of it to close it; below this, the distance to the first stop (“2.3km to Stop 1”); below that the list of people in the room and their vibe written beside it (if host/join)
Once a user enters a location mentioned in the stops in the event plan and open the active plan screen they’ll see a bouncing camera icon next to the stop which would allow them to open the camera and click a photo/video to post to their story
Once the user reaches the last stop on their event plan the “End Plan” button will become active and will appear besides the bar as mentioned earlier above the navigation screen and also at the bottom of the active plan screen once opened.
If clicked on the End Plan button the user will be prompted to give feedback on each of the locations he visited by rating them out of 5 stars. Each stop’s name will pop up on the screen of the user one after the other and will have a slider with markings of 1 star to 5 star and an optional text box below the slider.

## Venue Flow

The Name of the Place at the top and if the place suits the user’s vibe for the day “[name of the place] is strongly recommended by us for you.” highlighted in green. Share button next to this to share it to someone in the app DMs (NEW)
Latest images and videos posted by people of the place below that sort of in an instagram stories format. Content rights rule: only two sources may be shown here, (a) content posted by our own users from inside the app, and (b) media we hold a licence or an official API/partner permission for, such as venue owned media, licensed stock, or a permitted maps/venue API. Web and social media images are never scraped. If no in-app content exists for a place and no licensed media is available, fall back to the venue’s own media or a plain branded placeholder rather than pulling random web pictures. All venue stories and photos pass through moderation before they appear, since they routinely contain other people, and any user who appears in a venue story can report it for removal.
Below that, a sort of pie chart of the vibes that visit this place the most
Below that, a list of friends of the user that the user would enjoy this place the most with according to the blend they form with them and whether this place suits that blend.
Below that sticky notes/reviews left by other users for that place in a pinboard format
Below that, the location link for the place
A big “Go here” button in the bottom of the screen over the venue page which stays in that position as the user scrolls through the venue page without hiding the content behind it
*THIS SCREEN WILL APPEAR EACH TIME A USER CLICKS ON A PLACE IN THE APP*

## Add People Flow

If a user is about to add someone into their SHUFFL Capsule a box will pop up just above the SHUFFL button with a search bar at the top of the box and the list of all their friends on the app along with their vibe for the day besides their name below it. The friends that haven’t completed their swipe game for the day their names will appear at the bottom of the list with a red message saying “Not Completed Swipe” besides their name and the user will be unable to add them.
If a user adds friends into their room as Co-Hosts again a box will pop up this time covering most of the screen with a search bar at the top and they’ll again see the list of all their added friends along with their vibe for the day besides their name but the friends that haven’t completed the game can still be added into the room and they will be notified from their phone’s notification saying “X User has invited you to their room, Open the app and find your vibe today to join” and they will be prompted to complete the swipe game before they can join the room. If they don’t open the app and complete the game within 5 minutes they’ll automatically be removed from the room. As friends join the room the background of the room actively changes to the colour palette of the blend style the users present in the room continue to create. So if the user is alone and a friend joins it will change to the colour of the blend style that they form together and if another friend joins moments after it will change once again to the colour that those 3 form together and so an and so forth. The blend style name will also pop up and change below the room name as people continue to join (the same applies for when the room is hosted and other users join from the list of public rooms).

## Background Colour

The background colour of the room is initially the colour palette for the vibe of the user
As other people continue to be added the background colour keeps changing to the colour palette of the new blend style that’s created with the users in the rooms
## Music Flow

If clicked on the music icon in the top left corner of the room a box will pop up
At the top of the box will be a search bar
Below that, text saying  “These tunes are catered to your vibe today”
Below that, a list of songs that suit their vibe today
Once the user selects a song that song starts playing in the room and represented by a spinning record in the centre of the screen that fades in and out with the view plan button
## Messages/Social Flow

Top of the screen, instagram style stories of different people that the user follows
Below that, search bar allowing the user to search through DMs
Below that, notifications bar: Where all the friend requests and active room invites and and everything sit as follows- The capsule invite has been described previously; The room invite will say “X User Invited you to their room [room name” and if the user clicks accept and hasn’t completed their swipe game today, they will be taken to the room and they’ll see the room blurred in the background with the swipe game in the foreground. Once they’ve completed the swipe game the room flow for them will start. If they’ve already completed the swipe game they’ll directly be taken to the room and the room flow will start.
Below that, DMs instagrams style from the user’s friends
Top right corner of the screen just above the stories, an animated SHUFFL button which when clicked on opens a screen. Top of the screen says “SHUFFL with friends” and a list of their friends below that and a continue button at the bottom. Once they’ve selected the friends they want to add and clicked on the continue button they’re then taken to the next screen where they’re prompted to “Name this gathering” and give the group a name. After they’ve done that a gc is created with the group name which is visible in the overall list of dms. Once this gc is opened it has the group name at the top, message bar at the bottom to write messages in the group, create button in the top of the screen which when clicked on generates a plan for all the people in the group using their individual vibes for the day and sends it in the group chat in the form of a photo message which has the stops of the outing along w pros & cons for each user in the gc below each stop and an option just below the message to “Add to your active plan screen” in order to add this outing plan to their active plan screen (if it’s added to the active plan screen the outing plan has the same format as other outing plans in the active plan screen).If some of the people in the group haven’t played the swipe game and had their vibe assessed the create button doesn’t open anything and has a buffering animation play on it and the people are sent a notification on their phone “[user name] from [group name] is creating a plan with you! Open the app to get your vibe for the day, once all users have their vibe for the day the plan is sent as a photo message. After an outing plan has been generated using the create button in the top right corner of the gc once for the day the button no longer says “Create” but now says “Recreate” so if clicked on the same day regenerates the plan. As users continue to use the gc to create plans for themselves the preferences of that particular group are learned and outing plans become more catered as time goes on.
Apart from this a Search Icon will also be present in the top right corner
If clicked on this search icon it opens up a up a search screen with a search bar at the top saying “Add people or Search Places that might suit your group”
Once a user searches the name of a person their profile pops up as normal with a new “Add to [group name]” as a hovering button at the top of the screen. If clicked on it sends an invite to the user: “[user name] has added you to their gc- [gc name]” and then a decline/accept button below that is the same as room invitations in the messages and social of the invited user.
If they search the name of the place, the same venue flow pops up of that place but instead of the pros & cons of the user, the pros & cons for the gc are shown and the vibe score for the gc is shown instead of just the user. A new “Go here” hovering button will be at the top of the venue screen now which when clicked on makes a room with all the people in the GC same as a normal room when a user clicks on “host”. This time with the outing plan in the view plan button only containing the venue they chose and the lock plan button in the same place which when clicked on would not create any GC since the GC already exists and the outing plan would become active in the outing plan screen. The host button will be at the top and the user can choose to host the room for other people to view and join. Once the user clicks on host a new edit icon will appear next to the room name (which would’ve originally been the name of the SHUFFL GC) for the user to change the room name. The blend style of the room originally will be the blend style of the SHUFFL GC but when the room is hosted and other people join the blend style will change to the blend style of the vibes of the other people in the room along with the one’s in the original SHUFFL GC. In this scenario once the plan is locked a new gc will be created with the new room name and with the other people that join once the room is hosted.
So let’s say I make a SHUFFL gc with 3 friends and click on the search icon. I search the name Bohca and the venue name comes up. I click on the venue and in the venue screen I click on “Go here”, a room will be made with the people in the GC and I can choose to host this room for other people to join with the outing plan just containing Bohca.

## Home Page

If not completed vibe swipe game: Home page features blurred with lock icons and if user clicks on one the app takes them to the vibe swipe game. In the foreground at the top of the screen, an active floating button flashes with the username of the user written on it and beside it a confused/thinking emoji. if they click on the button it will expand and open the Profile screen.
After completing the swipe game: The active floating button will now flash their username and beside it their vibe for the day and the emojis associated with it.
Top right corner of the screen will be the a filters icon which when clicked on opens the filter settings
At the top of the main screen: The Search Bar
Below that, “What’s poppin right now that suits your vibe”. This will be a block which will have like a carousel of different activities and events going on in the person’s city catered to their vibe for the day.
(The following section will only be displayed if the user has added friends): “What your friends are up to:” This section will display the rooms their friends are part of at that moment and if they have active rooms they have hosted themselves. This section will list a carousel of different rooms with each room displayed the following way: “XYZ friend hosted this room” or “XYZ friend joined this room” at the top, room name just below that with the Host name just beside the room name ([room name] by [host name]), blend style of the room just below that highlighted in the font colour of the blend style colour palette of that particular blend style (if a friend has hosted a room there will also be a join button at the bottom to request to join the room only if the room has remaining capacity and the room passes the same gate and match as the public-room list (plan engine §13.4a and §13.6.3); a friend’s Open Night room has no plan and no gate, so its join button always shows, with the “No direction yet — whoever joins with one, sets it” line under the room name; if the user doesn’t pass the gate or the room is at full capacity the join button will not be there). Users can switch off the ability for other people to see this in their “What your friends are up to:” section in the privacy setting in settings.
Below that, “Explore other vibes”: (If user clicks on this he’ll be taken to a screen where he’ll be shown the heatmap for his vibe where he’ll be able to view which places other people belonging to his vibe are visiting the most today such as “The party monster heatmap” and below that a button saying “view other heatmaps” which when clicked will show locations on the map where people belonging to other vibes are visiting the most for each vibe one by one below one another in a similar fashion)  Heatmap privacy rules: an area is only rendered on a heatmap once a minimum threshold of distinct users is present in it (threshold tbd, suggested 20 or more), so small groups can never be resolved. Data is displayed at area/neighbourhood level, never at exact venue level, unless a venue clears a much higher user threshold. No individual identity, DP or username is ever exposed on a heatmap, and no icon on a heatmap is tappable through to a person. Users can opt out of contributing their visits to heatmaps from Settings. Heatmap data is aggregated and deliberately delayed (suggested 30 to 60 minutes) rather than live, so the feature can never be used as live tracking.

## Task Bar

Home Button to the left
Play Button in the middle
Messages/Social Button to the right

## Profile Screen

“[Name]’s vibe profile” at the top
Settings Icon in the top right corner which when clicked opens the Settings Page Flow
Music icon in the top left corner which when clicked on opens the same Add music flow. Once a user clicks on the music that they want to add, each time another user opens their profile they’ll hear that song, with the ability to mute.
Below that, DP which when clicked on opens the stories (instagram style) the user posted recently
Below that, “[vibe for the day] today”, example “Peak Mingler today”
Below that, the user’s **badges** — one for each preference they marked “the whole point”: Foodie, Gig-Goer, Dressed For It (or Hype), Good Eye, First Timer, Old Soul — as small chips; none if none.
Below that, **“What I care about in a place”** — a row of six: food, a live act, dressed-up, the look, somewhere new, somewhere old — each showing its current level (The whole point / Nice to have / Don’t mind / Don’t care) and tappable to change it; a “Redo my preferences” link under the row re-runs the preference deck. These never change on their own.
Below that, Bio
Below that, Pinboard, which includes the stories that the user pinned appearing there from any time in their history of using the app.
Below that, “Past Events” and just below that the list of event plans they’ve been a part of listed as buttons row wise in a creative way (tbd). If clicked on any one of these event plan buttons it expands a little to display the stops that that particular event plan had along with the usernames of the people that were a part of it
Below that, their vibe history. This will be a pie chart of the vibes that they had the most
Just below that, “Your Overall Going Out Type Is:” and this will mention their overall going out type
Below that, “Friends you vibe the most with:” , this will list the friends that had the most same/similar vibes as them out of all their friends over the course of the user using the app.

## Search Bar Flow

Users can use the search bar to look for other users, locations and heatmaps
Once a user clicks on the search bar the screen changes to only occupy the search bar at the top which will now be highlighted and the rest of the screen blank.
As the user begins to type in their search terms the app will start narrowing down the results as is done in other search bars
The results that show up will also have a vibe score next to them which will be how similar the factor scores of that place are to the factor scores of the vibe of the user today. This applies to people as well, the factor scores of the vibe of that person and how similar they are to the factor scores of the vibe of the user. Heatmaps appear as is, with the name of the heatmap mentioned, for example, “The Sunlit Brunch Friends Heatmap”Privacy controls: what other people can see about a user is controlled by that user from Settings, with separate toggles for today’s vibe, their vibe score against the viewer, their overall going out type, their vibe history and their past events. Each toggle can be set to Everyone, Friends only, or Nobody. If a user hides their vibe they still appear in search results, just without a vibe score attached, rather than disappearing from search. These settings apply consistently everywhere the same data surfaces: search results, the Profile Flow, the View Profile Flow, and the “Friends you vibe the most with” section.

## Outing Plan Flow

The main contents of the outing plan card as mentioned earlier in different occasions will appear like this
Duration slider just above the card which will have a slider to select the duration of the outing and the outing plan will get refreshed and adjusted on the basis of this duration
Title of the event plan at the top of the card which is editable
“Start off with”, and then the first stop mentioned
Just below the stop is the description of the place
Just below the description is the reason why this place is great for whichever user is viewing the outing plan card
Just below that the reasons why this location favours each person in the group is mentioned, “For X friend there are cocktails for Y friend there are delicious desserts” — **two lines per person** now: a vibe line from the shape of the night (“for Aarav — it builds from here”, “for Bela — you can hear each other”, “for Chirag — something to play”; or, where the street rather than the venue is carrying it, “the street outside is buzzing”) and a preference line from the venue (“the food’s good”, “there’s a set at ten”, “nobody’s been”). The plan engine returns the factor and where it came from; the app turns them into words. Above the per-person lines, the stop’s **type** in plain words — “a games bar”, “a quiet bar”, “a club” — and, when the room is a Settle Then Roam, the stop’s **hours** (“8 to 11”) — along with this a seating suggestion based on the affiliation score of the group, for example, “ask for a seat close to the bar as it matches your group vibe and you’ll be able to socialise more!”. Under the per-person lines, the card can carry up to three short notes per stop, all read straight off how the night was designed (plan engine §14.3 v4) — there is no easing, no ⓘ, no payback and no stop that is one person’s: (1) **a stand-in note**, when somebody’s second-favourite factor is shaping the night in place of their top one because another person is firmly set the other way — “Aarav’s here for the crowd tonight; Bela’s set on a calm one” — one line, in plain words, naming both people; (2) **a to-a-degree note**, when a person’s top factor is present at this stop but not fully — the place is on their side of the middle rather than inside what they asked for — “Some energy here for Arjun; more at the next stop” (the app knows where it *is* fully served, and says so if it is anywhere in the night); (3) **an absent note**, rare, when no kind of place could carry a person’s top factor together with everyone else’s at this stop — “No games here for Chetan — nowhere does games, a floor and a quiet table at once” — plain, never hidden, and never turned into a separate stop for that person. A person with no strong wants tonight (everything of theirs in the middle) gets their vibe line from bend rather than from a top factor: “Divit’s easy tonight.” Whole-point preferences the night could not serve anywhere get one line at the bottom of the card, not under a stop: “No live music tonight — none of the places on this shape has an act.”
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

On clicking the filter icon a screen will drop down from the top which will have all the filters
The first filter would be distance (this controls the radius in which venues/restaurants would be recommended to the user . This also means that only those rooms would be recommended to the user that have outing plans where the venues/restaurants fall within the distance radius set by the user) with a slider to increase/decrease the value in KMs
Second would be age range (this value dictates the profiles and rooms that are dictated to the user by only recommending them profiles and rooms that fall in the age range set by them)
Then filter vibes, clicking on this opens a pop up which contains a list of vibes along with a short description of the vibe and a view more button to open a full screen description of that vibe. This would be a multiple choice list and the vibes the user selects would be filtered out, ie rooms that contain a person that has one of the filtered out vibes would not be recommended to the user and profiles of people that have one of those vibes would not be recommended to the user. Restaurants that have factor scores similar to the filtered out vibe would also not be recommended to the user.
Then duration, which will allow the user to filter out rooms that have outing plans generated with a longer duration than their chosen duration
Then the last filter would be budget, which would have a slider ranging from 500 to “no budget” and the second last value before “no budget being” 25k. This would filter out any rooms where the lowest budget of a person is higher than the budget set by the user (if a room contains 3 people let’s say x,y and z and x has a budget of 10k and y has a budget of 15 and z has a budget of 20 the user would only be recommended this room if his budget filter value is over 10k).
