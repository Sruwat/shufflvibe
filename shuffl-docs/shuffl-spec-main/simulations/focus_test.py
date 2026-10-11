# -*- coding: utf-8 -*-
"""Is a FOCUS axis new information, or a linear combination of the six we already have?
Least squares of a proposed FOCUS column on the existing axes, across the venue types."""
import itertools
from splitsim import TYPES
import design as Dz  # adds 'games pub'

FOCUS = {
 'table for the night': 10, 'quiet bar': 20, 'buzzy restaurant': 15, 'pub': 35,
 'games bar': 40, 'games pub': 35, 'live room': 92, 'lounge / rooftop': 20,
 'club': 70, 'street / market': 25, 'open ground': 30,
 'screening room / match bar': 88,     # the proposed twelfth type
}
AX = ['ENRG', 'AFFIL', 'CROWD', 'TALK', 'MOVE', 'GAMES']
T = dict(TYPES)
T['screening room / match bar'] = dict(ENRG=65, AFFIL=55, CROWD=75, TALK=50, MOVE=20, GAMES=30)

import os
names = [n for n in FOCUS if n in T and not (os.environ.get('NO_MATCH') and 'match bar' in n)]
X = [[1.0] + [T[n][a] for a in AX] for n in names]
y = [float(FOCUS[n]) for n in names]

def solve(X, y):
    k = len(X[0])
    A = [[sum(r[i] * r[j] for r in X) for j in range(k)] + [sum(r[i] * v for r, v in zip(X, y))] for i in range(k)]
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(A[r][i])); A[i], A[p] = A[p], A[i]
        if abs(A[i][i]) < 1e-9: continue
        A[i] = [v / A[i][i] for v in A[i]]
        for r in range(k):
            if r != i and A[r][i]:
                f = A[r][i]; A[r] = [a - f * b for a, b in zip(A[r], A[i])]
    return [A[i][k] for i in range(k)]

b = solve(X, y)
pred = [sum(c * v for c, v in zip(b, r)) for r in X]
ybar = sum(y) / len(y)
ss_res = sum((a - p) ** 2 for a, p in zip(y, pred)); ss_tot = sum((a - ybar) ** 2 for a in y)
print(f'FOCUS regressed on all six existing axes: R2 = {1 - ss_res/ss_tot:.2f}  (n={len(y)} types)')
print('   residuals (what the six axes cannot say about focus):')
for n, a, p in sorted(zip(names, y, pred), key=lambda t: -abs(t[1] - t[2])):
    print(f'      {n:<28} FOCUS {a:>3.0f}   predicted {p:>5.1f}   miss {a - p:+6.1f}')

print('\n   pairwise correlation of FOCUS with each existing axis:')
def corr(u, v):
    n = len(u); mu, mv = sum(u)/n, sum(v)/n
    num = sum((a-mu)*(b-mv) for a, b in zip(u, v))
    den = (sum((a-mu)**2 for a in u) * sum((b-mv)**2 for b in v)) ** 0.5
    return num/den if den else 0.0
for a in AX:
    print(f'      {a:<6} r = {corr(y, [T[n][a] for n in names]):+.2f}')

print('\n   and how well each EXISTING axis is predicted by the other five (for comparison):')
for a in AX:
    others = [x for x in AX if x != a]
    X2 = [[1.0] + [T[n][o] for o in others] for n in names]
    y2 = [float(T[n][a]) for n in names]
    b2 = solve(X2, y2); p2 = [sum(c*v for c, v in zip(b2, r)) for r in X2]
    m2 = sum(y2)/len(y2)
    r2 = 1 - sum((q-p)**2 for q, p in zip(y2, p2)) / sum((q-m2)**2 for q in y2)
    print(f'      {a:<6} R2 = {r2:.2f}')
