-- ============================================================
-- stg_brevo.sql
-- Staging model for Brevo email marketing raw data
-- Reads from: raw.brevo_raw
-- Writes to:  staging.stg_brevo (view)
-- ============================================================

with source as (

    select * from {{ source('raw_sources', 'brevo_raw') }}

),

cleaned as (

    select
        campaign_id,
        campaign_name,

        coalesce(sent, 0)           as emails_sent,
        coalesce(opens, 0)          as emails_opened,
        coalesce(clicks, 0)         as emails_clicked,
        coalesce(unsubscribes, 0)   as unsubscribes,
        coalesce(bounces, 0)        as bounces,

        -- Open Rate = opens / sent
        safe_divide(opens, sent)            as open_rate,

        -- Click Rate = clicks / sent
        safe_divide(clicks, sent)           as click_rate,

        -- Click to Open Rate = clicks / opens
        safe_divide(clicks, opens)          as click_to_open_rate,

        -- Unsubscribe Rate = unsubscribes / sent
        safe_divide(unsubscribes, sent)     as unsubscribe_rate,

        cast(date as date)  as date,
        loaded_at

    from source
    where
        date is not null
        and sent > 0

)

select * from cleaned