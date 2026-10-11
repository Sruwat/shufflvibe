# -*- coding: utf-8 -*-
"""CHEMISTRY V4 - contagion on the six going-out identity factors only.

V3 asked: what does this room want from a venue. V4 asks: who is this room - because the plan now
comes from the skeleton, not from the factors. Standalone; it does not import the 8-factor set."""
import random, math
from collections import namedtuple

IMPACT_EXP = 0.6      # Latane: impact grows as N^t, t<1 - the first person on a pole matters most
NEUTRAL_W  = 0.25     # a neutral is present but does not advocate

IDENT  = ['ENRG', 'AFFIL', 'TALK', 'FOCUS', 'MOVE', 'SPONT']
WEIGHT = dict(ENRG=18, AFFIL=16, TALK=14, FOCUS=14, MOVE=12, SPONT=10)

AXIS = {
 # pull, discount applied to the losing pole, and which pole leads on a tie
 'ENRG':  dict(pull=0.75, discount=0.55, dom='high'),   # arousal contagion (Barsade 2002)
 'TALK':  dict(pull=0.60, discount=0.50, dom='high'),   # a talker recruits (Thorne 1987; turn-taking)
 'MOVE':  dict(pull=0.70, discount=0.55, dom='high', splits=True),   # V4: mimicry applies, but it splits
 'FOCUS': dict(pull=0.80, discount=0.45, dom='high'),   # gaze following is reflexive (Frischen 2007)
 'SPONT': dict(pull=0.55, discount=0.50, dom='low'),    # V4: the ONLY axis that leads DOWN
 'AFFIL': dict(pull=0.00, discount=1.00, dom=None, splits=True),    # similar, not complementary
}

Member = namedtuple('Member', 'name vibe fast')

def mk(name, **kw):
    return Member(name, {f: kw.get(f, 50) for f in IDENT}, kw.get('fast', set()))

def strength(m, f, pole):
    s = m.vibe[f]
    if not ((s >= 70) if pole == 'high' else (s <= 30)):
        return 0.0
    if s >= 80 or s <= 20:
        return 1.0
    return 0.75 if f in m.fast else 0.5

def impact(members, f, pole, disc):
    tot = sum(strength(m, f, pole) for m in members)
    return (tot ** IMPACT_EXP) * disc if tot else 0.0

def axis_level(members, f):
    cfg  = AXIS[f]
    base = sum(m.vibe[f] for m in members) / len(members)
    if cfg['pull'] == 0.0:
        return base, 'no contagion on this axis'
    hi_raw = sum(strength(m, f, 'high') for m in members)
    lo_raw = sum(strength(m, f, 'low')  for m in members)
    if hi_raw == 0 and lo_raw == 0:
        return base, 'nobody leads'
    dom  = cfg['dom']
    I_hi = impact(members, f, 'high', cfg['discount'] if dom == 'low'  else 1.0)
    I_lo = impact(members, f, 'low',  cfg['discount'] if dom == 'high' else 1.0)
    neutrals = [m for m in members if 31 <= m.vibe[f] <= 69]
    I_n  = (len(neutrals) ** IMPACT_EXP) * NEUTRAL_W if neutrals else 0.0
    lead = 'high' if I_hi >= I_lo else 'low'
    I_lead, I_rest = (I_hi, I_lo + I_n) if lead == 'high' else (I_lo, I_hi + I_n)
    share = I_lead / (I_lead + I_rest) if (I_lead + I_rest) else 0.0
    side  = [m for m in members if strength(m, f, lead) > 0]
    peak  = max(m.vibe[f] for m in side) if lead == 'high' else min(m.vibe[f] for m in side)
    lvl   = base + cfg['pull'] * share * (peak - base)
    note  = '%ss lead (%.2f v %.2f, share %.2f)' % (lead, I_lead, I_rest, share)
    return lvl, note

def room(members, verbose=False):
    v, why, flags, x = {}, {}, [], []
    for f in IDENT:
        v[f], why[f] = axis_level(members, f)
    # an axis SPLITS when its two poles can be enacted at the same time in the same room:
    # some at the table while others work the room; some on the floor while others sit.
    splits = set()
    for f in IDENT:
        if not AXIS[f].get('splits'): continue
        if sum(strength(m, f, 'high') for m in members) > 0 and sum(strength(m, f, 'low') for m in members) > 0:
            splits.add(f)
    split = 'AFFIL' in splits
    if len(members) == 2 and not split:
        v['AFFIL'] = max(v['AFFIL'], 70)
        x.append('a pair reads AFFIL high whatever the scores (Simmel)')
    if 'MOVE' not in splits and v['MOVE'] >= 65:
        v['ENRG'] += 5
        x.append('a moving room is a rising room (+5 ENRG): synchrony raises arousal')
    if v['FOCUS'] >= 70:
        v['ENRG'] += 5
        x.append('a room pointed at one thing runs hotter (+5 ENRG): shared attention amplifies')
    if v['ENRG'] >= 75 and 'MOVE' not in splits and v['MOVE'] < 60:
        v['MOVE'] = min(60, v['MOVE'] + 5)
        x.append('a rising room gets on its feet (+5 MOVE, capped 60): a derived value must never win the name')
    if v['FOCUS'] >= 70: flags.append('wants a clock - one stop is anchored to an hour')
    if v['SPONT'] <= 30: flags.append('closed to late joins - this room wants to be settled')
    if v['SPONT'] >= 70: flags.append('open to joins right up to the hour')
    if 'AFFIL' in splits: flags.append('AFFIL split - two social halves; a joiner joins one of them')
    if 'MOVE'  in splits: flags.append('MOVE split - this room needs a floor AND somewhere to sit')
    if verbose:
        for f in IDENT:
            lab = 'split' if f in splits else '%.0f' % v[f]
            print('     %-6s %-6s  %s' % (f, lab, why[f]))
        for n in x:     print('     x ' + n)
        for n in flags: print('     ! ' + n)
    return v, splits, flags

# ============================================================ the per-axis tables
def P(f, *scores):
    return [mk('p%d' % i, **{f: s}) for i, s in enumerate(scores)]

def show(f, title, rows):
    print()
    print('-' * 98)
    print(title)
    print('-' * 98)
    for label, ms in rows:
        base = sum(m.vibe[f] for m in ms) / len(ms)
        lvl, _ = axis_level(ms, f)
        _, splits, _ = room(ms)
        out = 'SPLIT' if f in splits else '%3.0f' % lvl
        print('   %-56s mean %3.0f   reads %5s' % (label, base, out))

print('=' * 98)
print('CHEMISTRY V4 - the six identity axes, axis by axis')
print('=' * 98)

show('ENRG', 'ENRG   pull 0.75, low discounted to 0.55, leads high   [UNCHANGED from V3]', [
    ('two 88s, two neutrals (45, 50)',                 P('ENRG', 88, 88, 45, 50)),
    ('one 88, two firm 12s',                           P('ENRG', 88, 12, 12)),
    ('one 88, one firm 12',                            P('ENRG', 88, 12)),
])
show('TALK', 'TALK   pull 0.60, low discounted to 0.50, leads high   [level UNCHANGED, floor RETIRED]', [
    ('one firm talker (88), two low-talk (20, 20)',     P('TALK', 88, 20, 20)),
    ('one noise-wanter (12), two talkers (85, 82)',     P('TALK', 12, 85, 82)),
])
show('MOVE', 'MOVE   pull 0.70, low discounted to 0.55, leads high, AND IT SPLITS   [CHANGED]', [
    ('one dancer (88) + two neutrals (45, 50)',         P('MOVE', 88, 45, 50)),
    ('everybody dances (88, 85, 76)',                   P('MOVE', 88, 85, 76)),
    ('one dancer (88) + two firm lows (12, 20)',         P('MOVE', 88, 12, 20)),
    ('one dancer (88) + one firm low (12)',              P('MOVE', 88, 12)),
])
show('FOCUS', 'FOCUS  pull 0.80, low discounted to 0.45, leads high   [NEW - the strongest pull]', [
    ('one gig-goer (90) + two neutrals (45, 50)',       P('FOCUS', 90, 45, 50)),
    ('one gig-goer (90) + two firm lows (15, 20)',      P('FOCUS', 90, 15, 20)),
    ('two gig-goers (90, 82) + two firm lows',          P('FOCUS', 90, 82, 15, 20)),
    ('nobody focal (12, 18, 25)',                       P('FOCUS', 12, 18, 25)),
])
show('SPONT', 'SPONT  pull 0.55, high discounted to 0.50, leads LOW   [NEW - the only downward axis]', [
    ('one planner (12) + two neutrals (50, 55)',        P('SPONT', 12, 50, 55)),
    ('one planner (12) + two firm spontaneous (85, 90)', P('SPONT', 12, 85, 90)),
    ('one spontaneous (90) + two neutrals (45, 50)',    P('SPONT', 90, 45, 50)),
    ('everyone spontaneous (85, 88, 92)',               P('SPONT', 85, 88, 92)),
])
show('AFFIL', 'AFFIL  pull 0.00 - it does not spread, it splits   [UNCHANGED from V3]', [
    ('two table people (85, 82) + one room-facer (15)', P('AFFIL', 85, 82, 15)),
])
print('   AFFIL never produces a level when both poles are firmly present - it reports SPLIT.')

# ============================================================ a room, end to end
print()
print('=' * 98)
print('A ROOM, END TO END   - the same three people V3 was tested on, read as identity')
print('=' * 98)
AARAV = mk('Aarav', ENRG=84, AFFIL=38, TALK=45, FOCUS=72, MOVE=80, SPONT=88, fast={'ENRG'})
NITYA = mk('Nitya', ENRG=52, AFFIL=78, TALK=86, FOCUS=30, MOVE=35, SPONT=22)
ZOYA  = mk('Zoya',  ENRG=66, AFFIL=55, TALK=58, FOCUS=88, MOVE=62, SPONT=50)
for m in (AARAV, NITYA, ZOYA):
    print('   %-6s ' % m.name + '  '.join('%s %3d' % (f, m.vibe[f]) for f in IDENT))
print()
rv, splits, flags = room([AARAV, NITYA, ZOYA], verbose=True)

# ============================================================ match and disturbance
def halves(members, f):
    """the two poles' own means, for an axis that split."""
    hi = [m.vibe[f] for m in members if m.vibe[f] >= 70]
    lo = [m.vibe[f] for m in members if m.vibe[f] <= 30]
    return sum(hi) / len(hi), sum(lo) / len(lo)

def match(user, rv, members=None, splits=frozenset()):
    """how close is this person's identity to the room's - the People sort.
    On a split axis the room contains both poles and the joiner will join ONE of them, so they
    are matched against the nearer half rather than against a fictional average."""
    tot, d = sum(WEIGHT.values()), 0.0
    for f in IDENT:
        if f in splits and members:
            h, l = halves(members, f)
            gap = min(abs(user.vibe[f] - h), abs(user.vibe[f] - l))
        else:
            gap = abs(user.vibe[f] - rv[f])
        d += WEIGHT[f] * gap
    return 1.0 - (d / tot) / 100.0

def disturbance(user, members):
    """how much would this person move the room - the point-6 question.
    An axis that was ALREADY split cannot be disturbed further; an axis this person SPLITS is the
    largest disturbance there is, because the room stops having a position at all."""
    before, sp_b, _ = room(members)
    after,  sp_a, _ = room(list(members) + [user])
    tot, d = sum(WEIGHT.values()), 0.0
    for f in IDENT:
        if f in sp_b:      continue                      # already saturated - nothing left to move
        if f in sp_a:      d += WEIGHT[f] * SPLIT_COST    # they broke the axis in two
        else:              d += WEIGHT[f] * abs(after[f] - before[f])
    return d / tot / 100.0

SPLIT_COST = 35.0     # a newly split axis costs as much as a 35-point move: the room loses a position

print()
print('=' * 98)
print('POINT 6 - are the rooms I match also the rooms I would not change?')
print('=' * 98)
random.seed(7)
def rnd_person(i):
    return mk('u%d' % i, **{f: min(100, max(0, int(random.gauss(50, 22)))) for f in IDENT})

pairs = []
for trial in range(4000):
    ms = [rnd_person(i) for i in range(random.randint(2, 5))]
    u  = rnd_person(999)
    rv2, sp2, _ = room(ms)
    pairs.append((match(u, rv2, ms, sp2), disturbance(u, ms), len(ms)))

def pearson(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)

M = [p[0] for p in pairs]; D = [p[1] for p in pairs]
print('   correlation of match against disturbance, all room sizes:  r = %+.3f' % pearson(M, D))
for k in (2, 3, 4, 5):
    sub = [p for p in pairs if p[2] == k]
    print('      rooms of %d (n=%4d):                                r = %+.3f   mean disturbance %.3f'
          % (k, len(sub), pearson([p[0] for p in sub], [p[1] for p in sub]),
             sum(p[1] for p in sub) / len(sub)))

# ---- disturbance falls with room size (Latane at the room level). Normalise or the People sort
# will simply surface the biggest rooms.
SIZE_REF = {}
for k in (2, 3, 4, 5):
    sub = [p for p in pairs if p[2] == k]
    SIZE_REF[k] = sum(p[1] for p in sub) / len(sub)
print()
print('   raw disturbance by room size: ' + '  '.join('%d:%.3f' % (k, SIZE_REF[k]) for k in (2, 3, 4, 5)))
print('   a pair is transformed by a third person; a five absorbs a sixth. That is Latane again,')
print('   one level up - so the raw number is not comparable across room sizes.')
norm = [(m, d / SIZE_REF[k], k) for m, d, k in pairs]
print('   after dividing by the size mean:            r = %+.3f' % pearson([p[0] for p in norm], [p[1] for p in norm]))

# would sorting by one give you the other's top picks?
for lbl, data in (('raw', pairs), ('size-normalised', norm)):
    idx = list(range(len(data)))
    tm = set(sorted(idx, key=lambda i: -data[i][0])[:400])
    td = set(sorted(idx, key=lambda i:  data[i][1])[:400])
    print('   of the 400 best-matched rooms, how many are in the 400 least-disturbed (%-15s)  %3d  (%.0f%%)'
          % (lbl, len(tm & td), 100.0 * len(tm & td) / 400))

# ---- is an AFFIL-split room really the most volatile?
print()
print('   volatility check - mean disturbance a joiner causes:')
for lbl, pred in (('rooms with AFFIL split', True), ('rooms without', False)):
    vals = []
    random.seed(23)
    for trial in range(3000):
        ms = [rnd_person(i) for i in range(random.randint(2, 5))]
        _, sp, _ = room(ms)
        if ('AFFIL' in sp) != pred: continue
        vals.append(disturbance(rnd_person(999), ms))
    print('      %-26s n=%4d   mean disturbance %.3f' % (lbl, len(vals), sum(vals) / len(vals) if vals else 0))
