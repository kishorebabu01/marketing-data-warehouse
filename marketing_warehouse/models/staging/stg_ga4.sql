-- ============================================================
-- stg_ga4.sql
-- Staging model for Google Analytics 4 raw data
-- Reads from: raw.ga4_raw
-- Writes to:  staging.stg_ga4 (view)
-- ============================================================

with source as (

    select * from {{ source('raw_sources', 'ga4_raw') }}

),

cleaned as (

    select
        session_id,
        channel,

        coalesce(sessions, 0)               as sessions,
        coalesce(users, 0)                  as users,
        coalesce(new_users, 0)              as new_users,
        coalesce(bounce_rate, 0)            as bounce_rate,
        coalesce(pages_per_session, 0)      as pages_per_session,
        coalesce(avg_session_duration, 0)   as avg_session_duration_seconds,

        -- Returning users = total users minus new users
        coalesce(users, 0) - coalesce(new_users, 0) as returning_users,

        -- New user rate = new users / total users
        safe_divide(new_users, users)       as new_user_rate,

        cast(date as date)  as date,
        loaded_at

    from source
    where
        date is not null
        and sessions > 0

)

select * from cleaned