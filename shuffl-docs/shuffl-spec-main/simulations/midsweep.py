# -*- coding: utf-8 -*-
"""THE MID-BAND CHANGE, ACROSS 4,000 ROOMS.

Does letting a mid value advocate for its own side break anything? Measured against the same
quantities CHEMISTRY_V4 section 9 measured, so the numbers are comparable to what is already in
the spec.
"""
import sys, io, contextlib, random, math, collections
sys.stdout.reconfigure(encoding='utf-8')
with contextlib.redirect_stdout(io.StringIO()):
    import chem4 as C
import roomfit as RF

MID_W = 0.30
ORIG = C.strength


def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)


def strength2(m, f, pole):
    base = ORIG(m, f, pole)
    if base:
        return base
    s = m.vibe[f]
    if s == 50:
        return 0.0
    return MID_W if (('high' if s > 50 else 'low') == pole) else 0.0


def pearson(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if not sx or not sy: return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def rnd_person(rng):
    return C.mk('p', **{f: max(0, min(100, int(rng.gauss(50, 24)))) for f in C.IDENT})


def sweep(use_mid, split_on_firm=True, n=4000, seed=7):
    """Returns the measurements. split_on_firm keeps the split test on the FIRM threshold."""
    rng = random.Random(seed)
    C.strength = strength2 if use_mid else ORIG
    levels = collections.defaultdict(list)
    crashes = [0]
    matches, dists, heads, splits, sizes = [], [], collections.Counter(), 0, 0
    try:
        for _ in range(n):
            k = rng.choice([2, 3, 3, 4, 4, 5])
            members = [rnd_person(rng) for _ in range(k)]
            joiner = rnd_person(rng)
            with contextlib.redirect_stdout(io.StringIO()):
                rv, sp, _ = C.room(members)
                if split_on_firm:
                    # the split test must use the FIRM ladder even when advocacy does not.
                    # Recompute it here rather than taking it from a room() that used strength2 -
                    # taking it from two separate calls also corrupted the AFFIL pair rule, which
                    # branches on `split` inside room().
                    sp = set()
                    for f in C.IDENT:
                        if not C.AXIS[f].get('splits'):
                            continue
                        if (sum(ORIG(m2, f, 'high') for m2 in members) > 0
                                and sum(ORIG(m2, f, 'low') for m2 in members) > 0):
                            sp.add(f)
                    if len(members) == 2 and 'AFFIL' not in sp:
                        rv['AFFIL'] = max(rv['AFFIL'], 70)
                try:
                    m = C.match(joiner, rv, members, sp)
                    d = C.disturbance(joiner, members)
                except ZeroDivisionError:
                    crashes[0] += 1
                    continue
            for f in C.IDENT:
                levels[f].append(rv[f])
            matches.append(m); dists.append(d); splits += 1 if sp else 0; sizes += k
            mb = RF.band(m, RF.MATCH_HI, RF.MATCH_LO)
            db = RF.band(d, RF.DIST_HI, RF.DIST_LO)
            heads['SPLIT' if sp else '%s/%s' % (mb, db)] += 1
    finally:
        C.strength = ORIG
    return dict(levels=levels, matches=matches, dists=dists, heads=heads,
                splits=splits, n=len(matches), meansize=sizes / float(n), crashes=crashes[0])


head('A.  4,000 ROOMS, EACH MEASURED BOTH WAYS')
A = sweep(False)
B = sweep(True)
print('   rooms %d, mean size %.1f, one random joiner each' % (A['n'], A['meansize']))
print()
print('   %-10s %10s %10s %9s' % ('axis', 'now', 'proposed', 'shift'))
line()
for f in C.IDENT:
    a = sum(A['levels'][f]) / A['n']; b = sum(B['levels'][f]) / B['n']
    print('   %-10s %10.1f %10.1f %+9.1f' % (f, a, b, b - a))
line()
print('   %-28s %10.3f %10.3f' % ('mean match', sum(A['matches']) / A['n'], sum(B['matches']) / B['n']))
print('   %-28s %10.3f %10.3f' % ('mean disturbance', sum(A['dists']) / A['n'], sum(B['dists']) / B['n']))
print('   %-28s %10.3f %10.3f' % ('r(match, disturbance)',
                                  pearson(A['matches'], A['dists']), pearson(B['matches'], B['dists'])))
print('   %-28s %10d %10d' % ('rooms with a split', A['splits'], B['splits']))

head('B.  THE HEADLINE DISTRIBUTION - does the read skew?')
keys = sorted(set(A['heads']) | set(B['heads']))
print('   %-14s %10s %10s %9s' % ('headline band', 'now', 'proposed', 'shift'))
line()
for k in keys:
    a, b = A['heads'][k], B['heads'][k]
    print('   %-14s %10d %10d %+9d' % (k, a, b, b - a))
line()

head('C.  WHAT HAPPENS IF THE SPLIT TEST IS NOT HELD BACK')
print("""
  `room()` decides a split with the same `strength` call it uses for advocacy. If the mid band is
  allowed to advocate AND to split, then one person at 62 and one at 38 on the same axis makes a
  split - which is not what a split means. A split is both poles being ENACTED in one room, and a
  mild lean does not enact anything.
""")
D = sweep(True, split_on_firm=False, n=1500)
A2 = sweep(False, n=1500)
print('   rooms with a split, out of 1,500')
print('      now                                  %5d   (%.0f%%)' % (A2['splits'], 100.0 * A2['splits'] / 1500))
print('      proposed, split test held at 70/30   %5d   (%.0f%%)'
      % (round(B['splits'] * 1500.0 / 4000), 100.0 * B['splits'] / 4000))
print('      proposed, split test NOT held back   %5d   of the %d rooms that survived'
      % (D['splits'], D['n']))
print()
print('   AND THAT IS NOT THE HEADLINE. It crashes match() outright:')
print('      rooms where match() divided by zero  %5d of 1500  (%.0f%%)'
      % (D['crashes'], 100.0 * D['crashes'] / 1500))
print()
print('''   `halves()` averages the members at each pole of a split axis. A split declared from mid-band
   leans has NOBODY at >= 70 or <= 30, so it divides by an empty list. **The naive one-function
   patch does not merely mis-model a split - it breaks the People sort in three rooms out of four.**''')
line()
print("""
  **So the change has to be made in two places, not one.** `strength()` gains the mid band for
  ADVOCACY; the split test keeps the firm 70/30 threshold. Patching one function does both and
  the second one is wrong.
""")

head('D.  THE SIDE EFFECT THAT HAS TO BE FIXED WITH IT')
print("""
  Rooms get harder to move, because mid people now count as advocates and stiffen the room. Mean
  disturbance falls about 15%, and the bands in `roomfit.py` were set against the OLD distribution -
  so the headline collapses toward one answer unless they are re-cut.
""")


def terciles(xs):
    s = sorted(xs); n = len(s)
    return s[n // 3], s[2 * n // 3]

a_lo, a_hi = terciles(A['dists'])
b_lo, b_hi = terciles(B['dists'])
print('   %-34s %10s %10s' % ('', 'now', 'proposed'))
line()
print('   %-34s %10.3f %10.3f' % ('disturbance, lower tercile', a_lo, b_lo))
print('   %-34s %10.3f %10.3f' % ('disturbance, upper tercile', a_hi, b_hi))
print('   %-34s %10s %10s' % ('thresholds in roomfit.py today', '0.070', '0.100'))
line()
nons = A['n'] - A['splits']
for tag, S in (('now', A), ('proposed, old bands', B)):
    lo = sum(v for k, v in S['heads'].items() if k != 'SPLIT' and k.endswith('/lo'))
    tot = sum(v for k, v in S['heads'].items() if k != 'SPLIT')
    print('   %-34s %5d of %d non-split reads say "you would barely change this room"  (%.0f%%)'
          % (tag, lo, tot, 100.0 * lo / tot))
rb = sum(1 for d_ in B['dists'] if d_ < b_lo)
print('   %-34s %5d of %d                                                   (%.0f%%)'
      % ('proposed, bands re-cut at terciles', rb, B['n'], 100.0 * rb / B['n']))
line()
print("""
  **Re-cutting the bands at the new terciles restores the spread.** Without it, more than half of
  all reads would open with the same sentence - which is the headline losing the thing it was for.
""")
