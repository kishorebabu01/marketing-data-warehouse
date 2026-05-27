# Marketing Data Warehouse + Growth Intelligence Dashboard

> Production-grade marketing data warehouse built with BigQuery, dbt Core, 
> Looker Studio, and Groq AI. Ingests data from 6 marketing sources, 
> transforms 40+ metrics, and delivers weekly AI-generated CMO briefs to Slack.

## Live Dashboard
[View Live Looker Studio Dashboard]:
https://datastudio.google.com/reporting/2f207167-e16f-46a6-9da4-d277b3e5ebee

## Architecture

6 Marketing Sources (demo data)
↓
BigQuery raw dataset (6 tables, 13,000+ rows)
↓
dbt Staging Layer (6 SQL models — clean & standardise)
↓
dbt Marts Layer (5 SQL models — CAC, ROAS, LTV, Retention, K-factor)
↓
Looker Studio Dashboard (6 tabs — live BigQuery connection)
↓
GitHub Actions (daily dbt run + weekly AI brief)
↓
Groq LLaMA 3.3 70B → CMO brief → Slack #growth-briefs

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Warehouse | BigQuery (GCP free tier) | Store all marketing data |
| Ingestion | Python + pandas | Load demo data into raw dataset |
| Transformation | dbt Core | Clean and calculate metrics |
| Testing | dbt tests (20 tests) | Data quality validation |
| Dashboard | Looker Studio | Live 6-tab executive dashboard |
| AI Brief | Groq API — LLaMA 3.3 70B | Weekly CMO insight generation |
| Orchestration | GitHub Actions | Daily dbt runs + weekly brief |
| Notifications | Slack Webhooks | AI brief delivery |

## dbt Models

### Staging Layer
- `stg_meta_ads` — Meta Ads spend, clicks, CTR, conversion rate
- `stg_google_ads` — Google Ads keywords, CPC, quality score
- `stg_ga4` — GA4 sessions, bounce rate, channel attribution
- `stg_gsc` — Search Console queries, CTR, position
- `stg_brevo` — Email open rate, click rate, unsubscribe rate
- `stg_posthog` — Product events, signups, activation, churn

### Marts Layer
- `mart_acquisition` — CAC, ROAS, CPL by channel
- `mart_activation` — Activation rate, purchase rate, churn rate
- `mart_retention` — Cohort retention matrix (D1, D7, D30)
- `mart_revenue` — MRR, LTV, LTV:CAC ratio, payback period
- `mart_referral` — K-factor, organic traffic share, search CTR

## Data Quality
- 20/20 dbt tests passing
- Custom tests: assert_cac_positive, assert_roas_positive, assert_retention_rate_valid
- Schema tests: not_null, accepted_values on all key columns

## Dashboard Tabs
1. Executive Overview — All KPIs, spend trend, CAC by channel
2. Acquisition — ROAS trend, spend by channel
3. Retention — Cohort retention rates, cohort sizes
4. Revenue — MRR, LTV:CAC ratio, CAC payback months
5. Referral & Organic — K-factor, organic sessions trend
6. Full Funnel AARRR — Signups, activation rate, churn rate

## Weekly AI Brief
Every Monday at 9am UTC, GitHub Actions:
1. Queries BigQuery for this week vs last week metrics
2. Calculates week-over-week deltas
3. Sends structured metrics to Groq LLaMA 3.3 70B
4. AI writes 3-bullet CMO insight brief
5. Posts to Slack #growth-briefs automatically

## Setup
bash
# Install dependencies
pip install dbt-bigquery google-cloud-bigquery groq python-dotenv

# Run dbt models
cd marketing_warehouse
dbt run

# Run tests
dbt test

# Generate AI brief manually
python brief_generator.py


## Portfolio Context
Built as Project 4 of 10 in a growth marketing portfolio.

