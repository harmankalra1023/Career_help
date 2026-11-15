# PRD: Digital Career Twin (DCT)
**An open-source, AI-powered lifelong career mentor for students and professionals**

| Field | Value |
|---|---|
| Version | 1.0 (build-ready) |
| License | Apache-2.0 (code), CC-BY-4.0 (taxonomies/question banks authored by the project) |
| Audience for this doc | Engineers and autonomous coding agents implementing the system |
| Note on file name | Requested as `prd.mv`; delivered as `prd.md` (Markdown) |

> **How an agent should use this document:** Section 18 gives the build order and task breakdown. Sections 6–12 are the normative specs (data model, formulas, APIs). Anything marked **MUST** is required for acceptance; **SHOULD** is strongly preferred; **MAY** is optional. Where a value is marked `[CONFIG]`, put it in a config file, not in code. If the spec is ambiguous, choose the simplest option, record the decision in `docs/decisions/ADR-XXXX.md`, and continue.

---

## 1. Vision, Problem, Goals

### 1.1 Problem
Students and professionals make career decisions with fragmented information: resumes say what they did, not who they are; job boards show openings, not trends; courses are recommended by popularity, not by personal gaps; advice is generic. There is no single system that models the *person*, models the *market*, and continuously connects the two.

### 1.2 Vision
A **Digital Career Twin**: a living, structured model of a user's skills, evidence, personality, interests, and goals, continuously compared against a living model of the job market, producing explainable scores and a concrete "do this next" plan. It acts as a lifelong mentor that gets more accurate over time.

### 1.3 Goals
1. Build a complete, evidence-backed professional profile from user input, uploaded documents, and connected accounts (e.g., GitHub).
2. Generate a **Professional DNA Profile** (a compact, visual, shareable fingerprint).
3. Compute explainable scores: Professional Profile, Technical, Non-Technical, Career Match (per path), Industry Demand, Job Readiness.
4. Identify strengths and skill gaps against specific target roles.
5. Recommend careers, courses, certifications, projects, internships, and roles, grounded in real market data.
6. Produce a milestone-based personalized roadmap and simulate career/salary growth.
7. Refresh recommendations automatically as market data and the user's profile change.
8. Be fully self-hostable, provider-agnostic for LLMs (local models supported), privacy-respecting, and extensible by the community.

### 1.4 Non-Goals (v1)
- Not a job board or application tracker (we link out to postings).
- Not a hiring/screening tool for employers. **The system MUST NOT be used to rank candidates for employers** (see Ethics, §14).
- Not a replacement for licensed counseling; no clinical psychological diagnosis.
- No guarantee of salary or placement outcomes; all projections are probabilistic and labeled as such.
- No scraping of sites that prohibit it in their ToS (use official APIs / open datasets).

### 1.5 Success Metrics
| Metric | Target (6 months post launch) |
|---|---|
| Profile completion rate (≥80% completeness) | ≥ 60% of signed-up users |
| Users who start a roadmap milestone | ≥ 50% |
| Weekly returning users after 8 weeks | ≥ 30% |
| Recommendation helpfulness (thumbs up) | ≥ 75% |
| Median time from signup to first dashboard | ≤ 10 minutes |
| Open-source health | ≥ 20 external contributors, CI green on main, ≥ 80% backend test coverage |

---

## 2. Users and Personas

| Persona | Description | Primary needs |
|---|---|---|
| **P1: Undergraduate student** | Branch such as CSE/ECE/Mech, 1st–4th year, limited experience | Discover paths, know what to learn, internships, first-job readiness |
| **P2: Recent graduate / job seeker** | 0–2 yrs, applying | Readiness score, gap closure, target roles, resume-aligned projects |
| **P3: Working professional** | 2–15 yrs | Upskilling, role switch, growth/salary simulation, trend awareness |
| **P4: Career switcher** | Non-tech to tech or vice versa | Transferable skills mapping, realistic timeline |
| **P5: Mentor / educator (v1.5)** | Reviews cohort, with consent | Aggregate view, no raw private data without consent |
| **P6: Self-hoster / contributor** | Runs or extends the project | Easy setup, plugin APIs, clear docs |

---

## 3. Product Scope and Phasing

| Phase | Scope |
|---|---|
| **MVP (v0.1)** | Auth, profile intake (forms + resume upload), GitHub import, skills taxonomy, assessments, scoring engine, career matching, gap analysis, dashboard, basic roadmap, course/project recommendations from curated catalog, market data from open datasets |
| **v0.5** | Live market connectors (job APIs), trend engine, internship/job recommendations, salary simulation, scheduled refresh + notifications, AI mentor chat |
| **v1.0** | Full continuous update loop, plugin system, multi-language UI, PDF export of DNA profile, mentor/educator view (consented), public shareable DNA card |
| **v1.5+** | LinkedIn data export import, portfolio site generator, mock interview module, community-contributed taxonomies |

The agent MUST implement MVP fully before starting later phases, but MUST design schemas and interfaces for later phases (see §6 and §17).

---

## 4. System Architecture

### 4.1 Tech Stack (default; replaceable behind interfaces)
| Layer | Choice | Notes |
|---|---|---|
| Frontend | Next.js (App Router) + TypeScript, Tailwind, shadcn/ui, Recharts (charts), i18n via `next-intl` | Responsive, accessible (WCAG 2.1 AA) |
| Backend API | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic | Typed OpenAPI contract |
| Workers | Celery (or Arq) + Redis | Ingestion, scoring, refresh jobs |
| Database | PostgreSQL 16 + `pgvector` | Relational + embeddings |
| Cache/queue | Redis | |
| Object storage | Local FS by default; S3-compatible (MinIO) optional | Uploaded resumes |
| LLM layer | Provider-agnostic interface: Ollama (local), OpenAI-compatible, Anthropic, others via adapter | Structured output required |
| Embeddings | `sentence-transformers` (local default, e.g., `all-MiniLM-L6-v2` or `bge-small`) | Swappable |
| Auth | Email+password (argon2), OAuth (GitHub, Google), JWT access + refresh | Self-host friendly |
| Observability | OpenTelemetry, Prometheus metrics, structured JSON logs | |
| Packaging | Docker Compose (dev + prod), optional Helm chart (v1.0) | One-command start |
| CI | GitHub Actions: lint, type-check, unit, integration, e2e (Playwright), container build | |

### 4.2 High-Level Components
```
┌────────────┐   ┌───────────────────────────── API (FastAPI) ─────────────────────────────┐
│  Web UI    │──▶│ Auth │ Profile │ Assessments │ Scoring │ Matching │ Roadmap │ Mentor    │
└────────────┘   └───────┬──────────────────────────────┬─────────────────────┬───────────┘
                         │                              │                     │
                ┌────────▼────────┐          ┌──────────▼────────┐   ┌────────▼────────┐
                │ Ingestion Svc   │          │ Intelligence Core │   │ Market Intel Svc │
                │ resume parser,  │          │ scoring engine,   │   │ connectors,      │
                │ GitHub analyzer │          │ matcher, planner, │   │ trend engine,    │
                └────────┬────────┘          │ simulator, LLM    │   │ demand index     │
                         │                   └──────────┬────────┘   └────────┬────────┘
                         └───────────┬──────────────────┴─────────────────────┘
                              ┌──────▼───────┐   ┌────────┐   ┌─────────┐
                              │ PostgreSQL + │   │ Redis  │   │ Storage │
                              │ pgvector     │   └────────┘   └─────────┘
                              └──────────────┘
```

### 4.3 Key Architectural Principles
1. **Deterministic core, LLM at the edges.** Scores, matches, and simulations are computed by transparent, testable code. LLMs are used for: parsing unstructured text, extracting skills, narrative explanations, mentor chat, and content generation, never as the sole source of a number.
2. **Evidence-based skills.** Every skill claim links to evidence items (certificate, project, repo, work experience, assessment, self-report) with a confidence weight.
3. **Explainability.** Every score and recommendation stores a machine-readable `explanation` (factors, weights, contributions) shown in the UI.
4. **Grounding.** Market claims MUST cite a stored data source and timestamp. The LLM mentor only states market facts retrieved from the DB (RAG over `market_*` tables); otherwise it says it doesn't know.
5. **Provider independence.** All LLM calls go through `LLMClient` (see §11). All market sources go through `MarketConnector` plugins.
6. **Idempotent, versioned computation.** Each score run is stored with `engine_version`, `taxonomy_version`, `market_snapshot_id`, so results are reproducible and diffable over time.
7. **Privacy by design.** User data is private by default; export and delete-all supported (§14).

---

## 5. Repository Structure (monorepo)

```
digital-career-twin/
├─ apps/
│  ├─ web/                      # Next.js frontend
│  └─ api/                      # FastAPI backend
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ core/               # config, security, logging, deps
│     │  ├─ db/                 # models, session, migrations (alembic)
│     │  ├─ schemas/            # pydantic models
│     │  ├─ routers/            # auth, profile, assessments, scores, careers, roadmap, market, mentor, admin
│     │  ├─ services/
│     │  │   ├─ ingestion/      # resume_parser, github_analyzer, import_adapters
│     │  │   ├─ skills/         # taxonomy, normalizer, evidence, proficiency
│     │  │   ├─ assessments/    # banks, scoring
│     │  │   ├─ scoring/        # profile, technical, nontechnical, readiness, dna
│     │  │   ├─ matching/       # career_match, gap_analysis
│     │  │   ├─ market/         # connectors, trend_engine, demand_index
│     │  │   ├─ recommend/      # courses, projects, internships, roles
│     │  │   ├─ planner/        # roadmap
│     │  │   ├─ simulator/      # career & salary
│     │  │   ├─ llm/            # client, prompts, schemas, guardrails
│     │  │   └─ refresh/        # scheduler, change detection, notifications
│     │  └─ workers/
│     └─ tests/
├─ packages/
│  ├─ taxonomy/                 # versioned skills/roles/ontology data (YAML/JSON) + validators
│  ├─ question-banks/           # assessment items (YAML) + licenses
│  └─ shared-types/             # generated TS types from OpenAPI
├─ data/
│  ├─ seeds/                    # roles, skills, courses, projects, salary bands (sample)
│  └─ fixtures/                 # test personas & sample resumes
├─ plugins/                     # example connector/plugin packages
├─ docs/                        # architecture, ADRs, contribution, API, taxonomy guide
├─ deploy/                      # docker-compose.yml, Dockerfiles, helm/
├─ .github/workflows/
├─ LICENSE  README.md  CONTRIBUTING.md  CODE_OF_CONDUCT.md  SECURITY.md
└─ Makefile                     # make dev | test | lint | seed | migrate
```

---

## 6. Data Model (normative)

All tables have `id (UUID PK)`, `created_at`, `updated_at`. `user_id` rows are deleted on account deletion (cascade). Use Alembic migrations.

### 6.1 Identity and Profile
| Table | Key columns |
|---|---|
| `users` | email (unique), password_hash (nullable if OAuth), display_name, locale, country, currency, timezone, role (`user`/`admin`), consent_flags (JSONB), onboarding_state |
| `oauth_accounts` | user_id, provider, provider_user_id, token_encrypted, scopes |
| `education` | user_id, institution, level (`school`/`diploma`/`bachelors`/`masters`/`phd`/`other`), degree, branch, start_year, end_year, status, grade_type (`cgpa10`/`cgpa4`/`percentage`/`gpa`), grade_value, grade_normalized (0–100), relevant_courses (text[]) |
| `certifications` | user_id, name, issuer, issued_on, expires_on, credential_url, taxonomy_cert_id (nullable), verified (bool) |
| `experiences` | user_id, type (`job`/`internship`/`freelance`/`research`/`volunteer`/`leadership`/`entrepreneurship`), org, title, start, end, description, achievements (text[]), team_size, skills_used (via link table) |
| `projects` | user_id, title, description, url, repo_url, role, start, end, outcomes, complexity_self (1–5), skills_used |
| `publications_awards` | user_id, type, title, date, description, url |
| `documents` | user_id, kind (`resume`/`transcript`/`certificate`/`other`), storage_key, mime, parse_status, parsed_json |
| `github_profiles` | user_id, username, synced_at, metrics_json (see §7.3), top_languages_json, repos_summary_json |
| `external_profiles` | user_id, kind (`linkedin_export`/`kaggle`/`leetcode`/`other`), data_json |

### 6.2 Skills and Evidence
| Table | Key columns |
|---|---|
| `skills` (taxonomy) | slug (unique), name, category, subcategory, type (`technical`/`non_technical`), aliases (text[]), description, embedding (vector), taxonomy_version |
| `skill_relations` | from_skill, to_skill, relation (`prerequisite`/`related`/`part_of`/`alternative`), weight |
| `user_skills` | user_id, skill_id, proficiency (0–100), confidence (0–1), level_label (`novice`/`beginner`/`intermediate`/`advanced`/`expert`), last_evidenced_at, source_mix (JSONB), self_rating (0–100 nullable) |
| `skill_evidence` | user_skill_id, evidence_type (`github`/`project`/`experience`/`certification`/`education`/`assessment`/`self_report`/`resume_parse`), ref_id, weight, signal_value (0–1), recency_date, notes |

### 6.3 Assessments
| Table | Key columns |
|---|---|
| `assessment_instruments` | slug, name, version, kind (`personality`/`interests`/`learning_style`/`work_style`/`soft_skills`/`values`/`goals`), items_ref, scoring_ref, license |
| `assessment_sessions` | user_id, instrument_id, status, started_at, completed_at |
| `assessment_responses` | session_id, item_id, response_value, response_time_ms |
| `assessment_results` | session_id, trait_scores (JSONB), interpretation_json, reliability_flags (JSONB) |
| `career_goals` | user_id, target_roles (text[]), target_industries, target_locations, target_timeline_months, target_salary_min/max, work_preferences (remote/hybrid/onsite, startup/enterprise), constraints (text), priority_notes |

### 6.4 Careers and Market
| Table | Key columns |
|---|---|
| `roles` | slug, title, family (e.g., `software_engineering`, `data_ai`, `security`, `devops_cloud`, `product`, `design`, `business`, `research`, `hardware_embedded`, `entrepreneurship`), description, seniority_ladder (JSONB), onet_code, esco_uri, emerging (bool) |
| `role_requirements` | role_id, skill_id, importance (0–1), required_level (0–100), kind (`must`/`should`/`nice`), source |
| `role_trait_profile` | role_id, riasec_vector (6), big5_fit_vector (5), work_style_vector, soft_skill_weights (JSONB) |
| `market_sources` | slug, name, type, license, last_fetched_at, status |
| `market_snapshots` | id, taken_at, region, notes |
| `market_role_metrics` | snapshot_id, role_id, region, postings_count, postings_growth_90d, median_salary, salary_p25, salary_p75, currency, remote_share, experience_distribution (JSONB), source_id |
| `market_skill_metrics` | snapshot_id, skill_id, region, mention_count, growth_90d, co_occurrence (JSONB), source_id |
| `emerging_roles` | role_id, signal_strength (0–1), evidence (JSONB), first_seen |
| `salary_bands` | role_id, region, seniority, p10, p25, p50, p75, p90, currency, source_id, as_of |
| `job_postings_cache` | external_id, source_id, title, company, location, remote, url, description_hash, skills_extracted (text[]), posted_at, role_id (nullable), expires_at |
| `internship_listings` | same shape as postings plus `duration`, `stipend`, `eligibility` |

### 6.5 Learning Resources and Projects
| Table | Key columns |
|---|---|
| `learning_resources` | title, provider, type (`course`/`certification`/`book`/`video`/`docs`/`practice`/`bootcamp`), url, cost_amount, currency, is_free, duration_hours, level, skills_taught (via link with `coverage` 0–1), rating, language, last_verified_at, cert_issuer |
| `project_templates` | title, description, difficulty (1–5), est_hours, skills (link with weight), deliverables (text[]), rubric (JSONB), role_families (text[]), stack_options (JSONB), portfolio_value (0–1) |

### 6.6 Outputs (versioned)
| Table | Key columns |
|---|---|
| `score_runs` | user_id, engine_version, taxonomy_version, market_snapshot_id, input_hash, created_at |
| `scores` | score_run_id, kind (`profile`/`technical`/`non_technical`/`career_match`/`industry_demand`/`job_readiness`), subject (role_id nullable), value (0–100), band (`low`/`developing`/`solid`/`strong`/`exceptional`), explanation (JSONB), confidence (0–1) |
| `dna_profiles` | score_run_id, dimensions (JSONB), archetype, narrative, card_png_key |
| `skill_gaps` | score_run_id, role_id, skill_id, gap_size, priority, impact_on_readiness, reasoning |
| `recommendations` | user_id, score_run_id, kind (`career`/`course`/`project`/`internship`/`job`/`cert`), item_ref, rank, score, reasons (JSONB), status (`new`/`saved`/`dismissed`/`in_progress`/`done`), feedback |
| `roadmaps` | user_id, target_role_id, version, horizon_months, status, generated_from_score_run_id |
| `roadmap_milestones` | roadmap_id, order, phase, title, description, target_skills, resources (JSONB), projects (JSONB), est_hours, due_date, status, success_criteria, completed_at |
| `simulations` | user_id, kind, params (JSONB), results (JSONB), created_at |
| `notifications` | user_id, kind, payload, read_at |
| `audit_log` | user_id, action, entity, entity_id, at, meta |

---

## 7. Data Intake and Analysis

### 7.1 Onboarding Flow (MUST)
1. Sign up → choose persona (student / professional / switcher) → locale, country, currency.
2. **Fast Start (≤3 min):** upload resume OR paste LinkedIn-style text OR minimal form; connect GitHub (optional).
3. Review parsed data (editable, with confidence highlights).
4. Skills self-rating screen (grouped, with "I've used it / comfortable / could teach it" scale mapped to 0–100).
5. Assessments (short versions first; deep versions optional, resumable).
6. Career goals.
7. Generate first Twin → dashboard.

Users MUST be able to leave and resume at any step; a profile **completeness meter** (§8.1) guides them.

### 7.2 Resume / Document Parsing
- Accept PDF, DOCX, TXT, MD (≤10 MB). Extract text (pdfminer/pypdf, python-docx; OCR via Tesseract if scanned, as an optional flag).
- Pipeline: text extraction → section segmentation → LLM structured extraction (Pydantic schema validated; retry up to 2× on invalid JSON) → skill normalization (§7.4) → user review.
- Output fields match §6.1 tables. Each extracted field carries `confidence`. Fields < 0.6 confidence are flagged for review.
- **MUST** work with a local LLM fallback and a **no-LLM heuristic fallback** (regex + taxonomy alias matching) so the system functions offline.
- Resume text is not sent to any third-party LLM unless the instance admin enabled a remote provider AND the user consented (§14).

### 7.3 GitHub Analysis
Inputs: username (public data) or OAuth for private repo stats (opt-in, read-only scopes).
Metrics `metrics_json` (computed over last 24 months unless noted):
| Metric | Definition |
|---|---|
| `active_months` | months with ≥1 contribution / 24 |
| `contribution_consistency` | 1 − coefficient of variation of monthly contributions, clamped 0–1 |
| `public_repos`, `original_repos` | non-fork count |
| `language_bytes` | aggregated by language, weighted by recency |
| `stars_received`, `forks_received` | totals on owned repos |
| `prs_merged_external` | PRs merged into repos the user doesn't own |
| `issues_opened_closed` | counts |
| `review_activity` | PR reviews submitted |
| `oss_projects_contributed` | distinct external repos with merged PRs |
| `repo_quality_signals` | per top-10 repo: has README, license, tests dir/CI config, Dockerfile, docs, releases, topic tags |
| `collaboration_signal` | distinct collaborators / co-committers |
| `topic_skills` | skills inferred from languages, dependency manifests (`package.json`, `requirements.txt`, `pom.xml`, `Cargo.toml`, `go.mod`), topics, and Dockerfile/CI configs |

Rules:
- Respect GitHub API rate limits; use conditional requests (ETag) and cache; sync on connect and then weekly (configurable).
- Do not clone code by default. Manifest/README analysis via contents API only. No source code is stored; only derived metrics.
- Derived skills create `skill_evidence` rows with `evidence_type='github'`.

### 7.4 Skill Normalization and Taxonomy
- Seed taxonomy from open sources where licenses permit (ESCO, O*NET, plus project-authored extensions); record provenance. Ship ≥ 1,500 skills at MVP across categories: languages, frameworks, tools, cloud, databases, AI/ML, cybersecurity, dev, DevOps, soft skills, domain skills.
- Normalizer: exact alias match → fuzzy match (Jaro-Winkler ≥ 0.92) → embedding similarity (cosine ≥ 0.80) → LLM disambiguation (optional) → else create `unmapped_skill` queue for admin review.
- Taxonomy is versioned (`taxonomy_version` semver). Migrations of skill IDs MUST preserve user data via a mapping table.

### 7.5 Proficiency Estimation (per skill)
For each `user_skill`, proficiency `P` (0–100) is computed from evidence:

```
signal_i  = base_i × recency_i × depth_i          # each in [0,1]
P = 100 × (1 − Π_i (1 − w_i × signal_i))          # noisy-OR over evidence
confidence = min(1, Σ_i w_i × signal_i × reliability_i / C)   # C = 1.5 [CONFIG]
```
Evidence weights `w` [CONFIG defaults]:
| Evidence | w | Notes |
|---|---|---|
| Verified certification (proctored) | 0.55 | base by cert level |
| Work experience using skill | 0.60 | scaled by duration (months/24, cap 1) |
| Internship | 0.40 | |
| Project with repo + outcomes | 0.45 | complexity-scaled |
| GitHub usage (lang/dependency) | 0.40 | scaled by commits & recency |
| Education coursework | 0.25 | grade-scaled |
| Skills assessment (if available) | 0.60 | |
| Self-report | 0.20 | capped; down-weighted if contradicted by evidence |
| Resume mention only | 0.10 | |

`recency_i = 0.5^(age_months / half_life)`; half-life by skill category [CONFIG] (e.g., frameworks 30, languages 60, cloud tools 24, soft skills 120).
`level_label`: <20 novice, 20–39 beginner, 40–59 intermediate, 60–79 advanced, ≥80 expert.
Self-ratings that exceed evidence-derived P by >30 points produce a "calibration note" (non-judgmental) rather than altering P directly.

---

## 8. Assessments

### 8.1 Profile Completeness
`completeness = Σ section_weight × section_fill` with weights [CONFIG]: education 0.12, experience 0.15, skills 0.20, projects 0.10, certifications 0.05, GitHub/portfolio 0.08, assessments 0.20, goals 0.10. Dashboard shows completeness and warns that scores are lower-confidence if < 60%.

### 8.2 Instruments (MUST ship openly licensed items only)
| Dimension | Instrument | Length (short / full) | Output |
|---|---|---|---|
| Personality | Big Five via IPIP (public domain) | 50 / 120 | O, C, E, A, N percentiles |
| Interests | Holland RIASEC (open-licensed or project-authored items, e.g., O*NET Interest Profiler-style, authored originally) | 30 / 60 | R, I, A, S, E, C vector |
| Learning preferences | Project-authored items (modalities: visual/reading/hands-on/auditory; structure: guided/self-directed; pace; social: solo/group) | 20 | Preference vector (not "learning styles" claims; framed as preferences) |
| Work style | Project-authored (autonomy, structure, pace, collaboration, risk tolerance, remote preference) | 24 | Work-style vector |
| Non-technical skills | Situational judgment tests (SJTs) + behavioral self-ratings for: communication, leadership, teamwork, problem-solving, creativity, time management, project management, public speaking, entrepreneurship, critical thinking | 6 SJT + 6 ratings per skill (short: 2+2) | Skill scores 0–100 |
| Values & motivators | Project-authored (impact, income, stability, autonomy, mastery, prestige, balance) | 14 | Ranked values |
| Strengths/weaknesses | Derived (cross-instrument + evidence) + user free-text reflection | n/a | See §9.3 |

Question banks live in `packages/question-banks/*.yaml` with: `id`, `text`, `scale`, `reverse_scored`, `dimension`, `locale`, `license`, `source`. Include a validator test (no duplicate IDs, all dimensions covered, reverse-key counts balanced).

### 8.3 Scoring Rules
- Likert items 1–5; reverse-scored handled; dimension raw = mean; percentile via norm tables in `question-banks/norms.yaml` (placeholder norms clearly labeled; community can improve).
- Reliability flags: straight-lining (SD of responses < 0.3 over ≥ 20 items), implausibly fast (< 1.0 s median), inconsistency pairs. Flagged results lower `confidence` and show a gentle "retake suggested" message.
- Non-technical skill score per skill: `0.5 × SJT_score + 0.25 × self_rating_calibrated + 0.25 × evidence_score` where evidence_score comes from experiences/leadership roles/projects/awards via LLM-assisted tagging with human-visible rationale.
- Disclaimers: assessments indicate tendencies, not fixed traits or medical/psychological diagnoses. Results are editable by the user via "this doesn't sound like me" feedback, which is stored and can adjust interpretation text (not raw scores).

---

## 9. Intelligence Core: Scores and Analyses (normative formulas)

All scores 0–100, rounded to 1 decimal. Bands: 0–29 low, 30–49 developing, 50–69 solid, 70–84 strong, 85–100 exceptional. Every score stores `explanation = {factors:[{name, value, weight, contribution}], data_gaps:[...], confidence}`. Weights are `[CONFIG]` in `config/scoring.yaml`; defaults below.

### 9.1 Technical Skills Score (TSS)
Categories and default weights depend on the user's target role family (family-specific weight tables in config). Generic default:

| Component | Weight |
|---|---|
| Programming languages (breadth-depth blend) | 0.18 |
| Frameworks & libraries | 0.12 |
| Tools & technologies (version control, testing, build, etc.) | 0.08 |
| Cloud platforms | 0.10 |
| Databases & data systems | 0.08 |
| AI/ML | 0.12 |
| Cybersecurity | 0.08 |
| Software development practices (design, testing, code quality, system design) | 0.10 |
| DevOps (CI/CD, containers, IaC, observability) | 0.06 |
| Open-source & GitHub activity | 0.08 |

Component score = `0.7 × depth + 0.3 × breadth`, where depth = mean of top-k proficiencies in category (k=3, [CONFIG]) and breadth = min(1, distinct skills with P≥40 / breadth_target_category) × 100. When a target role is set, weights are re-normalized to emphasize role-required categories (`w' = 0.5 w + 0.5 role_importance`).
Open-source/GitHub component: `0.25 consistency + 0.20 external_PR_signal + 0.20 repo_quality + 0.15 stars/forks (log-scaled) + 0.10 reviews + 0.10 collaboration`.

### 9.2 Non-Technical Skills Score (NTSS)
Weighted mean of the 10 non-technical skills; default weights equal (0.10 each) but re-weighted by role trait profile when a target role is set. Add a **balance bonus**: +up to 3 points if min skill ≥ 40 (rewards no severe weak spot). Confidence reduced if skills rely only on self-report.

### 9.3 Strengths and Weaknesses
- **Strengths:** skills/traits with percentile ≥ 75 within the user's cohort definition (cohort = same persona and experience band, using anonymized aggregate stats if available, else fixed norms) AND confidence ≥ 0.5. Top 5–7 shown, each with the evidence list.
- **Weaknesses / development areas:** (a) lowest-scoring dimensions with high role importance; (b) assessment-flagged tendencies; phrased constructively, with an action. Limit to 5.
- **Hidden strengths:** high evidence, low self-rating (underestimation) surfaced as a distinct card.

### 9.4 Professional Profile Score (PPS)
```
PPS = 0.30 × TSS' + 0.20 × NTSS + 0.15 × Experience + 0.12 × Education
    + 0.08 × Certifications + 0.08 × Projects/Portfolio + 0.07 × Presence(GitHub/public work)
```
Where `TSS'` = TSS using target-role weights if set. Sub-scores:
- **Experience (0–100):** `min(100, Σ_exp value)`, value = type_weight × duration_factor × relevance (embedding similarity of experience description/skills to target role family) × achievement_signal. Type weights: job 1.0, internship 0.6, freelance 0.7, research 0.6, leadership 0.4, entrepreneurship 0.8, volunteer 0.3. Normalization by `experience_target(persona)`: student 30, graduate 50, professional 100 [CONFIG].
- **Education:** `0.5 × grade_normalized + 0.3 × institution/degree_relevance (relevance only, NOT institution prestige) + 0.2 × coursework_relevance`. **The system MUST NOT use institution prestige or name as a scoring factor** (fairness, §14).
- **Certifications:** relevance-weighted, diminishing returns: `100 × (1 − Π(1 − cert_value_j))`.
- **Projects/Portfolio:** `100 × (1 − Π(1 − project_value_k))`, project_value = complexity × completeness (has repo/demo/readme) × relevance × impact.

PPS exposes `confidence` as a function of completeness and evidence coverage.

### 9.5 Career Match Score (per role r)
```
CM(r) = 100 × ( 0.45 × SkillFit + 0.20 × InterestFit + 0.15 × PersonalityWorkStyleFit
              + 0.10 × ExperienceFit + 0.10 × GoalMarketAlignment ) × readiness_modifier
```
- **SkillFit** = `Σ_s imp_s × min(1, P_s / req_s) / Σ_s imp_s` over role requirements (must-have skills have a 1.5× importance multiplier; related-skill transfer credit: if user lacks skill s but has related skill s' with relation weight ω, credit = ω × P_s' / req_s, ω ≤ 0.6).
- **InterestFit** = cosine similarity of user RIASEC vector and role RIASEC vector, rescaled to 0–1.
- **PersonalityWorkStyleFit** = weighted similarity of Big Five & work-style vectors to role's `role_trait_profile`. Weight is intentionally modest; personality MUST NOT disqualify any role. UI text emphasizes "tends to fit" and shows adaptation tips.
- **ExperienceFit** = relevance of experience/seniority to the role's entry/target level.
- **GoalMarketAlignment** = `0.5 × alignment_with_stated_goals + 0.3 × normalized IndustryDemand(r, region) + 0.2 × salary_alignment_with_expectation`.
- `readiness_modifier` = 1 (default; the match score itself measures fit, not readiness). Readiness is shown separately (§9.7).
Output: ranked list of ≥ 10 roles across ≥ 4 families, each with a breakdown, top matching skills, top gaps, "why this fits / why it might not", and confidence. Must include at least 2 "stretch" and 2 "adjacent/emerging" roles flagged as such.

### 9.6 Industry Demand Score (per role, per region)
```
IDS(r, region) = 100 × ( 0.35 × norm(postings_count) + 0.25 × norm(growth_90d)
                       + 0.15 × norm(salary_median_vs_region_median)
                       + 0.15 × (1 − norm(supply_proxy)) + 0.10 × emerging_signal )
```
`norm` = percentile rank among roles within the same snapshot/region. `supply_proxy` = proxy for competition (e.g., postings per typical applicant pool estimate; if unavailable, set weight to 0 and renormalize, and record in explanation). Dashboard's **Industry Demand Score** shown for the user is the demand score for their top target roles (posting-weighted mean), plus a skill-level demand index:
`SkillDemand(s) = 0.6 × norm(mention_count) + 0.4 × norm(growth_90d)`.
Every IDS value stores `source_ids`, `snapshot_id`, `as_of`. If data older than `[CONFIG] 45 days` → show "stale data" badge.

### 9.7 Job Readiness Score (JRS) for target role r
```
JRS(r) = 100 × ( 0.40 × MustHaveCoverage + 0.20 × ShouldHaveCoverage
               + 0.15 × EvidenceOfApplication (projects/experience demonstrating role skills)
               + 0.10 × Credentials + 0.10 × InterviewReadiness + 0.05 × PublicPresence )
```
- `MustHaveCoverage` = fraction of must-have weight achieved with `P ≥ req_level × 0.8`.
- `InterviewReadiness` (MVP): based on self-assessed + quiz-based checks of fundamentals for the role (small adaptive quiz of ≥ 10 items from role question bank, optional); if absent, weight redistributed and flagged.
- Readiness bands & labels: <35 "Exploring", 35–54 "Building", 55–69 "Almost ready (internships/entry roles)", 70–84 "Ready", ≥ 85 "Highly competitive".
- Also output **time-to-ready estimate**: `Σ gap_hours / weekly_study_hours` using skill-gap hour estimates from `learning_resources` (±range, labeled as estimate).

### 9.8 Skill Gap Analysis
For role r: `gap_s = max(0, req_s − P_s)`. Priority:
```
priority_s = imp_s × gap_s_norm × (1 + demand_boost_s) × (1 + prerequisite_unlock_s) / effort_s
```
`prerequisite_unlock_s` = number of other missing skills that list s as prerequisite (normalized). Output ordered gaps with: current vs required, reason, effort estimate (hours), resources, and `impact_on_JRS` (computed by simulating closing that gap).

### 9.9 Professional DNA Profile
A compact fingerprint, deterministic from stored scores, with an LLM-written narrative (grounded, §11).
Dimensions (0–100 each, radar chart):
1. Technical Depth 2. Technical Breadth 3. Builder/Execution (projects, OSS) 4. Analytical/Problem-Solving 5. Creativity 6. Communication & Influence 7. Leadership & Initiative 8. Collaboration 9. Learning Agility (rate of skill growth, breadth of new skills over time, cert cadence) 10. Entrepreneurial Drive 11. Market Alignment (IDS-weighted skill fit) 12. Consistency (GitHub/learning cadence).
Plus: Holland code (top 3 RIASEC letters), Big Five summary, work-style tags, **archetype** (rule-based mapping into ~12 archetypes such as "Systems Builder", "Applied Researcher", "Security Sentinel", "Product-minded Engineer", "Data Storyteller", "Founder-type Generalist"), top 5 strengths, top 3 growth edges, one-line positioning statement.
Archetype rule: nearest-centroid on the dimension vector against archetype centroids in `config/archetypes.yaml`; show top-2 with percentages. Narrative MUST NOT contradict the numbers (validated by a post-check, §11.5).
Export: shareable PNG/PDF card (v1.0), default private.

---

## 10. Recommendations, Roadmap, Simulation, Market

### 10.1 Career Recommendation (feature 4)
Rank by `0.6 × CM(r) + 0.25 × IDS(r) + 0.15 × growth_potential(r)` where growth_potential from salary progression slope & seniority ladder. Diversification rule (MMR): no more than 4 roles from the same family in top 10. Each recommendation includes a rationale generated from stored factors (template first; LLM may polish wording but not change facts).

### 10.2 Market Intelligence and Trend Tracking (feature 5)
**Connector interface** (plugins implement):
```python
class MarketConnector(Protocol):
    slug: str
    def fetch(self, region: str, since: datetime) -> Iterable[RawRecord]: ...
    def normalize(self, rec: RawRecord) -> NormalizedRecord: ...  # to role/skill metrics, postings, salary
    def license_info(self) -> LicenseInfo: ...
```
Built-in connectors (use only those with permissive/official API access; each behind an enable flag and API-key config):
- Open datasets: O*NET, ESCO, BLS OEWS (US), Stack Overflow Developer Survey, GitHub Innovation Graph / Octoverse-style public data, World Economic Forum / other open "future of jobs" reports (manually curated YAML with citation).
- Job APIs (user-supplied keys): e.g., Adzuna, Remotive, Arbeitnow, USAJobs, others via plugins. India-region support (e.g., INR salary bands and local sources) MUST be possible via configuration and plugin without code changes.
- Curated internship sources (public APIs/RSS where allowed).
Trend Engine (daily job):
1. Ingest → deduplicate (`description_hash`) → extract skills (taxonomy matcher + optional LLM) → map to roles (embedding + title rules).
2. Aggregate into a `market_snapshot` (weekly canonical snapshot; daily deltas).
3. Compute `growth_90d` (log ratio vs 90-day-ago snapshot, smoothed with min-count threshold 30).
4. **Emerging role detection:** titles/skills clusters with growth z-score > 2 AND count above floor AND not mapped to an existing role → candidate `emerging_roles` (admin approve or auto-add with `emerging=true`, confidence ≥ 0.7).
5. **Future skill requirements:** project skill demand 12–24 months using damped trend (Holt linear) + curated forecast sources; label as "projected," show uncertainty band, and always include method note. Dashboard "Future Skill Requirements" lists top skills relevant to the user's targets with `now`, `projected`, and `user_current_level`.
Cold start: ship a sample snapshot in `data/seeds/` so the system works with no API keys.

### 10.3 Learning Resource Recommendation (feature 6)
Candidates = resources covering the user's prioritized gaps. Rank:
```
score = 0.35 × gap_coverage_value + 0.15 × level_match + 0.15 × quality(rating, provider trust)
      + 0.10 × cost_fit(budget, free preference) + 0.10 × learning_preference_fit
      + 0.10 × time_fit(hours/week) + 0.05 × cert_value_for_role
```
Rules: include a mix (≥ 1 free option per top gap; ≥ 1 certification where relevant); respect learning preferences (video/reading/hands-on, guided vs. self-paced); no sponsored ranking; show `last_verified_at`; background link-checker job flags dead links weekly. Seed ≥ 300 curated, free/open resources at MVP (docs, open courseware, official certs, etc.); the community can add via PR to `data/seeds/learning_resources/*.yaml` (schema-validated).

### 10.4 Project Recommendation (feature 7)
From `project_templates` + LLM-assisted customization:
`score = 0.40 × skill_gap_closure + 0.20 × portfolio_value_for_role + 0.15 × difficulty_fit (stretch of +1 level) + 0.15 × interest_alignment + 0.10 × time_fit`.
Each suggestion contains: title, problem statement, why it helps (linked to gaps/JRS delta), suggested stack (uses skills the user is learning), milestones, deliverables, "definition of done," rubric, and "how to showcase" (README checklist, demo, metrics). Support three tiers: Starter (≤10h), Portfolio (20–60h), Capstone (80h+). Users can mark projects in-progress/done with a repo URL, which creates evidence (§7.5) and triggers a re-score.

### 10.5 Roadmap Generation (feature 9)
Input: target role, horizon (3/6/12/24 months), weekly hours, budget, learning preferences, current gaps.
Algorithm:
1. Order gaps by priority §9.8, respecting prerequisites (topological sort over `skill_relations`).
2. Pack into phases (Foundation → Core Skills → Applied Projects → Specialization → Job Search/Interview → Growth). Capacity per month = weekly_hours × 4.3 × 0.8 (slack).
3. For each milestone: skills, resources (from §10.3), a project (from §10.4), `success_criteria` (measurable, e.g., "Pass practice exam ≥ 75%", "Deploy app with CI/CD"), estimated hours, due date, expected `JRS_delta`.
4. Insert checkpoints every 4–6 weeks (reassess scores, adapt plan).
5. LLM may write motivational copy and refine milestone descriptions; structure/dates/hours are computed by code. Output validated against a JSON schema.
Re-planning: when milestones slip or scores change, the planner recomputes remaining work and shows a diff ("moved X to month 3 because…"). Users can edit/reorder/add milestones; manual edits are preserved across regenerations (locked flag).

### 10.6 Internship and Job Role Recommendations (feature 10)
Match user vector against cached postings/internships:
`score = 0.45 × skill_match(posting.skills_extracted, user_skills) + 0.20 × role/title match + 0.15 × location/remote/work-pref fit + 0.10 × eligibility fit (grad year, degree) + 0.10 × recency`.
Show missing skills per posting, "apply now" vs "prepare first" label (based on JRS-for-that-posting ≥ threshold), and deep link out. No auto-apply. Show data source and posted date. For students prioritize internships by graduation year and branch eligibility.
**Target Roles** (dashboard) = the user's chosen targets plus top recommended roles, each with JRS, IDS, CM.

### 10.7 Career Growth and Salary Simulation (feature 11)
Inputs: current role/level (or "entering"), target role path, region/currency, years horizon (1–15), assumptions (study hours, job-change frequency, performance level: below/avg/above, upskilling on/off), risk tolerance.
Model (transparent, in code, Monte Carlo N=2,000 [CONFIG]):
- State = (role, level, skills vector summary). Each year transition probabilities for promotion, lateral move, role change, stagnation depend on: JRS for next level, performance assumption, market growth of role, tenure (hazard function), and upskilling.
- Salary(t) drawn from the regional salary band for (role, level) with percentile placement tied to skill strength & negotiation assumption; annual raise distribution by level; market growth adjusts bands via role demand trend (capped ±3%/yr).
- Output: median, p10, p90 salary paths; probability of reaching target level/role by year; "what-if" comparisons (with vs. without roadmap, switching to an emerging role, adding a certification); sensitivity chart (which assumption matters most).
- UI MUST display: "Projection, not a prediction; based on [sources], [as_of]; actual results vary." Salary bands without sufficient data show ranges with a "low data" label, never false precision.
Seed ≥ 40 roles with salary bands for ≥ 3 regions including India (INR) and US (USD), clearly marked as sample data until a real source is configured.

### 10.8 Continuous Update Loop (feature 12) (MUST in v0.5+)
Triggers:
| Trigger | Action |
|---|---|
| Daily/weekly schedule | Pull market data → new snapshot → recompute IDS, emerging roles, future skills |
| User profile change (new skill, cert, project, GitHub sync, assessment) | Recompute affected scores (incremental via dependency graph, else full) |
| Milestone completed/overdue | Update roadmap + readiness + next best action |
| Taxonomy/engine version bump | Backfill recompute with versioned runs |
| Monthly | "Career check-in" summary |
Change detection: compare new `score_run` to previous; generate a **"What changed"** feed (e.g., "Demand for Kubernetes in your region +12% → raised priority of K8s gap," "Your JRS for Backend Engineer rose 4.2 points after Project X"). Notifications: in-app, email (SMTP configurable), and optional webhooks. Users can mute categories and set frequency. Recompute jobs MUST be idempotent, rate-limited, and observable. Keep full score history for trend charts.

### 10.9 AI Mentor (lifelong mentor chat)
- Chat that answers questions about the user's own twin, scores, plan, and the market, using tool calls: `get_profile`, `get_scores`, `get_gaps`, `get_roadmap`, `query_market(role|skill, region)`, `search_resources`, `simulate(params)`, `update_goal`.
- Must cite the data (score run id, snapshot date) for numeric claims. If a tool lacks data: say so; never fabricate market stats, salaries, or links.
- Capabilities: explain scores ("why is my JRS 58?"), what-if ("what if I learn Terraform?"), weekly planning, interview prep Q&A (MVP: practice questions with feedback), resume bullet improvement, mock decision support.
- Tone: encouraging, honest, specific; never guarantees outcomes; avoids discouraging absolutes.
- Safety: crisis/mental-health sensitive statements → supportive response + suggest professional help resources; do not diagnose. Prompt-injection resistant (see §11.4).

---

## 11. LLM Layer

### 11.1 Interface
```python
class LLMClient(Protocol):
    def complete(self, messages: list[Msg], *, schema: type[BaseModel] | None = None,
                 temperature: float = 0.2, max_tokens: int = 2000, tools: list[Tool] | None = None) -> LLMResult: ...
    def embed(self, texts: list[str]) -> list[list[float]]: ...
```
Adapters: Ollama, OpenAI-compatible HTTP, Anthropic, plus `MockLLM` for tests (deterministic fixtures). Config: `LLM_PROVIDER`, `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`, `EMBED_MODEL`.

### 11.2 Required Prompt Tasks (versioned in `services/llm/prompts/`, each with a JSON schema, golden tests)
1. `resume_extract` → structured profile JSON.
2. `skill_extract_from_text` → list of {raw, normalized_candidate, evidence_snippet}.
3. `nontech_evidence_tagger` → tags experiences with soft-skill evidence + rationale.
4. `dna_narrative` → ≤ 250 words from the numeric DNA vector (inputs are numbers + top evidence only).
5. `recommendation_explainer` → plain-language "why" from factor list.
6. `roadmap_polish` → improves text only; structural fields are immutable inputs.
7. `project_customizer` → tailors a template to the user's stack/interests.
8. `mentor_chat` (tool-using).
9. `job_posting_skill_extract` (for the trend engine; batch, cheap model OK).
10. `interview_question_gen` + `answer_feedback`.

### 11.3 Quality Controls
- All structured outputs validated by Pydantic; on failure retry with error feedback ≤ 2×, then fall back to heuristic path or surface "couldn't parse, please edit manually."
- Temperature ≤ 0.3 for extraction; response caching keyed by (prompt_version, input_hash).
- Token/cost accounting per user/task, with per-user daily caps [CONFIG] for hosted instances.

### 11.4 Safety / Security of LLM use
- Treat all user-provided documents and scraped postings as **untrusted data**: wrap in delimiters, instruct the model to ignore instructions inside them, and strip/escape control sequences. Tool calls in mentor chat are scoped to the authenticated user; server enforces `user_id` on every tool (the model never supplies it).
- No secrets in prompts. PII minimization: send only fields needed for the task.
- Output filters: block links not present in DB for resource recommendations.

### 11.5 Consistency Checks
Post-generation validators: narrative numbers/claims vs. stored values (regex + comparison), no invented certifications/companies, no salary figures not in `salary_bands`. Failures → regenerate once, then fall back to template text.

---

## 12. API Specification (REST, `/api/v1`, OpenAPI auto-generated)

Auth: Bearer JWT. Pagination `?limit&cursor`. Errors RFC 7807 problem+json. Rate limiting per IP/user.

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `GET /auth/oauth/{provider}/start|callback`, `POST /auth/password/reset` |
| User | `GET/PATCH /me`, `DELETE /me` (full deletion), `GET /me/export` (JSON+ZIP of all data), `GET/PATCH /me/consents` |
| Profile | CRUD: `/me/education`, `/me/certifications`, `/me/experiences`, `/me/projects`, `/me/awards`; `GET /me/completeness` |
| Documents | `POST /me/documents` (multipart), `GET /me/documents/{id}`, `POST /me/documents/{id}/parse`, `POST /me/documents/{id}/apply` (commit parsed data after review) |
| GitHub | `POST /me/github/connect`, `POST /me/github/sync`, `GET /me/github` |
| Skills | `GET /skills?q=`, `GET /me/skills`, `PUT /me/skills/{skill_id}` (self-rating), `GET /me/skills/{id}/evidence` |
| Assessments | `GET /assessments`, `POST /assessments/{slug}/sessions`, `PUT /assessments/sessions/{id}/responses`, `POST /assessments/sessions/{id}/complete`, `GET /me/assessment-results` |
| Goals | `GET/PUT /me/goals` |
| Twin | `POST /me/twin/generate` (async → job id), `GET /me/twin` (latest), `GET /me/twin/history`, `GET /me/twin/dna`, `GET /me/twin/diff?from&to` |
| Scores | `GET /me/scores` (all), `GET /me/scores/{kind}`, `GET /me/scores/explain/{score_id}` |
| Careers | `GET /me/careers` (ranked matches), `GET /me/careers/{role_slug}` (detail+gap), `GET /roles`, `GET /roles/{slug}` |
| Gaps | `GET /me/gaps?role=` |
| Market | `GET /market/roles?region=`, `/market/skills?region=`, `/market/trends`, `/market/emerging`, `/market/future-skills?role=`, `/market/sources`, `GET /market/snapshots/latest` |
| Recommendations | `GET /me/recommendations?kind=courses|projects|internships|jobs|certs`, `POST /me/recommendations/{id}/feedback`, `PATCH /me/recommendations/{id}` (status) |
| Roadmap | `POST /me/roadmaps` (generate), `GET /me/roadmaps/active`, `PATCH /me/roadmaps/{id}/milestones/{mid}`, `POST /me/roadmaps/{id}/replan` |
| Simulation | `POST /me/simulations/career`, `GET /me/simulations/{id}` |
| Mentor | `POST /me/mentor/chat` (SSE streaming), `GET /me/mentor/conversations` |
| Notifications | `GET /me/notifications`, `PATCH /me/notifications/{id}`, `GET/PUT /me/notification-settings` |
| Dashboard | `GET /me/dashboard` (aggregated payload; see §13) |
| Admin | `GET/POST /admin/taxonomy/*`, `/admin/market/connectors/*` (enable, run now), `/admin/unmapped-skills`, `/admin/jobs`, `/admin/health` |

Async jobs return `202 {job_id}`; poll `GET /jobs/{id}` or subscribe via SSE `/me/events`.
**Dashboard payload** (`GET /me/dashboard`) MUST contain: `scores{profile,technical,non_technical,career_match_top,industry_demand,job_readiness}` each with `value, band, delta_since_last, confidence, as_of`; `dna`; `strengths[]`; `gaps[]`; `careers[]`; `roadmap_summary`; `courses[]`; `projects[]`; `target_roles[]`; `future_skills[]`; `whats_changed[]`; `data_quality{completeness, stale_sources, warnings}`.

---

## 13. Frontend / Dashboard Requirements

### 13.1 Pages
1. **Landing/Docs** (static), 2. **Auth**, 3. **Onboarding wizard** (resumable), 4. **Dashboard**, 5. **Profile editor**, 6. **Skills explorer** (graph/table with evidence drill-down), 7. **Assessments**, 8. **DNA Profile**, 9. **Careers** (list + detail with fit breakdown), 10. **Gap analysis**, 11. **Roadmap** (timeline/kanban toggle), 12. **Learning** (courses/certs), 13. **Projects**, 14. **Jobs & Internships**, 15. **Market Insights** (demand, trends, emerging roles, future skills), 16. **Simulator**, 17. **Mentor chat**, 18. **Settings** (privacy, consents, integrations, export/delete, notifications, language/currency), 19. **Admin** (role-gated).

### 13.2 Dashboard Layout (MUST include all)
| Section | Content |
|---|---|
| Header strip | **Professional Profile Score** (gauge + band + Δ) · **Technical Skills Score** · **Non-Technical Skills Score** · **Career Match Score** (top role + score) · **Industry Demand Score** · **Job Readiness Score** (for selected target role, selector) |
| DNA | Radar chart + archetype + one-line positioning |
| Strengths & Gaps | Top strengths (with evidence chips) and prioritized gaps (with "+N JRS if closed") |
| Career Matches | Ranked cards with fit breakdown bars, demand badge, "emerging" flag |
| **Personalized Career Roadmap** | Phase timeline, current milestone highlighted, progress %, next best action |
| **Suggested Courses** | 3–6 items with cost/duration/level/free badge, "why" tooltip |
| **Suggested Projects** | 3–4 items with tier, hours, skills, JRS impact |
| **Target Roles** | Roles with CM/IDS/JRS and time-to-ready |
| **Future Skill Requirements** | Skill list: now vs. projected demand, your level, trend arrows, uncertainty marker |
| What changed | Feed of deltas since last visit |
| Data quality | Completeness meter, stale-data warnings, low-confidence flags |

### 13.3 UX Requirements
- Every score is clickable → **explanation drawer** (factors, weights, evidence, data gaps, how to improve).
- Show confidence visibly (e.g., hatched gauge edge) and avoid false precision for low-confidence values (show range or "estimated").
- Loading states for async generation with progress (steps: parsing → analyzing → scoring → matching → planning).
- Accessible: keyboard navigation, ARIA labels, color-blind-safe palettes, charts have table alternatives, dark/light themes, mobile-first responsive.
- i18n-ready from day one (English at MVP; string extraction for others), currency/units by locale.
- Empty states guide the user to the next best action; never show blank dashboards.
- Tone guidelines: constructive, non-judgmental; "development areas" not "failures."

---

## 14. Privacy, Security, Ethics, Fairness

### 14.1 Privacy (MUST)
- Data minimization; explicit, granular consents (resume processing, GitHub, remote LLM use, anonymized analytics, mentor sharing).
- User can export all data and delete account (hard delete within 30 days, immediate soft delete, backups age out).
- Sensitive attributes (gender, caste, religion, ethnicity, disability, health, marital status, age) are **not collected** and not used in scoring. If a resume contains them, the parser discards them.
- Default: profiles private; shareable DNA card is explicit opt-in with a revocable link.
- Telemetry off by default for self-hosted; if enabled, aggregate, anonymized, documented.
- GDPR/CCPA/India DPDP-aware design (consent records, purpose limitation, deletion).

### 14.2 Security (MUST)
- OWASP ASVS L2 targets: argon2id hashing, short-lived JWT + rotating refresh, CSRF protections for cookie flows, strict CORS, rate limiting, input validation, file-upload scanning (type/size checks, optional ClamAV), signed URLs for documents, encryption at rest for tokens (e.g., Fernet/KMS) and TLS in transit, secrets via env/secret manager, dependency scanning (Dependabot/pip-audit/npm audit), SAST (CodeQL/Bandit), SBOM on release.
- Row-level authorization on every query (`user_id` scoped); tests for IDOR.
- Audit log for sensitive actions.
- `SECURITY.md` with disclosure process.

### 14.3 Fairness and Responsible AI (MUST)
- No use of institution prestige, name, gender, age, nationality, or other protected attributes in any score or ranking. Provide a **bias test suite**: counterfactual tests swapping non-skill attributes (e.g., institution name, names) must yield identical scores (tolerance 0).
- Personality and interests influence *suggestions only* and never block any role; always show skills-based paths.
- Transparency: model/method card in `docs/model-card.md` describing data sources, formulas, limitations; "How this was calculated" is available for every metric.
- Human override: users can correct any parsed/inferred item; corrections win over inference.
- Anti-hype: no guarantees; salary/career projections labeled probabilistic. Provide "limitations" text where data is sparse.
- Misuse prevention: ToS/README prohibit employer screening use; no API to retrieve other users' profiles; aggregate stats require k-anonymity (k ≥ 20).

---

## 15. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Dashboard API p95 ≤ 500 ms (cached scores); twin generation ≤ 60 s p95 with a local small model, ≤ 30 s with hosted; resume parse ≤ 30 s |
| Scalability | Stateless API; horizontal worker scaling; supports 10k users on a single mid-size node; DB indexes on all FK/`user_id`/`role_id`/`snapshot_id` |
| Reliability | Jobs retried with backoff; dead-letter queue; graceful degradation if LLM/market sources are down (use cache + show banner) |
| Offline/Local mode | Full MVP flow works with Ollama + seed data, no external internet except optional GitHub |
| Portability | `docker compose up` brings the whole stack; ARM64 + AMD64 images |
| Observability | Request tracing, job metrics, LLM latency/cost, data freshness gauges, health endpoints `/healthz`, `/readyz` |
| Accessibility | WCAG 2.1 AA |
| Maintainability | Type hints required, `ruff` + `mypy --strict` on core modules, ESLint + `tsc --noEmit`, pre-commit hooks |
| Documentation | README quickstart (≤ 10 min), architecture docs, taxonomy contribution guide, connector plugin guide, ADRs |
| Licensing hygiene | `THIRD_PARTY_LICENSES.md`; each dataset/question bank records license and attribution; CI check for missing license fields |

---

## 16. Testing and Evaluation

### 16.1 Test Pyramid
- **Unit:** every formula in §7.5, §9, §10 with golden-value tests; property tests (monotonicity: adding evidence never lowers proficiency; closing a gap never lowers JRS; scores ∈ [0,100]).
- **Integration:** ingestion → skills → scores pipeline on fixtures; connector contract tests with recorded responses (VCR); migration tests.
- **E2E (Playwright):** onboarding → dashboard; edit profile → score delta; roadmap generate → complete milestone → replan; export/delete account.
- **LLM tests:** schema-validity tests with MockLLM; golden extraction set (≥ 30 resumes, synthetic) with field-level F1 targets (≥ 0.85 for skills, ≥ 0.9 for education/experience dates on structured resumes); prompt-injection test set (resumes containing "ignore previous instructions…") must not alter outputs.
- **Fairness tests:** counterfactual invariance (§14.3).
- **Security tests:** IDOR, authz, upload abuse, rate limit.
- **Load test:** k6 script for dashboard and twin generation.

### 16.2 Evaluation of Recommendation Quality
- Offline: curated persona set (`data/fixtures/personas/*.yaml`, ≥ 25 personas across branches/levels) with expert-labeled acceptable career/role sets; metric: top-5 hit rate ≥ 0.8, gap precision ≥ 0.8.
- Online (optional, opt-in): thumbs up/down and "did this help?" feedback logged to improve weights; a documented process for tuning `scoring.yaml` via PR with evidence.

### 16.3 Definition of Done (per feature)
Code + types + unit/integration tests + docs + OpenAPI updated + migration + seed data (if any) + accessibility check + explanation/“how calculated” text + feature flag if risky + CI green.

---

## 17. Extensibility and Configuration

- **Plugin system (v1.0; interfaces exist from MVP):** Python entry points `dct.connectors`, `dct.assessments`, `dct.scorers` (custom score components), `dct.resources` (course catalogs). Plugins declare `license`, `data_access`, and `config_schema`.
- **Config files:** `config/scoring.yaml` (weights, half-lives, thresholds), `config/archetypes.yaml`, `config/market.yaml` (regions, sources, schedules), `config/features.yaml` (flags), `.env` for secrets.
- **Regions:** configurable region list with currency, locale, salary tables, job sources; default regions at launch: Global, India, US, UK, EU.
- **Community content:** taxonomies, roles, resources, project templates, and question banks are YAML + JSON Schema with CI validation; PR templates for adding them.

---

## 18. Build Plan for the Implementing Agent

### 18.1 Ground Rules
1. Work milestone by milestone; each ends with passing tests and a runnable `docker compose up`.
2. Never hardcode weights/thresholds; use config.
3. Write the explanation object for every score at the time of computing it.
4. Commit small, with conventional commits; record ADRs for non-obvious choices.
5. Use fixtures/seed data so every milestone is demoable without external keys.
6. Do not fabricate data sources: where real data is missing, seed clearly labeled `sample` data and mark `source=sample`.

### 18.2 Milestones and Tasks

**M0: Foundations**
- Monorepo scaffold, Docker Compose (api, web, worker, postgres+pgvector, redis), Makefile, CI, linting, pre-commit.
- Config system, logging, health endpoints, Alembic baseline, OpenAPI → TS types generation.
- *Accept:* `make dev` runs; `/healthz` ok; CI green.

**M1: Auth, Profile CRUD, Consents**
- Auth (email + OAuth GitHub), JWT, user settings, consents, data export/delete.
- Profile tables + CRUD + completeness meter + onboarding wizard UI skeleton.
- *Accept:* E2E signup → fill profile → completeness updates; delete account removes all rows.

**M2: Taxonomy and Skills**
- Taxonomy package + loader + validators + seed (≥ 1,500 skills, ≥ 60 roles with requirements and trait profiles, relations).
- Normalizer (alias/fuzzy/embedding), unmapped queue, skills explorer UI, self-rating.
- *Accept:* normalization precision ≥ 0.9 on test list; taxonomy CI checks pass.

**M3: Ingestion**
- Resume upload/parse (LLM + heuristic fallback), review UI, apply flow.
- GitHub analyzer (public API), metrics, derived skills/evidence.
- LLM client + adapters + MockLLM + prompt versioning.
- *Accept:* golden resume set meets F1 targets; GitHub sync produces evidence rows; injection tests pass.

**M4: Assessments**
- Question banks (Big Five/IPIP, RIASEC, learning, work style, values, soft-skills SJT), engine, scoring, reliability flags, UI with resume/save progress.
- Non-technical evidence tagger.
- *Accept:* bank validator passes; scoring unit tests; results page renders.

**M5: Scoring Engine**
- Proficiency estimation, TSS, NTSS, PPS, strengths/weaknesses, DNA + archetypes, versioned `score_runs`, explanations, confidence.
- Twin generation job + `GET /me/twin`, explanation drawer.
- *Accept:* golden tests for all formulas; monotonicity property tests; fairness counterfactual tests pass.

**M6: Market Intel (seed first, connectors second)**
- Seed snapshot, `MarketConnector` interface, 2+ open-data connectors (O*NET/ESCO-based mapping; one job API connector behind a key), trend engine, IDS, skill demand, emerging roles, future skills.
- *Accept:* IDS computed from seed snapshot; connector contract tests; staleness badges.

**M7: Matching, Gaps, Readiness**
- Career match, recommendations ranking, gap analysis with JRS impact simulation, JRS + time-to-ready.
- Careers/Gap UI.
- *Accept:* persona fixtures meet top-5 hit-rate; "close gap → JRS up" property test.

**M8: Learning, Projects, Roadmap**
- Resource catalog seed (≥ 300), project templates (≥ 60), rankers, roadmap generator + replan, milestone UI, evidence creation on completion.
- *Accept:* roadmap respects prerequisites and capacity; locked edits preserved on regenerate.

**M9: Dashboard**
- Aggregated endpoint + full dashboard per §13.2, explanation drawers, what-changed feed, data-quality panel.
- *Accept:* all required dashboard sections render with seed persona; Lighthouse a11y ≥ 90.

**M10: Jobs/Internships, Simulator, Mentor**
- Job/internship cache + matching UI; Monte Carlo simulator + UI; mentor chat with tools and grounding checks.
- *Accept:* simulator deterministic given seed; mentor refuses to invent market data (test); tool authz tests.

**M11: Continuous Updates and Notifications**
- Scheduler (Celery beat), incremental recompute, diff engine, notifications (in-app/email/webhook), settings.
- *Accept:* simulated market change generates "what changed" entries and updates ranks; idempotency tests.

**M12: Hardening and Release**
- Security review checklist, load tests, docs (README, architecture, model card, contribution guides), sample data disclaimers, v0.1.0 release (images, SBOM, changelog), plugin interfaces documented.
- *Accept:* all CI gates pass; fresh-clone quickstart ≤ 10 min on a clean machine.

### 18.3 Seed Data Deliverables (shipped in repo)
- ≥ 1,500 skills (with aliases & categories), ≥ 60 roles across ≥ 8 families (including emerging: AI/LLM engineer, MLOps, AI security, platform engineer, data/AI product roles), ≥ 40 roles with salary bands (sample) for Global/India/US.
- ≥ 300 learning resources, ≥ 60 project templates, ≥ 25 persona fixtures, ≥ 30 synthetic resumes, 1 sample market snapshot.
- Each file has `source`, `license`, `as_of`.

### 18.4 Suggested Default Role Families (taxonomy seed)
Software Engineering (backend, frontend, full-stack, mobile) · Data & AI (data analyst, data scientist, ML engineer, AI/LLM engineer, MLOps, data engineer) · Cloud & DevOps (DevOps, SRE, cloud architect, platform engineer) · Cybersecurity (SOC analyst, pentester, security engineer, GRC) · Embedded/Hardware · QA/Test Automation · Product & Project Management · UX/UI Design · Research & Academia · Business/Consulting · Entrepreneurship/Founder · Technical Writing/DevRel.

---

## 19. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| LLM extraction errors | Wrong profile | Review-before-commit, confidence flags, heuristic fallback, golden tests |
| Market data licensing/availability | Stale or illegal data | Official APIs/open datasets only, source/license tracking, seed fallback, staleness badges |
| Score trust/over-reliance | Harm from false precision | Explanations, confidence, ranges, disclaimers, user overrides |
| Bias in recommendations | Unfair outcomes | No protected/prestige features, counterfactual tests, diverse role exposure, model card |
| Privacy breach | Severe | Minimization, encryption, authz tests, local-LLM option, delete/export |
| Taxonomy drift | Broken comparisons | Versioning, mapping tables, recompute with versioned runs |
| Scope creep | Delays | Strict MVP boundary, phased roadmap, feature flags |
| Cold start (no market keys) | Poor first run | Seed snapshot + sample data labeled as such |
| Contributor friction | Low adoption | Great docs, good-first-issues, schema-validated content PRs |

---

## 20. Open Questions (decide via ADR; defaults provided)
1. Default region at first launch → **Global with auto-suggest from user's country**.
2. Hosted vs. self-host-only at v0.1 → **Self-host-first**, hosted instance optional later.
3. Paid features → **None; keep core free/open**. Any hosted-instance monetization must not alter rankings (no sponsored recommendations).
4. Mentor/educator cohort views → **v1.0**, with explicit student consent and k-anonymity.
5. Rubric for "verified" certifications → **v0.5**: URL/credential ID check for supported issuers (AWS, Google, Microsoft, Cisco, CompTIA, etc.); otherwise unverified with lower weight.

---

## 21. Glossary
- **Digital Career Twin (DCT):** structured, evolving model of a user's skills, traits, evidence, and goals.
- **DNA Profile:** compact multidimensional fingerprint plus archetype and narrative.
- **TSS / NTSS / PPS / CM / IDS / JRS:** Technical Skills / Non-Technical Skills / Professional Profile / Career Match / Industry Demand / Job Readiness scores.
- **Evidence:** any artifact supporting a skill claim, with weight and recency.
- **Snapshot:** a dated, versioned aggregate of market data.
- **Score run:** a reproducible computation tied to engine, taxonomy, and market versions.

---
*End of PRD.*
