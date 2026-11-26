# PROGRESS.md

## 2026-11-25: A2 (fill the new repo) on branch `a2-setup`

- Core files: `CLAUDE.md` (master prompt, unchanged), `VISION.md` (placeholder; no vision document was provided), `REUSE.md` (from A1).
- `reference/`: prototype, Ingram rubric, Saylor Lee SP script, the master prompt, and a cleaned copy of the old repo (`reference/old_repo/`, exclusions in `EXCLUDED.md`).
- pnpm monorepo: `apps/web` (Vite + React, shows "TheiaXR"), `apps/server` (Fastify, `GET /api/v1/health` returns `{ "ok": true }`), `packages/shared` (zod schema for the health reply).
- `pnpm dev:mock` starts web and server with no keys and no network. `pnpm test` runs one smoke test. CI runs `pnpm test` on pull requests.
- No agent, patient, scoring or voice feature yet. Those start in A3.
