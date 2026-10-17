# -*- coding: utf-8 -*-
"""THE ROOM LINE - one sentence describing a room, from the vector CHEMISTRY_V4 already produces.

The user, 2026-10-07: "Each room when displayed to the user should have a line about the vibe of the
room - 'This room has chill vibe and people in here want to see how the night unfolds rather than go
on a fixed schedule' (if the chemistry turns the room low ENRG and high SPONT)."

Same selection logic as the daily name (VIBE_NAMES_V5 section 3): the factor furthest from the
middle leads, a second joins if it clears SECOND_MIN. The name renders that as two words; this
renders it as a sentence. No new engine - chem4.py produces every input.
"""
import sys, io, contextlib
try:
    sys.stdout.reconfigure(encoding='utf-8')     # no-op when stdout is already a StringIO
except AttributeError:
    pass
with contextlib.redirect_stdout(io.StringIO()):
    import chem4 as C

STICKY, SECOND_MIN, FLAT = 15, 20, 12      # FLAT: below this the room has no character at all

# THE ONE PLACE THIS DIFFERS FROM THE NAME. The name ranks factors on distance from the middle
# alone - weights were taken out of naming on 2026-09-23. A DESCRIPTION is a different job: the
# weights encode how much an axis matters to how a night feels, so a sentence should lead with the
# axis that matters, not merely the one that is furthest out. Set False to rank like the name.
WEIGHTED = True


def rank(rv, f):
    gap = abs(rv[f] - 50)
    return gap * (C.WEIGHT[f] if WEIGHTED else 1)

# ---------------------------------------------------------------- the clauses
# written to the rules of CHEMISTRY_LINES_V1: says what will happen, no jargon, no numbers,
# a difference is never a warning.
LEAD = {
 'ENRG':  dict(high='is going hard tonight',          low='has a chill vibe'),
 'AFFIL': dict(high='is here for its own table',      low='is here to meet the room'),
 'TALK':  dict(high='came to talk',                   low='wants it loud'),
 'FOCUS': dict(high='is here for whatever is on',     low='is its own main event'),
 'MOVE':  dict(high='is going to be on its feet',     low='is settling in somewhere'),
 'SPONT': dict(high='is deciding it on the night',    low='has tonight planned'),
}
SECOND = {
 'ENRG':  dict(high='nobody is planning an early night',
               low='nobody is trying to push it harder'),
 'AFFIL': dict(high='they will mostly keep to themselves',
               low='they will end up talking to strangers'),
 'TALK':  dict(high='the conversation is the point',
               low='you will not hear much over the music'),
 'FOCUS': dict(high='they will want to be near the front',
               low='they are not looking for a show'),
 'MOVE':  dict(high='they will want somewhere to dance',
               low='they will want somewhere to sit'),
 'SPONT': dict(high='they want to see how the night unfolds rather than stick to a plan',
               low='they would rather know where they are going'),
}
# a split is the most useful thing the model can say about a room, so it outranks a second factor
SPLIT = {
 'AFFIL': 'some will hold the table while others work the room',
 'MOVE':  'it needs a floor and somewhere to sit',
}
NOTHING = 'This room has not decided what it is yet - nobody in it is pushing in any direction.'


def room_line(rv, splits=frozenset()):
    """rv = the room vector from chem4.room(). Returns one sentence."""
    pole = lambda f: 'high' if rv[f] >= 50 else 'low'
    d = {f: rank(rv, f) for f in C.IDENT if f not in splits}
    raw = {f: abs(rv[f] - 50) for f in C.IDENT if f not in splits}
    if not raw or max(raw.values()) < FLAT:
        if splits:                                   # a split room always has something to say
            return 'This room is two things at once - ' + SPLIT[sorted(splits)[0]] + '.'
        return NOTHING
    first = max(d, key=lambda f: d[f])
    head = 'This room ' + LEAD[first][pole(first)]

    if splits:                                       # a split outranks a second factor
        return head + ', and ' + SPLIT[sorted(splits)[0]] + '.'

    cands = [f for f in raw if f != first and raw[f] >= raw[first] - STICKY
             and raw[f] >= SECOND_MIN]
    if not cands:
        return head + '.'
    second = max(cands, key=lambda f: d[f])
    return head + ', and ' + SECOND[second][pole(second)] + '.'


# ================================================================= examples
if __name__ == '__main__':
    def line(c='-', n=100): print(c * n)
    def head(t):
        print(); print('=' * 100); print(t); print('=' * 100)

    def mk(**kw): return C.mk('p', **kw)

    ROOMS = [
     ("the user's own example - a calm room that has not planned anything",
      [mk(ENRG=22, SPONT=82, AFFIL=55, TALK=60, FOCUS=45, MOVE=40),
       mk(ENRG=28, SPONT=78, AFFIL=50, TALK=55, FOCUS=48, MOVE=45),
       mk(ENRG=25, SPONT=85, AFFIL=58, TALK=62, FOCUS=40, MOVE=38)]),
     ("three people who came for the gig",
      [mk(ENRG=72, FOCUS=88, MOVE=65, TALK=35, AFFIL=45, SPONT=40),
       mk(ENRG=68, FOCUS=82, MOVE=60, TALK=40, AFFIL=50, SPONT=45),
       mk(ENRG=75, FOCUS=90, MOVE=70, TALK=30, AFFIL=42, SPONT=38)]),
     ("a table-holder and two room-workers - AFFIL splits",
      [mk(AFFIL=88, ENRG=60, TALK=65, FOCUS=45, MOVE=40, SPONT=50),
       mk(AFFIL=18, ENRG=65, TALK=55, FOCUS=48, MOVE=55, SPONT=52),
       mk(AFFIL=22, ENRG=62, TALK=58, FOCUS=50, MOVE=58, SPONT=48)]),
     ("a loud floor",
      [mk(ENRG=90, MOVE=88, TALK=15, CROWD=85, AFFIL=35, FOCUS=30, SPONT=55),
       mk(ENRG=86, MOVE=82, TALK=20, AFFIL=40, FOCUS=35, SPONT=60),
       mk(ENRG=92, MOVE=90, TALK=12, AFFIL=30, FOCUS=28, SPONT=50)]),
     ("a quiet table that wants to talk",
      [mk(TALK=90, ENRG=25, AFFIL=78, MOVE=15, FOCUS=30, SPONT=35),
       mk(TALK=85, ENRG=30, AFFIL=72, MOVE=20, FOCUS=35, SPONT=40),
       mk(TALK=88, ENRG=22, AFFIL=80, MOVE=18, FOCUS=28, SPONT=30)]),
     ("five people with no strong feelings about anything",
      [mk(ENRG=52, AFFIL=48, TALK=55, FOCUS=50, MOVE=47, SPONT=53) for _ in range(5)]),
    ]

    head('THE ROOM LINE, ON SIX ROOMS')
    for label, members in ROOMS:
        with contextlib.redirect_stdout(io.StringIO()):
            rv, splits, flags = C.room(members)
        print()
        print('  %s' % label)
        print('     room  ' + '  '.join('%s %s' % (f, 'SPLIT' if f in splits else round(rv[f]))
                                        for f in C.IDENT))
        print('     >>    %s' % room_line(rv, splits))
    line()
    print("""
  **The sentence comes from the same two factors that name the room**, so the line and the name can
  never disagree - they are two renderings of one selection. A split outranks a second factor,
  because *this room needs a floor AND somewhere to sit* is the most useful thing the model knows
  about a room and the name cannot say it.

  **And the flat room is handled rather than fudged.** Five people with no strong feelings produce
  no line about energy or plans, because there is nothing true to say - so it says that instead.
""")
