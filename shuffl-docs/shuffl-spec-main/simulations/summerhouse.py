# -*- coding: utf-8 -*-
"""BLIND RUN - Summer House Cafe, Aurobindo Place Market, on the lexicon method.
Corpus gathered 2026-10-02 from Google, TripAdvisor, JustDial, Wanderlog, Time Out, District,
LBB, Delhi10, Reddit and the venue's own Instagram. Verbatim, polarity mixed."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import lexicon as L

# the evening type prior this venue needs
L.TYPE_PRIOR['live room'] = dict(ENRG=62, CROWD=72, TALK=45, MOVE=55, FOCUS=78, FOOD=58,
                                 LIVE=88, POL=45, SCEN=62, HERIT=22, GAMES=8)
L.TYPE_PRIOR['lounge / rooftop'] = dict(ENRG=55, CROWD=60, TALK=58, MOVE=30, FOCUS=28, FOOD=62,
                                        LIVE=35, POL=60, SCEN=78, HERIT=18, GAMES=8)

CORPUS = [
 "Relaxed cafe with vibrant decor and a big terrace serving American and Western-style fare and cocktails.",
 "It's a really vibey, hipster type venue with good fun, good food, good music.",
 "Best place to dance in delhi. The music was good and crowd was great.",
 "Summer House Cafe offers a laid-back and urban vibe with warm wood textures and a rooftop setting perfect for any occasion.",
 "Summer House Cafe is a nice spot to grab a drink or catch up with friends while listening to interesting music. They host Boxout Wednesdays every week.",
 "Summer House Cafe is one of the best places to hang out in hauz khas. They have both indoor as well as outdoor seating options.",
 "Went to Summer House Cafe yesterday at around 7pm and found this place to be completely packed. The service was fast and staff was very polite.",
 "Summer House had already established its premier position with its ambiance and music. Their new food menu acts like a cherry on top.",
 "Presenting a new midweek ritual for Delhi's live independent sound. Fresh energy every Wednesday at Summer House Cafe.",
 "Summer House Cafe operates as a bar-lounge and live-music venue rather than a pure nightclub.",
 "Summer House Cafe is a great spot for those looking for a lively atmosphere and a variety of cuisines. While the service can be hit-or-miss, the food and drinks are good.",
 "The terrace at Summer House Cafe immediately puts you in a relaxed frame of mind. It is a highly popular aesthetic date spot during the day.",
 "Everyone wears whatever the hell they want. One of the best queer-inclusive bars in Delhi.",
 "If you're lucky, you might just catch some live music too. You can always head to Summer House Cafe if you want to party harder.",
 "Bro i was denied the entry as I was stag and that too in the evening around 5 pm on a Saturday, whats the scene with Summer house?",
 "Listed among the best jazz bars and jazz clubs in New Delhi.",
 "Where to sing karaoke with your crew in Delhi.",
]

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

head('SUMMER HOUSE CAFE - BLIND RUN')
print('Google 4.2 / 9,403   JustDial 4.0 / 15,068   TripAdvisor 3.8 / 158   closes 01:00')
print('Google type: Cafe. "Relaxed cafe with vibrant decor and a big terrace."  In: Auro Kitchen Bar')
print()
FACTORS = ['ENRG', 'CROWD', 'TALK', 'MOVE', 'FOCUS', 'FOOD', 'LIVE', 'POL', 'SCEN', 'HERIT', 'GAMES']
for vtype in ('lounge / rooftop', 'live room'):
    print()
    print('  --- scored with the %s prior ---' % vtype.upper())
    print('  %-7s %7s %8s   %s' % ('factor', 'score', 'evidence', 'matched'))
    line()
    for f in FACTORS:
        s, n, hf, lf = L.score(CORPUS, f, vtype)
        shown = ', '.join(dict.fromkeys(hf + ['NOT:' + x for x in lf]))[:52]
        print('  %-7s %7s %8d   %s' % (f, s if s is not None else '-', n, shown))
    line()

head('AND AGAINST BOHCA - the method has to SEPARATE them, not just score them')
BOHCA = dict(ENRG=96, CROWD=90, TALK=18, MOVE=94, FOCUS=25, FOOD=58, LIVE=15, POL=90, SCEN=86,
             HERIT=10, GAMES=37)
print('%-7s %12s %14s %9s   %s' % ('factor', 'Bohca', 'Summer House', 'gap', 'does it separate them?'))
line()
sep = 0
for f in FACTORS:
    sh, _, _, _ = L.score(CORPUS, f, 'live room')
    b = BOHCA[f]
    g = abs(sh - b)
    if g >= 20: sep += 1
    mark = 'YES, clearly' if g >= 30 else ('yes' if g >= 20 else 'no - reads alike')
    print('%-7s %12d %14d %9d   %s' % (f, b, sh, g, mark))
line()
print('%d of %d factors separate the two venues by 20 points or more.' % (sep, len(FACTORS)))
