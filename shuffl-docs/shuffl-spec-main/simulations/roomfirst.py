# -*- coding: utf-8 -*-
"""Room-first: the stop type is the one closest to the room's CHEMISTRY vector (the room read as a whole),
with a thin floor (nobody's top absent where the chemistry rules did not make them yield). Compare with
the individual-first designed night (design3)."""
import design3 as D3, design as Dz, splitsim as S
from splitsim import M, TYPES, STOP_AXES, fill

def room_first(members, hours=6, strangers=False):
    trace = []
    v, tags, ctx = D3.chemistry_vector(members, strangers)
    tops = {m.name: Dz.effective_top(m, members) for m in members}
    n, note = D3.D2.roam_count(members, hours, trace)
    if note: tags.append('Settle Then Roam')
    bringing = [m for m in members if tops[m.name][0]]
    stops, used, prev = [], [], -1
    for k in range(n):
        best = None
        for nm, t in TYPES.items():
            if nm == 'open ground' and k > 0: continue
            if ctx['talkers'] and t['TALK'] < D3.TALK_FLOOR: continue
            sat = {m.name: Dz.satisfaction(t, m, tops[m.name][0]) for m in bringing}
            floor_ok = all(x > 0 for x in sat.values())                      # nobody's reason absent - the floor
            # the collective reading, as demands on the type: the room's energy sets where the night ENDS and how it climbs
            target_e = v['ENRG'] if k == n - 1 else min(v['ENRG'], 45 + (v['ENRG'] - 45) * (k + 1) / n)
            reads = -abs(t['ENRG'] - target_e)                                # the arc toward the room's energy
            lo_a, hi_a = (62, 75) if ctx['affil_lean'] == 'high' else (50, 65) if ctx['affil_lean'] == 'low' else (55, 75)
            tag_fit = (1 if ctx['affil_split'] and lo_a <= t['AFFIL'] <= hi_a and t['CROWD'] >= 60 else 0)                     + (1 if ctx['strangers'] and k == 0 and t['GAMES'] >= 60 else 0)                     + (1 if ctx['games_minority'] and 55 <= t['GAMES'] <= 70 else 0)                     + (1 if ctx['movers_win'] and k == n - 1 and t['MOVE'] >= 60 else 0)
            key = (floor_ok, tag_fit, round(reads / 8), nm not in used, round(sum(sat.values()), 2),
                   -sum(abs(t[f] - v[f]) for f in STOP_AXES if f != 'ENRG'))
            if best is None or key > best[0]: best = (key, nm, sat)
        _, nm, sat = best; used.append(nm); prev = TYPES[nm]['ENRG']
        stops.append((nm, {m.name: (sat.get(m.name, 1.0), tops[m.name][0], 'top') for m in members}, ''))
    stops.sort(key=lambda s: TYPES[s[0]]['ENRG'])
    return v, tags, stops

def compare(title, members, strangers=False):
    print('\n' + title)
    tr = []; s_ind, chip, form, durs = D3.design(members, tr, 6, strangers)
    v, tags, s_room = room_first(members, 6, strangers)
    print('   room vector: ' + ', '.join(f'{f} {v[f]:.0f}' for f in STOP_AXES) + f'   tags: {tags or "-"}')
    for label, stops in (('individual-first (now)', s_ind), ('room-first', s_room)):
        f_, _ = fill(stops, members, [])
        print(f'   {label:<22} ' + ' -> '.join(f'[{tn}] {vn.name.split(" (")[0] if vn else "-"}' for tn, vn, lv, n, sp in f_))
        print(f'   {"":<22} ' + ' | '.join(f'{m.name} ' + '/'.join(f'{s[1][m.name][0]:.1f}' if s[1][m.name][1] else 'easy' for s in stops) for m in members))

compare('1. Caught the Spark: Arjun 88, Dev 85, Meher 45, Zoya 50', [M('Arjun', ENRG=88, CROWD=70), M('Dev', ENRG=85, MOVE=72), M('Meher', ENRG=45, TALK=62), M('Zoya', ENRG=50, AFFIL=66)])
compare('2. two energy camps, no #2s: Dev 90 v Ira 15', [M('Dev', ENRG=90, CROWD=60), M('Ira', ENRG=15, TALK=60), M('Kabir', AFFIL=70)])
compare('3. three at 70+ and one firm 12 (a firm talker)', [M('Arjun', ENRG=88, CROWD=70), M('Dev', ENRG=78, MOVE=70), M('Zoya', ENRG=72, SCEN=88), M('Bela', ENRG=12, TALK=80)])
compare('4. Arjun ENRG / Bea TALK+ROAM / Chetan GAMES', [M('Arjun', ENRG=90, CROWD=80), M('Bea', ROAM=88, TALK=80), M('Chetan', GAMES=92, AFFIL=88)])
compare('5. table majority v one room person', [M('Kabir', AFFIL=88, TALK=70), M('Meher', AFFIL=85), M('Zoya', AFFIL=82), M('Rohan', AFFIL=12, ENRG=75)])
