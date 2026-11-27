# PROGRESS.md

## 2026-11-25: A2 (fill the new repo) on branch `a2-setup`

- Core files: `CLAUDE.md` (master prompt, unchanged), `VISION.md` (placeholder; no vision document was provided), `REUSE.md` (from A1).
- `reference/`: prototype, Ingram rubric, Saylor Lee SP script, the master prompt, and a cleaned copy of the old repo (`reference/old_repo/`, exclusions in `EXCLUDED.md`).
- pnpm monorepo: `apps/web` (Vite + React, shows "TheiaXR"), `apps/server` (Fastify, `GET /api/v1/health` returns `{ "ok": true }`), `packages/shared` (zod schema for the health reply).
- `pnpm dev:mock` starts web and server with no keys and no network. `pnpm test` runs one smoke test. CI runs `pnpm test` on pull requests.
- No agent, patient, scoring or voice feature yet. Those start in A3.

## 2026-11-26: A3 (write the plan) on branch `a3-plan`

- `PLAN.md`: architecture, file tree, dependencies and why, data model, licence notes, cost assumptions, risks, and open questions (5 for the review, the rest listed).
- Follows the master prompt on the Google Doc's second tab (14 Ingram sections, 94.5 points), which is newer than the repo's `CLAUDE.md`.
- No application code. No packages installed. No paid service used; cost $0.
- Waiting for Shreenik and Mohsen to approve.
