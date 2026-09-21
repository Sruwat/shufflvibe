# -*- coding: utf-8 -*-
"""Scenario 1: Priya browses public rooms (gate §13.4a/13.4d + match §13.6.3).
   Scenario 2: Priya hosts with three co-hosts (room vector + payback §13.6.1, chemistry §13.6.2, plan §13.4c)."""
import friendsim as fs
from friendsim import M, V, FACTORS, ranked_wants, serve_level, violated, over_points, delivers_at, DELIVERS, ceiling


FIRM, ABSTAIN, DEFINING, RECIP, DEBT_ALLOW, PAYBACK_MIN, UNDEF = 0.5, 0.15, 25, 2.0, 10, 10, 0.05
SHIFT_GREAT, SHIFT_POOR, REINF_GREAT = 0.10, 0.20, 0.5

# ---------------- §13.6.1 room vector + payback
def room_vector(members, boost={}):
    v = {}
    for f in FACTORS:
        w = {m.name: m.firm(f) * boost.get((m.name, f), 1.0) for m in members}
        v[f] = None if sum(w.values()) < UNDEF else sum(w[m.name] * m.scores[f] for m in members) / sum(w.values())
    return v
def served_on_vector(m, f, value):
    return value is not None and value >= m.scores[f] - m.bend_pts(f)
def payback(members):
    v0 = room_vector(members)
    debt = [m for m in members if ranked_wants(m) and not served_on_vector(m, ranked_wants(m)[0], v0[ranked_wants(m)[0]])]
    boost = {(m.name, ranked_wants(m)[0]): 1 + RECIP * fs.debt_scale(m) for m in debt}
    v1 = room_vector(members, boost)
    paid, unpaid = [], []
    for m in debt:
        f = ranked_wants(m)[0]; lo, hi = 0, 100
        for o in members:
            if o is m or o.firm(f) < FIRM: continue
            allow = 0 if f in o.refused else DEBT_ALLOW          # a hard pass caps with no allowance (hole fixed 09-17)
            lo = max(lo, o.scores[f] - o.bend_pts(f) - allow); hi = min(hi, o.scores[f] + o.bend_pts(f) + allow)
        v1[f] = min(max(v1[f], lo), hi)
        v1[f] = max(v1[f], v0[f]) if m.scores[f] > 50 else min(v1[f], v0[f])   # the cap never moves the room AWAY from the owed member
        (paid if abs(v1[f] - (v0[f] or 50)) >= PAYBACK_MIN else unpaid).append((m.name, f))
    return v0, v1, paid, unpaid
def opposed(members, f):
    firm = [m for m in members if m.firm(f) >= FIRM]
    return any(a.scores[f] > 50 for a in firm) and any(b.scores[f] < 50 for b in firm)
def chemistry(members, v, paid, unpaid):
    firm_any = [m for m in members if any(m.firm(f) >= FIRM for f in FACTORS)]
    if not firm_any: return 'DRIFT'
    defining = [f for f in FACTORS if v[f] is not None and abs(v[f] - 50) >= DEFINING]
    if any(opposed(members, f) for _, f in unpaid): return 'TUG'
    if len({f for _, f in paid}) >= 2: return 'TRADE'
    if paid: return 'COMPROMISE'
    if len(firm_any) == 1 and len(members) >= 2: return 'ANCHORED'
    if all(m.scores['ENRG'] >= 55 for m in members) and not any(m.firm('ENRG') >= FIRM and m.scores['ENRG'] < 50 for m in members) and 'ENRG' not in defining: return 'SPARK'
    return 'LOCKSTEP'
WORD = {'LOCKSTEP': 'In Sync', 'COMPROMISE': 'Got Your Back', 'TRADE': 'Best of Both', 'ANCHORED': 'Along for the Ride', 'TUG': 'Something for Everyone', 'DRIFT': 'Open Night', 'SPARK': 'Could Go Late'}
def l1(a, b): return sum(abs((a[f] or 50) - (b[f] or 50)) for f in FACTORS)

# ---------------- §13.6.3 match
def match(joiner, room_members, room_state, room_vec):
    if room_state == 'DRIFT':
        n_firm = sum(1 for f in FACTORS if joiner.firm(f) >= FIRM)
        return ('great' if n_firm >= 5 else 'alright'), f'open night; joiner firm on {n_firm} factors'
    v0, v1, paid, unpaid = payback(room_members + [joiner])
    after = chemistry(room_members + [joiner], v1, paid, unpaid)
    defined = [f for f in FACTORS if room_vec[f] is not None]
    shift = sum(abs(room_vec[f] - (v1[f] if v1[f] is not None else room_vec[f])) for f in defined) / (50.0 * max(1, len(defined)))
    defining = [f for f in FACTORS if room_vec[f] is not None and abs(room_vec[f] - 50) >= DEFINING]
    reinf = sum(joiner.firm(f) * (1 if (joiner.scores[f] - 50) * (room_vec[f] - 50) > 0 else -1) for f in defining) / len(defining) if defining else 0.0
    worse = after == 'TUG' and room_state != 'TUG'
    why = f'shift {shift:.3f}, reinforcement {reinf:.2f}, state after {WORD[after]}'
    if worse or shift > SHIFT_POOR: return 'poor', why
    if shift <= SHIFT_GREAT and reinf >= REINF_GREAT: return 'great', why
    return 'alright', why

# ---------------- joiner gate §13.4a / §13.4d
def gate(user, plan):
    if not plan: return True, 'open night - no plan, no gate'
    for v in plan:
        if any(violated(v, user, f) for f in user.refused): return False, f'{v.name}: a hard pass is violated'
        if over_points(v, user, [user], frozenset()) > 0: return False, f'{v.name}: steps on an aversion of hers'
        lvl, f, how = serve_level(v, user)
        if lvl == 0 or how == 'area': return False, f'{v.name}: nothing for her by the venue'
    return True, 'every stop inside her bend and serving her'

VN = {v.name: v for v in fs.venues}
def stops_line(user, plan):
    return '  ·  '.join(f'{v.name.split(" (")[0]}: ' + (lambda l: f'{l[1]} {l[0]:.2f}{" (partial)" if l[2]=="partial" else ""}' if l[0] else '—')(serve_level(v, user)) for v in plan)

if __name__ == '__main__':
    priya = M('Priya', refused=['LIVE'], FOOD=88, SCEN=72, POL=65, AFFIL=70, NOV=55, PLAY=45, CROWD=40, ENRG=30, LIVE=12, HERIT=50)
    print('PRIYA  wants', ranked_wants(priya), '| refused', sorted(priya.refused), '| overall firmness (sim proxy)', f'{fs.overall_firmness(priya):.1f}')
    print('       bends: ENRG ceiling', f'{priya.scores["ENRG"] + priya.bend_pts("ENRG"):.0f}', '| CROWD ceiling', f'{priya.scores["CROWD"] + priya.bend_pts("CROWD"):.0f}', '| FOOD floor', f'{priya.scores["FOOD"] - priya.bend_pts("FOOD"):.0f}')
    rooms = {
     'Friday Fix':  ([M('Aarav', ENRG=88, CROWD=80), M('Divit', ENRG=85, CROWD=78, POL=70)], [VN['lively bar (CP)'], VN['club (Aerocity)']]),
     'Slow One':    ([M('Sana', SCEN=90, POL=80), M('Ria', SCEN=85, FOOD=75), M('Kabir', FOOD=88, SCEN=70)], [VN['quiet restaurant (HKV)'], VN['rooftop lounge (Aerocity)']]),
     'Open Night':  ([M('Meher', ENRG=55, FOOD=58), M('Anchal', SCEN=57)], []),
     'Set List':    ([M('Tara', LIVE=92, HERIT=62), M('Rohan', LIVE=85, ENRG=70)], [VN['Piano Man (Safdarjung)'], VN['gig venue (dead lane)']]),
     'Game On':     ([M('Kabir2', PLAY=90, NOV=61), M('Neha', PLAY=80, FOOD=70), M('Ishita', ENRG=85)], [VN['arcade bar (CP)'], VN['busy diner (CP)']]),
    }
    print('\n=== SCENARIO 1: the room list, as Priya sees it ===')
    for name, (mem, plan) in rooms.items():
        v0, v1, paid, unpaid = payback(mem); st = chemistry(mem, v1, paid, unpaid)
        ok, why = gate(priya, plan)
        if not ok: print(f'{name:<12} [{WORD[st]}]  HIDDEN - {why}'); continue
        band, mwhy = match(priya, mem, st, v1)
        print(f'{name:<12} [{WORD[st]}]  gate ok ({why})  ->  {band.upper()}  ({mwhy})')
        if plan: print('              plan for her: ' + stops_line(priya, plan))

    print('\n=== SCENARIO 2: Priya hosts with Sana (friend), Kabir, Rohan ===')
    sana = M('Sana', SCEN=90, POL=80, ENRG=35); kabir = M('Kabir', FOOD=88, SCEN=70, CROWD=30); rohan = M('Rohan', LIVE=85, ENRG=70, CROWD=65)
    room = [priya, sana, kabir, rohan]
    friends = frozenset({('Priya', 'Sana'), ('Sana', 'Priya')})
    for m in room: print(f'   {m.name:<6} wants {ranked_wants(m)}  firm wants {fs.firm_wants(m)}  refused {sorted(m.refused)}  overall_firm {fs.overall_firmness(m):.1f}')
    v0, v1, paid, unpaid = payback(room); st = chemistry(room, v1, paid, unpaid)
    print('   room vector (abstention):', {f: round(v0[f]) for f in FACTORS if v0[f] is not None})
    print('   after payback:           ', {f: round(v1[f]) for f in FACTORS if v1[f] is not None}, '| paid', paid, '| unpaid', unpaid)
    print('   chemistry:', st, '->', WORD[st])
    tr = []; fs.plan_debt(room, fs.venues, 3, tr, friends); print('\n'.join(tr))
