# -*- coding: utf-8 -*-
"""§13.4c rules 5-7 + §13.8 overall firmness + §13.9 friend mode, run on rooms."""
from itertools import product
import debtsim as d
from debtsim import M, V, Stop, FACTORS, ranked_wants, delivers_at, violated, overrun, DEBT_TRIGGER, DEBT_K, AVERSION_FLOOR, DELIVERS, SECOND_STRONG, STRONG2, SOFT, AREA_FACTORS, second_is_strong

def serve_level(v, m):
    """§13.4c: #1 by venue 1.0; strong #2 .85; weak #2 .5; #3+ 1/rank; the venue HAS the thing (>= DELIVERS)
    but below the person's floor -> SOFT ('to whatever degree'); the area carries it -> SOFT. Nothing -> 0."""
    if any(violated(v, m, g) for g in m.refused): return 0.0, None, None
    opts = []
    for rank, g in enumerate(ranked_wants(m), 1):
        if delivers_at(v[g], m, g):
            lvl = 1.0 if rank == 1 else (STRONG2 if second_is_strong(m) else SOFT) if rank == 2 else 1.0 / rank
            opts.append((lvl, 2, g, 'venue'))
        elif v[g] >= DELIVERS:
            opts.append((SOFT, 1, g, 'partial'))
        elif g in AREA_FACTORS and v.area and delivers_at(v.area[g], m, g):
            opts.append((SOFT, 0, g, 'area'))
    if not opts: return 0.0, None, None
    lvl, _, g, how = max(opts); return lvl, g, how

# ---------- §13.8 overall firmness (sim proxy: share of factors swiped extreme)
def overall_firmness(m):
    return sum(1 for f in FACTORS if abs(m.scores[f] - 50) >= 38) / 10.0
def debt_scale(m): return 0.5 + overall_firmness(m)

# ---------- §13.9.2 relaxed bends between friend pairs
FIRM, FRIEND_MAX_GIVE, FRIEND_MARGIN, SERVED_FLOOR = 0.5, 70, 10, 0.85
def ceiling(m, f, members, friends):
    own = m.scores[f] + m.bend_pts(f)
    if m.scores[f] >= 40 or m.firm(f) < FIRM: return own
    best = own
    for o in members:
        if o is m or (m.name, o.name) not in friends: continue
        if o.scores[f] >= 60 and o.firm(f) >= FIRM:
            need = o.scores[f] - o.bend_pts(f)
            best = max(best, min(max(own, need + FRIEND_MARGIN), m.scores[f] + FRIEND_MAX_GIVE))
    return best
def in_bend(v, members, friends=frozenset()):
    return not any(v[f] >= AVERSION_FLOOR and v[f] > ceiling(m, f, members, friends) for m in members for f in FACTORS if m.scores[f] < 50)

# ---------- §13.4c rule 7: payback target = highest rank with a compatible venue
def payback_target(m, remaining, members, friends):
    for f in ranked_wants(m):
        if any(delivers_at(v[f], m, f) and passes(v, members, friends, {x.name: serve_level(v, x) for x in members}) for v in remaining): return f
    return None

# ---------- rule 6: dedicated stop with the others softened
def dedicated_stop(m, pool, members):
    """m's own bend holds at m's own stop. Try m's #1, then #2. Among venues that deliver it, the one
    where the others are served best and stepped on least; a hard refusal is still a wall."""
    others = [o for o in members if o is not m]
    for f in ranked_wants(m)[:2]:
        ok = [v for v in pool if delivers_at(v[f], m, f) and in_bend(v, [m])
              and not any(violated(v, o, g) for o in others for g in o.refused)]
        if not ok: continue
        def key(v):
            served = sum(serve_level(v, o)[0] for o in others)
            over = sum(max(0, overrun(v, o, g)) for o in others for g in FACTORS if o.scores[g] < 50)
            return (served - OVERRUN_W * over, v[f])
        v = max(ok, key=key)
        levels = {m.name: (1.0 if f == ranked_wants(m)[0] else 0.85, f, 'venue')}; levels.update({o.name: serve_level(v, o) for o in others})
        return Stop(v, levels, dedicated=m.name)
    return None

OVERRUN_W = 0.01
def over_points(v, m, members, friends):
    return sum(max(0.0, v[g] - ceiling(m, g, members, friends)) for g in FACTORS if m.scores[g] < 50 and v[g] >= AVERSION_FLOOR)
def passes(v, members, friends, levels):
    """Rule 9: served -> aversions cost, not gate. Unserved -> must be in bend. Hard refusal -> wall for all."""
    if any(violated(v, m, g) for m in members for g in m.refused): return False
    return all(levels[m.name][0] > 0 or over_points(v, m, members, friends) == 0 for m in members)
COVER_K = 0.4
def firm_wants(m): return [g for g in ranked_wants(m) if m.firm(g) >= FIRM]
def pick_best(pool, members, debt, friends, ignore_zero=(), first=False, uncovered=None):
    best = None
    for v in pool:
        levels = {m.name: serve_level(v, m) for m in members}
        if not passes(v, members, friends, levels): continue
        nobody = sum(1 for m in members if m not in ignore_zero and ranked_wants(m) and levels[m.name][0] == 0)
        served = sum(l[0] * (1 + DEBT_K * debt[n]) for n, l in levels.items())
        cost = OVERRUN_W * sum(over_points(v, m, members, friends) for m in members)
        cover = COVER_K * sum(1 for m in members for g in (uncovered or {}).get(m.name, []) if v[g] >= DELIVERS) if uncovered else 0.0
        key = (-nobody, round(served + cover, 2), -v['ENRG'] if first else 0, -cost)   # served dominates; calmer first at stop 1; then least stepping-on
        if best is None or key > best[0]: best = (key, Stop(v, levels))
    return best[1] if best else None

def fmt(m, lvl, f, how, paid):
    return f'{f} {"#"+str(ranked_wants(m).index(f)+1) if f in ranked_wants(m) else ("sub" if f else "-")} {lvl:.2f}{" (area)" if how=="area" else ""}{" PAID" if paid else ""}'

# ================= debt mode (§13.4c) =================
MAX_STOPS = 3
def plan_debt(members, venues, n_stops, trace, friends=frozenset()):
    wanting = [m for m in members if ranked_wants(m)]
    # ---- pre-pass: how well can each person EVER be served with everyone in bend? (§13.4c rule 8)
    reach = {m.name: max([serve_level(v, m)[0] for v in venues if passes(v, members, friends, {x.name: serve_level(v, x) for x in members})] or [0.0]) for m in wanting}
    reserved = sorted([m for m in wanting if reach[m.name] < SERVED_FLOOR], key=lambda m: -debt_scale(m))
    required = len(reserved) + (1 if any(m not in reserved for m in wanting) else 0)
    if required > n_stops:
        if required <= MAX_STOPS: trace.append(f'           (night extended to {required} stops: {len(reserved)} one-each stop(s) reserved)'); n_stops = required
        else: trace.append(f'  {", ".join(m.name for m in reserved)} can never be served with the others in bend and there are not enough stops -> not a fit'); return
    held = {}
    for m in reserved:                                     # build the reserved stops now and hold their venues
        ded = dedicated_stop(m, [v for v in venues if v not in held.values()], members)
        if ded is None:
            trace.append(f'  {m.name} can only be served at a stop of their own, and a hard refusal blocks every such venue -> not a fit (said before anyone joins)'); return
        held[m.name] = ded.venue
    if reserved: trace.append('           reserved one-each stops for: ' + ', '.join(f'{m.name} (reach {reach[m.name]:.2f})' for m in reserved))
    debt = {m.name: 0.0 for m in members}; got = {m.name: 0.0 for m in members}; best_got = {m.name: 0.0 for m in members}; paid_tonight = set()
    covered = {m.name: set() for m in members}
    chosen = []; prev = -1; had = set(reserved)
    ordinary = n_stops - len(reserved)
    for k in range(n_stops):
        remaining = [v for v in venues if v not in chosen and (k >= ordinary or v not in held.values())]
        pool = [v for v in remaining if v['ENRG'] >= prev - 10] or remaining
        note = ''; best = None; target = {}; owed = []
        if k >= ordinary:                                              # the reserved slots, arc-ordered
            m = reserved[k - ordinary]
            best = dedicated_stop(m, remaining, members)
            if best is None: trace.append(f'  stop {k+1}: a hard refusal blocks the stop for {m.name} -> relax / not a fit'); return
            note = 'DEDICATED to ' + m.name + ' (others softened)'
        else:
            owed = [m for m in wanting if debt[m.name] >= DEBT_TRIGGER and m not in had and m.name not in paid_tonight]
            pool2 = pool
            if owed:
                target = {o.name: payback_target(o, remaining, members, friends) for o in owed}
                pays = lambda v: all(serve_level(v, o)[1:] == (target[o.name], 'venue') for o in owed if target[o.name]) and passes(v, members, friends, {x.name: serve_level(v, x) for x in members})
                pay = [v for v in pool if pays(v)] or [v for v in remaining if pays(v)]
                if pay: pool2 = pay; note = 'payback: ' + ', '.join(f'{o.name} on {target[o.name]} (#{ranked_wants(o).index(target[o.name])+1})' if target[o.name] else f'{o.name}: nothing reachable' for o in owed)
                else: note = 'no venue pays ' + ', '.join(o.name for o in owed) + ' - debt stays'
            ign = set(had)
            unc = {m.name: [g for g in firm_wants(m) if g not in covered[m.name]] for m in wanting}
            best = pick_best(pool2, members, debt, friends, ignore_zero=ign, first=(k == 0), uncovered=unc)
            if (best is None or any(ranked_wants(m) and m not in ign and best.levels[m.name][0] == 0 for m in members)) and pool2 is pool and pool is not remaining:
                alt = pick_best(remaining, members, debt, friends, ignore_zero=ign)
                if alt and not any(ranked_wants(m) and m not in ign and alt.levels[m.name][0] == 0 for m in members):
                    best = alt; note = (note + '; ' if note else '') + 'arc dropped so nobody gets nothing'
            if best is None: trace.append(f'  stop {k+1}: no venue within bend -> relax'); return
            # served once for real -> zeros accepted from here
            for m in wanting:
                if m not in had and best_got[m.name] >= SERVED_FLOOR and not any(serve_level(v, m)[0] > 0 and passes(v, members, friends, {x.name: serve_level(v, x) for x in members}) for v in remaining if v is not best.venue):
                    had.add(m)
        chosen.append(best.venue); prev = best.venue['ENRG']
        line = f'  stop {k+1}: {best.venue.name:<24}'
        for m in members:
            lvl, fct, how = best.levels[m.name]
            paid = (m in owed and fct == target.get(m.name) and how == 'venue') or best.dedicated == m.name
            if ranked_wants(m) and m not in reserved: debt[m.name] = 0.0 if paid else debt[m.name] + (1.0 - lvl) * debt_scale(m)
            got[m.name] += lvl; best_got[m.name] = max(best_got[m.name], lvl)
            for g in ranked_wants(m):
                if best.venue[g] >= DELIVERS: covered[m.name].add(g)
            if paid or (lvl == 1.0 and how == 'venue'): paid_tonight.add(m.name)
            line += f' | {m.name}: {fmt(m, lvl, fct, how, paid):<24}'
        line += ' | debt ' + ' '.join(f'{n[0]}={x:.2f}' for n, x in debt.items())
        if note: line += chr(10) + '           -> ' + note
        trace.append(line)
    miss = {m.name: [g for g in firm_wants(m) if g not in covered[m.name]] for m in wanting}
    miss = {k: v for k, v in miss.items() if v}
    trace.append('           firm wants never reached tonight: ' + (', '.join(f'{k}: {v}' for k, v in miss.items()) if miss else 'none'))

# ================= friend mode (§13.9) =================
MAX_RANK = 4
SUBSTITUTES = {'LIVE': ['ENRG', 'CROWD'], 'FOOD': ['SCEN', 'AFFIL'], 'POL': ['SCEN'], 'PLAY': ['ENRG', 'AFFIL'],
               'HERIT': ['SCEN', 'FOOD'], 'NOV': ['SCEN'], 'SCEN': ['POL'], 'CROWD': ['ENRG'], 'ENRG': ['CROWD'], 'AFFIL': ['FOOD']}

def friend_stop(members, remaining, lead, friends, wants):
    lists = [[(m, f) for f in wants[m.name]] for m in members if wants[m.name]]
    if not lists: return None, None
    combos = sorted(product(*lists), key=lambda c: (0 if any(m is lead and f == wants[lead.name][0] for m, f in c) else 1,
                                                    sum(wants[m.name].index(f) for m, f in c)))
    for combo in combos:
        ok = [v for v in remaining if all(delivers_at(v[f], m, f) for m, f in combo) and in_bend(v, members, friends)
              and not any(violated(v, o, g) for o in members for g in o.refused)]
        if ok: return max(ok, key=lambda v: sum(v[f] for _, f in combo)), combo
    return None, None

def plan_friends(members, venues, n_stops, trace, friends):
    got = {m.name: 0.0 for m in members}; chosen = []; prev = -1
    wanting = [m for m in members if ranked_wants(m)]
    lead = max(wanting, key=lambda m: m.scores[ranked_wants(m)[0]])
    for k in range(n_stops):
        remaining = [v for v in venues if v not in chosen]
        pool = [v for v in remaining if v['ENRG'] >= prev - 10] or remaining
        wants = {m.name: ranked_wants(m)[:MAX_RANK] for m in members}
        note = f'lead {lead.name}'
        v, combo = friend_stop(wanting, pool, lead, friends, wants)
        if v is None and pool is not remaining:
            v, combo = friend_stop(wanting, remaining, lead, friends, wants)          # the pairing outranks the arc
            if v: note += '; arc dropped'
        if v is None and all(len(wants[m.name]) == 1 for m in wanting):
            v = None                                                                   # single wants: dedicated stops, not substitutes
        elif v is None:
            # 1. drop whoever pairs with nothing
            for m in wanting:
                w2 = dict(wants); w2[m.name] = []
                v, combo = friend_stop([x for x in wanting if x is not m], pool, lead if lead is not m else [x for x in wanting if x is not m][0], friends, w2)
                if v: note += f'; {m.name} pairs with nothing here'; break
        if v is None and not all(len(wants[m.name]) == 1 for m in wanting):
            # 2. substitutes from the vibe profile (only for people with more than one want to draw on)
            w2 = {m.name: wants[m.name] + [s for f in wants[m.name] for s in SUBSTITUTES.get(f, []) if s not in wants[m.name]] for m in members}
            v, combo = friend_stop(wanting, pool, lead, friends, w2)
            if v: note += '; substitutes used'
        if v is None:
            # 3. dedicated stops, one each, in lead order
            ded = dedicated_stop(lead, remaining, members)
            if ded is None: trace.append(f'  stop {k+1}: nothing pairs and no dedicated stop -> not a fit'); return
            chosen.append(ded.venue); prev = ded.venue['ENRG']
            line = f'  stop {k+1}: {ded.venue.name:<24}'
            for m in members:
                lvl, f, how = ded.levels[m.name]; got[m.name] += lvl
                line += f' | {m.name}: {fmt(m, lvl, f, how, False):<24}'
            trace.append(line + chr(10) + '           -> DEDICATED to ' + lead.name + ' (nothing pairs)')
            lead = min(wanting, key=lambda m: got[m.name]); continue
        chosen.append(v); prev = v['ENRG']
        line = f'  stop {k+1}: {v.name:<24}'
        served_by = {m.name: f for m, f in combo}
        for m in members:
            lvl, f, how = serve_level(v, m)
            if m.name in served_by: f = served_by[m.name]; lvl = 1.0 if f in ranked_wants(m) and ranked_wants(m).index(f) == 0 else (0.85 if f in ranked_wants(m) else 0.6); how = 'venue'
            got[m.name] += lvl
            stretched = [g for g in FACTORS if m.scores[g] < 50 and v[g] > m.scores[g] + m.bend_pts(g)]
            line += f' | {m.name}: {fmt(m, lvl, f, how, False):<24}' + (f' stretched on {",".join(stretched)}' if stretched else '')
        trace.append(line + chr(10) + '           -> ' + note)
        lead = min(wanting, key=lambda m: got[m.name])

# ================= venues: debtsim's pool + a live-band bar
venues = d.venues + [V('Piano Man (Safdarjung)', {'CROWD': 55, 'ENRG': 45, 'POL': 45, 'SCEN': 55}, CROWD=70, ENRG=55, POL=65, SCEN=65, FOOD=65, LIVE=90, AFFIL=60),
                     V('Depot 48 (GK-2)', {'CROWD': 70, 'ENRG': 60, 'POL': 65, 'SCEN': 55}, CROWD=70, ENRG=65, POL=60, SCEN=60, FOOD=78, LIVE=60, AFFIL=65),
                     V('jazz bar (Lodhi)', {'CROWD': 40, 'ENRG': 25, 'POL': 75, 'SCEN': 85}, CROWD=50, ENRG=45, POL=65, SCEN=60, FOOD=55, LIVE=85, AFFIL=60),
                     V('haveli restaurant (Old Delhi)', {'CROWD': 85, 'ENRG': 50, 'POL': 15, 'SCEN': 80}, CROWD=60, ENRG=35, POL=40, SCEN=80, FOOD=85, HERIT=90, AFFIL=70),
                     V('bar with live band (GK)', {'CROWD': 70, 'ENRG': 60, 'POL': 65, 'SCEN': 55}, CROWD=70, ENRG=72, POL=45, SCEN=45, FOOD=40, LIVE=65, AFFIL=65)]

def show(title, members, n, mode, friends=frozenset()):
    print('\n' + title)
    for m in members: print(f'   {m.name:<6} wants {ranked_wants(m)}  overall_firm={overall_firmness(m):.1f}')
    tr = []
    (plan_friends if mode == 'friends' else plan_debt)(members, venues, n, tr, friends)
    print('\n'.join(tr))

if __name__ == '__main__':
    print('===== DEBT MODE, rules 5-7 + overall firmness =====')
    show('F. dedicated stop, others softened', [M('Aarav', ENRG=85, CROWD=80, LIVE=15), M('Divit', ENRG=85, CROWD=80, LIVE=15), M('Ruchi', LIVE=92, HERIT=62)], 3, 'debt')
    show('J. payback target is #2 because #1 (LIVE) is blocked by bends', [M('Aarav', ENRG=88, CROWD=80, LIVE=15), M('Divit', ENRG=88, CROWD=80, LIVE=15), M('Ruchi', LIVE=92, FOOD=75, SCEN=64)], 3, 'debt')
    show('K. opinionated vs easy - same concession, different debt', [M('Aarav', ENRG=90, CROWD=88, POL=85, FOOD=12, LIVE=10), M('Neha', FOOD=90, SCEN=62)], 2, 'debt')
    print('\n===== FRIEND MODE =====')
    AB = frozenset({('A', 'B'), ('B', 'A')})
    show('L. friends: A hates LIVE (0), loves ENRG; B wants LIVE 88, POL 85', [M('A', LIVE=0, ENRG=90, CROWD=75), M('B', LIVE=88, POL=85)], 2, 'friends', AB)
    show('M. friends: A wants LIVE, B wants POL - no POL+LIVE venue', [M('A', LIVE=90, CROWD=70), M('B', POL=90, SCEN=80, FOOD=62)], 2, 'friends', AB)
    show('N. friends, single wants that no venue joins (PLAY vs HERIT) -> substitutes / dedicated', [M('A', PLAY=90), M('B', HERIT=90)], 2, 'friends', AB)
    show('O. same pair as L, NOT friends -> debt mode for comparison', [M('A', LIVE=0, ENRG=90, CROWD=75), M('B', LIVE=88, POL=85)], 2, 'debt')
