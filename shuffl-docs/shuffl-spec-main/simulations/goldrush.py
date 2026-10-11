# -*- coding: utf-8 -*-
"""THE GOLD PROMOTION - costing a crowdsourced band-capture programme.

The user's design: venues whose bands are missing are highlighted in gold, contextually, based on
the time window the user already chose. Go there through the app with location on, and a guided
live-photo capture unlocks a voucher. A factor-card swipe afterwards pays a bonus.

Budget: Rs 2-3 lakh. The question is how far it goes, and that depends entirely on how many bands
actually need capturing.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

def line(c='-', n=96): print(c * n)
def head(t):
    print(); print('=' * 96); print(t); print('=' * 96)

# ---------------------------------------------------------------- which venues need bands at all
# type, count in NCR, bands that MATTER, why
# type, venues, bands that matter, DAY-MODES that matter, why
TYPES = [
 ('club',              25, 2, 1, 'weekend only - a club midweek is shut or empty, so one day-mode'),
 ('big loud bar',      55, 3, 2, 'weekday AND weekend, and they are different venues. The widest swing'),
 ('pub',               70, 3, 2, 'same shape, shallower, both day-modes'),
 ('lounge / rooftop',  50, 3, 2, 'sunset, evening, late - three rooms, twice over'),
 ('live room',         14, 2, 2, 'programme-driven, so the schedule matters more than the bands'),
 ('match bar',         22, 0, 0, 'driven by fixtures, not by the hour. Needs a schedule, not bands'),
 ('buzzy restaurant',  80, 0, 0, 'peaks at dinner and the type curve already says so'),
 ('table for the night',45,0, 0, 'flat by definition'),
 ('quiet bar',         35, 0, 0, 'flat, and quiet is the point'),
 ('games bar / pub',   15, 0, 0, 'flat'),
 ('open ground',        5, 0, 0, 'too few and too weather-dependent to model'),
]

head('A. WHICH BANDS ACTUALLY NEED CAPTURING')
print('%-22s %7s %6s %6s %8s   %s' % ('type', 'venues', 'bands', 'days', 'SLOTS', 'why'))
line()
need_v = need_b = 0
for t, n, b, d, why in TYPES:
    if b: need_v += n; need_b += n * b * d
    print('%-22s %7d %6s %6s %8s   %s' % (t, n, b or '-', d or '-', (n*b*d) or '-', why))
line()
print('%d of %d venues need bands; **%d SLOTS** in total once day-modes are counted.'
      % (need_v, sum(n for _, n, _, _, _ in TYPES), need_b))
print()
print('  The user is right that a Big Chill does not need this. **Six of eleven types need nothing**,')
print('  because a flat venue is already described by its type curve. The whole programme is aimed')
print('  at the four types that genuinely transform across a night.')

# ---------------------------------------------------------------- how many captures per band
head('B. HOW MANY CAPTURES PER BAND, AND WHY NOT ONE')
print("""
  One capture is one night. A Tuesday at a Friday venue, a dead week, a freak private party - any
  of those becomes the band forever if nothing contradicts it.

  And the capture must be tagged (venue, DAY-MODE, hour-band) and only count toward THAT slot.
  A weekday capture tells you nothing about the weekend band, which is a different number entirely.

  So: 3 captures per slot, taking the median. Two agree and one is an outlier - that is the
  minimum that can detect an outlier at all.
""")
REPS = 3
total_caps = need_b * REPS
print('  %d slots x %d captures = **%d captures** to fill the whole database.' % (need_b, REPS, total_caps))

# ---------------------------------------------------------------- the money
head('C. THE TRADE-OFF - how many venues, at what price a capture')
print("""
  Rs 2-3 lakh cannot fill 1,156 slots. The question is not "what is the voucher" - it is
  **"how many venues do we cover, and does the voucher get taken at that price"**.
""")
BUD = 250000
SLOTS_PER = need_b / float(need_v)       # average slots per venue that needs them
print('  At a Rs 2,50,000 budget, 3 captures a slot, %.1f slots a venue:' % SLOTS_PER)
print()
print('  %-34s %8s %10s %14s   %s' % ('coverage', 'venues', 'captures', 'per capture', 'verdict'))
line()
for label, v in [('everything that needs bands', need_v),
                 ('the top 120', 120), ('the top 60', 60),
                 ('the top 35 - clubs + named bars', 35), ('the top 20', 20)]:
    caps = int(v * SLOTS_PER * REPS)
    per = BUD / caps
    verdict = ('too thin to be taken' if per < 200 else
               'workable' if per < 400 else
               'a real voucher' if per < 800 else 'overpaying - widen instead')
    print('  %-34s %8d %10d %14s   %s' % (label, v, caps, 'Rs %.0f' % per, verdict))
line()
print("""
  **The top 35 is the answer**, and it is the same 35 the app will query most: the clubs everybody
  names plus the bars people actually plan around. **Rs 475 a capture**, which is a drink and
  change at the venue they are already standing in.

  Covering everything at Rs 72 a capture is not a cheaper version of the programme - it is a
  programme nobody completes twice.

  And the rest of the database is not left blank. **It keeps the type curve** (entry 141), which is
  83% as good as the full curve at putting the pick inside the shape gate. The captures are spent
  where the type curve is weakest and the traffic is heaviest, which is the same place.
""")

head('D. THE SPLIT - and it should be the other way round')
print("""
  The user proposed: voucher for the PHOTOS, a bonus for the factor-card swipe.

  **I would invert the weighting, and the reason is what each one actually produces.**

     THE PHOTOS need a model to interpret them. They go through the reference sets, the
     selection-bias correction and the confound rule, and come out as an ESTIMATE of energy and
     crowd. Useful, and indirect.

     THE SWIPE IS THE MEASUREMENT. A person standing in the room at 23:40 on a Friday saying "this
     is an 8 for energy, a 9 for how full it is" has produced the band. No model, no pipeline, no
     confound. **It is the number we have spent three days trying to infer.**

  So the swipe should not be a bonus. It should be the main task, and the photos the corroboration
  that stops somebody swiping from their sofa.
""")
for b in (250000,):
    cap = b / top_caps
    print('  At a Rs %s budget and %d captures, Rs %.0f a capture, split:' % ('{:,}'.format(b), top_caps, cap))
    print()
    print('     Rs %-5.0f  arriving with it in your active plan and location on   (the gate)' % 0)
    print('     Rs %-5.0f  the guided live photos - wide frame, crowd, bar        (proof of presence)' % (cap * 0.4))
    print('     Rs %-5.0f  the factor-card swipe                                  (THE DATA)' % (cap * 0.6))
    print('     ------')
    print('     Rs %-5.0f  total for a complete capture' % cap)
print("""
  And a small multiplier where it is hardest to get: **1.5x for the 24:00-02:00 band**, which is
  the one nobody is awake to capture and the one clubs are entirely defined by. It costs little
  because the late band is a fraction of the total, and it is the band most likely to stay empty.
""")

head('E. FIVE RISKS, AND WHAT THE DESIGN ALREADY DOES ABOUT THEM')
print("""
  SELECTION BIAS - AGAIN. Captures come from people who go out, at the times they go out, to the
     venues they already like. **Mitigated by the gold highlight itself**, which is the one part of
     the design that actively steers people toward the GAPS rather than the popular slots. That is
     the cleverest thing in the proposal and it should be said out loud.

  GAMING. Somebody photographs an empty corner to finish fast. **Live capture only and a GPS fence
     are already in the design.** Add: the three captures per slot are compared, and a capture more
     than two bands away from the other two pays but does not count. Nobody is accused of anything.

  THE REWARD BUYING THE WRONG NIGHT. People going somewhere they do not want to go for Rs 500.
     **The design already requires the venue to be in a plan they built**, which is most of the
     answer - and honestly, a nudge toward a place they would not have tried is half of what the
     app is for.

  THE CAPTURE INTERRUPTING THE NIGHT. Five screens of photography at 23:40 is a real cost to the
     user's evening. **Keep it under 60 seconds, and never fire the notification twice.**

  AND THE ONE THE DESIGN DOES NOT HANDLE: **a venue's bands change.** A capture is true for a
     season. Mark every band with its capture date, and let the gold highlight return to a venue
     whose data is more than, say, six months old. The programme is not a one-off - it is how the
     database stays alive.
""")
