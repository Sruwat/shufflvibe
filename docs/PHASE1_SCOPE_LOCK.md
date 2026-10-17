# SHUFFL Phase 1 — MVP scope lock

Phase 1 freezes the contract that the release build is allowed to ship.

## Locked release contract

- Release scope: `mvp`.
- Venue pipeline: locked with `VENUE_PIPELINE_LOCKED=1`.
- Public venue source: the published venue API and locked catalogue.
- Opening hours: fetched at display time.
- Google reviews, coordinates, hours, address and photos: never persisted as durable catalogue fields.
- Gold campaign: post-MVP and disabled.
- Messages SHUFFL/group-learning/insights paths: excluded from MVP.
- Automatic outing-plan generation: excluded from MVP; the intended path is shape → open venue options → user/host selection → locked plan.

## Runtime guards

- The backend exposes `/v1/release` and reports the locked catalogue and disabled post-MVP features.
- Production mobile builds require `EXPO_PUBLIC_RELEASE_SCOPE=mvp`.
- Production mobile builds require `EXPO_PUBLIC_API_URL`; they cannot silently fall back to `DemoService`.
- Local development may use the fixture service explicitly when no API URL is configured.

## Coverage decision

The current locked catalogue contains 4,429 records and 43 admitted/published venues. This is
usable for local/internal MVP testing, but it is below the approximately 360 admitted NCR target
described in the product specification. Coverage expansion remains a later data-quality gate and
must not be confused with the runtime catalogue lock.

## Deferred scope

Gold screens 20–26 and Plan Insights screen 54 are explicitly post-MVP. Their assets may remain in
the repository as reference material, but they must not be required by the MVP navigation.
