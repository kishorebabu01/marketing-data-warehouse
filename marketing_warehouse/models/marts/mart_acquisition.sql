-- ============================================================
-- mart_acquisition.sql
-- Mart model — Acquisition metrics
-- Answers: How much does it cost to acquire a customer?
--          Which channel gives best return on ad spend?
-- Reads from: staging views
-- Writes to:  marts.mart_acquisition (table)
-- ============================================================

with meta_spend as (

    -- Total Meta Ads spend and conversions by date
    select
        date,
        'meta'                      as channel,
        sum(spend_eur)              as total_spend,
        sum(clicks)                 as total_clicks,
        sum(impressions)            as total_impressions,
        sum(conversions)            as total_conversions
    from {{ ref('stg_meta_ads') }}
    group by date

),

google_spend as (

    -- Total Google Ads spend and conversions by date
    select
        date,
        'google'                    as channel,
        sum(cost_eur)               as total_spend,
        sum(clicks)                 as total_clicks,
        sum(impressions)            as total_impressions,
        sum(conversions)            as total_conversions
    from {{ ref('stg_google_ads') }}
    group by date

),

all_channels as (

    -- Combine Meta and Google into one table
    select * from meta_spend
    union all
    select * from google_spend

),

final as (

    select
        date,
        channel,
        total_spend,
        total_clicks,
        total_impressions,
        total_conversions,

        -- CAC = total spend / total conversions
        -- How much did we spend to get one conversion?
        safe_divide(total_spend, total_conversions)     as cac,

        -- CPL = total spend / total clicks
        -- How much did we spend to get one click?
        safe_divide(total_spend, total_clicks)          as cost_per_click,

        -- CTR = clicks / impressions
        -- What % of people who saw the ad clicked it?
        safe_divide(total_clicks, total_impressions)    as ctr,

        -- Conversion Rate = conversions / clicks
        safe_divide(total_conversions, total_clicks)    as conversion_rate,

        -- ROAS placeholder — revenue data would come from
        -- a revenue source; we use conversions * avg order value
        -- Assuming avg order value = €50 for demo purposes
        safe_divide(total_conversions * 50, total_spend) as roas

    from all_channels

)

select * from final
order by date desc, channel