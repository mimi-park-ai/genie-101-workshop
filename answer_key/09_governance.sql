-- Lab 9: column mask and row filter on gold_cases.
-- Run one part at a time, as the lab tells you.
--
-- Uses small "access" tables keyed on your login (current_user()), so it works in a
-- single-person Free Edition account. In a company you'd usually use groups instead
-- (is_account_group_member) or tag-based policies (ABAC), but the idea is the same.

USE CATALOG workspace;
USE SCHEMA summit_financial;

-- ===== Part 1: mask customer emails =====
CREATE TABLE IF NOT EXISTS pii_access (user_email STRING)
COMMENT 'People allowed to see customer email addresses.';

CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
RETURN CASE
  WHEN EXISTS (SELECT 1 FROM workspace.summit_financial.pii_access WHERE user_email = current_user())
    THEN email
  ELSE concat('****@', split(email, '@')[1])
END;

ALTER TABLE gold_cases ALTER COLUMN customer_email SET MASK mask_email;

-- Expect: masked
SELECT case_id, customer_name, customer_email FROM gold_cases LIMIT 5;

-- ===== Part 2: allow yourself to see emails =====
INSERT INTO pii_access VALUES (current_user());

-- Expect: real emails
SELECT case_id, customer_name, customer_email FROM gold_cases LIMIT 5;

-- ===== Part 3: RETAIL-only row filter =====
CREATE OR REPLACE TABLE segment_access (user_email STRING, segment STRING)
COMMENT 'Which customer segments each person may see.';
INSERT INTO segment_access VALUES (current_user(), 'RETAIL');

CREATE OR REPLACE FUNCTION segment_filter(segment STRING)
RETURNS BOOLEAN
RETURN EXISTS (
  SELECT 1 FROM workspace.summit_financial.segment_access a
  WHERE a.user_email = current_user() AND a.segment = segment_filter.segment
);

ALTER TABLE gold_cases SET ROW FILTER segment_filter ON (segment);

-- Expect: RETAIL 1,524 only
SELECT segment, count(*) AS complaints FROM gold_cases WHERE is_complaint GROUP BY segment;

-- ===== Part 4: give yourself every segment =====
INSERT INTO segment_access VALUES (current_user(), 'PREMIER'), (current_user(), 'WEALTH');

-- Expect: all three, 2,108 total
SELECT segment, count(*) AS complaints FROM gold_cases WHERE is_complaint GROUP BY segment;

-- ===== Part 5: clean up (so later labs see all data) =====
ALTER TABLE gold_cases DROP ROW FILTER;
ALTER TABLE gold_cases ALTER COLUMN customer_email DROP MASK;
