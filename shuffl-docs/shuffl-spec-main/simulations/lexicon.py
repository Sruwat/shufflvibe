# -*- coding: utf-8 -*-
"""SCORING A VENUE FROM REVIEW TEXT - a lexicon method, run on Bohca's real corpus.

The principle that makes it work, from entry 145: POLARITY IS IRRELEVANT. "Too loud" and "amazing
energy" are the same evidence. We count what people DESCRIBE, not whether they liked it - so a
one-star review complaining about noise is as useful as a five-star one praising the atmosphere.
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- the lexicon
# factor -> pole -> [(pattern, weight)]
LEX = {
 'ENRG': {'hi': [('packed', 2), ('party till late', 3), ('party all night', 3), ('energetic', 3),
                 ('loud', 2), ('banging', 3), ('pumping', 3), ('crazy', 2), ('wild', 2),
                 ('dance floor', 3), ('till 1 ?am|till 2 ?am|late night', 2), ('bass', 2), ('buzzing', 2)],
          'lo': [('quiet', 3), ('chill', 2), ('relaxed', 2), ('calm', 2), ('peaceful', 3),
                 ('laid.?back', 2), ('intimate', 2), ('mellow', 2), ('cosy|cozy', 2)]},
 'CROWD':{'hi': [('packed', 3), ('crowded', 3), ('massive crowd', 3), ('queue|long line', 3),
                 ('no space|nowhere to (stand|sit)', 3), ('reserve.{0,20}in advance|book.{0,20}days', 3),
                 ('rush', 2), ('full', 2), ('waiting', 2)],
          'lo': [('empty', 3), ('deserted', 3), ('spacious', 2), ('plenty of (room|space)', 3),
                 ('no crowd', 3), ('easy to get a table', 3)]},
 'TALK': {'hi': [('conversation', 3), ('catch up', 3), ('hear each other', 3), ('can talk|could talk', 3),
                 ('quiet enough', 3), ('intimate', 2)],
          'lo': [("can.?t hear|cannot hear|couldn.?t hear", 3), ('too loud', 3), ('shouting|had to shout', 3),
                 ('deafening', 3), ('music.{0,15}too loud', 3), ('noisy', 2)]},
 'MOVE': {'hi': [('dance floor', 3), ('danc(e|ed|ing)', 3), ('groov', 2), ('moving to the beat', 3)],
          'lo': [('seated|sit.?down', 2), ('no dance floor', 3), ('table service only', 2)]},
 'FOCUS':{'hi': [('live band', 3), ('performance', 2), ('gig', 3), ('the set|their set', 2),
                 ('screen', 2), ('match', 2), ('stage', 3), ('watched', 2)],
          'lo': []},
 'FOOD': {'hi': [('food', 1), ('dish(es)?', 2), ('menu', 1), ('delicious', 3), ('tasty', 3),
                 ('flavou?r', 2), ('chef', 2), ('portions', 2), ('tapas', 2), ('starters', 2),
                 ('cocktail', 1)],
          'lo': [('no food', 2), ('food was (bad|poor|average)', 3)]},
 'LIVE': {'hi': [('live music', 3), ('live band', 3), ('gig', 3), ('singer', 2), ('artist', 2),
                 ('performance', 2)],
          'lo': [('dj', 1)]},                     # a DJ is evidence AGAINST live, see the note
 'POL':  {'hi': [('upscale', 3), ('elegant', 3), ('sophisticated', 3), ('dress code', 3),
                 ('classy', 3), ('posh', 3), ('expensive', 2), ('premium', 2), ('bouncer', 2),
                 ('guestlist|guest list', 3), ('entry', 1), ('trendy|hip|happening', 2)],
          'lo': [('casual', 2), ('divey|dive bar', 3), ('no.?frills', 3)]},
 'SCEN': {'hi': [('ambian?ce|ambien?ce', 3), ('decor', 3), ('interior', 2), ('beautiful', 2),
                 ('aesthetic', 3), ('view', 2), ('gorgeous', 3), ('lighting', 2), ('terrace', 2),
                 ('open ambiance', 3), ('rooftop', 2)],
          # 2026-10-05: the Kwality test scored SCEN 75 on reviews that say the decor is DATED.
          # "decor" fired as a hi keyword and nothing fired against it. The look of a room is the
          # one attribute reviewers criticise in plain words, so the lo list has to carry them.
          'lo': [('shabby', 3), ('run.?down', 3), ('dingy', 3), ('dated', 3), ('no frills', 3),
                 ('nothing fancy', 3), ('plain', 2), ('basic (decor|interiors?|place)', 3),
                 ('needs? (a )?renovation|needs doing up', 3), ('tired', 2), ('cramped', 2)]},
 # 2026-10-05: HERIT scored 47 on Kwality - a 1940 CP institution whose reviews say so five times
 # over. The list was museum vocabulary; people write about old places in ORDINARY words.
 'HERIT':{'hi': [('heritage', 3), ('historic', 3), ('colonial', 3), ('haveli', 3), ('old.?world', 3),
                 ('vintage', 2), ('traditional', 2), ('sufi|qawwali|ghazal|sitar', 3),
                 ('institution', 3), (r'since (18|19|20)\d\d', 3), (r'est(ablished)?\.? (18|19|20)\d\d', 3),
                 ('old.?school', 3), ('legendary', 2), ('iconic', 2), ('nostalgi', 3),
                 ('grand(parent|father|mother)', 3), ('generations?', 3), ('decades', 2),
                 ('one of the oldest|very old|years old', 3), ('landmark', 2),
                 ('piece of .{0,12}history|a bit of history', 3), ('has ?n.?t changed', 3)],
          'lo': [('brand new', 2), ('newly opened|just opened', 2)]},
 'GAMES':{'hi': [('board game', 3), ('pool table', 3), ('darts', 3), ('foosball', 3), ('arcade', 3)],
          'lo': []},
}

# ---------------------------------------------------------------- Bohca's real corpus
# Verbatim fragments gathered 2026-10-02 from Google/Zomato/JustDial/TripAdvisor/LBB/Wanderlog/
# Reviewpedia/Wheree/Postcard and Bohca's own Facebook. Polarity deliberately mixed.
CORPUS = [
 "This is one of the finest place for the late night party in Delhi. I am impressed with the ambiance and the music while enjoying their great food.",
 "Bohca is one of the best places to party till late. With amazing food, drinks and vibe.",
 "Expensive place! We had a bill of 4k plus per person with no food.",
 "So-so music, puking teenagers, smoky indoors, over smart bouncers. Not recommended for a night out.",
 "The club has terrible rules for entry. It does show attitude in entertaining the guests.",
 "What kind of dining place outcasts you based on your drive? It's only advisable to boycott this place.",
 "Mostly appreciated for Vibe, Seating and Event. Drinks and Cocktails are worth trying.",
 "Customers report variability in service quality; while some praise staff friendliness and efficiency, others mention inconsistent attentiveness.",
 "Overall, Bohca appears to serve as an upscale social space suitable for gatherings, celebrations like birthdays, or enjoying music-driven nights out.",
 "Make sure you reserve your table 2-3 days in advance for weekends.",
 "Bohca sprouted up earlier this year and, judging by the massive crowd inside, instantly became the weekend go-to for all of Delhi. You'll find potent LIITs.",
 "I couldn't resist moving to the beat and joining the energetic crowd on the dance floor. The staff at Bohca were truly exceptional.",
 "Had to wait to grab a table outside. Once settled, the service was quite neat. Started with Rawa Fish Fry and Srilankan Prawn Spring Roll and loved both.",
 "Sophisticated restaurant with a terrace, specialising in traditional tapas and sharing plates.",
 "With a wonderful open ambiance, lovely board games to keep you engrossed and food and drinks to satiate your every hunger, the Hoppi Sunday Brunch is a VFM.",
 "Music to expect: Bollywood, Punjabi, and English hits.",
 "Reservations required. All you can eat. Outdoor seating.",
]

NEG = re.compile(r"\b(not|no|never|without|hardly|barely)\b[^.]{0,22}$")

# FIX 1 - EXCLUSION CONTEXTS. "traditional tapas" is a cuisine, not heritage. Context-free matching
# is what made HERIT read 77 on a 2017 hotel bar.
EXCLUDE = {
 'HERIT': [r'traditional (tapas|food|cuisine|recipe|dish|spanish|italian)',
           r'(tapas|food|cuisine|dish)\S* traditional'],
 'POL':   [r'entry (level|fee)'],
}

# FIX 2 - THE TYPE IS THE PRIOR. The lexicon is EVIDENCE; the type says what to believe before
# reading anything. Same move as the energy curve and the club AFFIL constant - the third time it
# has come up, so it is the method rather than a patch.
TYPE_PRIOR = {
 'club':             dict(ENRG=88, CROWD=85, TALK=18, MOVE=85, FOCUS=25, FOOD=35, LIVE=15,
                          POL=72, SCEN=60, HERIT=10, GAMES=5),
 'big loud bar':     dict(ENRG=78, CROWD=76, TALK=35, MOVE=45, FOCUS=30, FOOD=50, LIVE=25,
                          POL=58, SCEN=52, HERIT=12, GAMES=20),
 'buzzy restaurant': dict(ENRG=52, CROWD=66, TALK=62, MOVE=15, FOCUS=25, FOOD=78, LIVE=18,
                          POL=58, SCEN=62, HERIT=20, GAMES=10),
 # 2026-10-05: `live room` was in pipeline.py's PRIOR_KEY and NOT here, so every live venue fell
 # through the no-prior path and scored at the extremes - a jazz club read ENRG 0 and TALK 100.
 # A type with no prior is not a neutral type; it is an UNDAMPED one.
 'live room':        dict(ENRG=62, CROWD=62, TALK=45, MOVE=30, FOCUS=85, FOOD=45, LIVE=90,
                          POL=55, SCEN=55, HERIT=15, GAMES=5),
 'cafe':             dict(ENRG=30, CROWD=45, TALK=78, MOVE=10, FOCUS=15, FOOD=75, LIVE=10,
                          POL=45, SCEN=68, HERIT=25, GAMES=15),
}
PRIOR_WEIGHT = 6.0      # evidence units needed before the lexicon outweighs the prior


def hits(text, pats, factor=None):
    t = text.lower(); total = 0; found = []
    for pat, w in pats:
        for m in re.finditer(pat, t):
            pre = t[max(0, m.start() - 24):m.start()]
            if NEG.search(pre):                    # crude negation window
                continue
            ctx = t[max(0, m.start() - 30):m.end() + 30]
            if factor and any(re.search(x, ctx) for x in EXCLUDE.get(factor, [])):
                continue                           # FIX 1: wrong sense of the word
            total += w; found.append(m.group(0))
    return total, found

def score(corpus, factor, vtype=None):
    hi, hf = 0, []
    lo, lf = 0, []
    for line in corpus:
        a, f1 = hits(line, LEX[factor]['hi'], factor); hi += a; hf += f1
        b, f2 = hits(line, LEX[factor]['lo'], factor); lo += b; lf += f2
    prior = TYPE_PRIOR.get(vtype, {}).get(factor)
    if hi + lo == 0:
        # FIX 3: no evidence is not no answer - fall back to the type's prior
        return (prior, 0, [], []) if prior is not None else (None, 0, [], [])
    raw = hi / float(hi + lo)
    reading = 50 + (raw - 0.5) * 100                # what the text alone says
    if prior is None:
        conf = min(1.0, (hi + lo) / 12.0)
        return round(50 + (reading - 50) * (0.45 + 0.55 * conf)), hi + lo, hf, lf
    # FIX 2: blend the reading toward the type's prior, weighted by evidence volume
    w = (hi + lo) / float(hi + lo + PRIOR_WEIGHT)
    return round(prior * (1 - w) + reading * w), hi + lo, hf, lf

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

if __name__ == '__main__':
    head('THE LEXICON METHOD, RUN ON BOHCA\'S REAL REVIEW CORPUS')
    print('%d fragments, gathered verbatim. Polarity deliberately mixed - that is the point.' % len(CORPUS))
    print()
    print('%-7s %7s %7s   %s' % ('factor', 'score', 'evidence', 'what it matched'))
    line()
    RESULT = {}
    VTYPE = 'club'          # Bohca after 22:00 on a weekend
    print('venue type for the prior: %s' % VTYPE)
    print()
    print('%-7s %7s %7s   %s' % ('factor', 'score', 'evidence', 'what it matched'))
    line()
    for f in ['ENRG', 'CROWD', 'TALK', 'MOVE', 'FOCUS', 'FOOD', 'LIVE', 'POL', 'SCEN', 'HERIT', 'GAMES']:
        s, n, hf, lf = score(CORPUS, f, VTYPE)
        RESULT[f] = s
        shown = ', '.join(dict.fromkeys(hf + ['NOT:' + x for x in lf]))[:58]
        print('%-7s %7s %7d   %s' % (f, s if s is not None else '-', n, shown))
    line()

    head('AGAINST THE HAND-BUILT ROW FROM THE BOHCA TEST')
    HAND = dict(ENRG=86, CROWD=92, TALK=25, MOVE=80, FOCUS=25, FOOD=68, LIVE=18, POL=78, SCEN=74,
                HERIT=10, GAMES=45)
    print('%-7s %10s %10s %8s' % ('factor', 'by hand', 'by lexicon', 'gap'))
    line()
    tot = n = 0
    for f in HAND:
        got = RESULT.get(f)
        if got is None:
            print('%-7s %10d %10s %8s' % (f, HAND[f], 'no evidence', '-')); continue
        g = abs(got - HAND[f]); tot += g; n += 1
        flag = '  <-- miss' if g > 25 else ''
        print('%-7s %10d %10d %8d%s' % (f, HAND[f], got, g, flag))
    line()
    print('mean gap on the %d factors with evidence: %.1f points' % (n, tot / n))
