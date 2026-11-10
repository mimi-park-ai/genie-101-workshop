# Lab 11 · MCP: use your agent from other AI tools

- **Time:** 20 minutes
- **Goal:** let other AI assistants use your Complaint-Triage Agent as a tool.
- **You'll need:** Lab 5 finished (your agent exists). Labs 6 and 7 make it work better.

---

## What's MCP?

**MCP (Model Context Protocol)** is an open standard for connecting AI assistants to tools and
data. Think of it as a universal plug. Databricks makes your Genie agents, functions, and data
available as **MCP servers**, so other assistants, such as Claude, ChatGPT, or Cursor, can use
them, with your permissions and governance still applied.

---

## Part 1 · Use your agent as a tool in Playground (10 min)

1. In the left sidebar, click **Playground**.
2. At the top, pick a chat model.
3. Click **Tools** (or **Add tools**), then **MCP servers**, then **Genie**.
4. Choose your **Complaint-Triage Agent**, and click **Add** (or **Save**).
5. In the chat box, ask:

   ```text
   Using the complaint tool, which open critical complaints are due soonest,
   and what did those customers say?
   ```

6. When the answer appears, expand the **tool call** to see what happened.

✅ **You should see:** the chat model asked your Genie agent, Genie ran the SQL on your data, and
the chat model wrote the final answer.

> 💡 The chat model knew nothing about your tables. It asked your agent, which already knows your
> data and your business definitions from Labs 6 and 7. You built the context once, and now any
> AI tool can use it.

---

## Part 2 · Find your agent's MCP address (5 min)

Every Genie agent has an MCP address (a URL) that other assistants can connect to.

1. Open your **Complaint-Triage Agent**.
2. Look for **MCP**, **Connect**, or **Share → MCP**, and copy the URL.

   It looks like this:

   ```text
   https://<your-workspace>.cloud.databricks.com/api/2.0/mcp/genie/<agent-id>
   ```

> 💡 When an assistant connects, you sign in with **your** Databricks account. So the assistant
> can only see what **you** are allowed to see (remember Lab 9).

---

## Part 3 · Optional: connect an assistant outside Databricks (5 min)

If you use **Claude**, **Cursor**, or another AI assistant that supports remote MCP servers:

1. In that assistant's settings, find **Connectors**, **Integrations**, or **MCP servers**.
2. Add a **custom** connector, and paste the URL from Part 2.
3. Sign in with your Databricks account when asked.
4. Ask it: *"Which open complaints are highest priority right now?"*

---

## Troubleshooting

| Problem | What to do |
|---|---|
| I don't see **MCP servers** under Tools | This feature may not be in your account yet. Follow your instructor's demo. |
| My agent isn't in the list | Check the agent is saved, and that you're looking under **Genie**. |
| The external assistant can't connect | Check the URL is complete, and that you signed in with the same Databricks account. |

## What you learned

- What MCP is, and why open standards matter for AI.
- How to make your agent available to other AI tools, with governance still applied.

---

## 🎉 You did it

Today you went from spreadsheets to a governed AI agent:

1. Loaded raw data, and cleaned it into trusted **gold** tables.
2. Built a **dashboard** and an **AI agent** on top.
3. Taught the agent your business with a **semantic layer** and **metric views**, and proved it
   with benchmarks.
4. Put it on a **schedule**, **governed** it, controlled AI use with the **AI Gateway**, and
   opened it to other tools with **MCP**.

Your Free Edition account is yours to keep. Keep building!
