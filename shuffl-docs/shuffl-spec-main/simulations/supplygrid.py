# -*- coding: utf-8 -*-
"""The live preview, grounded in supply: the type shown at each stop comes from what the database
actually holds at that hour inside the radius - not from a static table of type targets."""
import venuedb as DB

V = DB.V
# a few more venues so the low-energy / high-crowd corner is genuinely represented
DB.add('Old Delhi food walk', 'Old Delhi', [('street / market', 18, 23)], {18: (46, 80), 20: (52, 90), 23: (44, 72)},
       'social', dict(FOOD=88, LIVE=10, POL=15, SCEN=80, HERIT=90), 79, 11.0)
DB.add('Dilli Haat',          'INA',       [('street / market', 18, 22)], {18: (42, 78), 20: (46, 86), 22: (38, 64)},
       'conversational', dict(FOOD=74, LIVE=30, POL=25, SCEN=72, HERIT=70), 71, 7.8)
DB.add('Big Chill, Khan',     'Khan Mkt',  [('buzzy restaurant', 18, 23)], {18: (44, 76), 20: (48, 88), 23: (42, 66)},
       'social', dict(FOOD=86, LIVE=10, POL=55, SCEN=52, HERIT=40), 84, 8.2)
DB.add('Rose Cafe',           'Saket',     [('buzzy restaurant', 18, 23)], {18: (40, 70), 20: (44, 80), 23: (38, 58)},
       'conversational', dict(FOOD=80, LIVE=15, POL=62, SCEN=84, HERIT=30), 77, 5.1)
DB.add('Kitty Su',            'CP',        [('club', 22, 27)], {22: (76, 82), 25: (94, 94)},
       'loud', dict(FOOD=25, LIVE=35, POL=84, SCEN=60, HERIT=20), 73, 10.4)

# ============================================================ THE SUPPLY GRID
# precomputed nightly: (hour, energy bucket, crowd bucket, radius ring) -> types ranked by real supply
EB = CB = 10          # bucket width
def bucket(x): return int(x // 10) * 10

def build_grid(radius):
    g = {}
    for v in V:
        for h in range(18, 27):
            t = DB.type_at(v, h)
            if not t or v['km'] > radius: continue
            e, c = v['curve'][h]
            g.setdefault((h, bucket(e), bucket(c)), {}).setdefault(t, []).append(v)
    return g

def preview(grid, hour, e, c, room, radius):
    """what the box above the circle shows while the line is being dragged.
    Looks at the buckets around the drawn point, keeps types that actually have venues,
    then lets the room's OTHER factors veto and re-rank."""
    hits = {}
    for de in (-10, 0, 10):
        for dc in (-10, 0, 10):
            cell = grid.get((hour, bucket(e) + de, bucket(c) + dc), {})
            for t, vs in cell.items():
                for v in vs:
                    ve, vc = v['curve'][hour]
                    d = abs(ve - e) + 0.6 * abs(vc - c)
                    hits.setdefault(t, []).append((d, v))
    # the room's other factors: a firm talker is a veto, LIVE and MOVE are re-rankers
    out = []
    for t, lst in hits.items():
        if room['talkers'] and DB.TYPE_TARGET.get(t, DB.GAMES_TYPES.get(t, (0, 0, 99)))[2] < 40:
            continue                                            # talk floor vetoes the type outright
        lst.sort(key=lambda x: x[0])
        best = lst[0][0]
        score = 1 - best / 160.0
        if room['live'] >= 75 and t == 'live room':   score += .10
        if room['move'] >= 75 and t in ('club', 'street / market', 'open ground'): score += .06
        out.append((score, t, len(lst), lst[0][1]['name']))
    out.sort(reverse=True)
    return out

# ============================================================ THE USER'S EXAMPLE
# drawn at 8PM: two low-energy high-crowd stops, then one high-energy high-crowd stop
RADIUS = 12.0
GRID = build_grid(RADIUS)
ROOM = dict(talkers=True, live=40, move=70)          # one firm talker in the room
DRAWN = [(20, 42, 82), (22, 46, 78), (24, 84, 88)]   # (hour, energy, crowd) as dragged

print('=' * 92)
print('THE PREVIEW, GROUNDED IN SUPPLY   radius %.0f km, drawn at 20:00, one firm talker in the room' % RADIUS)
print('=' * 92)
for i, (h, e, c) in enumerate(DRAWN):
    opts = preview(GRID, h, e, c, ROOM, RADIUS)
    print()
    print('stop %d  @ %02d:00   drawn energy %d, crowd %d' % (i + 1, h, e, c))
    if not opts:
        print('   the box shows NOTHING OPEN LIKE THIS - "nothing this calm and this full near you at %02d:00"' % h)
        continue
    for s, t, n, ex in opts[:3]:
        mark = '  <- the box shows this' if (s, t, n, ex) == opts[0] else ''
        print('   %-20s fit %.2f   %d venue(s) actually open, e.g. %s%s' % (t, s, n, ex, mark))

# ---- and the same shape drawn at a different hour, to show the preview is time-dependent
print()
print('=' * 92)
print('THE SAME SHAPE, DRAWN LATER   (stops pushed to 22:00 / 24:00 / 02:00)')
print('=' * 92)
for i, (h, e, c) in enumerate([(22, 42, 82), (24, 46, 78), (26, 84, 88)]):
    opts = preview(GRID, h, e, c, ROOM, RADIUS)
    print()
    print('stop %d  @ %02d:00   drawn energy %d, crowd %d' % (i + 1, h % 24, e, c))
    if not opts:
        print('   the box shows NOTHING OPEN LIKE THIS - redraw, or the night ends earlier')
        continue
    for s, t, n, ex in opts[:3]:
        mark = '  <- the box shows this' if (s, t, n, ex) == opts[0] else ''
        print('   %-20s fit %.2f   %d venue(s) actually open, e.g. %s%s' % (t, s, n, ex, mark))

# ---- what the grid costs
cells = len(GRID)
print()
print('=' * 92)
print('grid size for this city at %.0f km: %d non-empty cells (9 hours x energy x crowd buckets)' % (RADIUS, cells))
print('a real city is bigger but the shape is the same - a few thousand cells, precomputed nightly,')
print('small enough to ship to the phone so the preview is an O(1) lookup while the line is dragged.')
