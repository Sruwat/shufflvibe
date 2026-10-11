# -*- coding: utf-8 -*-
"""TWO WALKTHROUGHS, on the rules as they stand 2026-10-01.

PART 1  a user swipes the identity deck and gets a vibe for the day
PART 2  how four real-shaped venues get tagged and stored, and where they land in the supply grid
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from math import log, exp

# ================================================================= PART 1
IDENT  = ['ENRG', 'AFFIL', 'TALK', 'FOCUS', 'MOVE', 'SPONT']
WEIGHT = dict(ENRG=18, AFFIL=16, TALK=14, FOCUS=14, MOVE=12, SPONT=10)

# every card is oriented toward its factor's HIGH pole, so the swipe score IS the factor score
CARDS = {
 'ENRG':  ('a packed room at 1am, everyone up, lights going',
           'the same crowd at 7pm, drinks out, nobody shouting yet'),
 'AFFIL': ('a long table of eight who clearly came together',
           'a bar rail of strangers half-turned toward each other'),
 'TALK':  ('two people leaning in across a small table',
           'a room where everyone is mouthing words at each other'),
 'FOCUS': ('a crowd all facing one way, lit from the stage',
           'a circle of people facing each other, nothing behind them'),
 'MOVE':  ('a floor mid-song, nobody sitting',
           'a deep booth people have clearly not left for an hour'),
 'SPONT': ('a doorway at 9pm, nobody holding a booking',
           'a set table with a reserved card on it'),
}
SWIPE = {'LOVE': 88, 'UP FOR IT': 62, 'NOT FOR ME': 38, 'HARD PASS': 12}
PAIR = {   # (first, second) -> resolved score, ASSESSMENT_ENGINE section 2.2
 ('UP FOR IT', 'LOVE'): 75, ('UP FOR IT', 'UP FOR IT'): 62,
 ('UP FOR IT', 'NOT FOR ME'): 50, ('UP FOR IT', 'HARD PASS'): 37,
 ('NOT FOR ME', 'HARD PASS'): 25, ('NOT FOR ME', 'NOT FOR ME'): 38,
 ('NOT FOR ME', 'UP FOR IT'): 50, ('NOT FOR ME', 'LOVE'): 63,
}
BROKEN = {('UP FOR IT', 'HARD PASS'), ('NOT FOR ME', 'LOVE')}
GLOBAL_SCALE = 0.26        # log-seconds, population MAD - to be measured on the first users
K = 5                      # the ranking key's latency coefficient

# --- what Ishaan actually does. (factor, swipe, seconds) in deck order.
SESSION = [
 ('ENRG',  'LOVE',       3.1),   # instant - he knows
 ('AFFIL', 'NOT FOR ME', 6.8),   # a lean: a second AFFIL card will join the deck
 ('TALK',  'UP FOR IT',  7.4),   # a lean
 ('FOCUS', 'LOVE',       4.0),   # fast and firm
 ('MOVE',  'UP FOR IT',  9.1),   # a slow lean - he is unsure
 ('SPONT', 'HARD PASS',  5.2),   # firm low: he plans
 ('AFFIL', 'NOT FOR ME', 7.1),   # second card, same lean
 ('TALK',  'LOVE',       4.6),   # second card: lean confirmed and strengthened
 ('MOVE',  'NOT FOR ME', 11.3),  # second card contradicts the first - a true neutral at 50
]

def line(c='-', n=100): print(c * n)
def head(t):
    print(); line('='); print(t); line('=')

head('PART 1 ' + chr(8212) + '  ISHAAN PLAYS THE IDENTITY DECK, FRIDAY 20:12')
print('Six identity factors. Every factor starts with ONE card. An extreme swipe is believed and')
print('the factor is done; a mild swipe is checked with a second card from a different angle.')
print('The user is told none of this. They see images and swipe on appeal.')
print()
line()
print('%-4s %-6s %-11s %6s   %s' % ('#', 'factor', 'swipe', 'secs', 'what the image was'))
line()
seen = {}
for i, (f, sw, sec) in enumerate(SESSION, 1):
    nth = seen.get(f, 0); seen[f] = nth + 1
    print('%-4d %-6s %-11s %6.1f   %s' % (i, f, sw, sec, CARDS[f][nth]))
line()
print('Nine cards. A fully decisive person sees six; somebody who leans on everything sees twelve.')

# ---- scores
print()
head('STEP 1  ' + chr(8212) + '  THE SWIPES BECOME SCORES')
answers = {}
for f, sw, sec in SESSION:
    answers.setdefault(f, []).append((sw, sec))
score, notes = {}, {}
for f in IDENT:
    a = answers[f]
    if len(a) == 1:
        score[f] = SWIPE[a[0][0]]
        notes[f] = 'one card was enough ' + chr(8212) + ' an extreme is believed'
    else:
        key = (a[0][0], a[1][0])
        score[f] = PAIR[key]
        notes[f] = ('BROKEN PAIR ' + chr(8212) + ' the two cards disagree, so it lands at the middle'
                    if key in BROKEN else 'lean checked: %s then %s' % key)
for f in IDENT:
    print('   %-6s %3d   %s' % (f, score[f], notes[f]))

# ---- latency firmness
print()
head('STEP 2  ' + chr(8212) + '  LATENCY, MEASURED SILENTLY')
adj = {}
for f, sw, sec in SESSION:
    adj.setdefault(f, []).append(log(sec))        # card_baseline / position_baseline are 0 at launch
flat = [v for vs in adj.values() for v in vs]
flat.sort()
centre = flat[len(flat) // 2] if len(flat) % 2 else (flat[len(flat)//2 - 1] + flat[len(flat)//2]) / 2
print('   his own session median: %.2f log-seconds (%.1f s) ' % (centre, exp(centre)) +
      chr(8212) + ' that is HIS normal pace tonight')
print('   divided by GLOBAL_SCALE %.2f ' % GLOBAL_SCALE + chr(8212) +
      ' a SHARED scale, so how decisive he is survives')
print()
firm = {}
for f in IDENT:
    per = [1.0 / (1.0 + exp((x - centre) / GLOBAL_SCALE)) for x in adj[f]]
    firm[f] = sum(per) / len(per)
    secs = ', '.join('%.1fs' % exp(x) for x in adj[f])
    print('   %-6s %-16s -> firmness %.2f' % (f, secs, firm[f]))
print()
print('   Fast is firm. ENRG at 3.1s against his own 6.8s median reads 0.95; MOVE, dithered over')
print('   twice at 9.1 and 11.3 seconds, reads 0.19. Neither number came from asking him.')

# ---- the ranking key
print()
head('STEP 3  ' + chr(8212) + '  THE RANKING KEY  |score ' + chr(8722) + ' 50| + 5 ' + chr(215) + ' firmness')
rank = sorted(IDENT, key=lambda f: -(abs(score[f] - 50) + K * firm[f]))
for f in rank:
    key = abs(score[f] - 50) + K * firm[f]
    print('   %-6s |%3d' % (f, score[f]) + chr(8722) + '50| = %2d  + 5' % abs(score[f] - 50) +
          chr(215) + '%.2f = %.2f  -> %5.2f' % (firm[f], K * firm[f], key))
print()
print('   THIS SESSION IS EXACTLY WHY LATENCY IS IN THE KEY.')
print('   ENRG 88, FOCUS 88 and SPONT 12 are all |s-50| = 38. On score alone that is a THREE-WAY')
print('   TIE for the name, and the app would have to stop and ask him (the forced-choice screen).')
print('   Latency separates them 42.77 / 42.43 / 41.69 without a single extra question.')
print()
print('   And it still cannot overturn a score: K=5 is less than half of one 12-point step, so')
print('   TALK 75 answered fast never climbs above ENRG 88 answered slowly.')

# ---- the name
print()
head('STEP 4  ' + chr(8212) + '  THE NAME')
W = {
 'ENRG':  (('Low-Key', 'Slow-Burner'), ('Peak', 'Climber')),
 'AFFIL': (('Mingling', 'Mingler'), ('Inner-Circle', 'Insider')),
 'TALK':  (('Loud', 'Noise-Seeker'), ('Talking', 'Table-Talker')),
 'FOCUS': (('Headline', 'Headliner'), ('Front-Row', 'Front-Rower')),
 'MOVE':  (('Seated', 'Sitter'), ('Moving', 'Floor-Filler')),
 'SPONT': (('Locked-In', 'Planner'), ('Last-Minute', 'Wildcard')),
}
SINGLE = {'ENRG': ('Slow Burner', 'Night Climber'), 'AFFIL': ('Room Worker', 'Inner Circle'),
          'TALK': ('Noise Seeker', 'Table Talker'), 'FOCUS': ('Headline Act', 'Front Row'),
          'MOVE': ('Sitter', 'Floor Filler'), 'SPONT': ('Locked In', 'Wild Card')}
STICKY, SECOND_MIN = 15, 20
first = rank[0]
d_first = abs(score[first] - 50)
cands = [f for f in IDENT if f != first and abs(score[f] - 50) >= d_first - STICKY
         and abs(score[f] - 50) >= SECOND_MIN]
print('   first factor:  %s (highest key)' % first)
print('   second slot:   within %d of the first by |s' % STICKY + chr(8722) +
      '50|, AND at least %d from the middle' % SECOND_MIN)
for f in IDENT:
    if f == first: continue
    d = abs(score[f] - 50)
    ok = 'QUALIFIES' if f in cands else ('too close to the middle' if d < SECOND_MIN else 'too far behind the first')
    print('      %-6s |s' % f + chr(8722) + '50| = %2d   %s' % (d, ok))
pole = lambda f: 1 if score[f] >= 50 else 0
if cands:
    second = max(cands, key=lambda f: abs(score[f] - 50) + K * firm[f])
    name = W[first][pole(first)][0] + ' ' + W[second][pole(second)][1]
    print()
    print('   second factor: %s' % second)
else:
    second, name = None, SINGLE[first][pole(first)]
print()
print('   ' + chr(9608) * 3 + '  YOUR VIBE TODAY IS   >>>  %s  <<<' % name.upper())

print()
head('STEP 5  ' + chr(8212) + '  WHAT THAT NAME THEN DOES (and what it does NOT do)')
print('   DOES:')
print('      - it is what another user sees on his profile today')
print('      - the six scores are the vector behind the vibe match % against venues and users')
print('      - Chemistry V4 blends them with everyone else in a room to give the ROOM an identity')
print('      - the Join screen set to PEOPLE sorts rooms by closeness to this vector')
print('   DOES NOT:')
print('      - choose a venue, a stop count, an energy level or an hour. None of it.')
print('      - that is all the skeleton, which he has not drawn yet.')
print()
print('   His identity vector tonight: ' + '  '.join('%s %d' % (f, score[f]) for f in IDENT))
print('   A loud club scores low for him on TALK %d; a gig scores high on FOCUS %d.' % (score['TALK'], score['FOCUS']))
print('   Neither fact will put a club or a gig in his plan. It only colours what he is shown.')
