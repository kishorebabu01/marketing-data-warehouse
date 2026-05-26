# ============================================================
# load_demo_data.py
# Phase 1 — Load realistic demo data into BigQuery raw dataset
# This script generates 90 days of realistic marketing data
# for all 6 sources and loads them into BigQuery
# ============================================================

import pandas as pd
import random
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# ── CONFIG ──────────────────────────────────────────────────
PROJECT_ID = "marketing-warehouse-497216"
DATASET    = "raw"
# ────────────────────────────────────────────────────────────

# Authenticate using the gcloud credentials file on Desktop
CREDENTIALS_PATH = r"C:\Users\Lenovo\OneDrive\Desktop\gcloud_credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

client = bigquery.Client(project=PROJECT_ID)

# Helper — generate list of dates for last 90 days
def date_range(days=90):
    today = datetime.today()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

DATES = date_range(90)
CHANNELS = ["facebook", "instagram", "google_search", "google_display", "email", "organic"]
CAMPAIGNS = ["brand_awareness_q1", "retargeting_q1", "lead_gen_q2", "summer_sale", "product_launch"]

print("Starting demo data load into BigQuery...")

# ── TABLE 1: meta_ads_raw ────────────────────────────────────
print("Loading meta_ads_raw...")
meta_rows = []
for date in DATES:
    for campaign in CAMPAIGNS[:3]:
        meta_rows.append({
            "campaign_id":   f"meta_{campaign}_{date}",
            "campaign_name": campaign,
            "spend":         round(random.uniform(50, 500), 2),
            "impressions":   random.randint(1000, 50000),
            "clicks":        random.randint(50, 2000),
            "conversions":   random.randint(1, 100),
            "date":          date,
            "loaded_at":     datetime.utcnow().isoformat()
        })

df_meta = pd.DataFrame(meta_rows)
table_id = f"{PROJECT_ID}.{DATASET}.meta_ads_raw"
job = client.load_table_from_dataframe(df_meta, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))
job.result()
print(f"  meta_ads_raw loaded: {len(df_meta)} rows")

# ── TABLE 2: google_ads_raw ──────────────────────────────────
print("Loading google_ads_raw...")
keywords = ["growth marketing tool", "marketing dashboard", "seo analytics",
            "facebook ads manager", "email marketing software"]
google_rows = []
for date in DATES:
    for kw in keywords:
        google_rows.append({
            "keyword_id":      f"gads_{kw[:10].replace(' ','_')}_{date}",
            "keyword":         kw,
            "clicks":          random.randint(10, 500),
            "impressions":     random.randint(500, 20000),
            "cost":            round(random.uniform(10, 300), 2),
            "conversions":     random.randint(0, 50),
            "quality_score":   random.randint(4, 10),
            "date":            date,
            "loaded_at":       datetime.utcnow().isoformat()
        })

df_google = pd.DataFrame(google_rows)
table_id = f"{PROJECT_ID}.{DATASET}.google_ads_raw"
job = client.load_table_from_dataframe(df_google, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))
job.result()
print(f"  google_ads_raw loaded: {len(df_google)} rows")

# ── TABLE 3: ga4_raw ─────────────────────────────────────────
print("Loading ga4_raw...")
ga4_rows = []
for date in DATES:
    for channel in CHANNELS:
        ga4_rows.append({
            "session_id":       f"ga4_{channel}_{date}",
            "channel":          channel,
            "sessions":         random.randint(100, 5000),
            "users":            random.randint(80, 4000),
            "new_users":        random.randint(50, 2000),
            "bounce_rate":      round(random.uniform(0.2, 0.8), 2),
            "pages_per_session":round(random.uniform(1.5, 6.0), 2),
            "avg_session_duration": random.randint(30, 300),
            "date":             date,
            "loaded_at":        datetime.utcnow().isoformat()
        })

df_ga4 = pd.DataFrame(ga4_rows)
table_id = f"{PROJECT_ID}.{DATASET}.ga4_raw"
job = client.load_table_from_dataframe(df_ga4, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))
job.result()
print(f"  ga4_raw loaded: {len(df_ga4)} rows")

# ── TABLE 4: gsc_raw ─────────────────────────────────────────
print("Loading gsc_raw...")
queries = ["growth marketing", "marketing dashboard tool", "dbt bigquery tutorial",
           "looker studio dashboard", "marketing data warehouse", "cac ltv ratio"]
gsc_rows = []
for date in DATES:
    for query in queries:
        gsc_rows.append({
            "query":       query,
            "impressions": random.randint(100, 10000),
            "clicks":      random.randint(5, 500),
            "ctr":         round(random.uniform(0.01, 0.15), 4),
            "position":    round(random.uniform(1.0, 50.0), 1),
            "date":        date,
            "loaded_at":   datetime.utcnow().isoformat()
        })

df_gsc = pd.DataFrame(gsc_rows)
table_id = f"{PROJECT_ID}.{DATASET}.gsc_raw"
job = client.load_table_from_dataframe(df_gsc, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))
job.result()
print(f"  gsc_raw loaded: {len(df_gsc)} rows")

# ── TABLE 5: brevo_raw ───────────────────────────────────────
print("Loading brevo_raw...")
email_campaigns = ["welcome_sequence", "weekly_newsletter", "product_update", "re_engagement"]
brevo_rows = []
for date in DATES[::7]:  # weekly emails
    for camp in email_campaigns:
        sent = random.randint(500, 5000)
        brevo_rows.append({
            "campaign_id":    f"brevo_{camp}_{date}",
            "campaign_name":  camp,
            "sent":           sent,
            "opens":          random.randint(int(sent*0.1), int(sent*0.4)),
            "clicks":         random.randint(int(sent*0.01), int(sent*0.1)),
            "unsubscribes":   random.randint(0, 20),
            "bounces":        random.randint(0, 50),
            "date":           date,
            "loaded_at":      datetime.utcnow().isoformat()
        })

df_brevo = pd.DataFrame(brevo_rows)
table_id = f"{PROJECT_ID}.{DATASET}.brevo_raw"
job = client.load_table_from_dataframe(df_brevo, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))
job.result()
print(f"  brevo_raw loaded: {len(df_brevo)} rows")

# ── TABLE 6: posthog_raw ─────────────────────────────────────
print("Loading posthog_raw...")
events = ["page_view", "signup", "activation", "feature_used", "purchase", "churned"]
posthog_rows = []
for date in DATES:
    for _ in range(random.randint(50, 200)):
        posthog_rows.append({
            "event_id":   f"ph_{date}_{random.randint(10000,99999)}",
            "user_id":    f"user_{random.randint(1000, 9999)}",
            "event":      random.choice(events),
            "channel":    random.choice(CHANNELS),
            "country":    random.choice(["IE", "GB", "US", "IN", "DE"]),
            "timestamp":  date,
            "loaded_at":  datetime.utcnow().isoformat()
        })

df_posthog = pd.DataFrame(posthog_rows)
table_id = f"{PROJECT_ID}.{DATASET}.posthog_raw"
job = client.load_table_from_dataframe(df_posthog, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))
job.result()
print(f"  posthog_raw loaded: {len(df_posthog)} rows")

print("\n✅ ALL DONE! 6 tables loaded into BigQuery raw dataset.")
print(f"   Go to BigQuery and check: {PROJECT_ID}.raw")