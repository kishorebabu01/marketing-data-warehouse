-- This test FAILS if any CAC value is negative
-- A negative CAC is impossible — it means a data error
-- dbt tests pass when the query returns ZERO rows
-- So we select rows where CAC is wrong — if none found, test passes

select *
from {{ ref('mart_acquisition') }}
where cac < 0