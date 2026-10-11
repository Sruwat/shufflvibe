# -*- coding: utf-8 -*-
"""Does the vibe name survive losing CROWD, ROAM, RAMP and GAMES?
Names a synthetic population under V4 (8 factors) and V5 (6 identity factors) and compares
vocabulary, concentration and how often nothing qualifies for the second slot."""
import random, math
from collections import Counter

random.seed(11)

V4 = ['ENRG', 'AFFIL', 'CROWD', 'TALK', 'ROAM', 'RAMP', 'MOVE', 'GAMES']
V5 = ['ENRG', 'AFFIL', 'TALK', 'FOCUS', 'MOVE', 'SPONT']

# first-word / second-noun per pole
W = {
 'ENRG':  (('Low-Key', 'Slow-Burner'), ('Peak', 'Climber')),
 'AFFIL': (('Mingling', 'Mingler'), ('Inner-Circle', 'Insider')),
 'CROWD': (('Quiet', 'Quiet-One'), ('Big-Room', 'Crowd-Chaser')),
 'TALK':  (('Loud', 'Noise-Seeker'), ('Talking', 'Table-Talker')),
 'ROAM':  (('Settled', 'Settler'), ('Nomad', 'Nomad')),
 'RAMP':  (('Straight-In', 'Starter'), ('Slow-Build', 'Builder')),
 'MOVE':  (('Seated', 'Sitter'), ('Moving', 'Floor-Filler')),
 'GAMES': (('No-Games', 'Lounger'), ('Arcade', 'Score-Keeper')),
 'FOCUS': (('Headline', 'Headliner'), ('Front-Row', 'Front-Rower')),
 'SPONT': (('Locked-In', 'Planner'), ('Last-Minute', 'Wildcard')),
}
SINGLE = {
 'ENRG': ('Slow Burner', 'Night Climber'), 'AFFIL': ('Room Worker', 'Inner Circle'),
 'CROWD': ('Quiet One', 'Crowd Chaser'),   'TALK':  ('Noise Seeker', 'Table Talker'),
 'ROAM': ('Settler', 'Nomad'),             'RAMP':  ('Straight In', 'Slow Build'),
 'MOVE': ('Sitter', 'Floor Filler'),       'GAMES': ('Lounger', 'Score Keeper'),
 'FOCUS': ('Headline Act', 'Front Row'),   'SPONT': ('Locked In', 'Wild Card'),
}

K, STICKY = 5, 15

def person(factors):
    """most people land near the middle; a minority are firm. truncated normal, sd 22."""
    v, lat = {}, {}
    for f in factors:
        s = min(100, max(0, int(random.gauss(50, 22))))
        v[f] = s
        lat[f] = round(random.random(), 2)
    return v, lat

def firmness(v, lat, f):
    s, band = v[f], 21 <= v[f] <= 30 or 70 <= v[f] <= 79
    return lat[f] if band and lat[f] >= 0.60 else (1.0 if (s <= 20 or s >= 80) else 0.0)

def name(v, lat, factors, second_min=25):
    key = lambda f: abs(v[f] - 50) + K * firmness(v, lat, f)
    first = max(factors, key=key)
    d_first = abs(v[first] - 50)
    d = {f: abs(v[f] - 50) for f in factors if f != first}
    cands = [f for f in d if d[f] >= d_first - STICKY and d[f] >= second_min]
    pole = lambda f: 1 if v[f] >= 50 else 0
    if not cands:
        return SINGLE[first][pole(first)], True
    second = max(cands, key=lambda f: d[f] + K * firmness(v, lat, f))
    return W[first][pole(first)][0] + ' ' + W[second][pole(second)][1], False

def run(factors, label, second_min=25, n=20000):
    names, singles = Counter(), 0
    firsts = Counter()
    for _ in range(n):
        v, lat = person(factors)
        nm, is_single = name(v, lat, factors, second_min)
        names[nm] += 1; singles += is_single
        firsts[max(factors, key=lambda f: abs(v[f] - 50) + K * firmness(v, lat, f))] += 1
    tot = sum(names.values())
    ent = -sum((c / tot) * math.log2(c / tot) for c in names.values())
    print('%-34s %4d distinct   top name %5.1f%%   entropy %4.2f bits   single-name %4.1f%%'
          % (label, len(names), 100.0 * names.most_common(1)[0][1] / tot, ent, 100.0 * singles / n))
    return names, firsts

print('=' * 104)
print('VIBE NAME VOCABULARY - V4 (8 factors) against V5 (6 identity factors)')
print('=' * 104)
print('theoretical ceiling:  V4  %d pairs + %d singles = %d      V5  %d pairs + %d singles = %d'
      % (16 * 14, 16, 16 * 14 + 16, 12 * 10, 12, 12 * 10 + 12))
print()
n4, f4 = run(V4, 'V4, eight factors')
n5, f5 = run(V5, 'V5, six identity factors')
print()
print('the single-name rate is the problem: fewer factors means fewer candidates clear SECOND_MIN.')
for sm in (25, 22, 20, 18):
    run(V5, '   V5 with SECOND_MIN = %d' % sm, second_min=sm)

print()
print('=' * 104)
print('WHICH FACTOR WINS THE FIRST SLOT   (share of the population it names)')
print('=' * 104)
for lbl, fc, fs in (('V4', V4, f4), ('V5', V5, f5)):
    tot = sum(fs.values())
    print(lbl + ':  ' + '   '.join('%s %.0f%%' % (f, 100.0 * fs[f] / tot) for f in fc))
print()
print('flat, as it should be - the key is |s-50| and every factor has the same spread, so no')
print('factor is structurally advantaged. Losing four factors does not concentrate the first slot.')
print()
print('=' * 104)
print('THE TEN MOST COMMON V5 NAMES')
print('=' * 104)
tot = sum(n5.values())
for nm, c in n5.most_common(10):
    print('   %-28s %4.1f%%' % (nm, 100.0 * c / tot))
