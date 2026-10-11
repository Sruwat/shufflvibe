# -*- coding: utf-8 -*-
"""THE SWIPE SCORER - a runnable reference for ASSESSMENT_ENGINE.md sections 2, 4, 5, 6, 9 and
VIBE_NAMES_V5.md section 3.

Six identity factors (FACTORS_V6). Swipes in, a scored profile and a name out. Standard library
only, no state, no I/O - every function is pure so a developer can port it line by line.

    python assess.py            runs the worked examples at the bottom

WHAT THIS IS NOT: the card images, the deck UI, the timing capture, or storage. It is the maths
between a list of swipes and a stored profile.
"""
import sys, math, statistics as st
sys.stdout.reconfigure(encoding='utf-8')

# ================================================================= the constants, all from the spec
IDENTITY = ['ENRG', 'AFFIL', 'TALK', 'FOCUS', 'MOVE', 'SPONT']
WEIGHT   = dict(ENRG=18, AFFIL=16, TALK=14, FOCUS=14, MOVE=12, SPONT=10)

SWIPE = {'love': 88, 'up': 62, 'not': 38, 'pass': 12}      # section 2.1
EXTREME = ('love', 'pass')                                  # these end a factor; the others add a card

BROKEN_GAP   = 50     # section 5.1 - two cards this far apart are not measuring the same thing
SECOND_GAP   = 3      # section 2.4 - a B card lands at least this many positions later
MIN_FOR_LAT  = 5      # section 6.2 - fewer usable cards than this and latency cannot be ranked
GLOBAL_SCALE = 0.45   # log-seconds, the shared spread used until a person has their own
RESCALE_PART = 3.0    # section 9 - one third of the full correction, measured
PSD_FLOOR    = 5.0    # section 9 - a flat person divides by nothing
STICKY, SECOND_MIN = 15, 20                                 # VIBE_NAMES_V5 section 3.2


# ================================================================= 2.2  the adaptive deck
def deck_plan(swipes_in_order):
    """Which cards a session actually shows. `swipes_in_order` is what the user did to the A cards,
    in deck order: [(factor, swipe), ...]. Returns the full deck with B cards inserted.

    An extreme answer is believed and the factor is done. A mild one is checked with a second card
    from a different angle, at least SECOND_GAP positions later.
    """
    out = [(f, 'A', sw) for f, sw in swipes_in_order]
    for f, sw in swipes_in_order:
        if sw in EXTREME:
            continue
        # measure from where the A card sits NOW, not from its original index - inserting earlier
        # B cards shifts everything right, and measuring from the old index put a B card BEFORE
        # its own A card for the last factor in the deck.
        i = next(j for j, (ff, side, _) in enumerate(out) if ff == f and side == 'A')
        at = min(len(out), i + SECOND_GAP + 1)             # falls to the end when there is no room
        out.insert(at, (f, 'B', None))                     # queued; the answer is not known yet
    return out


def deck_length(n_mild, n_factors=6):
    """6 cards for somebody decisive, 12 for somebody mild on everything, about 9 for most."""
    return n_factors + n_mild


# ================================================================= 4  scoring one factor
def score_factor(cards):
    """cards = every answered card for ONE factor this session: one or two of them.
    Each card is a dict: {'swipe': 'love'|'up'|'not'|'pass', 'timed_out': bool}

    Returns (score, detail). An undefined factor stays undefined - NEVER substitute 50, because 50
    is a real neutral and this is an absence of data.
    """
    vals = [SWIPE[c['swipe']] for c in cards if not c.get('timed_out')]
    sws  = [c['swipe'] for c in cards if not c.get('timed_out')]
    if not vals:
        return None, dict(n_cards=0, gap=0, broken=False, refused=False, swipes=[])
    gap = max(vals) - min(vals) if len(vals) > 1 else 0
    return round(st.mean(vals)), dict(
        n_cards=len(vals),
        gap=gap,
        broken=len(vals) > 1 and gap >= BROKEN_GAP,         # section 5.1 - a fault in the cards
        # section 5.5: hard pass on any card, OR not-for-me on BOTH. The spec's one-line version
        # reads `all(sw == 'not')`, which is only correct for a FINISHED factor - a lone 'not'
        # queues a second card rather than ending anything, and the prose says so explicitly:
        # "a single not for me never ends a factor, so it is never a refusal on its own".
        refused=any(s == 'pass' for s in sws) or (len(sws) > 1 and all(s == 'not' for s in sws)),
        swipes=sws)


# ================================================================= 6.1  firmness from the score
def firmness_score(score):
    """0 at the centre, 1 at either end. Its known weakness: a person who compresses their answers
    has low firmness on everything by construction. 6.2 exists because of that."""
    return abs(score - 50) / 50.0 if score is not None else 0.0


# ================================================================= 6.2  firmness from latency
def latency_firmness(session, card_baseline=None, position_baseline=None, personal_scale=None):
    """session = [{'factor','side','total_latency_ms','first_position','exposures'}, ...]

    Every card counts, including the first three. The old warm-up rule discarded them as interface
    learning, and that premise is wrong about this deck: nobody playing the vibe game knows they
    are answering anything, so there is no instrument to learn. Discarding three of eight killed
    the tie-break on 61% of tied sheets.
    """
    card_baseline = card_baseline or {}
    position_baseline = position_baseline or {}
    usable = [a for a in session if a.get('exposures')]
    if len(usable) < MIN_FOR_LAT:
        return {}
    adj = {}
    for a in usable:
        adj[id(a)] = (math.log(max(a['total_latency_ms'], 1))
                      - card_baseline.get((a['factor'], a['side']), 0.0)
                      - position_baseline.get(a['first_position'], 0.0))
    centre = st.median(adj.values())
    scale = personal_scale or GLOBAL_SCALE
    per_card = {k: 1.0 / (1.0 + math.exp((v - centre) / scale)) for k, v in adj.items()}  # fast -> high
    out = {}
    for f in IDENTITY:
        mine = [per_card[id(a)] for a in usable if a['factor'] == f]
        if mine:
            out[f] = st.mean(mine)
    return out


# ================================================================= 9  rescaling
def rescale(scores, pop_mean, pop_sd):
    """People use the scale differently; one person's 4 is another's 5. Shift toward the population
    centre and stretch toward its spread, at ONE THIRD of the full correction.

    Full strength was tested and made retakes 37% LESS repeatable. A third leaves repeatability
    unchanged while still pulling a compressed person apart.

    pop_mean / pop_sd are RUNNING averages over every user so far, per factor - not a frozen table.
    """
    vals = [v for v in scores.values() if v is not None]
    if len(vals) < 2:
        return dict(scores)
    p_mean = st.mean(vals)
    p_sd = max(st.pstdev(vals), PSD_FLOOR)
    out = {}
    for f, s in scores.items():
        if s is None:
            out[f] = None; continue
        full = pop_mean[f] + (s - p_mean) * (pop_sd[f] / p_sd)
        out[f] = round(s + (full - s) / RESCALE_PART)
    return out


# ================================================================= 7 / VIBE_NAMES_V5  the name
FIRST_WORD = {
 'ENRG':  dict(low='Low-Key',     high='Peak'),
 'AFFIL': dict(low='Mingling',    high='Inner-Circle'),
 'TALK':  dict(low='Loud',        high='Talking'),
 'FOCUS': dict(low='Headline',    high='Front-Row'),
 'MOVE':  dict(low='Seated',      high='Moving'),
 'SPONT': dict(low='Locked-In',   high='Last-Minute'),
}
SECOND_WORD = {
 'ENRG':  dict(low='Slow-Burner', high='Climber'),
 'AFFIL': dict(low='Mingler',     high='Insider'),
 'TALK':  dict(low='Noise-Seeker',high='Table-Talker'),
 'FOCUS': dict(low='Headliner',   high='Front-Rower'),
 'MOVE':  dict(low='Sitter',      high='Floor-Filler'),
 'SPONT': dict(low='Planner',     high='Wildcard'),
}
SINGLE = {
 'ENRG':  dict(low='Slow Burner', high='Night Climber'),
 'AFFIL': dict(low='Room Worker', high='Inner Circle'),
 'TALK':  dict(low='Noise Seeker',high='Table Talker'),
 'FOCUS': dict(low='Headline Act',high='Front Row'),
 'MOVE':  dict(low='Sitter',      high='Floor Filler'),
 'SPONT': dict(low='Locked In',   high='Wild Card'),
}


def first_factor(scores, lat_firm):
    """Greatest |s - 50| + 5 x latency-firmness. Score decides; latency orders within a step."""
    live = {f: s for f, s in scores.items() if s is not None}
    return max(live, key=lambda f: abs(live[f] - 50) + 5 * lat_firm.get(f, 0.0))


def second_factor(scores, lat_firm, first):
    live = {f: s for f, s in scores.items() if s is not None}
    d_first = abs(live[first] - 50)
    d = {f: abs(live[f] - 50) for f in live if f != first}
    cands = [f for f in d if d[f] >= d_first - STICKY and d[f] >= SECOND_MIN]
    if not cands:
        return None
    hi = max(d[f] for f in cands)
    tied = [f for f in cands if d[f] == hi]
    if len(tied) == 1:
        return tied[0]
    return max(cands, key=lambda f: d[f] + 5 * lat_firm.get(f, 0.0))


def name(scores, lat_firm=None):
    lat_firm = lat_firm or {}
    first = first_factor(scores, lat_firm)
    second = second_factor(scores, lat_firm, first)
    pole = lambda f: 'high' if scores[f] >= 50 else 'low'
    if second is None:
        return SINGLE[first][pole(first)], first, None
    return '%s %s' % (FIRST_WORD[first][pole(first)], SECOND_WORD[second][pole(second)]), first, second


# ================================================================= the whole session
def run_session(answers, pop_mean=None, pop_sd=None, latency=None):
    """answers = {factor: [{'swipe': ...}, ...]}  -> everything the profile stores.

    Section 10: the raw score and the rescaled score are BOTH stored. The `refused` flag and the
    name read the RAW score; matching, blending and bend read the RESCALED one.
    """
    raw, detail = {}, {}
    for f in IDENTITY:
        s, d = score_factor(answers.get(f, []))
        raw[f], detail[f] = s, d
    lat = latency_firmness(latency, ) if latency else {}
    scaled = rescale(raw, pop_mean, pop_sd) if (pop_mean and pop_sd) else dict(raw)
    nm, first, second = name(raw, lat)
    return dict(raw=raw, rescaled=scaled, detail=detail, latency_firmness=lat,
                firmness={f: firmness_score(raw[f]) for f in IDENTITY},
                name=nm, first_factor=first, second_factor=second,
                n_cards=sum(d['n_cards'] for d in detail.values()))


# ================================================================= worked examples
if __name__ == '__main__':
    def line(c='-', n=92): print(c * n)
    def head(t):
        print(); print('=' * 92); print(t); print('=' * 92)

    POP_MEAN = dict(ENRG=55, AFFIL=52, TALK=56, FOCUS=48, MOVE=50, SPONT=47)
    POP_SD   = dict(ENRG=22, AFFIL=20, TALK=21, FOCUS=23, MOVE=22, SPONT=19)

    PEOPLE = [
     ('decisive - every card extreme', {
        'ENRG': [{'swipe': 'love'}], 'AFFIL': [{'swipe': 'pass'}], 'TALK': [{'swipe': 'love'}],
        'FOCUS': [{'swipe': 'pass'}], 'MOVE': [{'swipe': 'love'}], 'SPONT': [{'swipe': 'pass'}]}),
     ('mild on everything - 12 cards', {
        'ENRG': [{'swipe': 'up'}, {'swipe': 'up'}], 'AFFIL': [{'swipe': 'up'}, {'swipe': 'love'}],
        'TALK': [{'swipe': 'not'}, {'swipe': 'not'}], 'FOCUS': [{'swipe': 'up'}, {'swipe': 'not'}],
        'MOVE': [{'swipe': 'not'}, {'swipe': 'up'}], 'SPONT': [{'swipe': 'not'}, {'swipe': 'pass'}]}),
    ]
    # the A cards from the session of 2026-10-05. Only ENRG was extreme, so the other five each
    # queue a B card - this is an INCOMPLETE session and the scores below are provisional.
    AC = [('ENRG', 'love'), ('AFFIL', 'up'), ('TALK', 'up'),
          ('FOCUS', 'not'), ('MOVE', 'up'), ('SPONT', 'not')]
    head('A.  THREE SESSIONS, END TO END')
    for label, ans in PEOPLE:
        r = run_session(ans, POP_MEAN, POP_SD)
        print()
        print('  %s   -   %d cards answered' % (label, r['n_cards']))
        print('     raw      ', '  '.join('%s %3s' % (f, r['raw'][f]) for f in IDENTITY))
        print('     rescaled ', '  '.join('%s %3s' % (f, r['rescaled'][f]) for f in IDENTITY))
        flags = [('%s %s' % (f, 'BROKEN' if d['broken'] else 'refused'))
                 for f, d in r['detail'].items() if d['broken'] or d['refused']]
        print('     flags    ', ', '.join(flags) or 'none')
        print('     NAME      %s   (first %s, second %s)'
              % (r['name'], r['first_factor'], r['second_factor'] or '-'))

    head('A2.  AN INCOMPLETE SESSION - the A cards of 2026-10-05')
    prov = {f: [{'swipe': sw}] for f, sw in AC}
    r = run_session(prov, POP_MEAN, POP_SD)
    print('     A cards  ', '  '.join('%s %-5s' % (f, sw) for f, sw in AC))
    print('     so far   ', '  '.join('%s %3s' % (f, r['raw'][f]) for f in IDENTITY))
    print('     NAME      %s  (provisional)' % r['name'])
    plan = deck_plan(AC)
    print('     the deck  %d cards: %s' % (len(plan), ' '.join('%s%s' % (f, s) for f, s, _ in plan)))
    print('''
  Only ENRG was extreme, so five factors each queue a second card and the deck runs to eleven.
  **Those five scores are provisional** - a B card answered differently moves them, and FOCUS
  answered 'not' a second time would become a refusal where one card alone never can.''')

    head('B.  THE PAIR TABLE OF SECTION 2.2, REPRODUCED BY score_factor()')
    print('  the second card resolves the lean - these four rows are just the MEAN of the two cards')
    line()
    print('  %-12s %-12s %6s   %s' % ('first', 'second', 'score', 'reads as'))
    for a, b, reads in (('up', 'love', 'lean confirmed and strengthened'),
                        ('up', 'up', 'mild yes, confirmed'),
                        ('up', 'not', 'true neutral'),
                        ('up', 'pass', 'BROKEN PAIR - the two cards disagree')):
        s, d = score_factor([{'swipe': a}, {'swipe': b}])
        print('  %-12s %-12s %6d   %s%s' % (a, b, s, reads, '  <- flagged' if d['broken'] else ''))
    line()

    head('C.  DECK LENGTH')
    for n_mild in (0, 3, 6):
        print('  %d factors answered mildly -> %2d cards' % (n_mild, deck_length(n_mild)))
    print('''
  Six for somebody decisive, twelve for somebody who leans mildly on everything, about nine for
  most - without ever asking anyone how sure they are.''')

    head('D.  WHAT A FLAT PERSON LOOKS LIKE BEFORE AND AFTER RESCALING')
    flat = {f: 62 for f in IDENTITY}; flat['ENRG'] = 38
    print('     raw      ', '  '.join('%s %3d' % (f, flat[f]) for f in IDENTITY))
    print('     rescaled ', '  '.join('%s %3d' % (f, v) for f, v in rescale(flat, POP_MEAN, POP_SD).items()))
    print('''
  The spread widens but the order is untouched, and it moves by a third of the way, not all of it.
  Full strength was tested and made retakes 37% LESS repeatable.''')
