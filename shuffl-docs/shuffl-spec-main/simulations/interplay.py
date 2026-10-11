# -*- coding: utf-8 -*-
"""CHEMISTRY V3 - the interplay rules: how the people in a room move the ROOM's level on each axis.
One rule per axis, each from a finding. Influence aggregates sublinearly (Latane's social impact),
firmness multiplies it (Moscovici's consistent minority), and each axis has its own pull and asymmetry."""
import design2 as D2
from splitsim import M, VIBE, STOP_AXES

IMPACT_EXP = 0.6          # Latane: impact grows as N^t, t < 1 - the first person on a pole matters most
NEUTRAL_W  = 0.25         # a neutral has a weak pull toward the middle: they do not advocate

# per axis: (pull, discount on the non-dominant pole, dominant pole)  - see CHEMISTRY_V3.md for the finding behind each
AXIS = {
 'ENRG':  dict(pull=0.75, discount=0.55, dom='high'),   # arousal contagion, upward (Barsade; Hatfield)
 'TALK':  dict(pull=0.60, discount=0.50, dom='high'),   # a talker recruits others into talk (Thorne 1987; turn-taking)
 'MOVE':  dict(pull=0.70, discount=1.00, dom=None, tie_to='low'),   # venue-defining: a firm low is NOT discounted; a neutral is still movable (2026-09-22)
 'GAMES': dict(pull=0.50, discount=1.00, dom=None, tie_to='low', split_cap=65),   # venue-defining: a firm low is NOT discounted; a neutral is still movable (2026-09-22)
 'CROWD': dict(pull=0.25, discount=1.00, dom=None),     # appraisal, not affect - barely spreads (Stokols)
 'AFFIL': dict(pull=0.00, discount=1.00, dom=None),     # similar, not complementary: does not spread (Horowitz)
 'ROAM':  dict(pull=0.50, discount=1.00, dom=None, size_damped=True, split_band=(40, 60)),
 'RAMP':  dict(pull=0.50, discount=1.00, dom=None, split_band=(40, 60)),   # where the peak sits; a split is the peak-end compromise   # a quantity: a split settles in the middle  # coordination cost rises with the group (Steiner)
}

def strength(m, f, pole):
    s = m.vibe[f]
    on = (s >= 70) if pole == 'high' else (s <= 30)
    if not on: return 0.0
    if s >= 80 or s <= 20: return 1.0
    return 0.75 if D2.fast(m, f) else 0.5

def impact(members, f, pole, discount):
    tot = sum(strength(m, f, pole) for m in members)
    return (tot ** IMPACT_EXP) * (1.0 if discount == 1.0 else discount) if tot else 0.0

def room_level(members, f, trace=None):
    """base = the plain mean (where the room sits before anyone leads); then the leading pole pulls it,
    by its share of the influence in the room."""
    cfg = AXIS[f]
    base = sum(m.vibe[f] for m in members) / len(members)
    hi_raw = sum(strength(m, f, 'high') for m in members); lo_raw = sum(strength(m, f, 'low') for m in members)
    if hi_raw == 0 and lo_raw == 0: return base, 'nobody leads'
    dom = cfg['dom']
    I_hi = impact(members, f, 'high', cfg['discount'] if dom == 'low' else 1.0)
    I_lo = impact(members, f, 'low',  cfg['discount'] if dom == 'high' else 1.0)
    neutrals = [m for m in members if 31 <= m.vibe[f] <= 69]
    I_n = (len(neutrals) ** IMPACT_EXP) * NEUTRAL_W if neutrals else 0.0
    lead = ('high' if I_hi > I_lo else 'low') if cfg.get('tie_to') == 'low' else ('high' if I_hi >= I_lo else 'low')   # venue-defining: a tie goes to the low pole
    I_lead, I_rest = (I_hi, I_lo + I_n) if lead == 'high' else (I_lo, I_hi + I_n)
    share = I_lead / (I_lead + I_rest) if (I_lead + I_rest) else 0.0
    side = [m for m in members if strength(m, f, lead) > 0] or [m for m in members if 31 <= m.vibe[f] <= 69]
    peak = max(m.vibe[f] for m in side) if lead == 'high' else min(m.vibe[f] for m in side)
    pull = cfg['pull']
    if cfg.get('threshold') and sum(strength(m, f, lead) for m in side) < cfg['threshold']: pull *= 0.5
    if cfg.get('size_damped'): pull *= 2.0 / max(2, len(members))
    lvl = base + pull * share * (peak - base)
    band = cfg.get('split_band')
    if band and any(m.vibe[f] >= 70 for m in members) and any(m.vibe[f] <= 30 for m in members):
        # ROAM is a QUANTITY, not an atmosphere: with positions on both poles nobody gets their own
        # number. The room splits the difference - three places never becomes one, one never becomes three.
        clamped = min(max(lvl, band[0]), band[1])
        if abs(clamped - lvl) > 0.01:
            why_extra = f' -> split the difference, clamped to {clamped:.0f}'
            lvl = clamped
        else: why_extra = ''
    else: why_extra = ''
    why = f'{lead}s lead (impact {I_lead:.2f} v {I_rest:.2f}, share {share:.2f}) pull {pull:.2f} -> {lvl:.0f} from a mean of {base:.0f}' + why_extra
    return lvl, why

def room(members, verbose=True):
    v, notes = {}, []
    for f in STOP_AXES + ['ROAM', 'RAMP']:
        lvl, why = room_level(members, f)
        v[f] = lvl; notes.append(f'{f} {lvl:.0f}  ({why})')
    # ---- cross-axis rules
    x = []
    if v['AFFIL'] >= 70: v['CROWD'] += 8; x.append('AFFIL >= 70 buffers crowding (+8 CROWD): your own people make a full room safe (Evans & Lepore)')
    if v['MOVE'] >= 65:  v['ENRG'] += 5; x.append('a moving room is a rising room (+5 ENRG): synchrony raises arousal')
    if v['ENRG'] >= 75 and v['MOVE'] < 60:  v['MOVE'] = min(60, v['MOVE'] + 5); x.append('a rising room gets on its feet (+5 MOVE, capped at 60): room to stand, never a floor nobody asked for')
    firm_split = [f for f in STOP_AXES if f != 'GAMES'                                  # a room split ABOUT games is not bridged by games
                  and any(strength(m, f, 'high') > 0 for m in members) and any(strength(m, f, 'low') > 0 for m in members)]
    if firm_split:
        cap = AXIS['GAMES']['split_cap']
        if v['GAMES'] < cap: v['GAMES'] = min(cap, v['GAMES'] + 10); x.append(f'the room is split on {", ".join(firm_split)} (+10 GAMES, capped at {cap}): a shared task holds a divided group together (Sherif) - but only as far as a games pub, never a games bar')
    # AFFIL does not average: a split room has no level, it has two poles
    a_hi = sum(strength(m, 'AFFIL', 'high') for m in members); a_lo = sum(strength(m, 'AFFIL', 'low') for m in members)
    if a_hi > 0 and a_lo > 0: v['AFFIL'] = 'split'
    if verbose:
        for n in notes:
            f = n.split()[0]
            print('     ' + (f'{f} {v[f]}' if isinstance(v[f], str) else f'{f} {v[f]:.0f}') + n[n.index('  ('):])
        for n in x: print('     x ' + n)
    return v

def show(title, members):
    print('\n' + title)
    for m in members: print('     ' + m.name + ': ' + ', '.join(f'{f} {m.vibe[f]}' for f in VIBE if abs(m.vibe[f] - 50) >= 18))
    room(members)

if __name__ == '__main__':
    show('1. ENRG - two 88s and two neutrals (the spark)', [M('A', ENRG=88), M('B', ENRG=85), M('C', ENRG=45), M('D', ENRG=50)])
    show('2. ENRG - one 88 and two firm 12s', [M('A', ENRG=88), M('B', ENRG=12), M('C', ENRG=12)])
    show('3. ENRG - three at 70+ and one firm 12', [M('A', ENRG=88), M('B', ENRG=78), M('C', ENRG=72), M('D', ENRG=12)])
    show('4. TALK - one firm talker among two low-talk people', [M('A', TALK=88), M('B', TALK=20), M('C', TALK=20)])
    show('5. TALK - one noise-wanter among two talkers', [M('A', TALK=12), M('B', TALK=85), M('C', TALK=82)])
    show('6. MOVE - a lone mover (no first follower)', [M('A', MOVE=88), M('B', MOVE=45), M('C', MOVE=40)])
    show('7. MOVE - two movers (the first follower arrives)', [M('A', MOVE=88), M('B', MOVE=82), M('C', MOVE=40)])
    show('8. GAMES - one gamer among three non-gamers', [M('A', GAMES=90), M('B', GAMES=40), M('C', GAMES=45), M('D', GAMES=38)])
    show('9. CROWD - one crowd-lover among two haters', [M('A', CROWD=90), M('B', CROWD=20), M('C', CROWD=25)])
    show('10. CROWD x AFFIL - a crowd-lover with two table people', [M('A', CROWD=90, AFFIL=72), M('B', AFFIL=88), M('C', AFFIL=85)])
    show('11. AFFIL - a table majority and one room person (no spread)', [M('A', AFFIL=88), M('B', AFFIL=85), M('C', AFFIL=12)])
    show('12. ROAM - one roamer in a pair', [M('A', ROAM=92), M('B', ROAM=45)])
    show('13. ROAM - one roamer in a five', [M('A', ROAM=92), M('B', ROAM=45), M('C', ROAM=50), M('D', ROAM=48), M('E', ROAM=52)])
    show('14. ENRG x MOVE - a moving room lifts its own energy', [M('A', ENRG=70, MOVE=88), M('B', ENRG=68, MOVE=82), M('C', ENRG=55, MOVE=60)])
    show('15. the split bonus - a room divided on energy gets games', [M('A', ENRG=88, GAMES=50), M('B', ENRG=12, GAMES=45), M('C', ENRG=50, GAMES=48)])
