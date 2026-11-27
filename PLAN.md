# PLAN.md: how TheiaXR will be built

Ticket A3. Written 2026-11-26 on branch `a3-plan`. No application code is written in this ticket.

**Done when (tracker):** PLAN.md covers the architecture, data model, dependencies, risks and open questions. Shreenik and Mohsen approve it.

**Sources this plan follows, in order of authority:**
1. The master prompt on the second tab of the Google Doc "TheiaXR Build Plan and Tickets" (updated 20 November 2026). It already has the 14-section Ingram rubric and the Saylor Lee SP script.
2. The TheiaXR Ticket Tracker sheet (37 tickets, A1 to B16).
3. The decisions Shreenik made in A1 (`REUSE.md` section 7).

Shreenik confirmed on 2026-11-26 that the Google Doc is the current master prompt. `CLAUDE.md` was synced to it in this ticket (14 Ingram sections, 94.5 points, SP script as the source). The Claude Docs copy of "TheiaXR Build Plan and Tickets" (16 November) is older still, and should not be used.

---

## 1. In short (for a clinician)

- **One server does all the thinking.** The case, the patient's answers, the timer, the scoring and the feedback all run on one server. The browser (and later the Quest headset) only shows things and sends what the learner says or clicks. A session played on desktop and one played on Quest produce the same record.
- **Each case is a folder of data files, not code.** Robert Tremblay and Saylor Lee each become a "scenario package": facts, behaviour, exam findings, rubric. A checker rejects any file with a mistake before it can be used. Editing a case makes a new version; old sessions keep the version they used.
- **The patient can only say what it has been allowed to say.** Each learner question goes through two steps. First, a small, fast model decides which facts the question legitimately asks for. Then, a second call writes the reply, and that call only sees facts already revealed plus the newly allowed ones. Exam and test results never come from the AI; they come straight from the case file.
- **Scoring is separate from the patient.** Some rubric items are counted by plain code (was this fact asked? was this action done?). Others are judged by a strong model, which must quote the transcript. The server checks every quote. If the quote isn't in the transcript, the item is not met.
- **Five agents, each with one job, passing checked files.** Scenario, patient, evaluation and feedback, synthetic student, educator reviewer. They never chat with each other. Their instructions are plain text files in `agents/`, which Dr. Poenaru reviews.
- **Everything runs free in mock mode.** Every AI, speech and video service has a stand-in that needs no key and no network. All automated tests use the stand-ins. Real Claude calls start in A7 (patient), and only with Shreenik's approval of the spending cap.
- **What changes from the master prompt:** nothing in the stack. Three technical facts about the current Claude models shape the design (section 4.3). Shreenik's answers from the review are in section 10.1. One item is still open: getting an Anthropic API account before A7.

How to review this plan in 5 steps:
1. Read section 1 (this one) and section 10 (questions).
2. Look at the picture in section 2.1 and the turn walkthrough in 2.3.
3. Skim the data model in section 5. Each session must be traceable to its exact case, rubric and agent versions.
4. Read the risks in section 9.
5. Check the answers in section 10.1, then approve or reject the ticket. Mohsen reviews sections 2 to 6.

---

## 2. Architecture

### 2.1 The parts

```
                 Learner / educator
                        |
     +------------------+-------------------+
     |                                      |
 apps/web (browser)                 apps/quest (Unity, from B13)
 shows the station, sends text/      same API, same events
 audio, plays replies
     |                                      |
     +--------------- REST /api/v1 ---------+
                  + WebSocket (live audio, from B5)
                        |
                 apps/server (Fastify)
   +-----------+-----------+-----------+-------------+
   | Station   | Patient   | Scorer    | Orchestrator|
   | runner    | engine    | (eval +   | (agent loop,|
   | (timer,   | (2-step   | feedback) | sandbox)    |
   | states)   | fact gate)|           |             |
   +-----------+-----------+-----------+-------------+
        |            |           |            |
   Event log    Provider interfaces (real or Mock)
   (append-     PatientLLM, Scorer, SpeechToText,
    only)       TextToSpeech, AvatarProvider
        |
   Database (SQLite dev, Postgres pilot)  +  scenarios/ (package files)
```

- **`apps/server`** holds every rule: station states, the patient engine, scoring, logging, exports, accounts, and every AI call.
- **`apps/web`** is a thin client. No station logic, scoring or AI calls in any client (master prompt non-goal).
- **`packages/shared`** holds the zod schemas for every API body, every package file and every agent hand-off. The server and web app import the same schemas. The OpenAPI spec is generated from them, and that spec is the contract for the Unity client.
- **`scenarios/`** holds the case packages as JSON files in the repo. The database records which versions are published, but the files are the source. This keeps cases reviewable in pull requests.
- **`agents/<name>/instructions.md`** holds each agent's instructions. The server reads them at start-up, and every output records the file's version (its git commit hash plus a version line at the top of the file).

### 2.2 Station states (A6)

`briefing → encounter → ended → scoring → feedback`

- The server owns the clock. It stores the start time and duration and works out time left from those, so a refresh or headset reconnect does not lose the timer.
- One-minute warning for every case (decided in A1).
- The learner can end early. At time-out the server ends the encounter itself.
- Each state change is an event in the log.

### 2.3 One learner turn, in text (A7)

1. The learner types (later: speaks) a question. The server logs `learner_utterance`.
2. **Step 1, classify.** The fast model gets the question, the list of fact ids with their categories, disclosure levels and trigger examples (no fact content), and the facts already revealed. It returns which fact ids the question legitimately asks for, as structured output checked by zod.
3. Plain code applies the disclosure rules: a `spontaneous` fact can be released early, an `on_direct_question` fact needs a direct question, an `on_specific_question` fact needs a specific one. Code, not the model, makes the final release decision.
4. **Step 2, reply.** The fast model gets the persona, the rules, the facts revealed so far plus the newly released ones, and the conversation. Unrevealed facts are never in this prompt. It returns a short spoken-style reply and optional cues (emotion, gesture) from a fixed list.
5. The server logs `fact_revealed` events and `patient_reply`, with timings and token counts.

Exam and test actions (vitals, ECG, chest X-ray and so on) skip the model completely: the server looks up `findings.json` and logs `action_performed`.

**Mock mode:** the `PatientLLM` mock adapts the prototype's keyword fallback (`scriptedTurn`, see REUSE.md 2.2). It matches trigger examples and returns the fact text. It needs no network, so the whole station runs in tests.

### 2.4 Scoring (A10 to A12)

The scorer runs after `ended`, reading the event log and transcript. Four item types (master prompt 8.4):

| Type | How it is scored | Model? |
|---|---|---|
| `fact_elicited` | From the fact-reveal log | No |
| `action_performed` | From the action log, with optional time windows | No |
| `judged` | Strong model against written anchors. Must return verbatim quotes. The server normalises text (as the prototype does) and checks each quote is in the transcript. No match: not met. | Yes |
| `leveled_section` | Ingram sections. Elements are counted from logs and judged items. Then the profile's thresholds and mandatory rules are applied by code (for example "0 if no consent", "dose and frequency must be asked", "all 3 generations for full points"). Point values come from the profile file, never from code. | Partly |

Two checklist formats share this engine:
- **The 0/1/2 checklist** (about 15 items, instructor weights) for medicine and generated cases.
- **The official Ingram rubric**: 14 sections, 94.5 points, E/P/D/U/N/A, most sections 6.5/5/3.5/1/0, clinical judgement 10/7/5/3/0.

Every score stores the model id, the instruction version, the checklist version and the run number. A11 scores each test transcript 5 times and reports agreement per item.

Feedback (A12) is a structured object: strengths, missed items with transcript evidence, critical safety omissions, three things to practise, and a `next_station_request`. Labelled "Formative feedback. Not a grade."

### 2.5 The agent loop and the sandbox (A13 to A18)

Plain TypeScript orchestration, no agent framework:

```
library case ─► station (patient agent + synthetic student) ─► scorer ─► feedback
      ▲                                                                   │
      │                                          next_station_request ◄───┘
      └──── scenario agent makes a variation ◄────┘
                      │
           package validation + patient safety test must pass
                      │
           educator reviewer reads the whole packet ─► findings (report only)
```

- Every arrow is a JSON file checked against a zod schema in `packages/shared`. A file that fails stops the run with a readable error.
- `pnpm sandbox --case robert-tremblay --levels strong,average,weak --runs 3` (exact flags set in A14) writes one folder per encounter under `sandbox_runs/` (not committed): `packet.md` for people to read, and `packet.json` for code.
- The synthetic student and the reviewer are test tools. Their code lives under `apps/server/src/sandbox/` and has no API route, so they cannot reach the learner product.
- The scenario agent writes a new package version marked `origin: generated` and `clinical_review_status: "generated_not_reviewed"`. It never edits a library package and is switched off in summative mode.

### 2.6 Later phases (shape only, not built in Phase A)

- **Voice (B5) and video (B7):** a WebSocket carries learner audio to `SpeechToText` and patient audio and avatar events back. Text and voice turns produce the same events, so scoring does not change.
- **Quest (B13, B15):** Unity loads published packages from the API at runtime and plays the same station. It reads `presentation.json` to set up the room.
- **Hosting (B10):** one Node process plus Postgres on a single host with a Canadian region. No microservices.

---

## 3. File tree (end of Phase A)

What exists after A2 is marked (A2). Everything else is planned, with the ticket that adds it.

```
.
├─ CLAUDE.md, VISION.md, REUSE.md, PLAN.md, README.md          (A2, A3)
├─ PROGRESS.md, DECISIONS.md, KNOWN_ISSUES.md                  (A2)
├─ ASSETS.md                                                   (A9: fonts, SVG avatars)
├─ DATA_FLOWS.md                                               (A7: Anthropic first; full in B10)
├─ .env.example, .github/workflows/test.yml                    (A2)
├─ agents/
│  ├─ patient/instructions.md                                  (A7)
│  ├─ evaluation/instructions.md                               (A10)
│  ├─ student/instructions.md                                  (A13)
│  ├─ reviewer/instructions.md                                 (A16)
│  └─ scenario/instructions.md                                 (A17)
├─ scenarios/
│  ├─ robert-tremblay/1.0.0/ manifest.json, clinical_facts.json, patient_behavior.json,
│  │                         findings.json, presentation.json, assessments/medicine.json,
│  │                         feedback_rules.json, validation_tests.json        (A5)
│  └─ saylor-lee/1.0.0/      same files, assessments/nursing.json              (A5)
├─ apps/
│  ├─ server/src/
│  │  ├─ app.ts, index.ts                                      (A2)
│  │  ├─ config.ts             env, mock mode, model per agent (A6)
│  │  ├─ db/                   Drizzle schema, migrations      (A6)
│  │  ├─ packages/             load + validate scenario packages (A4)
│  │  ├─ station/              state machine, timer            (A6)
│  │  ├─ events/               append-only log, JSON/CSV export (A6)
│  │  ├─ patient/              classify + reply engine         (A7)
│  │  ├─ scoring/              item types, quote check, feedback (A10–A12)
│  │  ├─ providers/            PatientLLM, Scorer (+ mocks); speech/avatar from B5
│  │  ├─ llm/                  one Anthropic client, cost logging, refusal handling (A7)
│  │  ├─ agents/               instruction loader, versioning  (A7)
│  │  ├─ sandbox/              synthetic student, reviewer, scenario agent, runner (A13–A18)
│  │  └─ routes/               /api/v1 routes                  (A6, A9)
│  ├─ server/test/            unit tests, scripted transcripts (A11), safety questions (A8)
│  └─ web/src/                text station (A9); educator view (B4)
├─ packages/shared/src/       zod schemas: package files, API, events, hand-offs (A4 onward)
├─ e2e/                       Playwright, mock mode           (A9)
└─ reference/                 read-only sources               (A2)
```

---

## 4. Dependencies and why

### 4.1 Already installed in A2 (pinned)

Vite 8.3.8, React 19.3.1, Fastify 5.12.8, zod 4.6.7, Vitest 5.1.2, TypeScript 7.0.2, tsx, concurrently, pnpm 10.34.9.

### 4.2 To add, with the ticket that adds them

Versions are the current npm releases as of 2026-11-26. Each ticket re-checks them before installing.

| Package | Version | For | Why this one | Ticket | Still to confirm |
|---|---|---|---|---|---|
| `@anthropic-ai/sdk` | 1.14.0 | All Claude calls | The official SDK. Has structured outputs, streaming, typed errors and retries. | A7 | — |
| `drizzle-orm`, `drizzle-kit` | 0.45.4, 0.31.11 | Database and migrations | Required by the master prompt. One schema for SQLite and Postgres. | A6 | That the same schema moves to Postgres cleanly. Test in B10. |
| `better-sqlite3` | 13.2.0 | SQLite driver | The driver Drizzle supports best | A6 | Whether it ships a prebuilt binary for Node 26 (the project's Node version) on Windows. If not, it needs build tools (a manual Windows step). The alternative is Node's built-in `node:sqlite`, but only if Drizzle supports it. Decide in A6. |
| `fastify-type-provider-zod` | 7.0.0 | Request and response checking from zod schemas | Keeps API bodies and the OpenAPI spec tied to one schema | A6 | Compatibility with zod 4.6 and Fastify 5.12 |
| `@fastify/swagger` | 9.9.5 | OpenAPI spec generation | Standard for Fastify | A9 | — |
| `@playwright/test` | 1.65.1 | End-to-end tests (mock mode) | Required by the master prompt | A9 | Browser download size in CI |
| `@fastify/websocket` | 11.3.7 | Live audio channel | Standard for Fastify | B5 | — |

**Not needed:**
- `zod-to-json-schema`: zod 4 converts schemas to JSON Schema itself (`z.toJSONSchema`). That covers both the OpenAPI spec and Claude structured outputs.
- `i18next` or a router library for now. The text station can use a small typed dictionary taken from the prototype's `T` strings. Revisit in B3.
- Any agent framework (LangChain and similar). The loop is a few hundred lines of plain code, which is easier for Dr. Poenaru and Mohsen to review.

### 4.3 Claude models and three API facts that shape the design

Model names come from Anthropic's current model table (cached 2026-11-03). They are **candidates**. A7 and A15 confirm them by measurement.

| Setting | Candidate | Why | Effort |
|---|---|---|---|
| `PATIENT_MODEL` | `claude-haiku-5-5` | Fast and cheap, called twice per turn | `low` |
| `STUDENT_MODEL` | `claude-haiku-5-5` | Fast; test tool only | `low` |
| `SCORER_MODEL` | `claude-opus-5-5` | Strongest general model; judging is the product's value | `high` |
| `REVIEWER_MODEL` | `claude-opus-5-5` | Same | `high` |
| `SCENARIO_MODEL` | `claude-opus-5-5` | Same | `high` |

Decided 2026-11-26: the patient starts on Haiku 5.5 and stays there if it passes the A8 safety test. If it invents facts, the next step is `claude-sonnet-5-5`, which costs more per turn but is still fast.

Three API facts the code must respect:
1. **No forced tool calls on the current Opus and Sonnet models.** Requests that force a tool return an error. Every agent hand-off uses **structured outputs** (a JSON schema built from the zod schema), then zod checks the result again on our side.
2. **Randomness settings (temperature) are gone** from the current API version. So the scorer cannot be made fully repeatable. A11 *measures* agreement across 5 runs and reports it; the plan does not promise identical scores.
3. **The models can refuse a request** (`stop_reason: "refusal"`), and a clinical case can trip a safety filter by mistake. The `llm/` module handles a refusal as a clear, logged error, never as an empty reply. For Opus 5.5 the server-side fallback option is switched on; Haiku 5.5 has none, so the patient engine retries once and then shows "the patient did not answer" and logs it.

Also: **prompt caching.** Each agent's instructions and the case's stable parts go first in the request and are cached. Changing parts (revealed facts, the conversation) go after them. This cuts cost and response time per turn.

---

## 5. Data model

Two layers: **package files** (the case, in `scenarios/`) and **database tables** (what happened). Every zod schema lives in `packages/shared`.

### 5.1 Scenario package (A4)

Follows master prompt 8.1. Key fields:

| File | Key fields |
|---|---|
| `manifest.json` | `id`, `version` (semver), `title` {en, fr-CA}, `languages`, `duration_s`, `warning_s` (60), `door_note` {en, fr-CA}, `objectives`, `profession_tasks` (medicine / nursing task text), `clinical_review_status` (`draft`, `in_review`, `approved`, `generated_not_reviewed`), `origin` (`library` or `generated`), `parent` (for generated: source case and version), `todo_clinical` (list of open items) |
| `clinical_facts.json` | per fact: `id`, `category`, `content` {en, fr-CA}, `disclosure` (`spontaneous`, `on_direct_question`, `on_specific_question`), `trigger_examples`, `placeholder` (true when marked TODO(clinical)), `source` (prototype line or SP script section) |
| `patient_behavior.json` | `persona`, `speaking_style`, `emotional_state`, `concerns`, `unknown_policy` |
| `findings.json` | per action: `id`, `label` {en, fr-CA}, `result` {en, fr-CA}, `category` (exam, investigation) |
| `presentation.json` | per platform: `avatar`, `voice`, `environment_id`, `posture`, `equipment`, `interaction_points`. Only the mock avatar is filled in Phase A. |
| `assessments/<profile>.json` | `checklist_version`, `format` (`weighted_012` or `leveled`), items or sections. Each item: `id`, `type`, `domain`, `label`, `weight`, `anchors`, linked `fact_ids` / `action_ids`, `time_window_s`. Each leveled section: `levels` with points, `count_thresholds`, `mandatory_rules`. |
| `feedback_rules.json` | domain names, critical safety items, practise-next templates |
| `validation_tests.json` | questions that must get a given fact, and things the patient must never say or invent |

**One clinical truth:** medicine and nursing share `clinical_facts.json`. They differ only in the assessment profile and the task text.

### 5.2 Database tables (A6 onward)

| Table | What it holds | Notes |
|---|---|---|
| `package_versions` | case id, version, content hash, state (draft, in review, published, archived), origin, review status, created_at | Published rows never change. The hash proves the files match what the session used. |
| `checklist_versions` | case, profile, version, weights JSON, created_by, created_at | Editing weights (B9) adds a row; it never changes one. |
| `agent_instruction_versions` | agent name, version, git hash, content hash | |
| `participants` | pseudonymous id, role (learner, educator, admin), invite code used | No names or emails in Phase A. Accounts arrive in B1. |
| `sessions` | id, participant, package version, checklist version, profile, language, `client` (`web_desktop`, `quest_unity`, `sandbox`), mode (`formative`, `summative`), state, timer start and duration, `parent_session_id` (replay or next station) | Pins every version the session used. `sandbox` covers synthetic encounters. |
| `events` | session, sequence number, time, type, payload JSON, latency_ms | **Append-only**: no updates or deletes. Types: state_change, learner_utterance, patient_reply, fact_revealed, action_performed, timer_warning, llm_call (model, tokens, cost), error. |
| `scores` | session, item or section id, run number, AI value, quotes, quote_check result, model id, instruction version, checklist version | Several runs per item (for A11). |
| `overrides` | score id, educator, new value, required reason, time | The AI value stays in `scores`; both appear in the export (B4). |
| `feedback_reports` | session, report JSON, model id, instruction version | |
| `next_station_requests` | from session, weak areas, learner level, presentation, status (offered, accepted, generated) | Links to the generated package version. |
| `reviewer_findings` | session, findings JSON (case coherence, patient behaviour, scoring fairness), model id, instruction version | Sandbox only. |
| `audit_log` | who, what (publish, override, weight change), when | |

**Exports (A6, extended in A10 and B4):** full-session JSON; CSV with one row per event; CSV with one row per rubric item (AI score, override, reason). The CSVs carry a byte-order mark so Excel opens French accents correctly, as the prototype does.

---

## 6. Licence notes

| Item | Status | Action |
|---|---|---|
| npm packages listed above | MIT or Apache-2.0 according to their npm pages; recheck each when installing | Record in `DECISIONS.md` when added |
| Old repo code | Its READMEs say MIT, but there is **no LICENSE file** | Ask Mohsen before copying any code text (REUSE.md section 3). The plan reuses ideas and test questions, not code. |
| Prototype fonts (Bricolage Grotesque, IBM Plex Sans, IBM Plex Mono) | Google Fonts, believed to be under the SIL Open Font License | Confirm, and record in `ASSETS.md` in A9 |
| Prototype SVG avatars | Drawn for the prototype, not a real person | Record in `ASSETS.md` (A9) |
| Saylor Lee SP script, Ingram rubric | McGill course documents (NUR1-338, Fall 2024) | Used with the Ingram partnership. TODO: confirm in writing that the team may use them in software (open question). |
| Old repo photo, logo, video | Source unknown | Not used (REUSE.md) |
| Claude outputs | Covered by the Anthropic commercial terms of the account that holds the key | Check the account type once the account owner is known |
| Voice and video vendors | Not chosen | Licence and data terms are part of B6 |

---

## 7. Cost assumptions

**These are estimates, not measurements.** The token counts are guesses. The prices are from Anthropic's model table as cached on 2026-11-03 (per million tokens: Haiku 5.5 $0.10 in / $0.50 out; Opus 5.5 $4 in / $20 out). A15 replaces this section with measured numbers. Before any real call, the live pricing page is checked again.

| Step | Calls per encounter | Guess: tokens per call (in / out) | Rough cost |
|---|---|---|---|
| Patient (2 calls per turn, about 25 turns) | ~50 Haiku | 3,000 / 150 | ~$0.02 |
| Scoring and feedback (Saylor Lee, 14 sections plus feedback) | ~3 to 15 Opus | 12,000 / 2,000 | ~$0.25 to $1.30 |
| Synthetic student (sandbox only) | ~25 Haiku | 2,000 / 100 | ~$0.01 |
| Educator reviewer (sandbox only) | 1 Opus | 20,000 / 3,000 | ~$0.14 |

- **Scoring is the main cost, and the patient is cheap.** One sandbox encounter is roughly $0.40 to $1.50 before caching. Caching should cut the repeated instruction text.
- **A11 is the most expensive Phase A ticket:** 6 transcripts × 5 scoring runs. At the upper guess that is about $40.
- **Phase A total guess:** under $200 for model calls, consistent with the meeting's "three digits" estimate. Weekly spending is reported in each ticket, as the working rules require.
- No voice, video or hosting costs in Phase A. Those are measured in B6, B7 and B10.

---

## 8. Ticket order and what each one proves

The order is the tracker's. This plan adds no tickets.

| Week | Tickets | What exists at the end |
|---|---|---|
| 2 | A4, A5, A6 | Both cases as checked packages in English and French; a timed text station with a full event log and exports, in mock mode |
| 3 | A7, A8, A9 | The real two-step patient; 15 tricky questions per case with no invented findings; Shreenik plays both cases in a browser |
| 4 | A10, A11, A12 | Scoring on both formats with checked quotes; agreement across 5 runs; feedback and next-station requests |
| 5 | A13, A14, A15 | Synthetic student at three levels; one-command sandbox packets; measured cost |
| 6 | A16, A17, A18 | Reviewer findings; first generated variation; the closed loop |
| 7 | A19, A20, A21 | Human reading round; revised instructions; handover to Addie |

**A note on week 2:** it holds three tickets, and today is 26 November, three days before its end date. A5 is the heaviest, because Saylor Lee has 24 placeholder facts to rebuild from the SP script, with each conflict marked TODO(clinical). If the week slips, A5 moves first; A6 can run on Robert Tremblay alone.

---

## 9. Risks

| Risk | Why it matters | How the plan handles it |
|---|---|---|
| The patient invents a finding | Learners trust it; this is the main clinical risk in Phase A | Two-step fact gate; unrevealed facts never in the prompt; findings only from files; A8 safety test with the real model; `validation_tests.json` run on every package change |
| The scorer gives different scores on repeat runs | Fair scoring is the product's value; randomness cannot be switched off | Deterministic items wherever possible (counts and mandatory rules in code); judged items need checked quotes; A11 reports per-item agreement; low-agreement items go to Dr. Poenaru for clearer anchors |
| The AI scores professionalism (section 14) | The rubric leaves this section to the evaluator's discretion | Decided: the AI scores it, with quotes like every judged section. An educator can override it with a reason, and every score is labelled formative. |
| Saylor Lee's content is wrong or incomplete | The SP script leaves many details to the actor; French wording is unreviewed | Every gap marked TODO(clinical) and listed in the manifest; package stays `draft`; a faculty reviewer is still unnamed (REUSE.md section 8) |
| Agents share blind spots | The reviewer agent can pass a bad encounter | Human reading in A19 is the acceptance test |
| Two model calls per turn are too slow for voice | The M3 target is a median under 2.5 seconds from end of speech to patient audio | Fast model on both steps, caching, streaming the reply. Measure turn times from A7 so the risk is visible before B5. A fallback (one call with a short allowed-fact list) can be tested in B5 if needed. |
| A safety filter refuses a clinical prompt | A refused reply looks like a broken patient | Refusals are logged and shown clearly; fallback model on Opus calls; A8 includes sensitive topics (sexual health, substance use) to find refusals early |
| Native SQLite driver fails to install on Node 26 / Windows | Blocks A6 on Siqi's machine | Check first in A6; documented fallback (see 4.2) |
| Copies of the master prompt drift apart | Claude Code reads `CLAUDE.md` first, so an old copy builds the wrong rubric | The Google Doc is the source. `CLAUDE.md` was synced to it in A3. Any later change to the Google Doc is copied into `CLAUDE.md` in the same week, by pull request. The Claude Docs copy is retired or updated (section 10.1). |
| Scope: five agents and two clients | Two builders | No client work until the text loop is accepted; VR only after the desktop walkthrough (tracker order) |
| The old repo's OpenAI key is still live | Anyone with read access can use it | Not used or copied (KNOWN_ISSUES 1). Shreenik's decision stands, but this plan recommends revoking it, since nothing new depends on it. |

---

## 10. Open questions

### 10.1 Answered by Shreenik at review (2026-11-26)

1. **Current master prompt: the Google Doc.** `CLAUDE.md` is now synced to it (this ticket). The Claude Docs copy of "TheiaXR Build Plan and Tickets" (16 November) is out of date. It still says to build on the old repo, and it lists 10 rubric sections and the old ticket wording. Retire it or update it from the Google Doc.
2. **Anthropic API account: none yet. One is needed before A7 (week 3, from 30 November).** Phase A runs in mock mode until then. Setup steps are in section 10.3.
3. **Patient model:** start on the fast model, Haiku 5.5. Keep it if it passes the A8 safety test.
4. **Professionalism (Ingram section 14): the AI scores it.** It is a judged section with checked quotes. An educator can override it with a reason. This closes REUSE.md open item 8.3.
5. **Node version: Node 26 everywhere.** It is the current long-term support line. CI is moved from Node 24 to 26, and `.nvmrc` pins 26.

### 10.2 Other open questions (do not block A4)

- Who reviews Saylor Lee's TODO(clinical) items and the French wording? (Shreenik)
- What do "Level 4: 11 points minimum … Level 1: 0" on the last page of the official rubric mean? (Ingram faculty)
- Which rubric should Robert Tremblay's medicine station follow? The current one was drafted by the team. (Shreenik)
- May the team use the SP script and the Ingram rubric in software? Is there written permission? (Shreenik, Ingram)
- May code text from the old repo be reused, given there's no LICENSE file? (Mohsen)
- How many hours a week does Siqi have, and when does Addie start? (Shreenik)
- When can Ingram faculty do the walkthrough? Assumed early March 2027. (Shreenik)
- Will Dr. Poenaru edit drafts of the agent instructions? The plan assumes drafts adapted from the prototype's prompts, starting in A7. (Dr. Poenaru)

### 10.3 Getting an Anthropic API account (Shreenik or the Theion account owner)

1. Go to platform.claude.com (the Claude Console) and sign up with a Theion address, not a personal one. Create an organization named for Theion.
2. Under **Billing**, add a payment method and buy prepaid credits. $50 to $100 covers A7 to A10 (section 7).
3. Under **Workspaces**, create a workspace called `theiaxr-dev`. Set a **monthly spend limit** on it ($100 to $200 to start), so a bug can't run up a bill.
4. In that workspace, create an API key called `theiaxr-dev-siqi`. Copy it once. It is shown only once.
5. Send it to Siqi through a password manager or another private channel, never by email, chat or GitHub. Siqi puts it in the repo's local `.env` file as `ANTHROPIC_API_KEY=...`. That file is never committed.

Keys can be revoked and replaced in the same screen at any time. Usage per day appears under **Usage**, which feeds the weekly spending report.

---

## 11. What this ticket did not do

- No application code, schemas, packages or agent instructions. Those start in A4.
- No paid service was used. Cost: $0.
- Package versions were read from npm, nothing new was installed. Compatibility marked "still to confirm" in 4.2 has not been tested.
- `CLAUDE.md` was synced to the Google Doc master prompt (5 edits: reference list, leveled scoring, both seed cases, M2 acceptance). Nothing else in it changed.
- The tracker's Status column was not changed. That is for the weekly review.
