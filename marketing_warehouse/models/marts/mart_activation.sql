-- ============================================================
-- mart_activation.sql
-- Answers: Of everyone who signed up, how many activated?
-- Activation = a user completing a key action after signup
-- Example: signing up is step 1, using a feature is activation
-- ============================================================

with signups as (

    -- Count total signups per day per channel
    select
        event_date         as date,
        channel,
        countif(is_signup = true)       as total_signups,
        countif(is_activation = true)   as total_activations,
        countif(is_purchase = true)     as total_purchases,
        countif(is_churn = true)        as total_churns

    from {{ ref('stg_posthog') }}
    group by event_date, channel

),

final as (

    select
        date,
        channel,
        total_signups,
        total_activations,
        total_purchases,
        total_churns,

        -- Activation Rate = activations / signups
        -- What % of people who signed up actually used the product?
        safe_divide(total_activations, total_signups)   as activation_rate,

        -- Purchase Rate = purchases / activations
        -- What % of activated users made a purchase?
        safe_divide(total_purchases, total_activations) as purchase_rate,

        -- Churn Rate = churns / signups
        -- What % of users left?
        safe_divide(total_churns, total_signups)        as churn_rate

    from signups
    where total_signups > 0

)

select * from final
order by date desc, channel