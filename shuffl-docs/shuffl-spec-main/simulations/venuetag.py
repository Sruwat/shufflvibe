# -*- coding: utf-8 -*-
"""PART 2 - how a venue is tagged and stored, and where it lands in the supply grid.
Five contrasting venues, written out as the database would actually hold them."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# ===================================================================== THE ROW
# One flat table. Everything hour-scoped, because a venue is a different place at 19:00 and 01:00.
#
#   name, area, km
#   types[]   (type, from_hour, to_hour)   - a place can BE several types across a night
#   curve{}   hour -> (energy, crowd)      - the venue's own skeleton. THE EXPENSIVE FIELD.
#   prefs{}   FOOD LIVE POL SCEN HERIT GAMES - 0..100, one-ended, matches the preference set
#   quality   percentile within (type, area)
#   tags[]    character tags - the within-type discriminators
#
# register and role are NOT stored. They are DERIVED from the curve, per hour, so they can never
# drift out of sync with it.

V = [
 dict(name='Cirrus 9', area='Aerocity', km=9.1, quality=70,
      types=[('rooftop bar', 17, 24)],
      curve={17:(32,25), 19:(48,52), 21:(60,74), 23:(66,80), 25:(55,58)},
      prefs=dict(FOOD=58, LIVE=20, POL=72, SCEN=88, HERIT=10, GAMES=0),
      tags=['open-air', 'skyline', 'table-led', 'date-safe', 'queue-after-9']),

 dict(name='Depot 48', area='Aerocity', km=8.6, quality=81,
      types=[('big loud bar', 19, 26)],
      curve={19:(45,30), 21:(68,62), 23:(82,86), 25:(88,92)},
      prefs=dict(FOOD=46, LIVE=38, POL=55, SCEN=50, HERIT=5, GAMES=25),
      tags=['sports-screens', 'standing-room', 'open', 'bar-rail', 'gets-loud-at-11']),

 dict(name='Piano Man', area='Safdarjung', km=5.4, quality=88,
      types=[('live room', 19, 25)],
      curve={19:(38,40), 21:(55,78), 23:(62,88), 25:(44,46)},
      prefs=dict(FOOD=62, LIVE=96, POL=48, SCEN=70, HERIT=55, GAMES=0),
      tags=['stage-facing', 'seated', 'ticketed', 'set-at-2130', 'listening-room']),

 dict(name='Dilli Haat', area='INA', km=7.8, quality=71,
      types=[('street / market', 16, 22)],
      curve={16:(34,48), 18:(42,78), 20:(46,86), 22:(38,64)},
      prefs=dict(FOOD=90, LIVE=30, POL=18, SCEN=72, HERIT=84, GAMES=10),
      tags=['open-air', 'walkable', 'open', 'cash-light', 'early-close']),

 # the one that proves why types are hour-scoped: it is two different venues in one building
 dict(name='Perch', area='Khan Mkt', km=6.2, quality=76,
      types=[('brunch cafe', 11, 17), ('wine bar', 17, 24)],
      curve={11:(24,30), 14:(30,56), 17:(38,50), 19:(46,68), 21:(52,76), 23:(48,58)},
      prefs=dict(FOOD=84, LIVE=12, POL=66, SCEN=80, HERIT=22, GAMES=0),
      tags=['table-led', 'conversational-by-design', 'daylight', 'no-queue', 'small-room']),
]

# --------------------------------------------------------------------- DERIVED, never stored
def type_at(v, hour):
    for t, a, b in v['types']:
        if a <= hour < b: return t
    return None

def curve_at(v, hour):
    """the curve is sampled, so read the nearest stored point at or before the hour"""
    pts = sorted(v['curve'])
    best = pts[0]
    for h in pts:
        if h <= hour: best = h
    return v['curve'][best]

def register(v, hour):
    """can you hear each other here, at this hour? Derived from energy, not authored."""
    e, _ = curve_at(v, hour)
    return 'conversational' if e < 50 else ('social' if e < 72 else 'loud')

def role(v, hour):
    """warm-up / peak / wind-down, from where this hour sits on the venue's OWN curve"""
    pts = sorted(v['curve'])
    es = [v['curve'][h][0] for h in pts]
    peak_h = pts[es.index(max(es))]
    if hour < peak_h - 1: return 'warm-up'
    if hour > peak_h + 1: return 'wind-down'
    return 'peak'

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

head('PART 2  —  FIVE VENUES, AS THE DATABASE WOULD HOLD THEM')
for v in V:
    print()
    line()
    print('%s   %s   %.1f km   quality %d (percentile within its type AND area)'
          % (v['name'], v['area'], v['km'], v['quality']))
    line()
    print('  types      ' + ';  '.join('%s  %02d:00-%02d:00' % (t, a, b) for t, a, b in v['types']))
    print('  curve      ' + '   '.join('%02d:00 e%d/c%d' % (h, v['curve'][h][0], v['curve'][h][1])
                                       for h in sorted(v['curve'])))
    print('  prefs      ' + '  '.join('%s %d' % (k, x) for k, x in v['prefs'].items() if x >= 40)
          + '      (below 40 omitted)')
    print('  tags       ' + ', '.join(v['tags']))
    print('  DERIVED    ' + '   '.join(
        '%02d:00 %s/%s' % (h, register(v, h)[:4], role(v, h)[:4]) for h in sorted(v['curve'])))

head('WHY EACH FIELD IS SHAPED THAT WAY')
print("""
  types[] is HOUR-SCOPED because a venue is not one kind of place all evening.
      Perch is a 'brunch cafe' until 17:00 and a 'wine bar' after it. One row, two types, and a
      skeleton drawn for 13:00 and one drawn for 21:00 reach the same building for different
      reasons. Without hour-scoping you need two rows and they drift apart.

  curve{} IS THE VENUE'S OWN SKELETON, and it is what makes the whole engine work: the user draws
      (energy, crowd) at an hour, and the venue HAS (energy, crowd) at that hour. The match is a
      distance between two things of the same type. No translation layer anywhere.
      It is also the expensive field — see the note at the end.

  register and role are DERIVED, never stored. Depot 48 is 'conversational' at 19:00 and 'loud'
      at 23:00 — the same room, and nobody has to remember to update a second field when the
      curve changes. Store a derived value and it goes stale; derive it and it cannot.

  tags[] are the WITHIN-TYPE discriminators. They never replace the type. 'open-air' does not tell
      you Cirrus 9 is a rooftop bar; it tells you WHICH rooftop bar, once the skeleton has already
      asked for one. That is why there can be ~600 of them and only ~100 types: character is
      linear, shapes are combinatorial.

  quality is a percentile WITHIN (type, area), never citywide. 'Good for a rooftop bar in
      Aerocity' is a usable sentence; 'the 81st best venue in Delhi' is not, and it would rank
      every cheap place below every expensive one.
""")

head('THE SUPPLY GRID — WHAT GETS PRECOMPUTED FROM THE ABOVE')
print('  key: (hour, energy bucket, crowd bucket) -> the types that actually HAVE venues there')
print('  built nightly, shipped to the phone, so the skeleton preview is an O(1) lookup while')
print('  the line is being dragged. This is the table that makes the live preview possible.')
print()
grid = {}
for v in V:
    for h in range(11, 26):
        t = type_at(v, h)
        if not t: continue
        e, c = curve_at(v, h)
        grid.setdefault((h, e // 10 * 10, c // 10 * 10), {}).setdefault(t, []).append(v['name'])
print('  %-6s %-9s %-9s  %s' % ('hour', 'energy', 'crowd', 'types available (from 5 venues)'))
line()
for k in sorted(grid):
    h, eb, cb = k
    if h % 2: continue
    inner = '; '.join('%s [%s]' % (t, ', '.join(ns)) for t, ns in grid[k].items())
    print('  %02d:00  %2d-%-6d %2d-%-6d  %s' % (h, eb, eb + 9, cb, cb + 9, inner))
line()
print('  Five venues give %d non-empty cells. A real city gives a few thousand — still small' % len(grid))
print('  enough to ship to a phone, which is the whole point of precomputing it.')

head('WHAT A DRAWN STOP ACTUALLY DOES TO THIS')
print()
for hour, de, dc, why in [(21, 62, 76, 'he drags the line up and holds the circle wide'),
                          (23, 84, 88, 'the last stop, loud and packed'),
                          (21, 40, 30, 'quiet and empty at nine')]:
    print('  drawn: %02d:00  energy %d  crowd %d   (%s)' % (hour, de, dc, why))
    hits = []
    for v in V:
        t = type_at(v, hour)
        if not t: continue
        e, c = curve_at(v, hour)
        d = abs(e - de) + 0.6 * abs(c - dc)
        hits.append((d, v['name'], t, register(v, hour), role(v, hour)))
    hits.sort()
    if hits[0][0] > 35:
        print('       -> the box shows NOTHING LIKE THIS NEARBY (nearest is %.0f away).' % hits[0][0])
        print('          He is told while he is still dragging, not after the plan is made.')
        print('          AND THIS IS THE THIN-DATABASE FAILURE IN ONE LINE: with five venues the')
        print('          honest answer is "nothing". With four hundred, something sits at distance 5.')
        print('          The engine is identical in both cases. Only the supply is different.')
    else:
        for d, n, t, reg, rl in hits[:3]:
            mark = '   <- the preview box shows this type' if (d, n, t, reg, rl) == hits[0] else ''
            print('       %-16s %-16s dist %5.1f   %s / %s%s' % (n, t, d, reg, rl, mark))
    print()

head('THE HONEST PART — WHAT IS NOT SOLVED')
print("""
  CROWD has a source. Google Popular Times gives a by-hour curve for most venues in Delhi.

  ENERGY HAS NO SOURCE. There is no feed anywhere that says Depot 48 is 82 at 23:00. It is a
  judgement, per venue, per hour, and it is the field everything else is built on. At a few
  hundred venues that is a few thousand judgements and nobody has decided who makes them.

  Three ways it could work, none of them chosen yet:
    1. author it   — a human sets 4-5 curve points per venue. Slow, accurate, and it does not
                     scale past one city without hiring.
    2. infer it    — predict energy from type + hour + crowd + price + a few tags. Cheap, and
                     it will be wrong for exactly the venues that are interesting (the quiet
                     bar that goes off at midnight).
    3. learn it    — ship rough curves, then correct them from what users do: which stops get
                     locked, which get skipped, what they rate. Right in the long run, and it
                     needs users we do not have, so it cannot be the way we start.

  Realistically it is 1 for a seed area, 2 to extend, 3 to correct. But that is a decision, not
  a plan, until somebody writes it down.

  QUALITY needs populated cells. A percentile within (type, area) over three venues is noise, and
  in the current prototype every (type, area) cell holds exactly ONE venue — so rung 4 of the
  selection ladder has never once fired in any simulation we have run.
""")
