# REUSE.md: what we take from the prototype and the old repo

Ticket A1. Written 2026-11-25. No application code has been written.

This file lists every part of the two existing code bases and says whether the new TheiaXR build should **copy** it (take it as is), **adapt** it (take the idea or content and rewrite it for the new structure) or **leave it out**. When code or content is actually reused in a later ticket, that ticket adds the destination path to the tables below.

## In short (for a clinician)

- **The prototype is the main source.** It already does the hard parts in a simple way: fact-gated patient answers, scoring with checked quotes, a feedback screen, English and French, and data export. We keep its look, its text and its two cases, and rebuild the code properly on a server.
- **The old repo is useful above all for two source documents: the official Saylor Lee SP script and the official course rubric.** Both are McGill NUR1-338, Fall 2024. Copies are now in `reference/`.
- **Decided 2026-11-25: the SP script is the clinical truth for Saylor Lee.** It contradicts most of the prototype's placeholder details (age, job, surgery, family history, sleep and more). Section 4 lists every fact that has to change.
- **Decided 2026-11-25: the official rubric wins.** It has **14 sections, 94.5 points in total**, scored 6.5 / 5 / 3.5 / 1 / 0, with clinical judgement scored 10 / 7 / 5 / 3 / 0. The prototype scores only 10 sections on a 5 / 4 / 3 / 1 / 0 scale, and the master prompt repeats that scale. See section 5.
- **Decided 2026-11-25: every station gives a 1-minute warning**, including Saylor Lee (the SP script says 3 minutes).
- **Little of the old code is reused.** It is Python with LangChain and OpenAI, and the new build is TypeScript with Claude. We keep a few ideas and its test questions, not its code.
- **The old repo's OpenAI key.** It is committed in `backend/.env`. Shreenik decided not to revoke it for now. The new build uses Claude, so it doesn't need the key, and the key is never copied into the new repo. See section 6.

## 1. What I read

| Source | Where | Read? |
|---|---|---|
| Master prompt | `reference/TheiaXR_Master_Prompt_ClaudeCode.md` | In full |
| Prototype | `reference/prototype/index.html` (752 lines) | In full |
| Ingram rubric, official course version (clean copy) | `reference/ingram_rubric/OSCE_rubric_F24_from_old_repo.pdf` (copied from the old repo's `osce-simulator/docs/rubrik/OSCE_rubric.pdf`) | In full. "OSCE Rubric - Fall 2024 HHx Assessment (FINAL)", NUR1-338, 11 pages. |
| Ingram rubric, official course version (Drive copy) | `reference/ingram_rubric/F24_Midterm_OSCE_Rubric.pdf` (from Google Drive, "F24 Midterm OSCE Rubric PDF") | The same rubric, but most of its text can't be extracted (12 pages, mostly images). Kept for reference. |
| Ingram rubric, team guide | `reference/ingram_rubric/OSCE_Health_History_Rubric_Detailed_Guide.pdf` (from Google Drive) | In full, as text from Drive |
| Old repo | `C:\Users\Shreenik\Documents\GitHub\platform` (GitHub `Theia-XR/platform`, branch `main`, last commit 2025-09-12) | Every README, the Saylor Lee case files, the scoring service, the main API file, and the outline of every other code file. Read only: nothing was changed. |
| Saylor Lee SP script | `reference/saylor_lee/Saylor_Lee_SP_script_F24.docx` (copied from the old repo's `osce-simulator/docs/saylor_lee/Saylor_Lee.docx`) | In full |
| Vision document | Not provided | Shreenik confirmed it is not needed |

PDF and Word text was extracted with a small script in a temporary folder outside both repos, using `pypdf` 5.1.0 installed only in that folder (approved by Shreenik).

## 2. The prototype (`reference/prototype/index.html`)

Line numbers refer to `reference/prototype/index.html`.

### 2.1 Clinical content: copy exactly, into scenario packages

| Content | Where | Decision | Notes |
|---|---|---|---|
| Robert Tremblay patient facts (22 facts, English and French, disclosure levels, trigger words) | `R_FACTS`, lines 235-258 | **Copy** to `clinical_facts.json` | Trigger words become `trigger_examples`. Wording copied exactly. |
| Robert Tremblay persona | line 677 | **Copy** to `patient_behavior.json` | |
| Robert Tremblay medicine actions and findings (9 actions: vitals, JVP, heart, lungs, legs, medication list, ECG, chest X-ray, bloodwork) | `M_ACTIONS`, lines 706-714, reusing `R_ACTIONS` lines 259-265 | **Copy** to `findings.json` | Labelled in the prototype as not yet reviewed by physician faculty, including results and doses (line 739). Keep `clinical_review_status: "draft"`. |
| Robert Tremblay medicine rubric (23 items in 5 domains) | `M_RUBRIC`, lines 716-731 | **Copy** to `assessments/medicine.json` | Drafted by the Theia team, not by a medical school (master prompt section 9). |
| Robert Tremblay medicine door note, objectives, attending reply, presentation prompt | lines 734-747 | **Copy** to `manifest.json` and interface text | |
| Robert Tremblay judge context ("CASE FACTS" given to the scorer) | line 733 | **Adapt** | It restates facts already in the package. Generate it from the package so there is one clinical truth. |
| Robert Tremblay **nursing** version (SBAR escalation within 6 minutes, nursing rubric, nursing door note) | lines 266-286, 290-333 | **Leave out for now** | The prototype replaces it with the medicine version at line 732, so a learner never sees it. Keep it in `reference/prototype/` as reference in case a nursing version of this case is wanted later. TODO(clinical): confirm it is not needed. |
| Saylor Lee patient facts (38 facts, English and French) | `S_FACTS`, lines 613-652 | **Adapt. Do not copy as is.** | 24 facts are marked `p:1` as placeholders invented for the demo, and many contradict the SP script, which is now the source. Keep the prototype's French wording where the fact is unchanged. See section 4. |
| Saylor Lee persona | line 681 | **Adapt** from the SP script | The prototype says she is 45. The SP script says about 68. |
| Saylor Lee rubric (10 leveled sections with anchors and mandatory rules) | `S_RUBRIC`, lines 653-665 | **Adapt** to `assessments/nursing.json`, rebuilt from the official rubric | The prototype's anchor wording is a useful start, but sections, points and thresholds come from the official rubric. See section 5. |
| Saylor Lee judge context | line 682 | **Adapt** | Same reason as Robert's. It also repeats placeholder details. |
| Interface text, English and French (about 70 strings) | `T`, lines 289-334, and per-case text lines 683-692 and 734-747 | **Copy** to the web app's translation files | Includes the consent text, "Formative feedback. Not a grade." and the draft-case notices. |

### 2.2 How it works: adapt the logic, rewrite the code

| Feature | Where | Decision | Notes |
|---|---|---|---|
| Fact-gated patient prompt (disclosure levels, unknown-question rule, ignore role-change requests, JSON reply with revealed fact ids) | `patientPrompt`, lines 444-463 | **Adapt** into `agents/patient/instructions.md` and the server's patient engine | The prototype sends **all** facts to the model every turn and trusts it to hold back. The master prompt (8.2) requires a two-step design where unrevealed facts never reach the reply prompt. The rules text is reused; the design changes. |
| Keyword fallback patient (used when no AI is available) | `scriptedTurn`, lines 465-470 | **Adapt** as the `PatientLLM` Mock provider | Fits the "runs with no keys and no network" rule for tests. |
| Fact reveal log | lines 494-495 | **Adapt** into the server event log | |
| Station timer, one-minute warning, end early (tap twice), end on timeout | `startStation`, `tick`, `paintActions`, lines 402-425 | **Adapt** into the server-side station state machine (8.3) | Today the timer lives in the browser and is lost on refresh. Warning stays at 1 minute for every case (decided 2026-11-25). |
| Actions return findings | `doAction`, lines 426-431 | **Adapt** | Findings will come from `findings.json` on the server. |
| Presentation or handover to the attending | `openSbar` and the sheet, lines 432-438 | **Adapt** | The reply from the attending is fixed text. Keep it that way. |
| Deterministic scoring (fact elicited, action performed, escalation time) | `deterministic`, lines 506-514 | **Adapt** into the `Scorer` | Maps to `fact_elicited` and `action_performed` (8.4). |
| LLM-judged scoring with anchors and verbatim quotes, and the quote check that sets an item to 0 when the quote is not in the transcript | `judgePrompt` and `judge`, lines 515-545 | **Adapt** into `agents/evaluation/instructions.md` and the `Scorer` | This is the core safety rule for scoring. Keep it. The prototype's check normalises text before matching; keep that too. |
| Leveled scoring display (Excellent 5, Proficient 4, Developing 3, Unsatisfactory 1, Not applicable 0) | line 576 and strings line 305 | **Adapt** into the `leveled_section` item type | In the prototype the mandatory-item rules live inside the anchor text the AI reads. The master prompt wants them as explicit rules the server applies. |
| Feedback screen (domain tiles, what went well, practise next, item list with evidence) | `renderFeedback`, lines 561-589 | **Adapt** into React | Keep the layout and wording. |
| JSON session export, CSV event export (with Excel-friendly byte-order mark) | lines 592-601 | **Adapt** | Add the per-rubric-item CSV and override columns required in 8.6. Change `client: "web_demo"` to `"web_desktop"`. |
| Browser speech for the patient voice, with voice picking by name | `speak`, lines 381-399 | **Adapt** as a free, no-key `TextToSpeech` fallback | Real voices come from the vendor test in M3. |
| Animated SVG avatars (blinking, breathing, mouth moving while speaking) | lines 187-198 and 666-674 | **Copy** as the `AvatarProvider` Mock | Drawn for the prototype, not a real person's likeness. Record in `ASSETS.md`. |
| Visual design (colour tokens, fonts, layout) | lines 10-147 | **Copy** the tokens and look; rewrite the layout | Fonts are Bricolage Grotesque, IBM Plex Sans and IBM Plex Mono from Google Fonts. Check their licences before bundling (to be recorded in `ASSETS.md`). |
| Claude artifact hooks (`window.claude.use("sample")`, `"downloads"`) | lines 348-356, 474, 532, 604 | **Leave out** | These only work inside a Claude artifact. The new build calls the Anthropic API from the server. |
| Random participant id in the browser | line 338 | **Leave out** | Replaced by server-issued pseudonymous ids (8.6). |

## 3. The old repo (`Theia-XR/platform`)

The old repo is a Python (FastAPI, LangChain, OpenAI GPT-3.5) back end with a React front end. The new build uses TypeScript, Fastify and Claude, so almost none of its code can be copied directly. Paths are relative to the old repo's root.

| Part | Path | Decision | Reason |
|---|---|---|---|
| **Saylor Lee SP script** (official F24 Midterm OSCE SP Script) | `osce-simulator/docs/saylor_lee/Saylor_Lee.docx` | **Copied** to `reference/saylor_lee/Saylor_Lee_SP_script_F24.docx`. **The clinical source** for the Saylor Lee package (section 4). | |
| Saylor Lee question-and-answer list | `backend/app/models/SaylorLee/SaylorLee.md` | **Adapt** into `validation_tests.json` | A faithful rewording of the SP script as questions and answers. Good test questions for the patient. |
| Saylor Lee one-tool-per-topic answers (about 70 fixed answers with "only if asked" flags) | `backend/app/models/SaylorLee/SaylorLeeTools.py`; same idea in `osce-simulator/backend/app/services/minimal_saylor_lee_langchain_service.py` | **Adapt the content only** | The "only if asked" flags match our disclosure levels (`on specific question`). The code uses global variables and GPT-3.5 and is not reusable. |
| Sample Saylor Lee conversations | `backend/app/models/SaylorLee/SampleFlow1.md`, `SampleFlow2.md` | **Adapt** as scripted test transcripts (M2) | Need checking against the SP script first. |
| Rubric scoring prompts, one per section (12 in the code) | `osce-simulator/backend/app/services/specialized_evaluation_service.py` | **Adapt the anchor wording only**, checked against the official rubric | Its section list and point values differ from the official rubric (section 5). No quote checking, so its scores cannot be verified. |
| Description of that scoring system | `osce-simulator/backend/SPECIALIZED_EVALUATION_README.md` | Reference only | |
| Official rubric PDF | `osce-simulator/docs/rubrik/OSCE_rubric.pdf` | **Copied** to `reference/ingram_rubric/OSCE_rubric_F24_from_old_repo.pdf`. **The source** for `assessments/nursing.json` (section 5). | The same rubric as the Drive copy, but its text can be extracted. |
| Speech to text with OpenAI Whisper (record in browser, upload, transcribe) | `osce-simulator/backend/app/main.py` lines 269-318; `osce-simulator/frontend/src/pages/ConsultationPage.tsx` (MediaRecorder) | **Leave out** | The master prompt picks streaming speech vendors with turn detection (Deepgram Flux, AssemblyAI). Whisper is not on the shortlist. |
| Login with JWT in an HttpOnly cookie, user list from an environment variable | `osce-simulator/backend/app/core/auth.py` | **Leave out** (idea noted) | The new build uses invite codes with roles (8.8). The cookie approach is sound and may be reused as an idea. |
| Simple per-IP rate limiting | `osce-simulator/backend/app/main.py` lines 57-80 | **Adapt the idea** in M5 | Needed for pilot readiness. |
| Conversation store as JSON files | `osce-simulator/backend/app/services/session_manager.py` | **Leave out** | Replaced by SQLite and Drizzle with an append-only event log. |
| Database models (student, consultation, evaluation category) and seed data | `osce-simulator/backend/app/models/` | **Leave out** | Different data model. The seed data is made up ("John Doe", fixed scores). |
| Patient case generator from difficulty and personality settings | `osce-simulator/backend/app/services/langchain_service*.py`, `patient_service.py`, `chat_service.py` and the "simple" and "minimal" variants | **Leave out** | Generates clinical content freely. That breaks the "never invent clinical content" rule. The scenario agent (8.14) replaces it under strict validation. |
| Front-end pages (dashboard, practice, history, evaluations, tutorial, consultation notes) | `osce-simulator/frontend/src/pages/` | **Leave out the code.** Look at the dashboard and history pages again when designing the educator view (8.7). | Different stack choices (Tailwind, framer-motion) and different flow. |
| Educator question form (5 free-text questions) | `osce-simulator/frontend/src/pages/FormPage.tsx` | **Leave out** | An early idea for case authoring. Belongs to the Scenario Studio (M6). |
| Python tests | `osce-simulator/backend/tests/`, `test_*.py` | **Leave out the code.** Reuse the Saylor Lee questions they ask as patient test cases. | |
| Docker, Docker Compose, Nginx, run scripts | `osce-simulator/docker-compose.yml`, `Dockerfile`s, `nginx.conf`, `run.py`, `run.sh`, `docker-run.sh` | **Leave out** | Deployment and hosting files. Not to be copied (session rules). |
| Saylor Lee photo | `osce-simulator/frontend/public/Saylor Lee.png` | **Leave out** | Source and licence unknown. Could be a real person's likeness, which the rules forbid. |
| Tutorial video, logo, favicon, screenshots | `osce-simulator/frontend/public/videos/Tutorial.mov`, `public/logo.png`, `public/favicon.*`, `docs/screenshots/` | **Leave out** | Source and licence unknown. Ask Shreenik if a logo should be reused. |
| Licence | Both READMEs say MIT, but there is **no LICENSE file** | Note | Ask Mohsen before reusing any code text. |

## 4. Saylor Lee: the prototype disagrees with the official SP script

The SP script (`reference/saylor_lee/Saylor_Lee_SP_script_F24.docx`, "F24: Midterm OSCE SP Script") is the course document. The prototype's Saylor Lee facts were partly made up for the demo and marked as placeholders (`p:1`).

**Decided 2026-11-25 (Shreenik): the SP script is the single clinical truth.** When the package is built (ticket M1), each fact below takes the SP script's value. Where the SP script leaves a choice to the actor ("at the SP's discretion"), or says nothing, the fact stays marked TODO(clinical) for faculty review. I will not fill those gaps myself. New French wording for changed facts is also TODO(clinical) until a French-speaking reviewer checks it.

| Topic | Prototype (fact id) | SP script (now the source) | What happens in the package |
|---|---|---|---|
| Age | 45 (`s_age`, placeholder; persona line 681) | "According to SP, ideally approx. 68" | **Conflict.** TODO(clinical) |
| Occupation | Accountant, works from home (`s_work`, placeholder) | Lawyer, very busy, new firm | **Conflict.** TODO(clinical) |
| Relationship | Partner for 12 years (`s_relationship`, placeholder) | Common-law, about 32 years | **Conflict.** TODO(clinical) |
| Pronouns and sex | She/her (`s_name`, placeholder) | Adapted to the SP's own pronouns | An AI patient has no SP. TODO(clinical): choose. |
| Surgery and hospital stays | "No hospital stays and no surgeries" (`s_hosp`, placeholder) | Appendix removed at age 20, no complications | **Conflict.** TODO(clinical) |
| Injuries | Not in prototype | Broke tibia skiing as a child | Missing |
| Father | Heart attack at 62 (`s_family_parents`, placeholder) | Died 5 years ago of lung cancer | **Conflict.** TODO(clinical) |
| Mother | Type 2 diabetes | Lives in Florida, well-controlled type 2 diabetes | Agrees |
| Siblings | One brother, healthy (`s_family_sibs`, placeholder) | One sister, about 62, healthy; close to nieces and nephews | **Conflict.** TODO(clinical) |
| Grandparents | Maternal grandmother had diabetes (`s_family_grand`, placeholder) | Does not know grandparents' health history | **Conflict.** TODO(clinical) |
| Sleep | About 7 hours, no naps (`s_sleep`, placeholder) | About 6 hours, trouble falling asleep, "mental to-do lists" | **Conflict.** TODO(clinical) |
| Social support | Friends still in Ottawa, building a circle (`s_support`, placeholder) | Supportive family, many friends, great community, good new colleagues | **Conflict.** TODO(clinical) |
| Menstrual history | "My periods are regular" (`s_obgyn`, placeholder) | Never pregnant, no abortions or miscarriages; periods not mentioned | Prototype adds a detail not in the source. TODO(clinical) |
| Eye exam | "Last eye exam two years ago" (`s_ros_eyes`, placeholder) | Denies vision changes; no eye exam date | Prototype adds a detail not in the source. TODO(clinical) |
| Thirst and weight | "Not unusually thirsty, weight stable" (`s_ros_endo`, placeholder) | Diabetes well controlled; denies unintentional weight loss, fever, chills, night sweats | Close; wording differs. TODO(clinical) |
| Housing, language | Rents an apartment; speaks English, French improving (placeholders) | Not stated | Not in source. TODO(clinical) |
| Medication doses | Names only, no doses (`s_meds`) | Metformin 500 mg twice a day; Lipitor 20 mg every evening; Cipralex 10 mg daily, 2 years | **Missing doses.** The rubric requires the learner to ask dose and frequency, so the patient must know them. |
| Tylenol | "Occasional headaches" (`s_otc`) | 650 mg (2 tablets), about once a month | Missing dose and frequency |
| Sexual health | "Partner only, no concerns" (`s_sexual`, placeholder) | Monogamous; last STBBI test 2 years ago, negative; no contraception or barriers | Prototype is thinner than the source |
| Walking | "About 30 minutes every day" (`s_exercise`) | "Approx. 30 minutes every evening"; golf every Saturday in summer, mostly for networking | Small difference |
| Vaping | 1 nicotine cartridge a day for 5 years (`s_vape`) | Same, and "it used to help with the stress" | Agrees |
| Help to cut down vaping | "Open to help" (`s_vape_support`, specific) | Not in source (the source's "be open to it" refers to a medic alert bracelet or counselling) | Not in source. TODO(clinical) |
| Medic alert bracelet | Not in prototype | Does not wear one; open to it if offered | Missing |
| Other details in the SP script but not in the prototype | | Hair thinning in the shower; no childhood illnesses; last medical exam 6 months ago for diabetes; does not know how to get vaccines in Montreal; no drug or environmental allergies; no spiritual resources; no financial issues; no environmental hazards; "perception of health"; 24-hour diet recall | Missing |
| Station length and warning | 15 minutes (noted as assumed), 1-minute warning | 15 minutes with a 3-minute warning | 15 minutes, now from the source. Warning stays at **1 minute** (Shreenik's decision). |

Reading the table under the decision: every row marked "Conflict" or "Missing" takes the SP script's value. "Not in source" rows are dropped or marked TODO(clinical). Rows the SP script leaves to the actor (age, pronouns, birth date, partner's name) are TODO(clinical). The age will be about 68, as the script suggests, unless faculty say otherwise.

## 5. The Ingram rubric: which sections count?

**Decided 2026-11-25 (Shreenik): the official course rubric wins.** The source is `reference/ingram_rubric/OSCE_rubric_F24_from_old_repo.pdf`, "OSCE Rubric - Fall 2024 HHx Assessment (FINAL)", NUR1-338.

### 5.1 How the sources compare

| Source | Sections | Scale |
|---|---|---|
| **Official rubric (the source)** | **14** (listed in 5.2), **total 94.5** | 6.5 / 5 / 3.5 / 1 / 0; clinical judgement 10 / 7 / 5 / 3 / 0 |
| Prototype (`S_RUBRIC`) | 10. Past medical history is one section, and patient-centred care, clinical judgement and professionalism are missing. | 5 / 4 / 3 / 1 / 0 |
| Master prompt (sections 8.4 and 9) | Says "10 sections" | 5 / 4 / 3 / 1 / 0 |
| Team guide (`reference/ingram_rubric/OSCE_Health_History_Rubric_Detailed_Guide.pdf`) | 12. Professionalism and clinical judgement combined; no patient-centred care. | Level names only, plus 10 / 7 / 5 / 3 for professionalism and clinical judgement |
| Old code (`specialized_evaluation_service.py`) | The code has 12 scoring prompts, with no patient-centred care or professionalism. Its README lists 13 sections, including those two but missing past medical history part 1. | Mostly 0-6, intro 0-5, clinical judgement 0-10 |

**This changes the master prompt.** Sections 8.4 and 9 describe "10 sections" and "Excellent 5, Proficient 4, Developing 3, Unsatisfactory 1, Not applicable 0". The source has 14 sections and different points. The master prompt itself says the source document wins, so `nursing.json` follows the source. The level names in the source are E (Exceptional or Excellent), P (Proficient), D (Developing), U (Unsatisfactory) and N/A. Note: the last page of the PDF also lists "Level 4: 11 points minimum, Level 3: 8, Level 2: 5, Level 1: 0" with no explanation. TODO(clinical): what are these levels?

### 5.2 The 14 official sections

| # | Section | Points | Rule from the source (as written, shortened) |
|---|---|---|---|
| 1 | Introduction and collaboration with patient; biographical data | 6.5 | E 8 or more elements; P 7; D 5-6; U 1-4. **0 if no consent acquired** or section omitted. Levels also given as E ≥85% of elements, P 70-84%, D 55-69%, U <55%. |
| 2 | Past medical history, part 1 | 6.5 | E 7 or more; P 6; D 4-5; U 1-3; 0 if omitted. **Must give medical history examples. Must ask at least 1 sexual history element for the point.** Element given if obstetric history is not applicable. |
| 3 | Past medical history, part 2 (medications and allergies) | 6.5 | E 8 or more; P 7; D 5-6; U 1-4; 0 if omitted. Each category of medication is 1 element, and **dose and frequency must be asked** for that element's point. Each type of allergy is 1 element. |
| 4 | Family history | 6.5 | E 5 or more; P 4; D 3; U 1-2; 0 if omitted. Each generation is 1 element; **all 3 generations needed for full points.** Each hereditary illness example is 1 element. |
| 5 | Functional assessment, part 1 | 6.5 | E 6 or more; P 5; D 4; U 1-3; 0 if omitted. Activity must be quantified. Mobility and assistive devices. **Sleep: must also ask about daytime naps.** Nutrition and elimination: at least 1 element each for the point. |
| 6 | Functional assessment, part 2 | 6.5 | E 7 or more; P 6; D 4-5; U 1-3; 0 if omitted. Coping: **at least 2 questions about stress** for the point. Smoking and vaping: **must ask about both, and pack-years.** **Advance care planning is mandatory for full points (minus 1 if not asked).** |
| 7 | Review of systems | 6.5 | E 5 or more; P 4; D 3; U 1-2; 0 if omitted. **A system only counts if related to the patient's past medical or family history.** |
| 8 | Opportunities for health promotion | 6.5 | E 3 health promotion items or nursing interventions; P 2; D 1; U attempted but incomplete; 0 if no education given. |
| 9 | Quality of health promotion | 6.5 | Judged on: short statements, checking understanding, evidence-based and tailored advice. Anchors written for each level. 0 if no education. |
| 10 | Global appreciation: patient-centred care | 6.5 | Judged: validates experience, considers beliefs, concerns and expectations, adapts to needs, puts the patient at ease. Anchors for each level. |
| 11 | Global appreciation: interview style | 6.5 | Judged: open-ended question to confirm reason for visit, purposeful close-ended questions after, avoids negative phrasing. Anchors for each level. |
| 12 | Global appreciation: organization | 6.5 | Judged: completes the assessment in an orderly way. Anchors for each level. |
| 13 | Global appreciation: clinical judgement, reasoning and knowledge | **10** | Judged on 10 / 7 / 5 / 3 / 0: clinical knowledge tied to the reason for visit, and use of pertinent clinical data (for example, review of systems tailored to history). |
| 14 | Global appreciation: professionalism | 6.5 | Evaluator notes any professionalism concern in comments; marks may be adjusted at the evaluator's discretion. TODO(clinical): an AI scorer should probably only **flag** concerns for an educator, never deduct by itself. |

What this means for the build:
- Most section 1-8 rules are counts plus "must" rules, so they can be checked from the fact-reveal log and the transcript (`leveled_section` with mandatory-item rules, 8.4). Sections 9-14 are judged with quotes.
- The prototype's anchor text for sections 1-8 is close to the source, but its thresholds differ in places (for example, in section 4 it requires two hereditary illnesses for "Excellent"; the source does not). Every threshold is rebuilt from the source, not copied.
- Everything stays formative. A total "out of 94.5" can be shown, but is labelled "Formative feedback. Not a grade."

## 6. Not copied on purpose (paths recorded only)

| Item | Path in old repo | Why |
|---|---|---|
| **OpenAI API key, committed to GitHub** | `backend/.env` (holds `OPENAI_API_KEY`) | A secret. I read only the variable's name, never its value. Shreenik decided on 2026-11-25 not to revoke it for now. It is **not** copied into the new repo. The new build uses Claude, so it has no use for it. If an OpenAI key is ever needed, Shreenik or a builder pastes it into the new repo's own `.env`, which is never committed. Note: anyone who can read the old repo on GitHub can read this key. |
| Browser cookies file | `osce-simulator/cookies.txt` | Likely holds session tokens. Not opened. |
| Database file | `osce-simulator/backend/osce_simulator.db` | May hold user accounts. Not opened. |
| 52 saved conversations and evaluations | `osce-simulator/backend/.osce_data/*.json` | Practice transcripts tied to user ids. I read only the field names of one file. Treated as personal data. |
| Git, GitHub and hosting files | `.git/`, Docker and Nginx files | Session rules. There is no `.github/` folder or `CNAME` file in the old repo. |

## 7. Decisions from Shreenik (2026-11-25)

1. **Saylor Lee:** the SP script is the single clinical truth and replaces the prototype's placeholders (section 4).
2. **Rubric:** the official course rubric wins (section 5). `pypdf` was approved to read it.
3. **Reference files:** the SP script and the official rubric PDF are copied from the old repo. `_setup/` is now `reference/`, laid out as the master prompt expects: `reference/prototype/`, `reference/ingram_rubric/`, `reference/saylor_lee/`, and the master prompt itself at `reference/TheiaXR_Master_Prompt_ClaudeCode.md`.
4. **Warning:** 1 minute for every station.
5. **Old OpenAI key:** not revoked for now. Not copied. Not needed by the new build.

## 8. Still open (none of these block the next ticket)

1. Who is the faculty reviewer for Saylor Lee's TODO(clinical) items and the French wording?
2. What are "Level 4: 11 points minimum" and the other levels on the last page of the official rubric?
3. ~~Should the professionalism section (14) be AI-scored, or only flagged for an educator?~~ Answered 2026-11-26 (Shreenik): the AI scores it, with checked quotes; an educator can override.
4. ~~The master prompt still says the Ingram rubric has 10 sections on a 5 / 4 / 3 / 1 / 0 scale (sections 8.4 and 9). Should it be corrected? Changing the agent rulebook goes through Dr. Poenaru's review.~~ Answered 2026-11-26: the Google Doc master prompt already has the 14 sections; `CLAUDE.md` was synced to it in A3.
