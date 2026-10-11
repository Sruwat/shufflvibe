# -*- coding: utf-8 -*-
"""SHUFFL VENUE PIPELINE - discovery to database, in one run.

    python pipeline.py discover --key KEY                  # South Delhi, 20 districts (~$3.50)
    python pipeline.py discover --key KEY --catchment ncr  # all 32 districts   (~$5.60)
    python pipeline.py enrich   --key KEY                  # one call each    (~$0.025 ea)
    python pipeline.py build                               # no API: admit, score, gate
    python pipeline.py --help

Everything it STORES is an ID or our own derived data, which is what the Google Maps Platform
terms permit (VENUE_DATABASE_V1.md section 4a). Display data is re-fetched live by the app.

Outputs
    cache/places/<place_id>.json   raw responses, so a re-run costs nothing
    venues.json                    the database
    gold_list.json                 every slot the evidence could not reach
    human_pass.csv                 the two columns no API provides

Two fields no API gives, by design, not oversight:
    operator_class   guessed from brand + address, flagged where uncertain -> human_pass.csv
    fitout_years     a glance at the photos, ~3 seconds a venue          -> human_pass.csv
"""
import sys, os, json, csv, time, argparse, urllib.request, urllib.error, statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import lexicon as LEX
except Exception:
    LEX = None

API = 'https://places.googleapis.com/v1/places'
CACHE = 'cache/places'

DETAIL_FIELDS = (
    'id,displayName,formattedAddress,location,types,primaryType,primaryTypeDisplayName,'
    'rating,userRatingCount,priceLevel,priceRange,regularOpeningHours,businessStatus,'
    'editorialSummary,generativeSummary,reviews,liveMusic,goodForWatchingSports,'
    'outdoorSeating,reservable,goodForGroups,servesCocktails,servesWine,servesBeer,'
    'servesDinner,servesBrunch,servesCoffee,servesDessert,servesVegetarianFood')

# ---------------------------------------------------------------- what to look for, and where
# ---------------------------------------------------------------- the catchment
# TWO LISTS, and `--catchment` picks one. South Delhi is the default because that is what the
# first database pass covers; NCR is the destination (MVP_INSTRUCTIONS section 2.3, ~360 venues).
# Districts may overlap - duplicates are dropped on place_id, so over-covering costs one call,
# never a duplicate row.

SOUTH_DELHI = [
    ('Hauz Khas Village',      28.5535, 77.1940,  800), ('Deer Park / Hauz Khas', 28.5555, 77.2010, 700),
    ('Safdarjung Enclave',     28.5620, 77.1930,  900), ('Green Park & SDA',   28.5590, 77.2010,  900),
    ('Panchsheel Park',        28.5420, 77.2160,  700), ('Malviya Nagar',      28.5380, 77.2060,  900),
    ('Saket',                  28.5245, 77.2100, 1200), ('Mehrauli / Qutub',   28.5150, 77.1800, 1500),
    ('Vasant Kunj',            28.5200, 77.1550, 1500), ('Vasant Vihar',       28.5600, 77.1600,  900),
    ('Aerocity',               28.5540, 77.1200, 1200), ('Defence Colony',     28.5720, 77.2300,  800),
    ('Lajpat Nagar',           28.5670, 77.2430,  900), ('South Extension',    28.5700, 77.2220,  800),
    ('Greater Kailash 1',      28.5500, 77.2400,  900), ('Greater Kailash 2',  28.5330, 77.2420,  900),
    ('Kailash Colony',         28.5555, 77.2420,  700), ('Nehru Place',        28.5490, 77.2500,  900),
    ('Kalkaji',                28.5450, 77.2580,  900), ('Chittaranjan Park',  28.5370, 77.2490,  900),
]

# everything South Delhi does not cover. NCR = SOUTH_DELHI + this.
REST_OF_NCR = [
    ('Connaught Place',        28.6315, 77.2167, 1200), ('Khan Market',        28.6000, 77.2270,  600),
    ('Rajouri Garden',         28.6450, 77.1200, 1200), ('Punjabi Bagh',       28.6700, 77.1300, 1200),
    ('Cyber Hub Gurugram',     28.4950, 77.0890,  800), ('Sector 29 Gurugram', 28.4670, 77.0650,  900),
    ('Golf Course Rd Gurugram',28.4420, 77.0900, 2000), ('MG Road Gurugram',   28.4790, 77.0800, 1200),
    ('Sector 15 Gurugram',     28.4600, 77.0400, 1200), ('Noida Sector 18',    28.5700, 77.3250, 1200),
    ('Noida Sector 104',       28.5400, 77.3500, 1500), ('Noida Garden Galleria',28.5080,77.3900,1200),
]

CATCHMENTS = {'south-delhi': SOUTH_DELHI, 'ncr': SOUTH_DELHI + REST_OF_NCR}
DISTRICTS = SOUTH_DELHI                  # set by --catchment at run time

SEARCH_TYPES = ['bar', 'night_club', 'pub', 'restaurant', 'cafe']

# ---------------------------------------------------------------- operator classification
HOTELS = ('hotel', 'the lalit', 'shangri', 'oberoi', 'taj ', 'itc ', 'hyatt', 'jw marriott',
          'marriott', 'leela', 'roseate', 'andaz', 'pullman', 'radisson', 'novotel', 'westin',
          'sheraton', 'crowne plaza', 'le meridien', 'holiday inn', 'lemon tree', 'claridges')
CHAINS = ('social', 'imperfecto', 'lord of the drinks', 'beer cafe', 'cafe delhi heights',
          'barbeque nation', 'chili\'s', 'tgi', 'hard rock', 'farzi', 'nik baker', 'chaayos',
          'starbucks', 'blue tokai', 'third wave', 'costa', 'cafe coffee day', 'pvr', 'smaaash',
          'molecule', 'rockman', 'warehouse cafe', 'ardor', 'local', 'raasta', 'prankster',
          'downtown', 'striker', 'soi 7', 'wine company', 'pirates of grill', 'biryani blues')
GROUPS  = ('olive', 'sidecar', 'pco', 'piano man', 'depot 48', 'perch', 'qla', 'diablo',
           'dear donna', 'bohca', 'summer house', 'ek bar', 'jamun', 'lavaash', 'comorin',
           'indian accent', 'bo tai', 'toy room', 'privee', 'kitty su', 'dirty jungle')

def classify_operator(name, addr, types):
    s = ((name or '') + ' ' + (addr or '')).lower()
    if any(h in s for h in HOTELS):  return 'hotel', 'high'
    if any(c in s for c in CHAINS):  return 'chain', 'high'
    if any(g in s for g in GROUPS):  return 'group', 'high'
    return 'unknown', 'needs-human'          # -> human_pass.csv

# ---------------------------------------------------------------- HTTP, with retry and cache
def _req(url, key, body=None, mask=None, tries=4):
    last = None
    for a in range(tries):
        try:
            r = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                       method='POST' if body else 'GET')
            r.add_header('X-Goog-Api-Key', key); r.add_header('Content-Type', 'application/json')
            if mask: r.add_header('X-Goog-FieldMask', mask)
            with urllib.request.urlopen(r, timeout=25) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            body_txt = e.read().decode('utf-8', 'replace')[:200]
            if e.code in (429, 500, 502, 503):           # transient: back off
                last = '%s %s' % (e.code, body_txt); time.sleep(2 ** a); continue
            raise RuntimeError('HTTP %s %s' % (e.code, body_txt))
        except Exception as e:
            last = str(e); time.sleep(2 ** a)
    raise RuntimeError('gave up after %d tries: %s' % (tries, last))

def cached_details(pid, key):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, pid + '.json')
    if os.path.exists(f):
        return json.load(open(f, encoding='utf-8')), True        # free
    d = _req('%s/%s' % (API, pid), key, None, DETAIL_FIELDS)
    json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
    return d, False

# ---------------------------------------------------------------- stage: discover
def discover(key, out='candidates.json', dry=False, districts=None):
    districts = districts or DISTRICTS
    calls = len(districts) * len(SEARCH_TYPES)
    print('%d districts x %d types = %d Nearby Search calls, ~$%.2f'
          % (len(districts), len(SEARCH_TYPES), calls, calls * 0.035))
    if dry: return
    seen, rows = set(), []
    for dn, lat, lon, rad in districts:
        for ty in SEARCH_TYPES:
            body = {'includedTypes': [ty], 'maxResultCount': 20,
                    'locationRestriction': {'circle': {'center': {'latitude': lat, 'longitude': lon},
                                                       'radius': float(rad)}}}
            try:
                j = _req(API + ':searchNearby', key, body,
                         'places.id,places.displayName,places.formattedAddress,places.types')
            except Exception as e:
                print('  %-24s %-12s ERROR %s' % (dn, ty, str(e)[:50])); continue
            got = j.get('places') or []
            for p in got:
                if p['id'] in seen: continue
                seen.add(p['id'])
                rows.append(dict(place_id=p['id'], name=p.get('displayName', {}).get('text', ''),
                                 address=p.get('formattedAddress', ''), district=dn,
                                 found_as=ty, types=p.get('types', [])))
            print('  %-24s %-12s %3d  (total %d)' % (dn, ty, len(got), len(rows)))
            time.sleep(0.12)
    json.dump(rows, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('\n%d unique venues -> %s' % (len(rows), out))

# ---------------------------------------------------------------- stage: enrich
def enrich(key, src='candidates.json', out='enriched.json', limit=0, dry=False):
    cands = json.load(open(src, encoding='utf-8'))
    if limit: cands = cands[:limit]
    todo = [c for c in cands if not os.path.exists(os.path.join(CACHE, c['place_id'] + '.json'))]
    print('%d candidates, %d already cached, %d to fetch, ~$%.2f'
          % (len(cands), len(cands) - len(todo), len(todo), len(todo) * 0.025))
    if dry: return
    out_rows, hit = [], 0
    for i, c in enumerate(cands, 1):
        try:
            d, was_cached = cached_details(c['place_id'], key)
            hit += was_cached
            out_rows.append(dict(c, detail=d))
            if i % 25 == 0 or i == len(cands):
                print('  %4d/%d  (%d from cache)' % (i, len(cands), hit))
        except Exception as e:
            print('  %4d  %-30s ERROR %s' % (i, c['name'][:29], str(e)[:60]))
        if not was_cached: time.sleep(0.1)
    json.dump(out_rows, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('\n%d enriched -> %s' % (len(out_rows), out))

# ---------------------------------------------------------------- stage: build (no API)
COARSE = [('night_club', 'club'), ('bar', 'bar / pub'), ('pub', 'bar / pub'),
          ('cafe', 'cafe'), ('restaurant', 'restaurant')]

def coarse_type(d):
    t = set(d.get('types') or [])
    if 'night_club' in t: return 'club'
    if ('bar' in t or 'pub' in t) and d.get('liveMusic'): return 'live room'
    if 'bar' in t or 'pub' in t: return 'bar / pub'
    if 'cafe' in t: return 'cafe'
    if 'restaurant' in t: return 'restaurant'
    return 'other'

# ---------------------------------------------------------------- the venue's own statements
# A structured field is the venue SAYING SO on its own listing. Where it is present it beats any
# amount of keyword inference; where it is absent it says nothing at all. Added 2026-10-05 after
# the review-only corpus was found to be guessing LIVE from whether five reviewers mentioned a band.
SERVES_FIELDS = ('servesDinner', 'servesBrunch', 'servesDessert', 'servesVegetarianFood',
                 'servesCocktails', 'servesWine', 'servesBeer', 'servesCoffee')
FOOD_FIELDS = ('servesDinner', 'servesBrunch', 'servesDessert', 'servesVegetarianFood')


def structured_layer(row):
    """Returns (overrides, not_specialised, why) - VENUE_DATABASE_V1.md section 3b's three states.

    `not_specialised` is a FLAG, never a zero: it says this is not what the place is for, which is a
    different claim from measuring it and finding it poor.
    """
    ov, absent, why = {}, [], []
    if row.get('liveMusic') is True:
        ov['LIVE'] = 85
        why.append('liveMusic=true -> LIVE 85, the venue lists it')
    elif row.get('liveMusic') is False:
        absent.append('LIVE')
        why.append('liveMusic=false -> LIVE not specialised')
    if row.get('goodForWatchingSports') is True:
        ov['FOCUS'] = 78
        why.append('goodForWatchingSports=true -> FOCUS 78, a screen is a main event')
    # FOOD: the serves* family proves ABSENCE well and presence badly. Every bar "serves dinner";
    # that says a kitchen exists, not that food is the point. So only the all-false case is used.
    served = [row.get('serves', {}).get(k) for k in FOOD_FIELDS]
    if served and all(v is False for v in served if v is not None) and any(v is not None for v in served):
        absent.append('FOOD')
        why.append('every serves* food field is false -> FOOD not specialised')
    if row.get('outdoorSeating') is True:
        ov['SCEN_FLOOR'] = 60
        why.append('outdoorSeating=true -> SCEN floored at 60, a terrace is a scene asset')
    return ov, absent, why


# the lexicon's priors are keyed by SHUFFL venue type; coarse_type is keyed by Google's. Map them,
# or every factor falls through the no-prior path and returns extremes off two keyword hits.
PRIOR_KEY = {'club': 'club', 'bar / pub': 'big loud bar', 'live room': 'live room',
             'restaurant': 'buzzy restaurant', 'cafe': 'cafe', 'other': 'big loud bar'}

DOOR_WORDS = ('entry', 'bouncer', 'guestlist', 'guest list', 'stag', 'couple', 'door policy',
              'rules for entry', 'attitude')

def sentiment_spread(reviews):
    """Substitute for rating_sd, which no free source provides (section 5.0.1).
    ROUTED FIRST (entry 145): door complaints are evidence about the door, not quality, and
    counting them as inconsistency penalises exactly the selective venues the filter wants."""
    kept = [r for r in reviews
            if not any(w in ((r.get('text') or {}).get('text') or '').lower() for w in DOOR_WORDS)]
    sc = [r.get('rating') for r in kept if r.get('rating')]
    return round(st.pstdev(sc), 2) if len(sc) >= 3 else None

VOLUME_FLOOR, SD_CEILING, MEAN_PERCENTILE = 200, 0.85, 0.35
OPERATOR_OK = {'chain', 'group', 'hotel', 'indie-pro'}

def mean_floors(rows):
    """CORRECTED 2026-10-04: the mean floor is a percentile WITHIN TYPE, not an absolute 4.0.
    A real pass found Privee (a well-known club, 1,380 reviews) failing on 3.6, because clubs
    collect door complaints restaurants do not - so an absolute floor is a TYPE bar."""
    out = {}
    for ct in set(r['coarse_type'] for r in rows):
        peers = sorted(r['rating'] for r in rows if r['coarse_type'] == ct and r.get('rating'))
        out[ct] = peers[int(len(peers) * MEAN_PERCENTILE)] if len(peers) >= 8 else 4.0
    return out

def slot_gate(row):
    """Section 2a0: a slot fills only when a source NAMES ITS TIME."""
    filled, gold = [], []
    hrs = ((row.get('hours') or {}).get('weekdayDescriptions')) or []
    if hrs:
        filled += [dict(days='all', frm=12, to=18, src='structured: hours + type'),
                   dict(days='all', frm=18, to=22, src='structured: hours + type')]
    else:
        gold.append(dict(days='all', frm=12, to=22, why='no opening hours'))
    late = any(('1:' in h or '2:' in h or '3:' in h) and 'AM' in h.upper() for h in hrs)
    if late:
        gold += [dict(days='fri-sun', frm=22, to=26, why='open late; nothing names what it becomes'),
                 dict(days='mon-thu', frm=22, to=26, why='open late; nothing names what it becomes')]
    if row.get('liveMusic'):
        gold.append(dict(days='?', frm=20, to=24,
                         why='liveMusic is true but no API gives the SCHEDULE - see section 2a1'))
    return filled, gold

def build(src='enriched.json'):
    raw = json.load(open(src, encoding='utf-8'))
    rows = []
    for r in raw:
        d = r['detail']
        if d.get('businessStatus') not in (None, 'OPERATIONAL'):
            continue
        name = (d.get('displayName') or {}).get('text') or r['name']
        addr = d.get('formattedAddress') or r.get('address')
        op, conf = classify_operator(name, addr, d.get('types'))
        texts = [((rv.get('text') or {}).get('text') or '') for rv in (d.get('reviews') or [])]
        rows.append(dict(
            place_id=r['place_id'], name=name, district=r.get('district'), address=addr,
            coarse_type=coarse_type(d), rating=d.get('rating'), reviews=d.get('userRatingCount'),
            price=d.get('priceLevel'), hours=d.get('regularOpeningHours'),
            liveMusic=d.get('liveMusic'), outdoorSeating=d.get('outdoorSeating'),
            goodForWatchingSports=d.get('goodForWatchingSports'), reservable=d.get('reservable'),
            editorial=(d.get('editorialSummary') or {}).get('text'),
            generative=(d.get('generativeSummary') or {}).get('overview', {}).get('text'),
            serves=dict((k, d.get(k)) for k in SERVES_FIELDS if d.get(k) is not None),
            review_texts=texts, sentiment_sd=sentiment_spread(d.get('reviews') or []),
            operator_class=op, operator_confidence=conf, fitout_years=None))
    floors = mean_floors(rows)
    gold, human = [], []
    for row in rows:
        f = []
        if (row['reviews'] or 0) < VOLUME_FLOOR: f.append('volume %s' % row['reviews'])
        fl = floors.get(row['coarse_type'], 4.0)
        if (row['rating'] or 0) < fl: f.append('mean %.1f < %.1f (%s floor)' % (row['rating'] or 0, fl, row['coarse_type']))
        if row['operator_class'] not in OPERATOR_OK and row['operator_confidence'] != 'needs-human':
            f.append('operator %s' % row['operator_class'])
        if row['sentiment_sd'] is not None and row['sentiment_sd'] > SD_CEILING:
            f.append('spread %.2f' % row['sentiment_sd'])
        row['admit_fails'] = f; row['admitted'] = not f
        # ---- the corpus. The editorial and generative summaries are the densest sentences the
        # call returns - "sophisticated restaurant with a terrace, specialising in tapas" carries
        # POL, SCEN and FOOD in fourteen words - and we were paying for them and discarding them.
        corpus = list(row['review_texts'])
        for extra in (row.get('editorial'), row.get('generative')):
            if extra: corpus.append(extra)
        row['corpus_size'] = len(corpus)
        base, why = {}, []
        if LEX and corpus:
            for fac in ['ENRG','CROWD','TALK','MOVE','FOCUS','FOOD','LIVE','POL','SCEN','HERIT','GAMES']:
                sc, n, _, _ = LEX.score(corpus, fac, PRIOR_KEY.get(row['coarse_type']))
                if sc is not None: base[fac] = sc
        # ---- then the venue's own fields, which win. TALK, MOVE and FOCUS are kept as DESCRIPTIVE
        # tags only - selection never reads them (VENUE_DATABASE_V1.md section 0).
        ov, absent, swhy = structured_layer(row)
        for k, v in ov.items():
            if k == 'SCEN_FLOOR':
                if base.get('SCEN', 0) < v: base['SCEN'] = v
            else:
                base[k] = v
        for k in absent:
            base.pop(k, None)
        row['base'] = base
        row['not_specialised'] = absent
        row['base_source'] = swhy + ['lexicon over %d texts' % len(corpus)]
        sf, sg = slot_gate(row)
        row['slots_filled'], row['slots_gold'] = sf, sg
        if row['admitted']:
            for s in sg: gold.append(dict(venue=row['name'], place_id=row['place_id'], **s))
        if row['admitted'] and (row['operator_confidence'] == 'needs-human'
                                or row['fitout_years'] is None):
            human.append(dict(place_id=row['place_id'], name=row['name'], district=row['district'],
                              address=row['address'], coarse_type=row['coarse_type'],
                              operator_class='', fitout_years=''))
    json.dump(rows, open('venues.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump(gold, open('gold_list.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    with open('human_pass.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(human[0].keys()) if human else
                           ['place_id','name','district','address','coarse_type','operator_class','fitout_years'])
        w.writeheader(); w.writerows(human)
    adm = sum(1 for r in rows if r['admitted'])
    print('mean floors by type: ' + ', '.join('%s %.1f' % (k, v) for k, v in sorted(floors.items())))
    print('%d venues, %d admitted, %d gold slots, %d rows need a human'
          % (len(rows), adm, len(gold), len(human)))
    print('-> venues.json, gold_list.json, human_pass.csv')

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('stage', choices=['discover', 'enrich', 'build'])
    ap.add_argument('--key'); ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--catchment', choices=sorted(CATCHMENTS), default='south-delhi',
                    help='which district list to search (default: south-delhi)')
    a = ap.parse_args()
    if a.stage in ('discover', 'enrich') and not a.key and not a.dry_run:
        sys.exit('--key is required for %s (or use --dry-run to see the cost)' % a.stage)
    if a.stage == 'discover':
        print('catchment: %s' % a.catchment)
        discover(a.key, dry=a.dry_run, districts=CATCHMENTS[a.catchment])
    elif a.stage == 'enrich': enrich(a.key, limit=a.limit, dry=a.dry_run)
    else: build()

if __name__ == '__main__':
    main()
