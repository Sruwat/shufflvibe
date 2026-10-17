# -*- coding: utf-8 -*-
"""Two shades of purple, flat and neon."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

INK, LITE, WHITE = '#060609', '#F4F2F8', '#FFFFFF'
INK2, OFFW, DEEP = '#121218', '#FBFAFF', '#1A1A22'

VIO   = '#8B2BFF'   # electric violet
NEOP  = '#B14DFF'   # neon purple
ORCH  = '#C77DFF'   # orchid
LILAC = '#DCB0FF'
GRAPE = '#5B1E9E'
PLUM  = '#3F1260'
AUB   = '#260B38'   # aubergine
MAGP  = '#C026D3'   # magenta-leaning
IRIS  = '#6D28D9'   # blue-leaning
DARKT = '#2A0A44'

B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]

GLOW = ('<filter id="__ID__" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="__SD__" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/>'
        '<feMergeNode in="SourceGraphic"/></feMerge></filter>')


def disc_solid(ring_c, face, dot):
    d = ''.join('<circle cx="%s" cy="%s" r="5.4"/>' % (x, y) for x, y in B8)
    return ('<circle r="40" fill="%s"/><circle r="31" fill="%s"/><g fill="%s">%s</g>'
            % (ring_c, face, dot, d))


def disc_tube(col):
    d = ''.join('<circle cx="%s" cy="%s" r="4.4"/>' % (x, y) for x, y in B8)
    return ('<circle r="34" fill="none" stroke="%s" stroke-width="4"/><g fill="%s">%s</g>'
            % (col, col, d))


def solid(fid, c1, t1, c2, t2, ring_c, face, dot, w=290, sd=0):
    """sd=0 draws it flat, with no halo at all"""
    defs = ''
    open_g, close_g = '<g>', '</g>'
    if sd:
        defs = '<defs>' + GLOW.replace('__ID__', fid).replace('__SD__', str(sd)) + '</defs>'
        open_g = '<g filter="url(#' + fid + ')">'
    return ('      <svg viewBox="0 0 370 200" width="' + str(w) + '">' + defs + '\n'
            + open_g + ('\n        <g stroke="%s" stroke-linecap="round">'
               '<line x1="128" y1="66" x2="146" y2="62" stroke-width="5.5"/>'
               '<line x1="126" y1="96" x2="150" y2="94" stroke-width="5.5"/>'
               '<line x1="130" y1="126" x2="144" y2="124" stroke-width="5.5"/></g>\n'
               '        <g stroke="%s" stroke-linecap="round">'
               '<line x1="242" y1="66" x2="224" y2="62" stroke-width="5.5"/>'
               '<line x1="244" y1="96" x2="220" y2="94" stroke-width="5.5"/>'
               '<line x1="240" y1="126" x2="226" y2="124" stroke-width="5.5"/></g>\n'
               '        <g transform="translate(16,46) rotate(-20)">'
               '<rect width="84" height="104" rx="12" fill="%s"/>'
               '<text x="42" y="62" text-anchor="middle" '
               'style="font-family:Archivo;font-weight:800" font-size="34" fill="%s">SH</text></g>\n'
               '        <g transform="translate(354,46) rotate(20) translate(-84,0)">'
               '<rect width="84" height="104" rx="12" fill="%s"/>'
               '<text x="42" y="62" text-anchor="middle" '
               'style="font-family:Archivo;font-weight:800" font-size="34" fill="%s">FFL</text></g>\n'
               '        <g transform="translate(185,98)">%s</g>'
               % (c1, c2, c1, t1, c2, t2, disc_solid(ring_c, face, dot)))
            + close_g + '\n      </svg>\n')


def tube(fid, c1, c2, cd, w=290, sd=4.5):
    defs = '<defs>' + GLOW.replace('__ID__', fid).replace('__SD__', str(sd)) + '</defs>'
    return ('      <svg viewBox="0 0 370 200" width="' + str(w) + '">' + defs + '\n'
            + ('        <g filter="url(#%s)" fill="none">\n'
               '        <g stroke="%s" stroke-linecap="round">'
               '<line x1="128" y1="66" x2="146" y2="62" stroke-width="4.5"/>'
               '<line x1="126" y1="96" x2="150" y2="94" stroke-width="4.5"/>'
               '<line x1="130" y1="126" x2="144" y2="124" stroke-width="4.5"/></g>\n'
               '        <g stroke="%s" stroke-linecap="round">'
               '<line x1="242" y1="66" x2="224" y2="62" stroke-width="4.5"/>'
               '<line x1="244" y1="96" x2="220" y2="94" stroke-width="4.5"/>'
               '<line x1="240" y1="126" x2="226" y2="124" stroke-width="4.5"/></g>\n'
               '        <g transform="translate(16,46) rotate(-20)">'
               '<rect width="84" height="104" rx="12" stroke="%s" stroke-width="5"/>'
               '<text x="42" y="62" text-anchor="middle" '
               'style="font-family:Archivo;font-weight:800" font-size="34" fill="%s">SH</text></g>\n'
               '        <g transform="translate(354,46) rotate(20) translate(-84,0)">'
               '<rect width="84" height="104" rx="12" stroke="%s" stroke-width="5"/>'
               '<text x="42" y="62" text-anchor="middle" '
               'style="font-family:Archivo;font-weight:800" font-size="34" fill="%s">FFL</text></g>\n'
               '        <g transform="translate(185,98)">%s</g></g>\n      </svg>\n'
               % (fid, c1, c2, c1, c1, c2, c2, disc_tube(cd))))


CSS = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
  :root{color-scheme:dark}
  html,body{background:#030305;margin:0}
  body{font-family:"Instrument Sans",sans-serif;color:#FBFAFF;padding:30px 36px;width:1160px}
  h1{font-family:"Archivo";font-weight:800;letter-spacing:-.03em;font-size:28px;margin:0 0 4px}
  h2{font-family:"Archivo";font-weight:700;font-size:17px;margin:32px 0 6px}
  .sub{color:#9C98AE;font-size:12.5px;line-height:1.55;max-width:94ch;margin:0 0 20px}
  .lab{font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
       text-transform:uppercase;color:#6C6880}
  .cell{background:#08080C;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:16px;
        display:flex;flex-direction:column;gap:9px}
  .cell.flag{border-color:rgba(255,46,122,.35)}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.12)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.42}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:16px}
  .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:16px}
  .row{display:flex;gap:14px;margin-bottom:16px}
</style></head><body>
"""

H = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<title>SH:FFL — two purples</title>' + CSS,
     '<h1>SH:FFL &middot; two shades of purple</h1>',
     '<p class="sub"><b>A value pair fixes the structural half of the problem for free.</b> Two '
     'shades of one hue cannot read as two parties meeting — there is only one colour present, '
     'so the cards look like one deck splitting rather than two people arriving. That was the thing '
     'the pink-and-cyan arrangement was doing regardless of which hues sat in it.</p>',
     '<p class="sub"><b>The risk is a different one.</b> Purple on black with a glow is close to the '
     'territory streaming and crypto already occupy, and <b>the blue end of purple walks back toward '
     'the read you were trying to leave</b>. The pairs below are ordered from the magenta side to '
     'the blue side so you can see where that starts; the last one is flagged.</p>']

PAIRS = [
 ("P1 · MAGENTA-PURPLE + VIOLET", MAGP, WHITE, VIO, WHITE, INK, OFFW, INK, 0,
  "<b>The warm end.</b> One card leans toward magenta, the other toward true violet — far "
  "enough apart to be two shades, close enough to stay one colour. Nearest to the pink you already "
  "own, so it is the smallest move from where the brand is now."),
 ("P2 · NEON PURPLE + AUBERGINE", NEOP, '#1A0528', AUB, NEOP, INK, OFFW, INK, 0,
  "<b>The widest value gap here.</b> One card is nearly lit and the other nearly black, which gives "
  "the mark real depth — but the dark card needs the white disc beside it or it disappears "
  "into the ground."),
 ("P3 · ORCHID + GRAPE", ORCH, '#2A0A44', GRAPE, LILAC, INK, OFFW, INK, 0,
  "A mid-value pair, neither extreme. <b>The most usable of the six</b> — both cards read "
  "clearly on either ground, and neither one is doing anything loud enough to date badly."),
 ("P4 · LILAC + ELECTRIC VIOLET", LILAC, '#2A0A44', VIO, WHITE, INK, INK2, LILAC, 0,
  "Light against electric, with the crowd in lilac so the disc joins the family. <b>The softest "
  "option</b>, which is worth naming as a risk rather than a feature given what you are steering "
  "away from."),
 ("P5 · VIOLET + DEEP PLUM", VIO, WHITE, PLUM, ORCH, INK, OFFW, INK, 0,
  "Electric over deep plum. <b>Plum is the only one of these darks that still reads as a colour</b> "
  "rather than as black, so the mark keeps two hues without gaining two parties."),
 ("P6 · IRIS + LILAC · FLAGGED", IRIS, WHITE, LILAC, '#1A0B33', INK, OFFW, INK, 0,
  "<b>This is where purple becomes blue.</b> Iris sits on the blue side, and paired with a pale "
  "lilac the mark starts reading soft and romantic again. Included as the boundary, not as an option."),
]
H.append('<h2>Six purple pairs, flat</h2><div class="g3">')
for i, (lab, c1, t1, c2, t2, rc, face, dot, sd, note) in enumerate(PAIRS):
    H.append('<div class="cell%s"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (' flag' if 'FLAGGED' in lab else '', lab,
                solid('pf%d' % i, c1, t1, c2, t2, rc, face, dot), note))
H.append('</div>')

H.append('<h2>The same pairs lit</h2>'
         '<p class="sub"><b>Purple gains more from a halo than any other hue</b>, because a violet '
         'glow on black is the one piece of colour the eye reads as genuinely light-emitting rather '
         'than painted. It is also exactly why the territory is crowded.</p><div class="g3">')
for i, (lab, c1, t1, c2, t2, rc, face, dot, note) in enumerate([
 ("P1 LIT", MAGP, WHITE, VIO, WHITE, INK, OFFW, INK,
  "The warm pair lit. <b>The magenta card throws a pink halo and the violet throws a blue one</b>, "
  "so the glow quietly reintroduces the two-colour read the flat version had removed."),
 ("P3 LIT", ORCH, '#2A0A44', GRAPE, LILAC, INK, OFFW, INK,
  "Orchid and grape lit. <b>The halos are close enough in hue that they merge into one field</b> "
  "instead of two — which is the behaviour you want, and it only happens with a tight pair."),
 ("P5 LIT", VIO, WHITE, PLUM, ORCH, INK, OFFW, INK,
  "Electric and plum. <b>Only the bright card glows</b>, because a dark colour has nothing to emit "
  "— so the mark lights asymmetrically, which looks like one sign with one tube lit."),
]):
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (lab, solid('pl%d' % i, c1, t1, c2, t2, rc, face, dot, sd=5), note))
H.append('</div>')

H.append('<h2>As tube</h2><div class="g2">')
for i, (lab, c1, c2, cd, note) in enumerate([
 ("T · ORCHID + GRAPE", ORCH, GRAPE, '#EAD9FF',
  "<b>The darker purple struggles as glass.</b> A tube is a thin line, and a thin line in a deep "
  "colour on a dark ground has almost no contrast to work with — grape nearly vanishes while "
  "orchid sings."),
 ("T · TWO LIGHT PURPLES", ORCH, NEOP, '#EAD9FF',
  "<b>Tube needs both shades at the bright end.</b> Orchid against neon purple keeps the value gap "
  "small and the brightness high, which is the only way a two-shade tube reads as two shades."),
]):
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="min-height:170px">\n%s</div><div class="note">%s</div></div>'
             % (lab, tube('pt%d' % i, c1, c2, cd, 320), note))
H.append('</div>')

H.append('<h2>On the light ground</h2><div class="g3">')
for i, (lab, c1, t1, c2, t2, rc, face, dot, note) in enumerate([
 ("P1 ON LIGHT", MAGP, WHITE, VIO, WHITE, LITE, DEEP, OFFW,
  "<b>Both hold.</b> Purple is one of the few colours that keeps its identity against paper-white "
  "without darkening — the opposite of cyan, and the reason this direction is cheaper to "
  "maintain than the original."),
 ("P3 ON LIGHT", ORCH, '#2A0A44', GRAPE, LILAC, LITE, DEEP, OFFW,
  "<b>Orchid is the one to watch.</b> It is pale enough that on white it starts to lose its edge, "
  "though the dark letters hold it together. Grape is untouched."),
 ("P5 ON LIGHT", VIO, WHITE, PLUM, ORCH, LITE, DEEP, OFFW,
  "<b>The best of the three on light.</b> Deep plum against paper is a genuinely strong contrast, "
  "and the electric card keeps every bit of its chroma."),
]):
    H.append('<div class="cell lite"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (lab, solid('pw%d' % i, c1, t1, c2, t2, rc, face, dot, 300), note))
H.append('</div>')

H.append('<h2>Small — the whole mark at 150px, 96px and 64px wide</h2><div class="row">')
for i, (lab, args) in enumerate([
        ("P1 · MAGENTA + VIOLET", (MAGP, WHITE, VIO, WHITE, INK, OFFW, INK)),
        ("P3 · ORCHID + GRAPE", (ORCH, '#2A0A44', GRAPE, LILAC, INK, OFFW, INK)),
        ("P5 · VIOLET + PLUM", (VIO, WHITE, PLUM, ORCH, INK, OFFW, INK))]):
    inner = ''
    for j, w in enumerate((150, 96, 64)):
        inner += ('<div style="display:grid;place-items:center">%s</div>'
                  % solid('pi%d%d' % (i, j), *args, w=w))
    H.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="gap:10px;display:flex;align-items:center;min-height:80px">%s'
             '</div></div>' % (lab, inner))
H.append('</div>')
H.append('<p class="sub"><b>Two shades of one hue cost you something at small sizes.</b> A pair that '
         'is far apart in hue stays two cards all the way down; a pair that differs only in value '
         'starts to look like one card and its shadow. <b>P5 survives furthest</b> because the gap '
         'between electric violet and deep plum is wide enough to read at 64px, which is the '
         'argument for choosing a wide value gap over a subtle one.</p>')
H.append('</body></html>')
io.open(os.path.join(D, 'logos15.html'), 'w', encoding='utf-8').write('\n'.join(H))
print('written')
