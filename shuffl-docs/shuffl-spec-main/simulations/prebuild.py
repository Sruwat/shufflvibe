# -*- coding: utf-8 -*-
"""THE PRE-PROMOTION BUILD - what we can fill from reviews, photos and the venue's own information,
and what we deliberately leave empty for the gold promotion to fill.

The user, 2026-10-03: "before the gold promotion, factor scores for each venue will be fixed and
inputted a little bit as much as possible - the data for Bohca is accurate for it being a club
after 10pm and the factor scores changing - and for the venues that are convoluted the bands left
empty."
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

def line(c='-', n=98): print(c * n)
def head(t):
    print(); print('=' * 98); print(t); print('=' * 98)

# ---------------------------------------------------------------- what counts as evidence
EVIDENCE = [
 ('structured',  3, 'a Google field: type, hours, liveMusic, outdoorSeating, priceLevel, reservable'),
 ('own_copy',    3, "the venue's own site, Facebook or Instagram - and it STATES the time"),
 ('timed_review',2, 'a review fragment naming an hour or a day AND a character'),
 ('untimed',     1, 'the lexicon base - good for the venue, says nothing about when'),
 ('type_curve',  0, 'the prior. Not evidence - it is what an empty slot falls back TO'),
]
FILL_AT = 3      # a slot fills on one strong source, or two timed reviews that agree

head('A. WHAT WE HAVE, AND WHAT EACH KIND IS GOOD FOR')
print('%-14s %7s   %s' % ('source', 'weight', 'what it is'))
line()
for n, w, d in EVIDENCE:
    print('%-14s %7d   %s' % (n, w, d))
line()
print("""
  THE RULE: a slot is FILLED when its evidence reaches %d. One structured field or one line of the
  venue's own copy is enough; two agreeing timed reviews are enough; the lexicon base on its own
  never is, because it describes the VENUE and a slot is about an HOUR.

  **An empty slot is not blank.** It falls back to the type curve, which is 83%% as good as a full
  curve at putting the pick inside the shape gate. "Empty" means "not measured, using the prior".
""" % FILL_AT)

# ---------------------------------------------------------------- the two venues we actually did
VENUES = {
 'Bohca': dict(type_base='tapas bar / club', hours='12:00-01:00', slots=[
   ('all',     12, 17, 'buzzy restaurant', [('structured','Google type + hours + "terrace restaurant, sharing plates"')]),
   ('sun',     12, 17, 'games pub',        [('own_copy','their Facebook: "Hoppi Sunday Brunch... lovely board games"')]),
   ('all',     17, 22, 'buzzy restaurant', [('structured','hours; the type holds through the evening')]),
   ('fri-sun', 22, 26, 'club',             [('timed_review','"finest place for the LATE NIGHT party"'),
                                            ('timed_review','"massive crowd inside... the WEEKEND go-to"'),
                                            ('structured','closes 01:00; reservations required')]),
   ('mon-thu', 22, 26, None,               []),
 ]),
 'Summer House': dict(type_base='cafe / live room', hours='12:00-01:00', slots=[
   ('all',     12, 18, 'cafe',             [('structured','Google type "Cafe" + outdoor seating'),
                                            ('timed_review','"aesthetic date spot DURING THE DAY"')]),
   ('all',     18, 22, 'lounge / rooftop', [('timed_review','"around 7pm... completely packed"')]),
   ('wed',     20, 24, 'live room',        [('own_copy','their Instagram: "live independent sound, every WEDNESDAY"')]),
   ('thu-sat', 22, 26, None,               [('untimed','"party harder" - no hour, no day')]),
   ('sun-tue', 22, 26, None,               []),
 ]),
}
W = {n: w for n, w, _ in EVIDENCE}

head('B. THE TWO VENUES WE HAVE ACTUALLY BUILT')
gold = []
for name, v in VENUES.items():
    print()
    print('  %s   %s   open %s' % (name, v['type_base'], v['hours']))
    line()
    for days, a, b, vtype, ev in v['slots']:
        score = sum(W[k] for k, _ in ev)
        filled = score >= FILL_AT and vtype
        mark = 'FILLED ' if filled else '>> GOLD'
        why = ev[0][1][:46] if ev else 'nothing in any source says what this is'
        print('     %-8s %02d-%02d  %-17s %s  %s' % (days, a, b % 24 or 24, vtype or '(unknown)', mark, why))
        if not filled:
            gold.append((name, days, a, b))
    line()

head('C. SO THE GOLD LIST IS NOT A SEPARATE DECISION - IT IS THE GAPS')
print("""
  Nobody sits down and chooses which venues go gold. **The pre-promotion build produces the list by
  failing to fill a slot.** Every slot the evidence cannot reach is a slot the promotion targets,
  and the two are the same object seen from either end.
""")
for n, d, a, b in gold:
    print('     GOLD:  %-14s %-8s %02d:00-%02d:00' % (n, d, a, b % 24 or 24))
print("""
  And look at WHICH slots they are. **Every daytime slot fills from structured data alone. Every
  late slot but one is gold.**

     Bohca      mon-thu 22-02    the weekday version of a venue whose weekend is well documented
     Summer     thu-sat 22-02    "party harder" is the only evidence, and it names no hour
     Summer     sun-tue 22-02    nothing at all
     Summer     all     18-22    ONE timed review - "around 7pm, completely packed"

  **That last one is the gate working rather than failing.** A single person's seven o'clock is a
  single night, and the rule refuses it on purpose. Two agreeing timed reviews would have filled
  it; one does not, and the cost of being wrong here is a venue in the wrong list for months.

  **THE EVIDENCE IS THINNEST EXACTLY WHERE THE VENUE TRANSFORMS**, because that is the part nobody
  writes down: a listing states what a place IS, and reviews describe the night people had, which
  is almost always the busy one. The quiet Tuesday at eleven is unrecorded everywhere.
""")

head('D. WHAT THAT MEANS ACROSS 214 VENUES')
print("""
  Extrapolating the shape of the two we have done:

     DAYTIME and EARLY EVENING slots      mostly FILLABLE - hours and type carry them
     WEEKEND LATE slots                   fillable for FAMOUS venues, empty for the rest
     WEEKDAY LATE slots                   almost entirely EMPTY
     ANY slot where the venue changes     empty unless the venue itself announced it

  Call it **half to two-thirds of slots fillable before a single capture**, and the gaps
  concentrated in the late bands - which is **the same place the promotion was already pointed**,
  and the same place the type curve is weakest.

  **The three findings line up, which is the reassuring part:** the slots that are hardest to
  derive, the slots the type curve predicts worst, and the slots users query most are all the
  same slots. Nothing has to be traded off.
""")

head('E. THE RULE, STATED FOR WHOEVER BUILDS THE FIRST 214 ROWS')
print("""
  1  **The base always gets filled.** Lexicon over the review corpus, plus the structured fields,
     plus images where the text is thin. Every venue has a base on day one - that is §5.8 and it
     is done.

  2  **A slot is only filled when a source NAMES ITS TIME.** "Sunday brunch", "every Wednesday",
     "the weekend go-to", "during the day", "closes at 1am". A glowing review with no hour in it
     improves the base and must not touch a slot.

  3  **Never infer a slot from the type curve and store it.** That is the one mistake that would
     poison everything: a stored guess is indistinguishable from a measurement a month later.
     **Leave it empty and let the fallback happen at query time**, where it is visible and
     reversible.

  4  **Mark every filled slot with its source.** `structured` / `own_copy` / `timed_review`. When a
     capture later contradicts a slot, the source decides which wins - a capture beats a timed
     review, and nothing beats the venue's own statement of its own programme.

  5  **The empty slots are the gold list.** Export them, sort by venue popularity, and that is the
     promotion's target queue without anyone making a second decision.
""")
