"""Build the Genie 101 master deck as a Google Slides presentation.

Editorial design (no corporate template): oat canvas, ink text, Databricks Lava accents,
Fraunces headings, DM Sans body, line icons, a few hero photos, speaker notes on every slide.

    python3 deck/build_deck.py                 # creates a new presentation, prints its URL
    python3 deck/build_deck.py --title "..."   # custom title

Auth: needs a Google OAuth access token with the Slides scope. By default it runs
`gcloud auth print-access-token`; or set GOOGLE_ACCESS_TOKEN. If your Google Cloud setup needs a
quota project, set GOOGLE_CLOUD_QUOTA_PROJECT.

Lab guide links: each walkthrough slide links to its lab guide. By default that's the lab's
Markdown on GitHub. To link to your own Google Docs instead, set GUIDE_DOC_IDS to a JSON object of
lab number -> Google Doc ID, for example '{"1": "1AbC...", "2": "1DeF..."}'.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request

QUOTA = os.environ.get("GOOGLE_CLOUD_QUOTA_PROJECT", "")

# ---- design tokens ----
OAT, INK, BODY, LAVA, TEAL, RULE, DARK, CARD, MUTED = (
    "F7F3EB", "17150F", "4A4640", "FF3621", "1B5162", "D8CFC0", "1C1A15", "EFE8DC", "8A847A")
SERIF, SANS = "Fraunces", "DM Sans"
W, H = 720, 405  # points (16:9)

ICON = "https://img.icons8.com/ios/200/1C1A15/{}.png"
PHOTO = "https://images.unsplash.com/{}?w={}&h={}&fit=crop&q=80"
PH_STUDENTS = "photo-1522202176988-66273c2fd55f"
PH_TEAM = "photo-1531482615713-2afd69097998"
PH_TOWERS = "photo-1486406146926-c627a92ad1ab"

REPO = "https://github.com/mimi-park-ai/genie-101-workshop/blob/main/labs/"
LAB_FILES = {1: "01_databricks_101", 2: "02_upload_google_sheets", 3: "03_visual_data_prep",
             4: "04_dashboard", 5: "05_genie_agent", 6: "06_semantic_layer", 7: "07_metric_views",
             8: "08_scheduling", 9: "09_agent_governance", 10: "10_ai_gateway", 11: "11_mcp"}
_DOC_IDS = {int(k): v for k, v in json.loads(os.environ.get("GUIDE_DOC_IDS", "{}")).items()}


def guide_url(n):
    if n in _DOC_IDS:
        return f"https://docs.google.com/document/d/{_DOC_IDS[n]}/edit"
    return REPO + LAB_FILES[n] + ".md"


# ============================================================ API plumbing
def _token() -> str:
    if os.environ.get("GOOGLE_ACCESS_TOKEN"):
        return os.environ["GOOGLE_ACCESS_TOKEN"]
    return subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True, check=True).stdout.strip()


class Api:
    def __init__(self):
        self.h = {"Authorization": "Bearer " + _token(), "Content-Type": "application/json"}
        if QUOTA:
            self.h["x-goog-user-project"] = QUOTA

    def call(self, method, url, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers=self.h)
        try:
            return json.loads(urllib.request.urlopen(req).read() or b"{}")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{e.code}: {e.read().decode()[:800]}") from None

    def batch(self, pid, reqs):
        if reqs:
            self.call("POST", f"https://slides.googleapis.com/v1/presentations/{pid}:batchUpdate", {"requests": reqs})


def rgb(h):
    return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}


def pt(v):
    return {"magnitude": v, "unit": "PT"}


# ============================================================ slide primitives
class Slide:
    """Collects the requests for one slide."""

    def __init__(self, sid, bg=OAT, index=None):
        self.sid, self.reqs, self.k, self.notes = sid, [], 0, ""
        cs = {"objectId": sid, "slideLayoutReference": {"predefinedLayout": "BLANK"}}
        if index is not None:
            cs["insertionIndex"] = index
        self.reqs.append({"createSlide": cs})
        self.reqs.append({"updatePageProperties": {"objectId": sid, "fields": "pageBackgroundFill.solidFill.color",
                                                   "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(bg)}}}}}})

    def _id(self):
        self.k += 1
        return f"{self.sid}_e{self.k}"

    def _props(self, x, y, w, h):
        return {"pageObjectId": self.sid, "size": {"width": pt(w), "height": pt(h)},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": x, "translateY": y, "unit": "PT"}}

    def text(self, x, y, w, h, runs, size=12, font=SANS, color=BODY, bold=False, italic=False,
             align="START", valign="TOP", spacing=115, fill=None):
        """runs: a string, or a list of (text, style-overrides) tuples."""
        if isinstance(runs, str):
            runs = [(runs, {})]
        oid = self._id()
        full = "".join(t for t, _ in runs)
        self.reqs.append({"createShape": {"objectId": oid, "shapeType": "TEXT_BOX", "elementProperties": self._props(x, y, w, h)}})
        sp = {"contentAlignment": valign}
        fields = "contentAlignment"
        if fill:
            sp["shapeBackgroundFill"] = {"solidFill": {"color": {"rgbColor": rgb(fill)}}}
            fields += ",shapeBackgroundFill.solidFill.color"
        self.reqs.append({"updateShapeProperties": {"objectId": oid, "fields": fields, "shapeProperties": sp}})
        self.reqs.append({"insertText": {"objectId": oid, "text": full}})
        self.reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                              "fields": "fontFamily,fontSize,foregroundColor,bold,italic",
                                              "style": {"fontFamily": font, "fontSize": pt(size), "bold": bold, "italic": italic,
                                                        "foregroundColor": {"opaqueColor": {"rgbColor": rgb(color)}}}}})
        self.reqs.append({"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                                   "fields": "alignment,lineSpacing,spaceAbove,spaceBelow",
                                                   "style": {"alignment": align, "lineSpacing": spacing,
                                                             "spaceAbove": pt(0), "spaceBelow": pt(0)}}})
        i = 0
        for t, st in runs:
            if st and t:
                style, fl = {}, []
                for key, val in st.items():
                    if key == "color":
                        style["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb(val)}}; fl.append("foregroundColor")
                    elif key == "size":
                        style["fontSize"] = pt(val); fl.append("fontSize")
                    elif key == "font":
                        style["fontFamily"] = val; fl.append("fontFamily")
                    elif key == "link":
                        style["link"] = {"url": val}; fl.append("link")
                        if "color" not in st:  # links default to bright blue; keep the box's color
                            style["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb(color)}}; fl.append("foregroundColor")
                    else:
                        style[key] = val; fl.append(key)
                self.reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "FIXED_RANGE", "startIndex": i, "endIndex": i + len(t)},
                                                      "fields": ",".join(fl), "style": style}})
            i += len(t)
        return oid

    def rect(self, x, y, w, h, fill, outline=None):
        oid = self._id()
        self.reqs.append({"createShape": {"objectId": oid, "shapeType": "RECTANGLE", "elementProperties": self._props(x, y, w, h)}})
        sp = {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(fill)}}}}
        if outline:
            sp["outline"] = {"outlineFill": {"solidFill": {"color": {"rgbColor": rgb(outline)}}}, "weight": pt(0.75)}
        else:
            sp["outline"] = {"propertyState": "NOT_RENDERED"}
        self.reqs.append({"updateShapeProperties": {"objectId": oid, "fields": "shapeBackgroundFill.solidFill.color,outline", "shapeProperties": sp}})
        return oid

    def line(self, x1, y1, x2, y2, color=RULE, weight=0.75, arrow=False):
        oid = self._id()
        w, h = max(abs(x2 - x1), 0.01), max(abs(y2 - y1), 0.01)
        self.reqs.append({"createLine": {"objectId": oid, "lineCategory": "STRAIGHT", "elementProperties": {
            "pageObjectId": self.sid, "size": {"width": pt(w), "height": pt(h)},
            "transform": {"scaleX": 1 if x2 >= x1 else -1, "scaleY": 1 if y2 >= y1 else -1,
                          "translateX": x1, "translateY": y1, "unit": "PT"}}}})
        lp = {"lineFill": {"solidFill": {"color": {"rgbColor": rgb(color)}}}, "weight": pt(weight)}
        fields = "lineFill.solidFill.color,weight"
        if arrow:
            lp["endArrow"] = "FILL_ARROW"; fields += ",endArrow"
        self.reqs.append({"updateLineProperties": {"objectId": oid, "fields": fields, "lineProperties": lp}})

    def image(self, url, x, y, w, h):
        oid = self._id()
        self.reqs.append({"createImage": {"objectId": oid, "url": url, "elementProperties": self._props(x, y, w, h)}})

    def eyebrow(self, x, y, label, color=LAVA, w=520):
        self.text(x, y, w, 14, label.upper(), size=8.5, bold=True, color=color)

    def footer(self, n, total, dark=False):
        c = OAT if dark else INK
        self.text(40, 378, 120, 14, [("databricks", {}), (".", {"color": LAVA})], size=9.5, bold=True, color=c)
        self.text(560, 378, 120, 14, f"{n:02d} / {total:02d}", size=8.5, color=MUTED, align="END")


# ============================================================ slide layouts
def title_slide(s: Slide):
    s.image(PHOTO.format(PH_STUDENTS, 900, 1215), 420, 0, 300, 405)
    s.eyebrow(40, 72, "Hands-on workshop · University edition")
    s.text(40, 92, 360, 70, "Genie 101", size=52, font=SERIF, color=INK)
    s.text(40, 160, 360, 36, "Data to agents in a day", size=22, font=SERIF, color=INK, italic=True)
    s.line(40, 210, 110, 210, color=LAVA, weight=1.5)
    s.text(40, 224, 340, 70, "Turn a bank's messy spreadsheets into a trusted, governed AI agent, "
           "step by step, in your own free Databricks account. No experience needed.", size=12, color=BODY, spacing=135)
    s.text(40, 378, 160, 14, [("databricks", {}), (".", {"color": LAVA})], size=10, bold=True, color=INK)
    s.text(150, 378, 250, 14, "Databricks Free Edition", size=8.5, color=MUTED)


def agenda_slide(s: Slide, labs):
    s.eyebrow(40, 36, "Today's path")
    s.text(40, 52, 640, 40, "Eleven labs, one story", size=28, font=SERIF, color=INK)
    col_x, row_h = [40, 380], 42
    for i, (num, name, mins) in enumerate(labs):
        cx = col_x[0] if i < 6 else col_x[1]
        cy = 104 + (i if i < 6 else i - 6) * row_h
        s.line(cx, cy, cx + 300, cy, color=RULE)
        s.text(cx, cy + 8, 44, 30, f"{num:02d}", size=20, font=SERIF, color=LAVA)
        s.text(cx + 50, cy + 10, 200, 30, name, size=12, bold=True, color=INK)
        s.text(cx + 240, cy + 12, 60, 20, f"{mins} min", size=9.5, color=MUTED, align="END")


def three_ideas_slide(s: Slide):
    s.eyebrow(40, 36, "The big idea")
    s.text(40, 52, 640, 70, "AI is only as good as\nits data and its context", size=28, font=SERIF, color=INK)
    ideas = [
        ("1", "Trusted data", "Labs 2–3", "Raw spreadsheets in, clean gold tables out. Messy data in means messy answers out."),
        ("2", "Business context", "Labs 6–7", "Descriptions, business terms, and metric views teach the AI what your words mean."),
        ("3", "Governance", "Labs 8–11", "Schedules, permissions, AI Gateway, and MCP make the agent safe to use everywhere."),
    ]
    for i, (n, head, labs, body) in enumerate(ideas):
        x = 40 + i * 215
        s.line(x, 172, x + 190, 172, color=INK, weight=1)
        s.text(x, 182, 60, 56, n, size=44, font=SERIF, color=LAVA)
        s.text(x, 240, 190, 20, head, size=14, bold=True, color=INK)
        s.text(x, 260, 190, 16, labs.upper(), size=8, bold=True, color=TEAL)
        s.text(x, 280, 190, 80, body, size=10.5, color=BODY, spacing=135)


def story_slide(s: Slide):
    s.image(PHOTO.format(PH_TOWERS, 780, 1215), 460, 0, 260, 405)
    s.eyebrow(40, 36, "The scenario")
    s.text(40, 52, 400, 40, "Meet Summit Financial", size=28, font=SERIF, color=INK)
    s.text(40, 98, 390, 50, "A Texas bank with about 1,000 customers. By law, every complaint must be "
           "resolved within 8 weeks. Missing that deadline is an SLA breach.", size=11.5, color=BODY, spacing=135)
    s.text(40, 168, 390, 14, "THE VP'S QUESTIONS", size=8.5, bold=True, color=TEAL)
    qs = ["What's our NPS, and which channel is dragging it down?",
          "Which critical complaints are about to miss their deadline?",
          "How often do we solve a problem on the first contact?",
          "What are customers actually saying when they complain?"]
    for i, q in enumerate(qs):
        y = 188 + i * 44
        s.line(40, y, 420, y, color=RULE)
        s.text(40, y + 8, 380, 34, f"“{q}”", size=12.5, font=SERIF, italic=True, color=INK)


def kpi_slide(s: Slide):
    s.eyebrow(40, 36, "The KPIs")
    s.text(40, 52, 640, 40, "Four numbers the VP watches", size=28, font=SERIF, color=INK)
    s.text(40, 94, 640, 34, "Every question today comes back to these. Notice how precise each definition is: "
           "that precision is exactly what you'll teach the AI in Labs 6 and 7.", size=11, color=BODY, spacing=135)
    kpis = [
        ("NPS", "Net Promoter Score", "How likely are customers to recommend us?",
         "% of promoters (score 9–10) minus % of detractors (0–6). From −100 to +100.",
         "It's not the average score."),
        ("Complaints", "Complaint volume", "How many complaints, and how many are still open?",
         "Cases where case_type is COMPLAINT. Open = not resolved yet.",
         "Service requests aren't complaints."),
        ("SLA breach rate", "8-week deadline", "Are we missing the deadline?",
         "Complaints resolved after their 56-day deadline ÷ all resolved complaints.",
         "Open complaints aren't counted."),
        ("FCR", "First-contact resolution", "Do we fix it the first time?",
         "Contacts resolved during that first contact ÷ all contacts.",
         "Escalated or transferred contacts don't count as resolved."),
    ]
    for i, (name, sub, question, calc, trap) in enumerate(kpis):
        x = 40 + i * 162
        s.line(x, 144, x + 148, 144, color=INK, weight=1)
        s.text(x, 152, 148, 26, name, size=17, font=SERIF, color=LAVA)
        s.text(x, 178, 148, 14, sub.upper(), size=7.5, bold=True, color=MUTED)
        s.text(x, 196, 148, 40, f"“{question}”", size=10.5, font=SERIF, italic=True, color=INK, spacing=120)
        s.text(x, 244, 148, 12, "HOW IT'S CALCULATED", size=7.5, bold=True, color=TEAL)
        s.text(x, 258, 148, 52, calc, size=9.5, color=BODY, spacing=130)
        s.text(x, 316, 148, 12, "WATCH OUT", size=7.5, bold=True, color=LAVA)
        s.text(x, 330, 148, 36, trap, size=9.5, color=INK, spacing=130)


def data_map_slide(s: Slide):
    s.eyebrow(40, 36, "The data · Lab 2")
    s.text(40, 52, 640, 40, "Five Google Sheets, linked by IDs", size=28, font=SERIF, color=INK)
    boxes = {  # name: (x, y, rows, desc)
        "customers": (40, 130, "~1,000", "Who the customers are: segment, age, city"),
        "service_cases": (200, 130, "~3,000", "Complaints and service requests, with deadlines"),
        "interactions": (360, 130, "4,000", "Every call, chat, and branch visit"),
        "nps_survey": (520, 130, "800", "0–10 satisfaction scores, with comments"),
        "call_insights": (360, 262, "~380", "AI summaries of complaint conversations"),
    }
    bw, bh = 150, 82
    for name, (x, y, rows, desc) in boxes.items():
        s.rect(x, y, bw, bh, "FFFFFF", outline=RULE)
        s.text(x + 10, y + 9, bw - 20, 16, name, size=10.5, bold=True, color=INK)
        s.text(x + 10, y + 26, bw - 20, 14, f"{rows} rows", size=8.5, bold=True, color=LAVA)
        s.text(x + 10, y + 42, bw - 20, 36, desc, size=9, color=BODY, spacing=125)
    for x1, x2, label in [(190, 200, "customer_id"), (350, 360, "case_id"), (510, 520, "interaction_id")]:
        s.line(x1, 171, x2, 171, color=INK, weight=1, arrow=True)
        s.text(x1 - 40, 112, 90, 14, label, size=7.5, color=TEAL, bold=True, align="CENTER")
    s.line(435, 212, 435, 262, color=INK, weight=1, arrow=True)
    s.text(440, 230, 90, 14, "interaction_id", size=7.5, color=TEAL, bold=True)
    s.text(40, 262, 300, 90, [("Messy on purpose. ", {"bold": True, "color": INK}),
                              ("Mixed capitalization, duplicate rows, blanks, and dates stored as text. "
                               "You'll clean all of it in Lab 3, without code.", {})], size=10.5, color=BODY, spacing=135)


def build_slide(s: Slide):
    s.image(PHOTO.format(PH_TEAM, 780, 1215), 460, 0, 260, 405)
    s.eyebrow(40, 36, "What you'll build")
    s.text(40, 52, 410, 40, "From spreadsheet to AI agent", size=26, font=SERIF, color=INK)
    chain = ["Google Sheets", "Raw tables", "Gold tables", "Dashboard + Genie Agent"]
    for i, c in enumerate(chain):
        y = 112 + i * 44
        s.text(40, y, 22, 28, f"{i + 1}", size=18, font=SERIF, color=LAVA)
        s.text(70, y + 4, 340, 22, c, size=13, bold=True, color=INK)
    s.line(40, 296, 420, 296, color=RULE)
    s.text(40, 306, 380, 60, [("Then make it trustworthy: ", {"bold": True, "color": INK}),
                              ("semantic layer · metric views · schedules · governance · AI Gateway · MCP", {})],
           size=11, color=BODY, spacing=135)


def concept_slide(s: Slide, lab):
    s.text(40, 34, 150, 80, f"{lab['n']:02d}", size=64, font=SERIF, color=LAVA)
    s.image(ICON.format(lab["icon"]), 46, 128, 34, 34)
    s.eyebrow(210, 44, f"Lab {lab['n']} · Concept")
    title_lines = 1 if len(lab["title"]) <= 34 else 2
    s.text(210, 62, 470, 70, lab["title"], size=25, font=SERIF, color=INK, spacing=105)
    lead_y = 62 + title_lines * 32 + 10
    s.text(210, lead_y, 470, 60, lab["lead"], size=12, color=BODY, spacing=135)
    cy = lead_y + 88
    for i, (head, body) in enumerate(lab["cards"]):
        x = 210 + i * 160
        s.line(x, cy, x + 145, cy, color=INK, weight=1)
        s.text(x, cy + 10, 145, 34, head, size=11.5, bold=True, color=INK, spacing=110)
        s.text(x, cy + 32, 145, 96, body, size=9.5, color=BODY, spacing=135)


def walk_slide(s: Slide, lab):
    s.eyebrow(40, 34, f"Lab {lab['n']} · Walkthrough · {lab['mins']} min")
    s.text(40, 50, 640, 40, lab["walk_title"], size=24, font=SERIF, color=INK)
    steps = lab["steps"]
    size, per_line = 10.5, 64
    def heights(sz, chars):
        return [-(-len(st) // chars) * sz * 1.35 + 10 for st in steps]
    hs = heights(size, per_line)
    if sum(hs) > 226:
        size, per_line = 10, 68
        hs = heights(size, per_line)
    gap = max(0, (226 - sum(hs)) / max(len(steps), 1))
    y = 104
    for i, (st, h) in enumerate(zip(steps, hs)):
        s.text(40, y - 2, 26, 24, f"{i + 1}", size=16, font=SERIF, color=LAVA)
        s.text(68, y, 362, h, st, size=size, color=INK, spacing=125)
        y += h + min(gap, 10)
    s.rect(456, 104, 224, 214, CARD)
    s.text(472, 116, 192, 14, "YOU SHOULD SEE", size=8, bold=True, color=TEAL)
    s.text(472, 132, 192, 80, lab["see"], size=10, color=INK, spacing=130)
    s.line(472, 218, 664, 218, color=RULE)
    s.text(472, 228, 192, 14, "IF YOU'RE STUCK", size=8, bold=True, color=LAVA)
    s.text(472, 244, 192, 70, lab["stuck"], size=10, color=BODY, spacing=130)
    s.text(456, 334, 224, 16, [(f"Student guide: Lab {lab['n']} ↗", {"link": guide_url(lab["n"])})],
           size=9.5, bold=True, color=TEAL, align="END")


def proof_slide(s: Slide):
    s.eyebrow(40, 36, "Lab 7 · The proof")
    s.text(40, 52, 640, 40, "Same question. Same data. Different answer.", size=26, font=SERIF, color=INK)
    s.text(40, 98, 640, 20, "“What is our NPS?”", size=14, font=SERIF, italic=True, color=BODY)
    s.text(40, 128, 300, 120, "7.7", size=96, font=SERIF, color=MUTED)
    s.text(40, 250, 280, 40, [("Before. ", {"bold": True, "color": INK}), ("The agent averaged the 0–10 scores.", {})],
           size=11, color=BODY, spacing=130)
    s.line(355, 140, 355, 290, color=RULE)
    s.text(390, 128, 300, 120, "34", size=96, font=SERIF, color=LAVA)
    s.text(390, 250, 290, 40, [("After. ", {"bold": True, "color": INK}),
                               ("NPS from the metric view: % promoters minus % detractors.", {})], size=11, color=BODY, spacing=130)
    s.line(40, 310, 680, 310, color=INK, weight=1)
    s.text(40, 322, 640, 30, "The AI didn't get smarter. It got context.", size=18, font=SERIF, italic=True, color=INK)


def recap_slide(s: Slide):
    s.eyebrow(40, 36, "Recap")
    s.text(40, 52, 640, 40, "From spreadsheets to a governed AI agent", size=26, font=SERIF, color=INK)
    rows = [("Trusted data", "Loaded raw sheets, cleaned them into gold tables with no code."),
            ("Insight", "Built a dashboard and an AI agent on the gold tables."),
            ("Context", "Taught the agent your business, and proved it with benchmarks."),
            ("Operations", "Put it on a schedule, governed it, controlled AI use, and opened it to other tools.")]
    for i, (head, body) in enumerate(rows):
        y = 112 + i * 56
        s.line(40, y, 680, y, color=RULE)
        s.image(ICON.format("checked"), 40, y + 12, 22, 22)
        s.text(74, y + 12, 160, 24, head, size=13, bold=True, color=INK)
        s.text(240, y + 14, 440, 36, body, size=11.5, color=BODY, spacing=130)


def keep_going_slide(s: Slide):
    s.eyebrow(40, 36, "Keep going")
    s.text(40, 52, 640, 40, "Your account is yours to keep", size=26, font=SERIF, color=INK)
    cols = [("Free Edition", "Keep building in the account you made today. Try your own data.",
             "databricks.com/learn/free-edition", "https://www.databricks.com/learn/free-edition"),
            ("Databricks Academy", "Free self-paced courses on data engineering, analytics, and AI.",
             "databricks.com/learn/training", "https://www.databricks.com/learn/training/home"),
            ("Documentation", "Step-by-step guides for every feature you used today.",
             "docs.databricks.com", "https://docs.databricks.com")]
    for i, (head, body, label, url) in enumerate(cols):
        x = 40 + i * 215
        s.line(x, 132, x + 190, 132, color=INK, weight=1)
        s.text(x, 144, 190, 24, head, size=14, bold=True, color=INK)
        s.text(x, 172, 190, 60, body, size=10.5, color=BODY, spacing=135)
        s.text(x, 240, 190, 16, [(label + " ↗", {"link": url})], size=9.5, bold=True, color=TEAL)


def closing_slide(s: Slide):
    s.text(40, 120, 640, 70, "Thank you", size=54, font=SERIF, color=OAT)
    s.line(40, 196, 110, 196, color=LAVA, weight=1.5)
    s.text(40, 214, 640, 24, "Questions? Contact Mimi Park", size=16, font=SERIF, color=OAT, italic=True)
    s.text(40, 242, 640, 20, [("mimi.park@databricks.com", {"link": "mailto:mimi.park@databricks.com"})], size=11, color="D8CFC0")


# ============================================================ content
LABS = [
    dict(n=1, name="Databricks 101", mins=30, icon="database",
         title="One platform for data and AI",
         lead="Databricks keeps a company's data in one place, and lets people clean it, analyze it, and build AI on it, "
              "with security built in.",
         cards=[("Workspace", "Your own environment: files, notebooks, and tools."),
                ("Unity Catalog", "Data organized as catalog → schema → table, and rules for who can see what."),
                ("Warehouse + Genie", "The engine that runs your queries, and the AI that answers in plain English.")],
         walk_title="Sign up, look around, run your first query",
         steps=["Go to databricks.com/learn/free-edition and sign up (email code, Google, or Microsoft).",
                "Tour the sidebar: Workspace, Catalog, SQL Editor, Genie, Dashboards, Jobs & Pipelines.",
                "In the SQL Editor, run  SELECT 'hello, Databricks'.",
                "Create the schema  workspace.summit_financial."],
         see="summit_financial listed under the workspace catalog in Catalog.",
         stuck="No sign-up email? Check spam, or sign up with Google or Microsoft instead.",
         notes="Start the sign-ups first: workspace creation takes about a minute, so explain the platform while people wait. "
               "Key vocabulary for the day: workspace, catalog → schema → table, Unity Catalog, SQL warehouse, Genie. "
               "The first query can take 10–20 seconds while the warehouse starts. Reassure people that's normal."),
    dict(n=2, name="Meet the data and upload it", mins=20, icon="google-sheets",
         title="Keep a raw copy of what arrived",
         lead="Real data arrives messy. Data teams load it as-is first, as raw tables, and clean it in a separate step, "
              "so the original is never lost.",
         cards=[("Five sheets", "Customers, cases, contacts, surveys, and AI summaries of complaint conversations."),
                ("Linked by IDs", "customer_id, case_id, and interaction_id connect the tables."),
                ("Messy on purpose", "Mixed capitalization, duplicates, blanks, and text-typed dates.")],
         walk_title="Download the sheets, upload them as tables",
         steps=["Read the data tour in the Lab 2 guide: what each sheet and column means.",
                "Download each Google Sheet: File → Download → CSV.",
                "In Databricks: + New → Add or upload data → Create or modify table.",
                "Set catalog workspace, schema summit_financial, and the table name (customers_raw, …).",
                "Check the headers are real column names, then Create table. Repeat for all five."],
         see="Five tables in summit_financial: call_insights, customers_raw, interactions_raw, nps_survey, service_cases_raw.",
         stuck="Columns named _c0, _c1? Re-upload with “First row contains header” turned on.",
         notes="Spend the first five minutes on the data tour. It's what makes the rest of the day make sense. "
               "Point out the shared IDs, and the key terms: complaint, SLA breach, NPS, first-contact resolution. "
               "Ask: there are only four severities, so how many spellings do you see? That sets up Lab 3."),
    dict(n=3, name="Visual Data Prep", mins=40, icon="broom",
         title="Raw in, gold out",
         lead="Clean, trusted “gold” tables are the foundation for every dashboard and AI agent. "
              "Visual Data Prep builds them with drag-and-drop steps instead of code.",
         cards=[("Unique", "Removes duplicate rows: a few customers were exported twice."),
                ("Prepare", "Trim spaces, fix capitalization, change types, add calculated columns."),
                ("Join + Output", "Combine tables on a shared ID, then save the result as a gold table.")],
         walk_title="Build three gold tables with no code",
         steps=["+ New → Visual data prep. Name it summit_gold.",
                "gold_customers: Source → Unique → Prepare (segment uppercase, blank city → UNKNOWN) → Output.",
                "gold_cases: Unique → Prepare (fix severity, cast dates) → Join customers → add is_complaint, is_open, "
                "is_sla_breach, days_to_resolve → Output.",
                "gold_interactions: Prepare (channel, timestamp, boolean) → Join segment → Output.",
                "Run, and check the row counts."],
         see="gold_customers 1,000 · gold_cases 3,000 · gold_interactions 4,000 rows. Four clean severities.",
         stuck="Import the finished flow (summit_gold.designer.ipynb), or run the SQL fallback in the guide.",
         notes="The longest hands-on lab. Encourage everyone to try the AI assistant for at least one step: describe the step in "
               "plain English and check what it built. At the 25-minute mark, point slower students to the finished flow "
               "or the SQL fallback: both produce the same tables. Teaching point: messy data in means messy AI answers out."),
    dict(n=4, name="AI/BI Dashboard", mins=35, icon="combo-chart",
         title="A single pane of glass for leaders",
         lead="Dashboards built on gold tables give leaders numbers they can trust. AI drafts the charts; you check them.",
         cards=[("Built on gold", "Every chart reads the clean tables, so numbers agree."),
                ("AI drafts, you verify", "Describe a chart in plain English, then check one number yourself."),
                ("Ask Genie", "Leaders explore the dashboard by asking questions, no SQL needed.")],
         walk_title="Let AI draft the dashboard, then finish it",
         steps=["Dashboards → Create. Add gold_cases, gold_interactions, and nps_survey as data.",
                "Prompt the AI assistant: complaint counters, complaints by category, weekly trend, critical table.",
                "Verify one number in the SQL Editor: there are 2,108 complaints.",
                "Add a segment filter, give charts titles, and Publish.",
                "On the published dashboard, Ask Genie a question."],
         see="A published dashboard with four visuals; choosing WEALTH in the filter shrinks every number.",
         stuck="No AI assistant? Add each visual by hand with “Add a visualization”.",
         notes="Stress the habit of checking AI's work: the complaint count should be 2,108, not 3,000. "
               "Plant the seed for Lab 7: ask the dashboard for NPS and note how it calculates it. "
               "NPS isn't an average score, and AI often gets that wrong until you teach it."),
    dict(n=5, name="Build a Genie Agent", mins=35, icon="bot",
         title="An AI coworker for your data",
         lead="A Genie Agent answers questions about the tables you give it, in plain English, and shows the SQL it wrote "
              "so you can check its work.",
         cards=[("Scoped data", "It only sees the tables you add, nothing else."),
                ("Instructions", "Tell it how to behave: what to prioritize, what to always show."),
                ("Benchmarks", "Questions with known answers that measure accuracy objectively.")],
         walk_title="Create the Complaint-Triage Agent, and score it",
         steps=["Genie → + New. Add gold_cases, gold_interactions, nps_survey, call_insights.",
                "Name it Complaint-Triage Agent, and paste the instructions from the guide.",
                "Add the three sample questions, and try them. Click Show code to see the SQL.",
                "Ask the tricky ones: “What is our NPS?” and “What is our SLA breach rate?”",
                "Add the 8 benchmark questions, Run all, and record your Before score."],
         see="Sensible answers with SQL you can read. A Before score of about 5–6 out of 8 is normal.",
         stuck="Can't find Benchmarks? Ask the 8 questions in chat and compare with the answer table.",
         notes="Make sure everyone records a Before score: Lab 7 depends on it. "
               "Questions 1–4 (NPS, NPS by channel, complaint count, SLA breach rate) depend on business definitions "
               "the agent hasn't learned yet, so low scores there are expected and are the point."),
    dict(n=6, name="Semantic layer", mins=25, icon="book",
         title="Teach the AI your business language",
         lead="The semantic layer maps business words like “NPS” to the data. It lives in Unity Catalog, so every tool, "
              "and every AI, reads the same definitions.",
         cards=[("Descriptions", "AI drafts table and column descriptions; you review and correct them."),
                ("Domains", "Group trusted assets by business area, and certify the gold tables."),
                ("Business terms", "Define NPS, complaint, and SLA breach rate once, in plain language.")],
         walk_title="Describe the data, then define the terms",
         steps=["Catalog → gold_cases → AI generate the description. Review it, then Save.",
                "Describe is_complaint, is_sla_breach, is_open, and nps_survey.score exactly as the guide says.",
                "Discover → create a Customer Service domain; add the four tables; certify the gold ones.",
                "Add pages for NPS, Complaint, and SLA breach rate.",
                "Ask the agent “What is our NPS?” again."],
         see="Descriptions on every key column, a Customer Service domain, and an NPS answer closer to 34.",
         stuck="No domains or pages yet? Paste the three definitions into the agent's Instructions instead.",
         notes="Frame it as onboarding a new employee: what would they need to know? "
               "Domains and pages may not be in every account yet; the fallback (definitions in the agent's instructions) "
               "teaches the same idea. Genie's Ontology combines what you write here with what it learns from usage."),
    dict(n=7, name="Metric views", mins=35, icon="ruler",
         title="Define it once, use it everywhere",
         lead="A metric view stores the calculation itself in Unity Catalog. When anyone asks for NPS, Databricks uses your "
              "formula every time, instead of the AI guessing.",
         cards=[("One formula", "NPS, complaints, SLA breach rate, and first-contact resolution, defined once."),
                ("Every tool", "Dashboards, agents, and SQL all get the same answer."),
                ("Synonyms", "Display names and synonyms match the words people actually use.")],
         walk_title="Create metric views, then benchmark again",
         steps=["Run the metric view SQL from the guide: three views on the gold tables and the survey.",
                "Test it: SELECT channel, MEASURE(nps) … GROUP BY channel.",
                "Add the three metric views to your agent, plus one line of instructions.",
                "Re-run all benchmarks, and record your After score."],
         see="NPS by channel: Branch 38 · Call center 30 · Mobile 39 · Online 35. Questions 1–4 flip from ❌ to ✅.",
         stuck="YAML version error? Change version 1.1 to 0.1 and delete the display_name and synonyms lines.",
         notes="This is the aha moment. Ask a few students to read out their before and after scores. "
               "The point to land: the model didn't change between the two runs. The context did."),
    dict(n=8, name="Scheduling", mins=20, icon="calendar",
         title="From a tool you ask to a coworker that tells you",
         lead="Schedules keep data fresh and deliver answers automatically, so the right people see the right numbers "
              "without having to remember to look.",
         cards=[("Fresh data", "Re-run the gold flow every morning."),
                ("Reports delivered", "Email the dashboard to subscribers on weekdays."),
                ("Agent briefings", "A scheduled task asks the agent a question and sends the answer.")],
         walk_title="Put the work on autopilot",
         steps=["Open summit_gold → Schedule → every day at 6:00 AM.",
                "Open the dashboard → Schedule → weekdays at 6:30 AM; subscribe yourself.",
                "Open the agent → new scheduled task: critical and high complaints due in 14 days, at 8:00 AM.",
                "Click Run now to test the briefing."],
         see="Three schedules, at three different times, and one briefing delivered.",
         stuck="A run stuck in “queued”? Free Edition runs only a few things at once. Stagger the times.",
         notes="Free Edition caps how many tasks run at once, so insist on different times for each schedule. "
               "Agent scheduled tasks are in preview and may not be in every account; demo it if needed."),
    dict(n=9, name="Agent governance", mins=25, icon="shield",
         title="The rules live on the data, not the agent",
         lead="An agent must never become a back door. In Databricks it inherits the permissions of the person asking, "
              "and the rules apply in every tool at once.",
         cards=[("Column masks", "Hide personal data, like emails, from people who don't need it."),
                ("Row filters", "Show each team only the rows it's allowed to see."),
                ("Trust", "Benchmarks, monitoring, and sharing settings prove the agent can be relied on.")],
         walk_title="Watch the agent follow the rules",
         steps=["Run Part 1 of the guide: mask customer_email. Ask the agent for an email: it's masked.",
                "Add yourself to pii_access, and ask again: now you see it.",
                "Add a RETAIL-only row filter. Complaints by segment: only RETAIL, 1,524.",
                "Grant yourself every segment, and ask again: all three, 2,108 in total.",
                "Look at Monitoring and Share, then run the clean-up."],
         see="The agent's answers change with the rules, without changing the agent itself.",
         stuck="Counts didn't change? Ask in a new chat so the agent runs a fresh query.",
         notes="The key line: you changed the data's rules, not the agent, and it followed them. "
               "The access tables use current_user() so it works in a single-person account; companies usually use "
               "groups or tag-based (ABAC) policies, but the idea is the same. Make sure everyone runs the clean-up."),
    dict(n=10, name="AI Gateway", mins=20, icon="traffic-light",
         title="A control point for every AI call",
         lead="Every AI feature calls a model behind the scenes. AI Gateway sits between users and models, to control "
              "cost, block unsafe input, and show who uses what.",
         cards=[("Cost", "Rate limits stop one app from running up the bill. Budgets cap spend."),
                ("Safety", "Guardrails block personal data from being sent to AI."),
                ("Visibility", "Usage tracking shows who used how much.")],
         walk_title="Turn on the controls, then try to break them",
         steps=["Serving → a databricks- chat model → Edit AI Gateway.",
                "Turn on usage tracking, a 2-per-minute rate limit per user, and a PII guardrail on input.",
                "In Playground, send three quick messages: the third is blocked.",
                "Send the letter prompt with a fake SSN: it's blocked as personal data.",
                "Turn the test rate limit back off."],
         see="One request blocked by the rate limit, and one blocked by the guardrail.",
         stuck="No AI Gateway settings in your account? Follow the instructor demo.",
         notes="Budgets need account-admin access, which Free Edition doesn't have, so demo them from your own screen: "
               "alert at 80% of monthly AI spend, block at 100%. Remind everyone to remove the test rate limit."),
    dict(n=11, name="MCP", mins=20, icon="plug",
         title="A universal plug for AI tools",
         lead="MCP is an open standard for connecting AI assistants to tools and data. Your Genie agent becomes a tool "
              "any assistant can use, with your permissions still applied.",
         cards=[("Open standard", "Works with Claude, ChatGPT, Cursor, and more."),
                ("Context built once", "The assistant asks your agent, which already knows your data and definitions."),
                ("Governance travels", "Assistants sign in as you, so they see only what you can see.")],
         walk_title="Use your agent from another AI assistant",
         steps=["Playground → Tools → MCP servers → Genie → your Complaint-Triage Agent.",
                "Ask: which open critical complaints are due soonest, and what did those customers say?",
                "Expand the tool call to see the chat model ask your agent.",
                "Copy your agent's MCP URL.",
                "Optional: add it to Claude or Cursor as a custom connector."],
         see="A chat model answering by calling your Genie agent, with the SQL visible in the tool call.",
         stuck="No MCP servers under Tools? Follow the instructor demo.",
         notes="Land the payoff of the whole day: the chat model knew nothing about the tables. It asked the agent, "
               "which carries the semantic layer and metric views from Labs 6–7. Build context once, use it everywhere."),
]

NOTES = {
    "title": "Welcome everyone. Today you'll go from a bank's messy spreadsheets to a governed AI agent, in your own free "
             "Databricks account. No prior experience needed: every step is in a printed or shared guide.",
    "agenda": "Eleven labs, each 20–40 minutes, plus lunch and breaks. Every lab has its own step-by-step guide. "
              "Labs 1–7 are the core; 8–11 add the habits real companies use to run AI safely.",
    "ideas": "Three ideas run through the whole day. First, trusted data: messy in, messy out. Second, business context: "
             "the AI needs to know what your words mean. Third, governance: AI has to be safe to use everywhere.",
    "story": "Summit Financial is fictional and all the data is synthetic, so explore freely. Read the four VP questions "
             "out loud: by the end of the day, your agent will answer all of them.",
    "kpis": "These four KPIs come back all day. Read each 'watch out' out loud: they're the mistakes an AI makes on raw data, "
            "and fixing them is the point of Labs 6 and 7. Don't share the actual values yet (for example, NPS is 34): "
            "the Lab 7 before-and-after reveal works better if students discover them.",
    "data": "Five sheets, linked by shared IDs. Walk the chain left to right: customers open cases, cases have contacts, "
            "contacts get surveyed, and complaint conversations get AI summaries. The mess is deliberate: Lab 3 fixes it.",
    "build": "The first half of the day builds the chain: sheets, raw tables, gold tables, then a dashboard and an agent. "
             "The second half makes it trustworthy and useful in practice.",
    "proof": "Reveal this after students record their After scores. Same question, same data. Before, the agent averaged "
             "the scores. After, it used the NPS formula you defined. The model didn't change; the context did.",
    "recap": "Recap the four stages. Ask: which step surprised you most? Usually it's how much the benchmarks moved in Lab 7.",
    "keep": "Their Free Edition account is theirs to keep. Encourage them to try their own data, and point them to the "
            "free Academy courses.",
    "close": "Thank everyone, and take questions.",
}


# ============================================================ build
def build(title):
    api = Api()
    pres = api.call("POST", "https://slides.googleapis.com/v1/presentations", {"title": title})
    pid = pres["presentationId"]
    first = pres["slides"][0]["objectId"]

    plan = [("title", title_slide, NOTES["title"]),
            ("agenda", lambda s: agenda_slide(s, [(l["n"], l["name"], l["mins"]) for l in LABS]), NOTES["agenda"]),
            ("ideas", three_ideas_slide, NOTES["ideas"]),
            ("story", story_slide, NOTES["story"]),
            ("kpis", kpi_slide, NOTES["kpis"]),
            ("data", data_map_slide, NOTES["data"]),
            ("build", build_slide, NOTES["build"])]
    for lab in LABS:
        plan.append((f"lab{lab['n']}c", lambda s, lab=lab: concept_slide(s, lab), lab["notes"]))
        plan.append((f"lab{lab['n']}w", lambda s, lab=lab: walk_slide(s, lab), lab["notes"]))
        if lab["n"] == 7:
            plan.append(("proof", proof_slide, NOTES["proof"]))
    plan += [("recap", recap_slide, NOTES["recap"]), ("keep", keep_going_slide, NOTES["keep"]),
             ("close", closing_slide, NOTES["close"])]

    total = len(plan)
    for n, (key, fn, notes) in enumerate(plan, start=1):
        dark = key == "close"
        s = Slide(f"g101_{key}", bg=DARK if dark else OAT)
        fn(s)
        if key != "title":
            s.footer(n, total, dark=dark)
        api.batch(pid, s.reqs)
        print(f"  {n:02d}/{total} {key}")
    api.batch(pid, [{"deleteObject": {"objectId": first}}])

    # speaker notes
    pres = api.call("GET", f"https://slides.googleapis.com/v1/presentations/{pid}?fields=slides(objectId,slideProperties(notesPage(notesProperties)))")
    by_id = {sl["objectId"]: sl["slideProperties"]["notesPage"]["notesProperties"]["speakerNotesObjectId"] for sl in pres["slides"]}
    reqs = [{"insertText": {"objectId": by_id[f"g101_{key}"], "text": notes}} for key, _, notes in plan]
    api.batch(pid, reqs)
    print(f"https://docs.google.com/presentation/d/{pid}/edit")
    return pid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="Genie 101 — Data to agents in a day (master deck)")
    build(ap.parse_args().title)
