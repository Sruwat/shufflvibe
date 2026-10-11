# -*- coding: utf-8 -*-
"""What each axis DICTATES about the shape of the night: hold one axis extreme, everything else neutral,
and show what changes - stop count, types, order, durations."""
import readings as RD, interplay as IP, design3 as D3, design as Dz
from splitsim import M, TYPES, STOP_AXES, fill

def night(title, members, hours=6, strangers=False):
    R, stops, chip = RD.plan_room_first(members, hours, strangers)
    v = IP.room(members, verbose=False)
    f_, _ = fill(stops, members, [])
    lv = ', '.join(f'{f} ' + (v[f] if isinstance(v[f], str) else f'{v[f]:.0f}') for f in ['ENRG','AFFIL','CROWD','TALK','MOVE','GAMES','ROAM'])
    print('\n' + title)
    print('     room: ' + lv)
    print('     readings: ' + ('; '.join(f'{a} {k}' for a, (k, val), w in R) or '-'))
    print('     night: ' + ' -> '.join(f'[{tn}] {vn.name.split(" (")[0] if vn else "-"}' for tn, vn, l, n, sp in f_) + f'   chip: {chip}')

N = dict(ENRG=50, AFFIL=50, CROWD=50, TALK=50, ROAM=50, MOVE=50, GAMES=50)
def mk(name, **kw):
    d = dict(N); d.update(kw); return M(name, **d)

print('=== ENRG — the arc: where the night starts and where it ends ===')
night('high (three at 85+)', [mk('A', ENRG=88), mk('B', ENRG=86), mk('C', ENRG=85)])
night('low (three at 15)',   [mk('A', ENRG=15), mk('B', ENRG=18), mk('C', ENRG=12)])

print('\n=== AFFIL — who the setting faces ===')
night('high (our own table)', [mk('A', AFFIL=88), mk('B', AFFIL=86), mk('C', AFFIL=85)])
night('low (out to meet people)', [mk('A', AFFIL=12), mk('B', AFFIL=15), mk('C', AFFIL=18)])
night('split', [mk('A', AFFIL=88), mk('B', AFFIL=85), mk('C', AFFIL=12)])

print('\n=== CROWD — how full ===')
night('high', [mk('A', CROWD=88), mk('B', CROWD=86), mk('C', CROWD=85)])
night('low',  [mk('A', CROWD=15), mk('B', CROWD=18), mk('C', CROWD=12)])

print('\n=== TALK — whether you can hear each other ===')
night('high (firm talkers)', [mk('A', TALK=88), mk('B', TALK=86), mk('C', TALK=85)])
night('low (noise wanted)',  [mk('A', TALK=15), mk('B', TALK=18), mk('C', TALK=12)])

print('\n=== MOVE — on your feet or sat down ===')
night('high', [mk('A', MOVE=88), mk('B', MOVE=86), mk('C', MOVE=85)])
night('low',  [mk('A', MOVE=15), mk('B', MOVE=18), mk('C', MOVE=12)])

print('\n=== GAMES — something to play ===')
night('high', [mk('A', GAMES=88), mk('B', GAMES=86), mk('C', GAMES=85)])
night('low',  [mk('A', GAMES=15), mk('B', GAMES=18), mk('C', GAMES=12)])

print('\n=== ROAM — how many places, and for how long ===')
night('high (three roamers)', [mk('A', ROAM=92), mk('B', ROAM=88), mk('C', ROAM=85)])
night('low (three settlers)', [mk('A', ROAM=12), mk('B', ROAM=15), mk('C', ROAM=18)])
night('split (a roamer and two settlers)', [mk('A', ROAM=92), mk('B', ROAM=15), mk('C', ROAM=18)])
