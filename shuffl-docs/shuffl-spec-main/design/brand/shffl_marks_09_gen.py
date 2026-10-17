# -*- coding: utf-8 -*-
"""Evenly distributed circles at higher counts, then colour combinations across the whole mark."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos10.html')

PINK, CYAN, GOLD = '#FF2E7A', '#24E0FF', '#FFC247'
INK, LITE, WHITE = '#060609', '#F4F2F8', '#FFFFFF'
INK2, OFFW, DEEP = '#121218', '#FBFAFF', '#1A1A22'


def ring(n, R, start=-90):
    return [(round(R * math.cos(math.radians(start + i * 360.0 / n)), 2),
             round(R * math.sin(math.radians(start + i * 360.0 / n)), 2)) for i in range(n)]


CROWDS = {
 'c6':  ("WHERE WE GOT TO · 6", 4.3,
         [(-15,-5),(-3,-8),(9,-5),(-9,5),(4,6),(15,4)],
         "Last round — even size, loose placement."),
 'c7':  ("A · SEVEN · HEX", 6.0, [(0, 0)] + ring(6, 17),
         "One in the middle, six around it. <b>The only arrangement here that is perfectly even</b> "
         "— every circle sits exactly the same distance from every neighbour. No other count can."),
 'c8':  ("B · EIGHT · OPEN CENTRE", 5.4, ring(8, 18),
         "Eight on the edge, nothing in the middle. <b>This is the app's own room screen</b> "
         "— members ringing the blend. The hole in the centre is the price."),
 'c9':  ("C · NINE", 5.2, [(0, 0)] + ring(8, 17.5),
         "Eight plus a centre. <b>The middle one sits further from the ring than the ring sits from "
         "itself</b> — a small unevenness, but visible once you look for it."),
 'c10': ("D · TEN", 5.0, [(0, 0)] + ring(9, 18),
         "Nine plus a centre. <b>The densest version that still reads as separate people</b> "
         "rather than as texture."),
 'c10r':("E · TEN · ROWS 3/4/3", 4.6,
         [(-11,-13),(0,-13),(11,-13),(-16.5,0),(-5.5,0),(5.5,0),(16.5,0),(-11,13),(0,13),(11,13)],
         "The same ten in rows instead of rings. Evenly spaced, but <b>it fills a hexagon inside a "
         "circle</b>, so the corners of the disc stay empty."),
 'c12': ("F · TWELVE · TWO RINGS", 4.4, ring(3, 8.5, -90) + ring(9, 19, -70),
         "Three inside nine. <b>Twelve is where it stops being people and starts being pattern</b> "
         "— here to mark the ceiling, not to use."),
}
ORDER = ['c6', 'c7', 'c8', 'c9', 'c10', 'c10r', 'c12']


def disc(key, ring_c=INK, face=OFFW, dot=INK, r=40, ri=31):
    rd, pts = CROWDS[key][1], CROWDS[key][2]
    d = ''.join('<circle cx="%s" cy="%s" r="%s"/>' % (x, y, rd) for x, y in pts)
    return ('<circle r="%s" fill="%s"/><circle r="%s" fill="%s"/><g fill="%s">%s</g>'
            % (r, ring_c, ri, face, dot, d))


def mark(key, c1, t1, c2, t2, ring_c, face, dot, w=290):
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
            % (w, c1, c2, c1, t1, c2, t2, disc(key, ring_c, face, dot)))


# label, card1, text1, card2, text2, ring, face, dot, ground, note
# `ring` is the band behind the disc; set it to the ground to make it invisible, or to a
# contrasting value to give the disc a visible edge.
WAYS = [
 ("01 · THE ONE WE HAVE", PINK, WHITE, CYAN, WHITE, INK, OFFW, INK, 'd',
  "Pink and cyan cards, white type, white disc, ink crowd. <b>Four hues and three values</b> "
  "— the busiest version, and the one everything else gets measured against."),
 ("02 · DARK DISC, PINK CROWD", PINK, WHITE, CYAN, WHITE, INK, INK2, PINK, 'd',
  "<b>The disc stops competing.</b> It goes near-black and the crowd carries the pink, so the cards "
  "stay the brightest things in the mark — which is correct, because the cards are what move."),
 ("03 · DARK DISC, WHITE CROWD", PINK, WHITE, CYAN, WHITE, INK, INK2, OFFW, 'd',
  "Same idea, white crowd. <b>Quieter than 02 and the most legible of all ten at small sizes</b>, "
  "because white on near-black is the highest-contrast pair in the palette."),
 ("04 · ONE COLOUR, TWO CARDS", PINK, WHITE, PINK, WHITE, INK, INK2, CYAN, 'd',
  "Both cards pink, cyan only inside the disc. <b>Prints in two inks</b>, and makes pink "
  "unambiguously the brand colour rather than half of a pair."),
 ("05 · INK CARDS, COLOURED TYPE", DEEP, PINK, DEEP, CYAN, DEEP, OFFW, DEEP, 'l',
  "Cards go black, the colour moves into the letters. <b>The most restrained version, and the only "
  "one where SH and FFL are themselves the pink and the cyan.</b> Shown on light because black cards "
  "need a light ground."),
 ("06 · PINK DISC", DEEP, WHITE, DEEP, WHITE, LITE, PINK, '#12000A', 'l',
  "Inverted: black cards, pink disc. <b>The room becomes the loudest thing</b>, which reads as a "
  "venue mark rather than an app mark — the wrong story for what this is."),
 ("07 · CROSS-COLOURED TYPE", PINK, CYAN, CYAN, PINK, INK, INK2, OFFW, 'd',
  "Each card carries the other card's colour in its letters. <b>Ties the two halves together</b>, "
  "but cyan on pink is the weakest contrast pair available and it shows."),
 ("08 · PINK AND WHITE", PINK, WHITE, OFFW, PINK, INK, INK2, PINK, 'd',
  "One pink card, one white. <b>Drops cyan entirely</b> — worth seeing, because cyan is the "
  "colour that collapses on a light ground and this version never has to care."),
 ("09 · GOLD CROWD", PINK, WHITE, CYAN, WHITE, INK, INK2, GOLD, 'd',
  "<b>Gold is artwork-only in the system</b> — it means the promoted night and nothing else. "
  "Using it here spends that meaning on the logo. Here so the answer is a decision, not an oversight."),
 ("10 · MONO, FOR ONE INK", OFFW, DEEP, OFFW, DEEP, INK, INK2, OFFW, 'd',
  "No brand colour at all. <b>Every logo needs this version</b> — embroidery, a stamp, a "
  "newspaper, a sponsor wall, anywhere someone else controls the printing."),
]

LIGHT = [
 ("01 ON LIGHT", PINK, WHITE, CYAN, WHITE, DEEP, OFFW, DEEP,
  "<b>Cyan all but disappears on paper-white</b> — the known failure of the palette, and the "
  "reason the light ground gets checked separately every time. The disc needs a dark edge here or "
  "it dissolves into the page."),
 ("03 ON LIGHT", PINK, WHITE, CYAN, WHITE, LITE, DEEP, OFFW,
  "A dark disc needs no edge on light, so this one survives the flip untouched. <b>03 is the only "
  "combination that is identical on both grounds.</b>"),
 ("04 ON LIGHT", PINK, WHITE, PINK, WHITE, LITE, DEEP, CYAN,
  "Two pink cards invert cleanly, and the cyan sits inside the disc where its weakness on light "
  "never gets tested."),
 ("10 ON LIGHT", DEEP, OFFW, DEEP, OFFW, LITE, DEEP, OFFW,
  "The single-ink version, inverted. <b>This has to work before any of the others count as "
  "finished</b> — it is the one that ends up on a rubber stamp."),
]


H = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — count and colour</title>
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
  .cell.old{opacity:.5}
  .cell.pick{border-color:rgba(255,46,122,.5)}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.12)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.42}
  .g4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}
  .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:16px}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-bottom:16px}
  .row{display:flex;gap:14px;margin-bottom:16px}
</style></head><body>
<h1>SH:FFL &middot; the crowd counted, and the colour</h1>
<p class="sub"><b>Every circle inside any one disc is the same radius</b> &mdash; that is fixed and
stays fixed. The radius does fall as the count rises (6.0 at seven down to 4.4 at twelve), because
more circles in the same disc either get smaller or get closer, and <b>holding the gap constant near
4 units is what keeps it reading as people rather than as perforation</b>.</p>

<h2>Seven counts, evenly distributed</h2><div class="g4">"""]

for k in ORDER:
    lab, rd, pts, note = CROWDS[k]
    cls = ' old' if k == 'c6' else (' pick' if k == 'c7' else '')
    H.append('<div class="cell%s"><div class="lab">%s</div>'
             '<div class="art" style="min-height:118px">'
             '<svg viewBox="-44 -44 88 88" width="118">%s</svg></div>'
             '<div class="note">%s</div></div>' % (cls, lab, disc(k), note))
H.append('</div>')

H.append('<h2>At icon size &mdash; 72px and 32px</h2><div class="row">')
for k in ['c7', 'c8', 'c9', 'c10', 'c12']:
    short = CROWDS[k][0].split('·', 1)[1].strip()
    H.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="gap:10px;display:flex;align-items:center">'
             '<div style="width:72px;height:72px;border-radius:16px;background:#F4F2F8;'
             'display:grid;place-items:center">'
             '<svg viewBox="-44 -44 88 88" width="54">%s</svg></div>'
             '<div style="width:32px;height:32px;border-radius:8px;background:#F4F2F8;'
             'display:grid;place-items:center">'
             '<svg viewBox="-44 -44 88 88" width="26">%s</svg></div></div></div>'
             % (short, disc(k, LITE, INK, OFFW), disc(k, LITE, INK, OFFW)))
H.append('</div>')
H.append('<p class="sub"><b>At 32px the gaps close before the circles do.</b> Seven still reads as '
         'seven; by ten the ring has fused into a dotted band, and twelve is a ring of noise. '
         '<b>Seven is the highest count that survives the smallest size you actually ship</b> '
         '— the favicon and the notification badge.</p>')

H.append('<h2>Ten colour combinations &mdash; cards, letters, disc, crowd</h2>'
         '<p class="sub">All on the even seven. <b>Each one moves four things at once</b>, because '
         'they are not independent: a dark disc only works while the cards stay bright, and coloured '
         'letters only work once the cards go quiet. <b>Cells on white are the combinations that need '
         'a light ground</b> — black cards are invisible on black.</p><div class="g3">')
for lab, c1, t1, c2, t2, rc, face, dot, g, note in WAYS:
    H.append('<div class="cell%s"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div>'
             '<div class="note">%s</div></div>'
             % (' lite' if g == 'l' else '', lab, mark('c7', c1, t1, c2, t2, rc, face, dot), note))
H.append('</div>')

H.append('<h2>Four of them on the light ground</h2><div class="g2">')
for lab, c1, t1, c2, t2, rc, face, dot, note in LIGHT:
    H.append('<div class="cell lite"><div class="lab">%s</div>'
             '<div class="art" style="min-height:160px">\n%s</div>'
             '<div class="note">%s</div></div>'
             % (lab, mark('c7', c1, t1, c2, t2, rc, face, dot, 300), note))
H.append('</div>')

H.append('</body></html>')
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(H))
print('written')
