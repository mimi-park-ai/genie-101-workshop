# Lab 8 · Scheduling

- **Time:** 20 minutes
- **Goal:** make your work run itself: refresh the gold tables, email the dashboard, and have your
agent send a daily briefing, all on a schedule.
- **You'll need:** Labs 3, 4, and 5 finished.

> ⚠️ **Free Edition limit:** your account can only run a few things at the same time. Give each
> schedule below a **different time** (6:00, 6:30, and 8:00 AM). Don't set them all to the same
> minute.

---

## Part 1 · Refresh the gold tables every morning (5 min)

When the Customer Service team updates its Google Sheets, the gold tables should update too.

1. Open your **`summit_gold`** visual data prep. (Find it in **Workspace → Users → your email**,
   or use the search bar at the top.)
2. Click **Schedule** (top right).
3. Set it to run **every day** at **6:00 AM**, in your time zone.
4. Click **Create** (or **Save**).

✅ **You should see:** the schedule listed on the flow. It also appears in the sidebar under
**Jobs & Pipelines**.

> 💡 Today you uploaded the sheets by hand, so this schedule just re-runs on the same data. In a
> real company, a Google Drive connector would pull in the latest sheets first.

---

## Part 2 · Email the dashboard (5 min)

1. Open your published **Summit Financial · Customer Service** dashboard (sidebar →
   **Dashboards**).
2. Click **Schedule**, then **Add schedule**.
3. Set it to **every weekday** at **6:30 AM**.
4. Under **Subscribers**, add **yourself**.
5. Click **Create**.

✅ **You should see:** the new schedule in the list. Each weekday morning you'll get an email
snapshot of the dashboard.

---

## Part 3 · A daily briefing from your agent (10 min)

A **scheduled task** asks your agent a question on a timer, and sends you the answer.

1. Open your **Complaint-Triage Agent** (sidebar → **Genie**).
2. Look for **Schedule** or **Scheduled tasks** (in the chat menu, or the agent's **⋮** menu).
   Click **New scheduled task**.
3. Paste this as the task:

   ```text
   Send me the open CRITICAL and HIGH complaints that are due in the next 14 days,
   soonest deadline first, with case_id, customer_name, and a one-line summary.
   ```

4. Set it to **every weekday** at **8:00 AM**, and save.
5. Click **Run now** to test it without waiting until tomorrow.

✅ **You should see:** the briefing appear (or arrive by email) within a minute or two.

> 💡 This is the step from **a tool you ask** to **a coworker that tells you**. Nobody has to
> remember to check: the right person gets the right list every morning.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| A run says "queued" for a long time | Free Edition only runs a few things at once. Wait, or check your three schedules are at different times. |
| I can't find **Scheduled tasks** for the agent | This feature may not be in your account yet. Skip Part 3; your instructor will show it. |
| The dashboard email didn't arrive | Check spam. Email from schedules can take a few minutes. |

## What you learned

- How to keep data fresh automatically.
- How to deliver reports and AI briefings on a schedule, so the right people see them.
