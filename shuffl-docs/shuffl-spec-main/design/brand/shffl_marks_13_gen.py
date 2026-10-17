# -*- coding: utf-8 -*-
"""Colour pairs for the card mark that do not read as a dating app."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

PINK, CYAN = '#FF2E7A', '#24E0FF'
INK, LITE, WHITE = '#060609', '#F4F2F8', '#FFFFFF'
INK2, OFFW, DEEP = '#121218', '#FBFAFF', '#1A1A22'

MARI = '#FFB01F'   # marigold
SAFF = '#FF7A1A'   # saffron
VERM = '#FF4D2E'   # vermilion
CLAY = '#E0684A'
OXBL = '#9E1B32'   # oxblood
BRASS = '#D4A32C'
LIME = '#C6FF2E'   # acid lime
YELL = '#FFE500'
JADE = '#00C27A'
FOR = '#0E6B4A'    # deep green
TEAL = '#0FA3A3'
PLUM = '#5B1E4E'
CREAM = '#F6EFE2'
BONE = '#E8E2D4'

B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]


def disc(ring_c=INK, face=OFFW, dot=INK, r=40, ri=31):
    d = ''.join('<circle cx="%s" cy="%s" r="5.4"/>' % (x, y) for x, y in B8)
    return ('<circle r="%s" fill="%s"/><circle r="%s" fill="%s"/><g fill="%s">%s</g>'
            % (r, ring_c, ri, face, dot, d))


def mark(c1, t1, c2, t2, ring_c=INK, face=OFFW, dot=INK, w=290):
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
            % (w, c1, c2, c1, t1, c2, t2, disc(ring_c, face, dot)))


CSS = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap">
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
  .cell.bad{border-color:rgba(255,46,122,.35)}
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
     '<title>SH:FFL — colour pairs that are not a dating app</title>' + CSS,
     '<h1>SH:FFL &middot; getting the dating app out of it</h1>',
     '<p class="sub"><b>The hues are only half of why it reads that way.</b> Pink and blue is the '
     'specific coding, but the other half is structural: <b>two different colours meeting around a '
     'shared circle is a picture of two parties pairing up</b>, whatever the hues are. So there are '
     'two independent levers here, and the first section pulls each one on its own before the '
     'palettes start.</p>']

H.append('<h2>Two one-change fixes, before changing the palette at all</h2><div class="g3">')
for lab, args, note in [
 ("WHERE IT IS NOW", (PINK, WHITE, CYAN, WHITE, INK, OFFW, INK),
  "<b>Two hues, one each side, symmetric.</b> Pink and blue is the dating-app signal, but the "
  "arrangement is doing as much work as the colours — two parties approaching a shared middle."),
 ("FIX 1 · ONE COLOUR, BOTH CARDS", (PINK, WHITE, PINK, WHITE, INK, INK2, PINK),
  "<b>Same pink, both cards.</b> Nothing has met anything; it is one deck splitting, which is what "
  "the product actually does. <b>This alone removes most of the dating read</b> without touching "
  "the brand colour."),
 ("FIX 2 · NEIGHBOURS, NOT OPPOSITES", (PINK, WHITE, SAFF, WHITE, INK, OFFW, INK),
  "Pink and saffron — <b>two colours next to each other on the wheel instead of across it</b>. "
  "Reads as one thing shifting hue rather than two things meeting. Still warm, still pink-based."),
]:
    H.append('<div class="cell%s"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (' bad' if lab.startswith('WHERE') else '', lab, mark(*args), note))
H.append('</div>')

# label, card1, text1, card2, text2, face, dot, note
PALETTES = [
 ("01 · MARIGOLD + VERMILION", MARI, '#3A1E00', VERM, WHITE, OFFW, INK,
  "<b>Warm analogous — marigold into vermilion.</b> Neighbours on the wheel, so it reads as "
  "heat rather than as a pair. Marigold is also the most Delhi colour there is, and nobody has ever "
  "built a dating app on it."),
 ("02 · ONE COLOUR · MARIGOLD", MARI, '#3A1E00', MARI, '#3A1E00', INK2, MARI,
  "The same hue on both cards with the crowd carrying it too. <b>Three statements of one colour</b> "
  "— the most ownable version here, and the easiest to recognise at a distance."),
 ("03 · ACID LIME + INK", LIME, '#16220A', DEEP, LIME, OFFW, INK,
  "<b>Club flyer, not dating profile.</b> Acid lime on black is the loudest thing on this sheet and "
  "the furthest from soft. But look at the right card: <b>a black card disappears on a black "
  "ground</b>, so this one needs an outline on dark or a lighter neutral — see 10."),
 ("04 · LIME + DEEP GREEN", LIME, '#16220A', FOR, LIME, OFFW, INK,
  "Same lime, paired down into a deep green. <b>A value pair rather than a hue pair</b> — light "
  "and dark of the same family, which never reads as two parties."),
 ("05 · BRASS + OXBLOOD", BRASS, '#2A1B00', OXBL, BONE, OFFW, INK,
  "<b>The upmarket end.</b> Brass and oxblood is a bar interior, not an app — leather, low "
  "light, a good list. Costs you the neon energy the rest of the product has."),
 ("06 · SAFFRON + PLUM", SAFF, '#2A1200', PLUM, '#FFD9F2', OFFW, INK,
  "Warm against deep. <b>Plum is the one dark here that is not black</b>, which keeps the mark from "
  "going flat while staying well away from blue."),
 ("07 · ELECTRIC YELLOW · ONE COLOUR", YELL, '#2A2600', YELL, '#2A2600', INK2, YELL,
  "<b>Maximum visibility, zero romance.</b> Yellow is a warning colour and a taxi colour and a "
  "sodium-lamp colour. It is also the hardest of these to use on a light ground."),
 ("08 · JADE + MARIGOLD", JADE, '#002E1C', MARI, '#3A1E00', OFFW, INK,
  "Green and gold. <b>Opposites, so the pairing read comes back a little</b>, but green-and-gold "
  "codes as festive rather than romantic — it is the one complementary pair here that survives."),
 ("09 · CLAY + TEAL", CLAY, '#2E0E05', TEAL, '#002424', OFFW, INK,
  "A softer, earthier version of the original idea. <b>Teal is as close to blue as this sheet goes</b> "
  "— included so you can see where the line actually is."),
 ("10 · VERMILION + CREAM", VERM, WHITE, CREAM, '#5A1A0C', INK2, CREAM,
  "One hot card, one neutral. <b>The cream reads as paper</b>, so the mark looks like something "
  "printed rather than something rendered."),
 ("11 · ONE COLOUR · VERMILION", VERM, WHITE, VERM, WHITE, INK2, VERM,
  "Single-hue again, in the hottest red that is not a danger signal. <b>Closest in energy to the "
  "current pink</b> while carrying none of its coding."),
 ("12 · PINK + LIME", PINK, WHITE, LIME, '#16220A', OFFW, INK,
  "<b>The smallest possible change: keep the pink, replace the blue.</b> Lime is aggressive enough "
  "that the pair stops reading as soft, and you keep the brand colour you already own."),
]

H.append('<h2>Twelve palettes, on the 01 geometry</h2>'
         '<p class="sub">All with the eight and the open centre. <b>Where both cards share a hue the '
         'disc goes dark and the crowd takes the colour</b>, so there is still something for the '
         'colour to do in the middle.</p><div class="g3">')
for lab, c1, t1, c2, t2, face, dot, note in PALETTES:
    rc = INK
    H.append('<div class="cell"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (lab, mark(c1, t1, c2, t2, rc, face, dot), note))
H.append('</div>')

H.append('<h2>Four of them on the light ground</h2><div class="g2">')
for lab, c1, t1, c2, t2, rc, face, dot, note in [
 ("01 ON LIGHT", MARI, '#3A1E00', VERM, WHITE, DEEP, OFFW, DEEP,
  "<b>Both survive the flip untouched.</b> Warm colours hold their value against paper-white in a "
  "way cyan never did — this is the practical argument for a warm palette, not an aesthetic one."),
 ("02 ON LIGHT", MARI, '#3A1E00', MARI, '#3A1E00', LITE, DEEP, MARI,
  "Single-hue marigold with a dark disc. <b>Nothing is redrawn for either ground</b>, which was the "
  "property that made 03 the safe card mark two sheets ago."),
 ("03 ON LIGHT", LIME, '#16220A', DEEP, LIME, LITE, DEEP, LIME,
  "<b>Acid lime is the one that struggles.</b> It is a light colour, so on a light ground the card "
  "loses its edge and the mark starts to feel like it is missing a piece."),
 ("11 ON LIGHT", VERM, WHITE, VERM, WHITE, LITE, DEEP, VERM,
  "Vermilion holds as cleanly on light as pink does, and <b>reads hotter at the same saturation</b> "
  "because it sits closer to the middle of human colour sensitivity."),
]:
    H.append('<div class="cell lite"><div class="lab">%s</div>'
             '<div class="art" style="min-height:150px">\n%s</div><div class="note">%s</div></div>'
             % (lab, mark(c1, t1, c2, t2, rc, face, dot, 300), note))
H.append('</div>')

H.append('<p class="sub"><b>Note on the chameleon:</b> 02 is locked — pink body, cyan night. '
         'If the card mark moves off pink and cyan, <b>the two marks stop sharing a palette</b>, '
         'which is either a problem or a deliberate split between the product mark and the campaign '
         'mark. Worth deciding rather than discovering.</p>')
H.append('</body></html>')
io.open(os.path.join(D, 'logos13.html'), 'w', encoding='utf-8').write('\n'.join(H))
print('written')
