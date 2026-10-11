# -*- coding: utf-8 -*-
"""TAGGING VENUES FROM IMAGES - what the method can and cannot give us.

The user's proposal, 2026-10-02: hold a reference set of images per factor, embed a venue's own
photos, score by similarity. ENRG/CROWD/MOVE/HERIT/POL from social images; TALK/AFFIL/FOOD need
reviews; GAMES/LIVE from the venue's own description.

The method is sound. Three things in it break on contact, and this file shows each one.
"""
import sys, random, math
sys.stdout.reconfigure(encoding="utf-8")
random.seed(4)

def line(c='-', n=100): print(c * n)
def head(t):
    print(); print('=' * 100); print(t); print('=' * 100)

# ============================================================ 1. WHO ACTUALLY NEEDS A TAG
head('1. THREE OF THOSE FACTORS NO LONGER REACH A VENUE')
print("""
  Since 2026-10-01 the identity factors do not touch venues at all. So of the ten named:

     ENRG   band, per hour      NEEDED - it is half of stage 1
     CROWD  band, per hour      NEEDED - the other half
     SCEN   fixed preference    NEEDED - and NOT on the list, though it is the single most
                                image-assessable field there is. SCEN *is* the look of the place.
     POL    fixed preference    NEEDED
     HERIT  fixed preference    NEEDED
     FOOD   fixed preference    NEEDED
     LIVE   fixed preference    NEEDED
     GAMES  fixed preference    NEEDED

     MOVE   identity factor     NOT NEEDED - no consumer since 2026-10-01
     TALK   identity factor     NOT NEEDED
     AFFIL  identity factor     NOT NEEDED

  So the work shrinks by three and grows by one, and the one it grows by is the easiest.
""")

# ============================================================ 2. SELECTION BIAS
head('2. SELECTION BIAS - every venue photographs well, and the mean cannot see it')
VENUES = [('a genuinely loud club', 88), ('a big loud bar', 72), ('a rooftop', 55),
          ('a quiet wine bar', 34), ('a daytime cafe', 22)]
N_PHOTOS = 40
def photos(true_enrg):
    """people post their BEST moment: photos skew toward the venue's peak, not its average"""
    out = []
    for _ in range(N_PHOTOS):
        moment = min(100, max(0, random.gauss(true_enrg, 18)))
        if random.random() < 0.55 + 0.004 * moment:      # the better it looks, the likelier it is posted
            out.append(min(100, moment + random.gauss(9, 5)))   # and posted at its best
    return out

print('%-24s %6s   %8s %8s   %8s' % ('venue', 'true', 'photos', 'MEAN', 'TOP-DECILE SHARE'))
line()
rows = []
for name, t in VENUES:
    ps = photos(t)
    mean = sum(ps) / len(ps)
    share = sum(1 for x in ps if x >= 80) / len(ps)
    rows.append((name, t, len(ps), mean, share))
    print('%-24s %6d   %8d %8.1f   %15.2f' % (name, t, len(ps), mean, share))
line()
sp_mean = max(r[3] for r in rows) - min(r[3] for r in rows)
sp_share = (max(r[4] for r in rows) - min(r[4] for r in rows)) * 100
print('spread the MEAN can see:          %.0f points' % sp_mean)
print('spread the TOP-DECILE SHARE sees: %.0f points (rescaled to 0-100)' % sp_share)
print()
print('  Every venue is posted at its best, so every MEAN drifts up and they compress toward each')
print("  other. Use the SHARE of a venue's photos that match the high-pole reference, not the")
print('  average similarity.** The bias is roughly constant across venues, so a share stays')
print('  comparable where a mean does not.')

# ============================================================ 3. THE CONFOUND
head('3. THE REAL RISK - a reference set that varies on the wrong thing')
print("""
  Suppose the ENRG-high references are all dark club photos and the ENRG-low references are all
  daylight cafe photos. The embedding does not learn ENERGY. It learns BRIGHTNESS.
""")
# each venue: (name, true energy, true brightness) - deliberately decorrelated in reality
TEST = [('club, dark',            88, 10), ('club, bright lighting', 85, 72),
        ('rooftop at sunset',     58, 78), ('basement wine bar',     32, 14),
        ('bright daytime cafe',   20, 88), ('candlelit restaurant',  26, 12)]

def score(v, use_confounded_refs):
    name, e, b = v
    if use_confounded_refs:
        return 0.25 * e + 0.75 * (100 - b)      # mostly reading darkness
    return 0.92 * e + 0.08 * (100 - b)          # references varied on everything but energy

print('%-24s %6s %6s   %12s %12s' % ('venue', 'ENRG', 'bright', 'CONFOUNDED', 'CONTROLLED'))
line()
for v in TEST:
    print('%-24s %6d %6d   %12.0f %12.0f' % (v[0], v[1], v[2], score(v, True), score(v, False)))
line()
def rank_err(conf):
    truth = sorted(TEST, key=lambda v: -v[1])
    got = sorted(TEST, key=lambda v: -score(v, conf))
    return sum(abs(truth.index(v) - got.index(v)) for v in TEST)
print('rank error against the truth:  confounded %d,  controlled %d' % (rank_err(True), rank_err(False)))
print()
print('  The confounded set calls a brightly-lit club calmer than a candlelit restaurant.')
print()
print('  THE RULE THAT PREVENTS IT: a reference set must vary on EVERYTHING EXCEPT the factor.')
print('  For ENRG-high you need a dark club AND a bright afternoon rave AND a lit-up wedding floor.')
print('  10-20 images per pole, deliberately mixed on time of day, colour, indoor/outdoor and')
print('  crowd. If every high reference shares an incidental property, that property is what gets')
print('  measured - and nothing downstream will reveal it, because the number will look fine.')

# ============================================================ 4. BANDS
head('4. THE THING IMAGES CANNOT GIVE YOU AT ALL - the band')
print("""
  Bands are hour-scoped: Depot 48 is e55 at 20:00 and e88 at 23:00. An image score is a property
  of a VENUE, not of an HOUR - and photo timestamps are when somebody POSTED, not when they were
  there. People post the next morning.

  So images give the AMPLITUDE and cannot give the SHAPE.

  Popular Times is the other way round: it is an honest hourly CROWD curve and says nothing about
  how hot the room feels.

  COMBINE THEM. Popular Times gives the shape, images give the ceiling:
""")
POP = {19: 0.22, 20: 0.35, 21: 0.55, 22: 0.78, 23: 0.95, 24: 1.00, 25: 0.80}   # Popular Times, normalised
for peak_img, label in ((88, 'Depot 48  (images say it peaks at 88)'),
                        (52, 'Ikk Punjab (images say it peaks at 52)')):
    base = peak_img * 0.45
    print('  %s' % label)
    cells = []
    for h in sorted(POP):
        e = base + (peak_img - base) * POP[h]
        cells.append('%02d:00 e%-3d' % (h, round(e)))
    print('     ' + '  '.join(cells))
    # collapse into 2-3 bands
    print('     -> bands: ', end='')
    bands, cur = [], None
    for h in sorted(POP):
        e = round(base + (peak_img - base) * POP[h])
        b = 'low' if e < base + (peak_img - base) * 0.45 else ('mid' if e < base + (peak_img - base) * 0.85 else 'high')
        if cur and cur[0] == b: cur[2] = h + 1; cur[3].append(e)
        else:
            cur = [b, h, h + 1, [e]]; bands.append(cur)
    print('  '.join('%02d:00-%02d:00 e%d' % (b[1], b[2], round(sum(b[3]) / len(b[3]))) for b in bands))
    print()
print('  That is a SEED, not an answer - energy does not track crowd perfectly, and a human has to')
print('  correct it. But it turns a blank field into a wrong-by-a-little one, and correcting 2-4')
print('  numbers is a different job from inventing them.')

# ============================================================ 5. ACCESS
head('5. THE HINGE THE USER NAMED - and it is worse and better than it looks')
print("""
  He is right that everything rests on the images being reachable. The honest position:

  INSTAGRAM HASHTAG SEARCH IS NOT A VIABLE BASE.
     The Graph API returns a business's own media only once THEY connect their account. Hashtag
     search is capped (a handful of hashtags per week, recent posts only, no engagement), and
     scraping is against terms and actively blocked. It is not something to build a database on.

  GOOGLE PLACES PHOTOS IS, AND IT IS AVAILABLE TODAY.
     The Places API returns user-submitted photos per venue under licence - fewer than Instagram,
     no hashtag needed, and legal to use. It also arrives in the SAME CALL as the rating, the
     review count and Popular Times, which are three other things the database already needs.

  SO THE DESIGN SHOULD ASSUME PLACES, NOT INSTAGRAM.
     It is one API for photos, crowd curve, rating, spread and review text - which is admission
     (section 1), the CROWD band, the ENRG seed and the FOOD signal from a single integration.
     Instagram becomes an enrichment for venues that connect their own account later, not the
     foundation.

  AND THE VENUE'S OWN MEDIA IS THE THIRD SOURCE, for GAMES and LIVE as the user says - a pool
  table or a stage is unmistakable in a photo and usually stated in the venue's own copy anyway.
""")

head('WHAT THIS LEAVES AS THE ACTUAL SOURCE TABLE')
print("""
  field          primary source                              confidence
  ------------   -----------------------------------------   ----------
  CROWD band     Popular Times, directly                     high - it is literally the number
  ENRG band      image amplitude x Popular Times shape        seed only, human-corrected
  SCEN           images, top-decile share                     high - it IS the look
  POL            images, top-decile share                     good
  HERIT          heritage lists + images (fabric vs styled)   good
  FOOD           review text + rating                         fair - quality is not visible
  LIVE           venue's own copy + the events feed           high
  GAMES          venue's own copy + images                    high - a pool table is a pool table
  MOVE/TALK/AFFIL  - not needed, no consumer -
""")
