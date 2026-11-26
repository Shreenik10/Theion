# EXCLUDED.md: what was left out of this copy of the old repo

Source: `Theia-XR/platform` (local clone at `C:\Users\Shreenik\Documents\GitHub\platform`, branch `main`, last commit 2025-09-12). Copied on 2026-11-25 for ticket A2. The original repo was only read, never changed.

This copy is reference material only. Nothing in it runs. See `../README.md` and `../../REUSE.md`.

## Left out

| Path in old repo | Kind | Why |
|---|---|---|
| `.git/` | Git history | Not needed; the history also still contains `backend/.env` (below). |
| `.github/`, `CNAME` | GitHub and hosting | Do not exist in the old repo. Checked; nothing to leave out. |
| `backend/.env` | Secret | Holds an OpenAI API key (`OPENAI_API_KEY`). Never copied; value never read. See REUSE.md section 6. |
| `osce-simulator/cookies.txt` | Credentials | Browser cookie file; likely holds session tokens. Not opened. |
| `osce-simulator/backend/osce_simulator.db` | Data | SQLite database that may hold user accounts. Not opened. |
| `osce-simulator/backend/.osce_data/` (52 JSON files) | Data | Saved practice conversations and evaluations tied to user ids. Treated as personal data. |
| `osce-simulator/backend/app/core/auth.py` | Credentials | Hard-codes default usernames and passwords for named team members. Not needed (REUSE.md leaves the login code out). |
| `osce-simulator/backend/app/main.py`, line 102 | Credentials (one comment) | The file is copied, but a comment naming a default username and password was replaced with `[REDACTED for TheiaXR reference copy]`. This is the only edit made to any copied file. |
| `osce-simulator/docker-compose.yml`, `docker-run.sh`, `DOCKER_README.md` | Deployment | Docker hosting files. |
| `osce-simulator/backend/Dockerfile`, `osce-simulator/frontend/Dockerfile`, `osce-simulator/frontend/nginx.conf` | Deployment | Container and web-server hosting files. |
| `osce-simulator/db/init/001_init.sql` | Deployment | Postgres start-up script mounted only by `docker-compose.yml`. |
| `osce-simulator/run.py`, `osce-simulator/run.sh` | Deployment / run scripts | Start scripts for the old stack; REUSE.md section 3 leaves them out with the Docker files. |
| `osce-simulator/frontend/public/Saylor Lee.png` | Image, unknown source | Source and licence unknown; could be a real person's likeness, which the master prompt forbids (8.11). |
| `osce-simulator/frontend/public/videos/Tutorial.mov` (9.7 MB) | Video, unknown content | Source, licence and content unknown (may show real people or accounts); large binary. |
| `.DS_Store` (2 files) | macOS system files | No content. |

## Checked and kept

- Placeholder passwords such as `"hashed_password"` and made-up `@university.edu` emails in seed data, tests and `backend/app/models/README.md`. These are test fixtures, not real accounts.
- `osce-simulator/backend/app/core/config.py` reads `OPENAI_API_KEY` from the environment; it contains no key.
- `osce-simulator/docs/screenshots/*.png`: screenshots of the old app with made-up test content.
- `osce-simulator/docs/rubrik/OSCE_rubric.pdf` and `osce-simulator/docs/saylor_lee/Saylor_Lee.docx`: also copied to `reference/ingram_rubric/` and `reference/saylor_lee/`.
