# -*- coding: utf-8 -*-
"""Does capping a slot at 3 captures let us pay more? Simulate allocation with and without it."""
import sys, random
sys.stdout.reconfigure(encoding="utf-8")
random.seed(5)

VENUES, SLOTS_PER, REPS, BUDGET = 35, 5.4, 3, 250000
SLOTS = int(VENUES * SLOTS_PER)
NEEDED = SLOTS * REPS

# popularity is very uneven - the top slots get visited far more than the tail
pop = sorted([random.paretovariate(1.3) for _ in range(SLOTS)], reverse=True)
tot = sum(pop); pop = [p / tot for p in pop]

def run(capped, paid):
    """spend the budget one capture at a time, visits landing by popularity"""
    got = [0] * SLOTS
    spent = n = 0
    while spent + paid <= BUDGET:
        r, acc, i = random.random(), 0.0, 0
        for i, p in enumerate(pop):
            acc += p
            if r <= acc: break
        if capped and got[i] >= REPS:
            continue                      # the slot is no longer gold - nobody is paid
        got[i] += 1; spent += paid; n += 1
    useful = sum(min(g, REPS) for g in got)
    filled = sum(1 for g in got if g >= REPS)
    return n, useful, filled, spent

def line(c='-', n=92): print(c * n)
def head(t):
    print(); print('=' * 92); print(t); print('=' * 92)

head('DOES THE 3-CAPTURE CAP LET US PAY MORE?')
print('%d venues, %d slots, %d captures needed, Rs %s budget' % (VENUES, SLOTS, NEEDED, '{:,}'.format(BUDGET)))
print()
print('%-28s %9s %10s %12s %14s' % ('', 'paid for', 'useful', 'slots FULL', 'venues done'))
line()
for capped, paid, label in [(False, 441, 'no cap, Rs 441'),
                            (True,  441, 'CAPPED, Rs 441'),
                            (True,  600, 'CAPPED, Rs 600'),
                            (True,  750, 'CAPPED, Rs 750')]:
    n, useful, filled, spent = run(capped, paid)
    print('%-28s %9d %10d %12d %14.1f' % (label, n, useful, filled, filled / SLOTS_PER))
line()
print("""
  WITHOUT THE CAP the budget buys the same number of captures and far fewer USEFUL ones, because
  visits pile onto the popular slots. You pay three times for a Friday at the club everybody
  already goes to, and never once for its Tuesday.

  SO THE CAP DOES NOT HAND US MORE MONEY. It makes the money do what the costing assumed it would.

  WHAT IT DOES ALLOW is removing the waste buffer. Any honest plan without a cap needs 40-60% extra
  to cover duplicates. With the cap that buffer is unnecessary - which is the same thing as a raise.
""")
n0, u0, f0, _ = run(False, 441)
n1, u1, f1, _ = run(True, 441)
print('  waste without the cap: %d of %d captures paid for are duplicates (%.0f%%)' % (n0 - u0, n0, 100.0*(n0-u0)/n0))
print('  so the real choice is COVERAGE against AMOUNT, and the cap is what makes either honest.')
