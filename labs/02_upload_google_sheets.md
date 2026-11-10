# Lab 2 · Meet the data and upload it

- **Time:** 20 minutes
- **Goal:** understand Summit Financial's customer service data, then turn its five spreadsheets
  into tables in Databricks.
- **You'll need:** Lab 1 finished (the `summit_financial` schema exists), and the Google Sheets
  link from your instructor.

---

## The story

You've just joined **Summit Financial**, a Texas bank with about **1,000 customers**. Its
**Customer Service** team answers calls, app messages, web chats, and branch visits, and handles
customer **complaints**. By law, the bank must resolve every complaint within **8 weeks
(56 days)**. Missing that deadline is called an **SLA breach**.

The VP of Customer Service has questions she wants answered every week:

- *"What's our **NPS** (customer satisfaction score), and which channel is dragging it down?"*
- *"Which open complaints are **critical**, and which are about to miss their deadline?"*
- *"How often do we solve a customer's problem **on the first contact**?"*
- *"What are customers actually **saying** when they complain?"*

The team keeps its data in **Google Sheets**. Today you'll get that data into Databricks, clean
it, and build AI that answers those questions.

> 🔒 All of this data is **made up** (synthetic). No real customers are involved, so explore freely.

---

## Part 1 · Meet the data (5 min)

There are five sheets. Read through them before you upload. You'll use every one of them today.
The example values in each table come from one real row of that sheet (exact dates depend on
when your instructor generated the data).

### How the sheets connect

Every sheet links back to a customer, using a shared ID column:

```text
customers ──< service_cases ──< interactions ──< nps_survey
   (customer_id)   (case_id)      (interaction_id)
                       │
                       └──< call_insights
```

Read `──<` as "one to many": one customer can have many cases; one case can have many
interactions (contacts). A survey is about one interaction, and a call insight summarizes one
complaint conversation.

### 1. `customers`: who the bank's customers are

About **1,000 customers**, one row each. (The raw sheet has 1,012 rows, because a few customers
were exported twice. You'll remove the duplicates in Lab 3.)

| Column | What it means | Example values |
|---|---|---|
| `customer_id` | Unique ID for the customer | `CUST-00043` |
| `full_name` | Customer's name | `Carlos Brown` |
| `email` | Customer's email (personal data: you'll protect it in Lab 9) | `carlos.brown43@example.com` |
| `segment` | Type of customer: **RETAIL** (everyday banking, about 75%), **PREMIER** (higher balances, about 20%), **WEALTH** (wealthiest, about 5%) | `RETAIL` |
| `age_band` | Age group | `18-24` … `65+` |
| `tenure_years` | How many years they've banked with Summit | `1` to `25` |
| `preferred_channel` | How they like to contact the bank | `CALL_CENTER`, `MOBILE`, `ONLINE`, `BRANCH` |
| `city` | Texas city they live in (a few are blank) | `Dallas`, `Denton`, `Houston` … |
| `onboard_date` | When they became a customer | `2007-08-04` |

### 2. `service_cases`: complaints and requests

About **3,000 cases** (3,020 rows, including 20 duplicates). A **case** is opened whenever a
customer has a problem (a **complaint**, about 70%) or asks for something (a **service
request**, about 30%).

| Column | What it means | Example values |
|---|---|---|
| `case_id` | Unique ID for the case | `CASE-002747` |
| `customer_id` | The customer who opened it (links to `customers`) | `CUST-00741` |
| `case_type` | Complaint or service request | `COMPLAINT`, `SERVICE_REQUEST` |
| `complaint_category` | What the complaint is about (blank for service requests) | `FEES_CHARGES`, `ACCOUNT_ACCESS`, `TRANSACTION_DISPUTE`, `SERVICE_QUALITY`, `FRAUD_SCAM`, `STATEMENT_ERROR` |
| `product` | The product involved | `CHECKING`, `SAVINGS`, `CREDIT_CARD`, `MORTGAGE`, `PERSONAL_LOAN` |
| `severity` | How serious it is | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `channel_opened` | Where the customer raised it | `CALL_CENTER`, `MOBILE`, `ONLINE`, `BRANCH` |
| `agent_team` | The team handling it | `RETAIL_OPS`, `PREMIER_DESK`, `WEALTH_DESK`, `SPECIALIST_TEAM` |
| `open_date` | When the case was opened | `2026-01-19` |
| `sla_due_date` | Deadline: `open_date` + 56 days | `2026-03-16` |
| `resolved_date` | When it was resolved. **Blank = still open** | blank (this case is still open) |
| `resolution_outcome` | How it ended (blank if still open) | `UPHELD` (customer was right), `PARTIALLY_UPHELD`, `NOT_UPHELD`, `WITHDRAWN` |

> 💡 A case is an **SLA breach** if it was resolved *after* its `sla_due_date`.

### 3. `interactions`: every time a customer got in touch

**4,000 contacts**: phone calls, app messages, web chats, and branch visits.

| Column | What it means | Example values |
|---|---|---|
| `interaction_id` | Unique ID for the contact | `INT-003959` |
| `customer_id` | Who got in touch (links to `customers`) | `CUST-00043` |
| `case_id` | The case it was about, if any. **Blank for most contacts:** routine questions are answered on the spot, so no case is opened | `CASE-001714` or blank |
| `channel` | How they got in touch | `CALL_CENTER` (most common), `MOBILE`, `ONLINE`, `BRANCH` |
| `reason` | Why they got in touch | `BALANCE_QUESTION`, `CARD_DISPUTE`, `FRAUD_REPORT`, `PAYMENT_ISSUE`, `COMPLAINT` … |
| `interaction_time` | Date and time of the contact | `2025-11-04 04:43:09` |
| `duration_minutes` | How long it took (the **handle time**) | `13.28` |
| `outcome` | What happened | `RESOLVED`, `TRANSFERRED`, `ESCALATED`, `CALLBACK_SCHEDULED`, `ABANDONED` (customer hung up) |
| `first_contact_resolved` | Was the problem solved in this first contact? (**first-contact resolution**, or FCR). Only ever `TRUE` when the outcome is `RESOLVED` | `TRUE`, `FALSE` |

> 💡 **Escalations.** When a contact is `ESCALATED`, a case is opened to track it, with two
> exceptions: **fraud reports** and **card disputes** go to the bank's fraud & disputes team,
> which tracks them in its own system (so `case_id` stays blank). And a few **complaints were never
> logged** as a case at all. Banks are required to record every complaint, so finding those is
> a real compliance check. Can you spot them later in the day?

### 4. `nps_survey`: what customers thought

**800 survey responses**, sent after a contact. Customers answer: *"How likely are you to
recommend Summit Financial, from 0 to 10?"*

| Column | What it means | Example values |
|---|---|---|
| `survey_id` | Unique ID for the response | `NPS-00012` |
| `customer_id` | Who answered (links to `customers`) | `CUST-00058` |
| `interaction_id` | The contact the survey was about (links to `interactions`) | `INT-000465` |
| `survey_date` | When they answered | `2026-01-16` |
| `score` | Their 0–10 answer. **9–10 = promoter**, **7–8 = passive**, **0–6 = detractor** | `8` |
| `channel` | The channel of that contact | `CALL_CENTER`, `MOBILE`, `ONLINE`, `BRANCH` |
| `comment` | What they wrote (often blank) | `"Okay service, nothing special."` |

> 💡 **NPS (Net Promoter Score)** = % of promoters minus % of detractors. It's a number from −100
> to +100, and it is **not** the average score. Remember this for Lab 7.

### 5. `call_insights`: AI summaries of complaint conversations

About **380 complaint conversations**, each already summarized by AI: what the customer said,
how they felt, and whether they might escalate. Despite the name, they cover every channel:
phone calls, app and web chats, and branch visits. (The table is called `call_insights` because
most started as calls.)

| Column | What it means | Example values |
|---|---|---|
| `insight_id` | Unique ID for the summary | `INS-00001` |
| `interaction_id` | The conversation that was summarized (links to `interactions`) | `INT-003959` |
| `case_id` | The complaint it relates to (links to `service_cases`) | `CASE-001714` |
| `customer_id` | The customer (links to `customers`) | `CUST-00043` |
| `call_summary` | Short summary of the conversation, ending with how it ended | `"Customer disputes a savings fee and asks for a refund. Resolved during the conversation."` |
| `sentiment` | How the customer felt by the end. Follows the outcome: escalated or abandoned conversations are mostly `NEGATIVE` | `NEGATIVE`, `NEUTRAL`, `POSITIVE` |
| `complaint_category` | What the complaint was about | `FEES_CHARGES`, `FRAUD_SCAM` … |
| `key_phrases` | Notable phrases from the conversation, separated by `;` | `refund; overdraft fee; charged twice` |
| `escalation_risk` | Might this customer escalate further, for example to a regulator? Only unhappy customers are flagged, mostly when the problem wasn't fixed | `TRUE`, `FALSE` |

### The data isn't perfect, on purpose

Real exported data is messy, and this is too:

- **Inconsistent spelling:** `severity` appears as `HIGH`, `High`, and `high`; `segment` as
  `RETAIL`, `Retail`, and `retail`.
- **Duplicate rows:** some customers and cases appear twice.
- **Blanks:** a few customers have no city.
- **Wrong types:** dates and TRUE/FALSE values may arrive as plain text.

You'll fix all of this in **Lab 3**, without writing code.

---

## Part 2 · Download the five sheets (5 min)

1. Open the Google Sheets link from your instructor.
2. Open the first sheet, **customers**.
3. Click **File → Download → Comma-separated values (.csv)**.

   ✅ **You should see:** a file called something like `customers - customers.csv` in your
   Downloads folder.

4. Repeat for the other four sheets: **service_cases**, **interactions**, **nps_survey**, and
   **call_insights**.

---

## Part 3 · Upload each file as a table (10 min)

Upload each file and give it a table name from this list:

| File | Table name |
|---|---|
| customers | `customers_raw` |
| service_cases | `service_cases_raw` |
| interactions | `interactions_raw` |
| nps_survey | `nps_survey` |
| call_insights | `call_insights` |

For **each** of the five files:

1. In Databricks, click **+ New** (top of the left sidebar), then **Add or upload data**.
2. Click **Create or modify table**.
3. Drag the CSV file onto the page, or click **browse** and choose it.
4. Wait for the preview to load.
5. At the top, set:
   - **Catalog:** `workspace`
   - **Schema:** `summit_financial`
   - **Table name:** the name from the list above (for example `customers_raw`)
6. Check the preview: the **column names** should be the ones from Part 1 (like `customer_id`
   and `segment`), not `_c0`, `_c1`. If you see `_c0`, open the advanced options and turn on
   **First row contains header**.
7. Click **Create table**.

   ✅ **You should see:** the new table's page, with its columns and a sample of rows.

> 💡 **Why "raw"?** Three tables end in `_raw` because they're exactly what came out of the
> spreadsheet, mess and all. In Lab 3 you'll build clean **gold** tables from them. Raw, then
> clean, is how real data teams work. (`nps_survey` and `call_insights` are already clean
> enough to use as they are.)

---

## Check your work

1. Open **Catalog → workspace → summit_financial**.

   ✅ **You should see five tables:** `call_insights`, `customers_raw`, `interactions_raw`,
   `nps_survey`, `service_cases_raw`.

2. **See the mess for yourself.** Open the **SQL Editor** and run:

   ```sql
   SELECT severity, count(*) AS cases
   FROM workspace.summit_financial.service_cases_raw
   GROUP BY severity
   ORDER BY severity;
   ```

   There are really only four severities. **How many different spellings do you see?**

## Troubleshooting

| Problem | What to do |
|---|---|
| Columns are named `_c0`, `_c1`… | The header row wasn't used. Re-upload, and turn on **First row contains header**. |
| "Table already exists" | You uploaded this one already. Choose **Overwrite**, or skip it. |
| The upload button is greyed out | Check that the catalog is `workspace` and the schema is `summit_financial`. |
| A column type looks wrong (for example, dates shown as text) | That's fine. Lab 3 fixes the types. |

## What you learned

- What Summit Financial's five datasets contain, and how they connect through shared IDs.
- The key business terms you'll use all day: complaint, SLA breach, NPS, first-contact resolution.
- How to bring a spreadsheet into Databricks as a table, and why teams keep a **raw** copy first.
