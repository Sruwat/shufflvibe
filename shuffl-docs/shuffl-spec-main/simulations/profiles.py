# -*- coding: utf-8 -*-
"""PROFILES V1 - going-out personality as RULES, not as a type library.

A rule reads the SHAPE of one member's profile (two or three axes at once) and infers a want on an
axis they said nothing about. Person-centred analysis: a configuration carries information the
axes carry individually (Bergman & Magnusson), and the two approaches are complementary, not
rival - so this sits ON TOP of the axis readings, never instead of them.

Three guards:
  1. an inference only ever speaks where the axis is SILENT (no position, nobody firm) - it can
     never contradict or override something a person actually swiped;
  2. it is discounted: 0.6 x the axis weight, x the share of the room whose profile fires it;
  3. every firing is returned so it can be logged and validated rather than believed.
"""
HIGH, LOW = 70, 30
def hi(m, f): return m.vibe[f] >= HIGH
def lo(m, f): return m.vibe[f] <= LOW

# (name, matches(member), [(axis, pole)], the line the card can say)
RULES = [
 ('The Long Table',   lambda m: lo(m, 'ENRG') and hi(m, 'TALK'),
  [('ROAM', 'low'), ('CROWD', 'low')],       'a calm night that is all conversation wants one table, not three rooms'),
 ('Loud and Social',  lambda m: hi(m, 'ENRG') and hi(m, 'TALK'),
  [('CROWD', 'high'), ('GAMES', 'low')],     'loud and talking is a packed bar, not a games night'),
 ('Lose Yourself',    lambda m: hi(m, 'ENRG') and lo(m, 'TALK') and hi(m, 'MOVE'),
  [('CROWD', 'high'), ('RAMP', 'high')],     'energy with no talk and a floor peaks at the end, in a full room'),
 ('Settled In',       lambda m: hi(m, 'AFFIL') and hi(m, 'GAMES'),
  [('ROAM', 'low')],                          'our own people with something to play settle in'),
 ('Working the Room', lambda m: lo(m, 'AFFIL') and hi(m, 'CROWD'),
  [('ROAM', 'high')],                         'meeting people in full rooms takes more than one room'),
 ('Quiet Company',    lambda m: lo(m, 'ENRG') and lo(m, 'CROWD') and lo(m, 'AFFIL'),
  [('TALK', 'high')],                         'you cannot meet anyone somewhere you cannot hear them'),
]

INFERRED_W = 0.6                 # a stated want always outweighs an inferred one
LINE_TARGET = {'low': 25.0, 'high': 75.0}    # what an inference sets a silent night-level axis to

def fires(members):
    """[(rule name, [member names], [(axis, pole)], why)] - every rule that matches somebody."""
    out = []
    for name, match, infers, why in RULES:
        who = [m.name for m in members if match(m)]
        if who: out.append((name, who, infers, why))
    return out

def silent(members, axis, stated_axes):
    """An axis is silent when nobody has a position on it and it issued no reading of its own."""
    if axis in stated_axes: return False
    return all(31 <= m.vibe[axis] <= 69 for m in members)
