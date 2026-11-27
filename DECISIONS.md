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

## 2026-11-26: A3 plan choices (proposed, pending approval)

**1. The Google Doc's master prompt is treated as current, not the repo's `CLAUDE.md`.**
- Alternatives: follow `CLAUDE.md` as written.
- Reason: the Google Doc (updated 20 November) has the A1 decisions (14-section rubric, SP script as source). `CLAUDE.md` still says 10 sections. PLAN.md open question 1 asks Shreenik to confirm.

**2. Agent hand-offs use structured outputs plus a second zod check, not forced tool calls.**
- Alternatives: forced `tool_choice`.
- Reason: current Opus and Sonnet models reject forced tool calls. A zod check on our side catches anything the API lets through.

**3. Plain TypeScript orchestration for the agent loop, no agent framework.**
- Alternatives: LangChain or similar (used in the old repo).
- Reason: fewer dependencies, and a short loop that Mohsen and Dr. Poenaru can read.

**4. Case packages live as JSON files in `scenarios/`; the database records versions and hashes.**
- Alternatives: cases only in the database.
- Reason: case changes become reviewable pull requests, and a session can prove which files it used.

**5. Candidate models: Haiku 5.5 for patient and synthetic student, Opus 5.5 for scenario, scorer and reviewer.**
- Alternatives: Sonnet 5.5 for the patient.
- Reason: speed and cost per turn. To be confirmed by the A8 safety test and A15 cost measurement (PLAN.md open question 3).

## 2026-11-26: answers at the A3 review (Shreenik)

**6. The Google Doc master prompt is the source; `CLAUDE.md` is synced to it.** Confirms decision 1 above. Five edits were made to `CLAUDE.md` (reference list, leveled scoring, both seed cases, M2). The Claude Docs copy of the plan is out of date.

**7. Patient starts on Haiku 5.5** and keeps it if it passes the A8 safety test. Confirms decision 5 for the patient.

**8. The AI scores Ingram section 14 (professionalism).**
- Alternatives: flag concerns only, for an educator to score.
- Reason: Shreenik's decision. It is a judged section with checked quotes, an educator can override it, and all scores are formative.

**9. Node 26 everywhere.**
- Alternatives: Node 24 (what CI used).
- Reason: Node 26 is the current long-term support line and is what the builders run. `.nvmrc` pins 26, CI reads it, and `engines` requires 26 or later.
