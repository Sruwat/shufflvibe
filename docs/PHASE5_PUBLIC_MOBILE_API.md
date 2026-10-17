# Phase 5 — public and mobile venue API

## Public endpoints

```text
GET /v1/discovery
GET /v1/venues?query=&city=
GET /v1/venues/{venue_id}
GET /v1/venues/{venue_id}/live
GET /v1/venues/stop-options?energy=80&crowd=70&conversation=50&limit=10
```

The public catalogue only includes venues that are both eligible and published.
The detail endpoint returns normalized SHUFFL data. The live endpoint returns
current Google display fields and always marks the response as non-persistent.

`stop-options` ranks normalized venues against requested SHUFFL factors and can
attach live Google hours, address, coordinates, rating, reviews, and photos for
the returned candidates. This live attachment is request-scoped and is never
written to MySQL.

## Mobile integration

`mobile/src/services.ts` now exposes:

- `getDiscovery()` for the published catalogue;
- `getVenue(venueId)` for normalized detail;
- `getStopOptions(target, options)` for ranked stop candidates.

The adapter maps canonical factors such as `food`, `live_music`, `politics`,
`scene`, and `heritage` to the mobile app's `FOOD`, `LIVE`, `POL`, `SCEN`, and
`HERIT` fields. If `EXPO_PUBLIC_API_URL` is absent, the existing demo service
continues to work.
