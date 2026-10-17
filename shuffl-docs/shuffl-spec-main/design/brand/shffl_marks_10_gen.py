# -*- coding: utf-8 -*-
"""Crowd B (eight, open centre) across the three surviving colourways, and the crossed lines."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos11.html')

PINK, CYAN = '#FF2E7A', '#24E0FF'
INK, LITE, WHITE = '#060609', '#F4F2F8', '#FFFFFF'
INK2, OFFW, DEEP = '#121218', '#FBFAFF', '#1A1A22'


def ring(n, R, start=-90):
    return [(round(R * math.cos(math.radians(start + i * 360.0 / n)), 2),
             round(R * math.sin(math.radians(start + i * 360.0 / n)), 2)) for i in range(n)]


# B - eight, open centre
B8 = ring(8, 18)
RD = 5.4


def disc(ring_c=INK, face=OFFW, dot=INK, r=40, ri=31):
    d = ''.join('<circle cx="%s" cy="%s" r="%s"/>' % (x, y, RD) for x, y in B8)
    return ('<circle r="%s" fill="%s"/><circle r="%s" fill="%s"/><g fill="%s">%s</g>'
            % (r, ring_c, ri, face, dot, d))


def mark(c1, t1, c2, t2, ring_c, face, dot, l1=None, l2=None, w=290):
    """c1/t1 left card and letters, c2/t2 right. l1/l2 are the speed lines either side;
    default to the card colour, pass them explicitly to cross."""
    l1 = l1 or c1
    l2 = l2 or c2
    return ('      <svg viewBox="0 0 370 200" width="%s">\n'
            '        <g stroke="%s" stroke-linecap="round">'
            '<line x1="128" y1="66" x2="146" y2="62" stroke-width="5.5"/>'
            '<line x1="126" y1="96" x2="150" y2="94" stroke-width="5.5"/>'
            '<line x1="130" y1="126" x2="144" y2="124" stroke-width="5.5"/></g>\n'
            '        <g stroke="%s" stroke-linecap="round">'
            '<line x1="242" y1="66" x2="224" y2="62" stroke-width="5.5"/>'
            '<line x1="244" y1="96" x2="220" y2="94" stroke-width="5.5"/>'
            '<line x1="240" y1="126" x2="226" y2="124" stroke-width="5.5"/></g>\n'
            '        <g transform="translate(16,46) rotate(-20)">'
            '<rect width="84" height="104" rx="12" fill="%s"/>'
            '<text x="42" y="62" text-anchor="middle" style="font-family:Archivo;font-weight:800" '
            'font-size="34" fill="%s">SH</text></g>\n'
            '        <g transform="translate(354,46) rotate(20) translate(-84,0)">'
            '<rect width="84" height="104" rx="12" fill="%s"/>'
            '<text x="42" y="62" text-anchor="middle" style="font-family:Archivo;font-weight:800" '
            'font-size="34" fill="%s">FFL</text></g>\n'
            '        <g transform="translate(185,98)">%s</g>\n      </svg>\n'
            % (w, l1, l2, c1, t1, c2, t2, disc(ring_c, face, dot)))


H = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — eight, and the crossed lines</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
  :root{color-scheme:dark}
  html,body{background:#060609;margin:0}
  body{font-family:"Instrument Sans",sans-serif;color:#FBFAFF;padding:30px 36px;width:1160px}
  h1{font-family:"Archivo";font-weight:800;letter-spacing:-.03em;font-size:28px;margin:0 0 4px}
  h2{font-family:"Archivo";font-weight:700;font-size:17px;margin:32px 0 6px}
  .sub{color:#9C98AE;font-size:12.5px;line-height:1.55;max-width:94ch;margin:0 0 20px}
  .lab{font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
       text-transform:uppercase;color:#6C6880}
  .cell{background:#0D0D12;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:16px;
        display:flex;flex-direction:column;gap:9px}
  .cell.pick{border-color:rgba(255,46,122,.5)}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.12)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.42}
  .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:16px}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-bottom:16px}
  .row{display:flex;gap:14px;margin-bottom:16px}
</style></head><body>
<h1>SH:FFL &middot; eight with an open centre, and the crossed lines</h1>
<p class="sub"><b>Crowd B throughout</b> &mdash; eight circles, all one radius, evenly spaced on the
edge with nothing in the middle. It is the arrangement the app already draws on its own room screen,
members ringing the blend, so <b>the logo and the product now make the same shape</b>.</p>

<h2>01, 03 and 10, on the eight</h2><div class="g3">"""]

THREE = [
 ("01 · WHITE DISC", PINK, WHITE, CYAN, WHITE, INK, OFFW, INK, None, None,
  "White disc, ink crowd. <b>The open centre helps this one most</b> — the old solid middle "
  "made the disc read as a filled ball, and the hole is what turns it into a room seen from above."),
 ("03 · DARK DISC, WHITE CROWD", PINK, WHITE, CYAN, WHITE, INK, INK2, OFFW, None, None,
  "Dark disc, white crowd. <b>Still the only combination that is identical on both grounds</b>, "
  "and still the most legible at badge size."),
 ("10 · WHITE CARDS, CROSSED", OFFW, PINK, OFFW, CYAN, INK, INK2, OFFW, CYAN, PINK,
  "<b>The new one.</b> Cards go white, SH is pink and FFL is cyan, and each set of lines takes the "
  "other card's colour — cyan beside the pink letters, pink beside the cyan."),
]
for lab, c1, t1, c2, t2, rc, fc, dc, l1, l2, note in THREE:
    H.append('<div class="cell%s"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (' pick' if lab.startswith('10') else '', lab,
                mark(c1, t1, c2, t2, rc, fc, dc, l1, l2), note))
H.append('</div>')

H.append('<h2>Working out the crossed lines on 10</h2>'
         '<p class="sub">The crossing is worth testing against its alternatives, because <b>the lines '
         'are the only part of the mark that carries motion</b> and whichever colour they take is the '
         'colour the eye reads as moving.</p><div class="g3">')

TEN = [
 ("10a · CROSSED · SH PINK", OFFW, PINK, OFFW, CYAN, INK2, OFFW, CYAN, PINK,
  "<b>As asked.</b> Pink letters with cyan lines, cyan letters with pink lines. The crossing makes "
  "each card look like it is moving <i>into</i> the other one's colour, which is the right story for "
  "two cards swiping apart around a shared room."),
 ("10b · MATCHED · FOR COMPARISON", OFFW, PINK, OFFW, CYAN, INK2, OFFW, PINK, CYAN,
  "Lines matching their own card. <b>Reads as two separate objects</b> rather than one event — "
  "which is exactly what the crossing fixes. Here only to show the difference."),
 ("10c · CROSSED · SH CYAN", OFFW, CYAN, OFFW, PINK, INK2, OFFW, PINK, CYAN,
  "The same crossing with the two letter colours swapped. <b>Pink on the right is heavier</b>, and "
  "since FFL is the longer word it makes the mark lean right. 10a is better balanced."),
 ("10d · CROSSED · WHITE DISC", OFFW, PINK, OFFW, CYAN, OFFW, INK, CYAN, PINK,
  "Same crossing, white disc with an ink crowd. <b>Three white shapes in a row</b> — the disc "
  "stops being distinct from the cards and the mark flattens."),
 ("10e · CROSSED · ON PINK CARDS", PINK, WHITE, CYAN, WHITE, INK2, OFFW, CYAN, PINK,
  "The crossing applied to 01's colours instead. <b>It barely registers</b>, because a cyan line "
  "beside a pink card reads as part of the cyan card's trail. <b>The device only works when the "
  "cards are neutral.</b>"),
 ("10f · TRUE MONO · ONE INK", OFFW, DEEP, OFFW, DEEP, INK2, OFFW, OFFW, OFFW,
  "<b>Keep this one too.</b> 10 used to be the single-ink version, and adding colour to it means the "
  "system still needs a no-colour mark for embroidery, a stamp or a newspaper."),
]
for lab, c1, t1, c2, t2, fc, dc, l1, l2, note in TEN:
    H.append('<div class="cell%s"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (' pick' if lab.startswith('10a') else '', lab,
                mark(c1, t1, c2, t2, INK, fc, dc, l1, l2), note))
H.append('</div>')

H.append('<h2>On the light ground</h2><div class="g3">')
LIGHTS = [
 ("01 ON LIGHT", PINK, WHITE, CYAN, WHITE, DEEP, OFFW, DEEP, None, None,
  "<b>Cyan still collapses on paper-white.</b> The disc needs the dark ring here or it dissolves."),
 ("03 ON LIGHT", PINK, WHITE, CYAN, WHITE, LITE, DEEP, OFFW, None, None,
  "Untouched by the flip. <b>Nothing is redrawn for the inverse.</b>"),
 ("10 ON LIGHT", DEEP, PINK, DEEP, CYAN, LITE, OFFW, DEEP, CYAN, PINK,
  "<b>The cards invert to black and everything else holds</b> — the letters and the crossed "
  "lines keep their colours, because both sit on the card rather than on the page."),
]
for lab, c1, t1, c2, t2, rc, fc, dc, l1, l2, note in LIGHTS:
    H.append('<div class="cell lite"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (lab, mark(c1, t1, c2, t2, rc, fc, dc, l1, l2), note))
H.append('</div>')

H.append('<h2>The eight at icon size &mdash; 72px, 44px, 32px</h2><div class="row">')
ICONS = [
 ("ON WHITE", LITE, INK, OFFW),
 ("ON INK", INK2, INK2, OFFW),
 ("ON PINK", PINK, PINK, '#12000A'),
]
for lab, bg, fc, dc in ICONS:
    inner = ''
    for w, box in ((54, 72), (34, 44), (26, 32)):
        inner += ('<div style="width:%spx;height:%spx;border-radius:%spx;background:%s;'
                  'display:grid;place-items:center;border:1px solid rgba(128,128,140,.25)">'
                  '<svg viewBox="-44 -44 88 88" width="%s">%s</svg></div>'
                  % (box, box, box // 4, bg, w, disc(bg, fc, dc)))
    H.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="gap:10px;display:flex;align-items:center">%s</div></div>'
             % (lab, inner))
H.append('</div>')
H.append('<p class="sub"><b>The open centre is the thing that saves this at 32px.</b> A filled crowd '
         'turns into a blob when the gaps close; a ring keeps a hole in the middle that stays visible '
         'long after the individual circles have merged, so the mark still has an inside and an '
         'outside at any size.</p>')

H.append('</body></html>')
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(H))
print('written')
