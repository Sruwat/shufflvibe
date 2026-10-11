# -*- coding: utf-8 -*-
"""Verifying swipes against photos. The asymmetry: wrongly accusing an honest user costs far more
than paying once for a bad capture, so the threshold must be loose and must need MULTIPLE misses."""
import sys, random
sys.stdout.reconfigure(encoding="utf-8")
random.seed(9)

FACTORS = 5          # energy, crowd, how loud, how dressed, how much movement
N = 4000

def honest():
    """truth, then a human reading it with normal disagreement and a bit of rounding"""
    truth = [random.randint(1, 10) for _ in range(FACTORS)]
    swipe = [max(1, min(10, t + round(random.gauss(0, 1.6)))) for t in truth]   # honest noise
    photo = [max(1, min(10, t + round(random.gauss(0, 1.9)))) for t in truth]   # the model's read
    return swipe, photo

def careless():
    """swiped without looking - the swipes have no relationship to the room"""
    truth = [random.randint(1, 10) for _ in range(FACTORS)]
    swipe = [random.randint(1, 10) for _ in range(FACTORS)]
    photo = [max(1, min(10, t + round(random.gauss(0, 1.9)))) for t in truth]
    return swipe, photo

def misses(swipe, photo, gap):
    return sum(1 for s, p in zip(swipe, photo) if abs(s - p) >= gap)

def line(c='-', n=92): print(c * n)
def head(t):
    print(); print('=' * 92); print(t); print('=' * 92)

head('SETTING THE VERIFICATION THRESHOLD')
print('A capture fails if at least MIN_MISSES factors are off by GAP or more.')
print()
print('%-10s %-12s %16s %18s' % ('gap', 'min misses', 'honest FAILED', 'careless CAUGHT'))
line()
best = None
for gap in (4, 5, 6):
    for mm in (2, 3, 4):
        fp = sum(1 for _ in range(N) if misses(*honest(), gap) >= mm) / float(N)
        tp = sum(1 for _ in range(N) if misses(*careless(), gap) >= mm) / float(N)
        flag = ''
        if fp <= 0.02 and (best is None or tp > best[2]):
            best = (gap, mm, tp, fp); flag = '  <-- best under a 2% false-accusation cap'
        print('%-10d %-12d %15.1f%% %17.1f%%%s' % (gap, mm, fp * 100, tp * 100, flag))
line()
g, m, tp, fp = best
print("""
  PICK: a capture fails only if **%d or more factors are off by %d or more**.
     catches %.0f%% of careless swiping
     wrongly fails %.1f%% of honest users

  AND THE ASYMMETRY IS THE WHOLE DESIGN. Paying Rs 450 for one bad capture costs Rs 450. Telling an
  honest user they cheated costs that user, and anybody they tell. **So tune for the false-accusation
  rate first and accept that a third of careless captures get through** - the median of three
  captures absorbs them anyway, which is what the three were for.

  AND NEVER PHRASE IT AS AN ACCUSATION. "We could not verify this one - try again at your next
  stop" costs nothing and keeps the user. "You did not complete this honestly" is unrecoverable and
  will sometimes be wrong.
""" % (m, g, tp * 100, fp * 100))

head('AND THE WARNING MESSAGE DOES REAL WORK ON ITS OWN')
print("""
  "Make sure you carefully complete this since we'll be verifying" improves the data whether or not
  the check behind it is any good. Stating that an answer will be checked is one of the most
  reliable effects in survey design - it moves people from satisficing to actually looking.

  **So the sentence is worth more than the algorithm**, and it should be shown BEFORE the photos,
  not between the photos and the swipes - the user needs to know while they are still looking at
  the room, not after they have stopped.
""")
