# TheiaXR

AI standardized patient platform for OSCE practice in nursing and medicine. A formative practice tool, not a validated assessment.

## Run it locally (no API keys needed)

1. Install Node 26 or later and pnpm 10 (`npm install -g pnpm@10.34.9`).
2. `pnpm install`
3. `pnpm dev:mock`, then open http://127.0.0.1:5173
4. `pnpm test` runs the tests.

## Layout

- `apps/web`: Vite + React web app
- `apps/server`: Node + Fastify server (`/api/v1`)
- `packages/shared`: shared types and zod schemas
- `reference/`: read-only source material (see `reference/README.md`)
- `CLAUDE.md`: the master build prompt. `REUSE.md`: what is reused from the prototype and the old repo.
