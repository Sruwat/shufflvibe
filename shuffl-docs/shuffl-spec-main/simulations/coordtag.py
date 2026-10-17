# -*- coding: utf-8 -*-
"""COORDINATE TAGS AGAINST FACTOR SCORES.

The user, 2026-10-07: "explore whether the venues can be tagged with their best co-ordinate in a
skeleton as a replacement to tagging them with factor scores, and then checking whether that venue
matches the plan according to the timing and placement."

The current model stores a venue's ENERGY and CROWD and ranks by distance to the drawn stop. The
proposal stores WHERE IN A NIGHT the venue belongs - an opener, a middle, a closer - and matches on
position instead.

**The real question is not which is more elegant. It is which survives our measurement error.** Our
venue scores carry about 7 points of error (`lexicon.py`), and a coarse tag may be more honest about
what we actually know than a two-decimal distance is. That is testable, so this tests it.
"""
import sys, random, math, statistics as st
sys.stdout.reconfigure(encoding='utf-8')

SHAPE_GATE = 12
NOISE = 7.1                      # the lexicon's measured mean error
N_VENUES = 400


def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)


def dist(ve, vc, se, sc):
    """The live rule: energy, plus crowd at 0.6."""
    return abs(ve - se) + 0.6 * abs(vc - sc)


# ---------------------------------------------------------------- the world
def make_world(rng):
    V = []
    for i in range(N_VENUES):
        e = max(5, min(98, rng.gauss(55, 22)))
        c = max(5, min(98, e + rng.gauss(0, 14)))          # crowd correlates with energy, loosely
        opens = 11 if e < 55 else (17 if e < 75 else 20)
        closes = 23 if e < 45 else (26 if e < 75 else 28)  # hours past midnight count on
        V.append(dict(i=i, e=e, c=c, opens=opens, closes=closes,
                      oe=max(0, min(100, e + rng.gauss(0, NOISE))),   # what we OBSERVE
                      oc=max(0, min(100, c + rng.gauss(0, NOISE)))))
    return V


def draw_night(rng):
    k = rng.choice([2, 3, 3, 4])
    start = rng.choice([19, 20, 21])
    stops = []
    e = rng.uniform(25, 55)
    for s in range(k):
        e = min(97, e + rng.uniform(4, 22))                # nights rise
        stops.append(dict(hour=start + 2 * s, e=e, c=max(10, min(97, e + rng.gauss(0, 10))),
                          pos=s / float(k - 1) if k > 1 else 0.0))
    return stops


def open_at(v, hour):
    return v['opens'] <= hour < v['closes']


# ---------------------------------------------------------------- the two methods
def pick_scores(V, stop):
    """A: rank by distance on the OBSERVED scores, inside the gate."""
    cand = [(dist(v['oe'], v['oc'], stop['e'], stop['c']), v) for v in V if open_at(v, stop['hour'])]
    if not cand:
        return None
    best = min(d for d, _ in cand)
    inside = [v for d, v in cand if d <= best + SHAPE_GATE]
    return inside


# the coordinate: where in a night does this venue belong, and at what level
POS_BANDS = [(0.00, 0.34, 'opener'), (0.34, 0.67, 'middle'), (0.67, 1.01, 'closer')]
LVL_BANDS = [(0, 45, 'low'), (45, 72, 'mid'), (72, 101, 'high')]


def band(x, bands):
    for lo, hi, nm in bands:
        if lo <= x < hi:
            return nm
    return bands[-1][2]


def venue_coord(v):
    """The venue's best coordinate, from the OBSERVED scores - a position and a level."""
    # a venue's natural position in a night follows from when it opens and how hard it goes
    pos = 0.0 if v['opens'] <= 12 else (0.5 if v['opens'] < 20 else 1.0)
    return band(pos, POS_BANDS), band(v['oe'], LVL_BANDS)


def pick_coord(V, stop):
    """B: match the venue's coordinate to the stop's coordinate."""
    want = (band(stop['pos'], POS_BANDS), band(stop['e'], LVL_BANDS))
    cand = [v for v in V if open_at(v, stop['hour']) and venue_coord(v) == want]
    if not cand:                                            # relax the level, keep the position
        cand = [v for v in V if open_at(v, stop['hour']) and venue_coord(v)[0] == want[0]]
    if not cand:
        cand = [v for v in V if open_at(v, stop['hour'])]
    return cand or None


# ---------------------------------------------------------------- the trial
def trial(seed, n_nights=3000):
    rng = random.Random(seed)
    V = make_world(rng)
    out = {'scores': [], 'coord': [], 'sizeA': [], 'sizeB': [], 'empty': [0, 0]}
    for _ in range(n_nights):
        for stop in draw_night(rng):
            for name, fn in (('scores', pick_scores), ('coord', pick_coord)):
                cand = fn(V, stop)
                if not cand:
                    out['empty'][0 if name == 'scores' else 1] += 1
                    continue
                # judge every candidate against the TRUE scores - this is the honest measure
                true_d = [dist(v['e'], v['c'], stop['e'], stop['c']) for v in cand]
                out[name].append(st.mean(true_d))
                out['sizeA' if name == 'scores' else 'sizeB'].append(len(cand))
    return out


head('A.  THE TEST')
print("""
  400 venues with a true energy and crowd, and an OBSERVED pair carrying the lexicon's measured
  7.1 points of error. 3,000 drawn nights, every stop put through both methods.

     A  SCORES    rank by distance on the observed scores, keep everything inside SHAPE_GATE 12
     B  COORDINATE  tag each venue opener / middle / closer and low / mid / high, match the stop's
                    own coordinate, relax the level if nothing fits

  **Both are judged against the venue's TRUE energy and crowd**, which neither method can see. The
  number is the mean true shape-distance of the list each method produces - lower is better.
""")
R = trial(5)
line()
print('   %-26s %10s %10s' % ('', 'A scores', 'B coordinate'))
line()
print('   %-26s %10.2f %10.2f' % ('mean true distance of the list',
                                  st.mean(R['scores']), st.mean(R['coord'])))
print('   %-26s %10.1f %10.1f' % ('mean list size', st.mean(R['sizeA']), st.mean(R['sizeB'])))
print('   %-26s %10d %10d' % ('stops with nothing to show', R['empty'][0], R['empty'][1]))
line()

head('B.  THE SAME TEST AT DIFFERENT LEVELS OF MEASUREMENT ERROR')
print("""
  The proposal's real claim is robustness: a coarse tag should not care that our scores are noisy.
  So vary the noise and watch the gap.
""")
print('   %-14s %12s %12s %10s' % ('score error', 'A scores', 'B coordinate', 'A better by'))
line()
for noise in (0.0, 3.0, 7.1, 14.0, 25.0):
    globals()['NOISE'] = noise
    r = trial(11, n_nights=1200)
    a, b = st.mean(r['scores']), st.mean(r['coord'])
    print('   %-14s %12.2f %12.2f %10.2f' % ('%.1f points' % noise, a, b, b - a))
globals()['NOISE'] = 7.1
line()

head('C.  THE PROPOSAL IN ITS STRONGEST FORM')
print("""
  The first version of B took a venue's position from its opening hour alone, which throws away the
  energy information. **The fairest version quantises exactly the same two numbers the scores use**
  - so the only difference left is the resolution, which is the actual question.
""")

CELLS = [(0, 38), (38, 62), (62, 101)]      # three bands per axis, nine cells


def cell(x):
    for i, (lo, hi) in enumerate(CELLS):
        if lo <= x < hi:
            return i
    return 2


def pick_cell(V, stop):
    """B2: quantise energy AND crowd to 3x3 and match the stop's cell, widening if empty."""
    want = (cell(stop['e']), cell(stop['c']))
    openv = [v for v in V if open_at(v, stop['hour'])]
    cand = [v for v in openv if (cell(v['oe']), cell(v['oc'])) == want]
    if not cand:                                   # widen to any adjacent cell
        cand = [v for v in openv
                if abs(cell(v['oe']) - want[0]) <= 1 and abs(cell(v['oc']) - want[1]) <= 1]
    return cand or openv or None


def trial2(seed, n_nights=3000):
    rng = random.Random(seed)
    V = make_world(rng)
    out = {'scores': [], 'cell': [], 'sa': [], 'sb': []}
    for _ in range(n_nights):
        for stop in draw_night(rng):
            for name, fn, sz in (('scores', pick_scores, 'sa'), ('cell', pick_cell, 'sb')):
                cand = fn(V, stop)
                if not cand:
                    continue
                out[name].append(st.mean([dist(v['e'], v['c'], stop['e'], stop['c']) for v in cand]))
                out[sz].append(len(cand))
    return out


print('   %-14s %12s %12s %10s' % ('score error', 'A scores', 'B2 quantised', 'A better by'))
line()
for noise in (0.0, 7.1, 14.0, 25.0, 40.0):
    globals()['NOISE'] = noise
    r = trial2(21, n_nights=1200)
    a, b = st.mean(r['scores']), st.mean(r['cell'])
    print('   %-14s %12.2f %12.2f %10.2f' % ('%.1f points' % noise, a, b, b - a))
globals()['NOISE'] = 7.1
line()
r = trial2(21, n_nights=1200)
print('   list size at our real error: A %.0f   B2 %.0f' % (st.mean(r['sa']), st.mean(r['sb'])))
