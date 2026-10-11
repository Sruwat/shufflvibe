# -*- coding: utf-8 -*-
"""THE SLOT MODEL - every factor resolved for a (day, hour), not stored flat.

The user, 2026-10-03: "each venue's factor scores should be hour and day dependent, so for a
particular venue the factor scores will actively get replaced with the factor scores of that hour
range and day in real time."

And the correction that forced it: LIVE 92 was wrong. The user has been to Summer House on a
Thursday and a Friday after 11pm with NO live performance until it shut at 1:30. Boxout is a
WEDNESDAY. The lexicon read the venue's reputation and never saw the schedule.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

# ---------------------------------------------------------------- the row
# base = what does not move. slots = only the factors that DO, for a (days, hours) window.
# A slot inherits every factor it does not name.
SUMMER_HOUSE = dict(
  name='Summer House Cafe', area='Aurobindo Place', km=5.8, quality=79,
  base=dict(SCEN=89, HERIT=22, FOOD=77, POL=63, GAMES=8,
            ENRG=55, CROWD=60, TALK=58, MOVE=30, FOCUS=28, LIVE=35),
  slots=[
    dict(days='all',     frm=12, to=18, type='cafe',
         ENRG=32, CROWD=48, TALK=78, MOVE=10, FOCUS=15, LIVE=10),
    dict(days='all',     frm=18, to=22, type='lounge / rooftop',
         ENRG=58, CROWD=74, TALK=60, MOVE=28, FOCUS=30, LIVE=35),
    # the exception that the whole correction is about
    dict(days='wed',     frm=20, to=24, type='live room',
         ENRG=66, CROWD=82, TALK=42, MOVE=50, FOCUS=88, LIVE=95),
    dict(days='thu-sat', frm=22, to=26, type='big loud bar',
         ENRG=82, CROWD=88, TALK=22, MOVE=78, FOCUS=22, LIVE=12),
    dict(days='sun-wed', frm=22, to=26, type='lounge / rooftop',
         ENRG=58, CROWD=55, TALK=48, MOVE=40, FOCUS=25, LIVE=20),
  ])

def day_match(spec, day):
    if spec == 'all': return True
    if '-' in spec:
        a, b = spec.split('-'); i, j, k = DAYS.index(a), DAYS.index(b), DAYS.index(day)
        return (i <= k <= j) if i <= j else (k >= i or k <= j)
    return spec == day

def resolve(v, day, hour):
    """THE WHOLE MECHANISM. Start from base, apply the most specific matching slot."""
    out = dict(v['base']); out['type'] = None; out['slot'] = 'base only'
    best = None
    for s in v['slots']:
        if not day_match(s['days'], day): continue
        if not (s['frm'] <= hour < s['to']): continue
        # most specific wins: a single named day beats a range beats 'all'
        rank = 2 if s['days'] not in ('all',) and '-' not in s['days'] else (1 if s['days'] != 'all' else 0)
        if best is None or rank >= best[0]: best = (rank, s)
    if best:
        s = best[1]
        for k, val in s.items():
            if k not in ('days', 'frm', 'to'): out[k] = val
        out['slot'] = '%s %02d-%02d' % (s['days'], s['frm'], s['to'])
    return out

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

head('THE CORRECTION, RESOLVED')
print('The user was at Summer House on a THURSDAY and a FRIDAY after 23:00. No live act either time.')
print()
F = ['ENRG', 'CROWD', 'TALK', 'MOVE', 'FOCUS', 'LIVE', 'POL', 'SCEN', 'FOOD', 'HERIT', 'GAMES']
print('%-22s %-18s %s' % ('when', 'type', '  '.join('%-5s' % x for x in F)))
line()
for day, hour, label in [('wed', 21, 'Wednesday 21:00'), ('thu', 23, 'Thursday 23:00'),
                         ('fri', 23, 'Friday 23:00'), ('sat', 14, 'Saturday 14:00'),
                         ('tue', 23, 'Tuesday 23:00')]:
    r = resolve(SUMMER_HOUSE, day, hour)
    print('%-22s %-18s %s' % (label, r['type'] or '-', '  '.join('%-5d' % r[x] for x in F)))
line()
print()
print('  LIVE reads 95 on a Wednesday at nine and 12 on a Friday at eleven. The flat score was 92.')
print('  The user went on a Thursday and a Friday after eleven and saw nothing - which is exactly')
print('  what the slot model now predicts, and what the flat number could never have said.')

head('WHAT IT COSTS - and it is less than it looks')
base_n = 11
slot_n = sum(len([k for k in s if k not in ('days', 'frm', 'to', 'type')]) for s in SUMMER_HOUSE['slots'])
print("""
  Summer House carries %d base numbers and %d slot numbers = %d in total, against the 14 the flat
  row needed. Roughly double - but almost none of it has to be AUTHORED:

     the base              from the lexicon, in one pass          (free)
     the ordinary slots    GENERATED from the type curve x the venue amplitude (entry 141)
     the EXCEPTIONS        authored by hand - and there are usually one or two

  For Summer House the exceptions are **Boxout Wednesday** and nothing else. For Bohca they are
  **Sunday brunch** and the **weekend club mode**. That is two or three authored slots a venue,
  three numbers each - call it ten authored numbers on top of the base.

  So the real cost of making every factor hour-and-day scoped is about **ten numbers a venue**,
  not sixty. For a 50-venue seed that is still an afternoon.
""" % (base_n, slot_n, base_n + slot_n))

head('WHAT THIS CHANGES ELSEWHERE')
print("""
  1  `prefs{}` ARE NO LONGER FIXED, which reverses the 2026-10-01 decision - but only for the
     factors that genuinely move. SCEN, HERIT-fabric, FOOD and POL stay in the base; LIVE, FOCUS,
     GAMES and MOVE move into slots. **The decision was right about most preferences and wrong
     about the programmed ones**, and Bohca's Sunday board games was the first sign of it.

  2  THE EVENTS TABLE AND THE SLOT TABLE ARE THE SAME THING. Heritage programming, the FOCUS clock
     anchor, Boxout Wednesday and Sunday brunch are all one mechanism: a (days, hours) window that
     overrides some factors. Two tables collapse into one.

  3  "ACTIVELY REPLACED IN REAL TIME" has two readings and both are useful. The SOURCE OF TRUTH is
     the base-plus-slots row, resolved at query time - that is what selection reads. A MATERIALISED
     "what is this venue right now" view is worth keeping alongside it for the live parts of the
     app: what's popping tonight, and the venue screen. Same data, two access patterns.

  4  THE SUPPLY GRID IS BUILT BY EXPANDING SLOTS, which it already was for bands. Nothing changes
     except that more factors come along for the ride.
""")

head('AND WHAT IT MEANS FOR THE LEXICON')
print("""
  The flat LIVE 92 was not a bug in the lexicon. **It was the right answer to the wrong question.**
  Summer House genuinely IS a live-music venue - that is its reputation and it is accurate. What
  the text could not say is WHEN, because reviewers write about the venue and the venue's own
  Instagram writes about the schedule.

  So: **the lexicon fills the BASE. The schedule fills the SLOTS, and it comes from the venue's own
  posts, not from reviews.** Boxout Wednesday was stated plainly on Summer House's Instagram and
  never appeared in a single review.

  That is a cleaner division than the one before it:

     reviews          -> what the place is LIKE          -> the base
     the venue's own  -> what the place DOES, and when   -> the slots
     images           -> confirm the base where text is thin
     the type curve   -> the shape of the ordinary slots
""")
