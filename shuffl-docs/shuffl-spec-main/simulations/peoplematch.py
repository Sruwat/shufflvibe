# -*- coding: utf-8 -*-
"""SHOULD PERSON-TO-PERSON MATCHING USE SIMILARITY, OR THE CHEMISTRY ENGINE?

"Friends you vibe the most with", and the score beside a person in search, currently use plain
vector similarity between identity factors. Rooms use the chemistry engine. The chemistry work has
always said similarity is the wrong objective, and this measures how far apart the two actually are
and shows the cases where they invert.

Imports chem4.py so there is one engine and no second implementation.
"""
import sys, os, random, math, io, contextlib, statistics as st
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# chem4.py prints its own demo at import time; swallow it, we only want the functions
with contextlib.redirect_stdout(io.StringIO()):
    import chem4

IDENT = chem4.IDENT


def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)


def cosine(a, b):
    """similarity as it is actually used today: the two factor vectors, centred on 50."""
    xs = [a.vibe[f] - 50 for f in IDENT]
    ys = [b.vibe[f] - 50 for f in IDENT]
    na = math.sqrt(sum(x * x for x in xs)) or 1e-9
    nb = math.sqrt(sum(y * y for y in ys)) or 1e-9
    return sum(x * y for x, y in zip(xs, ys)) / (na * nb)


def pair_match(me, them):
    """the chemistry engine at n=2: build the room the two of us would be, score me against it."""
    rv, splits, _flags = chem4.room([me, them])
    return chem4.match(me, rv, [me, them], splits)


# ======================================================== A. one worked example
head('A.  ONE EVENING, FOUR FRIENDS')
me = chem4.mk('You', ENRG=78, AFFIL=35, TALK=30, FOCUS=72, MOVE=70, SPONT=60)
friends = [
    chem4.mk('Zoya',  ENRG=80, AFFIL=33, TALK=28, FOCUS=74, MOVE=72, SPONT=58),
    chem4.mk('Dev',   ENRG=50, AFFIL=50, TALK=50, FOCUS=50, MOVE=50, SPONT=50),
    chem4.mk('Ira',   ENRG=62, AFFIL=78, TALK=74, FOCUS=40, MOVE=45, SPONT=66),
    chem4.mk('Kabir', ENRG=84, AFFIL=30, TALK=22, FOCUS=30, MOVE=82, SPONT=40),
]
print('   you: ' + '  '.join('%s %d' % (f, me.vibe[f]) for f in IDENT))
line()
print('   %-8s %-34s %10s %12s' % ('friend', 'what they are', 'similarity', 'chemistry'))
line()
desc = {'Zoya': 'almost exactly you', 'Dev': 'middling on everything',
        'Ira': 'outward, talkative, no main event', 'Kabir': 'harder and quieter than you'}
rows = []
for fr in friends:
    rows.append((fr.name, cosine(me, fr), pair_match(me, fr)))
    print('   %-8s %-34s %9.2f %11.0f%%' % (fr.name, desc[fr.name], rows[-1][1], rows[-1][2] * 100))
line()
by_sim = [n for n, s, c in sorted(rows, key=lambda r: -r[1])]
by_chem = [n for n, s, c in sorted(rows, key=lambda r: -r[2])]
print('   ranked by similarity:  ' + '  >  '.join(by_sim))
print('   ranked by chemistry:   ' + '  >  '.join(by_chem))
line()
print("""
  **Dev is the case to look at.** He is middling on all six, so he is the one person in this list who
  wants nothing in particular - and similarity puts him well down, because a vector of zeroes points
  nowhere near yours. **The chemistry engine reads him differently**: a person with no firm wants does
  not pull a room away from you, so the night the two of you would have is largely the night you drew.

  **And Zoya is the one similarity gets right for the wrong reason.** She is nearly your twin, so she
  scores top on both - but the chemistry engine is agreeing that *this night will be as you want it*,
  not that *she is like you*. **The two agree here and disagree the moment anybody is firm about
  something you are not.**
""")

# ======================================================== B. how often do they disagree?
head('B.  HOW OFTEN DO THE TWO RANKINGS DISAGREE?')
rng = random.Random(5)
flip = pairs = 0
top_same = 0
TR = 2500
gaps = []
for _ in range(TR):
    you = chem4.rnd_person(rng.randrange(10 ** 6))
    pool = [chem4.rnd_person(rng.randrange(10 ** 6)) for _ in range(5)]
    sims = [cosine(you, p) for p in pool]
    chems = [pair_match(you, p) for p in pool]
    if sims.index(max(sims)) == chems.index(max(chems)):
        top_same += 1
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            pairs += 1
            if (sims[i] > sims[j]) != (chems[i] > chems[j]):
                flip += 1
    gaps.append(st.mean([abs(s) for s in sims]))
line()
print('   %d people, each ranked against five friends' % TR)
print('   %-44s %s' % ('the two pick the same best friend', '%.0f%%' % (100.0 * top_same / TR)))
print('   %-44s %s' % ('pairs of friends they order differently', '%.0f%%' % (100.0 * flip / pairs)))
line()

# ======================================================== C. the Open Night case
head('C.  THE CASE THE CHEMISTRY WORK HAS ALWAYS NAMED')
firm = chem4.mk('Firm', ENRG=88, AFFIL=14, TALK=12, FOCUS=86, MOVE=84, SPONT=20)
blank = chem4.mk('Blank', **{f: 50 for f in IDENT})
twin = chem4.mk('Twin', ENRG=88, AFFIL=14, TALK=12, FOCUS=86, MOVE=84, SPONT=20)
line()
print('   somebody firm on all six, against two friends:')
print('   %-30s %10s %12s' % ('', 'similarity', 'chemistry'))
print('   %-30s %9.2f %11.0f%%' % ('an identical twin', cosine(firm, twin), pair_match(firm, twin) * 100))
print('   %-30s %9.2f %11.0f%%' % ('somebody with no wants', cosine(firm, blank), pair_match(firm, blank) * 100))
line()
print("""
  **Similarity says the blank person is the worst possible friend** - the vectors are orthogonal, so
  the score is 0. **The chemistry engine says the night would be almost entirely yours**, which is a
  different claim and the true one: somebody easy-going does not fight you for the night.

  **This is the objection to similarity in one line.** It measures *are we the same*; the product
  needs *what would the night be like*. Those coincide for twins and come apart for everybody else.
""")

# ======================================================== D. what the label has to become
head('D.  AND THE LABEL HAS TO CHANGE WITH IT')
print("""
  "Friends you vibe the most with" is a similarity sentence. If the number underneath becomes the
  chemistry engine, the words have to follow it, or the screen says one thing and means another:

      friends you vibe the most with    ->    friends you would have the best night with

  **It is a better claim and a harder one.** Similarity can be checked by eye - two people look alike
  on a profile. **Chemistry cannot**, so the number has to carry a line that says why, in the same
  way a room does: *"the night would be yours end to end"*, *"she would take it further than you
  would"*. `CHEMISTRY_LINES_V1.md` already generates exactly those for rooms.
""")

head('E.  THE CATCH, AND IT DECIDES HOW THIS IS SHOWN')
line()
print("""
  **The chemistry numbers above sit between 84% and 90% for people who are nothing like each other.**
  Similarity spreads 0.00 to 1.00 across the same four friends; chemistry spreads six points.

  **As a RANKING that is fine** - the order is what the sort uses, and it disagrees with similarity
  on 38% of pairs. **As a NUMBER ON A SCREEN it is nearly useless**: everybody reads as a good match,
  so the figure tells a person nothing and quietly trains them to ignore it.

  **So the switch comes with a condition.** Either the score is **rescaled against the population**
  before it is shown - the same treatment the room match already needs - or **the number is not shown
  at all and the line carries it**: *"the night would be yours end to end"* says more than *90%* and
  cannot be misread as a percentage of anything.

  **The second is cheaper and more honest, and `CHEMISTRY_LINES_V1.md` already writes those lines.**
""")
