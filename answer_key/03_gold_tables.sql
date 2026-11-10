-- Lab 3 answer key: the gold tables, in SQL.
--
-- Two uses:
--   1. Check your Visual Data Prep output against this.
--   2. FALLBACK: if Visual Data Prep isn't available on the day, paste this into the SQL editor
--      and run it to create the gold tables, then carry on with Lab 4.
--
-- Casts go via STRING so this works whether the upload inferred a column as text or as a
-- date/boolean. Assumes the Lab 2 uploads landed in workspace.summit_financial with these names:
--   customers_raw, service_cases_raw, interactions_raw, nps_survey, call_insights

USE CATALOG workspace;
USE SCHEMA summit_financial;

-- gold_customers: one row per customer, tidy segment and city
CREATE OR REPLACE TABLE gold_customers
COMMENT 'One row per Summit Financial customer. Cleaned from customers_raw: duplicates removed, segment standardized, blank city set to UNKNOWN.'
AS
SELECT DISTINCT
  customer_id,
  full_name,
  email,
  upper(trim(segment))                          AS segment,
  age_band,
  CAST(tenure_years AS INT)                     AS tenure_years,
  preferred_channel,
  coalesce(nullif(trim(city), ''), 'UNKNOWN')   AS city,
  try_cast(CAST(onboard_date AS STRING) AS DATE) AS onboard_date
FROM customers_raw;

-- gold_cases: one row per service case, joined to the customer, with derived flags
CREATE OR REPLACE TABLE gold_cases
COMMENT 'One row per service case (complaints and service requests), joined to the customer. Complaint SLA is 56 days from open_date.'
AS
WITH cases AS (
  SELECT DISTINCT
    case_id, customer_id, case_type,
    nullif(trim(complaint_category), '')        AS complaint_category,
    product,
    upper(trim(severity))                       AS severity,
    channel_opened, agent_team,
    try_cast(CAST(open_date AS STRING) AS DATE)    AS open_date,
    try_cast(CAST(sla_due_date AS STRING) AS DATE) AS sla_due_date,
    try_cast(nullif(CAST(resolved_date AS STRING), '') AS DATE) AS resolved_date,
    nullif(trim(resolution_outcome), '')        AS resolution_outcome
  FROM service_cases_raw
)
SELECT
  c.*,
  cu.full_name AS customer_name,
  cu.email     AS customer_email,
  cu.segment,
  cu.city,
  c.case_type = 'COMPLAINT'                                   AS is_complaint,
  c.resolved_date IS NULL                                     AS is_open,
  c.resolved_date IS NOT NULL AND c.resolved_date > c.sla_due_date AS is_sla_breach,
  datediff(c.resolved_date, c.open_date)                      AS days_to_resolve
FROM cases c
LEFT JOIN gold_customers cu USING (customer_id);

-- gold_interactions: one row per customer contact, tidy channel, real timestamp and boolean
CREATE OR REPLACE TABLE gold_interactions
COMMENT 'One row per customer contact (call, app, web, branch), joined to the customer segment.'
AS
SELECT
  i.interaction_id,
  i.customer_id,
  nullif(trim(i.case_id), '')                             AS case_id,
  upper(trim(i.channel))                                  AS channel,
  i.reason,
  try_cast(CAST(i.interaction_time AS STRING) AS TIMESTAMP) AS interaction_time,
  CAST(i.duration_minutes AS DOUBLE)                      AS duration_minutes,
  i.outcome,
  upper(CAST(i.first_contact_resolved AS STRING)) = 'TRUE' AS first_contact_resolved,
  cu.segment
FROM interactions_raw i
LEFT JOIN gold_customers cu USING (customer_id);

-- Quick check: you should see 1,000 / 3,000 / 4,000 rows.
SELECT 'gold_customers' AS t, count(*) AS n FROM gold_customers
UNION ALL SELECT 'gold_cases', count(*) FROM gold_cases
UNION ALL SELECT 'gold_interactions', count(*) FROM gold_interactions;
