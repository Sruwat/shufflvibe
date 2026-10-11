# -*- coding: utf-8 -*-
"""A REAL ADMISSION PASS - twelve Delhi NCR venues, researched 2026-10-03/04.

Every number below was read from a live listing, not invented. Run through admission.py's criteria
with the fields that are actually obtainable, and the gaps named.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# name, rating, reviews, price_pp, operator, type guess, notes from the listing
V = [
 # name, rating, reviews, approx price pp, operator, type, note     [researched by hand 2026-10-03/04]
 ('Sidecar',          4.6,  2514, 3000, 'group',     'quiet bar',         'GK2 M-block. Cocktail bar'),
 ('Piano Man',        4.5,  5268, 1500, 'group',     'live room',         'Safdarjung'),
 ('PCO',              4.4,  2072, 2100, 'group',     'quiet bar',         'Vasant Vihar D-block'),
 ('Qla',              4.4,  3236, 2000, 'group',     'table for the night','Mehrauli, by Qutub Minar'),
 ('Hauz Khas Social', 4.3, 32158,  900, 'chain',     'big loud bar',      'Social chain. 32k reviews'),
 ('The Wine Company', 4.3,  2343, 2900, 'chain',     'buzzy restaurant',  'Cyber Hub'),
 ('Summer House',     4.2,  9403, 1500, 'indie-pro', 'cafe / live room',  'Aurobindo Place. Full row built'),
 ('Soi 7',            4.2,  8015, 2800, 'chain',     'pub',               'Cyber Hub. Review text shows decline'),
 ('Dear Donna',       4.2,  2620, 3900, 'group',     'buzzy restaurant',  'Qutub Hotel. 12pm-2am'),
 ('Bohca',            4.1,   953, 2000, 'hotel',     'club / tapas bar',  'Qutub Hotel. Full row built'),
 ('Kitty Su',         4.1,  1661, 2000, 'hotel',     'club',              'The Lalit, CP'),
 ('Lord of the Drinks',4.1,15623, 2800, 'chain',     'big loud bar',      'Connaught Place'),
 ('Imperfecto HKV',   4.0,  3264, 3000, 'chain',     'big loud bar',      'Hauz Khas Village'),
 ('Striker',          4.0,  2006, 1700, 'chain',     'games pub',         'Sector 29 Gurugram'),
 ('Privee',           3.6,  1380, 2000, 'hotel',     'club',              'Shangri-La Eros. THE REJECTION THAT FIXED THE FILTER'),
 ('Prankster',        4.2,   111, 1000, 'chain',     'big loud bar',      'Sector 29. Low count - may be a wrong match'),
]
# NOT RESOLVED by hand, and worth knowing why: searching "Cirrus 9" returned a venue at The Oberoi
# (4.5/195) when Cirrus 9 is at the Shangri-La. A WRONG-VENUE MATCH, which is worse than no data,
# and it is the failure mode hand collection has that an API call does not - the API matches on a
# place_id, a human search matches on a name and a guess. Depot 48, Raasta and antiSOCIAL did not
# render a knowledge panel at all.
VOLUME_FLOOR, MEAN_FLOOR = 200, 4.0
OPERATOR_OK = {'chain', 'group', 'hotel', 'indie-pro'}

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

head('THE PASS - twelve real venues, admission on the criteria we can actually fill')
print('%-18s %6s %8s %7s %-10s %-18s %s' % ('venue','rating','reviews','price','operator','type','verdict'))
line()
admitted, rejected, incomplete = [], [], []
for n, r, c, p, op, ty, note in V:
    if r is None or c is None:
        incomplete.append(n); v = 'NEEDS DATA'
    else:
        f = []
        if c < VOLUME_FLOOR: f.append('volume %d' % c)
        if r < MEAN_FLOOR:   f.append('mean %.1f' % r)
        if op not in OPERATOR_OK: f.append('operator')
        v = 'IN' if not f else 'OUT - ' + ', '.join(f)
        (admitted if not f else rejected).append(n)
    print('%-18s %6s %8s %7s %-10s %-18s %s'
          % (n, r if r else '-', c if c else '-', p, op, ty[:17], v))
line()
print('IN %d   OUT %d   INCOMPLETE %d' % (len(admitted), len(rejected), len(incomplete)))

head('THE FINDING - the mean floor is wrong for clubs, and real data found it immediately')
print("""
  **Privee fails on a 3.6 mean.** It is one of the best-known clubs in Delhi, in the Shangri-La,
  with 1,380 reviews. The filter throws it out.

  **And we already know why, from entry 145: clubs collect door complaints that restaurants do
  not.** "Terrible rules for entry", "attitude at the door", "bouncers" - we decided those are
  evidence about the DOOR and not about quality, and that they should be ROUTED rather than
  counted. But the MEAN RATING has already counted them, before we see it.

     Kitty Su   4.1     Privee   3.6     Bohca   4.1
     against
     Piano Man  4.5     Summer House 4.2     Hauz Khas Social 4.3

  **A club rates about half a point below a bar of the same quality, structurally.** So an absolute
  4.0 floor is not a quality bar - it is a type bar, and it excludes the type the app most needs.

  THE FIX: **make the mean floor a PERCENTILE WITHIN TYPE, not an absolute.**

     club              floor at the 35th percentile of clubs
     bar / pub         floor at the 35th percentile of bars
     restaurant        likewise

  Same rule, same strictness, applied against the right comparison - which is exactly what
  `quality` already does (percentile within type and area, VENUE_DATABASE_V1 section 2). **The
  admission filter should have been using it from the start.**
""")

head('WHAT IS STILL MISSING, AND WHETHER IT CAN BE GOT')
print("""
  %-18s %s
  %-18s %s
  %-18s %s
  %-18s %s
""" % ('rating_sd', 'NOT OBTAINABLE from any free source. Entry 142. Substitute: sentiment',
       '', '  variance across the 5 returned review texts, AFTER routing (entry 145)',
       'fitout_years', 'NOT in any API. Obtainable by eye from photos in about 3 seconds a venue',
       'last6mo_mean', 'NOT directly - but comparable from the 5 newest reviews against lifetime'))
print("""  So of admission's six criteria:
     volume, mean, operator     -> obtainable now, and done above
     fit-out age                -> a human glance, cheap
     drift                      -> approximable from the newest reviews
     SPREAD                     -> the one that does the work, and the one nothing free provides
""")
