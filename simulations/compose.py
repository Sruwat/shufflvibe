# -*- coding: utf-8 -*-
"""§14.3 v3 - compose first: do everyone's top vibe factors form a night shape on their own?
Only if they collide structurally does the compromise machinery (splitsim.shape_night) run.
Chemistry is read off HOW the shape was formed."""
from itertools import combinations
import splitsim as S
from splitsim import M, TYPES, STOP_AXES, PREFS, ranked_wants, second_is_strong, WANT_FLOOR, serve_level, fill, VENUES

HIGH_OK, LOW_OK = 60, 40           # structural: a type 'carries' a high pole at >= 60, a low pole at <= 40 - no personal bend here
DEMAND_RANKS = 2                    # #1 always; #2 if strong

def demands(m):
    """The (factor, pole) pairs this member brings to the table: their top vibe factor, and their #2 if strong."""
    w = ranked_wants(m)
    out = [(w[0], m.pole(w[0]))] if w else []
    if len(w) >= 2 and second_is_strong(m): out.append((w[1], m.pole(w[1])))
    return out
def roam_demand(m):
    return None if abs(m.vibe['ROAM'] - 50) < WANT_FLOOR else m.pole('ROAM')
def carries(t, dem):
    return all((t[f] >= HIGH_OK) if p == 'high' else (t[f] <= LOW_OK) for f, p in dem)
def types_for(dem):
    return [nm for nm, t in TYPES.items() if carries(t, dem)]

def partitions(items, k):
    """All ways to split items into at most k non-empty groups (small n, fine)."""
    items = list(items)
    if not items: yield []; return
    first, rest = items[0], items[1:]
    for p in partitions(rest, k):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i+1:]
        if len(p) < k: yield [[first]] + p

def compose(members, trace, hours=6):
    """Returns (stops, chemistry, notes) or None if no all-inclusive shape exists."""
    dem = {m.name: demands(m) for m in members}
    all_dem = sorted({d for ds in dem.values() for d in ds})
    roams = {m.name: roam_demand(m) for m in members if roam_demand(m)}
    if len(set(roams.values())) > 1:
        trace.append(f'   ROAM demands collide ({roams}) - no single night has one place and three'); return None
    roam = 88 if 'high' in roams.values() else 12 if 'low' in roams.values() else 50
    n0 = S.n_stops(roam, hours)
    if not all_dem:
        return [], 'DRIFT', ['nobody brought a top vibe factor']
    # can every demand be placed in <= n stops, each stop carried by some type? try n, then one more
    best, n, extended = None, n0, False
    for n in (n0, min(n0 + 1, S.MAX_STOPS)):
        for part in partitions(all_dem, n):
            if all(types_for(g) for g in part):
                key = (len(part), -min(len(types_for(g)) for g in part))
                if best is None or key < best[0]: best = (key, part)
        if best: extended = n > n0; break
    if best is None:
        trace.append(f'   no night of {n0} or {n0+1} stop(s) carries all of {all_dem} - collision'); return None
    part = best[1]
    had = {m.name: set() for m in members}
    def coverage(nm):
        return sum(1 for m in members for f in PREFS if m.pref[f] >= S.PREF_WHOLE and f not in had[m.name]
                   and any(v.type == nm and S.venue_has(v, f, m) for v in VENUES))
    def choose(cands, who, used):
        return min(cands, key=lambda nm: (nm in used, -coverage(nm),
                                          sum(abs(TYPES[nm][f] - m.vibe[f]) * max(m.firm(f), .05) for m in who for f in STOP_AXES)))
    stops, used = [], []
    for g in part:
        who = [m for m in members if any(d in g for d in dem[m.name])]
        tname = choose(types_for(g), who, used); used.append(tname)
        for m in members:
            for f in PREFS:
                if m.pref[f] >= S.PREF_WHOLE and any(v.type == tname and S.venue_has(v, f, m) for v in VENUES): had[m.name].add(f)
        stops.append((tname, {m.name: serve_level(TYPES[tname], m) for m in members}, ''))
    # top up to the stop count ROAM asked for: another type that carries the group everyone shares best, varied
    while len(stops) < n:
        cands = sorted({t for g in part for t in types_for(g)})            # any type that carries one of the groups
        tname = choose(cands, members, used); used.append(tname)
        stops.append((tname, {m.name: serve_level(TYPES[tname], m) for m in members}, ''))
    stops.sort(key=lambda s: TYPES[s[0]]['ENRG'])                       # the arc
    # chemistry from how it formed
    bringing = [m for m in members if dem[m.name]]
    if len(bringing) == 1 and len(members) > 1: chem = 'ANCHORED'
    elif extended: chem = 'COMPROMISE'
    elif len(part) == 1: chem = 'LOCKSTEP'
    else: chem = 'TRADE'
    if chem == 'LOCKSTEP' and all(m.vibe['ENRG'] >= 55 for m in members) and not any(('ENRG', 'high') in dem[m.name] for m in members): chem = 'SPARK'
    notes = [f'{len(all_dem)} top factor(s) from {len(bringing)} people, carried in {len(part)} stop group(s) of {n}' + (' - one more stop than ROAM asked for, so everyone is in' if extended else '')]
    return stops, chem, notes

WORD = {'LOCKSTEP': 'In Sync', 'TRADE': 'Best of Both', 'COMPROMISE': 'Got Your Back', 'TUG': 'Something for Everyone',
        'ANCHORED': 'Along for the Ride', 'DRIFT': 'Open Night', 'SPARK': 'Could Go Late'}

def plan(members, friends=frozenset(), hours=6):
    trace = []
    got = compose(members, trace, hours)
    if got is not None:
        stops, chem, notes = got; trace.append('   composed: ' + '; '.join(notes) + f' -> {WORD[chem]}')
    else:
        trace.append('   -> compromise machinery (bend, firmness, debt, payback)')
        stops, shape = S.shape_night(members, friends, trace, hours)
        ded = any('DEDICATED' in s[2] for s in stops)
        chem = 'TUG' if ded else 'COMPROMISE'
        trace.append(f'   formed by compromise -> {WORD[chem]}')
    filled, missing = fill(stops, members, trace)
    for k, (tname, v, levels, note, sp) in enumerate(filled):
        line = f'  stop {k+1}: [{tname}] {v.name if v else "-"}'
        for m in members:
            lvl, f, how = levels[m.name]
            line += f' | {m.name}: {(f + " " + m.pole(f) + f" {lvl:.2f}") if f else "- 0":<22} prefs {",".join(sp.get(m.name, [])) or "-"}'
        if note: line += '  <- ' + note
        trace.append(line)
    trace.append('   whole-point preferences never had: ' + (', '.join(f'{k}: {v}' for k, v in missing.items()) if missing else 'none'))
    return trace

def show(title, members, friends=frozenset(), hours=6):
    print('\n' + title)
    for m in members: print(f'   {m.name:<7} brings {demands(m)}{"  ROAM " + roam_demand(m) if roam_demand(m) else ""}  | prefs {[(f, m.pref[f]) for f in PREFS if m.pref[f] >= 60]}')
    print('\n'.join(plan(members, friends, hours)))

if __name__ == '__main__':
    F = lambda *names: frozenset({(a, b) for a in names for b in names if a != b})
    show('ROAM case: A ROAM high firm, CROWD high · B AFFIL high firm, ROAM low firm', [M('A', ROAM=92, CROWD=80), M('B', AFFIL=90, ROAM=12, GAMES=72)])
    show('T. the whole team out', [M('A', AFFIL=88, ENRG=85, GAMES=80, ROAM=75), M('B', AFFIL=85, ENRG=80, GAMES=88), M('C', AFFIL=90, ENRG=88, GAMES=70, FOOD=88)])
    show('H. two ENRG camps', [M('Aarav', ENRG=90, CROWD=85, ROAM=60), M('Neha', ENRG=15, TALK=85, FOOD=92)])
    show('H1. two ENRG camps, ROAM low (one place)', [M('Aarav', ENRG=90, CROWD=85, ROAM=15), M('Neha', ENRG=15, TALK=85, FOOD=92, ROAM=20)])
    show('U. Piano Man room', [M('Aarav', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Chirag', FOOD=88, ROAM=62)])
    show('E. quaint pub', [M('Priya', AFFIL=92, ENRG=20, CROWD=25), M('Sana', SCEN=90, POL=80, sense='classy'), M('Ria', SCEN=85, POL=75)])
    show('F. the gig person', [M('Aarav', ENRG=85, CROWD=80, LIVE=12), M('Divit', ENRG=85, CROWD=80, LIVE=12), M('Ruchi', LIVE=92, HERIT=62, ROAM=70)])
    show('I. one firm, two easy', [M('Aarav', ENRG=88, CROWD=80), M('Divit'), M('Neha', FOOD=58)])
    show('P2. Priya hosts three', [M('Priya', AFFIL=88, ENRG=80, FOOD=88, POL=65, sense='classy'), M('Sana', ENRG=35, TALK=80, SCEN=90, POL=80), M('Kabir', ROAM=20, TALK=78, FOOD=88), M('Rohan', ROAM=85, ENRG=75, LIVE=85)], F('Priya', 'Sana'))
    show('X. three-way: GAMES high · MOVE high · TALK high, ROAM low', [M('A', GAMES=90, ROAM=20), M('B', MOVE=90, ROAM=25), M('C', TALK=90, ROAM=15)])
