# Free Edition dry-run checklist

Run every lab on a **brand-new Databricks Free Edition account**, exactly as a student would, at
least a week before the workshop. Several features are new or in preview, and Free Edition
support for them was **not confirmed** when these labs were written (Nov 2026).

For each row, mark the result. Anything ❌ becomes an instructor demo (on a full workspace) or
uses the listed fallback.

| Lab | Check | Status at writing | Result | Fallback if it fails |
|---|---|---|---|---|
| 1 | Free Edition sign-up; `CREATE SCHEMA workspace.summit_financial` works | Confirmed | | — |
| 2 | **Add or upload data** creates tables from CSV in `summit_financial` | Confirmed | | Upload to a volume, then `read_files` |
| 3 | **Visual Data Prep** (Lakeflow Designer) is in the sidebar / + New menu | Listed for Free Edition | | `answer_key/03_gold_tables.sql` |
| 3 | Designer steps used (Source, Unique, Prepare: trim / text case / cast / formula, Join, Output) | Verified on a full workspace (Nov 2026); Free Edition unconfirmed | | SQL fallback |
| 3 | Row counts match: 1,000 / 3,000 / 4,000 | — | | Compare with the SQL fallback |
| 3 | Import `answer_key/summit_gold.designer.ipynb` (the finished flow, catalog `workspace`), open it in Designer without an "out of date" warning, and Run | The same flow ran correctly on a full workspace; the catalog-swapped copy is untested in the Designer UI | | If a step says its code is out of date, click **Regenerate**: the step settings are already correct |
| 4 | AI/BI dashboard; **Genie Code** AI authoring prompts work | Dashboards confirmed; AI authoring depends on region/partner-AI settings | | Build the charts by hand |
| 4 | **Ask Genie** on a published dashboard | Listed | | Skip 4.4 |
| 5 | Create a **Genie Agent** with 4 tables, instructions, sample questions | Listed | | — |
| 5 | **Benchmarks**: add questions with reference SQL; Run all | In-product benchmarks GA; Free Edition unconfirmed | | Ask the 8 questions manually; compare with `answer_key/benchmarks.md` |
| 6 | **AI generate** table/column descriptions | Unverified | | Type descriptions by hand |
| 6 | **Domains** (Catalog → Discover), certify assets | Domains GA; Free Edition unconfirmed | | Demo only |
| 6 | **Pages** (business term definitions) | Beta; Free Edition unconfirmed | | Put the definitions in the agent's Instructions instead |
| 7 | `answer_key/07_metric_views.sql` runs; `SELECT MEASURE(nps) FROM cs_nps_metrics` returns **34** | Metric views GA; Free Edition unconfirmed | | Change YAML `version: 1.1` to `0.1` and remove display_name/synonyms |
| 7 | Metric views can be added to the Genie Agent | Unverified | | — |
| 7 | Before/after: questions 1–4 improve | — | | If "before" is already right, discuss the SQL Genie used |
| 8 | Schedule a visual data prep | Jobs/pipelines listed; 5 concurrent tasks per account | | Schedule the SQL fallback as a job instead |
| 8 | Dashboard schedule + email subscription | Unconfirmed | | Demo only |
| 8 | **Genie scheduled task** + Run now | Public Preview; Free Edition unconfirmed | | Demo only |
| 9 | Column mask and row filter (`answer_key/09_governance.sql`) apply, and Genie answers change | Mask + filter verified on a full workspace; Visual Data Prep writes regular managed tables, so they apply | | Rebuild the table with the SQL fallback |
| 9 | Agent **Monitoring** tab and **Share** dialog | Unverified | | Demo only |
| 10 | **AI Gateway** on a Databricks-hosted chat endpoint: usage tracking, rate limit, PII guardrail | Unconfirmed for Free Edition | | Demo on a full workspace |
| 10 | Rate limit and guardrail visibly block requests in Playground | — | | Demo only |
| 11 | Playground: add a **Genie MCP** tool and call the agent | Managed MCP Public Preview; Free Edition unconfirmed | | Demo only |
| 11 | Agent's MCP URL; connect from an external assistant with OAuth | Unconfirmed | | Demo only |

**Also check**

- How long sign-up takes, start to finish (budgeted: 10 minutes).
- Whether the fair-use quota holds up through a full day of labs on one account.
- The exact UI wording and menu paths, and update the labs to match. Menus change often, and the
  labs describe the paths as of Nov 2026.

**Sources for the "status at writing" column:** Databricks Free Edition limitations page (updated
Oct 18, 2026), Lakeflow Designer October 2026 roundup, AI/BI 2026 release notes, metric views docs,
AI Gateway docs, and managed MCP docs.
