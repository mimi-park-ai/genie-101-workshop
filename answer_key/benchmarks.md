# Benchmark questions and correct answers

Used in **Lab 5** (baseline, "before") and **Lab 7** (after metric views). Add each question to
your Genie agent's **Benchmarks** with its reference SQL, then run them.

These counts come from the generated data and stay the same whatever `--as-of` date you
generate with. If you change `generate_data.py` itself, recompute them.

| # | Question | Correct answer | Common wrong answer (before) |
|---|---|---|---|
| 1 | What is our NPS? | **34** | ~7.7 (averaged the 0–10 score) |
| 2 | What is NPS by channel? | Branch **38**, Call center **30**, Mobile **39**, Online **35** | Average score per channel |
| 3 | How many complaints do we have? | **2,108** | 3,000 (counted every case, including service requests) |
| 4 | What is our SLA breach rate? | **11.5%** of resolved complaints | Includes service requests, or counts open cases |
| 5 | How many open critical complaints are there? | **20** | Usually right on gold tables |
| 6 | What is our first-contact resolution rate? | **68.0%** | Usually right |
| 7 | Which complaint category has the most complaints? | **FEES_CHARGES** (373) | Usually right |
| 8 | Average days to resolve a complaint? | **31.1 days** | Includes service requests |

Questions 1–4 are the ones a semantic layer should fix. Questions 5–8 are the "control group":
they should be right before *and* after.

## Reference SQL

```sql
-- 1. NPS = % promoters (9–10) minus % detractors (0–6)
SELECT round(100 * (count_if(score >= 9) - count_if(score <= 6)) / count(*)) AS nps
FROM workspace.summit_financial.nps_survey;

-- 2. NPS by channel
SELECT channel, round(100 * (count_if(score >= 9) - count_if(score <= 6)) / count(*)) AS nps
FROM workspace.summit_financial.nps_survey
GROUP BY channel ORDER BY channel;

-- 3. Complaints
SELECT count(*) FROM workspace.summit_financial.gold_cases WHERE is_complaint;

-- 4. SLA breach rate, over resolved complaints only
SELECT round(100 * count_if(is_sla_breach) / count(*), 1) AS sla_breach_pct
FROM workspace.summit_financial.gold_cases
WHERE is_complaint AND NOT is_open;

-- 5. Open critical complaints
SELECT count(*) FROM workspace.summit_financial.gold_cases
WHERE is_complaint AND is_open AND severity = 'CRITICAL';

-- 6. First-contact resolution rate
SELECT round(100 * avg(CAST(first_contact_resolved AS INT)), 1) AS fcr_pct
FROM workspace.summit_financial.gold_interactions;

-- 7. Top complaint category
SELECT complaint_category, count(*) AS complaints
FROM workspace.summit_financial.gold_cases
WHERE is_complaint
GROUP BY complaint_category ORDER BY complaints DESC LIMIT 1;

-- 8. Average days to resolve a complaint
SELECT round(avg(days_to_resolve), 1)
FROM workspace.summit_financial.gold_cases
WHERE is_complaint AND NOT is_open;
```

## Scorecard (fill in during the labs)

| # | Before (Lab 5) ✅/❌ | After (Lab 7) ✅/❌ |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
| **Score** | __ / 8 | __ / 8 |
