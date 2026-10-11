# -*- coding: utf-8 -*-
"""Places API returns max 10 photos. The top-decile-share method assumed ~40. How bad is it?"""
import sys, random
sys.stdout.reconfigure(encoding="utf-8")
VENUES = [('loud club', 88), ('big loud bar', 72), ('rooftop', 55), ('wine bar', 34), ('cafe', 22)]

def photos(true_e, n):
    out = []
    while len(out) < n:
        m = min(100, max(0, random.gauss(true_e, 18)))
        if random.random() < 0.55 + 0.004 * m:
            out.append(min(100, m + random.gauss(9, 5)))
    return out

def spread(f, n, trials=400):
    gaps = []
    for _ in range(trials):
        vals = [f(photos(t, n)) for _, t in VENUES]
        # how well does the estimator ORDER the venues, and how much range does it show
        order_ok = all(vals[i] >= vals[i+1] for i in range(len(vals)-1))
        gaps.append((max(vals) - min(vals), order_ok))
    return sum(g for g, _ in gaps)/len(gaps), 100.0*sum(1 for _, o in gaps if o)/len(gaps)

EST = [
 ('mean of all',      lambda ps: sum(ps)/len(ps)),
 ('top-decile share', lambda ps: 100.0*sum(1 for x in ps if x >= 80)/len(ps)),
 ('max',              lambda ps: max(ps)),
 ('mean of top 3',    lambda ps: sum(sorted(ps)[-3:])/3),
]
print('%-20s %28s %28s' % ('', '--- 40 photos ---', '--- 10 photos (the cap) ---'))
print('%-20s %12s %14s %12s %14s' % ('estimator', 'spread', 'order right', 'spread', 'order right'))
print('-'*78)
random.seed(3)
for name, f in EST:
    s40, o40 = spread(f, 40)
    s10, o10 = spread(f, 10)
    print('%-20s %12.1f %13.0f%% %12.1f %13.0f%%' % (name, s40, o40, s10, o10))
print('-'*78)
print()
print('THE CONCLUSION FLIPS AT THE CAP.')
print()
print('With 40 photos the top-decile SHARE orders venues best (92%) - the selection-bias argument')
print('for it was right. With 10, the SHARE needs a tail it does not have: a decile is one photo,')
print('so it quantises to 0/10/20 and drops to 83%.')
print()
print('THE PLAIN MEAN IS THE MOST ROBUST AT THE CAP (88%). Fewer samples punish every estimator,')
print('and the mean is the one that loses least, because averaging is what it was already doing.')
print()
print('So: SHARE if a venue has 30+ photos (its own feed, an opted-in Instagram), MEAN at the')
print('Places cap of 10. And the selection bias does not go away - it just has to be corrected')
print('with a constant per venue TYPE rather than measured per venue.')
