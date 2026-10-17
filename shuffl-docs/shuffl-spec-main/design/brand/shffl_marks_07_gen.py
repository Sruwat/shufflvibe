# -*- coding: utf-8 -*-
"""Type treatments for the lettered cards, and alternatives to the crowd circle."""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos8.html')

# ---------------------------------------------------------------- crowd fills
# each is a list of (cx, cy, r) in a circle of radius 31 centred on 0,0
CROWDS = {
 'die': ("THE ONE WE HAVE", [(0,-13,5),(-13,3,5),(13,3,5),(0,14,5)],
         "Four dots in a symmetric diamond. <b>That is a die face, and the eye knows it</b> - which "
         "is why it reads as a ball rather than a room."),
 'scatter': ("A · SCATTER", [(-13,-11,4.2),(2,-16,3.6),(14,-7,4.6),(-18,2,3.8),(-4,0,5.0),
                             (11,6,4.0),(-9,14,4.4),(6,17,3.4)],
         "Eight, irregular, slightly different sizes. <b>Nothing lines up, which is what makes it "
         "people.</b> Regularity is the whole problem with the original."),
 'cluster': ("B · CLUSTERED", [(-15,-9,4.4),(-7,-13,3.8),(-3,-3,4.8),(-13,2,4.2),(-8,10,4.0),
                               (3,8,3.6),(12,-4,4.2),(15,13,3.2)],
         "Same count, but bunched left with space on the right. <b>Real crowds clump and leave "
         "gaps</b>; an even spread is the thing that never happens in a room."),
 'depth': ("C · NEAR AND FAR", [(-12,-9,6.8),(6,-13,4.0),(16,2,2.8),(-6,7,7.8),(9,15,4.6)],
         "Five dots with a wide size range. <b>Size reads as distance</b>, so the circle gains depth "
         "and stops being a flat pattern. Fewest parts of any option here."),
 'ring': ("D · FACING IN", [(17,0,4.6),(8.5,14.7,4.6),(-8.5,14.7,4.6),(-17,0,4.6),
                            (-8.5,-14.7,4.6),(8.5,-14.7,4.6)],
         "Six around the edge with the middle empty. <b>This is the app's own room screen</b> - "
         "members' icons ringing the blend style. The most product-true of the six, and the most "
         "regular, which is the tension."),
 'you': ("E · ONE OF THEM IS YOU", [(-13,-11,4.2),(2,-16,3.6),(14,-7,4.6),(-18,2,3.8),
                                     (11,6,4.0),(-9,14,4.4),(6,17,3.4)],
         "The scatter, with <b>one dot in the live colour</b> - you, in the room. Says what the "
         "product is in one dot, and needs two colours to say it."),
 'heads': ("F · OVERLAPPING", [(-12,-6,10.5),(2,-10,9.5),(13,2,8.5),(-5,10,10.0)],
         "Four large discs that overlap. <b>Reads as people standing close rather than dots on a "
         "plane</b>, and holds its shape when everything shrinks because the forms are big."),
}
ORDER = ['die', 'scatter', 'cluster', 'depth', 'ring', 'you', 'heads']


def dots(key, fill, hi=None):
    out = ''
    for i, (x, y, r) in enumerate(CROWDS[key][1]):
        c = hi if (hi and key == 'you' and i == 3) else fill
        out += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (x, y, r, c)
    return out


# ---------------------------------------------------------------- the lettered mark (option 1)
def lettered(font, size, col_sh, col_ffl, crowd='scatter', dy=0):
    return ('      <svg viewBox="0 0 370 200" width="330">\n'
            '        <g stroke="#FF2E7A" stroke-linecap="round">'
            '<line x1="128" y1="66" x2="146" y2="62" stroke-width="5.5"/>'
            '<line x1="126" y1="96" x2="150" y2="94" stroke-width="5.5"/>'
            '<line x1="130" y1="126" x2="144" y2="124" stroke-width="5.5"/></g>\n'
            '        <g stroke="#24E0FF" stroke-linecap="round">'
            '<line x1="242" y1="66" x2="224" y2="62" stroke-width="5.5"/>'
            '<line x1="244" y1="96" x2="220" y2="94" stroke-width="5.5"/>'
            '<line x1="240" y1="126" x2="226" y2="124" stroke-width="5.5"/></g>\n'
            '        <g transform="translate(16,46) rotate(-20)">'
            '<rect width="84" height="104" rx="12" fill="#FF2E7A"/>'
            '<text x="42" y="%d" text-anchor="middle" style="font-family:%s" font-size="%d" '
            'fill="%s">SH</text></g>\n'
            '        <g transform="translate(354,46) rotate(20) translate(-84,0)">'
            '<rect width="84" height="104" rx="12" fill="#24E0FF"/>'
            '<text x="42" y="%d" text-anchor="middle" style="font-family:%s" font-size="%d" '
            'fill="%s">FFL</text></g>\n'
            '        <circle cx="185" cy="98" r="40" fill="#060609"/>'
            '<circle cx="185" cy="98" r="31" fill="#FBFAFF"/>\n'
            '        <g transform="translate(185,98)">%s</g>\n      </svg>\n'
            % (66 + dy, font, size, col_sh, 66 + dy, font, size, col_ffl,
               dots(crowd, '#060609', '#FF2E7A')))


# ---------------------------------------------------------------- F at gap 10
def f_lockup(crowd, light=False):
    ink = '#1A1A22' if light else '#FBFAFF'
    hole = '#F4F2F8' if light else '#FBFAFF'
    back = '#F4F2F8' if light else '#060609'
    cy = '#1A1A22' if light else '#24E0FF'
    mark = ('        <g fill="#FF2E7A">'
            '<g transform="translate(24,39) rotate(-13)" opacity=".32"><rect width="47" height="68" rx="8"/></g>'
            '<g transform="translate(0,47) rotate(-26)"><rect width="47" height="68" rx="8"/></g></g>'
            '<g fill="%s">'
            '<g transform="translate(180,39) rotate(13) translate(-47,0)" opacity=".32"><rect width="47" height="68" rx="8"/></g>'
            '<g transform="translate(204,47) rotate(26) translate(-47,0)"><rect width="47" height="68" rx="8"/></g></g>'
            '<circle cx="102" cy="67" r="33" fill="%s"/><circle cx="102" cy="67" r="26" fill="%s"/>'
            '<g transform="translate(102,67) scale(.79)">%s</g>'
            % (cy, back, hole, dots(crowd, back, '#FF2E7A')))
    return ('      <svg viewBox="0 0 498 140" width="460">\n'
            '        <text x="0" y="104" style="font-family:\'Bebas Neue\';letter-spacing:.14em" '
            'font-size="102" fill="%s">SH</text>\n'
            '        <g transform="translate(110,0)">%s</g>\n'
            '        <text x="322" y="104" style="font-family:\'Bebas Neue\';letter-spacing:.14em" '
            'font-size="102" fill="%s">FFL</text>\n      </svg>\n' % (ink, mark, ink))


# ---------------------------------------------------------------- page
H = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — type and crowd</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600;700&display=swap">
<style>
  :root{color-scheme:dark}
  html,body{background:#060609;margin:0}
  body{font-family:"Instrument Sans",sans-serif;color:#FBFAFF;padding:30px 36px;width:1120px}
  h1{font-family:"Archivo";font-weight:800;letter-spacing:-.03em;font-size:28px;margin:0 0 4px}
  h2{font-family:"Archivo";font-weight:700;font-size:17px;margin:30px 0 4px}
  .sub{color:#9C98AE;font-size:12.5px;line-height:1.55;max-width:94ch;margin:0 0 20px}
  .lab{font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
       text-transform:uppercase;color:#6C6880}
  .cell{background:#0D0D12;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:18px;
        display:flex;flex-direction:column;gap:10px}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.1)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .cell.dead{border-color:rgba(255,46,122,.3)}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.45}
  .row{display:flex;gap:16px;align-items:stretch;margin-bottom:16px}
  .g4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px}
</style></head><body>
<h1>SH:FFL &middot; type treatments, and the crowd</h1>
<p class="sub"><b>All three typefaces below are already in the product</b> &mdash; Bebas Neue names
things, Archivo is the display face, IBM Plex Mono writes every door time. Nothing new is being
introduced. <b>And the crowd: four dots in a symmetric diamond is a die face</b>, which is why it
reads as a ball. Everything after it breaks the symmetry one way or another.</p>

<h2>Three type treatments on option 1</h2>
<div class="row">"""]

TYPES = [
 ("BEBAS NEUE &middot; CROSS-COLOURED", "'Bebas Neue'", 40, '#24E0FF', '#FF2E7A', -2,
  "The house display face, with <b>each card carrying the other card's colour</b>. Ties the two "
  "halves together and keeps the pink/cyan pair doing work inside the mark rather than only as "
  "card fills."),
 ("ARCHIVO 800 &middot; WHITE", "Archivo", 34, '#FFFFFF', '#FFFFFF', -4,
  "Wider, heavier, and modern. <b>White on both reads as the most confident of the three</b> and is "
  "the only one that stays legible if the cards ever go to a single colour."),
 ("IBM PLEX MONO &middot; INK", "'IBM Plex Mono'", 30, '#12000A', '#06222B', -4,
  "The face the app writes <b>21:00</b> in. <b>Mono ties the wordmark to the colon</b>, which is "
  "the one piece of the name doing conceptual work &mdash; the clock separator every stop is "
  "written with."),
]
for lab, font, size, c1, c2, dy, note in TYPES:
    H.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="min-height:190px">\n%s</div>'
             '<div class="note">%s</div></div>' % (lab, lettered(font, size, c1, c2, 'scatter', dy), note))
H.append('</div>')

H.append('<h2>Seven crowds, same circle</h2><div class="g4">')
for k in ORDER:
    lab, _, note = CROWDS[k]
    cls = ' dead' if k == 'die' else ''
    H.append('<div class="cell%s"><div class="lab">%s</div><div class="art" style="min-height:120px">'
             '<svg viewBox="-44 -44 88 88" width="118">'
             '<circle r="40" fill="#060609"/><circle r="31" fill="#FBFAFF"/>%s</svg></div>'
             '<div class="note">%s</div></div>' % (cls, lab, dots(k, '#060609', '#FF2E7A'), note))
H.append('</div>')

H.append('<h2>F at optical gap 10, with four of them</h2>')
for k in ['scatter', 'depth', 'ring', 'heads']:
    H.append('<div class="cell" style="margin-bottom:16px"><div class="lab">F &middot; %s</div>'
             '<div class="art" style="min-height:140px">\n%s</div></div>'
             % (CROWDS[k][0], f_lockup(k)))
H.append('<div class="cell lite"><div class="lab">F &middot; A &middot; SCATTER, ON LIGHT</div>'
         '<div class="art" style="min-height:140px">\n%s</div>'
         '<div class="note">An irregular scatter survives the colour inversion better than the '
         'diamond did &mdash; <b>a pattern the eye cannot name does not acquire a wrong meaning</b> '
         'when the colours flip.</div></div>' % f_lockup('scatter', light=True))

H.append('</body></html>')
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(H))
print('written', len('\n'.join(H)))
