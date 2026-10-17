# -*- coding: utf-8 -*-
"""The locked chameleon: 02, pink body, cyan night."""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

PINK, CYAN = '#FF2E7A', '#24E0FF'
INK, LITE = '#060609', '#F4F2F8'
OFFW, DEEP = '#FBFAFF', '#1A1A22'
TEAL = '#0E7E93'          # the night, darkened for light grounds
EYEDK = '#12000A'

BODY = ("M88 170 C92 134 110 108 142 95 C174 82 200 76 220 72 C230 70 238 64 244 54 "
        "L252 30 L268 62 C276 72 286 80 296 86 L326 96 L300 110 L330 122 "
        "C308 138 282 148 252 153 C208 161 138 168 88 170 Z")
TAIL = ("M88 168 C62 168 46 180 46 196 C46 210 58 220 72 220 C84 220 93 212 93 201 "
        "C93 192 86 186 78 186 C72 186 68 190 68 195")
TONG = "M328 114 C364 114 380 102 396 86 C410 72 428 64 448 66"


def cham(w, body=PINK, tongue=CYAN, eye_ring=EYEDK, iris=OFFW, pupil=EYEDK):
    return ('<svg viewBox="30 20 440 215" width="%s">'
            '<path d="%s" fill="%s"/>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="15" stroke-linecap="round"/>'
            '<circle cx="268" cy="96" r="18" fill="%s"/>'
            '<circle cx="268" cy="96" r="10.5" fill="%s"/>'
            '<circle cx="271" cy="96" r="4" fill="%s"/>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
            '<circle cx="372" cy="100" r="8" fill="%s"/>'
            '<circle cx="410" cy="71" r="12" fill="%s"/>'
            '<circle cx="446" cy="66" r="17" fill="%s"/></svg>'
            % (w, BODY, body, TAIL, body, eye_ring, iris, pupil,
               TONG, tongue, tongue, tongue, tongue))


def lockup(w, ink=OFFW, body=PINK, tongue=CYAN, iris=OFFW):
    return ('<svg viewBox="0 0 900 250" width="%s">'
            '<g transform="scale(0.92)">'
            '<path d="%s" fill="%s"/>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="15" stroke-linecap="round"/>'
            '<circle cx="268" cy="96" r="18" fill="%s"/>'
            '<circle cx="268" cy="96" r="10.5" fill="%s"/>'
            '<circle cx="271" cy="96" r="4" fill="%s"/></g>'
            '<path d="M302 105 C336 105 352 96 366 86" fill="none" stroke="%s" stroke-width="7" '
            'stroke-linecap="round"/><circle cx="368" cy="85" r="11" fill="%s"/>'
            '<text x="398" y="178" style="font-family:\'Bebas Neue\';letter-spacing:.06em" '
            'font-size="150" fill="%s">SH</text>'
            '<circle cx="636" cy="100" r="15" fill="%s"/>'
            '<circle cx="636" cy="156" r="15" fill="%s"/>'
            '<text x="672" y="178" style="font-family:\'Bebas Neue\';letter-spacing:.06em" '
            'font-size="150" fill="%s">FFL</text></svg>'
            % (w, BODY, body, TAIL, body, EYEDK, iris, EYEDK,
               tongue, tongue, ink, tongue, tongue, ink))


H = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SH:FFL — the chameleon, locked</title>
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
  .cell{background:#0D0D12;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:18px;
        display:flex;flex-direction:column;gap:10px;margin-bottom:16px}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.12)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.45}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:16px}
  .swatch{display:flex;gap:10px;align-items:center}
  .chip{width:34px;height:34px;border-radius:8px;flex:0 0 auto}
  .cw{font-family:"IBM Plex Mono",monospace;font-size:10px;color:#9C98AE;line-height:1.4}
</style></head><body>
<h1>SH:FFL &middot; the chameleon, locked</h1>
<p class="sub"><b>02 &mdash; pink body, cyan night.</b> The animal is the brand colour and the night
it catches is the cyan. <b>The curl, the casque and the turret eye are the three cues that say
chameleon</b>; the tongue is the night skeleton, rising left to right with the stop circles growing
as the crowd does, which is how the drawing actually works in the app.</p>
"""]

H.append('<div class="cell"><div class="lab">THE MARK</div>'
         '<div class="art" style="min-height:250px">%s</div>'
         '<div class="note">Pink holds its hue on every ground, which is what makes it the brand '
         'colour rather than the letters. <b>The eye is the only place a third value appears</b> '
         '&mdash; near-black ring, white iris, near-black pupil &mdash; and it is what stops the '
         'head reading as a flat shape.</div></div>' % cham(620))

H.append('<div class="cell"><div class="lab">THE LOCKUP &middot; THE TONGUE WRITES THE NAME</div>'
         '<div class="art" style="min-height:190px">%s</div>'
         '<div class="note">The tongue leaves the mouth, lands as the first stop, and <b>the colon '
         'is the next two stops on the same line</b> &mdash; so the animal and the name share one '
         'baseline instead of sitting beside each other, and the colon in SH:FFL stops being '
         'punctuation and becomes two venues on a night.</div></div>' % lockup(900))

H.append('<h2>On the light ground</h2><div class="g2">')
H.append('<div class="cell lite"><div class="lab">AS DRAWN</div>'
         '<div class="art" style="min-height:190px">%s</div>'
         '<div class="note"><b>Cyan at full strength is close to invisible on paper-white.</b> '
         'The body is untouched; the night is the problem.</div></div>'
         % cham(430, iris=OFFW))
H.append('<div class="cell lite"><div class="lab">NIGHT DARKENED TO TEAL</div>'
         '<div class="art" style="min-height:190px">%s</div>'
         '<div class="note">The night drops to <b>#0E7E93</b> so it survives the page. <b>This is '
         'the one compromise in the locked mark</b> &mdash; on light grounds the night stops being '
         'exactly the app’s cyan. Worth recording now rather than discovering it at '
         'print.</div></div>' % cham(430, tongue=TEAL))
H.append('</div>')

H.append('<h2>The lockup on light</h2>')
H.append('<div class="cell lite"><div class="lab">LOCKUP &middot; LIGHT</div>'
         '<div class="art" style="min-height:180px">%s</div>'
         '<div class="note">Letters go to near-black, night goes to teal, body unchanged.</div>'
         '</div>' % lockup(860, ink=DEEP, tongue=TEAL))

H.append('<h2>Small &mdash; 300px, 180px, 110px wide</h2><div class="cell">'
         '<div class="art" style="gap:20px;display:flex;align-items:center;min-height:150px">')
for w in (300, 180, 110):
    H.append('<div style="display:grid;place-items:center">%s</div>' % cham(w))
H.append('</div><div class="note"><b>The night dies first.</b> By 180px the three stop circles have '
         'merged into a tapering wedge; by 110px the animal is a silhouette with a bump on its nose. '
         '<b>This is a header and campaign mark, not an app icon</b> &mdash; the card mark is what '
         'goes on the home screen.</div></div>')

H.append('<h2>The colours</h2><div class="cell"><div class="swatch">')
for name, hexv, use in [("PINK", PINK, "body, tail"), ("CYAN", CYAN, "the night · dark grounds"),
                        ("TEAL", TEAL, "the night · light grounds"),
                        ("EYE", EYEDK, "eye ring and pupil"), ("WHITE", OFFW, "iris")]:
    H.append('<div style="display:flex;gap:8px;align-items:center;margin-right:22px">'
             '<div class="chip" style="background:%s;border:1px solid rgba(128,128,140,.3)"></div>'
             '<div class="cw"><b>%s</b><br>%s<br>%s</div></div>' % (hexv, name, hexv, use))
H.append('</div></div>')

H.append('</body></html>')
io.open(os.path.join(D, 'logos16.html'), 'w', encoding='utf-8').write('\n'.join(H))
print('written')
