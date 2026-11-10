# Lab 10 · AI Gateway

- **Time:** 20 minutes
- **Goal:** put guardrails on how AI models are used: limit how often they can be called, block
sensitive information, and track usage.
- **You'll need:** Lab 1 finished.

---

## Why companies need this

Every AI feature you've used today talks to an AI model behind the scenes. Companies have to
control that:

- **Cost:** AI is paid for per use, and one runaway app can run up a big bill.
- **Safety:** people sometimes paste things into AI they shouldn't, such as customer data.
- **Visibility:** leaders need to know who is using AI, and how much.

**AI Gateway** is the control point between your users and the AI models.

---

## Part 1 · Open a model's gateway settings (5 min)

1. In the left sidebar, click **Serving**.
2. Find a **Databricks-hosted chat model**: any endpoint whose name starts with `databricks-`
   and is a chat or instruct model. Click it.
3. Find the **AI Gateway** section and click **Edit AI Gateway** (or **Edit**).

✅ **You should see:** settings for usage tracking, rate limits, and guardrails.

---

## Part 2 · Turn on three controls (5 min)

Set these, then click **Save**:

| Control | Set it to | Why companies use it |
|---|---|---|
| **Usage tracking** | **On** | See who used how much, for cost and capacity planning |
| **Rate limit** | **2 queries per minute, per user** (deliberately low, for the test) | Stop one person or app from running up the bill |
| **Guardrails** | Block **personal information (PII)** in the **input** | Stop customer data being pasted into AI |

---

## Part 3 · Test them (10 min)

1. In the left sidebar, click **Playground**.
2. At the top, pick the **same model** you just configured.
3. **Test the rate limit:** send three short messages quickly, one after another (for example
   "hi", "hi again", "and again").

   ✅ **You should see:** the third message blocked with a rate-limit message.

4. **Test the guardrail:** wait one minute, then send:

   ```text
   Write a letter to John Smith, SSN 123-45-6789, about his overdue loan.
   ```

   ✅ **You should see:** the request blocked because it contains personal information.

5. **Check usage:** go back to the model's page under **Serving**, and look at the usage
   information for your requests.

6. **Undo the test limit:** edit the AI Gateway again, and turn the rate limit **off** (or raise
   it to something sensible like 60 per minute). Click **Save**.

> 💡 **Budgets.** Companies also set **AI budgets**: for example, alert at 80% of the monthly AI
> spend and block at 100%. That needs account-admin access, which Free Edition doesn't have, so
> your instructor will show you instead.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| I can't find **AI Gateway** or **Edit** | This feature may not be available in your account. Follow along with your instructor's demo. |
| The rate limit didn't block anything | Send the messages faster, or set the limit to **1** per minute. |
| The PII message wasn't blocked | Check the guardrail is on for the **input** (not just the output), and that you saved. |

## What you learned

- Why companies govern how AI models are used.
- How rate limits, guardrails, and usage tracking work.
