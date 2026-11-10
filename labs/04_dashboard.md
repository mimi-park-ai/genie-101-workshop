# Lab 4 · AI/BI Dashboard

- **Time:** 35 minutes
- **Goal:** build a one-page dashboard for Summit Financial's VP of Customer Service, from your gold
tables, with AI doing most of the work.
- **You'll need:** Lab 3 finished (`gold_cases`, `gold_interactions` exist).

---

## Part 1 · Create the dashboard (5 min)

1. In the left sidebar, click **Dashboards**, then **Create dashboard**.
2. Click the name at the top (something like *New Dashboard*) and rename it
   **Summit Financial · Customer Service**.
3. Click the **Data** tab at the top.
4. Click **Add data source** (or **Select a table**), and add these three tables from
   `workspace.summit_financial`, one at a time:
   - `gold_cases`
   - `gold_interactions`
   - `nps_survey`

✅ **You should see:** three datasets listed on the **Data** tab, each with a preview of rows.

5. Click the **Canvas** tab (next to **Data**) to go back to the blank page.

---

## Part 2 · Let AI build the first draft (15 min)

1. Open the dashboard's AI assistant: look for the **✨ assistant** button on the canvas or in
   the toolbar.
2. Paste the first prompt below and press **Enter**. Wait for it to add the visual, then paste
   the next one.

   **Prompt 1:**

   ```text
   Add three counters from gold_cases: total complaints (rows where is_complaint is true),
   open complaints (is_complaint and is_open), and SLA breach rate. SLA breach rate =
   complaints where is_sla_breach is true, divided by complaints where is_open is false.
   ```

   **Prompt 2:**

   ```text
   Add a bar chart of complaints by complaint_category, largest first.
   ```

   **Prompt 3:**

   ```text
   Add a line chart of complaints opened per week, using open_date.
   ```

   **Prompt 4:**

   ```text
   Add a table of open CRITICAL complaints showing case_id, customer_name, product and
   sla_due_date, soonest deadline first.
   ```

3. **Check the AI's work.** AI is fast, but not always right. Open the **SQL Editor** in a new
   tab and run:

   ```sql
   SELECT count(*) AS complaints
   FROM workspace.summit_financial.gold_cases
   WHERE is_complaint;
   ```

✅ **You should see:** **2,108**. Does your "total complaints" counter say the same? If not,
click the counter, look at how it's calculated, and ask the assistant to fix it.

---

## Part 3 · Finish it by hand (10 min)

1. **Add a filter:**
   1. Click **Add a filter** in the toolbar and place it at the top of the page.
   2. Set the field to **`segment`** (from `gold_cases`).
   3. Make sure every visual is connected to the filter.
2. **Titles:** click each visual and give it a clear title, such as "Open critical complaints".
3. **Arrange:** drag the counters to the top row, and the charts underneath.
4. Click **Publish** (top right), then **Publish** again to confirm.

✅ **You should see:** your published dashboard. Try the segment filter: pick **WEALTH**, and
every number should get smaller.

---

## Part 4 · Ask the dashboard a question (5 min)

1. On the published dashboard, click **Ask Genie**.
2. Type: *"Which complaint category has the most open critical complaints?"*

✅ **You should see:** an answer, plus the chart or table it used.

> 💡 **Keep this in mind for Lab 7:** ask the dashboard *"What is our NPS?"* (the `nps_survey`
> table has the scores). NPS is **not** an average score, and AI often gets it wrong until you
> teach it. Note what it says.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| I can't find the AI assistant | Build the four visuals by hand: click **Add a visualization**, pick the dataset, and choose the chart type. |
| A chart is empty | Check it's using the right dataset, and that the filter isn't set to a value with no data. |
| The complaint count isn't 2,108 | The visual is counting every case. Add a filter on `is_complaint = true`. |
| Publish is greyed out | Make sure at least one visual is on the page, and you've saved. |

## What you learned

- How to build a dashboard on trusted gold tables.
- How to use AI to draft a dashboard, and why you still check its numbers.
- How filters and **Ask Genie** let leaders explore on their own.
