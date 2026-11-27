# KNOWN_ISSUES.md

## Open

1. **The old repo's OpenAI key is still live on GitHub** (`Theia-XR/platform`, `backend/.env`, also in its git history). It was not copied here. Shreenik decided on 2026-11-25 not to revoke it for now (REUSE.md section 6). Anyone who can read the old repo can use it.
2. **No vision document.** `VISION.md` is a placeholder. The master prompt refers to it for the Scenario Studio.
3. **The CI workflow has not run yet.** It runs only once the branch is on GitHub and a pull request is opened.
4. ~~Node versions differ.~~ Resolved 2026-11-26: Node 26 everywhere (`.nvmrc`, CI, `engines`).
5. **The Claude Docs copy of "TheiaXR Build Plan and Tickets" (16 November) is out of date.** The Google Doc is the current plan and master prompt; `CLAUDE.md` was synced to it on 2026-11-26. Retire or update the Claude Docs copy so nobody builds from it.
6. **No Anthropic API account yet.** Needed before A7. Steps in PLAN.md section 10.3.
