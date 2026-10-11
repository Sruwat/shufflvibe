# -*- coding: utf-8 -*-
import design3 as D3
from splitsim import M, STOP_AXES, fill
def lat(m, **kw): m.lat = kw; return m
def run(title, members, axis, hours=6, strangers=False):
    trace = []
    stops, chip, form, durs = D3.design(members, trace, hours, strangers)
    v = None
    for t in trace:
        if t.strip().startswith('chemistry vector'):
            v = t.split(axis + ' ')[1].split(',')[0] if axis + ' ' in t else '-'
    filled, missing = fill(stops, members, trace)
    stop_s = ' -> '.join(f'[{tn}] {vn.name.split(" (")[0] if vn else "-"}' + (f' {d:.1f}h' if len(set(round(x,1) for x in durs)) > 1 else '') for (tn, vn, lv, n, sp), d in zip(filled, durs))
    sat = ' | '.join(f'{m.name} ' + '/'.join(f'{s[1][m.name][0]:.1f}' if s[1][m.name][1] else 'easy' for s in stops) for m in members)
    print(f'{title}\n     room {axis} {v} · {stop_s}\n     {sat} · chip: {chip}')

print('\n==== ENRG ====')
run('1 all high (88, 85, 90)', [M('A', ENRG=88, CROWD=70), M('B', ENRG=85, MOVE=70), M('C', ENRG=90, TALK=40)], 'ENRG')
run('2 all low (12, 20, 15)', [M('A', ENRG=12, TALK=80), M('B', ENRG=20, AFFIL=85), M('C', ENRG=15, FOOD=88)], 'ENRG')
run('3 two 85+ among two neutrals (45, 50) - the spark', [M('A', ENRG=88, CROWD=70), M('B', ENRG=85, MOVE=72), M('C', ENRG=45, TALK=62), M('D', ENRG=50, AFFIL=66)], 'ENRG')
run('4 highs outnumber: 88, 78, 72 and one firm 12', [M('A', ENRG=88, CROWD=70), M('B', ENRG=78, MOVE=70), M('C', ENRG=72, SCEN=88), M('D', ENRG=12, TALK=80)], 'ENRG')
run('5 a tie: one 88, one 12', [M('A', ENRG=88, CROWD=70), M('B', ENRG=12, TALK=80)], 'ENRG')
run('6 lows outnumber: one 88, two 12s', [M('A', ENRG=88, CROWD=70), M('B', ENRG=12, TALK=80), M('C', ENRG=12, AFFIL=85)], 'ENRG')
run('7 everyone 55-79, nobody demanding it', [M('A', ENRG=62, AFFIL=80), M('B', ENRG=70, GAMES=78), M('C', ENRG=58, TALK=72)], 'ENRG')
print('\n==== AFFIL ====')
run('1 all high - Our Table', [M('A', AFFIL=90, TALK=75), M('B', AFFIL=85, FOOD=88), M('C', AFFIL=88, ENRG=40)], 'AFFIL')
run('2 all low - Meet the Room', [M('A', AFFIL=12, CROWD=75), M('B', AFFIL=15, ENRG=78), M('C', AFFIL=18, MOVE=70)], 'AFFIL')
run('3 split, table majority (88, 85, 82 v 12)', [M('A', AFFIL=88, TALK=70), M('B', AFFIL=85, FOOD=88), M('C', AFFIL=82), M('D', AFFIL=12, ENRG=75)], 'AFFIL')
run('4 split, room majority (88 v 15, 12, 18)', [M('A', AFFIL=88, TALK=70), M('B', AFFIL=15, CROWD=75), M('C', AFFIL=12, ENRG=78), M('D', AFFIL=18, MOVE=70)], 'AFFIL')
run('5 a public room of strangers', [M('A', ENRG=70, CROWD=65), M('B', MOVE=75, ENRG=68), M('C', GAMES=62, TALK=55)], 'AFFIL', strangers=True)
print('\n==== CROWD ====')
run('1 all high', [M('A', CROWD=88, ENRG=70), M('B', CROWD=85, AFFIL=40), M('C', CROWD=90, MOVE=60)], 'CROWD')
run('2 all low', [M('A', CROWD=12, TALK=80), M('B', CROWD=15, AFFIL=85), M('C', CROWD=20, FOOD=88)], 'CROWD')
run('3 one crowd-hater (12) in an energy room (88, 85) - counts at half', [M('A', ENRG=88, CROWD=70), M('B', ENRG=85, MOVE=72), M('C', CROWD=12, TALK=62)], 'CROWD')
run('4 one crowd-hater (12) in a talk room (85, 82) - counts in full', [M('A', TALK=85, AFFIL=70), M('B', TALK=82, FOOD=88), M('C', CROWD=12, ENRG=40)], 'CROWD')
run('5 one crowd-lover (90) among table people (85, 88)', [M('A', CROWD=90, ENRG=70), M('B', AFFIL=85, TALK=75), M('C', AFFIL=88, FOOD=88)], 'CROWD')
print('\n==== TALK ====')
run('1 all talkers', [M('A', TALK=88, AFFIL=70), M('B', TALK=85, FOOD=88), M('C', TALK=82, ENRG=40)], 'TALK')
run('2 all noise (12, 15, 18)', [M('A', TALK=12, ENRG=85), M('B', TALK=15, MOVE=80), M('C', TALK=18, CROWD=85)], 'TALK')
run('3 one firm talker (88) among energy people (88, 85) - the floor at 40', [M('A', ENRG=88, CROWD=70), M('B', ENRG=85, MOVE=72), M('C', TALK=88, ENRG=50)], 'TALK')
run('4 one noise-wanter (12) among talkers (85, 82) - lives with it', [M('A', TALK=85, AFFIL=70), M('B', TALK=82, FOOD=88), M('C', TALK=12, ENRG=75)], 'TALK')
print('\n==== MOVE ====')
run('1 all movers', [M('A', MOVE=88, ENRG=80), M('B', MOVE=85, CROWD=75), M('C', MOVE=90, ENRG=78)], 'MOVE')
run('2 all sitters', [M('A', MOVE=12, TALK=80), M('B', MOVE=15, AFFIL=85), M('C', MOVE=18, FOOD=88)], 'MOVE')
run('3 movers outnumber (85, 80 v 15) - the night ends on a floor', [M('A', MOVE=85, ENRG=78), M('B', MOVE=80, CROWD=70), M('C', MOVE=15, TALK=72)], 'MOVE')
run('4 sitters outnumber (15, 12 v 85) - room to stand, not a floor', [M('A', MOVE=15, TALK=80), M('B', MOVE=12, AFFIL=85), M('C', MOVE=85, ENRG=75)], 'MOVE')
run('5 strangers with a mover - On Our Feet', [M('A', MOVE=85, ENRG=70), M('B', CROWD=70, ENRG=65), M('C', TALK=60, GAMES=58)], 'MOVE', strangers=True)
print('\n==== GAMES ====')
run('1 all gamers', [M('A', GAMES=90, AFFIL=70), M('B', GAMES=85, ENRG=65), M('C', GAMES=88, TALK=55)], 'GAMES')
run('2 one gamer (90) among non-gamers - games on the premises, not the point', [M('A', GAMES=90, AFFIL=70), M('B', AFFIL=88, TALK=75), M('C', TALK=80, FOOD=88), M('D', AFFIL=80, SCEN=88)], 'GAMES')
run('3 two energy camps, no #2s - the games bridge takes the compromise stop', [M('A', ENRG=90, CROWD=60), M('B', ENRG=15, TALK=60), M('C', AFFIL=70)], 'GAMES')
run('4 a strangers room with a gamer - first stop breaks the ice', [M('A', GAMES=80, ENRG=60), M('B', CROWD=70, ENRG=65), M('C', TALK=60)], 'GAMES', strangers=True)
print('\n==== ROAM ====')
run('1 all roamers (92, 85, 88)', [M('A', ROAM=92, CROWD=80), M('B', ROAM=85, ENRG=78), M('C', ROAM=88, MOVE=70)], 'ROAM')
run('2 all settlers (12, 15, 20)', [M('A', ROAM=12, AFFIL=90), M('B', ROAM=15, TALK=85), M('C', ROAM=20, FOOD=88)], 'ROAM')
run('3 a roamer and a settler, both firm (92 v 12)', [M('A', ROAM=92, CROWD=80), M('B', ROAM=12, AFFIL=90, GAMES=72)], 'ROAM')
run('4 two roamers, one settler (92, 85 v 12)', [M('A', ROAM=92, CROWD=80), M('B', ROAM=85, ENRG=78), M('C', ROAM=12, AFFIL=90)], 'ROAM')
run('5 two settlers, one roamer (12, 15 v 92)', [M('A', ROAM=12, AFFIL=90), M('B', ROAM=15, TALK=85), M('C', ROAM=92, CROWD=80)], 'ROAM')
run('6 a roamer against a flexible 30', [M('A', ROAM=92, CROWD=80), M('B', ROAM=30, AFFIL=90)], 'ROAM')
