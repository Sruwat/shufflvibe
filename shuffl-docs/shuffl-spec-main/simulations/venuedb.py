# -*- coding: utf-8 -*-
"""The proposed venue database and the four-rung selection, run end to end on one imaginary room."""
import math

# ============================================================ THE DATABASE
# One flat table. type is HOUR-SCOPED. The curve is the venue's own skeleton.
# character = (role, register); role is COMPUTED from the curve, register is JUDGED from reviews.
def curve(pairs):
    """{hour: (energy, crowd)} interpolated from a few anchors"""
    out = {}
    hrs = sorted(pairs)
    for h in range(18, 27):
        lo = max([x for x in hrs if x <= h], default=hrs[0])
        hi = min([x for x in hrs if x >= h], default=hrs[-1])
        if lo == hi: out[h] = pairs[lo]
        else:
            t = (h - lo) / float(hi - lo)
            out[h] = tuple(round(pairs[lo][i] + t * (pairs[hi][i] - pairs[lo][i])) for i in (0, 1))
    return out

V = []
def add(name, area, types, anchors, register, prefs, quality, km):
    V.append(dict(name=name, area=area, types=types, curve=curve(anchors),
                  register=register, prefs=prefs, quality=quality, km=km))

#    name                     area        types (type, from, to)              curve anchors        register        prefs                                q   km
add('Depot 48',              'GK-2',     [('buzzy restaurant',19,22),('pub',22,25)], {19:(45,50),22:(70,75),25:(78,85)}, 'social',       dict(FOOD=78,LIVE=60,POL=60,SCEN=60,HERIT=30), 81, 6.2)
add('Diggin',                'Chanakya', [('buzzy restaurant',18,23)],       {18:(40,45),21:(55,65),23:(50,55)}, 'conversational', dict(FOOD=84,LIVE=25,POL=65,SCEN=78,HERIT=35), 74, 9.1)
add('Toy Room',              'Aerocity', [('club',23,26)],                   {23:(80,85),25:(94,95)},           'loud',         dict(FOOD=30,LIVE=30,POL=88,SCEN=62,HERIT=20), 77, 14.0)
add('Warehouse, Chhatarpur', 'Chhatarpur',[('club',23,27)],                  {23:(78,80),26:(96,96)},           'loud',         dict(FOOD=20,LIVE=40,POL=45,SCEN=50,HERIT=30), 69, 17.5)
add('Summer House',          'HKV',      [('pub',20,23),('live room',23,25)],{20:(55,60),23:(74,82),25:(80,88)},'social',       dict(FOOD=62,LIVE=80,POL=58,SCEN=62,HERIT=25), 83, 7.4)
add('Ping Pong Brewery',     'Sector 29',[('pub',19,25)],                    {19:(52,48),22:(72,78),25:(74,80)},'loud',         dict(FOOD=58,LIVE=45,POL=40,SCEN=42,HERIT=20), 66, 13.2)
add('Perch',                 'Khan Mkt', [('quiet bar',18,24)],              {18:(30,35),21:(42,48),24:(40,42)},'conversational', dict(FOOD=70,LIVE=20,POL=80,SCEN=76,HERIT=30), 88, 8.0)
add('The Piano Man',         'Safdarjung',[('live room',20,25)],             {20:(52,62),22:(66,78),25:(64,72)},'loud',         dict(FOOD=64,LIVE=92,POL=64,SCEN=66,HERIT=32), 90, 5.6)
add('Kylin Sky Bar',         'Aerocity', [('lounge / rooftop',19,25)],       {19:(46,52),22:(62,70),25:(60,66)},'social',       dict(FOOD=66,LIVE=30,POL=90,SCEN=90,HERIT=25), 72, 13.6)
add('Cirrus 9',              'CP',       [('lounge / rooftop',19,25)],       {19:(48,55),22:(66,74),25:(64,70)},'social',       dict(FOOD=60,LIVE=35,POL=86,SCEN=84,HERIT=28), 70, 10.2)
add('Bohca',                 'Saket',    [('games pub',18,24)],              {18:(42,44),21:(58,62),24:(56,58)},'conversational', dict(FOOD=60,LIVE=10,POL=45,SCEN=55,HERIT=20), 76, 4.4)
add('Social, Hauz Khas',     'HKV',      [('buzzy restaurant',18,22),('pub',22,25)], {18:(48,58),22:(70,82),25:(76,88)},'loud', dict(FOOD=66,LIVE=40,POL=45,SCEN=50,HERIT=25), 64, 7.1)
add('Olive, Mehrauli',       'Mehrauli', [('table for the night',19,24)],    {19:(32,38),22:(44,50),24:(40,44)}, 'conversational', dict(FOOD=88,LIVE=20,POL=82,SCEN=92,HERIT=80), 86, 11.8)
add('Lord of the Drinks',    'CP',       [('pub',20,26)],                    {20:(58,62),23:(80,88),26:(82,90)},'loud',         dict(FOOD=52,LIVE=35,POL=42,SCEN=40,HERIT=18), 58, 10.6)

# ============================================================ ROLE, COMPUTED FROM THE CURVE
def peak_hour(v):
    return max(v['curve'], key=lambda h: v['curve'][h][0])
def role_of(v, hour):
    """where this venue sits relative to its own peak at the hour we want it"""
    p = peak_hour(v)
    if hour < p - 1:  return 'warm-up'
    if hour > p + 1:  return 'wind-down'
    return 'peak'
def type_at(v, hour):
    for t, a, b in v['types']:
        if a <= hour < b: return t
    return None

# ============================================================ THE ROOM
class M:
    def __init__(s, name, skeleton, talk, move, affil, prefs):
        s.name, s.skeleton, s.talk, s.move, s.affil, s.prefs = name, skeleton, talk, move, affil, prefs

# each skeleton: [(energy, crowd)] per stop, as drawn
ROOM = [
    M('Aarav', [(55, 60), (78, 85)], talk=38, move=62, affil=50, prefs=dict(POL=88, NOV=62)),
    M('Nitya', [(45, 45), (58, 55)], talk=88, move=38, affil=88, prefs=dict(FOOD=88, SCEN=62)),
    M('Zoya',  [(60, 65), (85, 80)], talk=45, move=85, affil=45, prefs=dict(LIVE=88, NOV=75)),
]
HOURS = [20, 23]          # from the time step of the custom flow: out at 8, second stop at 11
RADIUS = 12.0             # km, from the distance step
TALK_FLOOR = 40

# ---- combine the skeletons: contagion per stop (CHEMISTRY_V3), drawn positions weigh more
def combine(stop_i):
    vals = [(m.skeleton[stop_i][0], m.skeleton[stop_i][1], m) for m in ROOM]
    out = []
    for idx in (0, 1):                                  # energy, then crowd
        xs = [v[idx] for v in vals]
        base = sum(xs) / len(xs)
        hi = [x for x in xs if x >= 70]; lo = [x for x in xs if x <= 30]
        pull = 0.75 if idx == 0 else 0.25               # ENRG pulls hard, CROWD barely
        if hi and not lo:
            peak = max(xs); share = (len(hi) ** 0.6) / ((len(hi) ** 0.6) + 0.25 * (len(xs) - len(hi)))
            out.append(base + pull * share * (peak - base))
        else:
            out.append(base)
    return round(out[0]), round(out[1])

STOPS = [combine(i) for i in range(2)]
TALKERS = [m for m in ROOM if m.talk >= 70]

print('=' * 96)
print('THE ROOM'.ljust(20), 'drew')
for m in ROOM:
    print(' ', m.name.ljust(7), ' -> '.join('stop %d  energy %2d  crowd %2d' % (i + 1, e, c)
          for i, (e, c) in enumerate(m.skeleton)), '  | TALK', m.talk, 'MOVE', m.move, 'AFFIL', m.affil)
print()
print('  combined, per stop (contagion runs per stop):')
for i, (e, c) in enumerate(STOPS):
    print('    stop %d @ %d:00   energy %d   crowd %d' % (i + 1, HOURS[i], e, c))
print('  firm talkers in the room:', ', '.join(m.name for m in TALKERS) or 'none',
      '-> TALK floor %d applies at every stop' % TALK_FLOOR)

# ============================================================ STOP -> TYPE (what the preview already shows)
TYPE_TARGET = {
    'table for the night': (25, 35, 90), 'quiet bar': (35, 40, 85), 'buzzy restaurant': (55, 70, 65),
    'pub': (60, 70, 55), 'lounge / rooftop': (50, 60, 60), 'live room': (65, 70, 25), 'club': (90, 90, 10),
}
# games types are only offered when somebody actually wants games - otherwise they win on
# arithmetic and a room with no interest in pool gets sent to a games bar
GAMES_TYPES = {'games pub': (55, 60, 60), 'games bar': (65, 65, 45)}
def type_for(e, c, talk_floor):
    best, bestd = None, 1e9
    for t, (te, tc, tt) in TYPE_TARGET.items():
        if talk_floor and tt < talk_floor: continue
        d = abs(te - e) * 1.0 + abs(tc - c) * 0.6
        if d < bestd: best, bestd = t, d
    return best

WANT_TYPE = [type_for(e, c, TALK_FLOOR) for e, c in STOPS]
print()
print('  the skeleton already resolved each stop to a type while it was being drawn:')
for i, t in enumerate(WANT_TYPE):
    print('    stop %d -> %s' % (i + 1, t))

# ============================================================ THE ROOM'S NEEDS PER STOP
def register_for(e, talkers):
    if talkers: return 'conversational' if e < 62 else 'social'
    return 'loud' if e >= 72 else ('social' if e >= 55 else 'conversational')
def role_for(i):
    peak = max(range(len(STOPS)), key=lambda k: STOPS[k][0])
    return 'warm-up' if i < peak else ('peak' if i == peak else 'wind-down')

ROOM_PREF = {}
for m in ROOM:
    for k, val in m.prefs.items():
        ROOM_PREF[k] = ROOM_PREF.get(k, 0) + val
ROOM_PREF = {k: v / len(ROOM) for k, v in sorted(ROOM_PREF.items(), key=lambda kv: -kv[1])}

# ============================================================ THE FOUR RUNGS
def select(i):
    hour, (e, c), want = HOURS[i], STOPS[i], WANT_TYPE[i]
    need_reg, need_role = register_for(e, TALKERS), role_for(i)
    print()
    print('-' * 96)
    print('STOP %d  @ %d:00   want type "%s"   character wanted: %s / %s' % (i + 1, hour, want, need_role, need_reg))
    notes = []

    # ---- rung 0: the type, at that hour, inside the radius. Widen the radius before anything else.
    radius = RADIUS
    pool = [v for v in V if type_at(v, hour) == want and v['km'] <= radius]
    while not pool and radius < RADIUS * 2:
        radius += 4
        pool = [v for v in V if type_at(v, hour) == want and v['km'] <= radius]
        if pool: notes.append('radius widened to %.0f km to find a %s open at %d:00' % (radius, want, hour))
    if not pool:
        # ---- last rung: the type does not exist near us at this hour. Take the nearest type that
        # still clears the talk floor, and SAY SO on the card.
        alts = [(t, abs(TYPE_TARGET[t][0] - e) + 0.6 * abs(TYPE_TARGET[t][1] - c))
                for t in TYPE_TARGET if TYPE_TARGET[t][2] >= TALK_FLOOR and t != want]
        for t, _ in sorted(alts, key=lambda x: x[1]):
            pool = [v for v in V if type_at(v, hour) == t and v['km'] <= radius]
            if pool:
                notes.append('no %s open at %d:00 within %.0f km - closest kind of place is a %s' % (want, hour, radius, t))
                want = t
                break
    print('  rung 0  type + inside %.0f km ............ %d venues: %s' % (radius, len(pool), ', '.join(x['name'] for x in pool)))
    for nt in notes: print('          ! ' + nt)
    if not pool:
        print('  nothing of any compatible type is open. The card says so.')
        return None

    # ---- rung 1: character = (role, register). Relax role first, then register, never the type.
    r1 = [v for v in pool if v['register'] == need_reg and role_of(v, hour) == need_role]
    relaxed = ''
    if not r1:
        r1 = [v for v in pool if v['register'] == need_reg]; relaxed = ' (role relaxed)'
    if not r1:
        r1 = [v for v in pool if role_of(v, hour) == need_role]; relaxed = ' (register relaxed)'
    if not r1:
        r1 = pool; relaxed = ' (character relaxed)'
    print('  rung 1  character%s ................... %d venues: %s' % (relaxed, len(r1), ', '.join(x['name'] for x in r1)))

    # ---- rung 2: how close the venue's own curve sits to what they drew, at this hour
    def fit(v):
        ve, vc = v['curve'][hour]
        return 1 - (abs(ve - e) + 0.6 * abs(vc - c)) / 160.0
    r2 = sorted(r1, key=fit, reverse=True)
    print('  rung 2  curve match at %d:00 ............. %s' % (hour,
          ' | '.join('%s %.2f' % (x['name'], fit(x)) for x in r2)))

    # ---- rung 3: the room's preferences, over the venues still standing
    def pscore(v):
        tot = sum(w * min(v['prefs'].get(k, 40), w) for k, w in ROOM_PREF.items())
        return tot / (sum(ROOM_PREF.values()) * 60.0)
    keep = [x for x in r2 if fit(x) >= fit(r2[0]) - 0.08] or r2[:2]
    r3 = sorted(keep, key=pscore, reverse=True)
    print('  rung 3  room preferences (%s) ... %s' % (
          ', '.join('%s %d' % (k, round(v)) for k, v in list(ROOM_PREF.items())[:3]),
          ' | '.join('%s %.2f' % (x['name'], pscore(x)) for x in r3)))

    # ---- rung 4: quality, and only as a tie-break
    close = [x for x in r3 if abs(pscore(x) - pscore(r3[0])) < 0.04]
    pick = max(close, key=lambda x: x['quality'])
    print('  rung 4  quality, within type+area ....... %s' % ' | '.join('%s %d' % (x['name'], x['quality']) for x in close))
    print('  PICK -> %s (%s)%s' % (pick['name'], pick['area'], '' if len(close) == 1 else '   [quality broke a %d-way tie]' % len(close)))
    pick['_note'] = notes
    pick['_type'] = want
    return pick

picks = [select(i) for i in range(2)]

print()
print('=' * 96)
print('THE NIGHT')
for i, p in enumerate(picks):
    ve, vc = p['curve'][HOURS[i]]
    print('  %d:00  %-22s %-12s  %-20s venue curve here: energy %d crowd %d' %
          (HOURS[i], p['name'], p['area'], '[' + p['_type'] + ']', ve, vc))
    for nt in p.get('_note', []): print('        ! ' + nt)
print()
print('  what could not be served:')
for m in ROOM:
    worst = [k for k, val in m.prefs.items() if val >= 75 and
             not any(pk['prefs'].get(k, 40) >= 60 for pk in picks)]
    if worst: print('    %s - %s' % (m.name, ', '.join(worst)))
