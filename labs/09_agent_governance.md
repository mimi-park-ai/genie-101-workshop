# Lab 9 · Agent governance

- **Time:** 25 minutes
- **Goal:** control what your agent can see and show, and prove it can be trusted.
- **You'll need:** Lab 5 finished (your agent exists).

---

## The key idea

An AI agent must never become a back door to data people aren't allowed to see. In Databricks,
the agent **inherits the permissions of the person asking**: if you can't see a row, neither can
the agent when you use it.

The rules live **on the data**, in Unity Catalog, not in the agent. So they apply everywhere: the
agent, dashboards, and the SQL Editor.

---

## Part 1 · Hide personal data with a column mask (10 min)

Customer emails are personal information. Most of the Customer Service team doesn't need them.

1. Open the **SQL Editor**, paste this, and click **Run**:

   ```sql
   USE CATALOG workspace;
   USE SCHEMA summit_financial;

   -- Who may see customer emails (empty for now)
   CREATE TABLE IF NOT EXISTS pii_access (user_email STRING);

   -- The mask: show the real email only to people in pii_access
   CREATE OR REPLACE FUNCTION mask_email(email STRING)
   RETURNS STRING
   RETURN CASE
     WHEN EXISTS (SELECT 1 FROM workspace.summit_financial.pii_access WHERE user_email = current_user())
       THEN email
     ELSE concat('****@', split(email, '@')[1])
   END;

   ALTER TABLE gold_cases ALTER COLUMN customer_email SET MASK mask_email;

   SELECT case_id, customer_name, customer_email FROM gold_cases LIMIT 5;
   ```

   ✅ **You should see:** emails shown as `****@example.com`.

2. Ask your **Complaint-Triage Agent**:
   *"Show the email of the customer for the most urgent open complaint."*

   ✅ **You should see:** a masked email. The agent follows the same rule as you.

3. Now give yourself access. Run:

   ```sql
   INSERT INTO workspace.summit_financial.pii_access VALUES (current_user());
   ```

4. Ask the agent the same question again.

   ✅ **You should see:** the real email address.

---

## Part 2 · Limit rows with a row filter (10 min)

Imagine the **Retail** team should only see Retail customers' cases.

1. Run:

   ```sql
   USE CATALOG workspace;
   USE SCHEMA summit_financial;

   -- Which segments each person may see. You start with RETAIL only.
   CREATE OR REPLACE TABLE segment_access (user_email STRING, segment STRING);
   INSERT INTO segment_access VALUES (current_user(), 'RETAIL');

   -- The filter: a row is visible only if its segment is in your list
   CREATE OR REPLACE FUNCTION segment_filter(segment STRING)
   RETURNS BOOLEAN
   RETURN EXISTS (
     SELECT 1 FROM workspace.summit_financial.segment_access a
     WHERE a.user_email = current_user() AND a.segment = segment_filter.segment
   );

   ALTER TABLE gold_cases SET ROW FILTER segment_filter ON (segment);
   ```

2. Ask your agent: *"How many complaints do we have, by segment?"*

   ✅ **You should see:** only **RETAIL**, with **1,524** complaints.

3. Now give yourself every segment. Run:

   ```sql
   INSERT INTO workspace.summit_financial.segment_access
   VALUES (current_user(), 'PREMIER'), (current_user(), 'WEALTH');
   ```

4. Ask the agent the same question again.

   ✅ **You should see:** all three segments: RETAIL 1,524, PREMIER 483, WEALTH 101 (2,108 in
   total).

> 💡 You didn't change the agent at all. You changed the **data's rules**, and the agent
> followed them automatically.

---

## Part 3 · Prove it's right, and keep watching (5 min)

Governance isn't only about **access**. It's also about **trust**.

1. **Benchmarks:** your before-and-after scores from Labs 5 and 7 are your evidence that the
   agent answers correctly. Re-run them whenever you change the agent.
2. **Monitoring:** open your agent and click **Monitoring**. You can see every question asked,
   the SQL that ran, and any 👎 feedback. That's how a team finds and fixes bad answers.
3. **Sharing:** click **Share**. Look at the permission levels. People you share with can use the
   agent, but still only see the data **they** are allowed to see.

---

## Part 4 · Clean up (1 min)

Remove the filter and mask, so later labs see all the data:

```sql
ALTER TABLE workspace.summit_financial.gold_cases DROP ROW FILTER;
ALTER TABLE workspace.summit_financial.gold_cases ALTER COLUMN customer_email DROP MASK;
```

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `SET MASK` or `SET ROW FILTER` gives an error | Check you ran the `CREATE FUNCTION` part first, and that `gold_cases` exists. |
| The agent still shows real emails in Part 1 | You may already be in `pii_access`. Run `DELETE FROM workspace.summit_financial.pii_access;` and ask again. |
| The counts don't change | Ask the question in a **new chat**, so the agent runs a fresh query. |

## What you learned

- How column masks and row filters protect data in every tool at once.
- Why an AI agent should follow the asking person's permissions.
- How benchmarks and monitoring build trust in an agent over time.
