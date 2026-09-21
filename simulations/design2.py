# -*- coding: utf-8 -*-
"""design.py + the 2026-09-18 bend rule: bend only counts at the extremes. A vibe score in 30-70 is
maximum bend by construction; an extreme score (0-20 / 80-100) is FIRM only if its bend (score x latency)
is 0.0-0.3; everything else is flexible. 'I would love this' / 'not my kind of night' - never 'I must'."""
import design as Dz
import splitsim as S
from splitsim import M, TYPES, STOP_AXES

BEND_FIRM = 0.30
EXTREME_LO, EXTREME_HI = 20, 80        # inclusive: a 20 or an 80 is extreme
BAND_LO, BAND_HI = 30, 70              # 30-70 is the middle: maximum bend, always
FAST = 0.60                            # latency-firmness at or above this = a fast swipe (rank-based, §6.2); nobody is 'fast' before §6.3 validates
BEND_EXTREME_PTS, BEND_BAND_PTS = 25, 28

def zone(m, f):
    s = m.vibe[f]
    if s <= EXTREME_LO or s >= EXTREME_HI: return 'extreme'
    if s < BAND_LO or s > BAND_HI: return 'band'          # 21-29, 71-79
    return 'middle'
def fast(m, f): return getattr(m, 'lat', {}).get(f, 0.0) >= FAST
def is_firm(m, f):
    """Firm = an extreme score (whatever the latency - a slow 12 still counts), OR a band score swiped fast.
    30-70 is never firm."""
    z = zone(m, f)
    return z == 'extreme' or (z == 'band' and fast(m, f))
def bend_frac(m, f):
    z = zone(m, f)
    if z == 'extreme': return BEND_EXTREME_PTS / 100
    if z == 'band' and fast(m, f): return BEND_BAND_PTS / 100
    return 1.0
def bend_pts(m, f): return 100 * bend_frac(m, f) if is_firm(m, f) else abs(m.vibe[f] - 50) + 5   # flexible = your side of the middle

# ---- patch the model
S.delivers = lambda t, m, f: (t[f] >= m.vibe[f] - bend_pts(m, f)) if m.pole(f) == 'high' else (t[f] <= m.vibe[f] + bend_pts(m, f))
Dz.opposed_by = lambda m, f, members: [o.name for o in members if o is not m and is_firm(o, f) and o.pole(f) != m.pole(f)]
def signals(t, members):
    return sum(abs(t[f] - m.vibe[f]) * (m.firm(f) if is_firm(m, f) else 0.25 * m.firm(f)) for m in members for f in STOP_AXES)
Dz.signals = signals
_orig_roam = Dz.roam_count
def roam_count(members, hours, trace):
    firm = [m for m in members if is_firm(m, 'ROAM')]
    if not firm:
        wants = [m for m in members if abs(m.vibe['ROAM'] - 50) >= S.WANT_FLOOR]
        if not wants: return S.n_stops(50, hours), ''
        val = sum(m.vibe['ROAM'] * m.firm('ROAM') for m in wants) / sum(m.firm('ROAM') for m in wants)
        return S.n_stops(val, hours), ''
    poles = {m.pole('ROAM') for m in firm}
    w = {m.name: 1.0 / bend_frac(m, 'ROAM') for m in firm}                 # the narrower the bend, the more say
    val = sum(m.vibe['ROAM'] * w[m.name] for m in firm) / sum(w.values())
    note = '' if len(poles) == 1 else f'ROAM: firm on both poles ({", ".join(f"{m.name} {m.vibe["ROAM"]}" for m in firm)}) -> one number, {val:.0f}'
    return S.n_stops(val, hours), note
Dz.roam_count = roam_count

def show(title, members, hours=6):
    print('\n' + title)
    for m in members:
        firm = [f'{f} {m.vibe[f]} (bend {bend_frac(m, f):.2f})' for f in S.VIBE if is_firm(m, f)]
        print(f'   {m.name:<7} firm: {firm or "nothing - flexible on everything"}')
    print('\n'.join(Dz.plan(members, hours)))

if __name__ == '__main__':
    def lat(m, **kw): m.lat = kw; return m
    show('U. Aarav ENRG 88 v Bela ENRG 12 - both extreme, so both FIRM (fast or slow)',
         [M('Aarav', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Chirag', FOOD=88, ROAM=62)])
    show('U-slow. the same, Aarav swiped slowly - still firm: an 88 is an 88',
         [lat(M('Aarav', ENRG=88, CROWD=70), ENRG=0.1), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Chirag', FOOD=88, ROAM=62)])
    show('U-band. Bela at ENRG 25 (the band) swiped at normal speed - flexible, opposes nobody',
         [M('Aarav', ENRG=88, CROWD=70), M('Bela', ENRG=25, TALK=80, LIVE=88), M('Chirag', FOOD=88, ROAM=62)])
    show('U-band-fast. Bela at ENRG 25 swiped FAST - firm; Aarav gives way to his #2',
         [M('Aarav', ENRG=88, CROWD=70), lat(M('Bela', ENRG=25, TALK=80, LIVE=88), ENRG=0.8), M('Chirag', FOOD=88, ROAM=62)])
    show('H. Aarav ENRG 90 v Neha ENRG 15, no strong #2s - both firm, both tops stand',
         [M('Aarav', ENRG=90, CROWD=60, ROAM=60), M('Neha', ENRG=15, TALK=60, FOOD=92)])
    show('ROAM: A 92 (extreme) v B 30 (middle) - B flexible, A sets three stops', [M('A', ROAM=92, CROWD=80), M('B', AFFIL=90, ROAM=30, GAMES=72)])
    show('ROAM: A 92 v B 25 swiped fast - both firm -> one number', [M('A', ROAM=92, CROWD=80), lat(M('B', AFFIL=90, ROAM=25, GAMES=72), ROAM=0.9)])
    show('Z. Priya CROWD 75 normal speed (flexible) with Rohan CROWD 12 (firm)', [M('Priya', CROWD=75, TALK=72), M('Rohan', CROWD=12, TALK=60)])
    show('T. the whole team out', [M('A', AFFIL=88, ENRG=85, GAMES=80, ROAM=75), M('B', AFFIL=85, ENRG=80, GAMES=88), M('C', AFFIL=90, ENRG=88, GAMES=70, FOOD=88)])
