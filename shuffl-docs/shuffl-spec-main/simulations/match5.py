# -*- coding: utf-8 -*-
"""13.6.3 v5 - the joiner's match, in the vocabulary of the readings model.

Two different questions, two different numbers, as 13.4a already says:
  FIT         - is this night mine?          the joiner's list, and the order of the room player
  DISTURBANCE - would they change our night?  the host's request list

Nothing here uses payback, debt, room states or the retired formation words: the room is re-read
and re-planned with the joiner in it, and what changed is the answer.
"""
import readings as RD, design as Dz, design2 as D2
from splitsim import TYPES, STOP_AXES, PREFS, PREF_WHOLE, venue_has, fill

# ---------------------------------------------------------------- the joiner's question
def fit(joiner, stops, venues=None):
    """0..1 - how well this frozen plan serves the joiner. Their own top factor at each stop,
    then their whole-point preferences across the night. Reads the plan, never the other members."""
    top = Dz.effective_top(joiner, [joiner])[0]
    sat = [Dz.satisfaction(TYPES[t], joiner, top) for t in stops]
    vibe = sum(sat) / len(sat) if sat else 1.0
    whole = [f for f in PREFS if joiner.pref[f] >= PREF_WHOLE]
    if whole and venues:
        served = sum(1 for f in whole if any(v and venue_has(v, f, joiner) for v in venues))
        pref = served / float(len(whole))
    else:
        pref = 1.0
    return 0.75 * vibe + 0.25 * pref, dict(per_stop=sat, prefs=pref)

# ---------------------------------------------------------------- the host's question
def disturbance(members, joiner, hours=6):
    """Re-read the room with the joiner in it and report what changed."""
    R0, stops0, chip0 = RD.plan_room_first(members, hours)
    R1, stops1, chip1 = RD.plan_room_first(members + [joiner], hours)
    t0 = [s[0] for s in stops0]; t1 = [s[0] for s in stops1]
    changed = sum(1 for i in range(min(len(t0), len(t1))) if t0[i] != t1[i]) + abs(len(t0) - len(t1))

    key0 = {(a, k) for a, (k, _), _ in R0}
    key1 = {(a, k) for a, (k, _), _ in R1}
    w0 = {(a, k): w for a, (k, _), w in R0}
    lost = key0 - key1
    added = key1 - key0
    heavy_lost = [x for x in lost if w0.get(x, 0) >= 14]          # a demand the room held firmly

    def absents(stops, who):
        out = set()
        for st in stops:
            for m in who:
                lv = st[1].get(m.name)
                if lv and lv[1] and lv[0] == 0: out.add(m.name)
        return out
    newly_absent = absents(stops1, members + [joiner]) - absents(stops0, members)

    # does the joiner add to what the room already is, on the axes the room has a position on
    agree = tot = 0
    for a, (k, val), w in R0:
        if a == 'ENRG':
            want_high = (val if not isinstance(val, tuple) else 50) >= 55
        elif k in ('table', 'full', 'games', 'floor', 'floor-at-the-end', 'talkable'): want_high = True
        elif k in ('quiet', 'loud', 'seated', 'no-games'): want_high = False
        else: continue
        if abs(joiner.vibe[a] - 50) < 12: continue                # no position: neither adds nor subtracts
        tot += 1
        if (joiner.vibe[a] >= 50) == want_high: agree += 1
    reinf = (agree / float(tot)) if tot else 0.0

    return dict(changed=changed, stops=len(t1), lost=lost, added=added, heavy_lost=heavy_lost,
                newly_absent=newly_absent, reinf=reinf, chip_before=chip0, chip_after=chip1,
                types_before=t0, types_after=t1, tot=tot)

def open_night(joiner, firm_of):
    """A room with no readings has no night yet: the more positions the joiner brings, the better."""
    n_firm = sum(1 for f in STOP_AXES + ['ROAM', 'RAMP'] if firm_of(joiner, f))
    return 'great' if n_firm >= 5 else 'alright'

def grade(d, frozen=True, fit_value=None, FIT_POOR=0.4):
    """great / alright / poor.

    frozen=True  (the room is hosted, so the plan cannot change): d is a COUNTERFACTUAL - how far
                 the night this room would now plan sits from the one it is committed to. The
                 joiner's own fit is the direct number and it can veto on its own.
    frozen=False (the room is still open, the plan re-plans as people join): d is literal."""
    if frozen and fit_value is not None and fit_value < FIT_POOR: return 'poor'
    if d['newly_absent']:                       return 'poor'
    if d['heavy_lost']:                         return 'poor'
    if d['changed'] > max(1, d['stops'] // 2):  return 'poor'
    if d['changed'] == 0 and d['reinf'] >= 0.5: return 'great'
    return 'alright'      # includes the easy joiner: nothing changes, but nothing is added either

# ---------------------------------------------------------------- demo
if __name__ == '__main__':
    from splitsim import M
    N = dict(ENRG=50, AFFIL=50, CROWD=50, TALK=50, ROAM=50, RAMP=50, MOVE=50, GAMES=50)
    def mk(n, **kw):
        d = dict(N); d.update(kw); return M(n, **d)
    ROOM = [mk('Ravi', ENRG=88, CROWD=75), mk('Sana', AFFIL=88, TALK=88), mk('Kabir', GAMES=88)]
    R0, stops0, chip0 = RD.plan_room_first(ROOM, 6)
    f0, _ = fill(stops0, ROOM, [])
    print('the room:  ' + ' -> '.join(f'[{t}] {(v.name.split(" (")[0] if v else "-")}' for t, v, l, n, sp in f0) + '   chip: ' + chip0)
    print('           readings: ' + '; '.join(f'{a} {k}' for a, (k, _), w in R0))
    print()
    CANDS = [
        ('Ira    - another high-energy crowd person', mk('Ira', ENRG=85, CROWD=80)),
        ('Bela   - firm low energy, firm talker',     mk('Bela', ENRG=12, TALK=85)),
        ('Divit  - no strong wants at all',           mk('Divit')),
        ('Nina   - out to meet the room, wants a floor', mk('Nina', AFFIL=12, MOVE=88)),
        ('Rhea   - a settler who wants one place',    mk('Rhea', ROAM=12, TALK=80)),
        ('Vik    - wants a quiet near-empty room',    mk('Vik', CROWD=12, ENRG=20)),
    ]
    for label, j in CANDS:
        d = disturbance(ROOM, j)
        fv, det = fit(j, [s[0] for s in stops0], [v for t, v, l, n, sp in f0])
        g = grade(d, frozen=True, fit_value=fv)
        print(f'{label:<44} {g:<8} fit {fv:.2f}  stops changed {d["changed"]}/{d["stops"]}  reinf {d["reinf"]:.2f}')
        if d['newly_absent']: print(f'{"":44}   nobody-gets-nothing broken for: {", ".join(sorted(d["newly_absent"]))}')
        if d['heavy_lost']:   print(f'{"":44}   the room loses: {", ".join(a + " " + k for a, k in d["heavy_lost"])}')
        if d['chip_after'] != d['chip_before']: print(f'{"":44}   chip {d["chip_before"]} -> {d["chip_after"]}')
        print(f'{"":44}   {" -> ".join(d["types_after"])}')
