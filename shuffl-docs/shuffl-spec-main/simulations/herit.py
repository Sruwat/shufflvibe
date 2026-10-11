# -*- coding: utf-8 -*-
"""HOW HERIT IS SERVED IN A PREMIUM-ONLY DATABASE.

The error this corrects (mine, 2026-10-01): I treated "heritage" as if it implied an old, locally
run room, and concluded that admitting only reliable venues kills HERIT. Those are two different
axes and they are orthogonal. Ikk Punjab is the proof - maximum heritage character, maximum
operational reliability. Nothing about old-world feeling requires an unreliable room.

So HERIT is CHARACTER, not a venue type, and it reaches a user three ways.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- the three routes
# fabric      the building really is old            -> a standing tag, always true
# styled      the room is built to feel old         -> a standing tag, always true
# programme   a sufi night, a sitar set, a qawwali  -> an EVENT, true only at an hour
FABRIC, STYLED, BASE = 85, 65, 15
EVENT_LIFT = 25          # on top of whichever standing score the venue has
CAP = 100

V = [
 dict(name='Ikk Punjab',     area='CP',         km=4.2, fabric=False, styled=True,
      tags=['heritage-styled', 'courtyard-feel', 'thali-service', 'table-led'],
      events=[('live ghazal set', 4, 21, 23)]),          # (what, weekday, from, to)
 dict(name='The Haveli Bar', area='Mehrauli',   km=14.0, fabric=True,  styled=True,
      tags=['heritage-building', 'courtyard', 'open-air', 'listed-structure'],
      events=[]),
 dict(name='Piano Man',      area='Safdarjung', km=5.4, fabric=False, styled=False,
      tags=['stage-facing', 'seated', 'listening-room'],
      events=[('sitar + tabla', 3, 21, 23), ('jazz quartet', 5, 22, 25)]),
 dict(name='Depot 48',       area='Aerocity',   km=8.6, fabric=False, styled=False,
      tags=['sports-screens', 'standing-room', 'bar-rail'],
      events=[]),
 dict(name='Qila',           area='Lodhi Rd',   km=6.1, fabric=True,  styled=False,
      tags=['heritage-building', 'colonial-bungalow', 'garden', 'table-led'],
      events=[('sufi evening', 3, 20, 23)]),
]

def standing(v):
    if v['fabric']: return FABRIC
    if v['styled']: return STYLED
    return BASE

def herit_at(v, weekday, hour):
    """HERIT is partly STANDING and partly PROGRAMMED, so it is hour-scoped like the curve."""
    s = standing(v)
    on = [e for e in v['events'] if e[1] == weekday and e[2] <= hour < e[3]]
    return (min(CAP, s + EVENT_LIFT) if on else s), (on[0][0] if on else None)

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

head('THE CATEGORY ERROR, NAMED')
print("""
  I had these as one axis. They are two, and they are independent:

                       RELIABLE  <------------------->  UNRELIABLE
        OLD-FEELING    Ikk Punjab, Qila, The Haveli      a gali in Old Delhi
                       Bar - premium, consistent,        - wonderful, and not
                       old-world by design or fabric     something we can promise

        NEW-FEELING    Depot 48, Cirrus 9                a new place run badly

  The admission filter cuts the HORIZONTAL axis. HERIT lives on the VERTICAL one. Cutting one
  does nothing to the other, and the top-left box is large, premium, and exactly where a lot of
  the best Indian hospitality sits.
""")

head('THE THREE ROUTES TO HERIT, ALL PREMIUM-COMPATIBLE')
print("""
  1  FABRIC      the building genuinely is old - a haveli, a colonial bungalow, a listed
                 structure, a converted mansion.          standing score 85
  2  STYLED      a new or renovated room built to feel old. Ikk Punjab is this: the architecture
                 is old-Punjab by design, the operation is a modern premium one.   standing 65
  3  PROGRAMME   a sufi evening, a sitar and tabla set, a qawwali, a ghazal night. Attaches to a
                 venue at an HOUR, not to the venue forever.          +25 at that hour

  1 and 2 are standing tags on the row. 3 is an event, and it is the reason HERIT is HOUR-SCOPED
  in exactly the way the energy curve already is.
""")

head('WHAT THAT LOOKS LIKE IN THE ROW')
print('%-16s %-11s %-8s %-7s  %s' % ('venue', 'area', 'standing', 'route', 'heritage tags'))
line()
for v in V:
    route = 'fabric' if v['fabric'] else ('styled' if v['styled'] else '-')
    ht = [t for t in v['tags'] if 'heritage' in t or t in ('courtyard', 'colonial-bungalow', 'listed-structure')]
    print('%-16s %-11s %-8d %-7s  %s' % (v['name'], v['area'], standing(v), route, ', '.join(ht) or '-'))
line()

head('AND WHAT IT LOOKS LIKE ACROSS A WEEK  (a stop drawn for 21:30)')
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
print('%-16s %s' % ('venue', '  '.join('%-5s' % d for d in DAYS)))
line()
for v in V:
    cells = []
    for wd in range(7):
        h, ev = herit_at(v, wd, 21.5)
        cells.append('%-5s' % (('%d*' % h) if ev else str(h)))
    print('%-16s %s' % (v['name'], '  '.join(cells)))
line()
print('* = a heritage event is on. Piano Man is a 15 on a Monday and a 40 on a Thursday, and it')
print('  is the same room - which is the whole point of letting programming carry HERIT.')

head('A USER WITH HERIT 88 DRAWS A QUIET, FULLISH 21:30 STOP')
for wd, label in ((0, 'Monday'), (3, 'Thursday'), (4, 'Friday')):
    print()
    print('  %s 21:30 - what the fill stage can offer at rung 3:' % label)
    rows = []
    for v in V:
        h, ev = herit_at(v, wd, 21.5)
        rows.append((h, v['name'], ev))
    rows.sort(reverse=True)
    for h, n, ev in rows[:3]:
        why = (' - %s on tonight' % ev) if ev else ''
        print('      %-16s HERIT %3d%s' % (n, h, why))
    best = rows[0]
    if best[0] >= 70:
        print('      -> served well. The card says why: "%s"' % (best[2] or 'the building itself'))
    else:
        print('      -> HERIT goes unserved tonight, and the card SAYS so at the bottom:')
        print('         "Nothing with much history on this shape tonight."')

head('WHERE THE TAGS ACTUALLY COME FROM — the part that decides if this is buildable')
print("""
  Each route has a different source, and they get cheaper as you go down:

  FABRIC      LOOKUP-ABLE. INTACH and ASI listings, state heritage lists, heritage-precinct
              addresses. Plus the venue's own copy, which almost always states a period when
              there is one ("in a 1920s bungalow"). A one-time pass, rarely changes.

  STYLED      A HUMAN GLANCE. Nobody can automate "does this room feel old", but anybody can
              decide it from four photos in about five seconds. At 40-60 seed venues that is
              under an hour of work, once.

  PROGRAMME   A FEED. Venue socials, Insider, BookMyShow, District. This is the only one that
              needs refreshing, and it is the one that is genuinely automatable, because event
              listings are structured data by nature.

  SO HERIT IS MUCH CHEAPER TO POPULATE THAN THE ENERGY CURVE, which needs a judgement per venue
  PER HOUR and has no source at all. Heritage needs one lookup, one glance, and one feed.
""")

head('TWO THINGS THIS CHANGES ELSEWHERE')
print("""
  1  `street / market` SHOULD NOT BE A VENUE TYPE AT ALL. The user: "we're sticking to venues."
     It was never scoped and it is the only thing the admission filter actually killed. Removing
     it is a deletion, not a loss - and it takes the whole "casualty" section of
     VENUE_DATABASE_V1 with it, because FOOD and HERIT were never in trouble.

  2  PROGRAMME-LED HERIT NEEDS CLOCK-ANCHORED STOPS - the ghazal set is at 21:00, not "in the
     evening". That is the same unbuilt feature FOCUS has been blocked on since 2026-09-30.
     One feature, two factors. It just became the most load-bearing thing on the list.
""")
