# Work Plan: Digital Career Twin (DCT)

| Field | Value |
|---|---|
| Companion to | `prd.md`, `technical-design.md` |
| Planning basis | 1 sprint = 2 weeks. Estimates in **ideal engineer-days (ed)**. Calendar durations assume the staffing below. |
| Target | **v0.1.0 (MVP) in 24 weeks (12 sprints)**; **v0.5 at +10 weeks**; **v1.0 at +12 weeks** |

---

## 1. Team and Roles

### 1.1 Recommended Team (human-led)
| Role | Count | Focus |
|---|---|---|
| Tech lead / architect | 1 | Architecture, reviews, ADRs, scoring engine |
| Backend engineers | 2 | API, ingestion, matching, market intel |
| ML/NLP engineer | 1 | LLM layer, parsing, embeddings, evaluation |
| Frontend engineer | 2 | Dashboard, onboarding, charts |
| Data/content curator | 1 (part-time) | Taxonomy, roles, resources, question banks |
| QA / SDET | 1 | E2E, fairness, load, security tests |
| Designer (UX) | 0.5 | Flows, design system, accessibility |
| DevOps | 0.5 | CI/CD, deploy, observability |
| Product owner | 0.5 | Priorities, acceptance, community |

### 1.2 If built primarily by coding agents
Agents execute tasks from section 4 in order; a human reviewer approves each milestone gate. Keep tasks small (≤ 2 ed), require tests in the same PR, and keep each agent run scoped to one task ID.

---

## 2. Timeline Overview

| Sprint | Weeks | Milestone | Outcome |
|---|---|---|---|
| S0 | 0–1 (week zero) | Setup | Repo, CI, design kickoff, content plan |
| S1 | 1–2 | **M0** Foundations | `make dev` works, CI green |
| S2 | 3–4 | **M1** Auth, profile, consents | Users can sign up and fill profile |
| S3 | 5–6 | **M2** Taxonomy & skills | Skills normalizer, seed data v1 |
| S4 | 7–8 | **M3** Ingestion | Resume + GitHub import |
| S5 | 9–10 | **M4** Assessments | All instruments live |
| S6 | 11–12 | **M5** Scoring engine | Scores + DNA computed with explanations |
| S7 | 13–14 | **M6** Market intel (seed + 2 connectors) | Demand scores, emerging roles |
| S8 | 15–16 | **M7** Matching, gaps, readiness | Career match + JRS |
| S9 | 17–18 | **M8** Learning, projects, roadmap | Roadmap generated/replanned |
| S10 | 19–20 | **M9** Dashboard | Full dashboard per PRD §13.2 |
| S11 | 21–22 | **M12-a** Hardening | Security, perf, a11y, docs |
| S12 | 23–24 | **Release v0.1.0** | Public MVP, community launch |
| S13–S17 | 25–34 | **v0.5**: M10 (jobs, simulator, mentor), M11 (continuous updates) | Live loop |
| S18–S23 | 35–46 | **v1.0**: plugins, mentor/educator view, PDF/DNA card, i18n, Helm | Full release |

Content work (taxonomy, resources, projects, questions) runs **in parallel from S0** and is on the critical path for S3, S5, S8.

---

## 3. Critical Path and Dependencies

```
M0 → M1 → M2 → M3 ─┐
           │        ├→ M5 → M7 → M8 → M9 → Hardening → v0.1.0
           └→ M4 ───┘     ↑
M2 → M6 (seed snapshot) ──┘
```
- **M2 (taxonomy)** gates M3, M5, M6, M7. Do not start scoring before the taxonomy schema is frozen (v1).
- **Seed data quality** gates M7/M8 acceptance; start curation in S0.
- **LLM layer** (in M3) gates narrative/explanations but not numeric scoring, so M5 can proceed using MockLLM.
- **M6 connectors** are not on the critical path for MVP (seed snapshot suffices); live connectors can slip to v0.5 without blocking the release.

---

## 4. Detailed Task Breakdown

Legend: **ed** = engineer-days · **Dep** = dependency task IDs · **Owner**: BE backend, FE frontend, ML, DATA, QA, OPS, TL.

### M0: Foundations (S1)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T0.1 | Monorepo scaffold, licensing files, CONTRIBUTING, CoC, SECURITY | TL | 1 | | Files present, license headers |
| T0.2 | Docker Compose (api, web, worker, beat, db, redis, mailhog), Makefile | OPS | 2 | T0.1 | `make dev` boots all |
| T0.3 | FastAPI skeleton, config loader (env + YAML), logging, `/healthz` `/readyz` | BE | 2 | T0.1 | Health checks pass |
| T0.4 | Alembic baseline, async SQLAlchemy session, UUIDv7 util | BE | 1.5 | T0.3 | Migration up/down |
| T0.5 | Next.js skeleton, Tailwind, shadcn/ui, layout, theme, i18n scaffold | FE | 2 | T0.1 | Page renders in light/dark |
| T0.6 | OpenAPI → TS type generation pipeline | FE/BE | 1 | T0.3, T0.5 | Types regenerate in CI |
| T0.7 | CI: lint, types, unit, build images, caching | OPS | 2 | T0.2 | Green on main |
| T0.8 | Pre-commit hooks, import-linter, ruff, mypy, ESLint | TL | 1 | T0.1 | Hooks enforced |
| T0.9 | Design system tokens + core components (UX) | FE/UX | 3 | T0.5 | Storybook/preview approved |

### M1: Auth, Profile, Consents (S2)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T1.1 | User model, register/login/refresh/logout, argon2id, JWT rotation + reuse detection | BE | 3 | T0.4 | Auth tests incl. reuse attack |
| T1.2 | GitHub + Google OAuth | BE | 2 | T1.1 | Login via both in dev |
| T1.3 | Consent model + API + UI | BE/FE | 2 | T1.1 | Consents enforced in services |
| T1.4 | Profile tables + CRUD (education, certs, experience, projects, awards) | BE | 3 | T1.1 | Authz matrix tests |
| T1.5 | Completeness calculator + endpoint | BE | 1 | T1.4 | Matches PRD §8.1 weights |
| T1.6 | Onboarding wizard UI (resumable) + profile editors | FE | 6 | T1.4, T0.9 | E2E: signup → complete profile |
| T1.7 | Data export + account deletion (cascade, audit) | BE | 2 | T1.4 | E2E delete leaves zero rows |
| T1.8 | Rate limiting, security headers, CORS | BE | 1 | T1.1 | Tests |

### M2: Taxonomy & Skills (S3)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T2.1 | Taxonomy schema (YAML + JSON Schema), loader, validator, versioning | BE | 2 | T0.4 | CI validates seed |
| T2.2 | Curate ≥ 1,500 skills (aliases, categories), ≥ 60 roles w/ requirements, relations, trait profiles | DATA | 15 | | Passes validator; reviewed |
| T2.3 | Embedding service + pgvector indexes | ML | 2 | T0.4 | Similarity query < 50 ms |
| T2.4 | Normalizer (alias → fuzzy → embedding → queue) + eval set | ML | 3 | T2.1, T2.3 | Precision ≥ 0.9 |
| T2.5 | Admin UI for unmapped skills + merge | FE/BE | 3 | T2.4 | Merge preserves user data |
| T2.6 | Skills explorer UI + self-rating | FE | 4 | T2.1 | Edit self-rating persists |
| T2.7 | Proficiency estimator (pure) + property tests | TL | 3 | T2.1 | Monotonicity tests pass |

### M3: Ingestion & LLM Layer (S4)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T3.1 | `LLMClient` + Ollama/OpenAI-compat/Anthropic adapters + MockLLM + usage logging + cache | ML | 4 | T0.3 | Adapter contract tests |
| T3.2 | Prompt framework (versioned Jinja + schema + retry/fallback) | ML | 2 | T3.1 | Invalid JSON retried ≤ 2× |
| T3.3 | Document upload, validation, storage, signed URLs | BE | 2 | T1.4 | Upload abuse tests pass |
| T3.4 | Resume parser (text extract → sections → LLM extract → normalize) + heuristic fallback | ML | 5 | T3.2, T2.4, T3.3 | Golden F1 targets met |
| T3.5 | Parse review UI (confidence highlights, edit, apply) | FE | 4 | T3.4 | E2E apply flow |
| T3.6 | GitHub analyzer (metrics, manifests → skills, ETag caching, cooldown) | BE | 5 | T2.4 | Evidence rows created |
| T3.7 | Prompt-injection corpus + tests | QA/ML | 2 | T3.4 | No output change |
| T3.8 | Synthetic resume set (≥ 30) + eval harness | DATA/ML | 3 | | In repo with labels |

### M4: Assessments (S5)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T4.1 | Instrument framework (banks, sessions, responses, scoring plug-ins) | BE | 3 | T1.1 | Pluggable scorers |
| T4.2 | Question banks: IPIP Big Five, RIASEC, learning prefs, work style, values (short + full) | DATA | 8 | | Validator passes; licenses recorded |
| T4.3 | Soft-skill SJT bank (10 skills × ≥ 6) + rating items | DATA | 6 | | Reviewed for bias/clarity |
| T4.4 | Scoring + reliability flags + norms file | BE | 3 | T4.1, T4.2 | Unit tests |
| T4.5 | Non-technical evidence tagger (LLM + rules) | ML | 3 | T3.2 | Rationale shown |
| T4.6 | Assessment UI (save/resume, progress, results with disclaimers) | FE | 5 | T4.1 | E2E |

### M5: Scoring Engine (S6)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T5.1 | `config/scoring.yaml` schema + loader + hash | TL | 1 | T0.3 | Invalid config blocks boot |
| T5.2 | TSS, NTSS, PPS, sub-scores (pure) | TL/BE | 6 | T2.7, T4.4 | Golden tests |
| T5.3 | Strengths/weaknesses/hidden strengths | BE | 2 | T5.2 | Evidence linked |
| T5.4 | DNA dimensions + archetype centroids + config | TL | 3 | T5.2 | Deterministic output |
| T5.5 | Explanation objects + confidence model | BE | 2 | T5.2 | Every score has explanation |
| T5.6 | `score_runs` persistence, input hashing, reuse logic | BE | 2 | T5.2 | Idempotent runs |
| T5.7 | `generate_twin` job + progress + SSE | BE | 3 | T5.6 | Job UI works |
| T5.8 | Fairness counterfactual suite | QA | 2 | T5.2 | Zero-tolerance pass |
| T5.9 | Score gauge + explain drawer + DNA radar components | FE | 5 | T5.5, T0.9 | Visuals match spec; a11y ok |

### M6: Market Intelligence (S7)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T6.1 | Market schema, snapshot builder, seed snapshot (sample, labeled) | BE/DATA | 4 | T2.2 | Cold start works |
| T6.2 | Connector interface + runner (rate limits, failure isolation) | BE | 3 | T6.1 | Contract tests |
| T6.3 | Connectors: O*NET/ESCO mapping, one job API, curated trend YAML | BE | 6 | T6.2 | Cassette tests |
| T6.4 | Posting skill extraction (matcher + embedding + optional LLM), dedupe | ML | 4 | T2.4 | Precision/recall report |
| T6.5 | IDS + SkillDemand computation | BE | 3 | T6.1 | Golden tests |
| T6.6 | Emerging role detection + future-skill forecasting (Holt + curated) | ML | 4 | T6.5 | Labeled outputs with uncertainty |
| T6.7 | Salary bands seed (≥ 40 roles, Global/India/US, sample-labeled) | DATA | 4 | T2.2 | Schema valid |
| T6.8 | Market insights UI | FE | 4 | T6.5 | Staleness badges |

### M7: Matching, Gaps, Readiness (S8)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T7.1 | Career match with transfer credit + weight redistribution | TL | 4 | T5.2, T6.5 | Persona hit-rate ≥ 0.8 |
| T7.2 | Recommendation ranker + MMR diversification | BE | 2 | T7.1 | ≤ 4 per family |
| T7.3 | Gap analysis + priority + JRS-impact simulation | BE | 3 | T7.1 | Close gap ⇒ JRS ↑ |
| T7.4 | JRS + time-to-ready | BE | 3 | T7.3 | Bands/labels correct |
| T7.5 | Role question bank (≥ 10 per top role) + quick quiz | DATA/BE | 5 | T2.2 | Quiz feeds InterviewReadiness |
| T7.6 | Persona fixtures (≥ 25) + expert labels + eval | DATA/QA | 4 | | Eval script in CI |
| T7.7 | Careers + gaps UI | FE | 6 | T7.1 | Fit breakdown bars |

### M8: Learning, Projects, Roadmap (S9)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T8.1 | Curate ≥ 300 resources (free-first) with skills coverage | DATA | 10 | T2.2 | Schema valid, links verified |
| T8.2 | Link checker job | BE | 1 | T8.1 | Weekly flag |
| T8.3 | Resource ranker | BE | 3 | T8.1, T7.3 | Mix rules enforced |
| T8.4 | Project templates (≥ 60) + ranker + customizer prompt | DATA/ML | 8 | T3.2 | Rubrics present |
| T8.5 | Roadmap planner + validation schema + replan/diff + lock | TL | 7 | T7.3, T8.3, T8.4 | Prereqs & capacity respected |
| T8.6 | Evidence creation when project/milestone done → re-score trigger | BE | 2 | T8.5 | Δ shown in feed |
| T8.7 | Roadmap, learning, projects UI | FE | 8 | T8.5 | Drag/lock/diff banner |

### M9: Dashboard (S10)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| T9.1 | Aggregated `GET /me/dashboard` with deltas | BE | 3 | T5.7, T7.4, T8.5 | Contract matches PRD §12 |
| T9.2 | Dashboard page (all sections of PRD §13.2) | FE | 8 | T9.1 | All sections render |
| T9.3 | What-changed feed + data-quality panel | BE/FE | 3 | T9.1 | Deltas correct |
| T9.4 | Empty states, loading/progress, error handling | FE | 3 | T9.2 | No blank screens |
| T9.5 | DNA narrative + recommendation explainer tasks + validator | ML | 4 | T5.4, T3.2 | Consistency checks enforced |

### Hardening & Release (S11–S12)
| ID | Task | Owner | ed | Dep | Done when |
|---|---|---|---|---|---|
| TH.1 | Security review (checklist in tech doc §8), pen-test pass, fix findings | TL/QA | 6 | all | No high/critical open |
| TH.2 | Load tests + tuning (indexes, caching) | OPS/BE | 4 | T9.1 | Meets NFRs |
| TH.3 | Accessibility audit and fixes | FE/QA | 4 | T9.2 | Lighthouse ≥ 90, axe clean |
| TH.4 | Docs: README quickstart, architecture, model card, taxonomy/connector guides, ADR index | TL/PO | 5 | | Fresh-clone quickstart ≤ 10 min |
| TH.5 | Privacy review (consents, export/delete, DPDP/GDPR checklist) | PO/TL | 2 | T1.7 | Checklist signed |
| TH.6 | Release engineering: images, SBOM, changelog, tags, demo instance/video | OPS | 3 | TH.1 | v0.1.0 published |
| TH.7 | Community launch: good-first-issues, templates, roadmap board | PO | 2 | TH.4 | ≥ 30 labeled issues |
| TH.8 | Beta test with 20–30 real users; triage feedback | PO/QA | 6 | T9.2 | Findings logged |

### v0.5 (S13–S17)
| ID | Task | Owner | ed | Dep |
|---|---|---|---|---|
| T10.1 | Job/internship cache + matching + UI | BE/FE | 10 | T6.3 |
| T10.2 | Career/salary simulator + UI | TL/FE | 10 | T6.7 |
| T10.3 | Mentor chat: tool registry, SSE, grounding checks, authz tests | ML/BE | 12 | T3.1 |
| T10.4 | Interview practice (question gen + feedback) | ML | 5 | T10.3 |
| T11.1 | Scheduler (beat), incremental recompute, dependency graph | BE | 8 | T5.6 |
| T11.2 | Diff engine + notifications (in-app, email, webhook) + settings | BE/FE | 8 | T11.1 |
| T11.3 | Certification verification for supported issuers | BE | 4 | T1.4 |
| T11.4 | Monitoring dashboards + alerts | OPS | 3 | |

### v1.0 (S18–S23)
| ID | Task | Owner | ed |
|---|---|---|---|
| T12.1 | Plugin system (entry points, manifest, sandboxing guidance) + 2 example plugins | TL/BE | 12 |
| T12.2 | Mentor/educator cohort view with consent + k-anonymity | BE/FE | 10 |
| T12.3 | DNA shareable card (PNG/PDF), revocable links | FE/BE | 5 |
| T12.4 | i18n: 2+ additional languages, localized question banks | FE/DATA | 8 |
| T12.5 | Helm chart + production hardening guide | OPS | 6 |
| T12.6 | Region packs (India, UK, EU) with salary/job sources | DATA/BE | 8 |
| T12.7 | Performance + cost optimizations (LLM caching, batching) | ML/BE | 5 |

### Effort Summary (MVP)
| Milestone | Approx. ed |
|---|---|
| M0 | 13.5 |
| M1 | 20 |
| M2 | 32 |
| M3 | 27 |
| M4 | 28 |
| M5 | 26 |
| M6 | 32 |
| M7 | 27 |
| M8 | 39 |
| M9 | 21 |
| Hardening/Release | 32 |
| **MVP total** | **≈ 298 ed** (≈ 14.5 person-months of work, plus ~20% contingency ≈ 360 ed) |

With the team in §1.1 (about 8 FTE, ~1.2 ed/day-productive each sprint-adjusted), 24 weeks is feasible with contingency. A 3-person core team would need roughly 8–9 months.

---

## 5. Sprint-by-Sprint Plan (MVP)

| Sprint | Goals | Demo at sprint end |
|---|---|---|
| S0 | Repo, CI skeleton, hiring/roles, design kickoff, content owners assigned, license audit of datasets | Plan walkthrough |
| S1 | M0 complete | `make dev`, health, themed empty app |
| S2 | M1 complete | Sign up, fill profile, export/delete |
| S3 | M2 complete (taxonomy v1 frozen) | Search skills, self-rate, evidence view |
| S4 | M3 complete | Upload resume → review → GitHub import |
| S5 | M4 complete | Take assessments, see results |
| S6 | M5 complete | "Generate twin" → scores + DNA with explanations |
| S7 | M6 complete (seed + connectors) | Demand scores, emerging roles |
| S8 | M7 complete | Ranked careers, gaps, readiness |
| S9 | M8 complete | Roadmap + courses + projects |
| S10 | M9 complete | Full dashboard on a persona |
| S11 | Hardening A: security, perf, a11y; beta recruitment | Beta build |
| S12 | Hardening B + release + community launch | v0.1.0 public |

Ceremonies: sprint planning (Mon, 1.5 h), daily 15-min standup, mid-sprint design/arch sync (30 min), review/demo (Fri, 1 h), retro (45 min), weekly risk review (20 min).

---

## 6. Quality Gates (must pass to close a milestone)

1. All tasks' "Done when" criteria met and demoed.
2. CI green: lint, types, unit, integration, e2e for that milestone's flows.
3. Coverage thresholds (tech doc §10) not regressed.
4. Fairness suite and injection corpus pass (from M3/M5 onward).
5. Docs updated (API, config, ADRs, "how calculated" text for any new metric).
6. No open Sev-1/Sev-2 bugs; Sev-3 triaged with owner and date.
7. Migration up/down verified; seed data validated.
8. Product owner sign-off.

Severity: Sev-1 data loss/security/privacy breach; Sev-2 core flow broken; Sev-3 degraded; Sev-4 cosmetic.

---

## 7. Risk Register (with owners and triggers)

| # | Risk | Prob. | Impact | Owner | Early warning | Mitigation / contingency |
|---|---|---|---|---|---|---|
| R1 | Taxonomy/seed curation late | High | High | DATA | M2 slips > 3 days | Start S0; reduce to 1,000 skills and 40 roles for MVP; recruit community curators |
| R2 | LLM extraction quality poor on local models | Med | High | ML | F1 < 0.75 on golden set | Heuristic fallback, constrained decoding, bigger model option, mandatory review UI |
| R3 | Market data licensing/availability | Med | High | PO/BE | Source ToS blocks use | Open datasets + seed snapshot; plugin architecture; drop source |
| R4 | Score credibility challenged by users | Med | High | TL | Low thumbs-up on scores | Explanations, confidence, calibration notes; beta feedback; tune via ADR |
| R5 | Scope creep | High | Med | PO | Backlog growth > 20%/sprint | Phase gates, freeze MVP scope at S2 |
| R6 | Key-person dependency (scoring engine) | Med | High | TL | Single reviewer on core | Pair on core modules; docs and ADRs |
| R7 | Privacy/legal issues with CV data | Low | High | PO | Complaint, audit | Consents, local-LLM option, minimization, deletion tested |
| R8 | Performance of twin generation | Med | Med | BE | p95 > 90 s | Caching, incremental recompute, smaller model, async tuning |
| R9 | Question-bank licensing | Low | Med | DATA | License ambiguity | Use IPIP and project-authored items only; record sources |
| R10 | Low community adoption | Med | Med | PO | < 5 contributors by v0.1 | Good-first-issues, content PR templates, demo instance, outreach to colleges |
| R11 | Dependency vulnerability or breaking update | Med | Med | OPS | CI alerts | Pin versions, Dependabot, weekly update window |

---

## 8. Communication and Governance

- **Decision log:** ADRs in `docs/decisions/`, linked from PRs.
- **Status:** weekly written update (progress vs. plan, risks, blockers, metrics); public roadmap board once the repo is public.
- **Change control:** scope changes after S2 need PO + TL approval and must name what is dropped or delayed.
- **Community:** GitHub Discussions for ideas, issues for bugs, labeled `good first issue`, `content`, `help wanted`; maintainers' response SLA of 3 working days.
- **Release cadence:** v0.1.0 at S12; minor releases every 2–4 weeks after; security patches ASAP.

---

## 9. Metrics Tracked During Delivery

| Area | Metric | Target |
|---|---|---|
| Flow | Sprint goal completion | ≥ 85% |
| Quality | Escaped defects per release | ≤ 5 Sev-3+, 0 Sev-1/2 |
| Quality | Test coverage (core scoring) | ≥ 90% |
| AI quality | Resume extraction F1 (skills / dates) | ≥ 0.85 / ≥ 0.90 |
| AI quality | Persona top-5 hit rate | ≥ 0.80 |
| Performance | Dashboard p95 | ≤ 500 ms |
| Product | Beta users reaching dashboard | ≥ 70% |
| Product | Beta "helpful" rating | ≥ 75% |
| Community | External contributors by v0.1 | ≥ 10 (target ≥ 20 by +6 months) |

---

## 10. Launch Checklist (v0.1.0)

- [ ] All MVP milestones passed gates
- [ ] Security review complete; no open high/critical findings
- [ ] Privacy checklist signed; export/delete verified
- [ ] Seed data licensed and attributed (`THIRD_PARTY_LICENSES.md`)
- [ ] All sample data clearly labeled `sample`
- [ ] README quickstart verified on clean Linux, macOS, and Windows (WSL2)
- [ ] Model card and "how scores are calculated" published
- [ ] Demo instance and walkthrough video
- [ ] Issue templates, good-first-issues, roadmap board live
- [ ] Release artifacts: images (amd64/arm64), SBOM, changelog, tag `v0.1.0`
