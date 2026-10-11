# -*- coding: utf-8 -*-
"""Interactions between vibe factors under the room-first readings model (§14.3 v5)."""
from readings import show
from splitsim import M

print('\n########## ENRG x TALK — contagion against masking')
show('a. the room catches a spark (88, 85, neutrals) but one person is a firm talker',
     [M('Arjun', ENRG=88, CROWD=70), M('Dev', ENRG=85, MOVE=70), M('Ira', TALK=88, ENRG=50), M('Zoya', ENRG=48, SCEN=88)])
show('b. the same room without the talker — the arc is free to end loud',
     [M('Arjun', ENRG=88, CROWD=70), M('Dev', ENRG=85, MOVE=70), M('Ira', ENRG=50, FOOD=88), M('Zoya', ENRG=48, SCEN=88)])

print('\n########## ENRG x AFFIL — a loud night against our own table')
show('a. two at 88 wanting a big night, two at 88 wanting their own people',
     [M('A', ENRG=88, CROWD=75), M('B', ENRG=85, MOVE=72), M('C', AFFIL=88, TALK=70), M('D', AFFIL=85, FOOD=88)])
show('b. the same, but the table people are the majority (three of four)',
     [M('A', ENRG=88, CROWD=75), M('B', AFFIL=88, TALK=70), M('C', AFFIL=85, FOOD=88), M('D', AFFIL=82)])

print('\n########## ENRG x MOVE — energy that wants a floor, against sitters')
show('a. movers and highs together — the night ends on a floor',
     [M('A', ENRG=88, MOVE=85), M('B', ENRG=82, MOVE=80), M('C', TALK=70, FOOD=88)])
show('b. the same energy, but the sitters outnumber the movers',
     [M('A', ENRG=88, MOVE=85), M('B', MOVE=12, TALK=80), M('C', MOVE=15, AFFIL=85)])

print('\n########## CROWD x TALK — crowding blocks conversation')
show('a. a crowd-lover and a firm talker — crowd counts in full against the talk goal',
     [M('A', CROWD=90, ENRG=60), M('B', TALK=88, AFFIL=70), M('C', FOOD=88)])
show('b. a crowd-hater in an energy room — his aversion counts at half',
     [M('A', ENRG=88, MOVE=80), M('B', ENRG=85, CROWD=75), M('C', CROWD=12, TALK=62)])

print('\n########## CROWD x AFFIL — packed, but ours')
show('a. a crowd-lover among table people — the street carries the crowd',
     [M('A', CROWD=90, ENRG=65), M('B', AFFIL=88, TALK=72), M('C', AFFIL=85, FOOD=88)])
show('b. a crowd-hater among room people — the split cuts the other way',
     [M('A', CROWD=12, TALK=80), M('B', AFFIL=12, ENRG=78), M('C', AFFIL=15, CROWD=72)])

print('\n########## GAMES x AFFIL — the task as glue')
show('a. a gamer and two table people — games available, not the point',
     [M('A', GAMES=90, ENRG=60), M('B', AFFIL=88, TALK=75), M('C', AFFIL=85, FOOD=88)])
show('b. a gamer in a room split on affiliation — the bridge and the split agree',
     [M('A', GAMES=88, ENRG=62), M('B', AFFIL=90, TALK=70), M('C', AFFIL=12, CROWD=75)])

print('\n########## GAMES x ENRG — something to do, or something to climb')
show('a. gamers against a high-energy majority',
     [M('A', GAMES=90, AFFIL=70), M('B', ENRG=88, CROWD=78), M('C', ENRG=85, MOVE=75)])
show('b. gamers in the majority against one high',
     [M('A', GAMES=90, AFFIL=70), M('B', GAMES=85, TALK=60), M('C', ENRG=88, CROWD=78)])

print('\n########## ROAM x ENRG — one place against a climbing night')
show('a. a settler and two highs — one place, and it has to carry the arc',
     [M('A', ROAM=12, AFFIL=88), M('B', ENRG=88, CROWD=75), M('C', ENRG=85, MOVE=70)])
show('b. roamers and one calm person — three stops, the last one loud',
     [M('A', ROAM=92, CROWD=75), M('B', ROAM=85, ENRG=80), M('C', ENRG=15, TALK=80)])

print('\n########## ROAM x TALK — moving against talking')
show('a. a roamer and a firm talker — the floor holds at every stop',
     [M('A', ROAM=92, CROWD=75), M('B', TALK=88, AFFIL=72), M('C', FOOD=88)])

print('\n########## MOVE x TALK — a floor against a conversation')
show('a. a mover and a firm talker — the floor at 40 caps the dance floor',
     [M('A', MOVE=88, ENRG=80), M('B', TALK=88, AFFIL=70), M('C', CROWD=70)])

print('\n########## three-way — ENRG x CROWD x TALK')
show('a. a big loud room, a packed room, a conversation',
     [M('A', ENRG=88, MOVE=72), M('B', CROWD=90, ENRG=70), M('C', TALK=88, AFFIL=70)])

print('\n########## strangers — every reading at once')
show('a. a public room: a mover, a gamer, a crowd person, a talker',
     [M('A', MOVE=85, ENRG=70), M('B', GAMES=82, AFFIL=60), M('C', CROWD=78, ENRG=68), M('D', TALK=85, FOOD=88)], strangers=True)
