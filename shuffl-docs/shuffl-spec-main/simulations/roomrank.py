# -*- coding: utf-8 -*-
"""RANKING ROOMS: against the room's SHAPE, or against the room's actual PLAN?

The user, 2026-10-08: "it should be chemistry with the people and how close the room's shape is to
the one you drew - or rather how well the skeleton that the user drew matches the plan generated for
the room."

Those are two different things and the second is the sharper one. A room's merged skeleton is what
its members WANTED. Its plan is what they actually GOT, after the venues that exist at those hours
had their say. This measures whether that difference changes the ranking.

Also: what the MVP loses by dropping the join gates, since there will not be enough rooms to filter.
"""
import sys, random, math, statistics as st
sys.stdout.reconfigure(encoding='utf-8')

TOL_HOURS = 1.5                  # a stop matches a stop within this much clock time
MISS_PENALTY = 40.0              # a stop of yours with no counterpart in their night
FLOOR_LIVABLE = 22.0             # a stop you could live with


def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)


def shape_d(ae, ac, be, bc):
    return abs(ae - be) + 0.6 * abs(ac - bc)


def draw(rng, k=None):
    k = k or rng.choice([2, 3, 3, 4])
    start = rng.choice([19, 20, 21])
    e = rng.uniform(25, 55)
    out = []
    for s in range(k):
        e = min(97, e + rng.uniform(4, 22))
        out.append(dict(h=start + 2 * s, e=e, c=max(10, min(97, e + rng.gauss(0, 10)))))
    return out


def venues_for(rng, stop):
    """What the city can actually offer at that hour, near that shape. Supply is imperfect."""
    best = None
    for _ in range(rng.choice([3, 5, 8])):
        ve = max(5, min(98, stop['e'] + rng.gauss(0, 16)))
        vc = max(5, min(98, stop['c'] + rng.gauss(0, 16)))
        d = shape_d(ve, vc, stop['e'], stop['c'])
        if best is None or d < best[0]:
            best = (d, dict(h=stop['h'], e=ve, c=vc))
    return best[1]


def make_room(rng):
    """A room: a merged skeleton, and the plan its members actually ended up with."""
    skel = draw(rng)
    plan = [venues_for(rng, s) for s in skel]
    return dict(skel=skel, plan=plan)


def match_against(mine, theirs):
    """Clock alignment, not index: a stop is a time (SKELETON_MERGE_V1 section 1)."""
    tot, n = 0.0, 0
    for s in mine:
        near = [t for t in theirs if abs(t['h'] - s['h']) <= TOL_HOURS]
        if not near:
            tot += MISS_PENALTY
        else:
            t = min(near, key=lambda t: abs(t['h'] - s['h']))
            tot += shape_d(t['e'], t['c'], s['e'], s['c'])
        n += 1
    return tot / n


def worst_stop(mine, theirs):
    out = []
    for s in mine:
        near = [t for t in theirs if abs(t['h'] - s['h']) <= TOL_HOURS]
        out.append(MISS_PENALTY if not near
                   else min(shape_d(t['e'], t['c'], s['e'], s['c']) for t in near))
    return max(out) if out else MISS_PENALTY


head('A.  DOES RANKING ON THE PLAN DIFFER FROM RANKING ON THE SHAPE?')
rng = random.Random(9)
flips, pairs, gaps = 0, 0, []
top_same = 0
TRIALS = 4000
for _ in range(TRIALS):
    me = draw(rng)
    rooms = [make_room(rng) for _ in range(rng.choice([4, 6, 8]))]
    by_shape = sorted(range(len(rooms)), key=lambda i: match_against(me, rooms[i]['skel']))
    by_plan = sorted(range(len(rooms)), key=lambda i: match_against(me, rooms[i]['plan']))
    if by_shape[0] == by_plan[0]:
        top_same += 1
    for a in range(len(rooms)):
        for b in range(a + 1, len(rooms)):
            pairs += 1
            sa, sb = match_against(me, rooms[a]['skel']), match_against(me, rooms[b]['skel'])
            pa, pb = match_against(me, rooms[a]['plan']), match_against(me, rooms[b]['plan'])
            if (sa < sb) != (pa < pb):
                flips += 1
            gaps.append(abs(pa - sa))
print('   %d users, each shown 4-8 rooms' % TRIALS)
line()
print('   %-46s %s' % ('the two methods pick the same top room', '%.0f%%' % (100.0 * top_same / TRIALS)))
print('   %-46s %s' % ('pairs of rooms they order differently', '%.0f%%' % (100.0 * flips / pairs)))
print('   %-46s %.1f points' % ('mean gap between the two scores', st.mean(gaps)))
line()
print("""
  **They are not the same ranking.** A room's merged skeleton is what its members WANTED; its plan is
  what they GOT once the venues that exist at those hours had their say. **Matching the plan asks
  whether you would enjoy this actual night; matching the shape asks whether you draw like they do.**

  The second question is only a proxy for the first, and it is a proxy that fails exactly where the
  supply is thin - which in Delhi is late, and on the nights people most want to go out.
""")

head('B.  WHAT THE JOIN GATES WOULD HAVE REMOVED')
rng = random.Random(4)
kept, cut_sim, cut_floor, empty = 0, 0, 0, 0
shown = []
for _ in range(3000):
    me = draw(rng)
    rooms = [make_room(rng) for _ in range(rng.choice([2, 3, 4, 5, 6]))]
    pass_ = []
    for r in rooms:
        d = match_against(me, r['plan'])
        sim = max(0.0, 1.0 - d / 60.0)                 # a stand-in for the 70% plan-similarity gate
        floor_ok = worst_stop(me, r['plan']) <= FLOOR_LIVABLE
        if sim < 0.70:
            cut_sim += 1
        elif not floor_ok:
            cut_floor += 1
        else:
            pass_.append(r)
    kept += len(pass_)
    shown.append(len(pass_))
    if not pass_:
        empty += 1
tot = cut_sim + cut_floor + kept
line()
print('   %-46s %5.0f%%' % ('rooms cut by the 70% similarity gate', 100.0 * cut_sim / tot))
print('   %-46s %5.0f%%' % ('rooms cut by the per-member FLOOR check', 100.0 * cut_floor / tot))
print('   %-46s %5.0f%%' % ('rooms that survive both', 100.0 * kept / tot))
print('   %-46s %5.0f%%' % ('USERS WHO SEE AN EMPTY LIST', 100.0 * empty / 3000))
print('   %-46s %5.1f' % ('mean rooms shown, after gating', st.mean(shown)))
line()
print("""
  **At launch volume the gates do not filter a list, they delete it.** With a handful of live rooms
  on a Friday, a user who would have had three to look at is left with one or none.

  **But the gates carry real information and dropping them silently loses it.** The FLOOR check is
  not a quality bar - it is the question *is there a single stop in this night you could live with*,
  and a room that fails it is a genuinely bad night for that person.

  **So: not a gate and not nothing. A label.** Rank every room, show every room, and put the thing
  the gate would have said on the card where the person can read it - which is the same move already
  made on the Go-here card, where the talk floor became a warning instead of a veto.
""")
