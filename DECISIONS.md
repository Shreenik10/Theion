# DECISIONS.md

Each entry: decision, alternatives considered, reason.

## 2026-11-25: A2 setup choices

**1. Reference material stays in `reference/`, not `_setup/`.**
- Alternatives: recreate `_setup/` as the ticket expects, then delete it.
- Reason: in A1 Shreenik decided to rename `_setup/` to `reference/` (REUSE.md section 7, decision 3). `CLAUDE.md` was copied from `reference/TheiaXR_Master_Prompt_ClaudeCode.md`, and there was no `_setup/` folder left to delete.

**2. Package versions are pinned exactly** (Vite 8.3.8, React 19.3.1, Fastify 5.12.8, zod 4.6.7, Vitest 5.1.2, TypeScript 7.0.2, pnpm 10.34.9), as current on npm on 2026-11-25.
- Alternatives: caret ranges (`^`).
- Reason: builds that can be reproduced on Siqi's and Addie's machines and in CI. The lockfile is committed.

**3. The shared package exports TypeScript source directly** (no build step).
- Alternatives: compile `packages/shared` to `dist/`.
- Reason: Vite and tsx both read TypeScript, so there's no build step to forget. This can be revisited if the Unity client ever needs generated artefacts (it will use the OpenAPI spec instead, section 8.10).

**4. Mock mode is a `--mock` flag (or `MOCK_MODE=1`) on the server; in mock mode the server does not read `.env`.**
- Alternatives: a separate `.env.mock` file.
- Reason: this guarantees that `pnpm dev:mock` never picks up a real key by accident, and it works the same on Windows and in CI.

**5. Agent model settings in `.env.example` are left blank.**
- Alternatives: fill in current Claude model ids.
- Reason: the ticket asks for no real values, and the master prompt says to check the Anthropic documentation for model names when they're first used (A3 or later).

**6. pnpm 10 was installed globally with `npm install -g pnpm@10.34.9`.**
- Alternatives: Corepack, which is not bundled with Node 26 on this computer.
- Reason: pnpm was not installed. pnpm 12 exists, but 10.x is the stable line used by `pnpm/action-setup` here, and the version is pinned in `packageManager`.
