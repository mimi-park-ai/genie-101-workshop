# Lab 6 · The semantic layer: describe your data

- **Time:** 25 minutes
- **Goal:** give the AI the business context a new employee would need: what each table is, what
the columns mean, and what your company's words mean.
- **You'll need:** Lab 5 finished (your Complaint-Triage Agent exists).

---

## What's a semantic layer?

The **semantic layer** (sometimes called an **ontology**) is a map between your data and your
business language. "NPS" is a business word; `score` is a column. The semantic layer connects
the two.

Databricks keeps it in **Unity Catalog**, so every tool reads the same definitions: your
dashboard, your Genie agent, and any other AI that uses your data.

---

## Part 1 · Describe your tables and columns (10 min)

1. In the left sidebar, open **Catalog → workspace → summit_financial**, and click
   **`gold_cases`**.
2. On the **Overview** tab, find the table description and click **✨ AI generate** (or
   **AI suggested description**).
3. Read the suggestion. Fix anything that's wrong, then click **Save**.
4. Scroll to the **columns** list. Click the description next to each of these columns, and
   type (or paste) exactly:

   | Column | Description |
   |---|---|
   | `is_complaint` | TRUE for complaints. Service requests are not complaints. |
   | `is_sla_breach` | TRUE if the complaint was resolved after its 8-week (56-day) deadline. |
   | `is_open` | TRUE if the case has not been resolved yet. |

   Press **Enter** (or click ✓) after each one.
5. Now open the **`nps_survey`** table, and set the **`score`** column description to:

   ```text
   0-10 survey score. 9-10 = promoter, 7-8 = passive, 0-6 = detractor.
   ```

✅ **You should see:** your descriptions next to each column.

---

## Part 2 · Group your data into a domain (5 min)

A **domain** groups the data that belongs to one part of the business, so people (and AI) can
find the trusted version.

1. In **Catalog**, click **Discover** (or **Domains**).
2. Click **Create domain** and name it **Customer Service**.
3. Add these four assets to it: `gold_cases`, `gold_interactions`, `nps_survey`,
   `call_insights`.
4. For each of the two gold tables, open it and mark it as **Certified**.

✅ **You should see:** the Customer Service domain listing four assets, with the two gold tables
marked certified.

---

## Part 3 · Define your business terms (10 min)

1. Open your **Customer Service** domain, and add a **page** (or **term**) for each of these:

   | Term | Definition |
   |---|---|
   | **NPS (Net Promoter Score)** | % of promoters (score 9–10) minus % of detractors (score 0–6), over all survey responses. A number from −100 to +100. It is **not** an average score. |
   | **Complaint** | A service case where `case_type = 'COMPLAINT'`. Service requests are not complaints. |
   | **SLA breach rate** | Resolved complaints that were resolved after their 56-day deadline, divided by all resolved complaints. Open complaints are not counted. |

2. Go back to your **Complaint-Triage Agent** (sidebar → **Genie**), and ask again:
   *"What is our NPS?"*

✅ **You should see:** an answer closer to **34** than before. If not, don't worry: Lab 7 makes it
exact.

> 💡 **How the agent learns.** Genie's **Ontology** combines the definitions you write down here
> with what it learns from how your data is actually used, such as saved queries and dashboards.
> You write down the important definitions; Genie fills in the rest.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| I don't see **AI generate** | Type a description yourself, such as "One row per service case, complaints and service requests." |
| I can't find **Discover** or **domains** | This feature may not be in your account yet. Skip Part 2, and in Part 3 paste the three definitions into your agent's **Instructions** instead. |
| I can't add pages or terms | Same fix: paste the three definitions into your agent's **Instructions**. |

## What you learned

- How to describe tables and columns so people and AI understand them.
- How domains and certification help everyone find trusted data.
- How business definitions make AI answers more accurate.
