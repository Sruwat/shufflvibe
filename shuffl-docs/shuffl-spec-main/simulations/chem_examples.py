# -*- coding: utf-8 -*-
"""One example of every chemistry situation in CHEMISTRY_V3.md, run through interplay.py."""
import interplay as IP, design2 as D2
from splitsim import M, VIBE, STOP_AXES

def mk(name, **kw):
    d = dict(ENRG=50, AFFIL=50, CROWD=50, TALK=50, ROAM=50, MOVE=50, GAMES=50)
    d.update(kw)
    m = M(name, **d)
    return m

def fast(m, f):
    m.lat = dict(getattr(m, 'lat', {})); m.lat[f] = 0.72
    return m

def one(title, members, axes):
    print('\n' + title)
    for m in members:
        pos = ', '.join(f'{f} {m.vibe[f]}' for f in VIBE if abs(m.vibe[f] - 50) >= 12)
        print(f'     {m.name}: {pos or "everything neutral"}')
    v = IP.room(members, verbose=False)
    for f in axes:
        lvl, why = IP.room_level(members, f)
        out = v[f]
        print(f'     -> {f} {out if isinstance(out, str) else format(out, ".0f")}   [{why}]')

print('=' * 30, 'A. the two general mechanisms', '=' * 30)
one('A1. Latane: influence is sublinear - the FIRST person on a pole matters most',
    [mk('A', ENRG=88), mk('B', ENRG=50), mk('C', ENRG=50), mk('D', ENRG=50)], ['ENRG'])
one('A1b. ...a second enthusiast adds much less than the first did',
    [mk('A', ENRG=88), mk('B', ENRG=88), mk('C', ENRG=50), mk('D', ENRG=50)], ['ENRG'])
one('A1c. ...and a third almost nothing',
    [mk('A', ENRG=88), mk('B', ENRG=88), mk('C', ENRG=88), mk('D', ENRG=50)], ['ENRG'])
one('A2. Moscovici: an EXTREME score is a consistent minority (strength 1.0)',
    [mk('A', TALK=85), mk('B', TALK=50), mk('C', TALK=50)], ['TALK'])
one('A2b. the same lean at 75, swiped slowly - half the strength',
    [mk('A', TALK=75), mk('B', TALK=50), mk('C', TALK=50)], ['TALK'])
one('A2c. 75 swiped FAST - three quarters (gated: latency not validated yet)',
    [fast(mk('A', TALK=75), 'TALK'), mk('B', TALK=50), mk('C', TALK=50)], ['TALK'])

print('\n' + '=' * 30, 'B. ENRG - arousal is contagious, upward', '=' * 30)
one('B1. Caught the Spark: two at 85+ and two neutrals',
    [mk('A', ENRG=88), mk('B', ENRG=85), mk('C', ENRG=45), mk('D', ENRG=50)], ['ENRG'])
one('B2. the mirror image - three calm people, and calm does NOT spread the same way',
    [mk('A', ENRG=15), mk('B', ENRG=18), mk('C', ENRG=50)], ['ENRG'])
one('B3. the asymmetry, head to head: two high, two firm low',
    [mk('A', ENRG=85), mk('B', ENRG=88), mk('C', ENRG=15), mk('D', ENRG=12)], ['ENRG'])
one('B4. one 88 against two FIRM 12s - the spark loses',
    [mk('A', ENRG=88), mk('B', ENRG=12), mk('C', ENRG=12)], ['ENRG'])

print('\n' + '=' * 30, 'C. TALK - one talker recruits', '=' * 30)
one('C1. one firm talker, two people who did not ask for it',
    [mk('A', TALK=88), mk('B', TALK=45), mk('C', TALK=40)], ['TALK'])
one('C2. a quiet person does NOT silence a table - against two FIRM talkers',
    [mk('A', TALK=12), mk('B', TALK=85), mk('C', TALK=82)], ['TALK'])
one('C2b. the same quiet person against two MILD talkers (60, 55) - a mild lean has no strength',
    [mk('A', TALK=12), mk('B', TALK=60), mk('C', TALK=55)], ['TALK'])
one('C3. two who want noise against one talker',
    [mk('A', TALK=88), mk('B', TALK=15), mk('C', TALK=12)], ['TALK'])

print('\n' + '=' * 30, 'D. MOVE - venue-defining', '=' * 30)
one('D1. a lone dancer among NEUTRALS - they are movable, the room goes up',
    [mk('A', MOVE=88), mk('B', MOVE=50), mk('C', MOVE=45)], ['MOVE', 'ENRG'])
one('D2. the same dancer against two FIRM sitters - no floor',
    [mk('A', MOVE=88), mk('B', MOVE=12), mk('C', MOVE=20)], ['MOVE'])
one('D3. two dancers, two neutrals',
    [mk('A', MOVE=88), mk('B', MOVE=82), mk('C', MOVE=50), mk('D', MOVE=45)], ['MOVE', 'ENRG'])
one('D4. cross-axis: a high-energy room where NOBODY asked for a floor (capped at 60)',
    [mk('A', ENRG=88), mk('B', ENRG=85), mk('C', ENRG=80)], ['ENRG', 'MOVE'])

print('\n' + '=' * 30, 'E. GAMES - venue-defining', '=' * 30)
one('E1. a lone gamer among neutrals - movable, so the room goes up',
    [mk('A', GAMES=90), mk('B', GAMES=50), mk('C', GAMES=45)], ['GAMES'])
one('E2. the same gamer against ONE firm low - the games night is off',
    [mk('A', GAMES=90), mk('B', GAMES=12), mk('C', GAMES=50)], ['GAMES'])
one('E3. half the room wants games',
    [mk('A', GAMES=90), mk('B', GAMES=85), mk('C', GAMES=45), mk('D', GAMES=50)], ['GAMES'])
one('E4. Sherif: a room split on ENERGY, nobody cares about games (+10, capped at 65)',
    [mk('A', ENRG=88), mk('B', ENRG=12), mk('C', ENRG=85)], ['ENRG', 'GAMES'])
one('E5. a room split ABOUT games - the bridge does NOT fire on its own argument',
    [mk('A', GAMES=90), mk('B', GAMES=12), mk('C', GAMES=45)], ['GAMES'])

print('\n' + '=' * 30, 'F. CROWD - an appraisal, barely spreads', '=' * 30)
one('F1. one person who wants the fullest room in the city, two neutrals',
    [mk('A', CROWD=90), mk('B', CROWD=50), mk('C', CROWD=45)], ['CROWD'])
one('F2. cross-axis: our own people make a full room safe (AFFIL >= 70 -> +8 CROWD)',
    [mk('A', CROWD=72, AFFIL=88), mk('B', CROWD=60, AFFIL=85), mk('C', CROWD=55, AFFIL=75)], ['AFFIL', 'CROWD'])
one('F3. a crowd-lover against a crowd-hater',
    [mk('A', CROWD=90), mk('B', CROWD=12), mk('C', CROWD=50)], ['CROWD'])

print('\n' + '=' * 30, 'G. AFFIL - it does not spread, it splits', '=' * 30)
one('G1. everyone here for their own people',
    [mk('A', AFFIL=88), mk('B', AFFIL=85), mk('C', AFFIL=75)], ['AFFIL', 'CROWD'])
one('G2. everyone out to meet the room',
    [mk('A', AFFIL=12), mk('B', AFFIL=15), mk('C', AFFIL=18)], ['AFFIL'])
one('G3. a firm split - the room has no AFFIL level at all',
    [mk('A', AFFIL=88), mk('B', AFFIL=85), mk('C', AFFIL=12)], ['AFFIL', 'GAMES'])

print('\n' + '=' * 30, 'H. ROAM - a quantity', '=' * 30)
for title, ms in [('H1. one roamer in a PAIR - one other person is easy to move', [mk('A', ROAM=92), mk('B', ROAM=50)]),
                  ('H1b. the same roamer in a FIVE - four people are not', [mk('A', ROAM=92)] + [mk(c, ROAM=50) for c in 'BCDE']),
                  ('H2. split: a firm settler and a firm roamer', [mk('A', ROAM=12), mk('B', ROAM=92)]),
                  ('H2b. split: TWO firm settlers and one roamer', [mk('A', ROAM=12), mk('B', ROAM=15), mk('C', ROAM=92)]),
                  ('H3. everyone settled', [mk('A', ROAM=12), mk('B', ROAM=15), mk('C', ROAM=50)]),
                  ('H3b. everyone roaming', [mk('A', ROAM=92), mk('B', ROAM=88), mk('C', ROAM=50)])]:
    lvl, why = IP.room_level(ms, 'ROAM')
    val, split, pos = D2.roam_value(ms)
    n, note = D2.roam_count(ms, 6, [])
    share = D2.settle_share(val)
    durs = [6 * share] + [6 * (1 - share) / (n - 1)] * (n - 1) if n > 1 else [6.0]
    print(f'\n{title}')
    print(f'     -> V3 level {lvl:.0f}  [{why}]')
    print(f'     -> planner {val:.0f} -> {n} stop(s), ' + ' + '.join(f'{d:.1f}h' for d in durs) + ('   ' + note if note else ''))
