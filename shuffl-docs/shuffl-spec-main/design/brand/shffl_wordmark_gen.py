# -*- coding: utf-8 -*-
"""The wordmark alone: SH, the card mark as the colon, FFL. Optical gap 10."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

PINK, CYAN = '#FF2E7A', '#24E0FF'
INK, LITE = '#060609', '#F4F2F8'
OFFW, DEEP, INK2 = '#FBFAFF', '#1A1A22', '#121218'

B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]


def wordmark(w, c1=PINK, c2=PINK, ink=OFFW, ring=OFFW, face=INK2, dot=CYAN,
             font="'Bebas Neue'", size=102, ls='.14em', x_ffl=322, box=498):
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
    return ('<svg viewBox="0 10 %s 112" width="%s">'
            '<text x="0" y="104" style="%s" font-size="%s" fill="%s">SH</text>'
            '<g transform="translate(110,0)">%s</g>'
            '<text x="%s" y="104" style="%s" font-size="%s" fill="%s">FFL</text></svg>'
            % (box, w, sty, size, ink, mark, x_ffl, sty, size, ink))


H = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — the wordmark</title>
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
  .cell{background:#0D0D12;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:22px;
        display:flex;flex-direction:column;gap:12px;margin-bottom:16px}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.12)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.45}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:16px}
</style></head><body>
<h1>SH:FFL &middot; the wordmark</h1>
<p class="sub"><b>The mark is not beside the name, it is the punctuation inside it.</b> SH, the card
mark where the colon goes, FFL &mdash; at the optical gap of 10 either side. The crowd is the eight
with the open centre, one radius throughout. <b>The thing that makes the spelling odd is the thing
that makes it the logo.</b></p>
"""]

H.append('<div class="cell"><div class="lab">PRIMARY &middot; BOTH CARDS PINK, CROWD CYAN</div>'
         '<div class="art" style="min-height:160px">%s</div>'
         '<div class="note">One hue on both cards, cyan kept for the crowd, and a white rim on the '
         'disc so it holds its edge against a dark ground. <b>One deck splitting, not two things '
         'meeting</b> &mdash; which is what takes the pairing read out of it.</div></div>'
         % wordmark(820))

H.append('<div class="cell"><div class="lab">ALTERNATIVE &middot; PINK AND CYAN CARDS</div>'
         '<div class="art" style="min-height:160px">%s</div>'
         '<div class="note">The two-colour version, with the white disc and ink crowd. <b>Louder, '
         'and it matches the chameleon’s pink and cyan exactly</b> &mdash; at the cost of '
         'bringing back the two-parties read the primary removes.</div></div>'
         % wordmark(820, c1=PINK, c2=CYAN, ring=INK, face=OFFW, dot=INK))

H.append('<h2>On the light ground</h2><div class="g2">')
H.append('<div class="cell lite"><div class="lab">PRIMARY &middot; LIGHT</div>'
         '<div class="art" style="min-height:140px">%s</div>'
         '<div class="note">Letters to near-black, disc keeps its dark face and white crowd, rim '
         'drops away. <b>Nothing else changes.</b></div></div>'
         % wordmark(480, ink=DEEP, ring=LITE, face=DEEP, dot=OFFW))
H.append('<div class="cell lite"><div class="lab">ALTERNATIVE &middot; LIGHT</div>'
         '<div class="art" style="min-height:140px">%s</div>'
         '<div class="note"><b>Cyan collapses toward black on paper-white</b>, so the right card '
         'stops being cyan and starts being dark. The known failure of that pair.</div></div>'
         % wordmark(480, c1=PINK, c2=CYAN, ink=DEEP, ring=DEEP, face=OFFW, dot=DEEP))
H.append('</div>')

H.append('<div class="cell"><div class="lab">ARCHIVO 800 INSTEAD OF BEBAS</div>'
         '<div class="art" style="min-height:160px">%s</div>'
         '<div class="note">Wider and heavier. <b>Archivo makes the name the loudest thing</b>, '
         'which is right when the wordmark stands alone and wrong when it sits under the '
         'chameleon.</div></div>'
         % wordmark(760, font='Archivo', size=70, ls='0', x_ffl=324, box=455))

H.append('<h2>Down in size</h2><div class="cell">'
         '<div class="art" style="display:flex;flex-direction:column;gap:22px;align-items:center;'
         'min-height:260px">')
for w in (560, 360, 230, 150):
    H.append('<div>%s</div>' % wordmark(w))
H.append('</div><div class="note"><b>The crowd is the first thing to go.</b> At 360px wide you can '
         'still count eight; by 230px it is a ring; by 150px it is a dark dot between two cards. '
         '<b>The cards and the letters survive all the way down</b>, which is what matters — '
         'the name still reads as SH:FFL even when the room inside it has closed up.</div></div>')

H.append('</body></html>')
io.open(os.path.join(D, 'logos18.html'), 'w', encoding='utf-8').write('\n'.join(H))
print('written')
