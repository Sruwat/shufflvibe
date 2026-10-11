# -*- coding: utf-8 -*-
"""ONE CAPTURE PER SLOT - is it good enough, and what does Rs 5 lakh then buy?

The user, 2026-10-03: one person per slot. They see it, they complete it inside the window, they
are paid. Fail verification and they retry. Run out of time and it releases to the next person.
"I want to see if I'm lucky enough to get this."
"""
import sys, random, statistics as st
sys.stdout.reconfigure(encoding="utf-8")
random.seed(17)

def line(c='-', n=94): print(c * n)
def head(t):
    print(); print('=' * 94); print(t); print('=' * 94)

head('A. WHAT THE THREE CAPTURES WERE ACTUALLY FOR - and why the time-box replaces most of it')
print("""
  I argued for three because "one capture is one night - a Tuesday at a Friday venue becomes the
  band forever". **That risk is already gone in this design**, and the user's time-box is what
  removes it:

     the slot IS (venue, day, hour-band) - "Bohca, Friday, 20:00-22:00"
     the capture MUST happen inside that window or it releases

  So a capture cannot land in the wrong slot. What is left is only the variation between one
  Friday-at-eight and the next Friday-at-eight at the same venue - which is a far smaller number
  than the day and hour variation the three captures were guarding against.
""")

# ---------------------------------------------------------------- how bad is n=1, really
TYPE_CURVE_ERR = 8.2        # measured, entry 141 - the fallback if a slot is never captured
BAND_W = 10                 # bands are 10-point buckets, so only errors that cross a bucket matter

def trial(sigma_week, sigma_swipe, n):
    truth = random.uniform(20, 95)
    reads = [truth + random.gauss(0, sigma_week) + random.gauss(0, sigma_swipe) for _ in range(n)]
    est = st.median(reads)
    return abs(est - truth)

print()
print('%-34s %12s %12s %14s' % ('', 'mean error', 'vs type curve', 'wrong bucket'))
line()
for label, sw, ss, n in [('the type curve, no capture', 0, 0, 0),
                         ('ONE capture', 6.0, 4.0, 1),
                         ('three captures, median', 6.0, 4.0, 3),
                         ('one capture, calm venue', 3.5, 4.0, 1),
                         ('one capture, volatile venue', 10.0, 4.0, 1)]:
    if n == 0:
        err, bad = TYPE_CURVE_ERR, None
        print('%-34s %12.1f %12s %14s' % (label, err, '-', '-'))
        continue
    errs = [trial(sw, ss, n) for _ in range(6000)]
    err = sum(errs) / len(errs)
    bad = sum(1 for e in errs if e > BAND_W / 2.0) / float(len(errs))
    print('%-34s %12.1f %12s %13.0f%%' % (label, err, ('BETTER' if err < TYPE_CURVE_ERR else 'worse'), bad * 100))
line()
print("""
  **One capture beats the type curve on an ordinary venue** (5.8 against 8.2) and loses on a
  volatile one. Three captures are clearly better still - but the question is not "is three better
  than one", it is **"is one capture everywhere better than three captures on a sixth of the
  database"**, because that is what the same money buys.

  And the answer is yes, because the alternative to a noisy capture is not a better capture.
  **It is the type curve**, which is worse than one capture and applies to every slot we skip.
""")

# ---------------------------------------------------------------- the money
head('B. WHAT Rs 5 LAKH BUYS AT ONE CAPTURE PER SLOT')
TOTAL_SLOTS = 1156                 # all venues needing bands, both day-modes
WEEKEND_ONLY = 578                 # thu-sun only
TOP35 = 189
BUD = 500000
print('%-46s %8s %14s   %s' % ('coverage', 'slots', 'per capture', 'verdict'))
line()
for label, n, note in [
    ('EVERY slot - 214 venues, both day-modes', TOTAL_SLOTS, 'full coverage, modest reward'),
    ('WEEKEND slots only - all 214 venues', WEEKEND_ONLY, 'every venue covered when it matters'),
    ('the top 35 venues, both day-modes', TOP35, 'deep but narrow'),
    ('the top 35, weekend only', int(TOP35 * 0.55), 'too narrow for Rs 5 lakh')]:
    per = BUD / n
    v = ('a strong reward' if per > 700 else 'a real reward' if per > 400 else 'thin')
    print('%-46s %8d %14s   %s - %s' % (label, n, 'Rs %.0f' % per, v, note))
line()
print("""
  **WEEKEND SLOTS ACROSS ALL 214 VENUES, at Rs 865, is the answer.**

     - **Rs 865 is a reward worth gambling for**, which is the whole point of the mechanic.
     - **Every venue that needs bands gets covered** where it matters. Thursday to Sunday is where
       the plans are; a Tuesday at a club is mostly a closed door.
     - **Weekday slots keep the type curve**, which is what they would have had anyway, and they
       are queried least.
     - And it leaves the top-35-weekday slots as an obvious **phase two** if the first round lands.
""")

head('C. WHAT THE GAMBLE MECHANIC ACTUALLY FIXES')
print("""
  The user framed this as advertising - "I want to see if I'm lucky enough to get this". It is
  that, and it also fixes two real problems the three-capture version had:

  **THE PROMISE BECOMES CLEAN.** Three captures meant "you might be third and get nothing". One
  capture plus the retry means **if you got the slot, you get paid** - as long as you do it
  properly. That is a promise worth advertising, and the previous one was not.

  **AND FAILING VERIFICATION STOPS BEING A PUNISHMENT.** With three captures, failing meant losing
  a slot somebody else would take. With one and a retry, **failing costs the user nothing but
  thirty seconds** - which is exactly the right stake, because the verification will be wrong
  1.4% of the time and that error now costs nobody anything.

  **One thing to add: tell them the window.** "You have until 22:00" on the notification. The
  release is the only part of the mechanic that can feel unfair, and it only feels unfair if it
  arrives unannounced.
""")
