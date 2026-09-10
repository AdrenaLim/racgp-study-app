# RACGP Fellowship Study System

**Live:** https://racgp-study.limkangxian99.workers.dev
**Repo:** https://github.com/AdrenaLim/racgp-study-app

A study system for the RACGP Fellowship exams (AKT, KFP, CCE), built as a **Cloudflare Worker + D1** app. All study content (exam map, curriculum, question bank, CCE cases, guidelines, rapid revision sheets, schedule, mistake log, spaced repetition) lives in the database and is served through a single-page dashboard.

**Curriculum v4** follows the official RACGP Curriculum and Syllabus (6th ed) unit structure. Each of the 42 units is presented exactly as the RACGP presents it: 1 · Rationale → 2 · Competencies and learning outcomes (per domain, with core competency outcome codes) → 3 · Words of wisdom → 4 · Case consultation example (with CCE-mapped reflection prompts) → 5 · Learning strategies (own / supervisor / small group / non-medical) → 6 · Guiding topics and content areas → 7 · Learning resources. A personal **study tracker** (topic status, notes) sits at the bottom of each unit, separate from the official content. The **Today** tab plans each day from the 18-week schedule (weeks map to focus units; week 18 lands on exam week).

> **Free-tier note:** D1 free plan allows 100,000 row writes/day (reads are unlimited and much higher). Normal study use (attempts, mistakes, review updates) is a few hundred writes a day at most — the limit only matters when bulk re-seeding. If a write returns `error 1101` with a D1 limit message, it resets at midnight UTC.

## Exam targets
- **AKT + KFP 2027.1**: 15/16 January 2027 (enrol 3 Sep - 1 Oct 2026)
- **CCE 2027.1**: expected June 2027

## Local development

```bash
npm install
npm run db:local     # create local D1, apply schema + seed
npm run dev          # http://localhost:8787
```

## Content editing (the GitHub workflow)

All seed content is in human-editable JSON files:

```
seed/data/
  presentations.json   # presentation-based topics (chest pain, fatigue, ...)
  systems.json         # systems/population topics (asthma, CKD, ATSI health, ...)
  questions_akt.json   # AKT single-best-answer questions
  questions_kfp.json   # KFP multi-select clinical cases
  cce_cases.json       # CCE scenario bank
  guidelines.json      # tiered guideline list with thresholds
  resources.json       # primary/secondary/rapid resource per domain
  rapid_sheets.json    # rapid revision sheets
  schedule.json        # 18-week study schedule
```

Edit any JSON, then regenerate + re-seed:

```bash
python seed/build_seed_sql.py     # or edit build_content.py for new records
npx wrangler d1 execute racgp-study-db --local --file=seed/content.sql
```

On GitHub, every push to `main` runs CI (seed a fresh local D1, boot the worker, smoke-test the API) and, once Cloudflare secrets are configured, deploys to production with the updated schema + seed.

## Deploy to Cloudflare (first time)

1. `npx wrangler login` (or create an API token with Workers Scripts:Edit + D1:Edit)
2. `npx wrangler d1 create racgp-study-db` and paste the printed `database_id` into `wrangler.jsonc`
3. `npx wrangler d1 execute racgp-study-db --remote --file=schema.sql`
4. `npx wrangler d1 execute racgp-study-db --remote --file=seed/seed.sql`
5. `npx wrangler d1 execute racgp-study-db --remote --file=seed/content.sql`
6. `npx wrangler deploy`

For GitHub Actions deploys, add repo secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. The workflow also auto-injects the database id on first deploy.

## App structure

- `src/index.js` - Worker API (all `/api/*` routes)
- `public/index.html` - single-page dashboard (10 tabs)
- `schema.sql` - D1 schema (idempotent)
- `seed/` - seed data + generators

## API

| Route | What |
|---|---|
| `/api/dashboard` | progress stats, weakest/strongest topics, due reviews |
| `/api/topics` | curriculum CRUD + status cycling |
| `/api/questions?type=AKT\|KFP` | question bank |
| `/api/attempts` | record an answer (POST) |
| `/api/cce` | CCE scenario bank |
| `/api/guidelines` | tiered guidelines |
| `/api/resources` | resource library |
| `/api/rapid` | rapid revision sheets |
| `/api/schedule` | 18-week plan |
| `/api/mistakes` | mistake log CRUD |
| `/api/reviews` | spaced repetition (POST `{topic, quality}`) |
| `/api/meta` | verified exam structure map with sources |

## Data provenance

Exam structure facts in `/api/meta` were verified from racgp.org.au (AKT/KFP/CCE pages, exam dates page, candidate handbook) on **2026-09-08**, each with source URL and checked date. Guideline seeds carry publisher and year; the 2026 HTN guideline (Q4 2026 release) and 2027.1 CCE dates are flagged as pending/announced.

[![CI + Deploy](https://github.com/AdrenaLim/racgp-study-app/actions/workflows/deploy.yml/badge.svg)](https://github.com/AdrenaLim/racgp-study-app/actions/workflows/deploy.yml)
