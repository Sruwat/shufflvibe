# Architecture

`mobile/` is an Expo Router TypeScript client. `src/theme.ts` centralises visual tokens; `src/data.ts` holds stable demo fixtures; `src/algorithms.ts` holds local scoring/name/plan rules; Zustand holds journey state and TanStack Query is ready for API-backed resources. A future `ApiService` can replace the DemoService without changing screens.

`backend/` is a FastAPI service with Pydantic request contracts and an intentionally small endpoint boundary. SQLAlchemy/Alembic/PostgreSQL/PostGIS are the next persistence layer; the demo is intentionally backend-independent.
