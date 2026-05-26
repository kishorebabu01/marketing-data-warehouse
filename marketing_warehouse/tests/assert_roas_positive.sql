-- This test FAILS if any ROAS value is negative
-- Negative ROAS means we somehow lost money
-- on revenue that doesn't exist — data error

select *
from {{ ref('mart_acquisition') }}
where roas < 0