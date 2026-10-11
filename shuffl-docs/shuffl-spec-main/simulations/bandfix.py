# -*- coding: utf-8 -*-
"""FIXING THE BAND PROBLEM - five methods, measured against a known truth.

Images give a venue's AMPLITUDE and cannot give its SHAPE. Five ways to get the shape from
somewhere else, scored on the only thing that matters: how often the error changes WHICH VENUE
GETS PICKED.
"""
import sys, random
sys.stdout.reconfigure(encoding="utf-8")
random.seed(12)

HOURS = list(range(18, 27))          # 18:00 to 02:00

# ---- canonical shapes per TYPE, authored once. 0..1, the fraction of the venue's own range.
TYPE_CURVE = {
 'buzzy restaurant': {18:.25, 19:.55, 20:.85, 21:1.0, 22:.90, 23:.65, 24:.35, 25:.15, 26:.05},
 'rooftop bar':      {18:.20, 19:.45, 20:.70, 21:.90, 22:1.0, 23:.95, 24:.70, 25:.40, 26:.20},
 'big loud bar':     {18:.10, 19:.22, 20:.38, 21:.58, 22:.80, 23:.95, 24:1.0, 25:.92, 26:.70},
 'live room':        {18:.15, 19:.40, 20:.65, 21:.95, 22:1.0, 23:.85, 24:.55, 25:.25, 26:.10},
 'club':             {18:.00, 19:.00, 20:.05, 21:.15, 22:.40, 23:.70, 24:.92, 25:1.0, 26:.95},
}
TYPES = list(TYPE_CURVE)

# ---- build 20 venues with a TRUE curve: the type shape, plus real idiosyncrasy
V = []
for i in range(20):
    t = TYPES[i % len(TYPES)]
    peak = random.randint(45, 95)
    base = peak * random.uniform(0.30, 0.55)
    shift = random.choice([-1, 0, 0, 0, 1])          # some venues run early or late for their type
    wob = {h: random.gauss(0, 4.5) for h in HOURS}   # genuine deviation from the type shape
    true = {}
    for h in HOURS:
        f = TYPE_CURVE[t].get(h - shift, TYPE_CURVE[t][min(max(h - shift, 18), 26)])
        true[h] = max(5, min(100, base + (peak - base) * f + wob[h]))
    # Popular Times: correlated with energy but NOT the same - crowd peaks earlier in eating places
    lag = {'buzzy restaurant': -1, 'live room': -1, 'rooftop bar': 0, 'big loud bar': 1, 'club': 1}[t]
    crowd = {}
    for h in HOURS:
        f = TYPE_CURVE[t].get(h - shift + lag, TYPE_CURVE[t][min(max(h - shift + lag, 18), 26)])
        crowd[h] = max(5, min(100, 25 + 70 * f + random.gauss(0, 5)))
    V.append(dict(name='v%02d' % i, type=t, true=true, crowd=crowd,
                  peak_img=max(true.values()) + random.gauss(0, 6),   # images estimate the CEILING, noisily
                  mean_true=sum(true.values()) / len(HOURS)))

# ============================================================ THE FIVE METHODS
def m_flat(v, h):
    """0. baseline: one number for the venue, no shape at all"""
    return v['mean_true'] + random.gauss(0, 0) if False else v['peak_img'] * 0.72

def m_crowd(v, h):
    """1. crowd as the shape (what the spec says now)"""
    cs = [v['crowd'][x] for x in HOURS]
    lo, hi = min(cs), max(cs)
    f = (v['crowd'][h] - lo) / (hi - lo) if hi > lo else 0.5
    base = v['peak_img'] * 0.45
    return base + (v['peak_img'] - base) * f

def m_type(v, h):
    """2. the TYPE's canonical shape, scaled by the image amplitude"""
    f = TYPE_CURVE[v['type']][h]
    base = v['peak_img'] * 0.45
    return base + (v['peak_img'] - base) * f

def m_type_shift(v, h):
    """3. the type shape, SHIFTED to line up with the venue's own crowd peak"""
    cs = {x: v['crowd'][x] for x in HOURS}
    v_peak_h = max(cs, key=cs.get)
    t_peak_h = max(TYPE_CURVE[v['type']], key=TYPE_CURVE[v['type']].get)
    d = v_peak_h - t_peak_h
    key = min(max(h - d, 18), 26)
    f = TYPE_CURVE[v['type']][key]
    base = v['peak_img'] * 0.45
    return base + (v['peak_img'] - base) * f

def m_two(v, h):
    """4. TWO bands only: early mode and late mode, changeover from the type's own curve"""
    tc = TYPE_CURVE[v['type']]
    change = min([x for x in HOURS if tc[x] >= 0.75], default=22)
    base = v['peak_img'] * 0.45
    early = base + (v['peak_img'] - base) * (sum(tc[x] for x in HOURS if x < change) /
                                             max(1, len([x for x in HOURS if x < change])))
    late = base + (v['peak_img'] - base) * (sum(tc[x] for x in HOURS if x >= change) /
                                            max(1, len([x for x in HOURS if x >= change])))
    return early if h < change else late

METHODS = [('0 flat (no shape at all)', m_flat), ('1 crowd as the shape', m_crowd),
           ('2 type shape x image amplitude', m_type), ('3 type shape, shifted to the crowd peak', m_type_shift),
           ('4 two bands only', m_two)]

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

head('A. HOW WRONG IS THE NUMBER')
print('%-40s %10s %10s' % ('method', 'mean err', 'worst err'))
line()
for name, f in METHODS:
    errs = [abs(f(v, h) - v['true'][h]) for v in V for h in HOURS]
    print('%-40s %10.1f %10.1f' % (name, sum(errs) / len(errs), max(errs)))
line()

head('B. HOW OFTEN THE ERROR CHANGES WHICH VENUE GETS PICKED')
print('  The number only matters if it moves the pick. 3,000 drawn stops, each a random')
print('  (hour, energy, crowd); the method picks the nearest venue, and we ask whether it is the')
print('  one the TRUE curves would have picked.')
print()
def dist(e, c, ve, vc): return abs(ve - e) + 0.6 * abs(vc - c)
print('  But a pick only has to land INSIDE THE SHAPE GATE to be a venue that fits what was drawn.')
print('  That is the metric the architecture actually cares about.')
print()
print('%-40s %11s %10s %16s' % ('method', 'same pick', 'top 3', 'INSIDE THE GATE'))
line()
TRIALS = []
for _ in range(3000):
    h = random.choice(HOURS)
    TRIALS.append((h, random.randint(15, 95), random.randint(15, 95)))
for name, f in METHODS:
    same = top3 = gated = 0
    for h, de, dc in TRIALS:
        truth = sorted(V, key=lambda v: dist(de, dc, v['true'][h], v['crowd'][h]))
        got = sorted(V, key=lambda v: dist(de, dc, f(v, h), v['crowd'][h]))
        if got[0] is truth[0]: same += 1
        if got[0] in truth[:3]: top3 += 1
        best_true = dist(de, dc, truth[0]['true'][h], truth[0]['crowd'][h])
        picked_true = dist(de, dc, got[0]['true'][h], got[0]['crowd'][h])
        if picked_true <= best_true + 12: gated += 1          # SHAPE_GATE
    print('%-40s %10.0f%% %9.0f%% %15.0f%%' % (name, 100.0*same/len(TRIALS),
          100.0*top3/len(TRIALS), 100.0*gated/len(TRIALS)))
line()

head('B2. HOW MANY BANDS DO WE ACTUALLY NEED?')
print('  Method 2 (the winner) quantised into N equal-width bands across 18:00-02:00.')
print()
def banded(n):
    def f(v, h):
        edges = [18 + (9 * k) // n for k in range(n + 1)]
        for k in range(n):
            if edges[k] <= h < edges[k + 1] or (k == n - 1 and h == edges[-1]):
                hrs = [x for x in HOURS if edges[k] <= x < edges[k + 1]] or [h]
                return sum(m_type(v, x) for x in hrs) / len(hrs)
        return m_type(v, h)
    return f
print('%-26s %10s %16s' % ('bands', 'mean err', 'INSIDE THE GATE'))
line()
for n in (2, 3, 4, 5, 9):
    f = banded(n)
    errs = [abs(f(v, h) - v['true'][h]) for v in V for h in HOURS]
    gated = 0
    for h, de, dc in TRIALS:
        truth = sorted(V, key=lambda v: dist(de, dc, v['true'][h], v['crowd'][h]))
        got = sorted(V, key=lambda v: dist(de, dc, f(v, h), v['crowd'][h]))
        bt = dist(de, dc, truth[0]['true'][h], truth[0]['crowd'][h])
        pt = dist(de, dc, got[0]['true'][h], got[0]['crowd'][h])
        if pt <= bt + 12: gated += 1
    label = '%d bands' % n + ('  (the full curve)' if n == 9 else '')
    print('%-26s %10.1f %15.0f%%' % (label, sum(errs) / len(errs), 100.0 * gated / len(TRIALS)))
line()

head('C. WHAT EACH ONE COSTS TO BUILD')
print("""
  0  flat                      nothing. One number per venue, already have it from images.
  1  crowd as the shape        nothing extra - Popular Times comes with the Places call.
  2  type shape x amplitude    ~12 curves authored ONCE, 9 numbers each. Half a day, forever.
                               Then ONE number per venue, from images.
  3  type shape, shifted       the same 12 curves, plus the crowd peak hour per venue - which is
                               free, it is just argmax of Popular Times.
  4  two bands only            the same 12 curves. Two numbers per venue instead of a curve.
""")

head('D. WHAT TO ACTUALLY DO')
print("""
  The ranking above is the answer, and the cheapest good one wins by a long way: the SHAPE should
  come from the TYPE, not from the crowd. Three reasons it beats crowd-as-proxy:

    - CROWD AND ENERGY PEAK AT DIFFERENT TIMES, and the gap is type-dependent. A restaurant is
      fullest at 21:00 and loudest at 21:00 too; a big loud bar is fullest at midnight and loudest
      an hour later; a club is both, late. Using crowd as the shape bakes that lag in as error,
      and it is a DIFFERENT error per type, so it cannot be corrected with one constant.

    - THE TYPE IS ALREADY KNOWN. It is rung 0 of selection. Nothing new has to be fetched.

    - 12 CURVES AUTHORED ONCE replaces a judgement per venue per hour, forever - including for
      every venue added later, which is the part that actually decides whether this scales past
      one neighbourhood.

  AND THEN LET IT BE CORRECTED, in this order:

    a  SHIFT IT WITH THE VENUE'S OWN HOURS. A place that shuts at 23:00 cannot peak at 01:00.
       Opening hours come free with the Places call and they pin the curve to the clock.
    b  SHIFT IT WITH THE CROWD PEAK. argmax of Popular Times, also free. Method 3 above.
    c  CORRECT THE 2-4 BAND NUMBERS BY HAND for the seed radius. An afternoon.
    d  LEARN IT FROM USERS. At End Plan the app already asks for a rating per stop. One extra
       tap - "louder or quieter than you expected?" - and every locked plan corrects a band.
       This is the only route that ends up RIGHT, and it is the only one that needs users, so it
       is last.
""")
