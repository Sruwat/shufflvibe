# -*- coding: utf-8 -*-
"""YOU AGAINST THE ROOM - the read a person gets before deciding whether to join.

`roomline.py` says what a room IS. This says what YOU would be in it. Both run off the vector
`chem4.py` already produces, plus two numbers it already computes:

    match        how close you are to the room's identity
    disturbance  how much the room moves when you join

Those two came apart when they were measured (CHEMISTRY_V4 section 9: r = -0.59, and only 40% of
the best-matched rooms are also the least-disturbed), so **the headline uses both**. A room can be
your kind of room that you would still tip, or not your kind at all and immovable.
"""
import sys, io, contextlib
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
with contextlib.redirect_stdout(io.StringIO()):
    import chem4 as C

GAP = 18          # below this you and the room are pitched the same. Judgement.
MATCH_HI, MATCH_LO = 0.80, 0.70
DIST_HI, DIST_LO = 0.090, 0.047   # terciles of the ADOPTED model over 6,000 joins, 2026-10-07.
                                  # The first re-cut used 0.073/0.033, taken from a preview that
                                  # still counted mid people as neutrals as well as advocates;
                                  # removing that double-count raised disturbance instead of
                                  # lowering it, and those bands put 11% of reads in the low band
                                  # where they should hold a third.

# ---------------------------------------------------------------- per-axis, three relations
# above  = the room sits ABOVE you on this axis
# level  = within GAP
# below  = the room sits BELOW you
AXIS = {
 'ENRG': dict(above='They will take this further than you would have.',
              level='You are pitched where they are, so nobody is dragging anybody.',
              below='You will be the one pushing this room along.'),
 'AFFIL':dict(above='They will stay at their own table longer than you would.',
              level='You face the night the same way they do.',
              below='They will be off meeting people while you would rather hold the table.'),
 'TALK': dict(above='They came to talk. You would take it louder than this.',
              level='You and they want the same volume.',
              below='It will be louder than you would have picked, so do not plan on talking.'),
 'FOCUS':dict(above='They are here for whatever is on. You would be fine without it.',
              level='You want the same amount of main event as they do.',
              below='They are the event themselves. You would have liked something to watch.'),
 'MOVE': dict(above='They will be on their feet before you are.',
              level='You will be standing and sitting at the same times they are.',
              below='You will be the first one up.'),
 'SPONT':dict(above='They are deciding it as it goes. You would rather have it set.',
              level='You and they want the same amount of plan.',
              below='They have it planned. You would have left it looser.'),
}
SPLIT = {
 ('AFFIL', 'high'): 'There is a table in this room, and it is yours.',
 ('AFFIL', 'low'):  'Half this room is working the floor. That half is yours.',
 ('MOVE',  'high'): 'There is a floor here and people already on it.',
 ('MOVE',  'low'):  'There is somewhere to sit here, and people sitting.',
 ('AFFIL', 'mid'): 'This room is in two halves and you are not firmly in either - take whichever suits.',
 ('MOVE',  'mid'): 'Some are on the floor and some are sitting. You could take either.',
}
HEAD = {
 ('hi', 'lo'): 'YOU WOULD SLOT STRAIGHT IN',
 ('hi', 'hi'): 'YOUR KIND OF ROOM, AND YOU WOULD SET THE TONE',
 ('hi', 'mid'): 'YOUR KIND OF ROOM',
 ('lo', 'lo'): 'THIS IS THEIR NIGHT, AND IT WILL NOT BEND',
 ('lo', 'hi'): 'YOU WOULD CHANGE THIS ROOM',
 ('lo', 'mid'): 'A DIFFERENT NIGHT FROM YOURS',
 ('mid', 'hi'): 'YOU WOULD MOVE THIS ROOM',
 ('mid', 'lo'): 'YOU WOULD BARELY CHANGE THIS ROOM',
 ('mid', 'mid'): 'YOU WOULD FIND YOUR PLACE',
}


def band(v, hi, lo):
    return 'hi' if v >= hi else ('lo' if v < lo else 'mid')


def read(user, members, top=3):
    """Returns (headline, [lines], match, disturbance)."""
    with contextlib.redirect_stdout(io.StringIO()):
        rv, splits, _ = C.room(members)
        m = C.match(user, rv, members, splits)
        dist = C.disturbance(user, members)
    mb = band(m, MATCH_HI, MATCH_LO)
    db = band(dist, DIST_HI, DIST_LO)
    headline = 'THERE IS A HALF OF THIS ROOM FOR YOU' if splits else HEAD[(mb, db)]

    lines, used = [], set()
    for f in sorted(splits):                       # a split is always worth saying first
        v = user.vibe[f]
        pole = 'high' if v >= 70 else ('low' if v <= 30 else 'mid')
        lines.append(SPLIT[(f, pole)]); used.add(f)
    scored = []
    for f in C.IDENT:
        if f in used:
            continue
        gap = rv[f] - user.vibe[f]
        rel = 'above' if gap >= GAP else ('below' if gap <= -GAP else 'level')
        # rank by how much this axis matters x how far apart you are, same idea as the room line
        scored.append((C.WEIGHT[f] * abs(gap), f, rel))
    scored.sort(reverse=True)
    # If even the widest gap is inside GAP, you and this room want the same night. Saying that
    # three times in three near-identical sentences is weaker than saying it once.
    if scored and scored[0][2] == 'level':
        if not lines:                              # a split line already says the useful thing
            f = max((x[1] for x in scored), key=lambda f: C.WEIGHT[f])
            lines.append(AXIS[f]['level'])
        return headline, lines, m, dist
    for _, f, rel in scored[:top - len(lines)]:
        if rel == 'level' and any(l for l in lines):
            continue                               # never pad a real difference with an agreement
        lines.append(AXIS[f][rel])
    return headline, lines, m, dist


# ================================================================= examples
if __name__ == '__main__':
    def line(c='-', n=100): print(c * n)
    def head(t):
        print(); print('=' * 100); print(t); print('=' * 100)
    mk = lambda **kw: C.mk('p', **kw)
    import roomline as RL

    ROOM_A = [mk(ENRG=86, MOVE=84, TALK=18, AFFIL=38, FOCUS=32, SPONT=58),
              mk(ENRG=82, MOVE=80, TALK=22, AFFIL=42, FOCUS=35, SPONT=62),
              mk(ENRG=90, MOVE=88, TALK=15, AFFIL=35, FOCUS=28, SPONT=55)]
    ROOM_B = [mk(TALK=88, ENRG=26, AFFIL=76, MOVE=18, FOCUS=30, SPONT=34),
              mk(TALK=84, ENRG=30, AFFIL=72, MOVE=22, FOCUS=34, SPONT=38),
              mk(TALK=90, ENRG=24, AFFIL=80, MOVE=16, FOCUS=28, SPONT=30)]
    ROOM_C = [mk(AFFIL=88, ENRG=62, TALK=66, FOCUS=44, MOVE=40, SPONT=52),
              mk(AFFIL=16, ENRG=66, TALK=54, FOCUS=48, MOVE=56, SPONT=50),
              mk(AFFIL=20, ENRG=64, TALK=58, FOCUS=50, MOVE=58, SPONT=48)]
    YOU = {
     'a loud mover': mk(ENRG=88, MOVE=86, TALK=20, AFFIL=40, FOCUS=30, SPONT=60),
     'a quiet talker': mk(ENRG=28, MOVE=20, TALK=86, AFFIL=74, FOCUS=32, SPONT=36),
     'somebody in the middle': mk(ENRG=55, MOVE=50, TALK=52, AFFIL=48, FOCUS=50, SPONT=52),
    }

    for label, members in (('a loud floor', ROOM_A), ('a quiet table', ROOM_B),
                           ('a room that splits on AFFIL', ROOM_C)):
        with contextlib.redirect_stdout(io.StringIO()):
            rv, splits, _ = C.room(members)
        head('THE ROOM: %s' % label)
        print('  %s' % RL.room_line(rv, splits))
        for who, u in YOU.items():
            hl, lines, m, d = read(u, members)
            print()
            print('  you are %s   -   match %d, disturbance %.3f' % (who, round(m * 100), d))
            print('     %s' % hl)
            for l in lines:
                print('       . %s' % l)
    print()
    line()
    print("""
  **The headline uses both numbers because they answer different questions.** A room of neutrals is
  moved by anybody, however well matched; a room already firm on both poles cannot be moved at all,
  however badly matched. *You would slot straight in* and *you would change this room* are both
  true things and neither is derivable from the other.

  **A split outranks everything.** When the room contains both poles there is no single answer to
  how you fit - there is a half of it that is yours, and that is the only honest sentence.
""")
