# -*- coding: utf-8 -*-
"""People instead of holes. Uniform size, placement only. Plus a colour matrix."""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos9.html')


# ---------------------------------------------------------------- the glyphs
def person(x, y, s=1.0, lean=0):
    """head and shoulders - the one shape nobody mistakes for a hole"""
    return ('<g transform="translate(%s,%s) rotate(%s) scale(%s)">'
            '<circle cx="0" cy="-4.4" r="3.3"/>'
            '<path d="M-4.6 5.4 A4.6 5.6 0 0 1 4.6 5.4 Z"/></g>' % (x, y, lean, s))


def head(x, y, s=1.0, lean=0):
    """head only, uniform radius"""
    return '<circle cx="%s" cy="%s" r="%s"/>' % (x, y, 4.3 * s)


def capsule(x, y, s=1.0, lean=0):
    """an upright pill - a figure with no features at all"""
    return ('<g transform="translate(%s,%s) rotate(%s)">'
            '<rect x="-3.1" y="-6.6" width="6.2" height="13.2" rx="3.1" transform="scale(%s)"/></g>'
            % (x, y, lean, s))


def wide(x, y, s=1.0, lean=0):
    """head on a wider shoulder - heavier, holds at small sizes"""
    return ('<g transform="translate(%s,%s) rotate(%s) scale(%s)">'
            '<circle cx="0" cy="-5" r="3.6"/>'
            '<path d="M-5.8 6 A5.8 6.4 0 0 1 5.8 6 Z"/></g>' % (x, y, lean, s))


# back row higher, front row lower - a crowd seen from the front
CROWDS = {
 'five': ("A · FIVE, TWO ROWS", person,
          [(-15,-6,1,-4),(-2,-7,1,2),(11,-5,1,5),(-8,7,1,-2),(6,8,1,3)],
          "<b>Head and shoulders, all the same size</b>, two rows with the front row lower. "
          "Overlap is doing the work that size variation used to — and overlap cannot trigger "
          "the pattern, because the forms are joined rather than isolated."),
 'seven': ("B · SEVEN, THREE ROWS", person,
           [(-16,-10,1,-5),(-5,-11,1,1),(7,-10,1,4),(-11,-1,1,-2),(2,0,1,3),(14,-1,1,-4),(-3,10,1,1)],
           "Denser. <b>Reads as a room rather than a group</b>, and the back row being partly "
           "hidden is what makes it feel like there are more than seven."),
 'heads': ("C · HEADS ONLY, EVEN SIZE", head,
           [(-15,-5,1,0),(-3,-8,1,0),(9,-5,1,0),(-9,5,1,0),(4,6,1,0),(15,4,1,0)],
           "Circles again, but <b>every one the same radius</b> — which is the specific thing "
           "that was wrong before. Simplest to render, and still the most hole-like of the four."),
 'capsule': ("D · CAPSULES", capsule,
             [(-14,-3,1,-6),(-4,-5,1,2),(6,-3,1,6),(-9,8,1,-3),(3,9,1,4),(14,5,1,-5)],
             "Featureless uprights. <b>Abstract enough to be anything, and the lean makes them "
             "people</b> — a row of straight capsules would read as a barcode."),
 'wideone': ("E · HEAVIER FIGURES", wide,
             [(-14,-4,1,-4),(-1,-6,1,2),(12,-3,1,5),(-7,8,1,-2),(7,9,1,3)],
             "Same arrangement, broader shoulders and a bigger head. <b>Built for the icon</b> "
             "— thin figures close up at 32px, these do not."),
}
ORDER = ['five', 'seven', 'heads', 'capsule', 'wideone']


def crowd(key, fill, scale=1.0):
    _, fn, pts, _ = CROWDS[key]
    return ('<g fill="%s" transform="scale(%s)">' % (fill, scale)
            + ''.join(fn(*p) for p in pts) + '</g>')


# ---------------------------------------------------------------- colourways
WAYS = [
 ("1 · INK ON WHITE", '#060609', '#FBFAFF', '#060609', False),
 ("2 · WHITE ON INK", '#060609', '#121218', '#FBFAFF', False),
 ("3 · INK ON PINK", '#060609', '#FF2E7A', '#12000A', False),
 ("4 · PINK ON WHITE", '#060609', '#FBFAFF', '#FF2E7A', False),
 ("5 · PINK ON INK", '#060609', '#121218', '#FF2E7A', False),
 ("6 · WHITE ON PINK", '#060609', '#FF2E7A', '#FFFFFF', False),
]


def disc(key, ring, face, figs, r=40, ri=31, sc=1.0):
    return ('<circle r="%s" fill="%s"/><circle r="%s" fill="%s"/>%s'
            % (r, ring, ri, face, crowd(key, figs, sc)))


# ---------------------------------------------------------------- B, Archivo white
def mark_b(key, ring, face, figs, light=False):
    cy = '#1A1A22' if light else '#24E0FF'
    lt = '#FFFFFF'
    return ('      <svg viewBox="0 0 370 200" width="330">\n'
            '        <g stroke="#FF2E7A" stroke-linecap="round">'
            '<line x1="128" y1="66" x2="146" y2="62" stroke-width="5.5"/>'
            '<line x1="126" y1="96" x2="150" y2="94" stroke-width="5.5"/>'
            '<line x1="130" y1="126" x2="144" y2="124" stroke-width="5.5"/></g>\n'
            '        <g stroke="%s" stroke-linecap="round">'
            '<line x1="242" y1="66" x2="224" y2="62" stroke-width="5.5"/>'
            '<line x1="244" y1="96" x2="220" y2="94" stroke-width="5.5"/>'
            '<line x1="240" y1="126" x2="226" y2="124" stroke-width="5.5"/></g>\n'
            '        <g transform="translate(16,46) rotate(-20)">'
            '<rect width="84" height="104" rx="12" fill="#FF2E7A"/>'
            '<text x="42" y="62" text-anchor="middle" style="font-family:Archivo;font-weight:800" '
            'font-size="34" fill="%s">SH</text></g>\n'
            '        <g transform="translate(354,46) rotate(20) translate(-84,0)">'
            '<rect width="84" height="104" rx="12" fill="%s"/>'
            '<text x="42" y="62" text-anchor="middle" style="font-family:Archivo;font-weight:800" '
            'font-size="34" fill="%s">FFL</text></g>\n'
            '        <g transform="translate(185,98)">%s</g>\n      </svg>\n'
            % (cy, lt, cy, lt, disc(key, ring, face, figs)))


H = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — people, not holes</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
  :root{color-scheme:dark}
  html,body{background:#060609;margin:0}
  body{font-family:"Instrument Sans",sans-serif;color:#FBFAFF;padding:30px 36px;width:1120px}
  h1{font-family:"Archivo";font-weight:800;letter-spacing:-.03em;font-size:28px;margin:0 0 4px}
  h2{font-family:"Archivo";font-weight:700;font-size:17px;margin:30px 0 6px}
  .sub{color:#9C98AE;font-size:12.5px;line-height:1.55;max-width:94ch;margin:0 0 20px}
  .lab{font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
       text-transform:uppercase;color:#6C6880}
  .cell{background:#0D0D12;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:16px;
        display:flex;flex-direction:column;gap:9px}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.1)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.42}
  .g5{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:16px}
  .g6{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-bottom:16px}
  .row{display:flex;gap:16px;margin-bottom:16px}
</style></head><body>
<h1>SH:FFL &middot; people, not holes</h1>
<p class="sub"><b>The size variation was the mistake.</b> Irregularly-sized round holes clustered on a
surface is the pattern that triggers trypophobia, and I introduced it by varying the radii.
<b>Everything below uses one size and varies only placement and lean</b>, and four of the five stop
being circles altogether. <b>Overlap now does the job size variation was doing</b> — and overlapping
forms cannot read as holes, because a hole does not cover another hole. Type is <b>Archivo 800 white</b>
throughout.</p>

<h2>Five crowds &mdash; one size, placement only</h2><div class="g5">"""]

for k in ORDER:
    lab, fn, pts, note = CROWDS[k]
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="min-height:110px">'
             '<svg viewBox="-44 -44 88 88" width="112">%s</svg></div>'
             '<div class="note">%s</div></div>'
             % (lab, disc(k, '#060609', '#FBFAFF', '#060609'), note))
H.append('</div>')

H.append('<h2>Six colourways, on A</h2><div class="g6">')
for lab, ring, face, figs, _ in WAYS:
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="min-height:96px">'
             '<svg viewBox="-44 -44 88 88" width="94">%s</svg></div></div>'
             % (lab, disc('five', ring, face, figs)))
H.append('</div>')
H.append('<p class="sub"><b>3 and 6 make the circle the loudest thing in the mark</b>, which fights '
         'the cards — the crowd is meant to be the still point. <b>1 is the safest and 5 is the '
         'most distinctive</b>: a dark face with pink figures keeps the circle quiet while still '
         'carrying the brand colour, and it is the only one of the six that needs no white at all.</p>')

H.append('<h2>In the mark &mdash; Archivo 800 white</h2>')
for k, lab in (('five', 'A &middot; FIVE'), ('wideone', 'E &middot; HEAVIER'),
               ('capsule', 'D &middot; CAPSULES')):
    H.append('<div class="cell" style="margin-bottom:16px"><div class="lab">%s &middot; INK ON WHITE</div>'
             '<div class="art" style="min-height:190px">\n%s</div></div>'
             % (lab, mark_b(k, '#060609', '#FBFAFF', '#060609')))
H.append('<div class="cell" style="margin-bottom:16px"><div class="lab">A &middot; PINK ON INK '
         '(COLOURWAY 5)</div><div class="art" style="min-height:190px">\n%s</div>'
         '<div class="note">The circle goes quiet and the figures carry the colour. '
         '<b>No white anywhere in the mark</b>, which makes it one fewer thing to manage across '
         'backgrounds.</div></div>' % mark_b('five', '#060609', '#121218', '#FF2E7A'))

H.append('<h2>At icon size</h2><div class="row">')
for k, lab in (('five', 'A &middot; FIVE'), ('wideone', 'E &middot; HEAVIER'),
               ('heads', 'C &middot; HEADS'), ('capsule', 'D &middot; CAPSULES')):
    H.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="gap:12px;display:flex">'
             '<div style="width:72px;height:72px;border-radius:16px;background:#0D0D12;'
             'border:1px solid rgba(255,255,255,.12);display:grid;place-items:center">'
             '<svg viewBox="-44 -44 88 88" width="52">%s</svg></div>'
             '<div style="width:44px;height:44px;border-radius:10px;background:#0D0D12;'
             'border:1px solid rgba(255,255,255,.12);display:grid;place-items:center">'
             '<svg viewBox="-44 -44 88 88" width="32">%s</svg></div></div></div>'
             % (lab, disc(k, '#060609', '#FBFAFF', '#060609'), disc(k, '#060609', '#FBFAFF', '#060609')))
H.append('</div>')
H.append('<p class="sub"><b>At 32px the shoulders close up on A and the figures merge into a mass.</b> '
         'E holds because the forms are fatter; C holds because circles always do. <b>If one crowd has '
         'to serve every size, it is E</b> — if two are allowed, A large and C small.</p>')

H.append('</body></html>')
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(H))
print('written')
