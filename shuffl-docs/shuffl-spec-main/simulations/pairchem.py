# -*- coding: utf-8 -*-
"""PAIRWISE VIBE CHEMISTRY - what two people would be like together, not how alike they are.

The user, 2026-10-03: "include a list of the ways vibes interact with one another in terms of
chemistry so we can give users insights other than just a vibe match score, by showing how the vibe
of the user they're viewing and their own vibe would get along and in what way."

Runs CHEMISTRY_V4's axis rules at n=2 and says what happens, in words.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

IDENT = ['ENRG', 'AFFIL', 'TALK', 'FOCUS', 'MOVE', 'SPONT']
WEIGHT = dict(ENRG=18, AFFIL=16, TALK=14, FOCUS=14, MOVE=12, SPONT=10)
SPLITS = {'AFFIL', 'MOVE'}            # both poles can be enacted at once in the same room

def pole(v):
    if v >= 70: return 'hi'
    if v <= 30: return 'lo'
    return 'mid'

# per axis, per (my pole, their pole) -> (interaction name, the line the card shows)
# the line is written to the VIEWER, about the person they are looking at.
READS = {
 'ENRG': {
   ('hi','hi'): ('both on',     'Neither of you is going home early.'),
   ('hi','mid'):('you lead',    'You set the pace and they will come along.'),
   ('mid','hi'):('they lead',   'They will take the night later than you planned it.'),
   ('hi','lo'): ('you pull',    'You want it louder than they do, and loud usually wins.'),
   ('lo','hi'): ('they pull',   'They will still be going when you are done.'),
   ('mid','mid'):('easy',       'Neither of you is pushing. The night goes where it goes.'),
   ('lo','lo'): ('both calm',   'A calm night, and you both actually want it.'),
   ('lo','mid'):('you anchor',  'You will be the reason it stays gentle.'),
   ('mid','lo'):('they anchor', 'They will keep it gentler than you might have.'),
 },
 'TALK': {
   ('hi','hi'): ('talkers',     'You will talk over anything. Pick somewhere you can.'),
   ('hi','lo'): ('mismatch',    'You came out to talk. They came out for the noise.'),
   ('lo','hi'): ('mismatch',    'They came out to talk and you came out for the noise.'),
   ('hi','mid'):('you lead',    'You will start the conversation and they will join it.'),
   ('mid','hi'):('they lead',   'They will pull you into talking more than you planned.'),
   ('lo','lo'): ('both loud',   'Neither of you needs to hear anyone. Good.'),
   ('mid','mid'):('easy',       'Talk if it happens, fine if it does not.'),
   ('lo','mid'):('you set it',  'You will not mind if it gets loud.'),
   ('mid','lo'):('they set it', 'They will not mind if it gets loud.'),
 },
 'MOVE': {
   ('hi','hi'): ('both up',     'You will both be on the floor and neither will be waiting.'),
   ('hi','lo'): ('split',       'One of you dances, one of you holds the table. That works.'),
   ('lo','hi'): ('split',       'They will dance and you will not, and that is fine.'),
   ('hi','mid'):('you start',   'You will get up first and they will follow.'),
   ('mid','hi'):('they start',  'They will get you up.'),
   ('lo','lo'): ('seated',      'Neither of you is getting up. Find a good table.'),
   ('mid','mid'):('open',       'Could go either way.'),
   ('lo','mid'):('you sit',     'You will stay sat and they will not mind.'),
   ('mid','lo'):('they sit',    'They will stay sat.'),
 },
 'FOCUS': {
   ('hi','hi'): ('both front',  'You will both be at the front for whatever is on.'),
   ('hi','mid'):('you bring it','You will find the thing worth watching.'),
   ('mid','hi'):('they bring it','They came for something, and you will end up watching it too.'),
   ('hi','lo'): ('you bring it','You want a main event. They want the people to be it.'),
   ('lo','hi'): ('they bring it','They want a main event. You would rather it was just you two.'),
   ('lo','lo'): ('you are it',  'No stage, no act. You two are the night.'),
   ('mid','mid'):('easy',       'Either works.'),
   ('lo','mid'):('no stage',    'You would rather nothing was on.'),
   ('mid','lo'):('no stage',    'They would rather nothing was on.'),
 },
 'SPONT': {
   ('lo','lo'): ('both booked', 'Booked by Tuesday, both of you.'),
   ('lo','hi'): ('you plan',    'You will have booked before they have decided. That usually helps.'),
   ('hi','lo'): ('they plan',   'They will have booked before you have decided. Let them.'),
   ('hi','hi'): ('nothing set', 'Nothing will get planned. See what happens.'),
   ('lo','mid'):('you plan',    'You will be the one who books.'),
   ('mid','lo'):('they plan',   'They will be the one who books.'),
   ('hi','mid'):('loose',       'You will leave it late.'),
   ('mid','hi'):('loose',       'They will leave it late.'),
   ('mid','mid'):('easy',       'It will get sorted at some point.'),
 },
 'AFFIL': {
   ('hi','hi'): ('your table',  'You will find a table and stay at it, together.'),
   ('lo','lo'): ('the room',    'Neither of you is sitting still. You will work the room.'),
   ('hi','lo'): ('split',       'You want your people. They want the room. Two different nights in one.'),
   ('lo','hi'): ('split',       'They want their people. You want the room.'),
   ('hi','mid'):('you hold',    'You will keep the group together.'),
   ('mid','hi'):('they hold',   'They will keep the group together.'),
   ('lo','mid'):('you roam',    'You will be the one talking to strangers.'),
   ('mid','lo'):('they roam',   'They will be the one talking to strangers.'),
   ('mid','mid'):('easy',       'Neither of you minds much.'),
 },
}

def match(a, b):
    tot = sum(WEIGHT.values())
    return 1 - sum(WEIGHT[f] * abs(a[f] - b[f]) for f in IDENT) / tot / 100.0

def read_pair(me, them):
    """return (headline, [(factor, interaction, line)]) ordered by how much it matters"""
    rows = []
    for f in IDENT:
        k = (pole(me[f]), pole(them[f]))
        name, line = READS[f][k]
        # how interesting is this? distance from the middle on both sides, weighted
        salience = (abs(me[f] - 50) + abs(them[f] - 50)) * WEIGHT[f] / 100.0
        rows.append((salience, f, name, line))
    rows.sort(reverse=True)
    # headline from the shape of the whole thing
    splits = [f for _, f, n, _ in rows if n == 'split']
    mine   = [f for _, f, n, _ in rows[:4] if n.startswith('you')]
    theirs = [f for _, f, n, _ in rows[:4] if n.startswith('they')]
    both   = [f for _, f, n, _ in rows[:4] if n.startswith('both') or
              n in ('talkers', 'your table', 'the room', 'you are it', 'seated')]
    flat   = [f for _, f, n, _ in rows if n in ('easy', 'open')]
    m = match(me, them)
    if len(both) >= 3:                        head = 'SAME WAVELENGTH'
    elif len(splits) >= 2:                    head = 'TWO DIFFERENT NIGHTS'
    elif len(splits) == 1 and len(both) >= 2: head = 'ALIGNED, WITH ONE SPLIT'
    elif len(mine) >= 3 and not theirs:       head = 'YOU WILL CARRY THIS ONE'
    elif len(theirs) >= 3 and not mine:       head = 'THEY WILL CARRY THIS ONE'
    elif mine and theirs:                     head = 'YOU WILL TRADE OFF'
    elif len(flat) >= 4:                      head = 'NOBODY IS PUSHING'
    else:                                     head = 'PUSH AND PULL'
    return head, m, rows

def line(c='-', n=94): print(c * n)
def head(t):
    print(); print('=' * 94); print(t); print('=' * 94)

PEOPLE = {
 'Ishaan': dict(ENRG=88, AFFIL=38, TALK=75, FOCUS=88, MOVE=50, SPONT=12),
 'Nitya':  dict(ENRG=52, AFFIL=78, TALK=86, FOCUS=30, MOVE=35, SPONT=22),
 'Aarav':  dict(ENRG=84, AFFIL=38, TALK=45, FOCUS=72, MOVE=80, SPONT=88),
 'Zoya':   dict(ENRG=66, AFFIL=25, TALK=58, FOCUS=88, MOVE=85, SPONT=50),
 'Dev':    dict(ENRG=45, AFFIL=55, TALK=50, FOCUS=48, MOVE=42, SPONT=52),
}

head('WHAT THE PROFILE SHOWS WHEN ISHAAN LOOKS AT SOMEBODY')
for other in ['Nitya', 'Aarav', 'Zoya', 'Dev']:
    h, m, rows = read_pair(PEOPLE['Ishaan'], PEOPLE[other])
    print()
    print('  viewing %-7s   match %.0f%%   >>> %s' % (other, m * 100, h))
    line()
    for sal, f, name, txt in rows[:4]:
        print('     %-6s %-13s %s' % (f, name, txt))

head('AND THE POINT OF IT - a match percentage cannot say any of this')
print("""
  Ishaan and Zoya match 80%. Ishaan and Dev match 71%. The numbers are close and the nights are
  nothing alike.

  WITH ZOYA, the read has content on both sides: both at the front for whatever is on, she is the
  one talking to strangers, he sets the pace. Things happen that neither would have done alone.

  WITH DEV, every line in the top four starts with YOU. You lead, you bring it, you plan, you
  start the conversation. Dev sits in the middle on all six factors, so there is nothing for the
  rules to catch. **That is not a bad match - it is a night one person has to carry**, and the
  percentage cannot tell you that.

  SO THE TWO ANSWER DIFFERENT QUESTIONS, and the profile should show both:
     the match percentage  ->  HOW ALIKE ARE WE
     the chemistry read    ->  WHO DOES WHAT, AND WHAT ACTUALLY HAPPENS

  And the second one is the reason to open somebody's profile at all.
""")
for other in ['Zoya', 'Dev']:
    h, m, rows = read_pair(PEOPLE['Ishaan'], PEOPLE[other])
    sides = [n.split()[0] for _, _, n, _ in rows[:4]]
    print('  Ishaan + %-5s  match %.0f%%  -> %-24s  top four led by: %s'
          % (other, m * 100, h, ', '.join(sides)))
