# -*- coding: utf-8 -*-
"""The alternative wordmark as a transparent PNG, and the open-screen animation."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

PINK, CYAN = '#FF2E7A', '#24E0FF'
INK, OFFW = '#060609', '#FBFAFF'

B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]
DOTS = ''.join('<circle cx="%s" cy="%s" r="5.4"/>' % (x, y) for x, y in B8)

FONT = "font-family:'Bebas Neue';letter-spacing:.14em"

# geometry in the 498 x 140 wordmark box
CIRC_X, CIRC_Y = 212.0, 67.0
SH_C = (50.0, 67.0)        # SH's optical centre at rest
FFL_C = (410.0, 67.0)      # FFL's optical centre at rest
CARD_DX = 66.0             # how far each card sits from the circle's centre at rest


# ---------------------------------------------------------------- easing
def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def seg(t, start, dur):
    """local 0..1 progress of a segment that begins at `start` and lasts `dur`"""
    if dur <= 0:
        return 1.0
    return max(0.0, min(1.0, (t - start) / dur))


# ---------------------------------------------------------------- one frame
def frame_svg(t, w=520, view='-22 -6 542 152',
              ink=OFFW, ring=INK, face=OFFW, dot=INK):
    """t runs 0..1 over the whole opening"""
    e_card = ease_out_cubic(seg(t, 0.00, 0.70))
    e_ghost = ease_out_cubic(seg(t, 0.00, 0.80))     # the trail lags the card
    e_let = ease_out_cubic(seg(t, 0.22, 0.68))
    e_spin = ease_out_cubic(seg(t, 0.00, 1.00))
    e_disc = ease_out_cubic(seg(t, 0.00, 0.40))

    cdx = CARD_DX * (1 - e_card)          # +66 at the centre, 0 at rest
    gdx = CARD_DX * (1 - e_ghost)
    crot = e_card                          # 0 stacked, 1 fanned
    cscale = 0.88 + 0.12 * e_card

    def letter(txt, x, cx_rest, cy_rest):
        s = 0.12 + 0.88 * e_let
        px = CIRC_X + (cx_rest - CIRC_X) * e_let
        py = CIRC_Y + (cy_rest - CIRC_Y) * e_let
        tx = px - cx_rest * s
        ty = py - cy_rest * s
        op = min(1.0, seg(t, 0.22, 0.17) * 1.0)
        return ('<g transform="translate(%.2f,%.2f) scale(%.4f)" opacity="%.3f">'
                '<text x="%s" y="104" style="%s" font-size="102" fill="%s">%s</text></g>'
                % (tx, ty, s, op, x, FONT, ink, txt))

    ang = -320 * (1 - e_spin)
    ds = 0.74 + 0.26 * e_disc

    return ('<svg viewBox="%s" width="%s">'
            # letters sit behind everything, so a card hides one until they separate
            '%s%s'
            # ghost trails
            '<g transform="translate(%.2f,0)" opacity=".32">'
            '<g transform="translate(134,39) rotate(%.2f) scale(%.4f)">'
            '<rect width="47" height="68" rx="8" fill="%s"/></g></g>'
            '<g transform="translate(%.2f,0)" opacity=".32">'
            '<g transform="translate(290,39) rotate(%.2f) translate(-47,0) scale(%.4f)">'
            '<rect width="47" height="68" rx="8" fill="%s"/></g></g>'
            # the cards
            '<g transform="translate(%.2f,0)">'
            '<g transform="translate(110,47) rotate(%.2f) scale(%.4f)">'
            '<rect width="47" height="68" rx="8" fill="%s"/></g></g>'
            '<g transform="translate(%.2f,0)">'
            '<g transform="translate(314,47) rotate(%.2f) translate(-47,0) scale(%.4f)">'
            '<rect width="47" height="68" rx="8" fill="%s"/></g></g>'
            # the room, on top, turning
            '<g transform="translate(%s,%s) scale(%.4f)">'
            '<circle r="33" fill="%s"/><circle r="26" fill="%s"/>'
            '<g transform="rotate(%.2f) scale(.79)" fill="%s">%s</g></g>'
            '</svg>'
            % (view, w,
               letter('SH', 0, *SH_C), letter('FFL', 322, *FFL_C),
               gdx, -13 * crot, cscale, PINK,
               -gdx, 13 * crot, cscale, CYAN,
               cdx, -26 * crot, cscale, PINK,
               -cdx, 26 * crot, cscale, CYAN,
               CIRC_X, CIRC_Y, ds, ring, face, ang, dot, DOTS))


# ---------------------------------------------------------------- 1. the still PNG
SHELL = ('<!doctype html><html><head><meta charset="utf-8">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Bebas+Neue&display=swap">'
         '<style>html,body{margin:0;background:transparent}'
         'body{display:inline-block}</style></head><body>%s</body></html>')
V = '-14 14 526 112'
io.open(os.path.join(D, 'wm_alt_onDark.html'), 'w', encoding='utf-8').write(
    SHELL % frame_svg(1.0, w=2200, view=V))
io.open(os.path.join(D, 'wm_alt_onLight.html'), 'w', encoding='utf-8').write(
    SHELL % frame_svg(1.0, w=2200, view=V, ink='#1A1A22', ring='#1A1A22',
                      face=OFFW, dot='#1A1A22'))

# ---------------------------------------------------------------- 2. frame strip
N = 26          # 22 moving, 4 holding
FW, FH = 540, 170
strip = ['<!doctype html><html><head><meta charset="utf-8">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Bebas+Neue&display=swap">'
         '<style>html,body{margin:0;background:#060609}'
         '.f{width:%spx;height:%spx;display:grid;place-items:center;overflow:hidden}'
         '</style></head><body>' % (FW, FH)]
for i in range(N):
    t = min(1.0, i / 21.0)
    strip.append('<div class="f">%s</div>' % frame_svg(t, w=470))
strip.append('</body></html>')
io.open(os.path.join(D, 'anim_strip.html'), 'w', encoding='utf-8').write('\n'.join(strip))

# ---------------------------------------------------------------- 3. keyframe sheet
KEYS = [(0.00, "0 ms · STACKED", "Both cards square on, one behind the other, sitting under the "
         "room. <b>The letters are there but tiny and hidden behind the cards.</b>"),
        (0.18, "250 ms · THE SWIPE STARTS", "The cards fan apart and begin to travel outward. "
         "The room is already turning and has snapped up to full size."),
        (0.38, "530 ms · LETTERS EMERGE", "<b>SH comes out of the pink card and FFL out of the "
         "cyan</b> — they are painted behind the cards, so separation alone reveals them."),
        (0.58, "810 ms · TRAILS OPEN", "The ghost cards lag behind the solid ones, which is "
         "what makes it read as a swipe rather than a slide."),
        (0.80, "1120 ms · SETTLING", "Cards near their rest angles, letters near full size. "
         "The room is finishing its turn."),
        (1.00, "1400 ms · AT REST", "<b>The wordmark exactly as locked</b> — optical gap "
         "10 either side, cards at ±26°, ghosts at ±13°.")]
sheet = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — opening animation</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
  :root{color-scheme:dark}
  html,body{background:#060609;margin:0}
  body{font-family:"Instrument Sans",sans-serif;color:#FBFAFF;padding:30px 36px;width:1160px}
  h1{font-family:"Archivo";font-weight:800;letter-spacing:-.03em;font-size:28px;margin:0 0 4px}
  h2{font-family:"Archivo";font-weight:700;font-size:17px;margin:30px 0 6px}
  .sub{color:#9C98AE;font-size:12.5px;line-height:1.55;max-width:94ch;margin:0 0 20px}
  .lab{font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
       text-transform:uppercase;color:#6C6880}
  .cell{background:#0D0D12;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:16px;
        display:flex;flex-direction:column;gap:9px}
  .art{display:grid;place-items:center;overflow:hidden}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.42}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-bottom:16px}
  table{border-collapse:collapse;width:100%;font-size:11px}
  th,td{text-align:left;padding:7px 10px;border-bottom:1px solid rgba(255,255,255,.09)}
  th{font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.18em;
     text-transform:uppercase;color:#6C6880;font-weight:400}
  td{color:#C9C5D6}
  td:first-child{font-family:"IBM Plex Mono",monospace;color:#FBFAFF}
</style></head><body>
<h1>SH:FFL &middot; the opening animation</h1>
<p class="sub"><b>The cards swipe out of the room and leave the name behind them.</b> Both cards start
square on and stacked under the disc; they fan apart and travel outward; <b>SH comes out of the pink
card and FFL out of the cyan</b>; the room turns throughout and stops when they do. The letters are
painted <b>behind</b> the cards, so nothing is masked — separation is what reveals them, which
is why it reads as physical rather than as a fade.</p>
<h2>Six keyframes</h2><div class="g2">"""]
for t, lab, note in KEYS:
    sheet.append('<div class="cell"><div class="lab">%s</div>'
                 '<div class="art" style="min-height:150px">%s</div>'
                 '<div class="note">%s</div></div>' % (lab, frame_svg(t, w=460), note))
sheet.append('</div>')

sheet.append('<h2>The timing, for the developer</h2>'
             '<p class="sub">Total <b>1400 ms</b>. Every track is <b>ease-out cubic</b> '
             '(<code>1-(1-x)³</code>) — fast away from the centre, slow into rest, which '
             'is how a swiped card actually behaves. <b>Nothing bounces</b>: an overshoot would '
             'make the cards look light, and these are meant to have weight.</p>')
sheet.append('<div class="cell"><table><tr><th>Track</th><th>Starts</th><th>Ends</th>'
             '<th>From</th><th>To</th></tr>'
             '<tr><td>Card travel</td><td>0 ms</td><td>980 ms</td>'
             '<td>&plusmn;66 toward centre</td><td>0 (rest)</td></tr>'
             '<tr><td>Card fan</td><td>0 ms</td><td>980 ms</td><td>0&deg;</td>'
             '<td>&minus;26&deg; left, +26&deg; right</td></tr>'
             '<tr><td>Card scale</td><td>0 ms</td><td>980 ms</td><td>0.88</td><td>1.00</td></tr>'
             '<tr><td>Ghost travel</td><td>0 ms</td><td>1120 ms</td>'
             '<td>&plusmn;66 toward centre</td><td>0 (rest)</td></tr>'
             '<tr><td>Letters, position</td><td>310 ms</td><td>1260 ms</td>'
             '<td>circle centre</td><td>rest</td></tr>'
             '<tr><td>Letters, scale</td><td>310 ms</td><td>1260 ms</td><td>0.12</td>'
             '<td>1.00</td></tr>'
             '<tr><td>Letters, opacity</td><td>310 ms</td><td>550 ms</td><td>0</td><td>1</td></tr>'
             '<tr><td>Room, rotation</td><td>0 ms</td><td>1400 ms</td><td>&minus;320&deg;</td>'
             '<td>0&deg;</td></tr>'
             '<tr><td>Room, scale</td><td>0 ms</td><td>560 ms</td><td>0.74</td><td>1.00</td></tr>'
             '</table><div class="note" style="margin-top:12px"><b>The ghost finishes 140 ms after '
             'the card it trails.</b> That lag is the whole trick — identical timing makes the '
             'pair read as one thick card, and the trail only becomes a trail when it is late.'
             '</div></div>')
sheet.append('<p class="sub"><b>Two things to hold the developer to.</b> First, <b>the letters are '
             'behind the cards in paint order</b> — no masks, no clipping paths; if they are '
             'drawn on top the reveal stops working and no amount of timing fixes it. Second, '
             '<b>the room’s rotation ends last</b>, 140 ms after everything else has settled, '
             'so the mark arrives and then quietly stops rather than everything landing on one '
             'beat.</p>')
sheet.append('</body></html>')
io.open(os.path.join(D, 'anim_sheet.html'), 'w', encoding='utf-8').write('\n'.join(sheet))
print('written', N)
