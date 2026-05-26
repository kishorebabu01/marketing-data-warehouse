-- ============================================================
-- mart_retention.sql
-- Answers: Are users coming back after they first visited?
-- Retention = % of users who return after N days
-- This is the most important metric for product health
-- ============================================================

with daily_users as (

    -- Get all unique users per day
    select
        event_date  as date,
        user_id,
        channel,
        is_signup,
        is_churn

    from {{ ref('stg_posthog') }}

),

cohort_base as (

    -- Find the first date each user was seen (their signup date)
    select
        user_id,
        min(date)   as cohort_date

    from daily_users
    group by user_id

),

user_activity as (

    -- Join each user's activity back to their cohort date
    -- Calculate how many days after signup they were active
    select
        c.cohort_date,
        d.user_id,
        d.date,
        date_diff(d.date, c.cohort_date, day) as days_since_signup

    from daily_users d
    join cohort_base c on d.user_id = c.user_id

),

retention_summary as (

    -- Count unique users per cohort date and days_since_signup
    select
        cohort_date,
        days_since_signup,
        count(distinct user_id) as active_users

    from user_activity
    group by cohort_date, days_since_signup

),

cohort_sizes as (

    -- Get size of each cohort (users who joined on each day)
    select
        cohort_date,
        count(distinct user_id) as cohort_size

    from cohort_base
    group by cohort_date

),

final as (

    select
        r.cohort_date,
        c.cohort_size,
        r.days_since_signup,
        r.active_users,

        -- Retention Rate = active users on day N / cohort size
        -- Day 0 = 100% (everyone is active on signup day)
        -- Day 7 = what % came back after 1 week?
        -- Day 30 = what % came back after 1 month?
        safe_divide(r.active_users, c.cohort_size) as retention_rate

    from retention_summary r
    join cohort_sizes c on r.cohort_date = c.cohort_date

)

select * from final
order by cohort_date desc, days_since_signup