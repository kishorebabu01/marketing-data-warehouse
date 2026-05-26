-- ============================================================
-- stg_meta_ads.sql
-- Staging model for Meta Ads raw data
-- Reads from: raw.meta_ads_raw
-- Writes to:  staging.stg_meta_ads (view)
-- What it does: cleans column names, removes nulls,
--               calculates click-through rate
-- ============================================================

with source as (

    -- Step 1: Read directly from the raw table in BigQuery
    -- It tells dbt "this table was NOT created by dbt"
    select * from {{ source('raw_sources', 'meta_ads_raw') }}

),

cleaned as (

    -- Step 2: Clean and standardise every column
    select
        -- IDs and dimensions
        campaign_id,
        campaign_name,

        -- Metrics — cast to correct types and handle nulls
        coalesce(spend, 0)          as spend_eur,
        coalesce(impressions, 0)    as impressions,
        coalesce(clicks, 0)         as clicks,
        coalesce(conversions, 0)    as conversions,

        -- Calculated metric: Click-Through Rate
        -- CTR = clicks / impressions (how many people who saw the ad clicked it)
        -- We use safe_divide to avoid dividing by zero
        safe_divide(clicks, impressions) as ctr,

        -- Calculated metric: Conversion Rate
        -- CVR = conversions / clicks
        safe_divide(conversions, clicks) as conversion_rate,

        -- Date
        cast(date as date)          as date,

        -- Audit column — when was this data loaded
        loaded_at

    from source
    where
        -- Remove any rows with no date (data quality filter)
        date is not null
        -- Remove rows with zero spend AND zero impressions (empty rows)
        and not (spend = 0 and impressions = 0)

)

-- Step 3: Return the cleaned data
select * from cleaned