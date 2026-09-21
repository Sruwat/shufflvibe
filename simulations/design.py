# -*- coding: utf-8 -*-
"""§14.3 v4 - the night is DESIGNED around every member's top vibe factor, present at every stop.
A top factor moves only if it is firmly opposed by someone and its owner has a strong #2 to substitute.
No dedicated stops, no debt. Each stop: the type that keeps the least-happy member happiest (maximin),
then the most total, then the other factors as signals. Chemistry from how the design went."""
import splitsim as S
from splitsim import M, TYPES, STOP_AXES, PREFS, VENUES, fill, WANT_FLOOR, FIRM, V
TYPES['games pub'] = dict(ENRG=60, AFFIL=70, CROWD=60, TALK=60, MOVE=20, GAMES=65)      # board games and a table you can talk at
VENUES.append(V('Bohca-style games cafe (Saket)', 'games pub', LIVE=10, FOOD=60, POL=45, SCEN=55, HERIT=20))
VENUES.append(V('brewery with board games (Cyber Hub)', 'games pub', LIVE=30, FOOD=68, POL=50, SCEN=50, HERIT=20))

SUB_MIN = 18          # a #2 can substitute a top factor if it is at least this far from the middle (score >= 68 / <= 32)
DEGREE  = 0.5         # "happy to at least a certain degree": on their side of the middle, at every stop

def ranked(m): return [f for f in sorted(STOP_AXES, key=lambda f: -abs(m.vibe[f] - 50)) if abs(m.vibe[f] - 50) >= WANT_FLOOR]
def opposed_by(m, f, members):
    return [o.name for o in members if o is not m and o.firm(f) >= FIRM and o.pole(f) != m.pole(f)]
def effective_top(m, members):
    """(factor, substituted?, opposed_by). The top factor stands unless somebody is firm on the other pole
    AND m has a strong #2 (score >= 68 / <= 32) to stand in. If not, the top stands anyway - it is their reason to go out."""
    w = ranked(m)
    if not w: return None, False, []
    opp = opposed_by(m, w[0], members)
    seconds = [f for f in sorted(STOP_AXES, key=lambda f: -abs(m.vibe[f] - 50)) if f != w[0] and abs(m.vibe[f] - 50) >= SUB_MIN]
    if opp and seconds:
        return seconds[0], True, opp
    return w[0], False, opp
def satisfaction(t, m, f):
    """1.0 inside m's bend on f; DEGREE if the type is at least on m's side of the middle; else 0."""
    if f is None: return 1.0
    if S.delivers(t, m, f): return 1.0
    if abs(t[f] - 50) <= 5 or (t[f] >= 50) == (m.pole(f) == 'high'): return DEGREE      # the middle counts for both sides
    return 0.0
def signals(t, members):
    """Everything else, as a tie-break: firmness-weighted distance on all axes."""
    return sum(abs(t[f] - m.vibe[f]) * m.firm(f) for m in members for f in STOP_AXES)

def roam_count(members, hours, trace):
    firm = [m for m in members if m.firm('ROAM') >= FIRM]
    if not firm: return S.n_stops(50, hours), ''
    poles = {m.pole('ROAM') for m in firm}
    val = sum(m.vibe['ROAM'] * m.firm('ROAM') for m in firm) / sum(m.firm('ROAM') for m in firm)
    note = '' if len(poles) == 1 else f'ROAM is one number for everyone: {", ".join(f"{m.name} {m.vibe["ROAM"]}" for m in firm)} -> {val:.0f}'
    return S.n_stops(val, hours), note

def design(members, trace, hours=6):
    tops = {m.name: effective_top(m, members) for m in members}
    for m in members:
        f, sub, opp = tops[m.name]
        if f: trace.append(f'   {m.name}: top {f} {m.pole(f)}' + (f' - stands in for {ranked(m)[0]}, which {", ".join(opp)} firmly opposes' if sub else (f' (opposed by {", ".join(opp)}; no strong #2, so it stands)' if opp else '')))
        else: trace.append(f'   {m.name}: no top vibe factor tonight - easy')
    n, note = roam_count(members, hours, trace)
    if note: trace.append('   ' + note)
    bringing = [m for m in members if tops[m.name][0]]
    had = {m.name: set() for m in members}
    def coverage(nm):
        return sum(1 for m in members for f in PREFS if m.pref[f] >= S.PREF_WHOLE and f not in had[m.name] and any(v.type == nm and S.venue_has(v, f, m) for v in VENUES))
    stops, used, prev = [], [], -1
    for k in range(n):
        best = None
        for nm, t in TYPES.items():
            if nm == 'open ground' and k > 0: continue
            sat = {m.name: satisfaction(t, m, tops[m.name][0]) for m in bringing}
            key = (min(sat.values()) if sat else 1.0, round(sum(sat.values()), 2), nm not in used,
                   -t['ENRG'] if k == 0 else (t['ENRG'] >= prev - 10), coverage(nm), -signals(t, members))
            if best is None or key > best[0]: best = (key, nm, sat)
        _, nm, sat = best; used.append(nm); prev = TYPES[nm]['ENRG']
        for m in members:
            for f in PREFS:
                if m.pref[f] >= S.PREF_WHOLE and any(v.type == nm and S.venue_has(v, f, m) for v in VENUES): had[m.name].add(f)
        stops.append((nm, {m.name: (sat.get(m.name, 1.0), tops[m.name][0], 'top') for m in members}, ''))
    stops.sort(key=lambda s: TYPES[s[0]]['ENRG'])
    mins = [min(s[1][m.name][0] for m in bringing) for s in stops] if bringing else [1.0]
    subs = [m for m in members if tops[m.name][1]]
    roam_collided = bool(note)
    if not bringing: chem = 'DRIFT'
    elif len(bringing) == 1 and len(members) > 1: chem = 'ANCHORED'
    elif min(mins) == 0: chem = 'TUG'                       # somebody's reason to go out is absent at a stop
    elif subs or roam_collided: chem = 'COMPROMISE'          # somebody gave way - a #2 stood in, or ROAM was split
    elif min(mins) < 1.0: chem = 'TRADE'                     # everyone met in the middle somewhere
    else: chem = 'LOCKSTEP'
    if chem == 'LOCKSTEP' and all(m.vibe['ENRG'] >= 55 for m in members) and not any(tops[m.name][0] == 'ENRG' for m in members): chem = 'SPARK'
    return stops, chem

WORD = {'LOCKSTEP': 'In Sync', 'TRADE': 'Best of Both', 'COMPROMISE': 'Got Your Back', 'TUG': 'Something for Everyone', 'ANCHORED': 'Along for the Ride', 'DRIFT': 'Open Night', 'SPARK': 'Could Go Late'}

def plan(members, hours=6):
    trace = []
    stops, chem = design(members, trace, hours)
    trace.append(f'   -> {WORD[chem]}')
    filled, missing = fill(stops, members, trace)
    for k, (tname, v, levels, note, sp) in enumerate(filled):
        line = f'  stop {k+1}: [{tname}] {v.name if v else "-"}'
        for m in members:
            lvl, f, how = levels[m.name]
            line += f' | {m.name}: {(f"{f} {lvl:.1f}") if f else "easy":<12} prefs {",".join(sp.get(m.name, [])) or "-"}'
        trace.append(line)
    trace.append('   whole-point preferences never had: ' + (', '.join(f'{k}: {v}' for k, v in missing.items()) if missing else 'none'))
    return trace

def show(title, members, hours=6):
    print('\n' + title); print('\n'.join(plan(members, hours)))

if __name__ == '__main__':
    show('Arjun ENRG · Bea ROAM · Chetan GAMES',
         [M('Arjun', ENRG=90, CROWD=80, AFFIL=55, TALK=30, ROAM=55, MOVE=65, GAMES=40, FOOD=62, POL=62, NOV=62, HERIT=12, sense='current'),
          M('Bea', ROAM=88, TALK=80, ENRG=55, AFFIL=62, CROWD=48, MOVE=55, GAMES=30, SCEN=88, FOOD=62, NOV=88, HERIT=62),
          M('Chetan', GAMES=92, AFFIL=88, ENRG=45, CROWD=55, TALK=50, ROAM=40, MOVE=35, FOOD=88, LIVE=12)])
    show('U. Piano Man room: Aarav ENRG 88 · Bela ENRG 12 firm, TALK 80 · Chirag FOOD', [M('Aarav', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Chirag', FOOD=88, ROAM=62)])
    show('U2. same, but Aarav has a strong #2 (CROWD 78)', [M('Aarav', ENRG=88, CROWD=78), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Chirag', FOOD=88, ROAM=62)])
    show('H. two ENRG camps, no strong seconds', [M('Aarav', ENRG=90, CROWD=60, ROAM=60), M('Neha', ENRG=15, TALK=60, FOOD=92)])
    show('ROAM case', [M('A', ROAM=92, CROWD=80), M('B', AFFIL=90, ROAM=12, GAMES=72)])
    show('T. the whole team out', [M('A', AFFIL=88, ENRG=85, GAMES=80, ROAM=75), M('B', AFFIL=85, ENRG=80, GAMES=88), M('C', AFFIL=90, ENRG=88, GAMES=70, FOOD=88)])
    show('E. quaint pub', [M('Priya', AFFIL=92, ENRG=20, CROWD=25), M('Sana', SCEN=90, POL=80, sense='classy'), M('Ria', SCEN=85, POL=75)])
    show('F. the gig person', [M('Aarav', ENRG=85, CROWD=80, LIVE=12), M('Divit', ENRG=85, CROWD=80, LIVE=12), M('Ruchi', LIVE=92, HERIT=62, ROAM=70)])
    show('X. GAMES · MOVE · TALK, all ROAM low', [M('A', GAMES=90, ROAM=20), M('B', MOVE=90, ROAM=25), M('C', TALK=90, ROAM=15)])
    show('Y. AFFIL high firm v AFFIL low firm (the room v the table), both with strong seconds', [M('A', AFFIL=90, CROWD=80), M('B', AFFIL=12, ENRG=80)])
