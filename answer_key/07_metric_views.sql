-- Lab 7 answer key: the three metric views.
-- Run this whole file in the SQL Editor, or paste each YAML block into the metric view editor.
--
-- YAML version 1.1 supports display names and synonyms (which help Genie match the words people
-- actually use). If your workspace rejects version 1.1, change it to 0.1 and delete the
-- display_name and synonyms lines.

USE CATALOG workspace;
USE SCHEMA summit_financial;

CREATE OR REPLACE VIEW cs_complaint_metrics
WITH METRICS
LANGUAGE YAML
COMMENT 'Certified complaint KPIs for Summit Financial customer service.'
AS $$
version: 1.1
source: workspace.summit_financial.gold_cases
filter: is_complaint
dimensions:
  - name: segment
    expr: segment
  - name: product
    expr: product
  - name: complaint_category
    expr: complaint_category
  - name: severity
    expr: severity
  - name: agent_team
    expr: agent_team
  - name: channel_opened
    expr: channel_opened
  - name: open_month
    expr: DATE_TRUNC('MONTH', open_date)
    display_name: Month opened
measures:
  - name: complaints
    expr: COUNT(1)
    display_name: Complaints
    synonyms: [complaint count, number of complaints]
  - name: open_complaints
    expr: COUNT(1) FILTER (WHERE is_open)
    display_name: Open complaints
    synonyms: [unresolved complaints, backlog]
  - name: sla_breach_rate
    expr: COUNT(1) FILTER (WHERE is_sla_breach) * 100.0 / COUNT(1) FILTER (WHERE NOT is_open)
    display_name: SLA breach rate (%)
    synonyms: [breach rate, SLA breaches, late complaints]
  - name: avg_days_to_resolve
    expr: AVG(days_to_resolve) FILTER (WHERE NOT is_open)
    display_name: Average days to resolve
$$;

CREATE OR REPLACE VIEW cs_nps_metrics
WITH METRICS
LANGUAGE YAML
COMMENT 'Certified NPS definition: % promoters (9-10) minus % detractors (0-6).'
AS $$
version: 1.1
source: workspace.summit_financial.nps_survey
dimensions:
  - name: channel
    expr: channel
  - name: survey_month
    expr: DATE_TRUNC('MONTH', survey_date)
    display_name: Survey month
measures:
  - name: nps
    expr: (COUNT(1) FILTER (WHERE score >= 9) - COUNT(1) FILTER (WHERE score <= 6)) * 100.0 / COUNT(1)
    display_name: NPS
    synonyms: [net promoter score, customer satisfaction score]
  - name: responses
    expr: COUNT(1)
    display_name: Survey responses
  - name: promoters
    expr: COUNT(1) FILTER (WHERE score >= 9)
  - name: detractors
    expr: COUNT(1) FILTER (WHERE score <= 6)
$$;

CREATE OR REPLACE VIEW cs_contact_metrics
WITH METRICS
LANGUAGE YAML
COMMENT 'Certified contact-center KPIs: first-contact resolution and handle time.'
AS $$
version: 1.1
source: workspace.summit_financial.gold_interactions
dimensions:
  - name: channel
    expr: channel
  - name: segment
    expr: segment
  - name: reason
    expr: reason
  - name: contact_month
    expr: DATE_TRUNC('MONTH', interaction_time)
    display_name: Month
measures:
  - name: contacts
    expr: COUNT(1)
    display_name: Contacts
  - name: fcr_rate
    expr: AVG(CAST(first_contact_resolved AS INT)) * 100
    display_name: First-contact resolution (%)
    synonyms: [FCR, first call resolution]
  - name: avg_handle_minutes
    expr: AVG(duration_minutes)
    display_name: Average handle time (min)
    synonyms: [AHT, handle time]
$$;

-- Check: should return 34
SELECT MEASURE(nps) AS nps FROM cs_nps_metrics;
