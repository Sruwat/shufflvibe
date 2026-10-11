# -*- coding: utf-8 -*-
"""CHEMISTRY_V2 on top of the designed night (design2): the psychology of each axis feeds the room's
chemistry vector, the tags, and which types win. Tops still stand at every stop."""
import design2 as D2, design as Dz, splitsim as S
from splitsim import M, TYPES, STOP_AXES, PREFS, VENUES, fill

SPARK_PULL, SPARK_PULL_LOW, DRIFT_UP, TALK_FLOOR, CROWD_HALF, SETTLE_SHARE = 0.6, 0.3, 10, 40, 0.5, 0.55
MINORITY_PULL = {0: 0.6, 1: 0.6, 2: 0.5}       # how far a lone high lifts a room where the lows match or outnumber it; 3+ -> 0.4
def strength(m, f, pole):
    """How much a person counts on a pole for contagion: an extreme 1.0; the band 0.5 (0.75 if swiped fast); else 0."""
    s_ = m.vibe[f]
    on = (s_ >= 70) if pole == 'high' else (s_ <= 30)
    if not on: return 0.0
    if s_ >= 80 or s_ <= 20: return 1.0
    return 0.75 if D2.fast(m, f) else 0.5
ONE_WAY = {'ENRG': 'high', 'TALK': 'high', 'MOVE': 'high'}     # on these axes only the named pole can oppose the other
is_firm, bend_pts, zone = D2.is_firm, D2.bend_pts, D2.zone
TYPES['games pub'] = dict(ENRG=55, AFFIL=70, CROWD=60, TALK=60, MOVE=20, GAMES=65)   # board-game cafes sit at the middle on energy

def base_vector(members):
    v = {}
    for f in STOP_AXES:
        w = {m.name: max(m.firm(f), 0.0) for m in members}
        if f in ONE_WAY:
            hi = sum(strength(m, f, 'high') for m in members); lo = sum(strength(m, f, 'low') for m in members)
            if hi > lo:                                                              # the dominant pole outnumbers: the other does not pull
                for m in members:
                    if m.pole(f) != ONE_WAY[f] and strength(m, f, 'low') > 0: w[m.name] = 0.0
        v[f] = 50.0 if sum(w.values()) < 0.05 else sum(w[n] * m.vibe[f] for n, m in zip(w, members)) / sum(w.values())
    return v

def chemistry_vector(members, strangers=False):
    v = base_vector(members); tags = []
    # ---- ENRG: contagion, upward-biased, count-weighted
    hi = sum(strength(m, 'ENRG', 'high') for m in members); lo = sum(strength(m, 'ENRG', 'low') for m in members)
    highs = [m for m in members if strength(m, 'ENRG', 'high') > 0]; lows = [m for m in members if strength(m, 'ENRG', 'low') > 0]
    mids = [m for m in members if 35 <= m.vibe['ENRG'] <= 65]
    if highs and not lows and len(highs) == len(members): tags.append('Running Hot')
    elif lows and not highs and len(lows) == len(members): tags.append('Slow Burn')
    elif highs and not lows and 1 <= len([m for m in highs if m.vibe['ENRG'] >= 80]) <= 2 and len(highs) <= 2 and mids:
        mean_mid = sum(m.vibe['ENRG'] for m in mids) / len(mids); peak = max(m.vibe['ENRG'] for m in highs)
        v['ENRG'] = mean_mid + SPARK_PULL * (peak - mean_mid); tags.append('Caught the Spark')
    elif highs and lows and hi > lo:
        pass                                                   # the highs outnumber: they set it (one-way abstention above); the lows live with it
    elif highs and lows:                                       # the lows match or outnumber: the room comes down to the lively middle
        gap = int(round(lo - hi)); pull = MINORITY_PULL.get(gap, 0.4)
        mean_low = sum(m.vibe['ENRG'] for m in lows) / len(lows); peak = max(m.vibe['ENRG'] for m in highs)
        v['ENRG'] = mean_low + pull * (peak - mean_low); tags.append('Slow Burn')
    elif not any(m.vibe['ENRG'] >= 80 for m in members) and not lows and all(55 <= m.vibe['ENRG'] <= 79 for m in members):
        v['ENRG'] += DRIFT_UP; tags.append('Could Go Late')
    # ---- AFFIL: non-averaging
    ah = [m for m in members if is_firm(m, 'AFFIL') and m.pole('AFFIL') == 'high']; al = [m for m in members if is_firm(m, 'AFFIL') and m.pole('AFFIL') == 'low']
    affil_split = bool(ah and al)
    if affil_split: tags.append('Table and Floor')
    elif ah and len(ah) == len(members): tags.append('Our Table')
    elif (al and len(al) == len(members)) or strangers: tags.append('Meet the Room')
    # ---- TALK: the floor
    talkers = [m for m in members if is_firm(m, 'TALK') and m.pole('TALK') == 'high']
    lively = v['ENRG'] >= 60
    if talkers and lively: tags.append('Buzz, Not Noise')
    # ---- CROWD: weighed by the goal
    crowd_low = [m for m in members if is_firm(m, 'CROWD') and m.pole('CROWD') == 'low']
    if crowd_low and (v['ENRG'] >= 65 or v['MOVE'] >= 60): v['CROWD'] = (v['CROWD'] + 50) / 2      # their aversion at half
    a_hi = sum(strength(m, 'AFFIL', 'high') for m in members); a_lo = sum(strength(m, 'AFFIL', 'low') for m in members)
    g_hi = sum(strength(m, 'GAMES', 'high') for m in members); g_lo = sum(strength(m, 'GAMES', 'low') for m in members)
    mv_hi = sum(strength(m, 'MOVE', 'high') for m in members); mv_lo = sum(strength(m, 'MOVE', 'low') for m in members)
    ctx = dict(affil_split=affil_split, talkers=bool(talkers), strangers=strangers,
               affil_lean='high' if a_hi > a_lo else 'low' if a_lo > a_hi else 'even',
               games_minority=(0 < g_hi < (len(members) / 2)),           # a gamer or two among non-gamers: games available, not the point
               movers_win=(mv_hi > mv_lo and mv_hi > 0))
    return v, tags, ctx

def opposed_by(m, f, members):
    out = []
    for o in members:
        if o is m or not is_firm(o, f) or o.pole(f) == m.pole(f): continue
        if f in ONE_WAY:
            hi = sum(strength(x, f, 'high') for x in members); lo = sum(strength(x, f, 'low') for x in members)
            if o.pole(f) != ONE_WAY[f] and hi > lo: continue           # the lows do not oppose while the highs outnumber them
            if o.pole(f) == ONE_WAY[f] and lo > hi and m.pole(f) != ONE_WAY[f]: continue   # nor does a lone high force a low majority's #2s out
        out.append(o.name)
    return out
Dz.opposed_by = opposed_by
TOLERATE_TO = 70
_sat = Dz.satisfaction
def satisfaction(t, m, f):
    if f in ONE_WAY and m.pole(f) != ONE_WAY[f]:                 # the pole that can live with the other
        if S.delivers(t, m, f): return 1.0
        return Dz.DEGREE if t[f] <= TOLERATE_TO else 0.0
    return _sat(t, m, f)
Dz.satisfaction = satisfaction

def design(members, trace, hours=6, strangers=False):
    v, tags, ctx = chemistry_vector(members, strangers)
    trace.append('   chemistry vector: ' + ', '.join(f'{f} {v[f]:.0f}' for f in STOP_AXES) + (' | tags: ' + ', '.join(tags) if tags else ''))
    tops = {m.name: Dz.effective_top(m, members) for m in members}
    for m in members:
        f, sub, opp = tops[m.name]
        if f: trace.append(f'   {m.name}: top {f} {m.pole(f)}' + (f' - stands in for {Dz.ranked(m)[0]}, which {", ".join(opp)} firmly opposes' if sub else ''))
        else: trace.append(f'   {m.name}: easy tonight')
    n, note = D2.roam_count(members, hours, trace)
    if note: trace.append('   ' + note); tags.append('Settle Then Roam')
    bringing = [m for m in members if tops[m.name][0]]
    had = {m.name: set() for m in members}
    def coverage(nm): return sum(1 for m in members for f in PREFS if m.pref[f] >= S.PREF_WHOLE and f not in had[m.name] and any(x.type == nm and S.venue_has(x, f, m) for x in VENUES))
    stops, used, prev = [], [], -1
    for k in range(n):
        best = None
        for nm, t in TYPES.items():
            if nm == 'open ground' and k > 0: continue
            if ctx['talkers'] and t['TALK'] < TALK_FLOOR: continue                                  # the talk floor
            sat = {m.name: Dz.satisfaction(t, m, tops[m.name][0]) for m in bringing}
            compromise = any(x == 0.5 for x in sat.values())
            bridge = 1 if (compromise or (ctx['strangers'] and k == 0)) and t['GAMES'] >= 60 else 0  # Common Ground
            lo_a, hi_a = (62, 75) if ctx['affil_lean'] == 'high' else (50, 65) if ctx['affil_lean'] == 'low' else (55, 75)
            table_floor = 1 if ctx['affil_split'] and lo_a <= t['AFFIL'] <= hi_a and t['CROWD'] >= 60 else 0  # Table and Floor, leaning with the majority
            gpub = 1 if ctx['games_minority'] and 55 <= t['GAMES'] <= 70 else 0                            # a minority gamer: games on the premises, not the point
            floor_end = 1 if ctx['movers_win'] and k == n - 1 and t['MOVE'] >= 60 else 0                    # movers outnumber: the night ends on a floor
            key = (min(sat.values()) if sat else 1.0, round(sum(sat.values()), 2), nm not in used,
                   table_floor, bridge, gpub, floor_end, -t['ENRG'] if k == 0 else (t['ENRG'] >= prev - 10), coverage(nm),
                   -sum(abs(t[f] - v[f]) for f in STOP_AXES))                                       # closeness to the CHEMISTRY vector
            if best is None or key > best[0]: best = (key, nm, sat, bridge)
        _, nm, sat, bridge = best; used.append(nm); prev = TYPES[nm]['ENRG']
        if bridge and 'Common Ground' not in tags: tags.append('Common Ground')
        for m in members:
            for f in PREFS:
                if m.pref[f] >= S.PREF_WHOLE and any(x.type == nm and S.venue_has(x, f, m) for x in VENUES): had[m.name].add(f)
        stops.append((nm, {m.name: (sat.get(m.name, 1.0), tops[m.name][0], 'top') for m in members}, ''))
    stops.sort(key=lambda s: TYPES[s[0]]['ENRG'])
    # durations
    if 'Settle Then Roam' in tags and n > 1:
        durs = [hours * SETTLE_SHARE] + [hours * (1 - SETTLE_SHARE) / (n - 1)] * (n - 1)
    else: durs = [hours / n] * n
    # formation word if no tag
    mins = [min(s[1][m.name][0] for m in bringing) for s in stops] if bringing else [1.0]
    subs = [m for m in members if tops[m.name][1]]
    form = 'Open Night' if not bringing else 'Along for the Ride' if len(bringing) == 1 and len(members) > 1 else 'Something for Everyone' if min(mins) == 0 else 'Got Your Back' if subs else 'Best of Both' if min(mins) < 1 else 'In Sync'
    chip = form if form == 'Something for Everyone' else (tags[0] if tags else form)   # an absent top is always said
    return stops, chip, form, durs

def show(title, members, hours=6, strangers=False):
    print('\n' + title)
    trace = []
    stops, chip, form, durs = design(members, trace, hours, strangers)
    filled, missing = fill(stops, members, trace)
    print('\n'.join(trace))
    for k, (tname, vn, levels, note, sp) in enumerate(filled):
        line = f'  stop {k+1} ({durs[k]:.1f} h): [{tname}] {vn.name if vn else "-"}'
        for m in members:
            lvl, f, how = levels[m.name]
            line += f' | {m.name}: {(f"{f} {lvl:.1f}") if f else "easy":<12}'
        print(line)
    print(f'   chip: {chip}   (formation: {form})')

if __name__ == '__main__':
    show('N1. three at 70+ and one firm 12 - the highs outnumber: the room goes up',
         [M('Arjun', ENRG=88, CROWD=70), M('Dev', ENRG=78, MOVE=70), M('Zoya', ENRG=72, SCEN=88), M('Bela', ENRG=12, TALK=80, LIVE=88)])
    show('N2. one 88 and two firm 12s - the lows outnumber: the lively middle',
         [M('Arjun', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80, LIVE=88), M('Neha', ENRG=12, AFFIL=85, FOOD=92)])
    show('N3. one 88 and one firm 12 - a tie: the middle, leaning up', [M('Arjun', ENRG=88, CROWD=70), M('Bela', ENRG=12, TALK=80, LIVE=88)])
    show('AF1. three table people (AFFIL 88, 85, 82) and one room person (AFFIL 12): Table and Floor, leaning to the table',
         [M('Kabir', AFFIL=88, TALK=70), M('Meher', AFFIL=85, FOOD=88), M('Zoya', AFFIL=82), M('Rohan', AFFIL=12, ENRG=75)])
    show('AF2. one table person and three room people: Table and Floor, leaning to the room',
         [M('Kabir', AFFIL=88, TALK=70), M('Tia', AFFIL=15, CROWD=75), M('Vik', AFFIL=12, ENRG=78), M('Nia', AFFIL=18, MOVE=70)])
    show('G1. one gamer (Ali GAMES 90) among three non-gamers: games on the premises, not the point',
         [M('Ali', GAMES=90, AFFIL=70), M('Bani', AFFIL=88, TALK=75), M('Cyrus', TALK=80, FOOD=88), M('Dia', AFFIL=80, SCEN=88)])
    show('M1. two movers (MOVE 85, 80) and one sitter (MOVE 15): the night ends on a floor',
         [M('Vik', MOVE=85, ENRG=78), M('Tia', MOVE=80, CROWD=70), M('Sana', MOVE=15, TALK=72, SCEN=88)])
