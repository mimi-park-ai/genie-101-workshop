# Instructor guide: Genie 101

For facilitators. Not for students.

## Who it's for

University students with no Databricks experience. Data or SQL experience helps but isn't
required: every SQL step is copy-and-paste, and every lab has an answer key.

## Timing (10:00 AM – 4:00 PM example)

| Time | Block | Notes |
|---|---|---|
| 10:00 – 10:30 | Lab 1 · Databricks 101 | Sign-up needs email verification. Start the sign-up first, then explain the platform while workspaces are created. |
| 10:30 – 10:50 | Lab 2 · Upload Google Sheets | Share the Google Sheets link (view-only) in the room. |
| 10:50 – 11:30 | Lab 3 · Visual Data Prep | The longest hands-on lab. Point slower students to the SQL fallback at the 25-minute mark. |
| 11:30 – 12:05 | Lab 4 · Dashboard | |
| 12:05 – 12:50 | *Lunch* | |
| 12:50 – 1:25 | Lab 5 · Genie Agent | Make sure everyone records a "before" benchmark score. Lab 7 depends on it. |
| 1:25 – 1:50 | Lab 6 · Semantic layer | |
| 1:50 – 2:25 | Lab 7 · Metric views before/after | The "aha" moment. Ask a few students to read out their before/after scores. |
| 2:25 – 2:35 | *Break* | |
| 2:35 – 2:55 | Lab 8 · Scheduling | |
| 2:55 – 3:20 | Lab 9 · Agent governance | |
| 3:20 – 3:40 | Lab 10 · AI Gateway | |
| 3:40 – 4:00 | Lab 11 · MCP + wrap-up | |

**Shorter versions**

- **Half day (about 3.5 hours):** Labs 1–7. Demo Labs 8–11 from the front.
- **10 AM – 3 PM:** Labs 1–9, with Labs 10–11 as instructor demos.

## Before the day

1. **Do the [Free Edition dry run](FREE_EDITION_DRY_RUN.md)** on a brand-new Free Edition account,
   at least a week ahead. Anything that fails there becomes an instructor demo.
2. **Regenerate the data** for the workshop date, so "this month" questions return results:

   ```bash
   python3 scripts/generate_data.py --as-of <workshop date, YYYY-MM-DD>
   ```

3. **Put the data in Google Sheets.** Create one Google Sheet per CSV in `data/`
   (**File → Import → Upload → Replace spreadsheet**), named `customers`, `service_cases`,
   `interactions`, `nps_survey`, and `call_insights`. Put them in one Drive folder, share it
   (view only), and make a short link or QR code for the room.
   Note: Google trims stray spaces and drops leading zeros from times on import. Both are fine:
   the labs still have messy values to clean, and Databricks parses the times correctly.
4. **Share the student lab guides.** Students follow `labs/*.md`. Share them as they are, or publish
   each one as a Google Doc (Drive converts Markdown on import), together with
   `answer_key/summit_gold.designer.ipynb` (the finished Lab 3 flow, for students who get stuck).
   If you edit a lab, edit the Markdown and re-publish, so the repo and the Docs stay the same.
5. **Check the room Wi-Fi** handles 30+ people signing in at once.
6. **Helpers:** about one per 15 students. Sign-up and Lab 3 are where people get stuck.

## Master deck

`deck/build_deck.py` generates a 32-slide Google Slides master deck: the opening story and data map,
a **concept** slide and a **walkthrough** slide for each lab (each linking to that lab's guide), the
Lab 7 before/after proof slide, and a recap. Every slide has speaker notes. See the top of the script
for how to run it. It creates a new presentation each time.

## A reference copy for demos

Before the workshop, complete all the labs yourself in a workspace you control. You then have a
finished copy (gold tables, metric views, and the Complaint-Triage Agent with its benchmarks) to demo
from your own screen, and to compare against students' results.

## Key teaching points

- **Lab 3:** messy data in means messy AI answers out. The gold layer is the foundation for
  everything after it.
- **Lab 5 → 7:** the AI didn't get smarter between the two benchmark runs. It got **context**.
  The semantic layer and metric views are the difference.
- **Lab 9:** the rules live on the *data*, not the agent, so they apply in every tool.

## Common problems

| Problem | Fix |
|---|---|
| Sign-up email doesn't arrive | Check spam; or sign up with Google or Microsoft instead. |
| Upload infers the wrong column types | Fine: the Lab 3 steps and the SQL fallback convert types. |
| Visual Data Prep missing or failing | Have the student import the finished flow, `answer_key/summit_gold.designer.ipynb` (also in the class Drive folder), or run [`answer_key/03_gold_tables.sql`](../answer_key/03_gold_tables.sql) in the SQL Editor. |
| "Quota exceeded" / compute stops | Free Edition fair-use limit. Wait for the reset; pair the student with a neighbor meanwhile. |
| AI dashboard authoring not visible | Build the charts by hand from the prompts in Lab 4. |
| Benchmarks "before" score is already 8/8 | Fine. Ask what the agent *assumed* NPS meant, and show the SQL. |
| Scheduled runs queue or fail | Free Edition caps concurrent tasks. Stagger the schedule times. |
