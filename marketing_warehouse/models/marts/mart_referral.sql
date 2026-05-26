-- ============================================================
-- mart_referral.sql
-- Answers: Are our existing users bringing new users?
-- K-factor = viral coefficient
-- K-factor > 1 means the product grows by itself (viral)
-- K-factor < 1 means you need paid ads to grow
-- ============================================================

with organic_traffic as (

    -- Get organic search traffic from GA4
    select
        date,
        sum(sessions)   as organic_sessions,
        sum(users)      as organic_users,
        sum(new_users)  as new_organic_users

    from {{ ref('stg_ga4') }}
    where channel = 'organic'
    group by date

),

paid_traffic as (

    -- Get total paid traffic from GA4
    select
        date,
        sum(sessions)   as paid_sessions,
        sum(users)      as paid_users

    from {{ ref('stg_ga4') }}
    where channel != 'organic'
    group by date

),

search_visibility as (

    -- Get search impressions and clicks from GSC
    select
        date,
        sum(impressions)    as total_impressions,
        sum(clicks)         as total_organic_clicks,
        avg(avg_position)   as avg_search_position

    from {{ ref('stg_gsc') }}
    group by date

),

new_users as (

    -- Count new signups from PostHog
    select
        event_date          as date,
        count(distinct user_id) as total_new_signups

    from {{ ref('stg_posthog') }}
    where is_signup = true
    group by event_date

),

final as (

    select
        o.date,
        o.organic_sessions,
        o.organic_users,
        o.new_organic_users,
        coalesce(p.paid_sessions, 0)        as paid_sessions,
        coalesce(s.total_impressions, 0)    as search_impressions,
        coalesce(s.total_organic_clicks, 0) as search_clicks,
        coalesce(s.avg_search_position, 0)  as avg_search_position,
        coalesce(n.total_new_signups, 0)    as total_new_signups,

        -- Organic share = organic sessions / total sessions
        -- What % of traffic came without paid ads?
        safe_divide(
            o.organic_sessions,
            o.organic_sessions + coalesce(p.paid_sessions, 0)
        ) as organic_traffic_share,

        -- K-factor estimate
        -- New organic users / total users (rough viral coefficient)
        safe_divide(o.new_organic_users, o.organic_users) as k_factor_estimate,

        -- Search CTR = clicks / impressions
        safe_divide(
            coalesce(s.total_organic_clicks, 0),
            coalesce(s.total_impressions, 0)
        ) as search_ctr

    from organic_traffic o
    left join paid_traffic p on o.date = p.date
    left join search_visibility s on o.date = s.date
    left join new_users n on o.date = n.date

)

select * from final
order by date desc