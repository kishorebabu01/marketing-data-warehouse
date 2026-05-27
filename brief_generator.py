# ============================================================
# brief_generator.py
# Phase 5 — Weekly AI CMO Brief Generator
# 
# What this script does:
# 1. Connects to BigQuery and reads this week's metrics
# 2. Compares them to last week's metrics
# 3. Sends the comparison to Groq's LLaMA 3.3 70B
# 4. Gets back a 3-bullet CMO insight brief
# 5. Posts the brief to Slack
# 6. Saves the brief to Supabase for history
# ============================================================

from dotenv import load_dotenv
load_dotenv()
import os
import json
import requests
from datetime import datetime, timedelta
from google.cloud import bigquery
from groq import Groq

# ── CONFIG ──────────────────────────────────────────────────
PROJECT_ID      = "marketing-warehouse-497216"
GROQ_API_KEY    = os.environ.get("GROQ_API_KEY")
SLACK_WEBHOOK   = os.environ.get("SLACK_WEBHOOK_URL")
SUPABASE_URL    = os.environ.get("SUPABASE_URL")
SUPABASE_KEY    = os.environ.get("SUPABASE_KEY")
CREDENTIALS     = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
# ────────────────────────────────────────────────────────────

# Set up BigQuery client
if CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS

client = bigquery.Client(project=PROJECT_ID)

def get_weekly_metrics(week_offset=0):
    """
    Reads metrics from BigQuery for a specific week.
    week_offset=0 means this week
    week_offset=1 means last week
    """
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday() + (7 * week_offset))
    week_end   = week_start + timedelta(days=6)

    start_str = week_start.strftime("%Y-%m-%d")
    end_str   = week_end.strftime("%Y-%m-%d")

    query = f"""
    -- Pull acquisition metrics for the week
    SELECT
        'acquisition' as metric_type,
        ROUND(AVG(cac), 2)              as avg_cac,
        ROUND(AVG(roas), 2)             as avg_roas,
        ROUND(SUM(total_spend), 2)      as total_spend,
        ROUND(SUM(total_conversions), 0) as total_conversions,
        ROUND(AVG(ctr) * 100, 2)        as avg_ctr_pct
    FROM `{PROJECT_ID}.marketing_warehouse_marts.mart_acquisition`
    WHERE date BETWEEN '{start_str}' AND '{end_str}'
    """

    query2 = f"""
    SELECT
        ROUND(AVG(activation_rate) * 100, 2)  as avg_activation_rate_pct,
        ROUND(AVG(churn_rate) * 100, 2)        as avg_churn_rate_pct,
        SUM(total_signups)                     as total_signups
    FROM `{PROJECT_ID}.marketing_warehouse_marts.mart_activation`
    WHERE date BETWEEN '{start_str}' AND '{end_str}'
    """

    query3 = f"""
    SELECT
        ROUND(AVG(organic_traffic_share) * 100, 2) as organic_share_pct,
        ROUND(AVG(k_factor_estimate), 4)            as avg_k_factor,
        SUM(organic_sessions)                       as total_organic_sessions
    FROM `{PROJECT_ID}.marketing_warehouse_marts.mart_referral`
    WHERE date BETWEEN '{start_str}' AND '{end_str}'
    """

    # Run all 3 queries
    acq   = list(client.query(query).result())[0]
    act   = list(client.query(query2).result())[0]
    ref   = list(client.query(query3).result())[0]

    return {
        "week_start":           start_str,
        "week_end":             end_str,
        "avg_cac":              float(acq.avg_cac or 0),
        "avg_roas":             float(acq.avg_roas or 0),
        "total_spend":          float(acq.total_spend or 0),
        "total_conversions":    int(acq.total_conversions or 0),
        "avg_ctr_pct":          float(acq.avg_ctr_pct or 0),
        "activation_rate_pct":  float(act.avg_activation_rate_pct or 0),
        "churn_rate_pct":       float(act.avg_churn_rate_pct or 0),
        "total_signups":        int(act.total_signups or 0),
        "organic_share_pct":    float(ref.organic_share_pct or 0),
        "k_factor":             float(ref.avg_k_factor or 0),
        "organic_sessions":     int(ref.total_organic_sessions or 0),
    }


def calculate_delta(this_week, last_week):
    """
    Calculates % change between this week and last week
    for each metric. Positive = improvement, negative = decline.
    """
    def pct_change(new, old):
        if old == 0:
            return 0
        return round(((new - old) / old) * 100, 1)

    return {
        "cac_change":           pct_change(this_week["avg_cac"], last_week["avg_cac"]),
        "roas_change":          pct_change(this_week["avg_roas"], last_week["avg_roas"]),
        "spend_change":         pct_change(this_week["total_spend"], last_week["total_spend"]),
        "conversions_change":   pct_change(this_week["total_conversions"], last_week["total_conversions"]),
        "activation_change":    pct_change(this_week["activation_rate_pct"], last_week["activation_rate_pct"]),
        "churn_change":         pct_change(this_week["churn_rate_pct"], last_week["churn_rate_pct"]),
        "organic_change":       pct_change(this_week["organic_sessions"], last_week["organic_sessions"]),
    }


def generate_brief(this_week, last_week, deltas):
    """
    Sends metrics to Groq LLaMA 3.3 70B and gets back
    a 3-bullet CMO-ready insight brief.
    """
    groq_client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a senior growth marketing analyst writing a weekly brief for the CMO.
You have this week's marketing metrics and the week-over-week changes.

THIS WEEK'S METRICS:
- CAC (Customer Acquisition Cost): €{this_week['avg_cac']}
- ROAS (Return on Ad Spend): {this_week['avg_roas']}x
- Total Ad Spend: €{this_week['total_spend']}
- Total Conversions: {this_week['total_conversions']}
- Click-Through Rate: {this_week['avg_ctr_pct']}%
- Activation Rate: {this_week['activation_rate_pct']}%
- Churn Rate: {this_week['churn_rate_pct']}%
- Total New Signups: {this_week['total_signups']}
- Organic Traffic Share: {this_week['organic_share_pct']}%
- Organic Sessions: {this_week['organic_sessions']}
- K-Factor (viral coefficient): {this_week['k_factor']}

WEEK-OVER-WEEK CHANGES:
- CAC: {deltas['cac_change']}% (negative = cheaper acquisition = GOOD)
- ROAS: {deltas['roas_change']}% (positive = better return = GOOD)
- Ad Spend: {deltas['spend_change']}%
- Conversions: {deltas['conversions_change']}%
- Activation Rate: {deltas['activation_change']}% (positive = more users activating = GOOD)
- Churn Rate: {deltas['churn_change']}% (negative = less churn = GOOD)
- Organic Sessions: {deltas['organic_change']}% (positive = growing organic = GOOD)

Write exactly 3 bullet points. Each bullet must:
1. State what changed (the number)
2. Explain why it matters to the business
3. Recommend one specific action

Format each bullet starting with an emoji:
📊 for acquisition/paid metrics
🔄 for retention/activation metrics  
🌱 for organic/referral metrics

Keep each bullet under 40 words. Be direct and specific. No fluff.
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.3
    )

    return response.choices[0].message.content


def post_to_slack(brief, this_week):
    """
    Posts the AI brief to Slack via webhook.
    """
    if not SLACK_WEBHOOK:
        print("No Slack webhook configured — skipping Slack post")
        return

    week_str = this_week["week_start"]

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📈 Weekly Growth Brief — {week_str}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": brief
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Generated by LLaMA 3.3 70B · Data from BigQuery · Week of {week_str}_"
                }
            }
        ]
    }

    response = requests.post(SLACK_WEBHOOK, json=message)
    if response.status_code == 200:
        print("✅ Brief posted to Slack successfully")
    else:
        print(f"❌ Slack post failed: {response.status_code}")



if __name__ == "__main__":
    print("🚀 Starting weekly brief generation...")
    print()

    # Step 1: Get this week's and last week's metrics
    print("📊 Fetching this week's metrics from BigQuery...")
    this_week = get_weekly_metrics(week_offset=0)
    print(f"   Week: {this_week['week_start']} to {this_week['week_end']}")
    print(f"   CAC: €{this_week['avg_cac']} | ROAS: {this_week['avg_roas']}x")

    print("📊 Fetching last week's metrics from BigQuery...")
    last_week = get_weekly_metrics(week_offset=1)
    print(f"   Week: {last_week['week_start']} to {last_week['week_end']}")

    # Step 2: Calculate deltas
    print()
    print("🔢 Calculating week-over-week changes...")
    deltas = calculate_delta(this_week, last_week)
    print(f"   CAC change: {deltas['cac_change']}%")
    print(f"   ROAS change: {deltas['roas_change']}%")
    print(f"   Organic change: {deltas['organic_change']}%")

    # Step 3: Generate brief with Groq
    print()
    print("🤖 Generating CMO brief with LLaMA 3.3 70B...")
    brief = generate_brief(this_week, last_week, deltas)
    print()
    print("=" * 60)
    print("GENERATED BRIEF:")
    print("=" * 60)
    print(brief)
    print("=" * 60)

    # Step 4: Post to Slack
    print()
    post_to_slack(brief, this_week)

    # Step 5: Save to Supabase (disabled in CI — runs locally only)
    # save_to_supabase(brief, this_week , deltas)
    print("⚠️  Supabase save skipped in CI environment")

    print()
    print("✅ Weekly brief complete!")