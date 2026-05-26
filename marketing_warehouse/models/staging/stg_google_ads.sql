-- ============================================================
-- stg_google_ads.sql
-- Staging model for Google Ads raw data
-- Reads from: raw.google_ads_raw
-- Writes to:  staging.stg_google_ads (view)
-- ============================================================

with source as (

    select * from {{ source('raw_sources', 'google_ads_raw') }}

),

cleaned as (

    select
        keyword_id,
        keyword,

        coalesce(clicks, 0)         as clicks,
        coalesce(impressions, 0)    as impressions,
        coalesce(cost, 0)           as cost_eur,
        coalesce(conversions, 0)    as conversions,
        coalesce(quality_score, 0)  as quality_score,

        -- CTR = clicks / impressions
        safe_divide(clicks, impressions)    as ctr,

        -- CPC = cost / clicks (Cost Per Click)
        safe_divide(cost, clicks)           as cost_per_click,

        -- Conversion Rate = conversions / clicks
        safe_divide(conversions, clicks)    as conversion_rate,

        cast(date as date)  as date,
        loaded_at

    from source
    where date is not null

)

select * from cleaned