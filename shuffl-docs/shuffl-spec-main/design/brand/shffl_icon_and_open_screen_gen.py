# -*- coding: utf-8 -*-
"""Chameleon as the icon; chameleon + SH[mark]FFL as the open screen."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

PINK, CYAN = '#FF2E7A', '#24E0FF'
INK, LITE = '#060609', '#F4F2F8'
OFFW, DEEP = '#FBFAFF', '#1A1A22'
INK2, TEAL, EYEDK = '#121218', '#0E7E93', '#12000A'

BODY = ("M88 170 C92 134 110 108 142 95 C174 82 200 76 220 72 C230 70 238 64 244 54 "
        "L252 30 L268 62 C276 72 286 80 296 86 L326 96 L300 110 L330 122 "
        "C308 138 282 148 252 153 C208 161 138 168 88 170 Z")
TAIL = ("M88 168 C62 168 46 180 46 196 C46 210 58 220 72 220 C84 220 93 212 93 201 "
        "C93 192 86 186 78 186 C72 186 68 190 68 195")
TONG = "M328 114 C364 114 380 102 396 86 C410 72 428 64 448 66"

# the chameleon drawn in its own coordinates: x 30..470, y 20..235
CH_W, CH_H = 440.0, 215.0


def cham_g(body=PINK, tongue=CYAN, iris=OFFW):
    return ('<path d="%s" fill="%s"/>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="15" stroke-linecap="round"/>'
            '<circle cx="268" cy="96" r="18" fill="%s"/>'
            '<circle cx="268" cy="96" r="10.5" fill="%s"/>'
            '<circle cx="271" cy="96" r="4" fill="%s"/>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
            '<circle cx="372" cy="100" r="8" fill="%s"/>'
            '<circle cx="410" cy="71" r="12" fill="%s"/>'
            '<circle cx="446" cy="66" r="17" fill="%s"/>'
            % (BODY, body, TAIL, body, EYEDK, iris, EYEDK,
               TONG, tongue, tongue, tongue, tongue))


def cham_box(scale, body=PINK, tongue=CYAN, iris=OFFW):
    """returns (svg group placed at 0,0, width, height)"""
    g = ('<g transform="scale(%s) translate(-30,-20)">%s</g>'
         % (scale, cham_g(body, tongue, iris)))
    return g, CH_W * scale, CH_H * scale


# ---------------------------------------------------------------- the wordmark
# F lockup at optical gap 10, in its own 498 x 140 box
B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]


def wordmark_g(c1=PINK, c2=CYAN, ink=OFFW, ring=INK, face=OFFW, dot=INK,
               font="'Bebas Neue'", size=102, ls='.14em', x_ffl=322):
    dots = ''.join('<circle cx="%s" cy="%s" r="5.4"/>' % (x, y) for x, y in B8)
    mark = ('<g fill="%s">'
            '<g transform="translate(24,39) rotate(-13)" opacity=".32">'
            '<rect width="47" height="68" rx="8"/></g>'
            '<g transform="translate(0,47) rotate(-26)"><rect width="47" height="68" rx="8"/></g></g>'
            '<g fill="%s">'
            '<g transform="translate(180,39) rotate(13) translate(-47,0)" opacity=".32">'
            '<rect width="47" height="68" rx="8"/></g>'
            '<g transform="translate(204,47) rotate(26) translate(-47,0)">'
            '<rect width="47" height="68" rx="8"/></g></g>'
            '<circle cx="102" cy="67" r="33" fill="%s"/>'
            '<circle cx="102" cy="67" r="26" fill="%s"/>'
            '<g transform="translate(102,67) scale(.79)" fill="%s">%s</g>'
            % (c1, c2, ring, face, dot, dots))
    sty = 'font-family:%s;letter-spacing:%s' % (font, ls)
    return ('<text x="0" y="104" style="%s" font-size="%s" fill="%s">SH</text>'
            '<g transform="translate(110,0)">%s</g>'
            '<text x="%s" y="104" style="%s" font-size="%s" fill="%s">FFL</text>'
            % (sty, size, ink, mark, x_ffl, sty, size, ink))


WM_W, WM_H = 498.0, 140.0


def lockup_h(w=880, body=PINK, tongue=CYAN, c1=PINK, c2=CYAN, ink=OFFW,
             ring=INK, face=OFFW, dot=INK, font="'Bebas Neue'", size=102, ls='.14em',
             x_ffl=322, wm_w=498.0):
    """chameleon left, wordmark right, optical centres aligned"""
    cs = 0.75
    ch, cw, chh = cham_box(cs, body, tongue)
    gap = 44
    wx = cw + gap
    wy = chh / 2.0 - 67          # 67 is the wordmark's cap-height centre
    total_w = wx + wm_w
    total_h = max(chh, wy + WM_H)
    return ('<svg viewBox="0 %s %s %s" width="%s">%s'
            '<g transform="translate(%s,%s)">%s</g></svg>'
            % (round(min(0, wy), 1), round(total_w, 1), round(total_h - min(0, wy), 1), w,
               ch, round(wx, 1), round(wy, 1),
               wordmark_g(c1, c2, ink, ring, face, dot, font, size, ls, x_ffl)))


def splash(w=460, body=PINK, tongue=CYAN, c1=PINK, c2=CYAN, ink=OFFW,
           ring=INK, face=OFFW, dot=INK):
    """stacked for a phone open screen"""
    cs = 0.95
    ch, cw, chh = cham_box(cs, body, tongue)
    ws = 0.92
    ww, wh = WM_W * ws, WM_H * ws
    total_w = max(cw, ww)
    cx = (total_w - cw) / 2.0
    wx = (total_w - ww) / 2.0
    wy = chh + 26
    return ('<svg viewBox="0 0 %s %s" width="%s">'
            '<g transform="translate(%s,0)">%s</g>'
            '<g transform="translate(%s,%s) scale(%s)">%s</g></svg>'
            % (round(total_w, 1), round(wy + wh, 1), w, round(cx, 1), ch,
               round(wx, 1), round(wy, 1), ws,
               wordmark_g(c1, c2, ink, ring, face, dot)))


def icon(px, bg, body=PINK, tongue=CYAN, iris=OFFW, mode='fit'):
    """a wide animal in a square tile: fit it, turn it onto the diagonal, or crop to the head"""
    if mode == 'fit':
        inner = '<svg viewBox="30 18 440 220" width="%s">%s</svg>' % (int(px * .88),
                                                                     cham_g(body, tongue, iris))
    elif mode == 'turn':
        inner = ('<svg viewBox="0 0 300 300" width="%s">'
                 '<g transform="translate(150,150) rotate(-22) scale(.61) translate(-250,-127)">'
                 '%s</g></svg>' % (int(px * .94), cham_g(body, tongue, iris)))
    else:  # head
        inner = '<svg viewBox="196 22 228 164" width="%s">%s</svg>' % (int(px * .9),
                                                                      cham_g(body, tongue, iris))
    return ('<div style="width:%spx;height:%spx;border-radius:%spx;background:%s;'
            'display:grid;place-items:center;overflow:hidden;'
            'border:1px solid rgba(128,128,140,.25)">%s</div>'
            % (px, px, int(px * 0.23), bg, inner))


H = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — icon and open screen</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
  :root{color-scheme:dark}
  html,body{background:#060609;margin:0}
  body{font-family:"Instrument Sans",sans-serif;color:#FBFAFF;padding:30px 36px;width:1160px}
  h1{font-family:"Archivo";font-weight:800;letter-spacing:-.03em;font-size:28px;margin:0 0 4px}
  h2{font-family:"Archivo";font-weight:700;font-size:17px;margin:32px 0 6px}
  .sub{color:#9C98AE;font-size:12.5px;line-height:1.55;max-width:94ch;margin:0 0 20px}
  .lab{font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
       text-transform:uppercase;color:#6C6880}
  .cell{background:#0D0D12;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:18px;
        display:flex;flex-direction:column;gap:10px;margin-bottom:16px}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.12)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.45}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:16px}
  .row{display:flex;gap:16px;margin-bottom:16px;align-items:stretch}
  .phone{width:300px;height:620px;border-radius:40px;background:#060609;
         border:1px solid rgba(255,255,255,.14);display:grid;place-items:center}
  .phone.lt{background:#F4F2F8;border-color:rgba(0,0,0,.14)}
</style></head><body>
<h1>SH:FFL &middot; the icon and the open screen</h1>
<p class="sub"><b>The animal is the icon; the full lockup is the first thing inside.</b> The
chameleon keeps its own tongue — the night skeleton, rising with the stops growing as the crowd
does — and the name is written separately with <b>the card mark standing in for the colon</b>,
at the optical gap of 10 we tightened to earlier. Two marks, one sentence: the animal that changes,
and the night it is being built into.</p>
"""]

H.append('<h2>The open screen &mdash; horizontal lockup</h2>')
H.append('<div class="cell"><div class="lab">PRIMARY &middot; PINK AND CYAN THROUGHOUT</div>'
         '<div class="art" style="min-height:220px">%s</div>'
         '<div class="note">One palette across both halves: the chameleon’s pink is the left '
         'card, its cyan night is the right card. <b>The two marks read as one object because the '
         'colour runs straight through them</b> — the tongue and the cards are the same two '
         'hues doing the same job at different scales.</div></div>' % lockup_h(900))

H.append('<div class="cell"><div class="lab">ALTERNATIVE &middot; CARDS BOTH PINK, CROWD CYAN</div>'
         '<div class="art" style="min-height:220px">%s</div>'
         '<div class="note">The structural fix applied to the cards only: <b>one hue on both cards, '
         'cyan kept for the crowd</b>. Removes the two-parties-meeting read from the card mark while '
         'keeping the chameleon exactly as locked. <b>This is the version I would take forward</b> '
         '— it answers the dating-app problem without splitting the palette in two.</div></div>'
         % lockup_h(900, c1=PINK, c2=PINK, ring=OFFW, face=INK2, dot=CYAN))

H.append('<div class="cell"><div class="lab">ARCHIVO 800 INSTEAD OF BEBAS</div>'
         '<div class="art" style="min-height:220px">%s</div>'
         '<div class="note">The same lockup with the display face swapped. <b>Archivo is wider and '
         'heavier, so the name holds more of the composition</b> and the chameleon stops being the '
         'loudest thing. Bebas keeps the animal first, which is probably right for an open '
         'screen.</div></div>'
         % lockup_h(900, c1=PINK, c2=PINK, ring=OFFW, face=INK2, dot=CYAN,
                    font='Archivo', size=70, ls='0', x_ffl=324, wm_w=455.0))

H.append('<h2>On the phone</h2><div class="row">')
H.append('<div class="cell" style="flex:0 0 auto"><div class="lab">OPEN SCREEN &middot; DARK</div>'
         '<div class="phone">%s</div></div>'
         % splash(230, c1=PINK, c2=PINK, ring=OFFW, face=INK2, dot=CYAN))
H.append('<div class="cell lite" style="flex:0 0 auto"><div class="lab">OPEN SCREEN &middot; LIGHT'
         '</div><div class="phone lt">%s</div></div>'
         % splash(230, tongue=TEAL, c1=PINK, c2=PINK, ink=DEEP, ring=LITE, face=DEEP, dot=OFFW))
H.append('<div class="cell" style="flex:1 1 0"><div class="lab">STACKED, LARGE</div>'
         '<div class="art" style="min-height:420px">%s</div>'
         '<div class="note">Stacked is the orientation an open screen actually needs — a phone '
         'is portrait and the horizontal lockup would have to shrink to about a third of the screen '
         'width to fit. <b>On light the night goes to teal and the disc inverts</b>, which are the '
         'two changes already recorded for the chameleon.</div></div>'
         % splash(400, c1=PINK, c2=PINK, ring=OFFW, face=INK2, dot=CYAN))
H.append('</div>')

H.append('<h2>The icon it opens from</h2>'
         '<p class="sub"><b>A wide animal in a square tile is the real tension here.</b> Fitted, it '
         'uses about 40 per cent of the height and the tile looks half empty. Two ways out: turn it '
         'onto the diagonal, or crop to the head.</p>')
for lab, mode, note in [
 ("A · FITTED", 'fit',
  "The whole animal, scaled to the width. <b>Correct and weak</b> — all three chameleon cues "
  "are present but the thing is tiny, and at 60px it is a pink smear."),
 ("B · TURNED ONTO THE DIAGONAL", 'turn',
  "<b>Rotated 22 degrees so the animal runs corner to corner.</b> A square’s diagonal is 40 "
  "per cent longer than its side, so this buys real size for free and keeps the curl, the casque "
  "and the eye all in frame. <b>This is the one I would ship.</b>"),
 ("C · CROPPED TO THE HEAD", 'head',
  "Casque, turret eye, open mouth, tongue leaving frame. <b>Biggest and boldest, and it holds at "
  "32px</b> — but it drops the tail curl, which was one of the three cues that stop this "
  "reading as a fish."),
]:
    row = ''
    for px, bg in ((112, INK2), (76, INK2), (48, INK2), (112, PINK), (76, LITE)):
        b = '#12000A' if bg == PINK else (DEEP if bg == LITE else PINK)
        t = OFFW if bg == PINK else (TEAL if bg == LITE else CYAN)
        ir = PINK if bg in (PINK, LITE) else OFFW
        row += icon(px, bg, b, t, ir, mode)
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="gap:16px;display:flex;align-items:center;min-height:130px">'
             '%s</div><div class="note">%s</div></div>' % (lab, row, note))

H.append('<h2>The open question</h2>'
         '<p class="sub"><b>This settles the card mark’s palette by implication.</b> If the '
         'chameleon is locked on pink and cyan and the two marks appear together on the open screen, '
         'the cards cannot be marigold or purple without the screen carrying two unrelated palettes. '
         '<b>So the marigold, vermilion, neon and purple explorations are now either dead or they '
         'belong to a campaign layer that never sits beside the chameleon.</b> Worth deciding which, '
         'because it is the difference between one brand and two.</p>')

H.append('</body></html>')
io.open(os.path.join(D, 'logos17.html'), 'w', encoding='utf-8').write('\n'.join(H))
print('written')
