# Lab 3 · Visual Data Prep → gold tables

- **Time:** 40 minutes
- **Goal:** clean and join the raw data **without writing code**, and produce three trusted
**gold** tables that everything else today is built on.
- **You'll need:** Lab 2 finished (the five tables are in `workspace.summit_financial`).

---

## Why this matters

Data teams talk about layers: **raw** (as it arrived) and **gold** (clean, trusted, ready for
reports and AI). If the data going into an AI agent is messy, its answers will be too.

You'll use **Visual Data Prep**. You build a flow of steps on a canvas, like a flowchart, and
Databricks turns it into a data pipeline. You'll use five kinds of step:

| Step | What it does |
|---|---|
| **Source** | Reads a table |
| **Unique** | Removes duplicate rows |
| **Prepare** | Cleans columns: trim spaces, change case, change type, add calculated columns |
| **Join** | Combines two tables on a matching column |
| **Output** | Saves the result as a table |

> ✨ **Shortcut:** Visual Data Prep has an AI assistant. You can describe a step in plain
> English, such as *"remove duplicate rows"*, and it adds the step for you. Try it for at least
> one step, and check what it did.

---

## Part 1 · Create the flow (2 min)

1. Click **+ New → Visual data prep**.
2. Click the name at the top and rename it **`summit_gold`**.

✅ **You should see:** an empty canvas.

---

## Part 2 · Build gold_customers (10 min)

1. **Source:** add a **Source** step. Choose the table
   `workspace.summit_financial.customers_raw`.
2. **Unique:** add a **Unique** step after the source. Leave it on **all columns**.
   *Why: a few customers were exported twice.*
3. **Prepare:** add a **Prepare** step after Unique, and add these actions:
   1. **Trim** the `segment` column (both sides).
   2. **Text case** on `segment`: **UPPERCASE**.
   3. **Trim** the `city` column.
   4. **Formula** that sets `city` to:

      ```sql
      CASE WHEN city IS NULL OR city = '' THEN 'UNKNOWN' ELSE city END
      ```

4. **Output:** add an **Output** step. Set catalog `workspace`, schema `summit_financial`,
   table name **`gold_customers`**, write mode **Overwrite**.

✅ **You should see:** in the preview of the Prepare step, `segment` only ever says RETAIL,
PREMIER, or WEALTH.

---

## Part 3 · Build gold_cases (20 min)

1. **Source:** add a second **Source** step for `service_cases_raw`.
2. **Unique:** add a **Unique** step after it (all columns).
3. **Prepare:** add a **Prepare** step with these actions:
   1. **Trim** `severity`.
   2. **Text case** on `severity`: **UPPERCASE**.
   3. **Cast** `open_date` to **date**.
   4. **Cast** `sla_due_date` to **date**.
   5. **Cast** `resolved_date` to **date**. Blank values should become null.
4. **Join:** add a **Join** step.
   - **Left input:** the Prepare step you just made.
   - **Right input:** the Prepare step from `gold_customers` (Part 2, step 3).
   - **Join type:** **Left**.
   - **Match on:** `customer_id` = `customer_id`.
   - **Columns to keep from the right side:** `full_name` (rename it **`customer_name`**),
     `email` (rename it **`customer_email`**), `segment`, and `city`. Untick the rest.
5. **Prepare (calculated columns):** add a **Prepare** step after the Join, with four
   **Formula** actions:

   | New column | Formula | Meaning |
   |---|---|---|
   | `is_complaint` | `case_type = 'COMPLAINT'` | A complaint, not a service request |
   | `is_open` | `resolved_date IS NULL` | Not resolved yet |
   | `is_sla_breach` | `resolved_date IS NOT NULL AND resolved_date > sla_due_date` | Resolved after the 8-week deadline |
   | `days_to_resolve` | `datediff(resolved_date, open_date)` | How long it took |

6. **Output:** table name **`gold_cases`**, write mode **Overwrite**.

---

## Part 4 · Build gold_interactions (8 min)

1. **Source:** add a **Source** step for `interactions_raw`.
2. **Prepare:** add these actions:
   1. **Trim** `channel`.
   2. **Text case** on `channel`: **UPPERCASE**.
   3. **Cast** `interaction_time` to **timestamp**.
   4. **Cast** `first_contact_resolved` to **boolean**.
3. **Join:** **Left** join to the `gold_customers` Prepare step on `customer_id`. From the
   right side keep only **`segment`**.
4. **Output:** table name **`gold_interactions`**, write mode **Overwrite**.

---

## Part 5 · Run it

1. Click **Run** (top right).
2. Wait for every step to show a green tick.

✅ **You should see:** three green **Output** steps.

---

## Check your work

Open the **SQL Editor** and run:

```sql
SELECT 'gold_customers' AS gold_table, count(*) AS row_count FROM workspace.summit_financial.gold_customers
UNION ALL SELECT 'gold_cases', count(*) FROM workspace.summit_financial.gold_cases
UNION ALL SELECT 'gold_interactions', count(*) FROM workspace.summit_financial.gold_interactions;
```

✅ **You should see:**

| gold_table | row_count |
|---|---|
| gold_customers | 1,000 |
| gold_cases | 3,000 |
| gold_interactions | 4,000 |

`gold_cases` has 3,000 rows, not 3,020, because the duplicates are gone.

## Troubleshooting

| Problem | What to do |
|---|---|
| A Join step shows an error | Check both inputs are connected, and the join is on `customer_id`. |
| `gold_cases` has more than 3,000 rows | The **Unique** step is missing or isn't connected before Prepare. |
| `segment` still shows mixed case | The Text case action is on the wrong column, or is switched off. |
| I want to see the finished flow | Download **`summit_gold.designer.ipynb`** from the class folder. In Databricks, open **Workspace → Users → your email**, click **⋮ → Import**, and choose the file. Open it and click **Run**. |
| I'm stuck or out of time | Import the finished flow (above), or use the SQL **fallback** below. Both build the same three tables. |

### Fallback: build the gold tables with SQL

If Visual Data Prep isn't working for you, paste this whole block into the **SQL Editor**,
click **Run**, and carry on with Lab 4.

```sql
USE CATALOG workspace;
USE SCHEMA summit_financial;

CREATE OR REPLACE TABLE gold_customers AS
SELECT DISTINCT
  customer_id, full_name, email,
  upper(trim(segment)) AS segment,
  age_band,
  CAST(tenure_years AS INT) AS tenure_years,
  preferred_channel,
  coalesce(nullif(trim(city), ''), 'UNKNOWN') AS city,
  try_cast(CAST(onboard_date AS STRING) AS DATE) AS onboard_date
FROM customers_raw;

CREATE OR REPLACE TABLE gold_cases AS
WITH cases AS (
  SELECT DISTINCT
    case_id, customer_id, case_type,
    nullif(trim(complaint_category), '') AS complaint_category,
    product,
    upper(trim(severity)) AS severity,
    channel_opened, agent_team,
    try_cast(CAST(open_date AS STRING) AS DATE) AS open_date,
    try_cast(CAST(sla_due_date AS STRING) AS DATE) AS sla_due_date,
    try_cast(nullif(CAST(resolved_date AS STRING), '') AS DATE) AS resolved_date,
    nullif(trim(resolution_outcome), '') AS resolution_outcome
  FROM service_cases_raw
)
SELECT
  c.*,
  cu.full_name AS customer_name,
  cu.email AS customer_email,
  cu.segment,
  cu.city,
  c.case_type = 'COMPLAINT' AS is_complaint,
  c.resolved_date IS NULL AS is_open,
  c.resolved_date IS NOT NULL AND c.resolved_date > c.sla_due_date AS is_sla_breach,
  datediff(c.resolved_date, c.open_date) AS days_to_resolve
FROM cases c
LEFT JOIN gold_customers cu USING (customer_id);

CREATE OR REPLACE TABLE gold_interactions AS
SELECT
  i.interaction_id, i.customer_id,
  nullif(trim(i.case_id), '') AS case_id,
  upper(trim(i.channel)) AS channel,
  i.reason,
  try_cast(CAST(i.interaction_time AS STRING) AS TIMESTAMP) AS interaction_time,
  CAST(i.duration_minutes AS DOUBLE) AS duration_minutes,
  i.outcome,
  upper(CAST(i.first_contact_resolved AS STRING)) = 'TRUE' AS first_contact_resolved,
  cu.segment
FROM interactions_raw i
LEFT JOIN gold_customers cu USING (customer_id);
```

## What you learned

- How to clean data with no code: remove duplicates, fix text, change types.
- How to join two tables, and add calculated columns.
- Why trusted **gold** tables come before dashboards and AI.
