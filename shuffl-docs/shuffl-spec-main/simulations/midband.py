# -*- coding: utf-8 -*-
"""IS A 50 A READING OR AN ABSENCE?

The user, 2026-10-07: "no factor is uncertain, it just says how much you want that. A drawn ENRG of
50 means they want a venue with energy but not a lot. A vibe 50 means it is not something they
completely identify with but identify to a certain degree."

SKELETON_MERGE_V1 section 4a already grants half of this - a drawn mid band scores 0.25 and the
skeleton is declared to have no true neutrals. This asks whether the PEOPLE side lives up to the
same principle, and measures what changes if it does.
"""
import sys, io, contextlib, math
sys.stdout.reconfigure(encoding='utf-8')
with contextlib.redirect_stdout(io.StringIO()):
    import chem4 as C


def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)


mk = lambda **kw: C.mk('p', **kw)

head('A.  WHERE THE MODEL ALREADY TREATS A MID VALUE AS REAL')
print("""
  1  THE BASE.  axis_level starts at the plain mean of every member's value, so somebody at 62 is
     in the room's number from the start. They are not ignored.

  2  MATCH.  match() compares raw values - |you 62 - room 71| - so a mid person is matched on
     exactly where they sit. No thresholding at all.

  3  THE DRAWN SKELETON.  Section 4a gives a drawn mid band 0.25 rather than 0.00, on precisely the
     user's argument. The spec already says the skeleton has no true neutrals.
""")

head('B.  WHERE IT DOES NOT - strength() cannot tell 62 from 38')
print("""
  strength(m, f, pole) returns 0.0 unless the value is >= 70 or <= 30. Everything between is a
  "neutral" worth NEUTRAL_W = 0.25 in the denominator - **and it is the same 0.25 whichever side of
  fifty they are on.**
""")
for v in (38, 50, 62):
    print('   value %d  ->  strength high %.2f   strength low %.2f   counted as a neutral'
          % (v, C.strength(mk(ENRG=v), 'ENRG', 'high'), C.strength(mk(ENRG=v), 'ENRG', 'low')))
line()

ROOMS = [
 ('four at 62 and one at 85', [mk(ENRG=62)] * 4 + [mk(ENRG=85)]),
 ('four at 38 and one at 85', [mk(ENRG=38)] * 4 + [mk(ENRG=85)]),
 ('five at 62 - nobody over 70', [mk(ENRG=62)] * 5),
 ('five at 50 exactly',          [mk(ENRG=50)] * 5),
 ('two at 62, two at 38',        [mk(ENRG=62)] * 2 + [mk(ENRG=38)] * 2),
]
print('   %-32s %8s   %s' % ('the room', 'ENRG', 'why'))
line()
for label, members in ROOMS:
    with contextlib.redirect_stdout(io.StringIO()):
        rv, _, _ = C.room(members)
    lvl, why = C.axis_level(members, 'ENRG')
    print('   %-32s %8.0f   %s' % (label, lvl, why))
line()
print("""
  **Rows one and two are the finding.** Four people at 62 and four people at 38 are not the same
  room, and the model gives the single person at 85 the same share in both, because all eight mid
  people are "neutrals". **The four at 62 are leaning the same way as the leader and get no credit
  for it; the four at 38 are leaning against and get no penalty.**
""")

head('C.  A WEAK-ADVOCATE ALTERNATIVE')
print("""
  Keep the ladder, but let the mid band advocate for its own side at a low weight instead of
  counting as a side-less neutral:

     |v - 50| >= 20   (<=30 or >=70)   full ladder, unchanged
     |v - 50| in 1..19                 strength MID_W on the side it leans toward
     v == 50 exactly                   a true neutral - the only one there is
""")
MID_W = 0.30


def strength2(m, f, pole):
    s = m.vibe[f]
    base = C.strength(m, f, pole)
    if base:
        return base
    if s == 50:
        return 0.0
    leans = 'high' if s > 50 else 'low'
    return MID_W if leans == pole else 0.0


def axis_level2(members, f):
    cfg = C.AXIS[f]
    base = sum(m.vibe[f] for m in members) / len(members)
    if cfg['pull'] == 0.0:
        return base
    hi = sum(strength2(m, f, 'high') for m in members)
    lo = sum(strength2(m, f, 'low') for m in members)
    if hi == 0 and lo == 0:
        return base
    dom = cfg['dom']
    I_hi = (hi ** C.IMPACT_EXP) * (cfg['discount'] if dom == 'low' else 1.0) if hi else 0.0
    I_lo = (lo ** C.IMPACT_EXP) * (cfg['discount'] if dom == 'high' else 1.0) if lo else 0.0
    neutrals = [m for m in members if m.vibe[f] == 50]
    I_n = (len(neutrals) ** C.IMPACT_EXP) * C.NEUTRAL_W if neutrals else 0.0
    lead = 'high' if I_hi >= I_lo else 'low'
    I_lead, I_rest = (I_hi, I_lo + I_n) if lead == 'high' else (I_lo, I_hi + I_n)
    share = I_lead / (I_lead + I_rest) if (I_lead + I_rest) else 0.0
    side = [m for m in members if strength2(m, f, lead) > 0]
    peak = max(m.vibe[f] for m in side) if lead == 'high' else min(m.vibe[f] for m in side)
    return base + cfg['pull'] * share * (peak - base)


print('   %-32s %9s %9s %8s' % ('the room', 'now', 'proposed', 'moves'))
line()
for label, members in ROOMS:
    a, _ = C.axis_level(members, 'ENRG')
    b = axis_level2(members, 'ENRG')
    print('   %-32s %9.0f %9.0f %+8.0f' % (label, a, b, b - a))
line()
print("""
  **The two rows that should differ now differ.** Four at 62 behind a leader at 85 push the room
  higher than four at 38 do, which is what anybody looking at those two groups would say.

  **And a room of five at 62 still reads 62** - the mid band advocating does not inflate a room
  that has no leader, because the pull moves the base toward the PEAK of the leading side, and when
  the peak is 62 there is nowhere to go.

  **The only true neutral left is an exact 50 on a swiped factor**, which is the one value that
  genuinely does mean the card did nothing - it can only arise from two cards disagreeing
  (`up for it` then `not for me`), and that is ambiguity rather than a want.
""")
