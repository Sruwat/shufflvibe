# -*- coding: utf-8 -*-
"""Neon palettes for the card mark, and the neon-tube treatment."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

INK, LITE, WHITE = '#060609', '#F4F2F8', '#FFFFFF'
INK2, OFFW, DEEP = '#121218', '#FBFAFF', '#1A1A22'

MAG   = '#FF2E7A'   # the brand pink, already a neon
HOTM  = '#FF1E88'
NRED  = '#FF3B1F'   # true neon: an orange-red
NTANG = '#FF8A00'
NAMB  = '#FFC400'
NYEL  = '#F0FF3D'
NLIME = '#A8FF1F'
NGRN  = '#2BFF88'
NTURQ = '#1FFFD0'
NVIO  = '#9B4DFF'
ICE   = '#EAFBFF'

B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]

GLOW = ('<filter id="__ID__" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="__SD__" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/>'
        '<feMergeNode in="SourceGraphic"/></feMerge></filter>')


def glow_def(fid, sd=5):
    return GLOW.replace('__ID__', fid).replace('__SD__', str(sd))


def disc_solid(ring_c, face, dot):
    d = ''.join('<circle cx="%s" cy="%s" r="5.4"/>' % (x, y) for x, y in B8)
    return ('<circle r="40" fill="%s"/><circle r="31" fill="%s"/><g fill="%s">%s</g>'
            % (ring_c, face, dot, d))


def disc_tube(col):
    """the disc as a drawn ring with lit dots, nothing filled"""
    d = ''.join('<circle cx="%s" cy="%s" r="4.4"/>' % (x, y) for x, y in B8)
    return ('<circle r="34" fill="none" stroke="%s" stroke-width="4"/><g fill="%s">%s</g>'
            % (col, col, d))


def solid(fid, c1, t1, c2, t2, face, dot, w=290, sd=5):
    """neon as a filled card with a halo behind it"""
    return ('      <svg viewBox="0 0 370 200" width="' + str(w) + '">'
            + '<defs>' + glow_def(fid, sd) + '</defs>\n'
            + ('        <g filter="url(#%s)">\n'
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
               '<text x="42" y="62" text-anchor="middle" '
               'style="font-family:Archivo;font-weight:800" font-size="34" fill="%s">SH</text></g>\n'
               '        <g transform="translate(354,46) rotate(20) translate(-84,0)">'
               '<rect width="84" height="104" rx="12" fill="%s"/>'
               '<text x="42" y="62" text-anchor="middle" '
               'style="font-family:Archivo;font-weight:800" font-size="34" fill="%s">FFL</text></g>\n'
               '        <g transform="translate(185,98)">%s</g></g>\n      </svg>\n'
               % (fid, c1, c2, c1, t1, c2, t2, disc_solid(INK, face, dot))))


def tube(fid, c1, c2, cd, w=290, sd=4.5):
    """neon as a drawn tube - nothing filled, everything lit"""
    return ('      <svg viewBox="0 0 370 200" width="' + str(w) + '">'
            + '<defs>' + glow_def(fid, sd) + '</defs>\n'
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
     '<title>SH:FFL — neon</title>' + CSS,
     '<h1>SH:FFL &middot; neon</h1>',
     '<p class="sub"><b>Neon is a treatment before it is a palette.</b> What makes a sign read as '
     'neon is that it is a lit tube on a dark wall, with a halo around it — not that it is a '
     'bright colour. So the sheet runs two sections: the same high-chroma pairs as filled cards with '
     'a glow behind them, and then the cards redrawn as tubes. <b>The ground is darker here than on '
     'previous sheets</b> (#030305), because a halo needs somewhere to fall off to.</p>']

# ---------------------------------------------------------------- solid neon
SOLID = [
 ("N1 · NEON RED + ACID LIME", NRED, '#2A0600', NLIME, '#1A2A00', OFFW, INK,
  "<b>The two colours real tubes actually come in.</b> Neon proper is an orange-red; the green is a "
  "different gas. Put them together and it reads as signage rather than as a brand palette."),
 ("N2 · TANGERINE + LIME", NTANG, '#2A1400', NLIME, '#1A2A00', OFFW, INK,
  "Analogous and both hot. <b>No pairing read at all</b> because they sit beside each other on the "
  "wheel — the mark looks like one light source, not two."),
 ("N3 · MAGENTA + ACID LIME", MAG, WHITE, NLIME, '#1A2A00', OFFW, INK,
  "<b>Keeps the brand pink and replaces the blue with the loudest thing available.</b> Magenta and "
  "lime is a rave palette, not a romance palette — the pink stops being soft the moment it is "
  "next to a green that aggressive."),
 ("N4 · VIOLET + LIME", NVIO, WHITE, NLIME, '#1A2A00', OFFW, INK,
  "UV and acid. <b>The most club-specific pair here</b> — this is what a blacklight room "
  "actually looks like. Violet is the risk: it is a short step from violet to the purple every "
  "streaming app uses."),
 ("N5 · ONE COLOUR · NEON GREEN", NGRN, '#002A14', NGRN, '#002A14', INK2, NGRN,
  "Single hue, disc dark, crowd lit. <b>Reads as one sign rather than two cards</b>, and green is "
  "the most legible neon at distance, which is why exit signs are green."),
 ("N6 · ONE COLOUR · NEON RED", NRED, '#2A0600', NRED, '#2A0600', INK2, NRED,
  "The same structure in the true neon hue. <b>Warmest and most nostalgic</b> — this is a bar "
  "sign in a window, which is the right association for what the product does."),
 ("N7 · YELLOW + NEON RED", NYEL, '#2A2A00', NRED, '#2A0600', OFFW, INK,
  "Sodium against neon — <b>the two colours a street at night is actually lit by</b>. Highest "
  "combined brightness on the sheet, and the hardest to look at for long."),
 ("N8 · TURQUOISE + TANGERINE", NTURQ, '#002A22', NTANG, '#2A1400', OFFW, INK,
  "<b>Where the blue line is.</b> Turquoise is a green-cyan, not a blue, and paired with orange "
  "instead of pink it does not read as a dating app — but it is the closest this sheet comes."),
 ("N9 · ICE + NEON RED", ICE, '#101018', NRED, '#2A0600', INK2, ICE,
  "A white tube is a real neon too, and the cheapest to make. <b>One colour plus white</b> is the "
  "most restrained neon available and the easiest to extend into a system."),
]
H.append('<h2>Nine neon pairs, filled cards with a halo</h2><div class="g3">')
for i, (lab, c1, t1, c2, t2, face, dot, note) in enumerate(SOLID):
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (lab, solid('ns%d' % i, c1, t1, c2, t2, face, dot), note))
H.append('</div>')

# ---------------------------------------------------------------- tube neon
TUBES = [
 ("T1 · TUBE · NEON RED", NRED, NRED, NRED,
  "<b>Nothing is filled.</b> The cards are the glass, the letters are the glass, the disc is the "
  "glass. This is the version that actually looks like a sign rather than like a logo with a glow "
  "applied to it."),
 ("T2 · TUBE · LIME + TANGERINE", NLIME, NTANG, ICE,
  "Two gases in one sign, with the crowd in white. <b>The disc in a third colour is what a real "
  "multi-tube sign does</b> — each colour is a separate tube, so each shape gets exactly one."),
 ("T3 · TUBE · MAGENTA + LIME", MAG, NLIME, ICE,
  "The brand pink as glass. <b>Pink loses its softness completely once it is a line instead of a "
  "field</b> — this may be the cheapest way to keep the colour you own and lose the coding."),
 ("T4 · TUBE · ICE, ONE COLOUR", ICE, ICE, NRED,
  "All white glass with a single red disc. <b>The quietest neon</b>, and the one that would still "
  "work printed flat, because a white line on black survives losing its halo."),
]
H.append('<h2>The tube treatment</h2>'
         '<p class="sub"><b>A neon sign is a bent tube, so everything becomes a line.</b> The cards '
         'lose their fill and become outlines, the disc becomes a drawn ring, and the crowd stays '
         'solid because eight small circles are the one thing you cannot render as tube without it '
         'turning to mush.</p><div class="g2">')
for i, (lab, c1, c2, cd, note) in enumerate(TUBES):
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="min-height:170px">\n%s</div><div class="note">%s</div></div>'
             % (lab, tube('nt%d' % i, c1, c2, cd, 320), note))
H.append('</div>')

# ---------------------------------------------------------------- the catch
H.append('<h2>The catch</h2><div class="g2">')
H.append('<div class="cell lite"><div class="lab">N3 ON LIGHT</div>'
         '<div class="art" style="min-height:160px">\n%s</div>'
         '<div class="note"><b>A halo on white does nothing.</b> Glow is light added to a dark '
         'ground; on paper there is no headroom above white, so the filter just softens the edges '
         'and the mark looks slightly out of focus. <b>Every neon option here needs a separate flat '
         'version for light grounds</b> — that is the real cost of this direction.</div></div>'
         % solid('nl1', MAG, WHITE, NLIME, '#1A2A00', DEEP, OFFW, 300))
H.append('<div class="cell lite"><div class="lab">T1 ON LIGHT</div>'
         '<div class="art" style="min-height:160px">\n%s</div>'
         '<div class="note">The tube is worse: <b>a lit line on a white page is just a thin line</b>, '
         'and the whole read depends on the glow that is no longer visible. If the mark has to live '
         'on light at all, the tube version cannot be the primary.</div></div>'
         % tube('nl2', NRED, NRED, NRED, 300))
H.append('</div>')

H.append('<h2>At icon size — 72px, 44px, 32px</h2><div class="row">')
for i, (lab, kind, args) in enumerate([
        ("N3 · FILLED", 'solid', (MAG, WHITE, NLIME, '#1A2A00', OFFW, INK)),
        ("N6 · ONE COLOUR", 'solid', (NRED, '#2A0600', NRED, '#2A0600', INK2, NRED)),
        ("T1 · TUBE", 'tube', (NRED, NRED, NRED))]):
    inner = ''
    for j, w in enumerate((150, 96, 64)):
        fid = 'ni%d%d' % (i, j)
        svg = solid(fid, *args, w=w, sd=3) if kind == 'solid' else tube(fid, *args, w=w, sd=2.5)
        inner += '<div style="display:grid;place-items:center">%s</div>' % svg
    H.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="gap:10px;display:flex;align-items:center;min-height:90px">%s'
             '</div></div>' % (lab, inner))
H.append('</div>')
H.append('<p class="sub"><b>The glow is the first casualty and the tube is the second.</b> By 64px '
         'wide the halo has merged with the shape it surrounds and is just making the mark look '
         'blurry, and the tube outlines have closed up into solid bars. <b>Neon is a header, poster '
         'and story treatment</b> — the app icon has to be the flat version of whichever palette '
         'you pick, which is an argument for choosing a pair that works flat first and glows second.</p>')

H.append('</body></html>')
io.open(os.path.join(D, 'logos14.html'), 'w', encoding='utf-8').write('\n'.join(H))
print('written')
