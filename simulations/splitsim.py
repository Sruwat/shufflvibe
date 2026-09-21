# -*- coding: utf-8 -*-
"""The split model (§14): seven vibe factors negotiate the shape -> a venue TYPE per stop;
six preferences pick the exact venue of that type. Debt/payback/friend mode on vibe only."""
from itertools import product
VIBE  = ['ENRG', 'AFFIL', 'CROWD', 'TALK', 'ROAM', 'MOVE', 'GAMES']
PREFS = ['FOOD', 'LIVE', 'POL', 'SCEN', 'NOV', 'HERIT']
NIGHT_LEVEL = ['ROAM']
FIRM, WANT_FLOOR, BASE_BEND = 0.5, 25, 0.20
SECOND_STRONG, SECOND_GAP, STRONG2, SOFT, DEBT_TRIGGER, DEBT_K, SERVED_FLOOR, OVERRUN_W, MAX_STOPS = 25, 10, 0.85, 0.5, 0.5, 0.6, 0.85, 0.01, 3
PREF_WHOLE, DELIVERS = 75, 55
FRIEND_MAX_GIVE, FRIEND_MARGIN = 70, 10

class M:
    def __init__(s, name, refused=(), sense='both', **sc):
        s.name = name; s.vibe = {f: 50 for f in VIBE}; s.pref = {f: 50 for f in PREFS}; s.sense = sense
        for k, v in sc.items(): (s.vibe if k in VIBE else s.pref)[k] = v
        s.refused = set(refused)                      # vibe factors hard-passed: firm low pole, a wall
        for f in s.refused: s.vibe[f] = 12
    def firm(s, f): return abs(s.vibe[f] - 50) / 50
    def bend(s, f): return 100 * BASE_BEND * (1 + 1.2 * (1 - s.firm(f)))
    def pole(s, f): return 'high' if s.vibe[f] >= 50 else 'low'
    def overall(s): return sum(1 for f in VIBE if abs(s.vibe[f] - 50) >= 38) / 7.0
def debt_scale(m): return 0.5 + m.overall()

# ---------------- venue types (FACTORS_V5 §4), on the six stop-level axes
TYPES = {
 'table for the night': dict(ENRG=25, AFFIL=85, CROWD=35, TALK=90, MOVE=10, GAMES=15),
 'quiet bar':           dict(ENRG=35, AFFIL=75, CROWD=40, TALK=85, MOVE=15, GAMES=20),
 'buzzy restaurant':    dict(ENRG=55, AFFIL=70, CROWD=70, TALK=65, MOVE=15, GAMES=10),
 'pub':                 dict(ENRG=60, AFFIL=60, CROWD=70, TALK=55, MOVE=25, GAMES=45),
 'games bar':           dict(ENRG=65, AFFIL=65, CROWD=65, TALK=45, MOVE=40, GAMES=90),
 'live room':           dict(ENRG=65, AFFIL=50, CROWD=70, TALK=25, MOVE=45, GAMES=10),
 'lounge / rooftop':    dict(ENRG=50, AFFIL=45, CROWD=60, TALK=60, MOVE=20, GAMES=10),
 'club':                dict(ENRG=90, AFFIL=30, CROWD=90, TALK=10, MOVE=90, GAMES=5),
 'street / market':     dict(ENRG=60, AFFIL=55, CROWD=85, TALK=60, MOVE=60, GAMES=10),
 'open ground':         dict(ENRG=50, AFFIL=70, CROWD=40, TALK=75, MOVE=70, GAMES=40),
}
STOP_AXES = ['ENRG', 'AFFIL', 'CROWD', 'TALK', 'MOVE', 'GAMES']

class V:
    def __init__(s, name, type, **sc):
        s.name, s.type = name, type; s.pref = {f: 40 for f in PREFS}; s.pref.update(sc); s.sense = sc.get('sense', 'both')
VENUES = [
 V('Piano Man (Safdarjung)',  'live room',        LIVE=90, FOOD=65, POL=65, SCEN=65, HERIT=30),
 V('jazz bar (Lodhi)',        'quiet bar',        LIVE=85, FOOD=55, POL=70, SCEN=60, HERIT=40),
 V('cocktail bar (Khan)',     'quiet bar',        LIVE=20, FOOD=60, POL=85, SCEN=75, HERIT=30, sense='classy'),
 V('quiet restaurant (HKV)',  'table for the night', LIVE=20, FOOD=90, POL=60, SCEN=70, HERIT=35),
 V('haveli restaurant (Old Delhi)', 'table for the night', LIVE=30, FOOD=85, POL=40, SCEN=80, HERIT=90),
 V('Depot 48 (GK-2)',         'buzzy restaurant', LIVE=60, FOOD=78, POL=60, SCEN=60, HERIT=30),
 V('busy diner (CP)',         'buzzy restaurant', LIVE=20, FOOD=85, POL=50, SCEN=50, HERIT=30),
 V('brewery (Sector 29)',     'pub',              LIVE=40, FOOD=65, POL=40, SCEN=45, HERIT=20),
 V('bar with live band (GK)', 'pub',              LIVE=65, FOOD=45, POL=45, SCEN=45, HERIT=25),
 V('arcade bar (CP)',         'games bar',        LIVE=20, FOOD=45, POL=35, SCEN=35, HERIT=20),
 V('bowling alley (Saket)',   'games bar',        LIVE=10, FOOD=55, POL=40, SCEN=40, HERIT=20),
 V('rooftop lounge (Aerocity)', 'lounge / rooftop', LIVE=30, FOOD=65, POL=90, SCEN=90, HERIT=30, sense='classy'),
 V('club (Aerocity)',         'club',             LIVE=30, FOOD=30, POL=85, SCEN=60, HERIT=20, sense='current'),
 V('warehouse (Chhatarpur)',  'club',             LIVE=40, FOOD=20, POL=45, SCEN=50, HERIT=30),
 V('gig venue (dead lane)',   'live room',        LIVE=92, FOOD=30, POL=30, SCEN=40, HERIT=20),
 V('Old Delhi food walk',     'street / market',  LIVE=10, FOOD=88, POL=15, SCEN=80, HERIT=90),
 V('Sunder Nursery lawn',     'open ground',      LIVE=20, FOOD=50, POL=50, SCEN=95, HERIT=80),
]

# ---------------- vibe wants (both poles), serving on a TYPE
def ranked_wants(m):
    return [f for f in sorted(STOP_AXES, key=lambda f: -abs(m.vibe[f] - 50)) if abs(m.vibe[f] - 50) >= WANT_FLOOR]
def second_is_strong(m):
    w = ranked_wants(m)
    return len(w) >= 2 and abs(m.vibe[w[1]] - 50) >= SECOND_STRONG and abs(m.vibe[w[0]] - 50) - abs(m.vibe[w[1]] - 50) <= SECOND_GAP
def ceiling(m, f, members, friends):
    """The far edge of m's bend on the pole OPPOSITE their want; friends stretch it - on the
    colliding factor, and on any factor of m's that EVERY type serving the friend's want overruns
    (an ENRG-high want implies a loud room: the friend's TALK stretches too)."""
    own = m.bend(f)
    give = 0
    for o in members:
        if o is m or (m.name, o.name) not in friends: continue
        if o.firm(f) >= FIRM and o.pole(f) != m.pole(f):
            need = abs(o.vibe[f] - m.vibe[f]) - o.bend(f) + FRIEND_MARGIN
            give = max(give, min(need, FRIEND_MAX_GIVE) - own)
        for g in STOP_AXES:                                   # implied: o's want on g forces types that overrun m on f
            if g == f or o.firm(g) < FIRM or m.firm(f) < FIRM: continue
            serving = [t for t in TYPES.values() if delivers(t, o, g)]
            if serving and all(_raw_over(t, m, f) > own for t in serving):
                need = min(_raw_over(t, m, f) for t in serving) + FRIEND_MARGIN
                give = max(give, min(need, FRIEND_MAX_GIVE) - own)
    return own + max(0, give)
def _raw_over(t, m, f):
    return (t[f] - m.vibe[f]) if m.pole(f) == 'low' else (m.vibe[f] - t[f])
def overrun(t, m, f, members=(), friends=frozenset()):
    d = (t[f] - m.vibe[f]) if m.pole(f) == 'low' else (m.vibe[f] - t[f])     # distance toward the pole they DON'T want
    return d - ceiling(m, f, members or [m], friends)
def violated(t, m, f): return False    # no walls on vibe factors: a hard pass is a firm want, served or conceded like any other
def delivers(t, m, f):
    return (t[f] >= m.vibe[f] - m.bend(f)) if m.pole(f) == 'high' else (t[f] <= m.vibe[f] + m.bend(f))
def serve_level(t, m, promoted=()):
    if any(violated(t, m, f) for f in STOP_AXES if m.firm(f) >= 0.75): return 0.0, None, None
    opts = []
    order = list(promoted) + [f for f in ranked_wants(m) if f not in promoted]
    for rank, f in enumerate(order, 1):
        if delivers(t, m, f):
            lvl = 1.0 if rank == 1 else (STRONG2 if second_is_strong(m) or f in promoted else SOFT) if rank == 2 else 1.0 / rank
            opts.append((lvl, 1, f, 'type'))
        elif (t[f] >= 50) == (m.pole(f) == 'high'):
            opts.append((SOFT, 0, f, 'partial'))
    if not opts: return 0.0, None, None
    lvl, _, f, how = max(opts); return lvl, f, how
def over_points(t, m, members, friends):
    return sum(max(0.0, overrun(t, m, f, members, friends)) for f in STOP_AXES if m.firm(f) >= FIRM)

# ---------------- §14.3.2 the negotiation on night-level factors
def negotiate_night(members, friends, trace):
    shape, owed = {}, {m.name: [] for m in members}
    for f in NIGHT_LEVEL:
        firm = [m for m in members if m.firm(f) >= FIRM]
        if not firm: shape[f] = 50; continue
        poles = {m.pole(f) for m in firm}
        if len(poles) == 1:
            shape[f] = sum(m.vibe[f] * m.firm(f) for m in firm) / sum(m.firm(f) for m in firm)
        else:
            shape[f] = sum(m.vibe[f] * m.firm(f) for m in firm) / sum(m.firm(f) for m in firm)
            for m in firm:
                if abs(shape[f] - m.vibe[f]) > m.bend(f): owed[m.name].append(f)
            trace.append(f'   {f} collides ({", ".join(f"{m.name} {m.vibe[f]}" for m in firm)}) -> settled at {shape[f]:.0f}; owed: {[n for n, v in owed.items() if v] or "nobody"}')
    promoted = {m.name: [] for m in members}
    for m in members:
        if owed[m.name]:
            nxt = [f for f in sorted(STOP_AXES, key=lambda g: -abs(m.vibe[g] - 50)) if abs(m.vibe[f] - 50) >= WANT_FLOOR]
            if nxt: promoted[m.name].append(nxt[0]); trace.append(f'   payback: {m.name}\'s {nxt[0]} promoted into the stop shape')
    return shape, promoted
def n_stops(roam, hours=5):
    by_roam = 1 if roam < 35 else 2 if roam < 65 else 3
    return min(by_roam, max(1, min(3, int(hours // 1.75))))

# ---------------- §14.3.3 the type per stop (pick_best over types, debt/payback)
def room_target(members):
    return {f: (sum(m.vibe[f] * max(m.firm(f), 0.05) for m in members) / sum(max(m.firm(f), 0.05) for m in members)) for f in STOP_AXES}
def coverage(tname, members, had):
    """How many un-had whole-point preferences some venue of this type could serve (the last shape tie-break)."""
    return sum(1 for m in members for f in PREFS if m.pref[f] >= PREF_WHOLE and f not in had.get(m.name, set())
               and any(v.type == tname and venue_has(v, f, m) for v in VENUES))
def pick_type(cands, members, debt, promoted, friends, ignore_zero=(), first=False, prev_type=None, had=None):
    best = None; tgt = room_target(members); had = had or {}
    for name, t in cands:
        levels = {m.name: serve_level(t, m, promoted[m.name]) for m in members}
        if any(violated(t, m, f) for m in members for f in STOP_AXES if m.firm(f) >= 0.75): continue
        if not all(levels[m.name][0] > 0 or over_points(t, m, members, friends) == 0 for m in members): continue
        nobody = sum(1 for m in members if m not in ignore_zero and ranked_wants(m) and levels[m.name][0] == 0)
        served = sum(l[0] * (1 + DEBT_K * debt[n]) for n, l in levels.items())
        cost = OVERRUN_W * sum(over_points(t, m, members, friends) for m in members)
        if name == 'open ground' and not first: continue                       # a lawn is an early-evening type
        variety = 1 if name == prev_type else 0
        l1 = sum(abs(t[f] - tgt[f]) * max(m.firm(f) for m in members) for f in STOP_AXES)   # closeness on the axes somebody is firm on
        key = (-nobody, round(served, 2), -round(cost, 2), -variety, -t['ENRG'] if first else 0, coverage(name, members, had), -l1)
        if best is None or key > best[0]: best = (key, name, levels)
    return best

def shape_night(members, friends, trace, hours=5):
    shape, promoted = negotiate_night(members, friends, trace)
    n = n_stops(shape['ROAM'], hours)
    trace.append(f'   ROAM {shape["ROAM"]:.0f} -> {n} stop(s)')
    wanting = [m for m in members if ranked_wants(m)]
    debt = {m.name: 0.0 for m in members}; best_got = {m.name: 0.0 for m in members}; paid = set(); had_own = set()
    # reach: can each person ever be served on a type with everyone passing?
    reach = {}
    for m in wanting:
        lv = [serve_level(t, m, promoted[m.name])[0] for nm, t in TYPES.items()
              if pick_type([(nm, t)], members, debt, promoted, friends) is not None]
        reach[m.name] = max(lv or [0.0])
    reserved = [m for m in wanting if reach[m.name] < SERVED_FLOOR]
    if reserved:
        n = min(MAX_STOPS, max(n, len(reserved) + (1 if len(reserved) < len(wanting) else 0)))
        trace.append(f'   reserved one-each stops: {[m.name for m in reserved]} (night is {n} stops)')
    stops = []; prev = -1; ordinary = n - len(reserved); had_own = set(reserved); had = {m.name: set() for m in members}
    for k in range(n):
        if k >= ordinary:
            m = reserved[k - ordinary]
            cands = [(nm, t) for nm, t in TYPES.items() if serve_level(t, m, promoted[m.name])[0] >= 0.85
                     and not any(violated(t, o, f) for o in members for f in STOP_AXES if o.firm(f) >= 0.75)]
            others = [o for o in members if o is not m]
            if not cands: trace.append(f'   no type serves {m.name} at all -> not a fit'); return stops, shape
            nm, t = max(cands, key=lambda c: (sum(serve_level(c[1], o)[0] for o in others) - OVERRUN_W * sum(over_points(c[1], o, members, friends) for o in others)))
            levels = {x.name: serve_level(t, x, promoted[x.name]) for x in members}
            stops.append((nm, levels, 'DEDICATED to ' + m.name)); prev = t['ENRG']; continue
        owed = [m for m in wanting if debt[m.name] >= DEBT_TRIGGER and m.name not in paid and m not in had_own]
        cands = [(nm, t) for nm, t in TYPES.items() if t['ENRG'] >= prev - 10] or list(TYPES.items())
        note = ''
        if owed:
            pay = [(nm, t) for nm, t in TYPES.items() if all(serve_level(t, o, promoted[o.name])[0] >= 0.85 for o in owed)
                   and pick_type([(nm, t)], members, debt, promoted, friends) is not None]
            if pay: cands = pay; note = 'payback for ' + ', '.join(o.name for o in owed)
        prev_type = stops[-1][0] if stops else None
        best = pick_type(cands, members, debt, promoted, friends, ignore_zero=had_own, first=(k == 0), prev_type=prev_type, had=had)
        if best is None or (best[0][0] < 0):
            alt = pick_type(list(TYPES.items()), members, debt, promoted, friends, ignore_zero=had_own, first=(k == 0), prev_type=prev_type, had=had)
            if alt and alt[0][0] == 0: best = alt; note = (note + '; ' if note else '') + 'arc dropped so nobody gets nothing'
        if best is None: trace.append('   no type passes for everyone -> relax / not a fit'); return stops, shape
        _, nm, levels = best; t = TYPES[nm]
        stops.append((nm, levels, note)); prev = t['ENRG']
        for m in members:
            for f in PREFS:
                if m.pref[f] >= PREF_WHOLE and any(v.type == nm and venue_has(v, f, m) for v in VENUES): had[m.name].add(f)
        for m in wanting:
            lvl, f, how = levels[m.name]
            got_paid = (m in owed and lvl >= 0.85)
            if m in reserved: continue
            debt[m.name] = 0.0 if got_paid else debt[m.name] + (1.0 - lvl) * debt_scale(m)
            best_got[m.name] = max(best_got[m.name], lvl)
            if got_paid or lvl == 1.0: paid.add(m.name)
    return stops, shape

# ---------------- §14.4 fill
def sense_ok(v, m): return v.sense == 'both' or m.sense == 'both' or v.sense == m.sense
def venue_has(v, f, m):
    if f == 'POL': return v.pref['POL'] >= DELIVERS and sense_ok(v, m)
    if f == 'NOV': return True                                   # everything is new tonight
    return v.pref[f] >= DELIVERS
def fill(stops, members, trace):
    had = {m.name: set() for m in members}; used = set(); out = []
    for k, (tname, levels, note) in enumerate(stops):
        pool = [v for v in VENUES if v.type == tname and v.name not in used]
        if not pool: out.append((tname, None, levels, note, {})); trace.append(f'   stop {k+1}: no venue of type "{tname}" in the pool'); continue
        def fit(v):
            tot = 0.0
            for m in members:
                for f in PREFS:
                    w = m.pref[f] / 100
                    if f == 'POL' and not sense_ok(v, m): continue
                    val = 100 if f == 'NOV' else v.pref[f]
                    urgent = 2 if m.pref[f] >= PREF_WHOLE and f not in had[m.name] else 1
                    tot += w * urgent * min(val, m.pref[f])
            return tot
        v = max(pool, key=fit); used.add(v.name)
        served_pref = {}
        for m in members:
            got = [f for f in PREFS if m.pref[f] >= 60 and venue_has(v, f, m)]
            for f in got:
                if m.pref[f] >= PREF_WHOLE: had[m.name].add(f)
            served_pref[m.name] = got
        out.append((tname, v, levels, note, served_pref))
    missing = {m.name: [f for f in PREFS if m.pref[f] >= PREF_WHOLE and f not in had[m.name]] for m in members}
    return out, {k: v for k, v in missing.items() if v}

def plan(members, friends=frozenset(), hours=6):
    trace = []
    stops, shape = shape_night(members, friends, trace, hours)
    filled, missing = fill(stops, members, trace)
    for k, (tname, v, levels, note, sp) in enumerate(filled):
        line = f'  stop {k+1}: [{tname}] {v.name if v else "-"}'
        for m in members:
            lvl, f, how = levels[m.name]
            vibe_line = f'{f} {m.pole(f)} {lvl:.2f}{" (partial)" if how == "partial" else ""}' if f else '- 0'
            line += f' | {m.name}: {vibe_line:<22} prefs {",".join(sp.get(m.name, [])) or "-"}'
        if note: line += '  <- ' + note
        trace.append(line)
    trace.append('   whole-point preferences never had: ' + (', '.join(f'{k}: {v}' for k, v in missing.items()) if missing else 'none'))
    return trace

def show(title, members, friends=frozenset(), hours=6):
    print('\n' + title)
    for m in members:
        print(f'   {m.name:<7} vibe wants {[(f, m.pole(f), m.vibe[f]) for f in ranked_wants(m)]}{"  ROAM " + str(m.vibe["ROAM"]) if abs(m.vibe["ROAM"]-50) >= WANT_FLOOR else ""}  | prefs {[(f, m.pref[f]) for f in PREFS if m.pref[f] >= 60]}')
    print('\n'.join(plan(members, friends, hours)))

if __name__ == '__main__':
    F = lambda *names: frozenset({(a, b) for a in names for b in names if a != b})
    show('ROAM example (user): A ROAM high firm, CROWD high · B AFFIL high firm, ROAM low firm',
         [M('A', ROAM=92, CROWD=80), M('B', AFFIL=90, ROAM=12, GAMES=72)])
    show('ROAM example, A firmer on ROAM (95 vs B 25)',
         [M('A', ROAM=95, CROWD=80), M('B', AFFIL=90, ROAM=25, GAMES=72)])
    show('U. the Piano Man room: Aarav ENRG high, CROWD · Bela ENRG low firm + LIVE whole-point · Chirag FOOD whole-point',
         [M('Aarav', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Chirag', FOOD=88, ROAM=62)])
    show('F. "Ruchi wants a gig, the boys hate live music" - LIVE is a preference now',
         [M('Aarav', ENRG=85, CROWD=80, LIVE=12), M('Divit', ENRG=85, CROWD=80, LIVE=12), M('Ruchi', LIVE=92, HERIT=62, ROAM=70)])
    show('E. the quaint pub: Priya AFFIL high + ENRG low · Sana & Ria SCEN whole-point (a preference now)',
         [M('Priya', AFFIL=92, ENRG=20, CROWD=25), M('Sana', SCEN=90, POL=80, sense='classy'), M('Ria', SCEN=85, POL=75)])
    show('S. the mutual wall: Aarav ENRG high · Bela ENRG low firm, TALK high · Chirag FOOD',
         [M('Aarav', ENRG=88, CROWD=70, ROAM=70), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Chirag', FOOD=88)])
    show('H. two firm camps on ENRG, two people', [M('Aarav', ENRG=90, CROWD=85, ROAM=60), M('Neha', ENRG=15, TALK=85, FOOD=92)])
    show('L. FRIENDS: A ENRG high firm · B ENRG low firm - relaxed bends', [M('A', ENRG=90, CROWD=75, LIVE=12), M('B', ENRG=15, TALK=80, LIVE=88)], F('A', 'B'))
    show('O. the same two, NOT friends', [M('A', ENRG=90, CROWD=75, LIVE=12), M('B', ENRG=15, TALK=80, LIVE=88)])
    show('N. GAMES high vs HERIT whole-point - no collision now', [M('A', GAMES=90, ROAM=30), M('B', HERIT=90, FOOD=70, ROAM=30)])
    show('I. one firm person, two easy ones', [M('Aarav', ENRG=88, CROWD=80), M('Divit'), M('Neha', FOOD=58)])
    show('T. the whole team out: three high AFFIL, ENRG, GAMES', [M('A', AFFIL=88, ENRG=85, GAMES=80, ROAM=75), M('B', AFFIL=85, ENRG=80, GAMES=88), M('C', AFFIL=90, ENRG=88, GAMES=70, FOOD=88)])
    show('P2. Priya hosts: Sana (friend), Kabir, Rohan', [M('Priya', AFFIL=70, ENRG=30, CROWD=40, FOOD=88, SCEN=72, POL=65, sense='classy'), M('Sana', ENRG=35, TALK=75, SCEN=90, POL=80), M('Kabir', CROWD=30, FOOD=88, SCEN=70), M('Rohan', ENRG=70, CROWD=65, LIVE=85)], F('Priya', 'Sana'))
