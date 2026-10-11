# -*- coding: utf-8 -*-
"""Run §13.4c (debt/payback across stops) on a handful of rooms and a small venue pool.
Venue first; the area only serves a want the venue itself cannot (the user's correction)."""
FACTORS = ['CROWD','ENRG','SCEN','FOOD','POL','NOV','PLAY','LIVE','HERIT','AFFIL']
WANT_FLOOR, DELIVERS = 60, 55
SECOND_STRONG, SECOND_GAP, STRONG2, SOFT, DEBT_TRIGGER, DEBT_K = 70, 10, 0.85, 0.5, 0.5, 0.6
AREA_FACTORS = {'CROWD','ENRG','POL','SCEN'}
BASE_BEND = 0.20

class M:
    def __init__(s, name, refused=(), **sc):
        s.name = name; s.scores = {f: 50 for f in FACTORS}; s.scores.update(sc); s.refused = set(refused)
    def firm(s, f): return abs(s.scores[f]-50)/50
    def bend_pts(s, f): return 100*BASE_BEND*(1+1.2*(1-s.firm(f)))
class V:
    def __init__(s, name, area=None, **sc):
        s.name = name; s.area = area; s.sc = {f: 30 for f in FACTORS}; s.sc.update(sc)
    def __getitem__(s, f): return 75 if f == 'NOV' else s.sc[f]     # every venue is new tonight -> NOV served (§13.4b)
class Stop:
    def __init__(s, venue, levels, dedicated=None): s.venue, s.levels, s.dedicated = venue, levels, dedicated

def ranked_wants(m):
    hi = max(m.scores.values())
    out = [f for f in sorted(FACTORS, key=lambda f: -m.scores[f]) if m.scores[f] >= WANT_FLOOR]
    return [f for f in out if f != 'AFFIL' or m.scores[f] == hi]
def second_is_strong(m):
    w = ranked_wants(m)
    return len(w) >= 2 and m.scores[w[1]] >= SECOND_STRONG and m.scores[w[0]]-m.scores[w[1]] <= SECOND_GAP
def delivers_at(score, m, f): return score >= m.scores[f] - m.bend_pts(f) and score >= DELIVERS
AVERSION_FLOOR = 55   # a venue below this on f is not 'the thing' and cannot overrun an aversion to it
def violated(v, m, f): return v[f] >= AVERSION_FLOOR and v[f] > m.scores[f] + m.bend_pts(f) + 15
def overrun(v, m, f): return (v[f] - (m.scores[f] + m.bend_pts(f))) if v[f] >= AVERSION_FLOOR else -1

def serve_level(v, m):
    if any(violated(v, m, f) for f in m.refused): return 0.0, None, None
    opts = []
    for rank, f in enumerate(ranked_wants(m), 1):
        if delivers_at(v[f], m, f):                         # the venue itself
            lvl = 1.0 if rank == 1 else (STRONG2 if second_is_strong(m) else SOFT) if rank == 2 else 1.0/rank
            opts.append((lvl, 1, f, 'venue'))
        elif f in AREA_FACTORS and v.area and delivers_at(v.area[f], m, f):   # fallback: the area
            opts.append((SOFT, 0, f, 'area'))
    if not opts: return 0.0, None, None
    lvl, _, f, how = max(opts); return lvl, f, how

def in_bend(v, members, skip=()):
    return not any(overrun(v, m, f) > 0 for m in members if m not in skip for f in FACTORS if m.scores[f] < 50)

def pick_best(pool, members, debt, ignore_zero=()):
    best = None
    for v in pool:
        if not in_bend(v, members): continue                       # bend check, everyone, every stop
        levels = {m.name: serve_level(v, m) for m in members}
        nobody = sum(1 for m in members if m not in ignore_zero and ranked_wants(m) and levels[m.name][0] == 0)
        served = sum(l[0]*(1+DEBT_K*debt[n]) for n, l in levels.items())
        key = (-nobody, served)
        if best is None or key > best[0]: best = (key, Stop(v, levels))
    return best[1] if best else None

def dedicated_stop(m, pool, members):
    """The venue that best serves m's #1. Others' bend NOT checked (this is the compromise);
    a hard refusal is still a wall."""
    f = ranked_wants(m)[0]
    ok = [v for v in pool if delivers_at(v[f], m, f) and not any(violated(v, o, g) for o in members if o is not m for g in o.refused)]
    if not ok: return None
    v = max(ok, key=lambda v: v[f])
    levels = {m.name: (1.0, f, 'venue')}; levels.update({o.name: (0.0, None, 'dedicated') for o in members if o is not m})
    return Stop(v, levels, dedicated=m.name)

def plan(members, venues, n_stops, trace):
    debt = {m.name: 0.0 for m in members}; got = {m.name: 0.0 for m in members}; top_served = set()
    chosen = []; prev = -1; pending = None; had = set()
    for k in range(n_stops):
        last = k == n_stops - 1
        remaining = [v for v in venues if v not in chosen]
        pool = [v for v in remaining if v['ENRG'] >= prev - 10]
        if not pool: pool = remaining; trace.append('           (arc dropped - nothing left within it; the night winds down)')
        owed = [m for m in members if ranked_wants(m) and debt[m.name] >= DEBT_TRIGGER and m not in had and m.name not in top_served]
        note = ''; best = None
        if pending:                                   # the stop promised last time
            best = dedicated_stop(pending, remaining, members); note = 'DEDICATED to ' + pending.name
            had.add(pending); pending = None
        else:
            # stranded = cannot be served on anything at any venue the others tolerate
            st = [m for m in members if m not in had and ranked_wants(m) and
                  not any(serve_level(v, m)[0] > 0 and in_bend(v, members) for v in remaining)]
            if len(st) >= 2:
                trace.append(f'  stop {k+1}: {" and ".join(m.name for m in st)} can each be served nowhere the others tolerate -> not one person left out but a room that does not work: relax (§13.1) / not a fit'); return chosen
            if st:
                m = st[0]
                if got[m.name] > 0:                    # they had something earlier; zeros from here are accepted
                    had.add(m)
                else:
                    others = [o for o in members if o is not m]
                    ded = dedicated_stop(m, remaining, members)
                    if ded is None:
                        trace.append(f'  stop {k+1}: {m.name} can be served nowhere the others tolerate, and a hard refusal blocks a dedicated stop -> relax (§13.1) / not a fit'); return chosen
                    if last: best = ded; note = 'DEDICATED to ' + m.name; had.add(m)
                    else:    pending = m; note = m.name + ' gets nothing here - their stop is next'
            if best is None:
                pool2 = pool
                if owed:
                    pays = lambda v: all(serve_level(v, o)[1:] == (ranked_wants(o)[0], 'venue') for o in owed) and in_bend(v, members)
                    pay = [v for v in pool if pays(v)] or [v for v in remaining if pays(v)]      # the debt outranks the arc
                    if pay: pool2 = pay; note = (note + '; ' if note else '') + 'payback for ' + ', '.join(o.name for o in owed)
                    else:   note = (note + '; ' if note else '') + 'no venue pays ' + ', '.join(o.name for o in owed) + ' within everyone\'s bend - best available, debt stays'
                best = pick_best(pool2, members, debt, ignore_zero=had | ({pending} if pending else set()))
            if best is None:
                trace.append(f'  stop {k+1}: no venue within everyone\'s bend -> relax (§13.1)'); return chosen
        chosen.append(best.venue); prev = best.venue['ENRG']
        line = f'  stop {k+1}: {best.venue.name:<26}'
        for m in members:
            lvl, f, how = best.levels[m.name]
            paid = (m in owed and lvl == 1.0 and how == 'venue') or best.dedicated == m.name
            debt[m.name] = 0.0 if (paid or not ranked_wants(m)) else debt[m.name] + (1.0 - lvl)
            got[m.name] += lvl
            if lvl == 1.0 and how == 'venue': top_served.add(m.name)
            tag = f'{f} {"#"+str(ranked_wants(m).index(f)+1) if f else "-"} {lvl:.2f}{" (area)" if how=="area" else ""}{" PAID" if paid else ""}'
            line += f' | {m.name}: {tag:<24}'
        line += ' | debt ' + ' '.join(f'{n[0]}={d:.2f}' for n, d in debt.items())
        if note: line += chr(10) + '           -> ' + note
        trace.append(line)
    return chosen

# ---------------- venues (a small NCR-ish pool). area = dict of the four area factors
HKV     = {'CROWD': 85, 'ENRG': 80, 'POL': 55, 'SCEN': 90}      # Hauz Khas Village, late band
CP      = {'CROWD': 80, 'ENRG': 70, 'POL': 50, 'SCEN': 60}
AERO    = {'CROWD': 65, 'ENRG': 70, 'POL': 90, 'SCEN': 75}
DEAD    = {'CROWD': 30, 'ENRG': 25, 'POL': 40, 'SCEN': 35}
venues = [
    V('lively bar (CP)',            CP,   CROWD=85, ENRG=85, POL=55, SCEN=45, FOOD=40, AFFIL=60),
    V('busy diner (CP)',            CP,   CROWD=80, ENRG=60, POL=50, SCEN=50, FOOD=85, AFFIL=65),
    V('quiet restaurant (HKV)',     HKV,  CROWD=35, ENRG=30, POL=60, SCEN=55, FOOD=90, AFFIL=80),
    V('quaint pub (HKV)',           HKV,  CROWD=40, ENRG=35, POL=50, SCEN=50, FOOD=50, AFFIL=90),
    V('rooftop lounge (Aerocity)',  AERO, CROWD=60, ENRG=55, POL=90, SCEN=90, FOOD=65, AFFIL=55),
    V('club (Aerocity)',            AERO, CROWD=90, ENRG=92, POL=85, SCEN=60, FOOD=30, AFFIL=40),
    V('gig venue (dead lane)',      DEAD, CROWD=70, ENRG=80, POL=30, SCEN=40, FOOD=30, LIVE=92, AFFIL=45),
    V('arcade bar (CP)',            CP,   CROWD=70, ENRG=70, POL=35, SCEN=35, FOOD=45, PLAY=90, AFFIL=70),
]

rooms = {
 'A. strong #2 everywhere - nobody is ever owed': (
    [M('Aarav', ENRG=88, CROWD=82), M('Divit', ENRG=85, CROWD=80), M('Neha', FOOD=88, CROWD=80)], 3),
 'B. weak #2 -> payback at stop 2, the others on their strong #2': (
    [M('Aarav', ENRG=88, CROWD=80), M('Divit', ENRG=88, CROWD=80), M('Neha', FOOD=90, SCEN=62)], 3),
 'C. weak #2 -> payback; the others have no #2 -> the area carries their #1; stop 3 pays them': (
    [M('Aarav', ENRG=88), M('Divit', ENRG=88), M('Neha', FOOD=90, SCEN=62)], 3),
 'D. two people owed at once, wanting different things': (
    [M('Aarav', ENRG=88, CROWD=80), M('Neha', FOOD=90, SCEN=62), M('Kabir', PLAY=90, NOV=61)], 3),
 'E. the quaint pub - Priya wants AFFIL and a low-energy night; Sana and Ria want SCEN (and POL)': (
    [M('Priya', AFFIL=92, ENRG=20, CROWD=25), M('Sana', SCEN=90, POL=80), M('Ria', SCEN=85, POL=75)], 2),
 'F. dedicated stop - Ruchi wants LIVE, the other two are low and firm on it and on everything else she ranks': (
    [M('Aarav', ENRG=85, CROWD=80, LIVE=15), M('Divit', ENRG=85, CROWD=80, LIVE=15), M('Ruchi', LIVE=92, HERIT=62)], 3),
 'G. same, but Divit hard-passed LIVE': (
    [M('Aarav', ENRG=85, CROWD=80, LIVE=15), M('Divit', ENRG=85, CROWD=80, LIVE=12, refused=['LIVE']), M('Ruchi', LIVE=92, HERIT=62)], 3),
 'H. two firm camps, no overlap - nobody can be served where the other side tolerates': (
    [M('Aarav', ENRG=90, CROWD=85, FOOD=20), M('Neha', FOOD=92, ENRG=15, CROWD=20)], 2),
 'I. one firm person, two easy ones (Along for the Ride) - no debt ever, nothing to pay': (
    [M('Aarav', ENRG=88, CROWD=80), M('Divit'), M('Neha', FOOD=58)], 2),
}
if __name__ == "__main__":
  for title, (members, n) in rooms.items():
      print('\n' + title)
      for m in members:
        w = ranked_wants(m); print(f'   {m.name:<6} wants {w}  strong#2={second_is_strong(m)}  refused={sorted(m.refused)}')
      trace = []; plan(members, venues, n, trace); print('\n'.join(trace))
