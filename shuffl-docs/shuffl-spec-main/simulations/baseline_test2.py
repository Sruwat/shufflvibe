# -*- coding: utf-8 -*-
"""Rank-within-person (the spec today) versus scale-within-person (the user's rule).

The user: a person's OWN range is the baseline. 7-10s across four cards is their normal; 3s or
11s on another card means something. Ranking cannot express that - it is scale-free, so it throws
the magnitudes away and gives every person the same 0..1 spread.

Two things are measured:
  (a) within a person, does the recovered firmness track how much they identify with each card
  (b) ACROSS people, does the SPREAD of their firmness track how decisive they actually were
"""
import random, statistics as st
random.seed(5)
F, N = 8, 4000
SIGNAL, NOISE = 0.45, 0.30
DIFF = [random.gauss(0, 0.35) for _ in range(F)]

def corr(u, v):
    n = len(u); mu, mv = sum(u)/n, sum(v)/n
    num = sum((a-mu)*(b-mv) for a, b in zip(u, v))
    den = (sum((a-mu)**2 for a in u) * sum((b-mv)**2 for b in v)) ** 0.5
    return num/den if den else 0.0

def rank01(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0]*len(xs)
    for pos, i in enumerate(order): out[i] = 1.0 - pos/(len(xs)-1)
    return out

def zscore01(xs):
    """the user's rule: their own centre and their own spread, magnitudes kept.
    median + MAD because a near-timeout must not set the scale for everything else."""
    med = st.median(xs)
    mad = st.median([abs(x-med) for x in xs]) or 1e-6
    z = [(x-med)/(1.4826*mad) for x in xs]
    return [1/(1+pow(2.718281828, zz)) for zz in z]        # fast (negative z) -> high

people = []
for _ in range(N):
    speed = random.gauss(0, 0.40)
    decisive = random.random()                      # how much this person's identification VARIES
    ident = [0.5 + (random.random()-0.5)*decisive for _ in range(F)]
    lat = [speed + DIFF[c] - SIGNAL*ident[c] + random.gauss(0, NOISE) for c in range(F)]
    people.append((lat, ident, decisive))

base = [sum(p[0][c] for p in people)/N for c in range(F)]

r_rank = r_z = 0.0
spread_rank, spread_z, truth = [], [], []
for lat, ident, decisive in people:
    adj = [lat[c] - base[c] for c in range(F)]
    fr, fz = rank01(adj), zscore01(adj)
    r_rank += corr(fr, ident); r_z += corr(fz, ident)
    spread_rank.append(st.pstdev(fr)); spread_z.append(st.pstdev(fz)); truth.append(decisive)

print('(a) within a person - does firmness track identification per card')
print(f'    rank-within-person   {r_rank/N:+.3f}')
print(f'    scale-within-person  {r_z/N:+.3f}')
print()
print('(b) across people - does the SPREAD of their firmness track how decisive they were')
print(f'    rank-within-person   {corr(spread_rank, truth):+.3f}   (sd of the spread itself: {st.pstdev(spread_rank):.4f})')
print(f'    scale-within-person  {corr(spread_z, truth):+.3f}   (sd of the spread itself: {st.pstdev(spread_z):.4f})')
print()
print('    the rank transform gives every person the same spread by construction, so (b) is')
print('    unmeasurable from latency under the current rule - which is exactly what the')
print('    validation criterion in ASSESSMENT_ENGINE 6.3 asks it to show.')
