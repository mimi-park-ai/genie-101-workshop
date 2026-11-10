# Lab 5 · Build a Genie Agent

- **Time:** 35 minutes
- **Goal:** create an AI agent the Customer Service team can ask about complaints in plain
English, then measure how accurate it is.
- **You'll need:** Lab 3 finished (the gold tables exist).

---

## What's a Genie Agent?

A **Genie Agent** is an AI assistant you point at specific tables and give instructions to. When
someone asks it a question, it writes the SQL, runs it, and explains the answer. It only sees the
data you give it.

---

## Part 1 · Create the Complaint-Triage Agent (10 min)

1. In the left sidebar, click **Genie**.
2. Click **+ New** to create a new Genie Agent.
3. **Add data:** choose these four tables from `workspace.summit_financial`, then click
   **Create** (or **Save**):
   - `gold_cases`
   - `gold_interactions`
   - `nps_survey`
   - `call_insights`
4. **Name it:** click the title at the top and rename it **Complaint-Triage Agent**.
5. **Add instructions:** open **Configure → Instructions** (or the **Instructions** tab), and
   paste:

   ```text
   You help the Summit Financial customer service team triage complaints.
   - Prioritize open complaints by severity (CRITICAL first), then by the soonest sla_due_date.
   - When asked about a specific case, use call_insights to summarize what the customer said.
   - Always show the case_id and customer_name so the team can follow up.
   ```

   Click **Save**.
6. **Add sample questions** (they help people know what to ask). Find **Sample questions**
   and add these three:
   - Which open complaints are highest priority right now?
   - Which open complaints are closest to their SLA deadline?
   - Summarize what the customer said about case CASE-002747.

✅ **You should see:** your agent's chat page, with the three sample questions shown as buttons.

---

## Part 2 · Try it (10 min)

1. Click each sample question and read the answers.
2. Under an answer, click **Show code** (or **View SQL**). That's the SQL Genie wrote. This is how
   you check its work.
3. Ask a few questions of your own, such as *"How many complaints are about fraud?"*
4. Now ask the two tricky ones, and **write down the answers**:
   - *What is our NPS?*
   - *What is our SLA breach rate?*

> 💡 Don't worry if these look wrong. They depend on **business definitions** the agent hasn't
> been taught yet. You'll fix that in Labs 6 and 7.

---

## Part 3 · Benchmark it: your "before" score (15 min)

**Benchmarks** are a test: questions with known correct answers. Genie runs them all and tells
you which it got right.

1. In your agent, open **Benchmarks**.
2. For each of the 8 questions below: click **Add benchmark**, paste the **question**, paste the
   **reference SQL** as the answer, and save.
3. When all 8 are added, click **Run all** (or **Run benchmarks**).
4. When it finishes, fill in the **Before** column of the scorecard at the end of this lab.

| # | Question | Correct answer |
|---|---|---|
| 1 | What is our NPS? | 34 |
| 2 | What is NPS by channel? | Branch 38, Call center 30, Mobile 39, Online 35 |
| 3 | How many complaints do we have? | 2,108 |
| 4 | What is our SLA breach rate? | 11.5% of resolved complaints |
| 5 | How many open critical complaints are there? | 20 |
| 6 | What is our first-contact resolution rate? | 68.0% |
| 7 | Which complaint category has the most complaints? | FEES_CHARGES (373) |
| 8 | What is the average number of days to resolve a complaint? | 31.1 days |

**Reference SQL** (one per question):

```sql
-- 1. What is our NPS?
SELECT round(100 * (count_if(score >= 9) - count_if(score <= 6)) / count(*)) AS nps
FROM workspace.summit_financial.nps_survey;

-- 2. What is NPS by channel?
SELECT channel, round(100 * (count_if(score >= 9) - count_if(score <= 6)) / count(*)) AS nps
FROM workspace.summit_financial.nps_survey
GROUP BY channel ORDER BY channel;

-- 3. How many complaints do we have?
SELECT count(*) AS complaints FROM workspace.summit_financial.gold_cases WHERE is_complaint;

-- 4. What is our SLA breach rate?
SELECT round(100 * count_if(is_sla_breach) / count(*), 1) AS sla_breach_pct
FROM workspace.summit_financial.gold_cases
WHERE is_complaint AND NOT is_open;

-- 5. How many open critical complaints are there?
SELECT count(*) AS open_critical FROM workspace.summit_financial.gold_cases
WHERE is_complaint AND is_open AND severity = 'CRITICAL';

-- 6. What is our first-contact resolution rate?
SELECT round(100 * avg(CAST(first_contact_resolved AS INT)), 1) AS fcr_pct
FROM workspace.summit_financial.gold_interactions;

-- 7. Which complaint category has the most complaints?
SELECT complaint_category, count(*) AS complaints
FROM workspace.summit_financial.gold_cases
WHERE is_complaint
GROUP BY complaint_category ORDER BY complaints DESC LIMIT 1;

-- 8. What is the average number of days to resolve a complaint?
SELECT round(avg(days_to_resolve), 1) AS avg_days
FROM workspace.summit_financial.gold_cases
WHERE is_complaint AND NOT is_open;
```

> 💡 Don't worry if you score 5 or 6 out of 8. Questions 1–4 rely on business definitions,
> like "NPS" and "SLA breach", that the agent hasn't learned yet. That's what Labs 6 and 7 are for.

---

## Your scorecard

Keep this. You'll fill in **After** in Lab 7.

| # | Question | Before (✅ / ❌) | After (✅ / ❌) |
|---|---|---|---|
| 1 | NPS | | |
| 2 | NPS by channel | | |
| 3 | Number of complaints | | |
| 4 | SLA breach rate | | |
| 5 | Open critical complaints | | |
| 6 | First-contact resolution | | |
| 7 | Top complaint category | | |
| 8 | Average days to resolve | | |
| | **Score** | ___ / 8 | ___ / 8 |

## Troubleshooting

| Problem | What to do |
|---|---|
| I can't find a table when adding data | Check you're in the `workspace` catalog, `summit_financial` schema. Re-do Lab 3 if the gold tables are missing. |
| I can't find Benchmarks | Ask the 8 questions in the chat instead, and compare its answers with the table above. |
| An answer says "no results" | Click **Show code**. Check it's using the right table and filter. |

## What you learned

- How to build an AI agent on your own data, with instructions and sample questions.
- How to check an AI answer by reading the SQL it wrote.
- How benchmarks measure an agent's accuracy objectively.
