# -*- coding: utf-8 -*-
"""VENUE ADMISSION - who gets into the database at all.

The user's rule, 2026-10-01: start premium, where premium means ESTABLISHED AND REPUTED, not
expensive. The worked example is his: Kent's in Defence Colony against Nik Baker's at the same
price point. Both established, both reputed. Only one is a place we can PROMISE a vibe at.

The numbers below are illustrative, not scraped. What matters is which signal does the separating.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# n_reviews, mean rating, SD of ratings, last-6mo mean, operator, fit-out age (yrs), price band
CANDIDATES = [
 ('Nik Baker\'s',      1840, 4.3, 0.62, 4.3, 'chain',       3,  2),
 ('Kent\'s-like',       930, 4.3, 1.34, 4.0, 'owner-local', 17, 2),
 ('Depot 48',          2600, 4.1, 0.71, 4.2, 'group',        4,  2),
 ('Cirrus 9',          1420, 4.4, 0.58, 4.4, 'hotel',        2,  3),
 ('Piano Man',         3100, 4.6, 0.55, 4.6, 'group',        6,  2),
 ('Dilli Haat',        8800, 4.2, 1.12, 4.1, 'public',      25,  1),
 ('new rooftop, 3mo',    74, 4.7, 0.48, 4.7, 'group',        0,  3),
 ('old-school dhaba',  1150, 4.5, 1.41, 4.4, 'owner-local', 30,  1),
 ('declining chain',   2200, 4.2, 0.74, 3.5, 'chain',        9,  2),
 ('tiny wine bar',      310, 4.5, 0.61, 4.5, 'indie-pro',    1,  3),
]

VOLUME_FLOOR   = 200     # below this the variance is not measurable
MEAN_FLOOR     = 4.0
SD_CEILING     = 0.85    # THE ONE THAT DOES THE WORK
DRIFT_FLOOR    = -0.35   # last 6 months against lifetime
FITOUT_CEILING = 15      # years since the room was last done
OPERATOR_OK    = {'chain', 'group', 'hotel', 'indie-pro'}

def admit(row):
    name, n, mean, sd, recent, op, age, price = row
    fails = []
    if n < VOLUME_FLOOR:              fails.append('too few reviews to judge (%d)' % n)
    if mean < MEAN_FLOOR:             fails.append('mean %.1f below %.1f' % (mean, MEAN_FLOOR))
    if sd > SD_CEILING:               fails.append('SD %.2f above %.2f - INCONSISTENT' % (sd, SD_CEILING))
    if recent - mean < DRIFT_FLOOR:   fails.append('slipped %.1f in 6 months' % (recent - mean))
    if op not in OPERATOR_OK:         fails.append('owner-operated local, no group behind it')
    if age > FITOUT_CEILING:          fails.append('room last done %d years ago' % age)
    return fails

def line(c='-', n=102): print(c * n)
def head(t):
    print(); print('=' * 102); print(t); print('=' * 102)

head('THE ADMISSION TEST — reviews and interaction get you CONSIDERED, not admitted')
print('%-20s %6s %6s %6s %6s  %-12s %5s   %s' %
      ('venue', 'n', 'mean', 'SD', '6mo', 'operator', 'fit', 'decision'))
line()
for row in CANDIDATES:
    fails = admit(row)
    name, n, mean, sd, recent, op, age, price = row
    verdict = 'IN' if not fails else 'OUT - ' + fails[0]
    print('%-20s %6d %6.1f %6.2f %6.1f  %-12s %5d   %s' % (name, n, mean, sd, recent, op, age, verdict))
    for f in fails[1:]:
        print('%73s also: %s' % ('', f))
line()
print('IN: %d of %d' % (sum(1 for r in CANDIDATES if not admit(r)), len(CANDIDATES)))

head('THE SEPARATION THAT MATTERS')
a = CANDIDATES[0]; b = CANDIDATES[1]
print("""
  Nik Baker's and the Kent's-like place have the SAME MEAN RATING (4.3) and the SAME PRICE BAND.
  A ranking built on stars cannot tell them apart, and that is exactly the failure the user named:
  both are established, both are reputed, and only one of them can be promised.

  What separates them is the SPREAD.

      Nik Baker's      mean 4.3   SD 0.62     most nights are the night you were told about
      Kent's-like      mean 4.3   SD 1.34     lots of 5s and lots of 2s - it depends who is on

  A high standard deviation IS the thing the user described as "too locally run to ensure anyone
  any vibe there". It is not a judgement about quality, it is a measurement of RELIABILITY, and it
  comes free from the same API call that gives the mean. Nobody ranks venues this way, and for an
  app that makes a promise about a night rather than a recommendation about a place, it is the
  single most load-bearing number available.

  The other half of his point is the room itself: fit-out 3 years against 17. Old infrastructure
  cannot deliver a drawn energy reliably - the lighting, the sound and the seating are what turn
  a crowd into a vibe, and a room last done in 2009 will not do it on demand.
""")

head('WHAT EACH REJECTION IS ACTUALLY PROTECTING')
print("""
  SD ceiling 0.85     the promise. If a place is a coin flip, every plan containing it is a coin
                      flip, and one bad stop sinks a whole night (peak-end: people remember the
                      worst moment and the last one).

  operator class      consistency across staff and across nights. A group or chain has a standard
                      it has to hit on a Tuesday. This is the rule that excludes Kent's even if
                      its variance were tight, and the user is right that it should.

  fit-out ceiling     deliverability of a drawn energy. This is the only criterion that is about
                      the SKELETON rather than about reputation.

  volume floor 200    honesty about what we know. The 3-month-old rooftop scores 4.7 across 74
                      reviews and might be excellent - we cannot tell yet, so it waits.

  drift floor         the declining chain. Lifetime 4.2, last six months 3.5. Admitted on a
                      lifetime average it would poison plans for a year before anyone noticed.
""")

head('THE CASUALTY NOBODY ASKED FOR — AN ENTIRE VENUE TYPE')
print("""
  Run the filter and Dilli Haat fails it. So does the dhaba. Both are famous, both are reputed,
  and both are exactly what the rule was written to exclude: publicly or locally run, old rooms,
  and a spread that says the experience depends on the day.

  By the user's own rule that is CORRECT. But it has a consequence nobody has decided on:

      the `street / market` venue type may admit ZERO venues at launch
      `HERIT` becomes a preference the engine can almost never serve
      a slice of `FOOD` goes with it - the best cheap food in Delhi is owner-run and old

  That is a real narrowing of what SHUFFL can be on day one, and it is worth saying out loud
  rather than discovering it when the first heritage-leaning user gets a night of chain cafes.

  Three ways out, none chosen:
    1. ACCEPT IT. Launch premium, add the rest later on a different standard. Clean, and it
       means HERIT should probably not ship as a preference at all until there is somewhere
       to point it.
    2. A SECOND ADMISSION TRACK for institutions - places where the variance IS the experience
       and everybody knows it. Nobody expects a market to be consistent; the promise there is
       "this is a market", not "this is a reliable room". Different promise, different bar.
    3. ADMIT THEM, FLAG THEM. They enter the database marked unpredictable, and the plan card
       says so at the stop: "Dilli Haat is a market - it is whatever it is tonight."

  2 is the honest answer and 3 is the cheap one. 1 is what happens if nobody decides.
""")

head('THE COST, STATED HONESTLY')
print("""
  THIS MAKES THE THIN-SUPPLY PROBLEM WORSE BEFORE IT MAKES IT BETTER, and the two goals are in
  direct conflict:

      the preview is only honest if the database is DENSE
      the promise is only kept if the database is CHOOSY

  Both are right and they pull opposite ways. The resolution is not to compromise on either - it
  is to shrink the area. A dense, choosy, fully-curved SINGLE RADIUS beats a thin choosy city,
  because a user inside it gets honest previews and kept promises, and a user outside it gets
  nothing rather than a bad night.

  So admission being strict is an argument FOR seeding one area first, not against it.

  And the database must SHRINK as well as grow: a venue whose stops get rated low, or skipped
  repeatedly at lock time, is evicted. Admission is a filter on the way in; eviction is the only
  thing that keeps the promise true after the reviews that admitted it have gone stale.
""")
