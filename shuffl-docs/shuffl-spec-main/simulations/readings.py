# -*- coding: utf-8 -*-
"""Room-first, properly: the night is planned from the READINGS - what the psychology says the seven axes do
when these people meet (Chemistry V2) - never from an average. Each reading is a demand on the stop types.
Individuals enter only as a floor (nobody's reason absent) and as sums beneath the readings.

2026-09-23: RAMP decides where the peak sits (it replaces the hard-coded climb), and PROFILE RULES
(profiles.py) may add a reading on an axis nobody spoke on."""
import design3 as D3, design as Dz, design2 as D2, splitsim as S, profiles as P, roomread as RR
from splitsim import M, TYPES, STOP_AXES, fill
WEIGHT = dict(ENRG=18, AFFIL=16, CROWD=14, TALK=14, ROAM=14, MOVE=12, GAMES=12, RAMP=10)

def readings(members, strangers=False):
    """The room read as a whole: a list of (axis, demand, weight). No averages."""
    v, tags, ctx = RR.room_read(members, strangers)                  # CHEMISTRY V3 levels (interplay.py), not a mean
    R = []
    # an axis with no position issues no reading: a room at ENRG 50 is not asking for a mid-energy venue
    if abs(v['ENRG'] - 50) >= 8 or any(D3.is_firm(m, 'ENRG') for m in members):
        R.append(('ENRG', ('end', v['ENRG']), WEIGHT['ENRG']))      # the arc ends where contagion says
    if ctx['affil_split']:
        lo_a, hi_a = (62, 75) if ctx['affil_lean'] == 'high' else (50, 65) if ctx['affil_lean'] == 'low' else (55, 75)
        R.append(('AFFIL', ('table-in-a-room', (lo_a, hi_a)), WEIGHT['AFFIL']))
    elif 'Our Table' in tags: R.append(('AFFIL', ('table', 70), WEIGHT['AFFIL']))
    elif 'Meet the Room' in tags: R.append(('AFFIL', ('outward-first', 60), WEIGHT['AFFIL']))
    if ctx['talkers']: R.append(('TALK', ('floor', D3.TALK_FLOOR), WEIGHT['TALK'] * 2))   # absolute
    else:
        t_lo = sum(D3.strength(m, 'TALK', 'low') for m in members); t_hi = sum(D3.strength(m, 'TALK', 'high') for m in members)
        if t_lo > t_hi and t_lo > 0: R.append(('TALK', ('loud', 40), WEIGHT['TALK']))
    c_hi = sum(D3.strength(m, 'CROWD', 'high') for m in members); c_lo = sum(D3.strength(m, 'CROWD', 'low') for m in members)
    if c_hi > c_lo and c_hi > 0: R.append(('CROWD', ('full', 60), WEIGHT['CROWD']))
    elif c_lo > c_hi and c_lo > 0: R.append(('CROWD', ('quiet', 45), WEIGHT['CROWD']))
    g_hi = sum(D3.strength(m, 'GAMES', 'high') for m in members)
    if g_hi >= len(members) / 2 and g_hi > 0: R.append(('GAMES', ('games', 60), WEIGHT['GAMES']))
    elif ctx['games_minority']: R.append(('GAMES', ('games-available', (55, 70)), WEIGHT['GAMES'] * 0.6))
    if strangers: R.append(('GAMES', ('ice-breaker-first', 60), WEIGHT['GAMES'] * 0.6))
    if ctx['movers_win']: R.append(('MOVE', ('floor-at-the-end', 60), WEIGHT['MOVE']))
    else:
        mv_lo = sum(D3.strength(m, 'MOVE', 'low') for m in members)
        if mv_lo > 0 and mv_lo >= sum(D3.strength(m, 'MOVE', 'high') for m in members): R.append(('MOVE', ('seated', 40), WEIGHT['MOVE'] * 0.6))
    return R, tags, ctx, v

# ---------------- profile rules: a reading on an axis nobody spoke on (profiles.py)
INFER_KIND = {('CROWD', 'high'): ('full', 60), ('CROWD', 'low'): ('quiet', 45),
              ('GAMES', 'low'): ('no-games', 40), ('GAMES', 'high'): ('games-available', (55, 70)),
              ('TALK', 'high'): ('talkable', 55),  ('TALK', 'low'): ('loud', 40),
              ('MOVE', 'high'): ('floor-at-the-end', 60), ('MOVE', 'low'): ('seated', 40)}

def profile_layer(members, R):
    """Returns (extra readings, {night-level axis: value}, [what fired]). Guards in profiles.py."""
    stated = {a for a, _, _ in R}
    extra, lines, log = [], {}, []
    for name, who, infers, why in P.fires(members):
        share = len(who) / float(len(members))
        for axis, pole in infers:
            if not P.silent(members, axis, stated): continue                  # guard 1: only where silent
            if axis in S.NIGHT_LEVEL:
                lines.setdefault(axis, []).append((P.LINE_TARGET[pole], share))
            else:
                kind = INFER_KIND.get((axis, pole))
                if not kind: continue
                extra.append((axis, kind, WEIGHT[axis] * P.INFERRED_W * share))  # guard 2: discounted
            log.append((name, who, axis, pole, why))                             # guard 3: logged
    # a night-level inference moves the number by the SHARE of the room whose profile fires it:
    # one member of four cannot make a room of four settle in one place.
    lines = {a: 50.0 + (sum(t * s for t, s in v) / sum(s for t, s in v) - 50.0) * min(1.0, sum(s for t, s in v))
             for a, v in lines.items()}
    return extra, lines, log

def met(t, r, k, n, ramp=50.0):
    axis, (kind, val), w = r
    if kind == 'end':
        if n == 1: lo = val
        else:
            climb = ramp / 100.0                       # how much of the way down from the level stop 1 starts
            start = val - (val - 45) * climb
            peak_at = n if ramp >= 60 or n <= 2 else n - 1     # peak-end: mid and low ramps peak early and hold
            lo = start + (val - start) * min(1.0, (k + 1) / float(peak_at))
        return 1 - min(1, abs(t['ENRG'] - lo) / 25)
    if kind == 'table-in-a-room': return 1.0 if val[0] <= t['AFFIL'] <= val[1] and t['CROWD'] >= 60 else 0.0
    if kind == 'table':    return 1.0 if t['AFFIL'] >= val else 0.0
    if kind == 'outward-first': return (1.0 if t['AFFIL'] <= val else 0.0) if k == 0 else 1.0
    if kind == 'floor':    return 1.0 if t['TALK'] >= val else -9.0
    if kind == 'talkable': return 1.0 if t['TALK'] >= val else 0.0     # inferred: a preference, never a wall
    if kind == 'loud':     return 1.0 if t['TALK'] <= val else 0.0
    if kind == 'full':     return 1.0 if t['CROWD'] >= val else 0.0
    if kind == 'quiet':    return 1.0 if t['CROWD'] <= val else 0.0
    if kind == 'games':    return 1.0 if t['GAMES'] >= val else 0.0
    if kind == 'no-games': return 1.0 if t['GAMES'] <= val else 0.0
    if kind == 'games-available': return 1.0 if val[0] <= t['GAMES'] <= val[1] else 0.0
    if kind == 'ice-breaker-first': return (1.0 if t['GAMES'] >= val else 0.0) if k == 0 else 1.0
    if kind == 'floor-at-the-end': return (1.0 if t['MOVE'] >= val else 0.0) if k == n - 1 else 1.0
    if kind == 'seated':   return 1.0 if t['MOVE'] <= val else 0.0
    return 1.0

def plan_room_first(members, hours=6, strangers=False, trace=None):
    R, tags, ctx, v = readings(members, strangers)
    extra, lines, log = profile_layer(members, R)
    R = R + extra
    tops = {m.name: Dz.effective_top(m, members) for m in members}
    roam, _, _ = D2.line_value(members, 'ROAM')
    if 'ROAM' in lines: roam = lines['ROAM']
    n = S.n_stops(roam, hours)
    if D2.line_value(members, 'ROAM')[1]: tags.append('Settle Then Roam')
    ramp, ramp_split, _ = D2.line_value(members, 'RAMP')
    if 'RAMP' in lines: ramp = lines['RAMP']
    if ramp >= 60 and n > 1: tags.append('Builds to It')
    elif ramp <= 40 and n > 1: tags.append('Straight In')
    bringing = [m for m in members if tops[m.name][0]]
    stops, used = [], []
    for k in range(n):
        best = None
        for nm, t in TYPES.items():
            if nm == 'open ground' and k > 0: continue
            sat = {m.name: Dz.satisfaction(t, m, tops[m.name][0]) for m in bringing}
            floor_ok = all(x > 0 for x in sat.values())
            score = sum(r[2] * met(t, r, k, n, ramp) for r in R)
            key = (floor_ok, round(score, 1), nm not in used, round(sum(sat.values()), 2))
            if best is None or key > best[0]: best = (key, nm, sat)
        _, nm, sat = best; used.append(nm)
        stops.append((nm, {m.name: (sat.get(m.name, 1.0), tops[m.name][0], 'top') for m in members}, ''))
    stops.sort(key=lambda s: TYPES[s[0]]['ENRG'], reverse=(ramp < 40))
    absent = any(s[1][m.name][0] == 0 for s in stops for m in bringing)
    chip = 'Something for Everyone' if absent else (tags[0] if tags else ('Open Night' if not bringing else 'In Sync'))
    if trace is not None: trace.extend([('ramp', ramp), ('roam', roam), ('inferred', log)])
    return R, stops, chip

def show(title, members, strangers=False):
    print('\n' + title)
    tr = []
    R, stops, chip = plan_room_first(members, 6, strangers, tr)
    print('   readings: ' + '; '.join(f'{a} {k} {val if not isinstance(val, float) else round(val)}' for a, (k, val), w in R))
    inf = dict(tr).get('inferred') or []
    if inf: print('   inferred: ' + '; '.join(f'{nm} ({",".join(who)}) -> {ax} {pole}' for nm, who, ax, pole, why in inf))
    f_, _ = fill(stops, members, [])
    print('   ' + ' -> '.join(f'[{tn}] {vn.name.split(" (")[0] if vn else "-"}' for tn, vn, lv, n, sp in f_))
    print('   ' + ' | '.join(f'{m.name} ' + '/'.join(f'{s[1][m.name][0]:.1f}' if s[1][m.name][1] else 'easy' for s in stops) for m in members) + f'   chip: {chip}')

if __name__ == '__main__':
    show('1. Caught the Spark: Arjun 88, Dev 85, Meher 45, Zoya 50', [M('Arjun', ENRG=88, CROWD=70), M('Dev', ENRG=85, MOVE=72), M('Meher', ENRG=45, TALK=62), M('Zoya', ENRG=50, AFFIL=66)])
    show('2. two energy camps, no #2s: Dev 90 v Ira 15', [M('Dev', ENRG=90, CROWD=60), M('Ira', ENRG=15, TALK=60), M('Kabir', AFFIL=70)])
    show('3. three at 70+ and one firm 12 who is a firm talker', [M('Arjun', ENRG=88, CROWD=70), M('Dev', ENRG=78, MOVE=70), M('Zoya', ENRG=72, SCEN=88), M('Bela', ENRG=12, TALK=80)])
    show('4. Arjun ENRG / Bea TALK+ROAM / Chetan GAMES', [M('Arjun', ENRG=90, CROWD=80), M('Bea', ROAM=88, TALK=80), M('Chetan', GAMES=92, AFFIL=88)])
    show('5. table majority v one room person', [M('Kabir', AFFIL=88, TALK=70), M('Meher', AFFIL=85), M('Zoya', AFFIL=82), M('Rohan', AFFIL=12, ENRG=75)])
    show('6. one 88 and two firm 12s', [M('Arjun', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80), M('Neha', ENRG=12, AFFIL=85)])
    show('7. strangers: a mover, a crowd person, a gamer', [M('Vik', MOVE=85, ENRG=70), M('Tia', CROWD=70, ENRG=65), M('Nia', GAMES=80, TALK=55)], strangers=True)
    show('8. all low energy, all talkers', [M('A', ENRG=12, TALK=85), M('B', ENRG=20, TALK=80, AFFIL=85), M('C', ENRG=15, TALK=82)])
