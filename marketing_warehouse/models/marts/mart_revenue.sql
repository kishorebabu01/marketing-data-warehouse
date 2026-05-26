-- ============================================================
-- mart_revenue.sql
-- Answers: How much revenue are we generating?
--          Is each customer worth more than they cost us?
-- ============================================================

with acquisitions as (

    -- Get daily spend and conversions from acquisition mart
    select
        date,
        channel,
        total_spend,
        total_conversions,
        cac

    from {{ ref('mart_acquisition') }}

),

product_events as (

    -- Get purchase and activation data from PostHog
    select
        event_date          as date,
        channel,
        countif(is_purchase = true)     as purchases,
        countif(is_activation = true)   as activations

    from {{ ref('stg_posthog') }}
    group by event_date, channel

),

combined as (

    select
        a.date,
        a.channel,
        a.total_spend,
        a.total_conversions,
        a.cac,
        coalesce(p.purchases, 0)    as purchases,
        coalesce(p.activations, 0)  as activations

    from acquisitions a
    left join product_events p
        on a.date = p.date
        and a.channel = p.channel

),

final as (

    select
        date,
        channel,
        total_spend,
        total_conversions,
        purchases,
        activations,
        cac,

        -- Revenue estimate: purchases x avg order value (€50 demo)
        purchases * 50                              as estimated_revenue_eur,

        -- MRR estimate: activated users x monthly subscription (€29 demo)
        activations * 29                            as estimated_mrr_eur,

        -- ROAS = revenue / ad spend
        -- For every €1 spent on ads, how much revenue came back?
        safe_divide(purchases * 50, total_spend)    as roas,

        -- LTV estimate: avg customer pays €29/month for 6 months
        activations * 29 * 6                        as estimated_ltv_eur,

        -- LTV:CAC ratio — the most important SaaS metric
        -- If LTV:CAC > 3, the business model works
        -- If LTV:CAC < 1, you lose money on every customer
        safe_divide(activations * 29 * 6, cac)      as ltv_cac_ratio,

        -- CAC Payback Period = CAC / monthly revenue per customer
        -- How many months until a customer pays back their acquisition cost?
        safe_divide(cac, 29)                        as cac_payback_months

    from combined

)

select * from final
order by date desc, channel