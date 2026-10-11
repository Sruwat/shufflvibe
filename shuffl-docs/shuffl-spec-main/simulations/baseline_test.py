# -*- coding: utf-8 -*-
"""Does the latency method recover how much a person identifies with each card?

Three corrections compared, on simulated sessions where we KNOW the truth:
  raw       - rank the person's own latencies, no correction
  universal - subtract the card's mean log-latency across all users (the spec today)
  per-person- subtract that card mean SCALED by this person's own sensitivity to card difficulty
"""
import random, math
random.seed(3)

F = 8                      # factors, one card each (a decisive person's deck)
N_PEOPLE = 4000
SIGNAL = 0.45              # how much identification speeds a swipe, in log-seconds
NOISE = 0.30               # everything else

def corr(u, v):
    n = len(u); mu, mv = sum(u)/n, sum(v)/n
    num = sum((a-mu)*(b-mv) for a, b in zip(u, v))
    den = (sum((a-mu)**2 for a in u) * sum((b-mv)**2 for b in v)) ** 0.5
    return num/den if den else 0.0

def rank01(xs):
    """fastest -> 1.0, slowest -> 0.0, like latency_firmness"""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0]*len(xs)
    for pos, i in enumerate(order): out[i] = 1.0 - pos/(len(xs)-1)
    return out

# card difficulty: some images take everyone longer (busy scene v a single object)
DIFF = [random.gauss(0, 0.35) for _ in range(F)]

def session(spread_sensitivity):
    speed = random.gauss(0, 0.40)                 # this person's overall pace
    sens  = max(0.2, random.gauss(1.0, spread_sensitivity))   # how much card difficulty costs THEM
    ident = [random.random() for _ in range(F)]   # the truth we want back
    lat = [speed + sens*DIFF[c] - SIGNAL*ident[c] + random.gauss(0, NOISE) for c in range(F)]
    return lat, ident, sens

def run(spread_sensitivity, label):
    # pass 1: build the universal baseline from the population
    sessions = [session(spread_sensitivity) for _ in range(N_PEOPLE)]
    base = [sum(s[0][c] for s in sessions)/len(sessions) for c in range(F)]
    r_raw = r_uni = r_pp = 0.0
    for lat, ident, sens in sessions:
        r_raw += corr(rank01(lat), ident)
        adj_u = [lat[c] - base[c] for c in range(F)]
        r_uni += corr(rank01(adj_u), ident)
        # per-person: fit lat_c = a + b * base_c within this session, keep the residual
        mb = sum(base)/F; ml = sum(lat)/F
        cov = sum((base[c]-mb)*(lat[c]-ml) for c in range(F))
        var = sum((base[c]-mb)**2 for c in range(F))
        b_hat = cov/var if var > 1e-9 else 1.0
        b = (F*b_hat + 6*1.0) / (F + 6)            # shrink toward 1 - only 8 points to fit it
        adj_p = [lat[c] - b*base[c] for c in range(F)]
        r_pp += corr(rank01(adj_p), ident)
    n = len(sessions)
    print(f'{label:<42} raw {r_raw/n:+.3f}   universal {r_uni/n:+.3f}   per-person {r_pp/n:+.3f}')

print('correlation between recovered latency-firmness and TRUE identification')
print()
run(0.00, 'everyone equally affected by card difficulty')
run(0.35, 'people differ moderately in sensitivity')
run(0.70, 'people differ a lot in sensitivity')
print()
print('card difficulty spread (sd of log-seconds):', round((sum(d*d for d in DIFF)/F)**0.5, 2))
