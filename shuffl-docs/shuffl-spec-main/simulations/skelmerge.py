# -*- coding: utf-8 -*-
"""THE SKELETON MERGE - how several drawn lines in one room become one plan.

The hard part is not contagion, it is ALIGNMENT: you cannot average stop 2 of a three-stop night
with stop 2 of a two-stop night, because they are at different times. So a stop is a TIME, not an
index: every skeleton is resampled onto the shared window's clock before anything is merged."""
import math

IMPACT_EXP = 0.6
PULL       = dict(energy=0.75, crowd=0.25)   # CHEMISTRY_V4 pulls: arousal spreads, crowding barely does
DISCOUNT   = dict(energy=0.55, crowd=1.00)   # energy leads high; crowding is an appraisal, symmetric
COUNT_PULL = 0.50                            # the stop count, size-damped, as ROAM was
OPPOSED    = -0.50                           # below this correlation, arcs are opposed, not averagable
AMPLITUDE  = 20                              # ...and only if both people actually drew an arc

# ------------------------------------------------------------------ a drawn skeleton
class Drawn(object):
    def __init__(self, name, stops):
        self.name, self.stops = name, stops          # stops: [(energy, crowd), ...] over the WHOLE window
    @property
    def n(self): return len(self.stops)
    def at(self, frac):
        """the value the line holds at this fraction through the window. Midpoint sampling, not
        overlap-averaging: it preserves the drawn extremes, and a firm position is the thing that
        has to survive the merge."""
        k = min(self.n - 1, int(frac * self.n))
        return self.stops[k]

# ------------------------------------------------------------------ drawn firmness
def drawn_strength(v):
    """A SWIPED 50 means 'this card did nothing for me'. A DRAWN 50 means 'I want this stop at
    exactly medium'. So the skeleton has no true neutrals - that, and not a blanket multiplier, is
    what 'a drawn position is firmer than a swiped one' actually amounts to."""
    if v <= 20 or v >= 80: return 1.00
    if v <= 30 or v >= 70: return 0.75      # a swipe here is 0.5 unless it was fast; a drag is always deliberate
    return 0.25                             # a swiped neutral is 0.0; a drawn one still advocates

def contagion(values, axis):
    """CHEMISTRY_V4 section 0.3, run on drawn values instead of swiped ones."""
    base = sum(values) / len(values)
    hi = sum(drawn_strength(v) for v in values if v >= 70)
    lo = sum(drawn_strength(v) for v in values if v <= 30)
    mid = sum(drawn_strength(v) for v in values if 31 <= v <= 69)
    if hi == 0 and lo == 0: return base, 'nobody off the middle'
    d = DISCOUNT[axis]
    I_hi = (hi ** IMPACT_EXP) if hi else 0.0
    I_lo = ((lo ** IMPACT_EXP) * d) if lo else 0.0
    I_mid = (mid ** IMPACT_EXP) if mid else 0.0
    lead = 'high' if I_hi >= I_lo else 'low'
    I_lead, I_rest = (I_hi, I_lo + I_mid) if lead == 'high' else (I_lo, I_hi + I_mid)
    share = I_lead / (I_lead + I_rest) if (I_lead + I_rest) else 0.0
    side = [v for v in values if (v >= 70 if lead == 'high' else v <= 30)]
    peak = max(side) if lead == 'high' else min(side)
    lvl = base + PULL[axis] * share * (peak - base)
    return lvl, '%ss lead, share %.2f, mean %.0f' % (lead, share, base)

# ------------------------------------------------------------------ stage 1: the count
SIZE_CEILING = {1: 99, 2: 5, 3: 4, 4: 4, 5: 3}   # Steiner: getting five people out of a bar is
                                                 # not linear. 1 is uncapped (entry 202) - a solo
                                                 # drawer is capped by the window alone

def merge_count(drawings, ceiling):
    """A COUNT is a divisible quantity, so a split is split rather than won: nobody who drew a
    different number gets their own number back. This is ROAM's split-the-difference clamp, moved
    here from chemistry and applied to literal stops instead of a 0-100 axis."""
    ns = [d.n for d in drawings]
    lo_n, hi_n, mean = min(ns), max(ns), sum(ns) / float(len(ns))
    if lo_n == hi_n:
        return min(lo_n, ceiling), 'unanimous at %d' % lo_n
    hi = sum(1.0 for n in ns if n > mean); low = sum(1.0 for n in ns if n < mean)
    I_hi = hi ** IMPACT_EXP if hi else 0.0
    I_lo = low ** IMPACT_EXP if low else 0.0
    lead_hi = I_hi >= I_lo
    I_lead, I_rest = (I_hi, I_lo) if lead_hi else (I_lo, I_hi)
    share = I_lead / (I_lead + I_rest) if (I_lead + I_rest) else 0.0
    raw = mean + COUNT_PULL * share * ((hi_n if lead_hi else lo_n) - mean)
    # round to nearest, ties toward the plain mean - a tie must not be a windfall for the roamer
    n = int(math.floor(raw + 0.5)) if abs(raw - math.floor(raw) - 0.5) > 1e-9 else int(round(mean))
    note = 'drew %s -> %.2f' % ('/'.join(str(x) for x in ns), raw)
    if hi_n - lo_n >= 2:                                   # positions on both poles: the clamp bites
        n = min(max(n, lo_n + 1), hi_n - 1)
        note += ', clamped off both ends'
    if n > ceiling:
        n = ceiling; note += ', cut to %d by the window' % ceiling
    return n, note

# ------------------------------------------------------------------ stage 4: the arc
def pearson(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    if sa == 0 or sb == 0: return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)

def arcs_opposed(series):
    """A SHAPE IS NOT A QUANTITY. Half of a rising night and half of a falling night is not a
    compromise, it is a flat night neither person drew. So opposed arcs are not averaged."""
    names = list(series.keys())
    worst, pair = 1.0, None
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = series[names[i]], series[names[j]]
            if max(a) - min(a) < AMPLITUDE or max(b) - min(b) < AMPLITUDE: continue
            r = pearson(a, b)
            if r < worst: worst, pair = r, (names[i], names[j])
    return (worst < OPPOSED), worst, pair

# ------------------------------------------------------------------ the merge
def merge(drawings, window, ceiling=None, verbose=True):
    t0, t1 = window
    L = t1 - t0
    by_window = max(1, int(L // 1.5))                           # ~90 min a stop; the window is a hard filter
    by_size   = SIZE_CEILING.get(len(drawings), 3)
    ceiling   = ceiling if ceiling else min(by_window, by_size)
    N, cnote = merge_count(drawings, ceiling)
    # ---- stage 2: resample every drawing onto the merged clock
    slots = [(t0 + j * L / float(N), t0 + (j + 1) * L / float(N)) for j in range(N)]
    E = {d.name: [] for d in drawings}; C = {d.name: [] for d in drawings}
    for j in range(N):
        frac = (j + 0.5) / N
        for d in drawings:
            e, c = d.at(frac)
            E[d.name].append(e); C[d.name].append(c)
    # ---- stage 4 first: is the arc averagable at all?
    opposed, r, pair = arcs_opposed(E)
    notes = ['stops: ' + cnote]
    if opposed:
        amp = lambda nm: max(E[nm]) - min(E[nm])
        owner = max(E, key=lambda nm: amp(nm) * sum(drawn_strength(v) for v in E[nm]))
        E = {owner: E[owner]}; C = {owner: C[owner]}       # BOTH axes - a shape is one object
        notes.append('arcs opposed (r = %+.2f between %s and %s): the whole shape is taken from %s'
                     % (r, pair[0], pair[1], owner))
        notes.append('ASK, do not decide: two opposed arcs are the signal to offer TWO rooms, not one plan')
    # ---- stage 3: contagion per slot
    out = []
    for j in range(N):
        e, ew = contagion([E[nm][j] for nm in E], 'energy')
        c, cw = contagion([C[nm][j] for nm in C], 'crowd')
        out.append(dict(slot=j + 1, clock=slots[j], energy=e, crowd=c, ewhy=ew, cwhy=cw))
    if verbose:
        for n in notes: print('     . ' + n)
        for s in out:
            h0, h1 = s['clock']
            print('     stop %d  %02d:%02d-%02d:%02d   energy %3.0f  crowd %3.0f   (%s)'
                  % (s['slot'], int(h0) % 24, int((h0 % 1) * 60), int(h1) % 24, int((h1 % 1) * 60),
                     s['energy'], s['crowd'], s['ewhy']))
    return out, notes

# ============================================================ worked examples
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

head('1. THE COUNT - a divisible quantity is split, never won')
for ns, lbl in ([1, 4], 'Sana drew 1, Kabir drew 4'), ([1, 1, 4], 'two settlers and a roamer'), \
               ([3, 3, 1], 'two roamers and a settler'), ([1, 5], 'the widest gap'), \
               ([2, 2, 2], 'unanimous'), ([2, 3], 'one apart - no clamp needed'),                ([3, 3, 3, 1], 'THE BAD CASE: three drew 3, one drew 1'):
    ds = [Drawn('p%d' % i, [(50, 50)] * n) for i, n in enumerate(ns)]
    n, note = merge_count(ds, SIZE_CEILING.get(len(ds), 3))
    print('   %-34s -> %d stops   (%s)' % (lbl, n, note))

head('2. ALIGNMENT - a three-stop night and a two-stop night over the SAME window')
AARAV = Drawn('Aarav', [(45, 60), (70, 75), (88, 85)])       # builds across three
NITYA = Drawn('Nitya', [(40, 55), (52, 62)])                 # two calm stops
print('   Aarav drew 3 stops: ' + str(AARAV.stops))
print('   Nitya drew 2 stops: ' + str(NITYA.stops))
print('   window 20:00-02:00, so Nitya stop 1 covers 20:00-23:00 and spans two of the merged slots')
print()
merge([AARAV, NITYA], (20.0, 26.0))

head('3. THE FLATTENING CASE - one builds, one front-loads')
RISE = Drawn('Ishaan', [(35, 45), (60, 65), (90, 88)])
FALL = Drawn('Zoya',   [(88, 85), (60, 62), (30, 40)])
print('   Ishaan builds 35 -> 90; Zoya front-loads 88 -> 30. A plain average is flat at ~60,')
print('   which is a night neither of them drew.')
print()
merge([RISE, FALL], (20.0, 26.0))

head('4. THE SAME TWO, BUT ONE ARC IS TENTATIVE')
SOFT = Drawn('Zoya', [(62, 70), (55, 62), (48, 58)])          # amplitude 14: not really an arc
print('   Zoya now drifts 62 -> 48, an amplitude of 14. Below the threshold, so it averages.')
print()
merge([RISE, SOFT], (20.0, 26.0))

head('5. ONE DRAWER, THREE MEMBERS - no inference from cards, ever')
print('   Nitya and Zoya have not drawn. The merge counts DRAWERS ONLY, so the plan is Aarav\'s')
print('   shape and the card says so. Inferring their skeleton from their vibe cards is exactly')
print('   the inference the architecture removed.')
print()
merge([AARAV], (20.0, 26.0))

head('6. DRAWN VALUES MOVE MORE THAN SWIPED ONES - the measurable consequence')
def swiped_strength(v):
    if v <= 20 or v >= 80: return 1.0
    if v <= 30 or v >= 70: return 0.5
    return 0.0
import random
random.seed(5)
gaps = []
for _ in range(4000):
    vals = [min(100, max(0, int(random.gauss(50, 22)))) for _ in range(random.randint(2, 5))]
    base = sum(vals) / len(vals)
    def lvl(sf):
        hi = sum(sf(v) for v in vals if v >= 70); lo = sum(sf(v) for v in vals if v <= 30)
        mid = sum(sf(v) for v in vals if 31 <= v <= 69)
        if hi == 0 and lo == 0: return base
        I_hi = hi ** IMPACT_EXP if hi else 0.0
        I_lo = (lo ** IMPACT_EXP) * 0.55 if lo else 0.0
        I_mid = mid ** IMPACT_EXP if mid else 0.0
        lead = 'high' if I_hi >= I_lo else 'low'
        I_l, I_r = (I_hi, I_lo + I_mid) if lead == 'high' else (I_lo, I_hi + I_mid)
        sh = I_l / (I_l + I_r) if (I_l + I_r) else 0.0
        side = [v for v in vals if (v >= 70 if lead == 'high' else v <= 30)]
        pk = max(side) if lead == 'high' else min(side)
        return base + 0.75 * sh * (pk - base)
    gaps.append((abs(lvl(drawn_strength) - base), abs(lvl(swiped_strength) - base)))
md = sum(g[0] for g in gaps) / len(gaps); ms = sum(g[1] for g in gaps) / len(gaps)
print('   mean distance the level travels from the plain mean, over 4000 random rooms:')
print('      drawn  strengths (no true neutrals): %.2f points' % md)
print('      swiped strengths (neutrals at 0.0):  %.2f points' % ms)
print()
print('   Drawn rooms move LESS, not more (%.2f against %.2f). That is the right direction and it' % (md, ms))
print('   is worth stating plainly: giving the middle a real weight means the people who drew a')
print('   middling stop now COUNT AGAINST the one person who drew an extreme. "A drawn position is')
print('   firmer than a swiped one" holds per person - but a room full of firmer positions is a')
print('   room that compromises more, because the moderates stop being bystanders.')
