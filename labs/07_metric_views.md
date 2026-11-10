# Lab 7 · Metric views: before & after

- **Time:** 35 minutes
- **Goal:** define your key metrics **once**, as metric views, then prove they make your agent more
accurate by re-running your benchmarks.
- **You'll need:** Lab 5 finished, including your **Before** score.

---

## What's a metric view?

In Lab 6 you *described* your metrics in words. A **metric view** goes further: it stores the
**calculation itself**. When your agent or dashboard asks for "NPS", Databricks uses your
formula, every time, instead of the AI guessing.

---

## Part 1 · Create the three metric views (15 min)

1. Open the **SQL Editor**.
2. Paste this whole block and click **Run**. It creates three metric views:

   | Metric view | Built on | Measures |
   |---|---|---|
   | `cs_complaint_metrics` | `gold_cases` | complaints, open complaints, SLA breach rate, average days to resolve |
   | `cs_nps_metrics` | `nps_survey` | NPS, responses, promoters, detractors |
   | `cs_contact_metrics` | `gold_interactions` | contacts, first-contact resolution rate, average handle time |

```sql
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
```

3. **Test one.** Metric views use `MEASURE()` to calculate a measure. Run:

   ```sql
   SELECT channel, round(MEASURE(nps)) AS nps
   FROM workspace.summit_financial.cs_nps_metrics
   GROUP BY channel
   ORDER BY channel;
   ```

✅ **You should see:** BRANCH 38, CALL_CENTER 30, MOBILE 39, ONLINE 35.

4. **Look at one in Catalog.** Open **Catalog → workspace → summit_financial →
   cs_nps_metrics**. You'll see its measures and dimensions listed, with their display names.

> 💡 **Prefer clicking?** You can also create a metric view in Catalog: open a table, click
> **Create → Metric view**, and use the visual editor.

---

## Part 2 · Add them to your agent (5 min)

1. Open your **Complaint-Triage Agent** (sidebar → **Genie**).
2. Open **Configure → Data** (or the **Data** tab), click **Add**, and add the three metric views:
   `cs_complaint_metrics`, `cs_nps_metrics`, `cs_contact_metrics`.
3. Open **Instructions**, and add this line at the end:

   ```text
   For NPS, complaint counts, SLA breach rate, and first-contact resolution, always use the metric views.
   ```

4. Click **Save**.

---

## Part 3 · Benchmark again: your "after" score (10 min)

1. In your agent, open **Benchmarks** and click **Run all** again.
2. Fill in the **After** column of your scorecard from Lab 5.

✅ **You should see:** questions 1–4 (NPS, NPS by channel, complaint count, SLA breach rate) go
from ❌ to ✅.

**This is the big idea of the day:** the AI didn't get smarter between your two runs. It got
**context**. Clean data, clear descriptions, and shared metric definitions are what make AI
trustworthy.

> 💡 **Discussion:** your Lab 4 dashboard can use these metric views too. Why would a company
> want the dashboard and the AI agent to share **one** definition of NPS?

---

## Troubleshooting

| Problem | What to do |
|---|---|
| The `CREATE ... WITH METRICS` block gives an error about the version | Change every `version: 1.1` to `version: 0.1`, delete every `display_name:` and `synonyms:` line, and run it again. |
| "Table not found" | Check the gold tables from Lab 3 exist in `workspace.summit_financial`. |
| My score didn't go up | Check the metric views were added to the agent (Part 2), and that you saved the new instruction. |

## What you learned

- How a metric view stores a business calculation once, for every tool to reuse.
- How to measure an AI improvement objectively, with before-and-after benchmarks.
