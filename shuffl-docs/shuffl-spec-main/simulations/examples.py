# -*- coding: utf-8 -*-
import design2 as D2, design as Dz, splitsim as S
from splitsim import M, STOP_AXES
FRIEND_MAX_GIVE = 70
FRIENDS = set()
def opposed_by(m, f, members):
    out = []
    for o in members:
        if o is m or not D2.is_firm(o, f) or o.pole(f) == m.pole(f): continue
        if frozenset({m.name, o.name}) in FRIENDS and abs(o.vibe[f] - m.vibe[f]) - D2.bend_pts(o, f) <= FRIEND_MAX_GIVE:
            continue                                           # a friend stretches: the opposition is absorbed
        out.append(o.name)
    return out
Dz.opposed_by = opposed_by
def lat(m, **kw): m.lat = kw; return m
def run(title, members, friends=(), hours=6):
    global FRIENDS; FRIENDS = {frozenset(p) for p in friends}
    D2.show(title, members, hours)

run('1. IN SYNC - Kabir, Meher, Zoya: all three love their own table and a night you can talk',
    [M('Kabir', AFFIL=90, TALK=82, ENRG=40, FOOD=88), M('Meher', TALK=88, AFFIL=80, CROWD=35, SCEN=88), M('Zoya', AFFIL=85, TALK=78, ROAM=25, HERIT=70)])
run('2. BEST OF BOTH - Dev wants it loud (ENRG 90), Ira wants it calm (ENRG 15); neither has a strong #2',
    [M('Dev', ENRG=90, CROWD=60, ROAM=60), M('Ira', ENRG=15, TALK=60, FOOD=92)])
run('3. GOT YOUR BACK - the same pair, but Dev has a strong #2 (CROWD 82)',
    [M('Dev', ENRG=90, CROWD=82, ROAM=60), M('Ira', ENRG=15, TALK=60, FOOD=92)])
run('4. SOMETHING FOR EVERYONE - Tanvi wants games, Yash wants a floor, Om wants to talk; all three want ONE place',
    [M('Tanvi', GAMES=90, ROAM=15), M('Yash', MOVE=90, ROAM=20), M('Om', TALK=90, ROAM=12)])
run('5. ALONG FOR THE RIDE - Rhea is set on a packed room; Nikhil and Sana are easy tonight',
    [M('Rhea', CROWD=88, ENRG=72), M('Nikhil', FOOD=62), M('Sana', SCEN=88, POL=80)])
run('6. OPEN NIGHT - nobody swiped past the middle',
    [M('Arnav', ENRG=55, GAMES=58), M('Diya', TALK=60, FOOD=62)])
run('7. COULD GO LATE - three friends there for the games and each other, all 55+ on energy, none of them made energy the point',
    [M('Ali', GAMES=88, AFFIL=82, ENRG=62), M('Bani', AFFIL=90, GAMES=75, ENRG=70), M('Cyrus', GAMES=85, AFFIL=78, ENRG=58)])
run('8. ROAM SPLIT - Farah wants three places (ROAM 92), Gaurav wants one (ROAM 12); both firm',
    [M('Farah', ROAM=92, CROWD=80), M('Gaurav', ROAM=12, AFFIL=90, GAMES=72)])
run('9. THE BAND - Hina at ENRG 25: swiped at normal speed she is flexible...',
    [M('Jai', ENRG=88, CROWD=75), M('Hina', ENRG=25, TALK=80, SCEN=88)])
run('9b. ...swiped FAST she is firm, and Jai\'s crowd stands in',
    [M('Jai', ENRG=88, CROWD=75), lat(M('Hina', ENRG=25, TALK=80, SCEN=88), ENRG=0.8)])
run('10. FRIENDS - Karan ENRG 85 v Leela ENRG 20, both firm - but they are friends by data, and the gap is inside the stretch',
    [M('Karan', ENRG=85, CROWD=80), M('Leela', ENRG=20, TALK=85, FOOD=88)], friends=[('Karan', 'Leela')])
run('10b. the same two, NOT friends',
    [M('Karan', ENRG=85, CROWD=80), M('Leela', ENRG=20, TALK=85, FOOD=88)])
run('11. SOLO - Priya plans alone: her own vibe is the shape',
    [M('Priya', AFFIL=70, TALK=78, ENRG=30, ROAM=25, FOOD=88, SCEN=72, POL=65, sense='classy')])
