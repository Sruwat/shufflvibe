# -*- coding: utf-8 -*-
"""IS WITHIN-FACTOR CHEMISTRY DOING ANY WORK?

The user, 2026-10-05, correcting the veto reading: a preference is dropped for a stop when **no
venue that fits the shape can serve it**. That is FEASIBILITY, not a multiplier - and if the
candidate set is already gated on the drawn shape, the gate may be doing the suppression by itself.

This measures whether it is. Three questions:
  1  at a loud stop, how many in-gate venues serve FOOD at all?
  2  does adding the suppression multiplier change the pick, once feasibility has run?
  3  where the two disagree, which one is right?
"""
import random, sys
sys.stdout.reconfigure(encoding='utf-8')
random.seed(11)

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

# venue type -> (energy range, crowd range, P(serves) per preference)
TYPES = {
 'cafe':             ((18, 42), (25, 55), dict(FOOD=.80, LIVE=.05, POL=.25, SCEN=.70, HERIT=.20, GAMES=.10)),
 'restaurant':       ((30, 55), (35, 65), dict(FOOD=.92, LIVE=.05, POL=.45, SCEN=.55, HERIT=.25, GAMES=.03)),
 'buzzy restaurant': ((52, 72), (55, 80), dict(FOOD=.78, LIVE=.12, POL=.60, SCEN=.55, HERIT=.15, GAMES=.05)),
 'big loud bar':     ((68, 86), (70, 92), dict(FOOD=.30, LIVE=.20, POL=.50, SCEN=.35, HERIT=.05, GAMES=.35)),
 'live room':        ((58, 82), (55, 85), dict(FOOD=.25, LIVE=.95, POL=.45, SCEN=.50, HERIT=.10, GAMES=.05)),
 'club':             ((84, 97), (80, 97), dict(FOOD=.06, LIVE=.15, POL=.85, SCEN=.40, HERIT=.02, GAMES=.03)),
 'games venue':      ((58, 80), (50, 80), dict(FOOD=.35, LIVE=.05, POL=.35, SCEN=.20, HERIT=.02, GAMES=.98)),
 'heritage room':    ((25, 50), (30, 60), dict(FOOD=.70, LIVE=.25, POL=.55, SCEN=.70, HERIT=.95, GAMES=.05)),
}
PREFS = ['FOOD', 'LIVE', 'POL', 'SCEN', 'HERIT', 'GAMES']
W = dict(FOOD=20, LIVE=18, POL=18, SCEN=16, HERIT=10, GAMES=12)      # HERIT lowered 2026-10-05
SUPP = dict(FOOD=(1.00, 0.25), HERIT=(1.00, 0.30), SCEN=(1.00, 0.55),
            POL=(1.00, 1.00), GAMES=(1.00, 1.00), LIVE=(0.70, 1.30))
SHAPE_GATE = 12

def mk(i):
    t = random.choice(list(TYPES))
    (e0, e1), (c0, c1), p = TYPES[t]
    return dict(name='%s#%d' % (t, i), type=t,
                E=random.uniform(e0, e1), C=random.uniform(c0, c1),
                serves={f: (random.random() < p[f]) for f in PREFS})

UNIVERSE = [mk(i) for i in range(400)]

def gate(drawn_e, drawn_c):
    scored = [(abs(v['E'] - drawn_e) + 0.6 * abs(v['C'] - drawn_c), v) for v in UNIVERSE]
    best = min(d for d, _ in scored)
    return [(d, v) for d, v in sorted(scored) if d <= best + SHAPE_GATE]

def live_w(f, e, suppress):
    if not suppress: return W[f]
    lo, hi = SUPP[f]
    t = max(0.0, min(1.0, (e - 40) / 45.0))
    return W[f] * (lo + (hi - lo) * t)

def pick(cands, user, e, suppress):
    best, bestv = None, None
    for d, v in cands:
        s = sum(live_w(f, e, suppress) * (user[f] / 100.0) for f in PREFS
                if v['serves'][f] and user[f] >= 60)
        if best is None or s > best:
            best, bestv = s, v
    return bestv

# ===================================================================== 1. feasibility alone
head('1.  AT A LOUD STOP, CAN THE IN-GATE VENUES SERVE FOOD AT ALL?')
print('%-26s %7s   %s' % ('the stop the user drew', 'in gate', 'share of in-gate venues serving...'))
print('%-26s %7s   %s' % ('', '', '  '.join('%-6s' % f for f in PREFS)))
line()
for e, c, lab in ((25, 35, 'quiet, empty   E25 C35'), (45, 50, 'calm           E45 C50'),
                  (65, 70, 'buzzy          E65 C70'), (80, 85, 'loud           E80 C85'),
                  (92, 92, 'going off      E92 C92')):
    g = gate(e, c)
    sh = {f: sum(1 for _, v in g if v['serves'][f]) / float(len(g)) for f in PREFS}
    print('%-26s %7d   %s' % (lab, len(g), '  '.join('%-6.0f' % (100 * sh[f]) for f in PREFS)))
line()
print("""
  **FOOD falls from ~80% of candidates at a quiet stop to the teens at a loud one, and HERIT falls
  to near nothing - without any multiplier being applied.** The shape gate already removed the
  venues that cannot carry those preferences, because the venues that serve food ARE the quiet ones.
  **That is the suppression the user described, arrived at from the data rather than from a table.**
""")

# ===================================================================== 2. does the multiplier change the pick?
head('2.  ONCE FEASIBILITY HAS RUN, DOES THE MULTIPLIER CHANGE THE PICK?')
random.seed(5)
rows, disagree, examples = 0, 0, []
for _ in range(4000):
    e = random.uniform(15, 97); c = max(10, min(97, e + random.uniform(-18, 18)))
    user = {f: random.choice([20, 38, 62, 75, 88, 92]) for f in PREFS}
    g = gate(e, c)
    if not g: continue
    a = pick(g, user, e, False)          # feasibility only
    b = pick(g, user, e, True)           # feasibility + within-factor chemistry
    rows += 1
    if a is not b:
        disagree += 1
        if len(examples) < 4 and e > 70:
            examples.append((e, user, a, b))
print('   stops simulated                 %d' % rows)
print('   the two methods pick the SAME venue   %.1f%%' % (100.0 * (rows - disagree) / rows))
print('   they disagree                         %.1f%%' % (100.0 * disagree / rows))
line()
for e, user, a, b in examples:
    print('   drawn E%.0f   user: %s' % (e, ' '.join('%s%d' % (f, user[f]) for f in PREFS)))
    print('      feasibility only      -> %-22s serves %s' % (a['name'], ','.join(f for f in PREFS if a['serves'][f])))
    print('      with the multiplier   -> %-22s serves %s' % (b['name'], ','.join(f for f in PREFS if b['serves'][f])))
    print()

# ===================================================================== 3. who is right where they differ
head('3.  WHERE THEY DIFFER, WHICH ONE IS RIGHT?')
print("""
  The disagreements are **venues inside the gate that serve a suppressed preference anyway** - the
  loud bar that genuinely does good food, the busy room that genuinely is old.

     feasibility only   gives that venue full credit, because it really does serve both
     the multiplier     discounts it to a quarter, because the TYPE usually cannot

  **The multiplier penalises exactly the venue that solves the problem.** A correlation learned
  across venue types is being applied to a venue whose own data contradicts it - and we have the
  venue's own data. That is the same mistake as storing a type-curve guess in a slot
  (`VENUE_DATABASE_V1.md` section 2a1): **the prior is for when evidence is missing, never for
  overruling evidence that is present.**
""")
