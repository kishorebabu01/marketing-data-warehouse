-- This test FAILS if retention rate is above 1 (above 100%)
-- A retention rate of 1.5 means 150% of users came back
-- which is mathematically impossible — data error

select *
from {{ ref('mart_retention') }}
where retention_rate > 1