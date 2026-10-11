# -*- coding: utf-8 -*-
"""One full night, end to end: three imaginary users, swipes -> scores -> chemistry -> readings -> types -> venues."""
import readings as RD, interplay as IP, design3 as D3, design as Dz, design2 as D2
from splitsim import M, TYPES, STOP_AXES, PREFS, VIBE, fill, ranked_wants, delivers, venue_has

RAVI  = M('Ravi',  ENRG=88, CROWD=75, MOVE=62, TALK=38, AFFIL=50, ROAM=62, GAMES=38,
          POL=88, NOV=62, LIVE=62, SCEN=62, FOOD=38, HERIT=12, sense='current')
SANA  = M('Sana',  TALK=88, AFFIL=88, ENRG=50, CROWD=38, ROAM=12, MOVE=38, GAMES=50,
          FOOD=88, SCEN=62, HERIT=62, LIVE=38, POL=38, NOV=38, sense='classy')
KABIR = M('Kabir', GAMES=88, ROAM=75, ENRG=62, AFFIL=50, CROWD=50, TALK=62, MOVE=50,
          NOV=88, FOOD=62, LIVE=38, POL=38, SCEN=38, HERIT=12)
G = [RAVI, SANA, KABIR]
HOURS = 6

print('=== 1. what each person is, after the deck ===')
for m in G:
    print(f'{m.name:<6} vibe ' + ' '.join(f'{f} {m.vibe[f]}' for f in STOP_AXES))
    print(f'{"":<6} firm on ' + (', '.join(f'{f}' for f in VIBE if D3.is_firm(m, f)) or 'nothing') +
          '   | bends: ' + ' '.join(f'{f} {m.bend(f):.0f}' for f in STOP_AXES))
    print(f'{"":<6} wants (ranked) ' + str(ranked_wants(m)) + f'   overall firmness {m.overall():.2f}')
    print(f'{"":<6} prefs ' + ' '.join(f'{f} {m.pref[f]}' for f in PREFS) + f' sense={m.sense}')

print('\n=== 2. the room: Chemistry V3 interplay (interplay.py) ===')
v3 = IP.room(G, verbose=True)

print('\n=== 3. the room as the planner reads it (design3, what readings.py calls) ===')
v2, tags, ctx = D3.chemistry_vector(G)
print('   levels: ' + ', '.join(f'{f} ' + (v2[f] if isinstance(v2[f], str) else f'{v2[f]:.0f}') for f in STOP_AXES))
print('   tags: ', tags)
print('   ctx: ', {k: ctx[k] for k in ctx if k not in ('strangers',)})

print('\n=== 4. readings (demands on the stop types) ===')
R, stops, chip = RD.plan_room_first(G, HOURS)
for a, (k, val), w in R:
    print(f'   {a:<6} {k:<20} {val}   weight {w}')

print('\n=== 5. stops ===')
tr = []
n, note = D2.roam_count(G, HOURS, tr)
print(f'   ROAM -> {n} stops over {HOURS}h. {note}')
if 'Settle Then Roam' in tags or note:
    durs = [HOURS * D3.SETTLE_SHARE] + [HOURS * (1 - D3.SETTLE_SHARE) / (n - 1)] * (n - 1) if n > 1 else [HOURS]
    print('   durations: ' + ', '.join(f'{d:.1f}h' for d in durs))

filled, missing = fill(stops, G, [])
tops = {m.name: Dz.effective_top(m, G) for m in G}
print('\n=== 6. the night ===')
for i, (tname, ven, levels, nt, sp) in enumerate(filled, 1):
    t = TYPES[tname]
    print(f'   stop {i}: [{tname}] {ven.name if ven else "-"}   type axes: ' + ' '.join(f'{f} {t[f]}' for f in STOP_AXES))
    for m in G:
        top, sub, opp = tops[m.name]
        s = levels[m.name][0]
        word = 'fully' if s == 1.0 else ('to a degree' if s == 0.5 else 'ABSENT')
        print(f'      {m.name:<6} top={top}{" (stand-in, opposed by " + ",".join(o.name for o in opp) + ")" if sub else ""}: {word}'
              f'   | prefs served: {sp.get(m.name)}')
print('   chip:', chip)
print('   whole-point preferences the night could not serve:', missing)
