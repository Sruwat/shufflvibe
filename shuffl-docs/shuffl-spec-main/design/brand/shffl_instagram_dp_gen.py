# -*- coding: utf-8 -*-
"""Instagram display-picture cuts: the mark alone, and the full wordmark."""
import io, os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))

PINK, CYAN, INK, OFFW = '#FF2E7A', '#24E0FF', '#060609', '#FBFAFF'
B8 = [(round(18 * math.cos(math.radians(-90 + i * 45)), 2),
       round(18 * math.sin(math.radians(-90 + i * 45)), 2)) for i in range(8)]
DOTS = ''.join('<circle cx="%s" cy="%s" r="5.4"/>' % (x, y) for x, y in B8)

MARK = ('<g fill="%s">'
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
        % (PINK, CYAN, INK, OFFW, INK, DOTS))

SHELL = ('<!doctype html><html><head><meta charset="utf-8">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Bebas+Neue&display=swap">'
         '<style>html,body{margin:0;background:transparent}body{display:inline-block}'
         '</style></head><body>%s</body></html>')

# the mark alone, transparent, large
io.open(os.path.join(D, 'ig_mark.html'), 'w', encoding='utf-8').write(
    SHELL % ('<svg viewBox="-6 24 222 94" width="1800">%s</svg>' % MARK))

# the whole wordmark, transparent, large
FONT = "font-family:'Bebas Neue';letter-spacing:.14em"
wm = ('<svg viewBox="-10 16 518 108" width="2600">'
      '<text x="0" y="104" style="%s" font-size="102" fill="%s">SH</text>'
      '<g transform="translate(110,0)">%s</g>'
      '<text x="322" y="104" style="%s" font-size="102" fill="%s">FFL</text></svg>'
      % (FONT, OFFW, MARK, FONT, OFFW))
io.open(os.path.join(D, 'ig_wordmark.html'), 'w', encoding='utf-8').write(SHELL % wm)
print('written')
