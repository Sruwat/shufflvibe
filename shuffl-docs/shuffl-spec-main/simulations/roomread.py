# -*- coding: utf-8 -*-
"""The room read, on CHEMISTRY V3 (interplay.py) - the levels the spec documents.

Replaces design3.chemistry_vector as the planner's source of levels. design3 stays for is_firm,
strength and the TALK floor. Same signature, so readings.py only swaps the call:
    (levels, tags, ctx)
Levels come from interplay.room (V3: per-axis pulls, sublinear influence, the cross-axis rules,
AFFIL returning 'split'). Tags and ctx are membership patterns, computed here against V3's levels.
"""
import interplay as IP, design3 as D3
from splitsim import STOP_AXES

def is_firm(m, f): return D3.is_firm(m, f)
def strength(m, f, pole): return D3.strength(m, f, pole)

def room_read(members, strangers=False):
    v = IP.room(members, verbose=False)
    tags = []
    n = len(members)

    # ---- ENRG: V3 has already applied contagion; the tag names the pattern
    highs = [m for m in members if strength(m, 'ENRG', 'high') > 0]
    lows  = [m for m in members if strength(m, 'ENRG', 'low') > 0]
    mids  = [m for m in members if 35 <= m.vibe['ENRG'] <= 65]
    hi = sum(strength(m, 'ENRG', 'high') for m in members)
    lo = sum(strength(m, 'ENRG', 'low') for m in members)
    if highs and not lows and len(highs) == n:            tags.append('Running Hot')
    elif lows and not highs and len(lows) == n:           tags.append('Slow Burn')
    elif (highs and not lows and len(highs) <= 2 and mids
          and 1 <= len([m for m in highs if m.vibe['ENRG'] >= 80]) <= 2):  tags.append('Caught the Spark')
    elif highs and lows and lo >= hi:                     tags.append('Slow Burn')
    elif (not lows and not any(m.vibe['ENRG'] >= 80 for m in members)
          and all(55 <= m.vibe['ENRG'] <= 79 for m in members)): tags.append('Could Go Late')

    # ---- AFFIL: V3 returns 'split' where both poles are firmly present
    ah = [m for m in members if is_firm(m, 'AFFIL') and m.pole('AFFIL') == 'high']
    al = [m for m in members if is_firm(m, 'AFFIL') and m.pole('AFFIL') == 'low']
    affil_split = (v['AFFIL'] == 'split')
    if affil_split:                                 tags.append('Table and Floor')
    elif ah and len(ah) == n:                       tags.append('Our Table')
    elif (al and len(al) == n) or strangers:        tags.append('Meet the Room')

    # ---- TALK: the floor is absolute, the tag is about a lively room you can still talk in
    talkers = [m for m in members if is_firm(m, 'TALK') and m.pole('TALK') == 'high']
    enrg = v['ENRG'] if not isinstance(v['ENRG'], str) else 50
    if talkers and enrg >= 60: tags.append('Buzz, Not Noise')

    a_hi = sum(strength(m, 'AFFIL', 'high') for m in members)
    a_lo = sum(strength(m, 'AFFIL', 'low') for m in members)
    g_hi = sum(strength(m, 'GAMES', 'high') for m in members)
    mv_hi = sum(strength(m, 'MOVE', 'high') for m in members)
    mv_lo = sum(strength(m, 'MOVE', 'low') for m in members)
    ctx = dict(affil_split=affil_split, talkers=bool(talkers), strangers=strangers,
               affil_lean='high' if a_hi > a_lo else 'low' if a_lo > a_hi else 'even',
               games_minority=(0 < g_hi < (len(members) / 2.0)),
               movers_win=(mv_hi > mv_lo and mv_hi > 0))
    return v, tags, ctx
