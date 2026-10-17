# -*- coding: utf-8 -*-
"""Two sheets: the two surviving card marks, and the chameleon in colour."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

PINK, CYAN, GOLD = '#FF2E7A', '#24E0FF', '#FFC247'
INK, LITE, WHITE = '#060609', '#F4F2F8', '#FFFFFF'
INK2, OFFW, DEEP = '#121218', '#FBFAFF', '#1A1A22'

CSS = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap">
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
        display:flex;flex-direction:column;gap:10px}
  .cell.lite{background:#F4F2F8;border-color:rgba(0,0,0,.12)}
  .cell.lite .lab{color:#7A7686}.cell.lite .note{color:#55525F}
  .art{display:grid;place-items:center}
  .note{font-size:10.5px;color:#9C98AE;line-height:1.42}
  .g2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:16px}
  .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:16px}
  .g4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}
  .row{display:flex;gap:14px;margin-bottom:16px}
</style></head><body>
"""

# ================================================================= SHEET A
B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]


def disc(ring_c=INK, face=OFFW, dot=INK, r=40, ri=31):
    d = ''.join('<circle cx="%s" cy="%s" r="5.4"/>' % (x, y) for x, y in B8)
    return ('<circle r="%s" fill="%s"/><circle r="%s" fill="%s"/><g fill="%s">%s</g>'
            % (r, ring_c, ri, face, dot, d))


def mark(c1, t1, c2, t2, ring_c, face, dot, l1=None, l2=None, w=330):
    l1, l2 = l1 or c1, l2 or c2
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


A = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<title>SH:FFL — the two finalists</title>' + CSS,
     '<h1>SH:FFL &middot; the two that are left</h1>',
     '<p class="sub"><b>01</b> is the colour-forward one: the cards carry the brand pair and the disc '
     'stays white. <b>10a</b> is the inverse: the cards go neutral and all the colour moves into the '
     'letters and the lines, crossed so each card appears to be moving into the other one&rsquo;s '
     'colour. Both on the eight with the open centre.</p>',
     '<div class="g2">']
for lab, args, note in [
 ("01 · COLOURED CARDS", (PINK, WHITE, CYAN, WHITE, INK, OFFW, INK, None, None),
  "<b>Louder and more immediate.</b> Pink and cyan arrive before anything else and the white disc "
  "sits between them as the still point. The cost is that four hues and three values is a lot of "
  "mark to manage, and the disc competes with the cards for brightness."),
 ("10A · WHITE CARDS, CROSSED LINES", (OFFW, PINK, OFFW, CYAN, INK, INK2, OFFW, CYAN, PINK),
  "<b>Quieter and more deliberate.</b> The colour is in the type, where the name is, and the crossed "
  "lines are the only place the two colours meet — which reads as one event rather than two "
  "objects. Holds its contrast further down in size than 01."),
]:
    A.append('<div class="cell"><div class="lab">%s</div><div class="art" style="min-height:200px">\n'
             '%s</div><div class="note">%s</div></div>' % (lab, mark(*args), note))
A.append('</div><h2>On the light ground</h2><div class="g2">')
for lab, args, note in [
 ("01 ON LIGHT", (PINK, WHITE, CYAN, WHITE, DEEP, OFFW, DEEP, None, None),
  "<b>Cyan collapses toward black on paper-white</b> and the disc needs a dark ring added or it "
  "dissolves into the page. Two changes to the artwork, every time."),
 ("10A ON LIGHT", (DEEP, PINK, DEEP, CYAN, LITE, OFFW, DEEP, CYAN, PINK),
  "<b>The cards invert and nothing else moves.</b> The letters and the crossed lines keep their "
  "colours because both sit on the card rather than on the page. One change, and it is a swap."),
]:
    A.append('<div class="cell lite"><div class="lab">%s</div><div class="art" style="min-height:200px">\n'
             '%s</div><div class="note">%s</div></div>' % (lab, mark(*args), note))
A.append('</div><h2>The disc alone, at 72px, 44px and 32px</h2><div class="row">')
for lab, bg, fc, dc in [("01 · WHITE DISC", LITE, OFFW, INK),
                        ("01 · WHITE DISC ON INK", INK2, OFFW, INK),
                        ("10A · DARK DISC", LITE, INK2, OFFW),
                        ("10A · DARK DISC ON INK", INK2, INK2, OFFW)]:
    inner = ''
    for w, box in ((54, 72), (34, 44), (26, 32)):
        inner += ('<div style="width:%spx;height:%spx;border-radius:%spx;background:%s;'
                  'display:grid;place-items:center;border:1px solid rgba(128,128,140,.3)">'
                  '<svg viewBox="-44 -44 88 88" width="%s">%s</svg></div>'
                  % (box, box, box // 4, bg, w, disc(bg, fc, dc)))
    A.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="gap:9px;display:flex;align-items:center">%s</div></div>'
             % (lab, inner))
A.append('</div><p class="sub"><b>10a&rsquo;s dark disc with white circles survives further down</b> '
         '— white on near-black is the highest-contrast pair in the palette, and at 32px it is '
         'still a ring rather than a smudge. 01&rsquo;s white disc needs a surrounding dark ring to '
         'hold its edge, which it gets free on a dark ground and has to be drawn on a light one.</p>')
A.append('</body></html>')
io.open(os.path.join(D, 'logos12a.html'), 'w', encoding='utf-8').write('\n'.join(A))


# ================================================================= SHEET B
BODY = ("M88 170 C92 134 110 108 142 95 C174 82 200 76 220 72 C230 70 238 64 244 54 "
        "L252 30 L268 62 C276 72 286 80 296 86 L326 96 L300 110 L330 122 "
        "C308 138 282 148 252 153 C208 161 138 168 88 170 Z")
TAIL = ("M88 168 C62 168 46 180 46 196 C46 210 58 220 72 220 C84 220 93 212 93 201 "
        "C93 192 86 186 78 186 C72 186 68 190 68 195")
TONG = "M328 114 C364 114 380 102 396 86 C410 72 428 64 448 66"


def cham(body, tail, eye_ring, iris, pupil, tongue, grad=None, gid='g', outline=False):
    """grad = (from, to) paints the body as a gradient instead of a flat fill."""
    defs = ''
    fill = body
    if grad:
        defs = ('<defs><linearGradient id="%s" x1="0" y1="0" x2="1" y2="0.6">'
                '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
                '</linearGradient></defs>' % (gid, grad[0], grad[1]))
        fill = 'url(#%s)' % gid
    if outline:
        shape = ('<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linejoin="round"/>'
                 '<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
                 '<circle cx="268" cy="96" r="15" fill="none" stroke="%s" stroke-width="7"/>'
                 % (BODY, fill, TAIL, tail, eye_ring))
    else:
        shape = ('<path d="%s" fill="%s"/>'
                 '<path d="%s" fill="none" stroke="%s" stroke-width="15" stroke-linecap="round"/>'
                 '<circle cx="268" cy="96" r="18" fill="%s"/>'
                 '<circle cx="268" cy="96" r="10.5" fill="%s"/>'
                 '<circle cx="271" cy="96" r="4" fill="%s"/>'
                 % (BODY, fill, TAIL, tail, eye_ring, iris, pupil))
    night = ('<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
             '<circle cx="372" cy="100" r="8" fill="%s"/>'
             '<circle cx="410" cy="71" r="12" fill="%s"/>'
             '<circle cx="446" cy="66" r="17" fill="%s"/>'
             % (TONG, tongue, tongue, tongue, tongue))
    return ('<svg viewBox="30 20 440 215" width="%s">%s%s%s</svg>' % ('%s', defs, shape, night))


WAYS = [
 ("01 · GREEN · WHERE WE STARTED", None,
  dict(body='#3BD1A0', tail='#3BD1A0', eye_ring='#07372A', iris=GOLD, pupil='#07372A', tongue=PINK),
  "The literal reading. <b>Green says chameleon faster than any other colour</b>, and that is its "
  "whole case — it is also a colour the brand does not own, so the mark would be importing a "
  "hue the rest of the system never uses."),
 ("02 · PINK BODY, CYAN NIGHT", None,
  dict(body=PINK, tail=PINK, eye_ring='#12000A', iris=OFFW, pupil='#12000A', tongue=CYAN),
  "<b>Brand-correct and unmistakable.</b> The animal is the brand colour and the night it catches is "
  "the cyan. Loses the green cue, so it reads as a lizard first and a chameleon on second look."),
 ("03 · CYAN BODY, PINK NIGHT", None,
  dict(body=CYAN, tail=CYAN, eye_ring='#06222B', iris=OFFW, pupil='#06222B', tongue=PINK),
  "The reverse. <b>The night is now the brand colour, which is the right emphasis</b> — the "
  "product is the night, not the animal. But cyan is the colour that collapses on light grounds, and "
  "here it is the biggest shape in the mark."),
 ("04 · PINK TO CYAN", (PINK, CYAN),
  dict(body=PINK, tail=CYAN, eye_ring='#12000A', iris=OFFW, pupil='#12000A', tongue=OFFW),
  "<b>The animal is itself the colour change.</b> Pink at the tail, cyan at the head, and the night "
  "goes white so it stays separate from both. This is the only version where the gradient is doing "
  "conceptual work rather than decoration — the chameleon that is mid-shift."),
 ("05 · CYAN TO PINK", (CYAN, PINK),
  dict(body=CYAN, tail=PINK, eye_ring='#12000A', iris=OFFW, pupil='#12000A', tongue=OFFW),
  "The same gradient reversed, so the head is pink and the night leaves a pink mouth as a white "
  "line. <b>Weaker than 04</b>, because the brightest part of the animal now sits next to the "
  "brightest part of the night and they compete."),
 ("06 · INK BODY, PINK NIGHT", None,
  dict(body=DEEP, tail=DEEP, eye_ring=LITE, iris=PINK, pupil=DEEP, tongue=PINK),
  "Black animal, pink night, and <b>the eye is the only other colour in the mark</b>. The most "
  "restrained of the eight, and the one that would survive being printed by someone else. "
  "<b>Shown on light, because a black animal needs a light ground.</b>"),
 ("07 · WHITE BODY, PINK NIGHT", None,
  dict(body=OFFW, tail=OFFW, eye_ring=INK, iris=PINK, pupil=INK, tongue=PINK),
  "The inverse of 06. <b>Pairs with 10a</b> — same logic, neutral body with the colour carried "
  "by the thing that moves. On a light ground this one has to flip to 06."),
 ("08 · OUTLINE, PINK AND CYAN", None,
  dict(body=PINK, tail=PINK, eye_ring=PINK, iris=None, pupil=None, tongue=CYAN, outline=True),
  "<b>One weight throughout, so it strokes in a single pass</b> — a stamp, a neon tube, an "
  "embroidery file. The tail curl is the thinnest thing here and also the part doing the most work, "
  "so it is the first thing to fail when this gets small."),
]

B = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<title>SH:FFL — the chameleon in colour</title>' + CSS,
     '<h1>SH:FFL &middot; the chameleon, night as the tongue</h1>',
     '<p class="sub">Same drawing throughout &mdash; <b>the curl, the casque and the turret eye are '
     'the three cues that say chameleon</b>, and the tongue is the night skeleton: it rises left to '
     'right and the stop circles grow with the crowd, which is literally how the drawing works in the '
     'app. <b>Only the colour changes below</b>, which is the one thing a chameleon ought to be '
     'flexible about.</p><div class="g2">']
for i, (lab, grad, kw, note) in enumerate(WAYS):
    outline = kw.pop('outline', False)
    svg = cham(gid='cg%d' % i, grad=grad, outline=outline, **kw) % 420
    B.append('<div class="cell%s"><div class="lab">%s</div><div class="art" style="min-height:190px">'
             '%s</div><div class="note">%s</div></div>'
             % (' lite' if lab.startswith('06') else '', lab, svg, note))
B.append('</div><h2>Three of them on the light ground</h2><div class="g3">')
LT = [
 ("02 ON LIGHT", None, dict(body=PINK, tail=PINK, eye_ring='#12000A', iris=OFFW,
                            pupil='#12000A', tongue='#0E7E93'),
  "Pink holds exactly as it does on dark. <b>The night has to darken</b> — cyan at full "
  "strength is invisible here, so it drops to a deeper teal and stops matching the app."),
 ("06 ON LIGHT", None, dict(body=DEEP, tail=DEEP, eye_ring=LITE, iris=PINK, pupil=DEEP, tongue=PINK),
  "<b>Unchanged.</b> A black animal with a pink night needs nothing redrawn for either ground, which "
  "is the same property that makes 03 the safest of the card marks."),
 ("04 ON LIGHT", (PINK, CYAN), dict(body=PINK, tail=CYAN, eye_ring='#12000A', iris=DEEP,
                                    pupil=OFFW, tongue=DEEP),
  "The gradient survives, but <b>the cyan end fades out against the page</b> and the animal looks "
  "like it is dissolving at the head rather than changing colour."),
]
for i, (lab, grad, kw, note) in enumerate(LT):
    svg = cham(gid='lg%d' % i, grad=grad, **kw) % 330
    B.append('<div class="cell lite"><div class="lab">%s</div><div class="art" style="min-height:150px">'
             '%s</div><div class="note">%s</div></div>' % (lab, svg, note))
B.append('</div><h2>Small &mdash; 120px, 72px, 44px</h2><div class="row">')
for lab, grad, kw in [("02 · PINK", None, dict(body=PINK, tail=PINK, eye_ring='#12000A',
                                                    iris=OFFW, pupil='#12000A', tongue=CYAN)),
                      ("07 · WHITE", None, dict(body=OFFW, tail=OFFW, eye_ring=INK,
                                                   iris=PINK, pupil=INK, tongue=PINK)),
                      ("04 · GRADIENT", (PINK, CYAN), dict(body=PINK, tail=CYAN,
                                                                eye_ring='#12000A', iris=OFFW,
                                                                pupil='#12000A', tongue=OFFW))]:
    inner = ''
    for j, w in enumerate((120, 72, 44)):
        inner += ('<div style="display:grid;place-items:center">%s</div>'
                  % (cham(gid='s%s%d' % (lab[1], j), grad=grad, **kw) % w))
    B.append('<div class="cell" style="flex:1 1 0"><div class="lab">%s</div>'
             '<div class="art" style="gap:12px;display:flex;align-items:center;min-height:80px">%s'
             '</div></div>' % (lab, inner))
B.append('</div><p class="sub"><b>The night is the first thing to die.</b> By 72px the three stop '
         'circles have merged into a tapering wedge and by 44px the animal is a silhouette with a '
         'bump on its nose. <b>This is a header mark, not an app icon</b> — it needs width, and '
         'the card mark is what goes on the home screen.</p>')
B.append('</body></html>')
io.open(os.path.join(D, 'logos12b.html'), 'w', encoding='utf-8').write('\n'.join(B))
print('written both')
