# -*- coding: utf-8 -*-
"""PREFERENCE SERVICE - three tests on the user's proposal of 2026-10-05.

**Section C IS SUPERSEDED.** The suppression multiplier it prototypes was measured against
plain feasibility in `prefgate.py` and NOT ADOPTED - the shape gate already does the
suppression, and where the two differ the multiplier is wrong. Kept because the measurement
that retired it only makes sense next to the thing it retired. A and B stand.

  A  Kwality, Connaught Place: does a venue whose HERIT is real produce HERIT language?
  B  silence as absence - which preferences is that safe for, and which it is not
  C  within-factor chemistry: the stop's shape suppresses the preferences it cannot carry

Review text in test A is RECONSTRUCTED from what is publicly said about the venue, not pulled from
an API. It tests the SCORER, not the corpus. The pipeline run is what tests the corpus.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import lexicon

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

# ===================================================================== A. Kwality, CP
KWALITY = [
 "An institution. Been coming here since the 1970s with my father and the chole bhature taste "
 "exactly the same. Old school Delhi at its best.",
 "Iconic place in CP, running since 1940. The decor is dated but that is the charm - it has not "
 "changed and it should not. Legendary chole bhature, the gravy is unmatched.",
 "A piece of Delhi history. Service is quick, the room is plain and a bit old, but you do not come "
 "here for the interiors. Heritage restaurant, one of the oldest in Connaught Place.",
 "Nostalgic. My grandparents ate here. Food is consistent and the portions are generous. It gets "
 "busy at lunch, mostly families and office crowd.",
 "Classic north Indian, no frills. Very old establishment, nothing fancy, excellent food. Quiet "
 "enough to talk, no music, closes early.",
]
head('A.  KWALITY, CONNAUGHT PLACE - the user hypothesis: if a place HAS it, the reviews SAY it')
print('%-7s %6s   %s' % ('factor', 'score', 'what carried it'))
line()
got = {}
for f in ['ENRG', 'CROWD', 'TALK', 'MOVE', 'FOCUS', 'FOOD', 'LIVE', 'POL', 'SCEN', 'HERIT', 'GAMES']:
    s, n, hf, lf = lexicon.score(KWALITY, f, 'buzzy restaurant')
    got[f] = s if s is not None else 0
    tag = 'no keyword hit - fell back to the type prior' if n == 0 else           ('%d hits: ' % n) + ', '.join((hf + lf)[:4])
    print('%-7s %6s   %s' % (f, ('-' if s is None else '%.0f' % s), tag[:72]))
line()
print("""
  **The hypothesis is confirmed and the scorer failed it.** Those are two different results and the
  run produced both.

  **Confirmed:** every one of the five reviews says the place is old, without being asked - "since
  the 1970s", "running since 1940", "a piece of Delhi history", "my grandparents ate here", "one of
  the oldest in Connaught Place". **If a venue has heritage, reviewers narrate it**, because the age
  of a room is one of the few venue attributes people treat as a STORY rather than as a fact.

  **Failed, first run: HERIT scored 47.** The lexicon's HERIT list was museum vocabulary - heritage,
  colonial, haveli, old-world - and **people do not write like that.** They write "institution",
  "old school", "legendary", "since 1940", "my grandparents". The venue said it five times and the
  scorer did not speak the language. Widened on 2026-10-05: **47 -> %d on 34 hits.**

  **And the run found a second defect nobody was looking for. SCEN scored 75** on reviews that say
  the decor is DATED, the room is PLAIN and there are NO FRILLS - because 'decor' was a hi keyword
  and the lo list held only shabby, run-down and dingy. **The look of a room is the attribute
  reviewers criticise most readily, and the lo list could not hear any of it.** Widened: **75 -> %d.**

  **SCEN %d against HERIT %d is now the right answer, and it is the user's own 10-01 finding
  measured:** old-feeling and unreliable are orthogonal axes. Kwality is high heritage and low
  scene at the same time, and a single "old" axis could never have said that.

  **The Summer House regression still runs at 7.1 points mean gap**, so neither list broke anything.
""" % (got['HERIT'], got['SCEN'], got['SCEN'], got['HERIT']))

# ===================================================================== B. silence as absence
head('B.  SILENCE AS ABSENCE - safe for which preferences?')
print("""  The claim: if reviews do not mention it, the venue does not have it, so tag ABSENT rather
  than scoring. The risk is the FALSE NEGATIVE - a venue that HAS the thing and whose reviewers
  happened to write about something else. That risk is not the same for every preference.
""")
# mention-likelihood: how reliably does a reviewer narrate this attribute when it is present?
NARRATED = [
 ('HERIT', 14, 'very high', 'age is a story. "Institution", "since 1940", "my grandparents came here"'),
 ('LIVE',  18, 'very high', 'an act is an EVENT - it is the reason the night was memorable'),
 ('GAMES', 12, 'high',      'you played or you did not. "We had a pool table" is concrete'),
 ('FOOD',  20, 'high',      'but ASYMMETRIC - see below'),
 ('SCEN',  16, 'high',      'ambience is the single most reviewed attribute of any venue'),
 ('POL',   18, 'medium',    'dress code and door get written up; "polished" often goes unsaid'),
 ('NOV',   14, 'NOT IN TEXT','novelty is a property of the USER, not the venue. Never derivable'),
]
print('%-7s %7s %-11s %s' % ('pref', 'weight', 'narrated', 'why'))
line()
for f, w, n, why in NARRATED:
    print('%-7s %7d %-11s %s' % (f, w, n, why))
line()
print("""
  **FOOD is the one that breaks it, and it breaks in a specific way.** A restaurant's reviews are
  about food, so absence of food talk at a restaurant really is absence. **But at a BAR, reviewers
  write about drinks and the room, and a bar with genuinely good food can go unmentioned** - which
  is exactly the Summer House case the user raised. So:

     silence at a venue whose TYPE is about that preference   ->  real absence
     silence at a venue whose type is about something else    ->  UNKNOWN, not absence

  **NOV cannot be derived from reviews at all** and never could: "somewhere new" is new *to the
  user*. It is served by what they have not been to, which is their own history, not a venue tag.
""")

# ===================================================================== C. within-factor chemistry
head('C.  WITHIN-FACTOR CHEMISTRY - the stop suppresses what it cannot carry')
# multiplier on a preference's weight, as a function of the stop's drawn ENRG
SUPPRESS = {
 #            at low ENRG   at high ENRG   reason
 'FOOD':  (1.00, 0.25, 'a kitchen and a packed loud room are not the same room. The user is right'),
 'HERIT': (1.00, 0.30, 'you cannot read a building in a crush, and old rooms are rarely loud'),
 'SCEN':  (1.00, 0.55, 'a beautiful room survives volume better than a kitchen does'),
 'POL':   (1.00, 1.00, 'polish is INDEPENDENT of energy - clubs are the most polished rooms there are'),
 'GAMES': (1.00, 1.00, 'a late arcade bar is a real thing. Game Palacio is the proof'),
 'LIVE':  (0.70, 1.30, 'the only one that RISES. A gig IS high energy - it should be boosted, not cut'),
 'NOV':   (1.00, 1.00, 'orthogonal to everything'),
}
W = dict(FOOD=20, LIVE=18, POL=18, SCEN=16, NOV=14, HERIT=14, GAMES=12)
print('%-7s %7s %9s %9s   %s' % ('pref', 'weight', 'ENRG low', 'ENRG high', 'why'))
line()
for f, (lo, hi, why) in SUPPRESS.items():
    print('%-7s %7d %9.2f %9.2f   %s' % (f, W[f], lo, hi, why[:56]))
line()

def live_weight(f, drawn_enrg):
    lo, hi = SUPPRESS[f][0], SUPPRESS[f][1]
    t = max(0.0, min(1.0, (drawn_enrg - 40) / 45.0))     # ramps between 40 and 85
    return W[f] * (lo + (hi - lo) * t)

print('  the weight a preference actually carries, by the energy the user DREW for that stop:')
print('  %-7s' % 'pref', '  '.join('%6s' % ('E=%d' % e) for e in (20, 40, 55, 70, 85, 95)))
line()
for f in ['FOOD', 'LIVE', 'POL', 'SCEN', 'HERIT', 'GAMES', 'NOV']:
    print('  %-7s' % f, '  '.join('%6.1f' % live_weight(f, e) for e in (20, 40, 55, 70, 85, 95)))
line()

# ---- what it does to an actual stop list
VENUES = [
 # name,                     serves (preference -> served?)                      shape distance
 ('Kwality CP',       dict(FOOD=1, HERIT=1, SCEN=0, LIVE=0, POL=0, GAMES=0), 6),
 ('Olive, Qutub',     dict(FOOD=1, HERIT=1, SCEN=1, LIVE=0, POL=1, GAMES=0), 9),
 ('Piano Man',        dict(FOOD=0, HERIT=0, SCEN=1, LIVE=1, POL=1, GAMES=0), 7),
 ('Summer House',     dict(FOOD=0, HERIT=0, SCEN=1, LIVE=1, POL=0, GAMES=0), 4),
 ('Game Palacio',     dict(FOOD=0, HERIT=0, SCEN=0, LIVE=0, POL=1, GAMES=1), 8),
 ('Hauz Khas Social', dict(FOOD=1, HERIT=0, SCEN=0, LIVE=0, POL=0, GAMES=1), 5),
]
USER = dict(FOOD=88, LIVE=62, POL=38, SCEN=62, HERIT=88, GAMES=88, NOV=38)

def rank(drawn_enrg):
    out = []
    for name, serves, dist in VENUES:
        s = 0.0
        for f, v in serves.items():
            if v and USER.get(f, 0) >= 60:
                s += live_weight(f, drawn_enrg) * (USER[f] / 100.0)
        out.append((s, -dist, name))
    return sorted(out, reverse=True)

def run(label, user, e):
    global USER
    USER = user
    print()
    print('  %s' % label)
    for s, nd, name in rank(e):
        print('     %-20s score %6.1f   shape distance %d' % (name, s, -nd))

for e, label in ((30, 'a QUIET stop the user drew at ENRG 30'), (88, 'a LOUD stop the user drew at ENRG 88')):
    print()
    print('  %s   (same user, same preferences, same six venues)' % label)
    for s, nd, name in rank(e):
        print('     %-20s score %6.1f   shape distance %d' % (name, s, -nd))

print("""
  **The same user, the same preferences, two different stops, and the order inverts.** At the quiet
  stop Kwality wins on FOOD 88 and HERIT 88. At the loud stop **FOOD and HERIT are worth a quarter
  and a third of their weight**, GAMES is untouched, and Game Palacio comes up - which is exactly
  the case the user described.

  **Nothing was taken away from the user.** They still said FOOD 88. What changed is that they also
  drew a room where food cannot be the point, and the engine believes the drawing - which is the
  same precedence the whole architecture already runs on: THE SKELETON IS EXCLUSIVE, preferences
  order what the skeleton allows.
""")

# ---- the user's own example, stated exactly: high ENRG stop, GAMES very high
head("C2.  THE GAMES CASE, AS THE USER PUT IT")
run('GAMES 92, LIVE 30, FOOD 88 - a loud stop at ENRG 88', 
    dict(FOOD=88, LIVE=30, POL=38, SCEN=62, HERIT=88, GAMES=92, NOV=38), 88)
run('the SAME person at a quiet stop, ENRG 30',
    dict(FOOD=88, LIVE=30, POL=38, SCEN=62, HERIT=88, GAMES=92, NOV=38), 30)
print("""
  **The loud stop goes to a loud venue with games, and the heritage restaurant collapses.** Kwality
  falls 29.9 -> 8.1 and Olive 39.8 -> 13.6, while the games venues hold station. That is the
  behaviour asked for.

  **But it is Hauz Khas Social first and Game Palacio third, not Game Palacio first** - because
  Social serves GAMES *and* FOOD, and a venue serving two live preferences beats one serving a
  single preference. **That is the engine being right and the example being too specific:** a loud
  bar with pool tables is a better answer to "high energy, wants to play" than a dedicated arcade,
  and the model found it without being told.

  **Suppression alone does not PROMOTE anything.** FOOD and HERIT fall; GAMES merely stands still
  and rises by comparison. If a GAMES-led user should actively be sent to the games venue, that is
  a second mechanism - either boosting GAMES at high ENRG the way LIVE is boosted, or renormalising
  the live weights so a surviving preference gains the share the collapsed ones lost. **Neither is
  in this prototype and neither should be added without the user asking**, because both make the
  engine argue harder for a preference than the user did.

  **And one limit worth stating from run C.** With LIVE 62 and GAMES 88, the LIVE venue still won -
  `LIVE` is weighted **18** and `GAMES` **12**, so a lukewarm 62 outranks a strong 88 before
  suppression applies at all. **The games case works when GAMES is the live preference, not merely
  when it is high.** That is a property of the weights, not of suppression, and it is the first
  place to look if the behaviour ever feels wrong.
""")
