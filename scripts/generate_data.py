"""Generate the Summit Financial 101 dataset as CSVs (one per Google Sheet).

Pure standard-library Python: no Spark, no Databricks needed.

    python scripts/generate_data.py            # writes data/*.csv
    python scripts/generate_data.py --as-of 2026-12-03   # anchor dates to the workshop day
    python scripts/generate_data.py --clean    # same data, without the deliberate mess

The raw data is intentionally a little messy (inconsistent casing, stray spaces, blank
values, duplicate rows) so that Lab 3 (Visual Data Prep) has real cleanup to do. Sizes are
small on purpose: every student loads their own copy into Databricks Free Edition.

Calibrated to the full CSO workshop: segment mix 75/20/5, NPS ~35, SLA breach ~13% of resolved
cases, 8-week (56-day) complaint SLA. Contact outcomes depend on the contact reason, and
first-contact resolution (~68%) is only ever true for contacts resolved there and then.
"""
from __future__ import annotations

import argparse
import csv
import os
import random
from datetime import date, datetime, timedelta

SEED = 42
N_CUSTOMERS = 1000
N_CASES = 3000
N_INTERACTIONS = 4000
N_SURVEYS = 800
N_INSIGHTS = 600
SLA_DAYS = 56
AS_OF = date.today()  # overridden by --as-of; all dates are relative to this

FIRST = ["James", "Mary", "John", "Priya", "Wei", "Amara", "David", "Sophie", "Mohammed",
         "Olivia", "Liam", "Aisha", "George", "Emily", "Raj", "Grace", "Carlos", "Mei"]
LAST = ["Smith", "Jones", "Patel", "Brown", "Wilson", "Khan", "Taylor", "Garcia", "Evans",
        "Okafor", "Murphy", "Singh", "Clarke", "Nguyen", "Ahmed", "Lopez", "Kim", "Walsh"]
CITIES = ["Dallas", "Denton", "Fort Worth", "Austin", "Houston", "San Antonio", "Plano",
          "Arlington", "Frisco", "El Paso"]
SEGMENTS = [("RETAIL", 75), ("PREMIER", 20), ("WEALTH", 5)]
AGE_BANDS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
CHANNELS = ["CALL_CENTER", "MOBILE", "ONLINE", "BRANCH"]
COMPLAINT_CATS = ["FEES_CHARGES", "ACCOUNT_ACCESS", "TRANSACTION_DISPUTE", "SERVICE_QUALITY",
                  "FRAUD_SCAM", "STATEMENT_ERROR"]
PRODUCTS = ["CREDIT_CARD", "CHECKING", "SAVINGS", "MORTGAGE", "PERSONAL_LOAN"]
SEVERITY = [("LOW", 35), ("MEDIUM", 40), ("HIGH", 20), ("CRITICAL", 5)]
TEAMS = ["RETAIL_OPS", "PREMIER_DESK", "WEALTH_DESK", "SPECIALIST_TEAM"]
OUTCOMES = ["UPHELD", "PARTIALLY_UPHELD", "NOT_UPHELD", "WITHDRAWN"]
REASONS = ["BALANCE_QUESTION", "CARD_DISPUTE", "LOAN_QUESTION", "PAYMENT_ISSUE", "FRAUD_REPORT",
           "ACCOUNT_UPDATE", "COMPLAINT", "TECH_SUPPORT"]
CALL_OUTCOMES = [("RESOLVED", 62), ("TRANSFERRED", 14), ("ESCALATED", 10),
                 ("CALLBACK_SCHEDULED", 8), ("ABANDONED", 6)]
# How each kind of contact usually ends. Simple questions are resolved on the spot; complaints,
# fraud reports and card disputes are escalated far more often.
_SIMPLE = [("RESOLVED", 92), ("TRANSFERRED", 4), ("CALLBACK_SCHEDULED", 2), ("ABANDONED", 2)]
_MEDIUM = [("RESOLVED", 80), ("TRANSFERRED", 8), ("CALLBACK_SCHEDULED", 5), ("ESCALATED", 3), ("ABANDONED", 4)]
_SERIOUS = [("RESOLVED", 55), ("ESCALATED", 25), ("TRANSFERRED", 12), ("CALLBACK_SCHEDULED", 4), ("ABANDONED", 4)]
OUTCOME_BY_REASON = {
    "BALANCE_QUESTION": _SIMPLE, "ACCOUNT_UPDATE": _SIMPLE,
    "TECH_SUPPORT": _MEDIUM, "LOAN_QUESTION": _MEDIUM, "PAYMENT_ISSUE": _MEDIUM,
    "FRAUD_REPORT": _SERIOUS, "CARD_DISPUTE": _SERIOUS,
    "COMPLAINT": [("RESOLVED", 45), ("ESCALATED", 30), ("TRANSFERRED", 12), ("CALLBACK_SCHEDULED", 8), ("ABANDONED", 5)],
}
# How customers feel by the end of a complaint conversation, and how likely an unhappy customer
# is to escalate further (for example, to a regulator).
SENTIMENT_BY_OUTCOME = {
    "RESOLVED": [("NEGATIVE", 25), ("NEUTRAL", 50), ("POSITIVE", 25)],
    "ESCALATED": [("NEGATIVE", 75), ("NEUTRAL", 22), ("POSITIVE", 3)],
    "TRANSFERRED": [("NEGATIVE", 55), ("NEUTRAL", 40), ("POSITIVE", 5)],
    "CALLBACK_SCHEDULED": [("NEGATIVE", 50), ("NEUTRAL", 45), ("POSITIVE", 5)],
    "ABANDONED": [("NEGATIVE", 85), ("NEUTRAL", 15)],
}
ESCALATION_RISK_BY_OUTCOME = {"RESOLVED": 0.05, "ESCALATED": 0.5, "TRANSFERRED": 0.25,
                              "CALLBACK_SCHEDULED": 0.25, "ABANDONED": 0.4}
VERBATIM = {
    "PROMOTER": ["Very helpful and quick to resolve.", "Sorted my issue the first time.",
                 "The agent was polite and efficient.", "Really impressed with how fast this was handled."],
    "PASSIVE": ["It was fine, took a little while.", "Resolved eventually, average experience.",
                "Okay service, nothing special."],
    "DETRACTOR": ["Had to call three times, very frustrating.", "Still not resolved, poor experience.",
                  "Long wait and the fee was never refunded.", "Nobody followed up as promised."],
}
SUMMARY = {
    "FEES_CHARGES": "Customer disputes a {p} fee and asks for a refund.",
    "ACCOUNT_ACCESS": "Customer is locked out of online banking for their {p} account.",
    "TRANSACTION_DISPUTE": "Customer does not recognize a transaction on their {p}.",
    "SERVICE_QUALITY": "Customer complains about wait times and repeat calls about their {p}.",
    "FRAUD_SCAM": "Customer reports suspected fraud on their {p} and wants it blocked.",
    "STATEMENT_ERROR": "Customer says their {p} statement shows an incorrect balance.",
}
OUTCOME_SENTENCE = {
    "RESOLVED": "Resolved during the conversation.",
    "ESCALATED": "Escalated to a specialist team.",
    "TRANSFERRED": "Transferred to another team.",
    "CALLBACK_SCHEDULED": "A callback was scheduled.",
    "ABANDONED": "The customer hung up before it was resolved.",
}
PHRASES = {
    "FEES_CHARGES": "refund; overdraft fee; charged twice",
    "ACCOUNT_ACCESS": "locked out; password reset; app login",
    "TRANSACTION_DISPUTE": "unknown charge; chargeback; merchant",
    "SERVICE_QUALITY": "long wait; called again; no follow-up",
    "FRAUD_SCAM": "fraud; block card; unauthorized",
    "STATEMENT_ERROR": "wrong balance; statement; correction",
}


def weighted(rng: random.Random, pairs):
    vals, weights = zip(*pairs)
    return rng.choices(vals, weights=weights, k=1)[0]


def messy_case(rng: random.Random, value: str, clean: bool) -> str:
    """Return the value with occasional inconsistent casing / stray spaces (raw-data realism)."""
    if clean or value == "":
        return value
    r = rng.random()
    if r < 0.08:
        return value.lower()
    if r < 0.14:
        return value.title()
    if r < 0.18:
        return f" {value} "
    return value


def write_csv(path: str, header: list[str], rows: list[list]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {os.path.basename(path):24s} {len(rows):>6,} rows")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", action="store_true", help="skip the deliberate messiness")
    ap.add_argument("--as-of", help="last date in the data, YYYY-MM-DD (default: today). Use the workshop date.")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    global AS_OF
    if args.as_of:
        AS_OF = date.fromisoformat(args.as_of)
    start = AS_OF - timedelta(days=365)
    rng = random.Random(SEED)
    clean = args.clean

    # ---- customers ----
    customers, seg_of = [], {}
    for i in range(1, N_CUSTOMERS + 1):
        cid = f"CUST-{i:05d}"
        first, last = rng.choice(FIRST), rng.choice(LAST)
        seg = weighted(rng, SEGMENTS)
        seg_of[cid] = seg
        tenure = rng.randint(1, 25)
        onboard = AS_OF - timedelta(days=tenure * 365 + rng.randint(0, 364))
        city = "" if (not clean and rng.random() < 0.03) else rng.choice(CITIES)
        customers.append([cid, f"{first} {last}", f"{first}.{last}{i}@example.com".lower(),
                          messy_case(rng, seg, clean), rng.choice(AGE_BANDS), tenure,
                          rng.choice(CHANNELS), city, onboard.isoformat()])
    if not clean:  # a few exact duplicate rows, as if exported twice
        customers += [list(r) for r in rng.sample(customers, 12)]
    write_csv(os.path.join(out, "customers.csv"),
              ["customer_id", "full_name", "email", "segment", "age_band", "tenure_years",
               "preferred_channel", "city", "onboard_date"], customers)
    cust_ids = list(seg_of)

    # ---- service_cases ----
    cases, case_meta = [], {}
    for i in range(1, N_CASES + 1):
        case_id = f"CASE-{i:06d}"
        cid = rng.choice(cust_ids)
        ctype = weighted(rng, [("COMPLAINT", 70), ("SERVICE_REQUEST", 30)])
        cat = rng.choice(COMPLAINT_CATS) if ctype == "COMPLAINT" else ""
        product = rng.choice(PRODUCTS)
        sev = weighted(rng, SEVERITY)
        opened = start + timedelta(days=rng.randint(0, 360))
        due = opened + timedelta(days=SLA_DAYS)
        resolved_on, outcome = "", ""
        if rng.random() < 0.85 and opened < AS_OF - timedelta(days=5):
            if rng.random() < 0.13:  # breached: resolved after the SLA due date
                rdate = due + timedelta(days=rng.randint(1, 20))
            else:
                rdate = opened + timedelta(days=rng.randint(1, SLA_DAYS - 1))
            if rdate <= AS_OF:
                resolved_on, outcome = rdate.isoformat(), rng.choice(OUTCOMES)
        case_meta[case_id] = (cid, cat, product)
        cases.append([case_id, cid, ctype, cat, product, messy_case(rng, sev, clean),
                      rng.choice(CHANNELS), rng.choice(TEAMS), opened.isoformat(),
                      due.isoformat(), resolved_on, outcome])
    if not clean:
        cases += [list(r) for r in rng.sample(cases, 20)]
    write_csv(os.path.join(out, "service_cases.csv"),
              ["case_id", "customer_id", "case_type", "complaint_category", "product",
               "severity", "channel_opened", "agent_team", "open_date", "sla_due_date",
               "resolved_date", "resolution_outcome"], cases)
    complaint_ids = [k for k, v in case_meta.items() if v[1]]

    # ---- interactions ----
    # The main rng draws below are kept in their original order, so customers, cases, surveys and
    # call insights are identical to earlier versions. Outcome, first-contact resolution and
    # escalation case links come from rng_outcome, so they stay consistent with each other.
    rng_outcome = random.Random(SEED + 1)
    service_request_ids = [k for k, v in case_meta.items() if not v[1]]
    sr_by_customer: dict[str, list[str]] = {}
    for k in service_request_ids:
        sr_by_customer.setdefault(case_meta[k][0], []).append(k)
    interactions = []
    for i in range(1, N_INTERACTIONS + 1):
        iid = f"INT-{i:06d}"
        reason = rng.choice(REASONS)
        case_id = rng.choice(complaint_ids) if reason == "COMPLAINT" and rng.random() < 0.8 else ""
        cid = case_meta[case_id][0] if case_id else rng.choice(cust_ids)
        ts = datetime.combine(start, datetime.min.time()) + timedelta(days=rng.randint(0, 364), seconds=rng.randint(0, 86399))
        channel = weighted(rng, [("CALL_CENTER", 45), ("MOBILE", 22), ("ONLINE", 20), ("BRANCH", 13)])
        duration = round(rng.lognormvariate(1.74, 0.5), 2)
        rng.random()  # retired draw (old independent first-contact flag), kept for stable output
        channel_raw = messy_case(rng, channel, clean)
        weighted(rng, CALL_OUTCOMES)  # retired draw (old independent outcome), kept for stable output

        # Outcome depends on why the customer got in touch.
        outcome = weighted(rng_outcome, OUTCOME_BY_REASON[reason])
        # Only a contact resolved there and then counts as resolved on first contact
        # (a few "resolved" contacts were repeat contacts about the same issue).
        fcr = outcome == "RESOLVED" and rng_outcome.random() < 0.95
        # Escalations get a (service request) case, except fraud and card disputes, which the
        # fraud & disputes team tracks in its own system, and complaints that were never logged
        # (the deliberate "unlogged complaint" gap).
        if outcome == "ESCALATED" and not case_id and reason not in ("FRAUD_REPORT", "CARD_DISPUTE", "COMPLAINT"):
            own = sr_by_customer.get(cid)
            if own:
                case_id = rng_outcome.choice(own)
            else:
                case_id = rng_outcome.choice(service_request_ids)
                cid = case_meta[case_id][0]
        interactions.append([iid, cid, case_id, channel_raw, reason,
                             ts.strftime("%Y-%m-%d %H:%M:%S"), duration,
                             outcome, "TRUE" if fcr else "FALSE"])
    write_csv(os.path.join(out, "interactions.csv"),
              ["interaction_id", "customer_id", "case_id", "channel", "reason", "interaction_time",
               "duration_minutes", "outcome", "first_contact_resolved"], interactions)

    # ---- nps_survey ----
    surveys = []
    for i, row in enumerate(rng.sample(interactions, N_SURVEYS), start=1):
        cat = weighted(rng, [("PROMOTER", 55), ("PASSIVE", 25), ("DETRACTOR", 20)])
        score = rng.randint(9, 10) if cat == "PROMOTER" else rng.randint(7, 8) if cat == "PASSIVE" else rng.randint(0, 6)
        sdate = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S").date() + timedelta(days=rng.randint(1, 7))
        verb = "" if rng.random() < 0.25 else rng.choice(VERBATIM[cat])
        surveys.append([f"NPS-{i:05d}", row[1], row[0], min(sdate, AS_OF).isoformat(), score,
                        row[3].strip().upper(), verb])
    write_csv(os.path.join(out, "nps_survey.csv"),
              ["survey_id", "customer_id", "interaction_id", "survey_date", "score",
               "channel", "comment"], surveys)

    # ---- call_insights (pre-computed AI summaries of complaint conversations) ----
    # Covers complaint contacts on any channel (calls, app and web chats, branch visits).
    # Sentiment and escalation risk follow how the conversation ended.
    call_rows = [r for r in interactions if r[2] and r[4] == "COMPLAINT"]  # complaint contacts linked to a case
    insights = []
    for i, row in enumerate(rng.sample(call_rows, min(N_INSIGHTS, len(call_rows))), start=1):
        cid, cat, product = case_meta[row[2]]
        outcome = row[7]
        sentiment = weighted(rng, SENTIMENT_BY_OUTCOME[outcome])
        # Only an unhappy customer is an escalation risk; much more likely if the problem wasn't fixed.
        at_risk = sentiment == "NEGATIVE" and rng.random() < ESCALATION_RISK_BY_OUTCOME[outcome]
        insights.append([f"INS-{i:05d}", row[0], row[2], cid,
                         SUMMARY[cat].format(p=product.replace("_", " ").lower()) + " " + OUTCOME_SENTENCE[outcome],
                         sentiment, cat, PHRASES[cat], "TRUE" if at_risk else "FALSE"])
    write_csv(os.path.join(out, "call_insights.csv"),
              ["insight_id", "interaction_id", "case_id", "customer_id", "call_summary",
               "sentiment", "complaint_category", "key_phrases", "escalation_risk"], insights)

    print(f"Done -> {out}  (data ends {AS_OF.isoformat()})")


if __name__ == "__main__":
    main()
