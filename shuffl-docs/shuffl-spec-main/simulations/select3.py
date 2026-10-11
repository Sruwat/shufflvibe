# -*- coding: utf-8 -*-
"""SELECTION V2 - the skeleton picks the venue, preferences only break what is left.

The user, 2026-10-01:
  "venue selection should happen EXCLUSIVELY on the basis of the skeleton - energy and crowd at
   that moment - and then move onto the preference factors depending on whether there is a clash
   in the room. The preference factors are FIXED per venue; ENRG and CROWD are tagged in BANDS
   from per-hour statistics and the venue's own curve: Depot 48, 8pm-12am, ENRG 88, CROWD 88."

Two changes. Stage 1 is the whole of selection until it runs out of candidates, and the curve
becomes BANDS rather than a point per hour.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# ============================================================ THE ROW, with banded energy/crowd
# bands: (from_hour, to_hour, ENRG, CROWD) - a venue needs 2-4 of these, not 9 hourly points
# prefs: FIXED. They do not move with the hour.
V = [
 dict(name='Depot 48',    area='Aerocity', km=8.6, type='big loud bar', quality=81,
      bands=[(19, 22, 55, 40), (22, 26, 88, 88)],
      prefs=dict(FOOD=46, LIVE=38, POL=55, SCEN=50, HERIT=5,  GAMES=25)),
 dict(name='Social, HKV', area='HKV',      km=6.9, type='big loud bar', quality=64,
      bands=[(19, 23, 60, 55), (23, 26, 84, 86)],
      prefs=dict(FOOD=72, LIVE=20, POL=35, SCEN=45, HERIT=10, GAMES=70)),
 dict(name='Lord of the Drinks', area='CP', km=5.2, type='big loud bar', quality=58,
      bands=[(20, 24, 72, 70), (24, 27, 86, 90)],
      prefs=dict(FOOD=40, LIVE=78, POL=60, SCEN=38, HERIT=8,  GAMES=15)),
 dict(name='Cirrus 9',    area='Aerocity', km=9.1, type='rooftop bar', quality=70,
      bands=[(17, 20, 35, 28), (20, 24, 60, 76)],
      prefs=dict(FOOD=58, LIVE=20, POL=72, SCEN=88, HERIT=10, GAMES=0)),
 dict(name='Ikk Punjab',  area='CP',       km=4.2, type='buzzy restaurant', quality=74,
      bands=[(18, 23, 52, 68)],
      prefs=dict(FOOD=88, LIVE=35, POL=62, SCEN=70, HERIT=65, GAMES=0)),
 dict(name='Piano Man',   area='Safdarjung', km=5.4, type='live room', quality=88,
      bands=[(19, 25, 58, 80)],
      prefs=dict(FOOD=62, LIVE=96, POL=48, SCEN=70, HERIT=20, GAMES=0)),
]

def band_at(v, hour):
    for a, b, e, c in v['bands']:
        if a <= hour < b: return e, c
    return None

PREFS = ['FOOD', 'LIVE', 'POL', 'SCEN', 'HERIT', 'GAMES']
LIVE_AT, SERVED_AT = 70, 70        # a preference is "live" in the room at 70+; a venue "serves" it at 70+
SHAPE_GATE = 12                    # stage 2 may only choose among venues THIS close to the drawn shape.
                                   # Beyond it the user could tell the difference, so preferences do not
                                   # get to overrule the line they drew. This is what makes stage 1
                                   # "exclusive" rather than merely "first".

ROOM = [
 ('Aarav', dict(FOOD=88, LIVE=30, POL=55, SCEN=74, HERIT=20, GAMES=15)),
 ('Nitya', dict(FOOD=40, LIVE=92, POL=30, SCEN=50, HERIT=35, GAMES=10)),
 ('Zoya',  dict(FOOD=35, LIVE=25, POL=45, SCEN=86, HERIT=15, GAMES=78)),
]

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

# ============================================================ STAGE 1
def stage1(hour, de, dc, radius=12.0, trace=True):
    """THE SKELETON ALONE. No preference, no tag, no vibe. Energy and crowd at that hour."""
    out = []
    for v in V:
        b = band_at(v, hour)
        if not b or v['km'] > radius: continue
        e, c = b
        d = abs(e - de) + 0.6 * abs(c - dc)
        out.append((d, v))
    out.sort(key=lambda x: x[0])
    if trace:
        for d, v in out:
            e, c = band_at(v, hour)
            print('     %-20s %-17s band %02d:00 e%-3d c%-3d   distance %5.1f'
                  % (v['name'], v['type'], hour, e, c, d))
    return out

# ============================================================ STAGE 2
def live_prefs(room):
    out = {}
    for p in PREFS:
        holders = [(n, pr[p]) for n, pr in room if pr[p] >= LIVE_AT]
        if holders: out[p] = holders
    return out

def serves(v, p): return v['prefs'][p] >= SERVED_AT

def stage2(cands, room, already_served, trace=True):
    """Preferences only decide among what stage 1 left, and ONLY where the room clashes."""
    if not cands: return None, set(), 'nothing in range'
    best_d = cands[0][0]
    inside = [(d, v) for d, v in cands if d <= best_d + SHAPE_GATE]
    if trace and len(inside) < len(cands):
        cut = [v['name'] for d, v in cands if d > best_d + SHAPE_GATE]
        print('     shape gate (+%d): %s cannot compete here, they are not the night that was drawn'
              % (SHAPE_GATE, ', '.join(cut)))
    cands = inside
    want = live_prefs(room)
    outstanding = {p: h for p, h in want.items() if p not in already_served}
    if trace:
        print('     live in the room: ' + ', '.join('%s (%s)' % (p, ', '.join(n for n, _ in h))
                                                    for p, h in want.items()))
        if already_served:
            print('     already served earlier tonight: ' + ', '.join(sorted(already_served)))
        print('     outstanding here: ' + (', '.join(sorted(outstanding)) or 'nothing'))
    if not outstanding:
        if trace: print('     NO CLASH - nothing left to want, so stage 1 stands')
        return cands[0][1], set(), 'the shape alone'
    # can one candidate serve everything outstanding?
    full = [(d, v) for d, v in cands if all(serves(v, p) for p in outstanding)]
    if full:
        if trace: print('     NO CLASH - %s serves all of it' % full[0][1]['name'])
        return full[0][1], set(outstanding), 'serves everything outstanding'
    # a clash: nobody serves all of it. Weight by WHO CARES, summed.
    if trace: print('     CLASH - no venue here serves all of ' + ', '.join(sorted(outstanding)))
    best, best_v, best_set = -1, None, set()
    for d, v in cands:
        got = {p for p in outstanding if serves(v, p)}
        weight = sum(s for p in got for _, s in outstanding[p])
        tie = weight - d * 0.9 + v['quality'] * 0.05   # shape still pulls, inside the gate
        if trace and got:
            print('        %-20s serves %-22s weight %3d' % (v['name'], ', '.join(sorted(got)), weight))
        if tie > best: best, best_v, best_set = tie, v, got
    return (best_v or cands[0][1]), best_set, 'resolved by who cares'

head('STAGE 1 — THE SKELETON, AND NOTHING ELSE')
print('  The user drew stop 2 at 23:00, energy 86, crowd 88.')
print()
c1 = stage1(23, 86, 88)
print()
print('  Three big loud bars are in range and all three fit the shape. The skeleton has done its')
print('  job and CANNOT choose between them - which is exactly when preferences get a turn.')

head('STAGE 2 — PREFERENCES, AND ONLY BECAUSE STAGE 1 TIED')
print()
pick2, got2, why2 = stage2(c1[:3], ROOM, set())
print()
print('  PICK -> %s   (%s)' % (pick2['name'], why2))

head('THE SAME ROOM, STOP 1 AT 20:00 — WHERE THE CLASH ACTUALLY LIVES')
print('  drawn: 20:00  energy 55  crowd 70')
print()
c0 = stage1(20, 55, 70)
print()
pick1, got1, why1 = stage2(c0[:3], ROOM, set())
print()
print('  PICK -> %s   (%s)' % (pick1['name'], why1))

head('AND THE RULE THAT STOPS THE CLASH BEING A CLASH AT ALL')
print("""
  A clash at ONE STOP is usually not a clash across THE NIGHT. Run the two stops in order and
  carry what has already been served:
""")
served = set()
plan = []
for hour, de, dc in [(20, 55, 70), (23, 86, 88)]:
    cands = stage1(hour, de, dc, trace=False)
    pick, got, why = stage2(cands[:3], ROOM, served, trace=False)
    served |= got
    plan.append((hour, pick, got, why))
    print('  %02d:00  %-20s  serves %-24s (%s)'
          % (hour, pick['name'], ', '.join(sorted(got)) or '-', why))
print()
unserved = set(live_prefs(ROOM)) - served
print('  served across the night: ' + ', '.join(sorted(served)))
print('  never served:            ' + (', '.join(sorted(unserved)) or 'nothing'))
if unserved:
    for p in sorted(unserved):
        who = ', '.join(n for n, _ in live_prefs(ROOM)[p])
        print('     -> the card carries ONE line at the bottom, not under a stop:')
        print('        "No %s tonight - nothing on this shape has it." (%s wanted it)' % (p, who))

head('WHAT THIS CHANGES IN THE SPEC')
print("""
  1  FOUR RUNGS BECOME THREE, and the middle one is gone. Rung 1 was "character tags the room
     asked for" - and since the identity factors stopped touching venues it had no source worth
     keeping. Selection is now:

         stage 1   the skeleton: energy and crowd at that hour, inside the radius   <- does the work
         stage 2   preferences, and ONLY where stage 1 left a tie and the room clashes
         stage 3   quality, tie-break only

     Tags do not filter at all any more. They are how a preference FINDS a venue (HERIT wants
     `heritage-building`) and what the card PRINTS. Nothing is selected by a tag on its own.

  2  THE CURVE BECOMES BANDS, and this is the cheap part. Instead of a judgement per venue per
     hour - nine of them - a venue needs 2 to 4 blocks:

         Depot 48    19:00-22:00  e55 c40
                     22:00-02:00  e88 c88

     That is 2-4 judgements instead of 9, a 2-3x cut in the one field that had no source. It is
     also closer to how anybody actually describes a venue: "it's quiet till ten and then it goes."

  3  PREFERENCES ARE FIXED PER VENUE and do not move with the hour. One consequence to decide:
     HERIT programming (a sufi night at 21:00) was written as an HOUR-SCOPED LIFT on the venue's
     HERIT. Under "prefs are fixed" that cannot sit on the venue - so it belongs in a SEPARATE
     EVENTS TABLE keyed (venue, date, hour, kind), read at stage 2 alongside the fixed prefs.
     The venue stays static; the calendar moves. That is cleaner than what the doc says now.
""")
