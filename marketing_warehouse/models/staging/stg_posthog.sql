-- ============================================================
-- stg_posthog.sql
-- Staging model for PostHog product analytics raw data
-- Reads from: raw.posthog_raw
-- Writes to:  staging.stg_posthog (view)
-- ============================================================

with source as (

    select * from {{ source('raw_sources', 'posthog_raw') }}

),

cleaned as (

    select
        event_id,
        user_id,
        event,
        channel,
        country,

        -- Flag key events as booleans (true/false)
        -- This makes mart calculations much simpler
        case when event = 'signup'      then true else false end as is_signup,
        case when event = 'activation'  then true else false end as is_activation,
        case when event = 'purchase'    then true else false end as is_purchase,
        case when event = 'churned'     then true else false end as is_churn,

        cast(timestamp as date) as event_date,
        loaded_at

    from source
    where
        timestamp is not null
        and user_id is not null

)

select * from cleaned