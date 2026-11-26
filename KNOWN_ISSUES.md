# KNOWN_ISSUES.md

## Open

1. **The old repo's OpenAI key is still live on GitHub** (`Theia-XR/platform`, `backend/.env`, also in its git history). It was not copied here. Shreenik decided on 2026-11-25 not to revoke it for now (REUSE.md section 6). Anyone who can read the old repo can use it.
2. **No vision document.** `VISION.md` is a placeholder. The master prompt refers to it for the Scenario Studio.
3. **The CI workflow has not run yet.** It runs only once the branch is on GitHub and a pull request is opened.
4. **Node versions differ:** this computer has Node 26.13.1, while CI uses Node 24. `engines` requires Node 22 or later.
