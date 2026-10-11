# -*- coding: utf-8 -*-
"""The corpus is HOUR-BLIND. Reviews of a daytime terrace and reviews of a late party sit in the
same bag and the lexicon averages them, producing a number that describes neither."""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
import lexicon as L
from summerhouse import CORPUS

DAY   = re.compile(r'during the day|brunch|afternoon|daytime|date spot|[1-5] ?pm|noon|lunch', re.I)
NIGHT = re.compile(r'night|party|dance|dancing|dj|late|midnight|1 ?am|11 ?pm|club|boxout|gig|live', re.I)

day   = [c for c in CORPUS if DAY.search(c) and not NIGHT.search(c)]
night = [c for c in CORPUS if NIGHT.search(c) and not DAY.search(c)]
both  = [c for c in CORPUS if c not in day and c not in night]

print('corpus of %d: %d day-marked, %d night-marked, %d unmarked' % (len(CORPUS), len(day), len(night), len(both)))
print()
print('%-7s %10s %12s %12s' % ('factor', 'WHOLE', 'DAY only', 'NIGHT only'))
print('-' * 48)
for f in ['ENRG', 'CROWD', 'TALK', 'MOVE', 'FOCUS', 'LIVE', 'POL']:
    w, _, _, _ = L.score(CORPUS, f, 'live room')
    d, dn, _, _ = L.score(day + both, f, 'lounge / rooftop')
    n, nn, _, _ = L.score(night + both, f, 'live room')
    print('%-7s %10d %12d %12d' % (f, w, d, n))
print('-' * 48)
print()
print('ENRG splits %d (day) against %d (night) - the whole-corpus 41 described neither.' %
      (L.score(day + both, 'ENRG', 'lounge / rooftop')[0], L.score(night + both, 'ENRG', 'live room')[0]))
print()
print('SO: PARTITION THE CORPUS BY TIME MARKERS BEFORE SCORING. "during the day", "brunch", "5pm"')
print('go in one bag; "night", "party", "DJ", "late" in the other; unmarked text counts in both.')
print('It is the same hour-scoping every other part of this engine needed, arriving at the text layer.')
