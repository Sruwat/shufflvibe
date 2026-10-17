# -*- coding: utf-8 -*-
"""DO FOUR BANDS DISCRIMINATE?

The build-my-own meter set is four meters - ENERGY, CROWD, TALK, ON YOUR FEET - each drawn as a
SPAN across the night's stops, as a BAND rather than a number, and HOLLOW when the value came from
the venue's type rather than from its reviews (entries 190 and 196).

**A first version of this file asked whether two independently generated nights ever render the
same meter block. They never do - the block is eight quantised numbers - so the answer was 0% in
every condition and told us nothing.** The question that matters is not whether two nights collide.
It is whether the reading MOVES WHEN IT SHOULD and STAYS STILL WHEN IT SHOULD:

  A. How often is the hollow mark on? A mark that is always on is a label, not a mark.
  B. BLINDNESS - swap one stop for a venue of a different kind. How often does nothing change?
  C. JITTER    - swap one stop for an equivalent venue of the same kind. How often does it change
                 anyway? A display that moves for no reason reads as arbitrary.
  D. Span against mean, and what CROWD's 22:00 split buys, on both measures.
  E. Would FOCUS as a fifth meter reduce blindness?
  F. Band resolution - the blindness/jitter trade, which is what quantisation really is.

Standard library only. Synthetic venues from the type priors the pipeline already uses.
"""
import sys, random, statistics as st
sys.stdout.reconfigure(encoding='utf-8')

# (ENRG, CROWD_early, CROWD_late, TALK, MOVE, FOCUS)
TYPES = {
    'cafe':             (25, 40, 22, 80, 10, 10),
    'restaurant':       (38, 52, 38, 72,  8, 12),
    'buzzy restaurant': (55, 58, 66, 50, 12, 15),
    'pub':              (58, 45, 70, 52, 25, 30),
    'bar':              (68, 42, 78, 38, 40, 20),
    'big loud bar':     (80, 44, 88, 22, 60, 15),
    'live room':        (70, 50, 78, 30, 45, 92),
    'night club':       (90, 30, 92, 10, 88, 25),
}
EARLY = ['cafe', 'restaurant', 'buzzy restaurant', 'pub']
LATE = ['pub', 'bar', 'big loud bar', 'live room', 'night club']

VENUE_SD = 12.0            # venue-to-venue spread plus the lexicon's own error
PRIOR_WEIGHT = 6.0         # pipeline.py: w = n / (n + 6)
CUT = 22                   # entry 196: CROWD's slot boundary
QUANT = 10                 # how finely a person can read a band on a 300px phone
HITS = {'ENRG': 9.0, 'CROWD': 7.0, 'TALK': 4.0, 'MOVE': 2.5, 'FOCUS': 1.0}
METERS = ['ENRG', 'CROWD', 'TALK', 'MOVE']


def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)


def poisson(rng, lam):
    L, k, p = pow(2.718281828459045, -lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L: return k
        k += 1


def make_venue(rng, kind):
    e, ce, cl, t, m, f = TYPES[kind]
    v = dict(kind=kind)
    for key, base in (('ENRG', e), ('CROWD_e', ce), ('CROWD_l', cl),
                      ('TALK', t), ('MOVE', m), ('FOCUS', f)):
        v[key] = max(2, min(98, base + rng.gauss(0, VENUE_SD)))
    v['hits'] = {}
    for fac, lam in HITS.items():
        lam2 = 15.0 if (fac == 'FOCUS' and kind == 'live room') else lam
        v['hits'][fac] = poisson(rng, lam2)
    return v


def crowd_at(v, hour, split=True):
    if not split:
        return (v['CROWD_e'] + v['CROWD_l']) / 2.0
    return v['CROWD_l'] if hour >= CUT else v['CROWD_e']


def val(v, hour, fac, split=True):
    return crowd_at(v, hour, split) if fac == 'CROWD' else v[fac]


def make_night(rng, n=None):
    n = n or rng.choice([2, 3, 3, 4])
    start = rng.choice([20, 21])
    return [(start + 2 * i, make_venue(rng, rng.choice(EARLY if start + 2 * i < CUT else LATE)))
            for i in range(n)]


def block(stops, facs=METERS, split=True, quant=QUANT, use_span=True):
    out = []
    for f in facs:
        vals = [val(v, h, f, split) for h, v in stops]
        if use_span:
            out.append((round(min(vals) / quant), round(max(vals) / quant)))
        else:
            out.append(round(st.mean(vals) / quant))
    return tuple(out)


def swap(rng, stops, i, same_kind):
    h, old = stops[i]
    if same_kind:
        kind = old['kind']
    else:
        pool = [k for k in (EARLY if h < CUT else LATE) if k != old['kind']]
        kind = rng.choice(pool)
    out = list(stops)
    out[i] = (h, make_venue(rng, kind))
    return out


def stop_gap(a, b, i):
    """how far the swapped stop actually moved, on the four meters"""
    (ha, va), (hb, vb) = a[i], b[i]
    return st.mean([abs(val(va, ha, f) - val(vb, hb, f)) for f in METERS])


# =========================================================== A. the hollow mark
head('A.  THE HOLLOW MARK - how often is it on?')
rng = random.Random(11)
N = 8000
hollow = {f: 0 for f in METERS + ['FOCUS']}
for _ in range(N):
    v = make_venue(rng, rng.choice(list(TYPES)))
    for f in METERS + ['FOCUS']:
        w = v['hits'][f] / (v['hits'][f] + PRIOR_WEIGHT)
        if w < 0.5:
            hollow[f] += 1
print('   %d synthetic venues at five reviews each. HOLLOW = the type prior carries more than half' % N)
print('   the weight, i.e. fewer than %d keyword hits.' % int(PRIOR_WEIGHT))
line()
for f in METERS + ['FOCUS']:
    pc = 100.0 * hollow[f] / N
    print('   %-8s %5.0f%% hollow   %s' % (f, pc, '#' * int(pc / 2.5)))
line()

# =========================================================== B & C. blindness and jitter
def measure(rng_seed, facs=METERS, split=True, quant=QUANT, use_span=True, trials=30000):
    rng = random.Random(rng_seed)
    blind_n = blind_hit = 0
    jit_n = jit_hit = 0
    by_gap = {}
    for _ in range(trials):
        night = make_night(rng)
        i = rng.randrange(len(night))
        # a genuinely different venue in that slot
        other = swap(rng, night, i, same_kind=False)
        g = stop_gap(night, other, i)
        same = block(night, facs, split, quant, use_span) == block(other, facs, split, quant, use_span)
        blind_n += 1; blind_hit += 1 if same else 0
        b = min(int(g // 10) * 10, 40)
        d = by_gap.setdefault(b, [0, 0]); d[0] += 1; d[1] += 1 if same else 0
        # an equivalent venue of the same kind
        eq = swap(rng, night, i, same_kind=True)
        jit_n += 1
        if block(night, facs, split, quant, use_span) != block(eq, facs, split, quant, use_span):
            jit_hit += 1
    return (100.0 * blind_hit / blind_n, 100.0 * jit_hit / jit_n, by_gap)


head('B.  BLINDNESS - one stop swapped for a venue of a DIFFERENT kind')
blind, jitter, by_gap = measure(4)
print('   30,000 swaps. "Blind" = the whole meter block renders identically afterwards.')
line()
print('   %-30s %10s %12s' % ('how far that stop moved', 'swaps', 'blind'))
for b in sorted(by_gap):
    n, h = by_gap[b]
    if n < 60: continue
    lbl = '%d-%d points' % (b, b + 10) if b < 40 else '40+ points'
    print('   %-30s %10d %11.1f%%' % (lbl, n, 100.0 * h / n))
line()
print('   overall blind rate: %.1f%%' % blind)

head('C.  JITTER - one stop swapped for an EQUIVALENT venue of the same kind')
line()
print('   the block changes anyway: %.1f%% of swaps' % jitter)
line()
print('   (a different bar, same kind of bar. The night a person would describe has not changed.)')

# =========================================================== D. encodings
head('D.  SPAN AGAINST MEAN, AND WHAT CROWD\'S 22:00 SPLIT BUYS')
line()
print('   %-36s %10s %10s' % ('encoding', 'blind', 'jitter'))
line()
for name, kw in (('span, CROWD split      (shipped)', dict(use_span=True, split=True)),
                 ('span, CROWD single value', dict(use_span=True, split=False)),
                 ('mean, CROWD split', dict(use_span=False, split=True)),
                 ('mean, CROWD single value', dict(use_span=False, split=False))):
    b, j, _ = measure(4, **kw)
    print('   %-36s %9.1f%% %9.1f%%' % (name, b, j))
line()

# =========================================================== E. FOCUS as a fifth
head('E.  FOCUS AS A FIFTH METER')
line()
print('   %-36s %10s %10s' % ('', 'blind', 'jitter'))
for facs, label in ((METERS, 'four meters (shipped)'), (METERS + ['FOCUS'], 'five, with FOCUS')):
    b, j, _ = measure(4, facs=facs)
    print('   %-36s %9.1f%% %9.1f%%' % (label, b, j))
line()

# =========================================================== F. resolution
head('F.  BAND RESOLUTION - the blindness / jitter trade')
line()
print('   %-36s %10s %10s' % ('quantisation', 'blind', 'jitter'))
line()
for q in (5, 10, 15, 20, 25):
    b, j, _ = measure(4, quant=q)
    print('   %-36s %9.1f%% %9.1f%%' % ('%d points (%d steps)' % (q, 100 // q), b, j))
line()

# =========================================================== G. the word, not the band
WORDS = ('low', 'mid', 'high')


def lvl(x):
    return 0 if x < 35 else (1 if x <= 65 else 2)


def words(stops, split=True):
    """What the right-hand column says. The band is the detail; this is what a person reads."""
    out = []
    for f in METERS:
        vals = [val(v, h, f, split) for h, v in stops]
        out.append((lvl(min(vals)), lvl(max(vals))))
    return tuple(out)


head('G.  THE WORD, NOT THE BAND - is the phrase steadier than the bar?')
rng = random.Random(9)
wb_n = wb_hit = wj_n = wj_hit = 0
for _ in range(30000):
    night = make_night(rng)
    i = rng.randrange(len(night))
    other = swap(rng, night, i, same_kind=False)
    wb_n += 1
    if words(night) == words(other):
        wb_hit += 1
    eq = swap(rng, night, i, same_kind=True)
    wj_n += 1
    if words(night) != words(eq):
        wj_hit += 1
line()
print('   %-36s %10s %10s' % ('', 'blind', 'jitter'))
print('   %-36s %9.1f%% %9.1f%%' % ('the band (10-point steps)', 6.5, 89.5))
print('   %-36s %9.1f%% %9.1f%%' % ('the word (low / mid / high)',
                                     100.0 * wb_hit / wb_n, 100.0 * wj_hit / wj_n))
line()

# =========================================================== H. what the span actually buys
head('H.  WHAT THE SPAN ACTUALLY BUYS - direction, or range?')
rng = random.Random(21)
same_span = same_mean = same_arc = 0
rng2 = random.Random(22)
narrow_vs_wide_span = narrow_vs_wide_mean = 0
T = 20000
for _ in range(T):
    night = make_night(rng, 3)
    rev = [(h, v) for (h, _), (_, v) in zip(night, reversed(night))]   # same venues, reversed order
    if block(night) == block(rev):
        same_span += 1
    if block(night, use_span=False) == block(rev, use_span=False):
        same_mean += 1
    arc_a = [round(st.mean([val(v, h, f) for f in METERS])) for h, v in night]
    arc_b = [round(st.mean([val(v, h, f) for f in METERS])) for h, v in rev]
    if arc_a == arc_b:
        same_arc += 1
line()
print('   %d nights, each against its own time-reversal (the SAME venues, opposite order):' % T)
print('   %-40s %10s' % ('', 'renders alike'))
print('   %-40s %9.1f%%' % ('the span', 100.0 * same_span / T))
print('   %-40s %9.1f%%' % ('the mean', 100.0 * same_mean / T))
print('   %-40s %9.1f%%' % ('the arc sparkline', 100.0 * same_arc / T))
line()

# a flat night against a night with the same mean but a wide range
flat_hit_span = flat_hit_mean = flat_n = 0
for _ in range(T):
    a = make_night(rng2, 3)
    b = make_night(rng2, 3)
    ma = [st.mean([val(v, h, f) for h, v in a]) for f in METERS]
    mb = [st.mean([val(v, h, f) for h, v in b]) for f in METERS]
    if max(abs(x - y) for x, y in zip(ma, mb)) > 6:
        continue                                  # keep only pairs with near-identical means
    ra = [max(val(v, h, f) for h, v in a) - min(val(v, h, f) for h, v in a) for f in METERS]
    rb = [max(val(v, h, f) for h, v in b) - min(val(v, h, f) for h, v in b) for f in METERS]
    if max(abs(x - y) for x, y in zip(ra, rb)) < 25:
        continue                                  # ...and clearly different ranges
    flat_n += 1
    flat_hit_span += 1 if block(a) == block(b) else 0
    flat_hit_mean += 1 if block(a, use_span=False) == block(b, use_span=False) else 0
print('   nights with near-identical MEANS but clearly different RANGES  (%d pairs):' % flat_n)
print('   %-40s %9.1f%%' % ('the span renders them alike', 100.0 * flat_hit_span / max(1, flat_n)))
print('   %-40s %9.1f%%' % ('the mean renders them alike', 100.0 * flat_hit_mean / max(1, flat_n)))
line()

head('WHAT THIS SETTLES')
print("""
  1. **The hollow mark works on two rows and is a constant on a third.** ENERGY is hollow 12% of the
     time and CROWD 30% - there the mark carries information. **ON YOUR FEET is hollow 96% of the
     time**, which is not a mark, it is a label, and its constancy makes the other rows' hollowness
     harder to notice. Either **widen the MOVE keyword list** - the fix the Kwality test forced on
     HERIT and SCEN, both of which went from unusable to usable by being written in the words people
     actually use - or **suppress the mark on that row and say it once in the footer**.

  2. **The band is sensitive and noisy; the word is stable and blunt.** A genuine venue swap leaves
     the band unchanged 6.5% of the time and the word unchanged 28.8%. An *equivalent* swap - a
     different bar of the same kind - moves the band 89.5% of the time and the word 51%.
     **Keeping both is right, and now for a measured reason**: the band is the detail and moves for
     almost anything, the word is the headline and holds still for a night of the same character.

  3. **The span was adopted for the wrong stated reason and is still the right choice.** The record
     says it exists because *the mean of a rising night equals the mean of a falling one*. **A
     min-max span cannot see direction either** - it is order-invariant on everything but CROWD.
     What the span actually buys is **range**: on nights with near-identical means and clearly
     different ranges, **the mean renders them alike 20.6% of the time and the span never does**.
     **Direction is carried by the arc and only by the arc** - reversing a night changes the arc
     99.9% of the time. The sparkline is load-bearing, not decoration.

  4. **FOCUS as a fifth meter cuts blindness from 6.5% to 2.0%** - a bigger gain than expected - at
     94.6% jitter and a row that would be **hollow 88% of the time**. It buys sensitivity by adding
     a mostly-guessed row. The badge stays, but this is now a judgement with a number against it.

  5. **Ten-point bands sit where the curve bends.** Five points: 4.6% blind, 92.9% jitter. Twenty-
     five: 14.2% blind, 75.9% jitter. There is no free lunch in the resolution, only the trade.
""")
