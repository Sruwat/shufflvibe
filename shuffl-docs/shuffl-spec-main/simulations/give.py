# -*- coding: utf-8 -*-
"""Exploration: AFFIL as 'give' - how far a person bends the rest of their vibe for the group."""
import design3 as D3, design2 as D2, design as Dz, splitsim as S
from splitsim import M, STOP_AXES, fill

def give(m):
    """0-0.4. Give comes from AFFIL being among the person's TOP reasons tonight (their #1, or a strong #2):
    'my people are why I am out' - so the rest of their vibe pushes at half strength."""
    w = sorted(STOP_AXES, key=lambda f: -abs(m.vibe[f] - 50))
    if m.vibe['AFFIL'] < 65: return 0.0
    if w[0] == 'AFFIL': return 0.4
    if len(w) > 1 and w[1] == 'AFFIL' and abs(m.vibe['AFFIL'] - 50) >= 25 and abs(m.vibe[w[0]] - 50) - abs(m.vibe['AFFIL'] - 50) <= 10: return 0.4
    return 0.2
_bend = D2.bend_pts
def bend_pts(m, f):
    b = _bend(m, f)
    return b * (1 + give(m)) if (f != 'AFFIL' and D2.is_firm(m, f)) else b
D2.bend_pts = bend_pts
S.delivers = lambda t, m, f: (t[f] >= m.vibe[f] - bend_pts(m, f)) if m.pole(f) == 'high' else (t[f] <= m.vibe[f] + bend_pts(m, f))
_strength = D3.strength
def strength(m, f, pole):
    s = _strength(m, f, pole)
    return s * (1 - give(m) / 2) if f != 'AFFIL' else s          # a high-AFFIL person pushes their pole on the group less hard
D3.strength = strength
_opp = D3.opposed_by
def opposed_by(m, f, members):
    """A high-AFFIL person yields more readily: even a band-strength opposer (0.5) moves their top to a strong #2."""
    out = _opp(m, f, members)
    hi = sum(strength(x, f, 'high') for x in members); lo = sum(strength(x, f, 'low') for x in members)
    mine = hi if m.pole(f) == 'high' else lo; theirs = lo if m.pole(f) == 'high' else hi
    if give(m) >= 0.4 and not mine > theirs:                       # yields to a mild opposer - unless their side is the majority
        for o in members:
            if o is m or o.pole(f) == m.pole(f) or o.name in out: continue
            if _strength(o, f, o.pole(f)) >= 0.5: out.append(o.name)
    return out
Dz.opposed_by = opposed_by

def show(title, members):
    print('\n' + title)
    for m in members: print(f'   {m.name:<6} AFFIL {m.vibe["AFFIL"]:>3} give {give(m):.1f}  firm on {[f for f in S.VIBE if D2.is_firm(m, f)]}')
    trace = []; stops, chip, form, durs = D3.design(members, trace, 6)
    for t in trace:
        if 'stands in' in t or 'top ' in t: print('   ' + t.strip())
    filled, _ = fill(stops, members, trace)
    print('   ' + ' -> '.join(f'[{tn}] {vn.name.split(" (")[0] if vn else "-"}' for tn, vn, lv, n, sp in filled))
    print('   ' + ' | '.join(f'{m.name} ' + '/'.join(f'{s[1][m.name][0]:.1f}' if s[1][m.name][1] else 'easy' for s in stops) for m in members) + f'   chip: {chip}')


show('A. Kabir ENRG 88 with AFFIL 30 v Neha ENRG 25 (band, normal)', [M('Kabir', ENRG=88, CROWD=75, AFFIL=30), M('Neha', ENRG=25, TALK=80)])
show('B. Kabir ENRG 88 with AFFIL 78 (a strong #2: my people are half of why) v the same Neha', [M('Kabir', ENRG=88, CROWD=75, AFFIL=78), M('Neha', ENRG=25, TALK=80)])
show('C. two 88s with AFFIL 30 and one firm 12', [M('A', ENRG=88, AFFIL=30, CROWD=70), M('B', ENRG=85, AFFIL=30, MOVE=70), M('C', ENRG=12, TALK=80)])
show('D. two 88s with AFFIL 78 and one firm 12 - they push at half strength', [M('A', ENRG=88, AFFIL=78, CROWD=70), M('B', ENRG=85, AFFIL=78, MOVE=70), M('C', ENRG=12, TALK=80)])
show('E. Bela ENRG 12 with AFFIL 78 v Aarav 88 - she bends further', [M('Aarav', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80, AFFIL=78)])
