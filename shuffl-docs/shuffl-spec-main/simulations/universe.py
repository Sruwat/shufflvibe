# -*- coding: utf-8 -*-
"""HOW BIG IS THE UNIVERSE - Delhi NCR venues passing reputed / established / not locally run.

These are INFORMED ESTIMATES, not counts. Nobody has queried anything. The working is laid out so
each line can be argued with, and section D says how to replace the whole thing with real numbers
in an afternoon - legitimately, without storing anything.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

def line(c='-', n=94): print(c * n)
def head(t):
    print(); print('=' * 94); print(t); print('=' * 94)

# district, total F&B outlets (rough), share that is nightlife-relevant, share of THOSE that are premium
D = [
 ('Gurugram - Cyber Hub',          55, 0.85, 0.75),
 ('Gurugram - Sector 29',          70, 0.90, 0.45),
 ('Gurugram - Golf Course Rd',     45, 0.70, 0.60),
 ('Gurugram - MG Rd / Sec 15',     40, 0.65, 0.40),
 ('Delhi - Connaught Place',      130, 0.70, 0.42),
 ('Delhi - Aerocity',              32, 0.85, 0.90),
 ('Delhi - Hauz Khas Village',     45, 0.90, 0.32),
 ('Delhi - Khan Market',           55, 0.55, 0.55),
 ('Delhi - Greater Kailash 1&2',   48, 0.70, 0.45),
 ('Delhi - Saket / Select City',   45, 0.65, 0.65),
 ('Delhi - Vasant Kunj malls',     35, 0.60, 0.70),
 ('Delhi - Defence Colony',        28, 0.55, 0.35),
 ('Delhi - Rajouri Garden',        38, 0.70, 0.40),
 ('Delhi - Punjabi Bagh / West',   30, 0.55, 0.32),
 ('Delhi - Mehrauli / Chattarpur', 25, 0.70, 0.50),
 ('Noida - Sec 18 / Film City',    50, 0.65, 0.45),
 ('Noida - Garden Galleria / 104', 30, 0.70, 0.55),
 ('hotel bars + restaurants, NCR', 70, 0.80, 0.95),
 ('scattered standalone premium',  45, 0.75, 0.55),
]

head('A. THE UNIVERSE, DISTRICT BY DISTRICT')
print('%-32s %7s %12s %10s %9s' % ('district', 'F&B', 'nightlife', 'x premium', 'PASSES'))
line()
tot = 0
for name, n, nl, pr in D:
    p = n * nl * pr
    tot += p
    print('%-32s %7d %12.0f %10.0f%% %9.0f' % (name, n, n * nl, pr * 100, round(p)))
line()
print('%-32s %7s %12s %10s %9.0f' % ('TOTAL', '', '', '', round(tot)))
print()
print('  So roughly **%d** venues in Delhi NCR pass "nightlife-relevant, established, reputed,' % round(tot))
print('  professionally run". A defensible range is **%d to %d** - the premium shares are the' % (round(tot*0.72), round(tot*1.28)))
print('  softest numbers and they swing it most.')

head('B. CROSS-CHECKS, FROM TWO OTHER DIRECTIONS')
print("""
  LIQUOR LICENCES. Delhi NCR has on the order of 1,000-1,200 licensed bars, pubs and clubs across
  the five jurisdictions. If a quarter to a third are chain, group, hotel or professionally-run
  independent, that is 250-400. Consistent.

  LISTING FILTERS. A nightlife listing for Delhi NCR runs to a few thousand entries; filtering to
  4.0+ with 500+ reviews cuts it to the high hundreds, and requiring a group or chain behind it
  cuts it again by roughly half. Also consistent.

  Three independent routes landing in the same band is about as much confidence as an estimate
  gets without counting.
""")

head('C. THE PART THAT MATTERS MORE THAN THE TOTAL - the type mix')
TYPES = [
 ('pub / big loud bar',   125), ('buzzy restaurant',      80),
 ('table for the night',   45), ('lounge / rooftop',      50),
 ('quiet bar',             35), ('match bar',             22),
 ('club',                  25), ('games bar / games pub', 15),
 ('live room',             14), ('open ground',            5),
]
print('%-26s %8s   %s' % ('type', 'venues', ''))
line()
for t, n in sorted(TYPES, key=lambda x: -x[1]):
    bar = '#' * int(n / 2.2)
    print('%-26s %8d   %s' % (t, n, bar))
line()
print('  total across types: %d  (types overlap, so this exceeds the district total)' % sum(n for _, n in TYPES))
print("""
  THE DISTRIBUTION IS VERY UNEVEN, AND IT IS THINNEST EXACTLY WHERE NIGHTS END.

  There are maybe **25 real clubs in the whole of Delhi NCR**, and about **14 live rooms**. Those
  are the two types a high-energy late stop resolves to - so the top-right corner of the supply
  grid, late and loud, is sparse CITYWIDE, not merely inside a seed radius.

  Three consequences:

    - A skeleton drawn with a hard late peak will often find only two or three candidates inside
      12 km, which is below the point where the SHAPE_GATE and stage 2 do anything. Selection
      effectively collapses to "the nearest club".
    - Those venues will be repeated across many users' plans. `NOV` - somewhere new - becomes
      hard to serve at the late end specifically.
    - And it argues for admitting the late end more liberally than the rest. The admission filter
      was written for the whole database; the club end may need its own, looser bar simply because
      there is no supply to be choosy with.
""")

head('D. SEEDING, AND HOW TO REPLACE ALL OF THIS WITH REAL NUMBERS')
for radius, label, lo, hi in [(0, 'one strong district (Cyber Hub, or CP, or HKV+GK)', 28, 45),
                              (0, 'two adjacent districts', 55, 90),
                              (0, 'all of South Delhi', 90, 140),
                              (0, 'all of Gurugram', 95, 150),
                              (0, 'Delhi NCR, everything', 250, 450)]:
    print('  %-52s %4d - %-4d venues' % (label, lo, hi))
print("""
  **The 50-venue seed is about one strong district, or two small ones.** That is a day of
  curation, not a project - and it is the first point at which the selection ladder has real
  competition to resolve.

  TO REPLACE THIS ESTIMATE WITH A COUNT, legitimately and in an afternoon:

    Run Places **Nearby Search** per district with a type filter, and COUNT the results. Counting
    is not storing - you are measuring the size of a market, not building a database, and nothing
    persists but a number in a notebook. One query per (district x type) is a few hundred queries,
    well inside a free tier, and it gives the real distribution instead of my guesses at the
    premium shares.

    Then filter the counts by rating and review volume to get the premium share per district
    properly, which is the softest input in section A and the one worth firming up first.
""")
