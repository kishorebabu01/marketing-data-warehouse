-- ============================================================
-- stg_gsc.sql
-- Staging model for Google Search Console raw data
-- Reads from: raw.gsc_raw
-- Writes to:  staging.stg_gsc (view)
-- ============================================================

with source as (

    select * from {{ source('raw_sources', 'gsc_raw') }}

),

cleaned as (

    select
        query,

        coalesce(impressions, 0)    as impressions,
        coalesce(clicks, 0)         as clicks,
        coalesce(ctr, 0)            as ctr,
        coalesce(position, 0)       as avg_position,

        -- Categorise ranking position
        case
            when position <= 3  then 'top_3'
            when position <= 10 then 'page_1'
            when position <= 20 then 'page_2'
            else 'page_3_plus'
        end as position_bucket,

        cast(date as date)  as date,
        loaded_at

    from source
    where
        date is not null
        and impressions > 0

)

select * from cleaned