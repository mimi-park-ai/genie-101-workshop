# Lab 1 · Databricks 101

- **Time:** 30 minutes
- **Goal:** create your own free Databricks account, find your way around it, and make a place to store today's data.
- **You'll need:** a laptop with Chrome (or another modern browser), and an email address you can check right now.

---

## What is Databricks?

Databricks is a **data and AI platform**. Companies use it to keep all their data in one place,
clean it up, analyze it, and build AI on top of it, with security built in. Today you'll do the
work of a data engineer, a data analyst, and an AI developer, all in one tool.

Five words you'll hear all day:

| Word | What it means |
|---|---|
| **Workspace** | Your own Databricks environment, where your data and tools live |
| **Catalog → Schema → Table** | Folders for data. A *catalog* holds *schemas*, and a schema holds *tables* |
| **Unity Catalog** | The part of Databricks that organizes data and controls who can see what |
| **SQL warehouse** | The engine that runs your queries and dashboards |
| **Genie** | Databricks' AI that answers questions about your data in plain English |

---

## Part 1 · Sign up for Databricks Free Edition (10 min)

1. Open a new browser tab and go to **databricks.com/learn/free-edition**.
2. Click **Sign up**.
3. Choose how to sign in:
   - **Email:** type your email address and click **Continue**. Databricks emails you a
     one-time code. Type the code in.
   - **Google** or **Microsoft:** click the button and pick your account.
4. If asked, choose a region close to you, and accept the terms.
5. Wait about a minute while Databricks creates your workspace.

✅ **You should see:** the Databricks **Home** page, with a sidebar on the left.

> 💡 **Free Edition** is a free, personal Databricks account for learning. It's yours to keep
> after today, so you can keep practicing.

---

## Part 2 · Tour the workspace (15 min)

Everything you need is in the **left sidebar**. If you can only see icons, hover over the sidebar
or click the **☰** button at the top to expand it.

Open each of these in turn:

1. **Workspace.** This is where files and notebooks live. Click **Users**, then the folder
   with your email address. That's your personal folder.
2. **Catalog.** This is where all your data lives. Click the **`workspace`** catalog to expand it.
   You'll see a schema called **`default`**. Your data will go in a new schema next to it.
3. **SQL Editor.** This is where you write and run SQL. Try it:
   1. Click **SQL Editor**.
   2. Paste this into the editor:

      ```sql
      SELECT 'hello, Databricks' AS greeting
      ```

   3. Click **Run** (or press **Ctrl + Enter**, or **Cmd + Enter** on a Mac).

   ✅ **You should see:** a result table with one row: `hello, Databricks`.

   > 💡 The first query can take 10–20 seconds while the SQL warehouse starts up. After that
   > it's fast.

4. **Genie.** This is where you'll build an AI agent in Lab 5. Just look for now.
5. **Dashboards.** You'll build one in Lab 4.
6. **Jobs & Pipelines.** This is where scheduled work runs. You'll use it in Lab 8.

---

## Part 3 · Create your schema (5 min)

A **schema** is a folder for tables. You'll keep all of today's data in one called
`summit_financial`.

1. Open the **SQL Editor**.
2. Delete what's in the editor, then paste:

   ```sql
   CREATE SCHEMA IF NOT EXISTS workspace.summit_financial
   COMMENT 'Summit Financial customer service data for the Genie 101 workshop';
   ```

3. Click **Run**.
4. Open **Catalog**, then expand **workspace**. If you don't see the new schema, click the
   **refresh** icon at the top of the Catalog panel.

✅ **You should see:** `summit_financial` listed under the `workspace` catalog.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| The sign-up email hasn't arrived | Check your spam folder. Or go back and sign up with **Google** or **Microsoft** instead. |
| The query has been "running" for a long time | The warehouse is starting up. Wait up to a minute, then try again. |
| `CREATE SCHEMA` gives a permission error | Check you typed `workspace.summit_financial` exactly. `workspace` is the catalog name in Free Edition. |

## What you learned

- How to get a free Databricks account.
- Where data, files, and tools live in a workspace.
- How to run SQL, and how data is organized into catalogs, schemas, and tables.
