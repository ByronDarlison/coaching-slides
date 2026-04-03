#!/usr/bin/env python3
"""
Build all coaching slideshow HTML files (M3 through M13).
Reads the CSS/JS template from M2 and generates each month's slideshow
with the correct deliverables, reading lists, and homework.
"""

import os
import html as html_mod

# ─── Paths ───────────────────────────────────────────────────────────
BASE_DIR = os.path.expanduser("~/coaching-slides")
MONTHLY_DIR = os.path.join(BASE_DIR, "monthly")

# ─── Image URL map (keyed by article topic) ──────────────────────────
IMG = {
    "kffm": "https://www.darlison.com/content/images/size/w1920/2026/03/key-function-flow-map-how-company-makes-money.png",
    "purpose": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_cav5aicav5aicav5.png",
    "planning": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_6ndqgg6ndqgg6ndq.png",
    "meetings": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_29ejjc29ejjc29ej.png",
    "aplayer": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_hhw37ohhw37ohhw3.png",
    "values": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_83f51483f51483f5.png",
    "scorecards": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_yxjsdkyxjsdkyxjs.png",
    "coaching": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_jksdx8jksdx8jksd.png",
    "skiplevel": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_nw29ftnw29ftnw29.png",
    "owner": "https://www.darlison.com/content/images/size/w1920/2026/03/Gemini_Generated_Image_c8oxcvc8oxcvc8ox.png",
}

# ─── Book data ────────────────────────────────────────────────────────
BOOKS_PREKICKOFF = [
    ("Metronomics", "Shannon Susko", "https://www.amazon.ca/dp/1544521294"),
    ("The Five Dysfunctions of a Team", "Patrick Lencioni", "https://www.amazon.ca/dp/0787960756"),
    ("Start with Why", "Simon Sinek", "https://www.amazon.ca/dp/1591846447"),
]
BOOKS_M3 = [
    ("3HAG WAY", "Shannon Susko", "https://www.amazon.ca/dp/1544503687"),
    ("Topgrading", "Bradford D. Smart", "https://www.amazon.ca/dp/1591845262"),
]
BOOKS_M6 = [
    ("The Four Obsessions of an Extraordinary Executive", "Patrick Lencioni", "https://www.amazon.ca/dp/0787954039"),
    ("Mastering the Rockefeller Habits", "Verne Harnish", "https://www.amazon.ca/dp/0978774957"),
]
BOOKS_M9 = [
    ("Overcoming the Five Dysfunctions of a Team", "Patrick Lencioni", "https://www.amazon.ca/dp/0787976377"),
    ("The Metronome Effect", "Shannon Susko", "https://www.amazon.ca/dp/1599325446"),
]
BOOKS_M12 = [
    ("Beyond Entrepreneurship 2.0", "Jim Collins & Bill Lazier", "https://www.amazon.ca/dp/0399564233"),
]

def reading_for(month):
    """Return cumulative book list for a given month."""
    books = list(BOOKS_PREKICKOFF)
    if month >= 3:
        books += BOOKS_M3
    if month >= 6:
        books += BOOKS_M6
    if month >= 9:
        books += BOOKS_M9
    if month >= 12:
        books += BOOKS_M12
    return books


# ─── Deliverable helper ──────────────────────────────────────────────
def D(name, symbol, badge, time, cumulative, subtitle=None, desc=None,
      points=None, article=None, prompt=None, image_key=None):
    """Create a deliverable dict."""
    return {
        "name": name,
        "symbol": symbol,
        "badge": badge,
        "time": time,
        "cumulative": cumulative,
        "subtitle": subtitle,
        "desc": desc,
        "points": points or [],
        "article": article,
        "prompt": prompt,
        "image_key": image_key,
    }


# ─── Homework helper ─────────────────────────────────────────────────
# Each homework section: (heading, items)
# Items can be strings or tuples of (name, article_url, prompt_url)

# ─── MEETING DATA ────────────────────────────────────────────────────

MEETINGS = {}

# ── M3 ────────────────────────────────────────────────────────────────
MEETINGS[3] = {
    "num": 3,
    "title": "Monthly Meeting Three",
    "subtitle": "From Vision to Execution — Your First Planning Cascade",
    "fixed_hw_time": 10,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("Org Function Chart", "▲", "symbol-evolution", 8, 20,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Revisit the functional map from M2 — have any new functions surfaced or been consolidated?",
              "Update ownership assignments: who has stepped into gaps since kick-off?",
          ]),
        D("KFFM", "▲", "symbol-evolution", 8, 28,
          subtitle="Key Function Flow Map",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Sharpen Level 1 widget flow — are the 3-5 key functions and their handoffs accurate?",
              "Begin identifying widgets (leads, orders, deliveries) flowing between functions",
              "Rate each function's maturity: still gut-feel or starting to get data?",
          ]),
        D("Functional Accountability Chart", "▲", "symbol-evolution", 6, 34,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Every function now needs a critical number with green/yellow/red thresholds",
              "Test: does each owner actually control the metric assigned to them?",
          ]),
        D("Profit/X", "▲", "symbol-evolution", 6, 40,
          subtitle="The one unit of measurement that captures how the company makes money",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Revisit the economic unit chosen at kick-off — does it still feel right?",
              "Cross-check against KFFM widgets: is Profit/X measurable from the flow?",
          ]),
        D("Core Values", "▲", "symbol-evolution", 8, 48,
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values",
          points=[
              "Values were acknowledged at kick-off; now begin formal discovery (Mission to Mars exercise)",
              "Seven story prompts surface real behavioral patterns: proudest moment, regretted decisions, behavioral frustrations, refused actions",
              "Goal: surface 5-8 candidate values to pressure-test over the coming months",
          ]),
        D("3HAG", "★", "symbol-introduced", 20, 68,
          subtitle="3-Year Highly Achievable Goal",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=[
              "Fiscal targets, key capabilities, and widget commitments for 3 years",
              "Gut it out: write the first version now — good enough, not perfect",
              "Must connect to the BHAG (10-30 yr) and drive the 1HAG below it",
              "Include 3-year widget projections that align to the KFFM",
          ]),
        D("1HAG", "★", "symbol-introduced", 16, 84,
          subtitle="1-Year Highly Achievable Goal",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=[
              "3-5 corporate priorities with single owners — shared ownership is no ownership",
              "Each priority needs a measurable outcome and a clear connection to the 3HAG",
              "Translate year one of the 3HAG into actionable annual targets",
          ]),
        D("QHAG + 13-Week Sprint Lanes", "★", "symbol-introduced", 21, 105,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=[
              "The 90-day plan: 3-5 priorities for this quarter, each with metrics and an owner",
              "Sprint Lanes: a 13-week grid with one binary deliverable per priority per week",
              "No gaps allowed — every week needs a milestone to prevent strategic work from slipping",
              "Each level must cascade cleanly: if quarterly work doesn't connect to the 3HAG, adjust",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize 3HAG, 1HAG, QHAG + Sprint Lanes in Mural and Metronome Software",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M4", [
            ("Market Map ★", None, None),
            ("Core Customer Analysis ★", None, None),
            ("Attribution Map ★", None, None),
        ]),
    ],
}

# ── M4 ────────────────────────────────────────────────────────────────
MEETINGS[4] = {
    "num": 4,
    "title": "Monthly Meeting Four",
    "subtitle": "Know Your Market — Mapping Customers, Competitors, and White Space",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 3, 15,
          desc="What the owner personally wants the business to deliver — by when, measured by what.",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("QHAG + Sprint Lanes", "✓", "symbol-confirm", 3, 18,
          desc="Quick alignment: are sprint lanes on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("Org Function Chart", "▲", "symbol-evolution", 6, 24,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Update for any structural changes since M3",
              "Review function ownership — any gaps that need filling?",
          ]),
        D("KFFM", "▲", "symbol-evolution", 6, 30,
          subtitle="Key Function Flow Map",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Continue sharpening widget definitions",
              "Are functions beginning to track their widgets?",
          ]),
        D("Functional Accountability Chart", "▲", "symbol-evolution", 5, 35,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Review critical numbers: any thresholds need adjustment?",
          ]),
        D("Profit/X", "▲", "symbol-evolution", 5, 40,
          subtitle="The one unit of measurement that captures how the company makes money",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Refine based on one quarter of data",
              "Does the chosen unit hold up?",
          ]),
        D("Core Values", "▲", "symbol-evolution", 6, 46,
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values",
          points=[
              "Review candidate values from M3 discovery",
              "Begin pressure testing: custom crisis scenarios to expose genuine commitment",
          ]),
        D("Market Map", "★", "symbol-introduced", 20, 66,
          points=[
              "Map ALL players: buyers/customers left, company center, suppliers right",
              "Draw channels, competitors, trade associations with sticky notes",
              "Follow the dollar — draw revenue flows, estimate percentages per channel",
              "Red circles = weak position, green = strong. Keep it on the wall, update quarterly",
          ]),
        D("Core Customer Analysis", "★", "symbol-introduced", 20, 86,
          points=[
              "Identify the ONE customer type who buys at a profit — not every customer",
              "Get down to eye level — name them, describe their life, create a cardboard cutout",
              "Often 60% of customers are Core Customers generating profit; the rest may cost more than they're worth",
              "Identify their top 3 needs and the benefits you offer to serve those needs",
          ]),
        D("Attribution Map", "★", "symbol-introduced", 17, 103,
          points=[
              "Identify 6-8 key market attributes. Rank your company and 2-4 competitors 1-5",
              "Plot as lines on a graph — where your line diverges from competitors is your white space",
              "Add a '3HAG Line' showing where you want to be in three years",
              "Forces strategic trade-offs: decide what you WILL do and what you WON'T",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize Market Map, Core Customer Analysis, and Attribution Map in Mural",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M5", [
            ("Function Scorecards ★", "https://www.darlison.com/scoreboard-day/", None),
            ("Activity Fit Map ★", None, None),
        ]),
    ],
}

# ── M5 ────────────────────────────────────────────────────────────────
MEETINGS[5] = {
    "num": 5,
    "title": "Monthly Meeting Five",
    "subtitle": "Sharpening the Edge — Scorecards, Differentiators, and Strategic Discipline",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("Core Purpose", "✓", "symbol-confirm", 2, 14,
          desc="Why the company exists beyond making money.",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 16,
          subtitle="Big Hairy Audacious Goal",
          desc="A 10-to-30-year goal with no numbers — just a destination.",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("QHAG + Sprint Lanes", "✓", "symbol-confirm", 3, 19,
          desc="Sprint lane status check.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 21,
          desc="Eight meetings at six frequencies.",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 23,
          desc="Quick scan of the values-performance chart.",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Org Function Chart", "▲", "symbol-evolution", 5, 28,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Evolving with KFFM refinement"]),
        D("KFFM", "▲", "symbol-evolution", 5, 33,
          subtitle="Key Function Flow Map",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Continue defining widgets and handoffs between functions"]),
        D("Functional Accountability Chart", "▲", "symbol-evolution", 4, 37,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Sharpen critical numbers as KFFM matures"]),
        D("Profit/X", "▲", "symbol-evolution", 4, 41,
          subtitle="The one unit of measurement that captures how the company makes money",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Refine with accumulating data"]),
        D("Core Values", "▲", "symbol-evolution", 5, 46,
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values",
          points=[
              "Continue pressure testing candidate values",
              "Each faces ten systematic tests including custom crisis scenarios",
          ]),
        D("Function Scorecards", "★", "symbol-introduced", 30, 76,
          article="https://www.darlison.com/scoreboard-day/",
          image_key="scorecards",
          points=[
              "One-page view per function: role purpose, key accountabilities, critical numbers, values expected",
              "CEO creates the first one (Head of Company) as the model",
              "Scoreboard Day: once per week, same day, all critical numbers updated by 10 AM",
              "Every red number triggers a written Situation Report: Situation, Cause, Correction, Follow-up",
              "Causes must be structural (capacity, policies, incentives) — never motivation",
          ]),
        D("Activity Fit Map", "★", "symbol-introduced", 27, 103,
          subtitle="Differentiators",
          points=[
              "From Attribution Map white space, determine 3-5 interdependent Differentiating Actions",
              "Draw connections showing dependencies (Activity Fit Map Level I) — Porter's framework",
              "If a competitor copies any single action, it shouldn't upend your position — interdependence is the key",
              "Level II adds supporting tactical activities around each differentiator",
              "Distill into a One-Phrase Strategy that ties all differentiating actions together",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize Function Scorecards and Activity Fit Map",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M6", [
            ("Swimlanes ★", None, None),
        ]),
        ("Books for Month 6", "books"),
    ],
    "homework_books": [
        ("The Four Obsessions of an Extraordinary Executive", "Patrick Lencioni", "https://www.amazon.ca/dp/0787954039"),
        ("Mastering the Rockefeller Habits", "Verne Harnish", "https://www.amazon.ca/dp/0978774957"),
    ],
}

# ── M6 ────────────────────────────────────────────────────────────────
MEETINGS[6] = {
    "num": 6,
    "title": "Monthly Meeting Six",
    "subtitle": "Building the Machine — Swimlanes, Sprint Reset, and Team Evolution",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("3HAG", "✓", "symbol-confirm", 2, 14,
          subtitle="3-Year Highly Achievable Goal",
          desc="Quick alignment: still on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("1HAG", "✓", "symbol-confirm", 2, 16,
          subtitle="1-Year Highly Achievable Goal",
          desc="Quick alignment.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("Org Function Chart", "▲", "symbol-evolution", 5, 21,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Final Q2 refinement before quarterly freeze"]),
        D("KFFM", "▲", "symbol-evolution", 5, 26,
          subtitle="Key Function Flow Map",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["End of Q2 maturity push — Level 1 should be solid"]),
        D("Functional Accountability Chart", "▲", "symbol-evolution", 4, 30,
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Critical numbers refined after 6 months of data"]),
        D("Profit/X", "▲", "symbol-evolution", 4, 34,
          subtitle="The one unit of measurement that captures how the company makes money",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Half a year of data — does the chosen unit still hold?"]),
        D("Core Values", "▲", "symbol-evolution", 5, 39,
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values",
          points=[
              "Values confirmed and locked at this meeting",
              "No more discovery — these are the 3-5 non-negotiables",
          ]),
        D("A-Player Team Assessment", "▲", "symbol-evolution", 10, 49,
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer",
          points=[
              "Significant evolution: Core Values now confirmed",
              "Full leadership team runs the assessment with values axis in place",
              "Not just CEO gut feel anymore — the whole team owns this conversation",
          ]),
        D("QHAG + Sprint Lanes", "■", "symbol-rebuilt", 18, 67,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=[
              "Rebuilt from scratch — new quarter, fresh 90-day priorities",
              "3-5 priorities aligned to the 1HAG, each with an owner and metric",
              "Sprint Lanes: 13-week grid, one binary deliverable per priority per week",
          ]),
        D("Swimlanes", "★", "symbol-introduced", 36, 103,
          points=[
              "12-quarter grid: one row per differentiating action from the Activity Fit Map",
              "Each cell = the key milestone for that capability in that quarter",
              "Pull milestones from Activity Fit Map Level II — supporting circles become quarterly deliverables",
              "Look horizontally (progression over time) AND vertically (dependencies across lanes in same quarter)",
              "This is what connects strategy to execution quarter by quarter for 3 years",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize Swimlanes in Mural",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M7", [
            ("Quarterly Coaching Reviews ★", "https://www.darlison.com/coaching-framework/", None),
            ("Skip-Level Reviews ★", "https://www.darlison.com/skip-level-reviews/", None),
        ]),
    ],
}

# ── M7 ────────────────────────────────────────────────────────────────
MEETINGS[7] = {
    "num": 7,
    "title": "Monthly Meeting Seven",
    "subtitle": "The Coach Cascade — Reviews, Skip-Levels, and Scorecard Evolution",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 3, 15,
          desc="Quarterly check-in: are you measurably closer to your stated outcome?",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("QHAG + Sprint Lanes", "✓", "symbol-confirm", 3, 18,
          desc="On track for mid-quarter.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("KFFM", "▲", "symbol-evolution", 10, 28,
          subtitle="Key Function Flow Map",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Push toward Level 2: zoom into each function",
              "Handoffs between functions should now have defined widgets",
          ]),
        D("Function Scorecards", "▲", "symbol-evolution", 18, 46,
          article="https://www.darlison.com/scoreboard-day/",
          image_key="scorecards",
          points=[
              "Scorecards become the basis for quarterly coaching reviews",
              "Each leader reviews their scorecard — are critical numbers, accountabilities, and values sharp enough for a coaching conversation?",
              "Scoreboard Day rhythm should be established: weekly, same day, by 10 AM",
          ]),
        D("Quarterly Coaching Reviews", "★", "symbol-introduced", 30, 76,
          article="https://www.darlison.com/coaching-framework/",
          image_key="coaching",
          points=[
              "90-day two-way conversation based on the function scorecard",
              "Not a top-down annual review — both sides give and receive feedback",
              "W.A.I.T. (Why Am I Talking?) — prioritize listening",
              "Question Funnel: broad exploration through five dimensions to specific action",
              "Feedback Model: What went well? What was tricky? What would you do differently?",
          ]),
        D("Skip-Level Reviews", "★", "symbol-introduced", 27, 103,
          article="https://www.darlison.com/skip-level-reviews/",
          image_key="skiplevel",
          points=[
              "CEO talks directly with people one level below leaders",
              "Five pre-meeting questions: keep/stop/start doing, team struggles, what would you do differently?",
              "Feedback attributed to the team, not individuals — distill into ONE improvement focus",
              "Schedule one month before the manager's own quarterly review so findings feed in",
              "Applies to all managers including the CEO — ideally conducted by an external coach",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "CEO conducts first quarterly coaching review with one leader",
            "Schedule skip-level reviews for the quarter",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M8", [
            ("12-Month Widget-Based Forecast ★", None, None),
            ("Positioning Statement ★", None, None),
            ("Value Proposition ★", None, None),
        ]),
    ],
}

# ── M8 ────────────────────────────────────────────────────────────────
MEETINGS[8] = {
    "num": 8,
    "title": "Monthly Meeting Eight",
    "subtitle": "Numbers Tell the Story — Forecasting, Positioning, and Market Advantage",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("QHAG + Sprint Lanes", "✓", "symbol-confirm", 3, 15,
          desc="Mid-quarter sprint check.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("Activity Fit Map", "✓", "symbol-confirm", 3, 18,
          subtitle="Differentiators",
          desc="Quick alignment: differentiators still hold?"),
        D("KFFM", "▲", "symbol-evolution", 10, 28,
          subtitle="Key Function Flow Map",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=[
              "Level 2 development continues",
              "Each function's internal widget flow getting defined",
          ]),
        D("Swimlanes", "▲", "symbol-evolution", 14, 42,
          points=[
              "Functional view added: each department sees their piece of the 12-quarter grid",
              "Review horizontal progression and vertical dependencies",
          ]),
        D("12-Month Widget-Based Forecast", "★", "symbol-introduced", 25, 67,
          points=[
              "A P&L forecast built on widgets, not top-down revenue guesses",
              "Finance builds the model, leaders own their function's widget assumptions",
              "Forecast widgets first, then layer in fiscal assumptions — never start with dollars",
              "This shifts forecast ownership from finance to the people who control the numbers",
          ]),
        D("Positioning Statement", "★", "symbol-introduced", 19, 86,
          subtitle="Moore's Format",
          points=[
              "Geoffrey Moore's Crossing the Chasm format: For [target customer] who [need], our [product] is a [category] that [key benefit], unlike [alternatives]",
              "Takes all strategic work to date and formats it into one confident, repeatable statement",
              "Working through it will surface gaps in the strategy — that's the point",
              "Introduced now because the team needs a full year of strategic picture-building first",
          ]),
        D("Value Proposition", "★", "symbol-introduced", 17, 103,
          subtitle="Moore's Format",
          points=[
              "The value exchange: what the customer gets and why it's worth the price",
              "Paired with the Positioning Statement: Positioning says where you play, Value Proposition says why customers buy",
              "A living artifact — revisited and refined as strategy validation continues",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize forecast model, Positioning Statement, and Value Proposition",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M9", [
            ("Monthly Forecast Review ★", None, None),
            ("Strategy Confirmation ★", None, None),
            ("36-Month Rolling Forecast ★", None, None),
        ]),
        ("Books for Month 9", "books"),
    ],
    "homework_books": [
        ("Overcoming the Five Dysfunctions of a Team", "Patrick Lencioni", "https://www.amazon.ca/dp/0787976377"),
        ("The Metronome Effect", "Shannon Susko", "https://www.amazon.ca/dp/1599325446"),
    ],
}

# ── M9 ────────────────────────────────────────────────────────────────
MEETINGS[9] = {
    "num": 9,
    "title": "Monthly Meeting Nine",
    "subtitle": "Strategy Under the Microscope — Confirmation, Forecasting, and the Road Ahead",
    "fixed_hw_time": 10,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("A-Player Team Assessment", "✓", "symbol-confirm", 3, 15,
          desc="Quick scan with confirmed values axis.",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("QHAG + Sprint Lanes", "■", "symbol-rebuilt", 20, 35,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=[
              "Rebuilt from scratch — new quarter, fresh 90-day priorities",
              "3-5 priorities aligned to the 1HAG",
              "Sprint Lanes: 13-week grid with one binary deliverable per priority per week",
          ]),
        D("Monthly Forecast Review", "★", "symbol-introduced", 25, 60,
          points=[
              "Recurring monthly meeting, max one hour, with the leadership team",
              "Compare three numbers: actuals, rolling forecast (evolves monthly), and original approved forecast (stays static)",
              "Leaders adjust the rolling forecast to align with the approved — never change the approved itself",
              "Five benefits: leaders own forecasts, clear visibility, improved accuracy, forward visibility, collective forecasting skill",
          ]),
        D("Strategy Confirmation", "★", "symbol-introduced", 25, 85,
          points=[
              "Progressive series of validation exercises, each adding a different strategic picture",
              "Business Model Canvas (Osterwalder): maps how you create, deliver, and capture value",
              "Porter's Five Forces: assesses industry profitability through five lenses",
              "Business model innovation is the most valuable area of innovation — not product or technology",
          ]),
        D("36-Month Rolling Forecast", "★", "symbol-introduced", 20, 105,
          points=[
              "Extends the 12-month widget forecast to 36 months",
              "Three columns per month: Approved (locked), Rolling (evolves), Actual",
              "Add another month to the end each month — always see 36 months ahead",
              "Replace the word 'budget' forever — a budget is a license to spend",
              "Also build a 12-Quarter Functional Org Chart showing FTEs per function per quarter",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize forecast extensions",
            "Conduct first Monthly Forecast Review",
            "Begin Strategy Confirmation exercises",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M10", [
            ("Flywheel ★", None, None),
        ]),
    ],
}

# ── M10 ───────────────────────────────────────────────────────────────
MEETINGS[10] = {
    "num": 10,
    "title": "Monthly Meeting Ten",
    "subtitle": "Year Two Begins — Rebuild, Refine, and Accelerate",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 2, 14,
          desc="Quarterly check-in.",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("Org Function Chart", "✓", "symbol-confirm", 2, 16,
          desc="Quick alignment.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 18,
          desc="Quick alignment.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm"),
        D("Core Values", "✓", "symbol-confirm", 2, 20,
          desc="Confirmed and locked.",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("QHAG + Sprint Lanes", "✓", "symbol-confirm", 2, 22,
          desc="Quick alignment.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("Core Customer Analysis", "✓", "symbol-confirm", 2, 24,
          desc="Still the right customer profile?"),
        D("Market Map", "✓", "symbol-confirm", 2, 26,
          desc="Quick alignment."),
        D("Quarterly Coaching Reviews", "✓", "symbol-confirm", 2, 28,
          desc="Reviews running smoothly?",
          article="https://www.darlison.com/coaching-framework/",
          image_key="coaching"),
        D("Strategy Confirmation", "✓", "symbol-confirm", 2, 30,
          desc="Strategic pictures validated?"),
        D("Profit/X", "▲", "symbol-evolution", 5, 35,
          subtitle="The one unit of measurement that captures how the company makes money",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm",
          points=["Hedgehog Concept evolution: now connected to Core Purpose, core business, and economic engine"]),
        D("Core Purpose", "▲", "symbol-evolution", 5, 40,
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose",
          points=["Annual validation using Simon Sinek's Golden Circle (What/How/Why)"]),
        D("BHAG", "▲", "symbol-evolution", 5, 45,
          subtitle="Big Hairy Audacious Goal",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose",
          points=["Deepened using Collins's Hedgehog Concept: best at, passionate about, economic engine"]),
        D("Function Scorecards", "▲", "symbol-evolution", 5, 50,
          article="https://www.darlison.com/scoreboard-day/",
          image_key="scorecards",
          points=["Leaders now create scorecards for every subfunction, aligned to KFFM Level 2"]),
        D("3HAG", "■", "symbol-rebuilt", 12, 62,
          subtitle="3-Year Highly Achievable Goal",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=[
              "Rebuilt from scratch — don't consult last year's version",
              "Force fresh thinking on fiscal targets, capabilities, and widgets",
          ]),
        D("1HAG", "■", "symbol-rebuilt", 10, 72,
          subtitle="1-Year Highly Achievable Goal",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=["Rebuilt: new year, new 3-5 corporate priorities"]),
        D("Attribution Map", "■", "symbol-rebuilt", 8, 80,
          points=[
              "Rebuilt from scratch to prevent anchoring on old assumptions",
              "Re-rank all attributes for your company and competitors",
          ]),
        D("Activity Fit Map", "■", "symbol-rebuilt", 8, 88,
          subtitle="Differentiators",
          points=["Rebuilt: re-derive 3-5 differentiators from the fresh Attribution Map"]),
        D("Swimlanes", "■", "symbol-rebuilt", 8, 96,
          points=["Rebuilt alongside new differentiators — fresh 12-quarter grid"]),
        D("Flywheel", "★", "symbol-introduced", 7, 103,
          points=[
              "Jim Collins: the greatest companies became great through relentless grit, push by push",
              "Map the architecture of key components that build momentum",
              "Color-rate each component (red/yellow/green) and overlay against the KFFM",
              "Gaps between Flywheel and KFFM reveal where momentum is stuck",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize all rebuilt artifacts in Mural and Metronome",
            "Activate new sprint lanes",
            "Leaders begin creating sub-function scorecards",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M11", [
            ("Brand Promise with Guarantee ★", None, None),
        ]),
    ],
}

# ── M11 ───────────────────────────────────────────────────────────────
MEETINGS[11] = {
    "num": 11,
    "title": "Monthly Meeting Eleven",
    "subtitle": "Momentum and Promise — Building the Brand from the Inside Out",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("KFFM", "✓", "symbol-confirm", 3, 15,
          subtitle="Key Function Flow Map",
          desc="Quick alignment.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm"),
        D("QHAG + Sprint Lanes", "✓", "symbol-confirm", 3, 18,
          desc="Sprint status check.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("Meeting Cadence", "✓", "symbol-confirm", 3, 21,
          desc="All meetings running?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("Monthly Forecast Review", "✓", "symbol-confirm", 3, 24,
          desc="Actuals vs. rolling vs. approved."),
        D("Positioning Statement", "✓", "symbol-confirm", 3, 27,
          subtitle="Moore's Format",
          desc="Still confident in the statement?"),
        D("Value Proposition", "✓", "symbol-confirm", 3, 30,
          subtitle="Moore's Format",
          desc="Still the right value exchange?"),
        D("Skip-Level Reviews", "✓", "symbol-confirm", 3, 33,
          desc="Reviews on schedule?",
          article="https://www.darlison.com/skip-level-reviews/",
          image_key="skiplevel"),
        D("Flywheel", "▲", "symbol-evolution", 25, 58,
          points=[
              "Color-rate each flywheel component against actuals",
              "Overlay with KFFM — should be full overlap between flywheel components and widget metrics",
              "Misalignments reveal where momentum is stuck",
              "Review component ratings quarterly from now on",
          ]),
        D("Brand Promise with Guarantee", "★", "symbol-introduced", 45, 103,
          points=[
              "A differentiated brand promise addresses the greatest need of your Core Customer",
              "The guarantee is the 'hurt' — what the company will suffer if it fails to deliver",
              "Collins calls the guarantee a 'catalytic mechanism' — aligns the entire team by putting real stakes on performance",
              "Test against four questions: Does it attract? Do competitors think you're crazy? Does it matter to the Core Customer? Does it differentiate instantly?",
              "Draft from Core Customer's top needs and Activity Fit Map, then test with friendly existing customers",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Draft Brand Promise options",
            "Test with 2-3 friendly Core Customers",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M12", [
            ("Secret Sauce ★", None, None),
        ]),
        ("Books for Month 12", "books"),
    ],
    "homework_books": [
        ("Beyond Entrepreneurship 2.0", "Jim Collins & Bill Lazier", "https://www.amazon.ca/dp/0399564233"),
    ],
}

# ── M12 ───────────────────────────────────────────────────────────────
MEETINGS[12] = {
    "num": 12,
    "title": "Monthly Meeting Twelve",
    "subtitle": "The Secret Advantage — Discovering What No One Else Will Solve",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("A-Player Team Assessment", "✓", "symbol-confirm", 3, 15,
          desc="Quick scan.",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Flywheel", "✓", "symbol-confirm", 3, 18,
          desc="Quick alignment on component ratings."),
        D("36-Month Rolling Forecast", "✓", "symbol-confirm", 3, 21,
          desc="Forecast-to-actual tracking."),
        D("QHAG + Sprint Lanes", "■", "symbol-rebuilt", 22, 43,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning",
          points=[
              "Rebuilt from scratch — new quarter, fresh 90-day priorities",
              "3-5 priorities aligned to the 1HAG",
          ]),
        D("Brand Promise with Guarantee", "▲", "symbol-evolution", 20, 63,
          points=[
              "Review market validation results from customer testing",
              "Refine the promise based on feedback",
              "Begin locking the specific guarantee — what exactly will you suffer if you don't deliver?",
          ]),
        D("Secret Sauce", "★", "symbol-introduced", 40, 103,
          points=[
              "Your unique tenfold advantage — the problem you solve that no one else wants to solve",
              "Look externally at industry pain points (conferences are a goldmine for unsolved problems)",
              "Look internally at your own processes for improvement opportunities",
              "Unlike strategy (which you share openly), Secret Sauce stays confidential",
              "If competitors figure it out, start looking for the next one immediately",
              "Make it a standing agenda item — may take months or years to find",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Continue Secret Sauce discussion at every strategy meeting",
            "Finalize Brand Promise guarantee",
        ]),
        ("Read Ahead", [
            "Prepare for full system review",
        ]),
    ],
}

# ── M13 ───────────────────────────────────────────────────────────────
MEETINGS[13] = {
    "num": 13,
    "title": "Monthly Meeting Thirteen",
    "subtitle": "Full System Review — Eighteen Months of Compounding Growth",
    "fixed_hw_time": 12,
    "fixed_hw_cum": 115,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 2, 14,
          desc="Quarterly check-in.",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("Org Function Chart", "✓", "symbol-confirm", 2, 16,
          desc="Quick alignment.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm"),
        D("Profit/X", "✓", "symbol-confirm", 2, 18,
          desc="Still the right unit.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="kffm"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 20,
          desc="Still resonating?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 22,
          subtitle="Big Hairy Audacious Goal",
          desc="Still pointing the right direction?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("3HAG", "✓", "symbol-confirm", 2, 24,
          subtitle="3-Year Highly Achievable Goal",
          desc="On track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("1HAG", "✓", "symbol-confirm", 2, 26,
          subtitle="1-Year Highly Achievable Goal",
          desc="On track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("QHAG + Sprint Lanes", "✓", "symbol-confirm", 2, 28,
          desc="Sprint status.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="planning"),
        D("Core Customer Analysis", "✓", "symbol-confirm", 2, 30,
          desc="Still the right customer?"),
        D("Market Map", "✓", "symbol-confirm", 2, 32,
          desc="Any market shifts?"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 34,
          desc="Numbers updating weekly?",
          article="https://www.darlison.com/scoreboard-day/",
          image_key="scorecards"),
        D("Attribution Map", "✓", "symbol-confirm", 2, 36,
          desc="Still differentiated?"),
        D("Activity Fit Map", "✓", "symbol-confirm", 2, 38,
          subtitle="Differentiators",
          desc="Still interdependent?"),
        D("12-Month Widget-Based Forecast", "✓", "symbol-confirm", 2, 40,
          desc="Tracking to plan?"),
        D("Swimlanes", "✓", "symbol-confirm", 2, 42,
          desc="On track by quarter?"),
        D("Monthly Forecast Review", "✓", "symbol-confirm", 2, 44,
          desc="Running smoothly?"),
        D("Brand Promise with Guarantee", "✓", "symbol-confirm", 2, 46,
          desc="Promise validated?"),
        D("Secret Sauce", "✓", "symbol-confirm", 2, 48,
          desc="Any new leads?"),
        D("Flywheel", "✓", "symbol-confirm", 2, 50,
          desc="Momentum building?"),
        D("Quarterly Coaching Reviews", "▲", "symbol-evolution", 25, 75,
          article="https://www.darlison.com/coaching-framework/",
          image_key="coaching",
          points=[
              "Leaders now cascade coaching reviews to THEIR team members",
              "Same format: 90-day two-way conversation based on scorecards",
              "This is the moment the coaching culture spreads beyond the leadership team",
          ]),
        D("Strategy Confirmation", "▲", "symbol-evolution", 28, 103,
          points=[
              "Add Consumption Chain Mapping (McGrath): map the Core Customer's entire experience",
              "Highlights friction points and validates strategy-execution alignment",
              "Forces immediate action on gaps",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Leaders conduct first cascaded coaching reviews",
            "Complete Consumption Chain Map",
        ]),
        ("Read Ahead", [
            "Prepare for Year 2 annual planning",
        ]),
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# HTML GENERATION
# ═══════════════════════════════════════════════════════════════════════

def e(text):
    """HTML-escape a string."""
    return html_mod.escape(text, quote=True)


def build_css():
    """Return the full CSS block (copied verbatim from M2 + symbol-rebuilt)."""
    return """        /* ===========================================
           CSS CUSTOM PROPERTIES (THEME)
           Brand: Blue #326AB5, Green #54B570
           =========================================== */
        :root {
            /* Colors */
            --bg-primary: #FAFAFA;
            --bg-white: #FFFFFF;
            --text-primary: #1a1a1a;
            --text-secondary: #555555;
            --text-muted: #999999;
            --accent-blue: #326AB5;
            --accent-green: #54B570;
            --accent-green-light: #f5faf6;
            --accent-green-border: #dceee0;
            --accent-green-text: #54B570;
            --border-light: #e8e8e8;

            /* Typography */
            --font-main: 'IBM Plex Sans', sans-serif;
            --title-size: clamp(1.75rem, 3.5vw, 2.5rem);
            --h2-size: clamp(1.375rem, 2.5vw, 1.875rem);
            --h3-size: clamp(1.125rem, 1.8vw, 1.5rem);
            --body-size: clamp(1rem, 1.5vw, 1.25rem);
            --small-size: clamp(0.875rem, 1.2vw, 1.0625rem);

            /* Spacing */
            --slide-padding: clamp(2rem, 5vw, 5rem);
            --content-gap: clamp(0.75rem, 2vw, 1.5rem);
            --element-gap: clamp(0.25rem, 1vw, 0.75rem);

            /* Animation */
            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
            --duration-normal: 0.6s;
        }

        /* ===========================================
           RESET
           =========================================== */
        * { margin: 0; padding: 0; box-sizing: border-box; }

        /* ===========================================
           VIEWPORT FITTING: MANDATORY BASE STYLES
           =========================================== */
        html, body {
            height: 100%;
            overflow-x: hidden;
            font-family: var(--font-main);
            color: var(--text-primary);
            background: var(--bg-primary);
        }

        html {
            scroll-snap-type: y mandatory;
            scroll-behavior: smooth;
        }

        .slide {
            width: 100vw;
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            position: relative;
            background: var(--bg-white);
        }

        .slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            max-height: 100%;
            overflow: hidden;
            padding: var(--slide-padding);
            padding-left: clamp(3rem, 8vw, 8rem);
            padding-right: clamp(3rem, 8vw, 8rem);
        }

        .card, .container, .content-box {
            max-width: min(90vw, 1000px);
            max-height: min(80vh, 700px);
        }

        .feature-list, .bullet-list {
            gap: clamp(0.4rem, 1vh, 1rem);
        }

        .feature-list li, .bullet-list li {
            font-size: var(--body-size);
            line-height: 1.4;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
            gap: clamp(0.5rem, 1.5vw, 1rem);
        }

        img, .image-container {
            max-width: 100%;
            max-height: min(50vh, 400px);
            object-fit: contain;
        }

        /* ===========================================
           RESPONSIVE BREAKPOINTS
           =========================================== */
        @media (max-height: 700px) {
            :root {
                --slide-padding: clamp(0.75rem, 3vw, 2rem);
                --content-gap: clamp(0.4rem, 1.5vw, 1rem);
                --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
                --h2-size: clamp(1rem, 3vw, 1.75rem);
            }
        }

        @media (max-height: 600px) {
            :root {
                --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
                --content-gap: clamp(0.3rem, 1vw, 0.75rem);
                --title-size: clamp(1.1rem, 4vw, 2rem);
                --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
            }
            .nav-dots, .keyboard-hint, .decorative {
                display: none;
            }
        }

        @media (max-height: 500px) {
            :root {
                --slide-padding: clamp(0.4rem, 2vw, 1rem);
                --title-size: clamp(1rem, 3.5vw, 1.5rem);
                --h2-size: clamp(0.9rem, 2.5vw, 1.25rem);
                --body-size: clamp(0.65rem, 1vw, 0.85rem);
            }
        }

        @media (max-width: 600px) {
            :root {
                --title-size: clamp(1.25rem, 7vw, 2.5rem);
            }
            .grid { grid-template-columns: 1fr; }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.2s !important;
            }
            html { scroll-behavior: auto; }
        }

        /* ===========================================
           SLIDE DESIGN SYSTEM
           =========================================== */

        /* --- Top accent bar --- */
        .slide::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-blue) 60%, var(--accent-green) 60%);
        }

        /* --- Slide titles --- */
        .slide-title {
            font-size: var(--title-size);
            font-weight: 700;
            color: var(--accent-blue);
            letter-spacing: -0.02em;
            line-height: 1.15;
            margin-bottom: var(--content-gap);
        }

        .slide-subtitle {
            font-size: var(--h3-size);
            font-weight: 400;
            color: var(--text-secondary);
            margin-bottom: var(--content-gap);
        }

        /* --- Symbol badges --- */
        .symbol-badge {
            display: inline-flex;
            align-items: center;
            gap: clamp(4px, 0.5vw, 8px);
            font-size: var(--small-size);
            font-weight: 600;
            padding: clamp(2px, 0.3vw, 4px) clamp(8px, 1vw, 14px);
            border-radius: 4px;
            margin-bottom: var(--content-gap);
        }

        .symbol-introduced {
            color: var(--accent-blue);
            background: rgba(50, 106, 181, 0.08);
            border: 1px solid rgba(50, 106, 181, 0.2);
        }

        .symbol-evolution {
            color: #b5832a;
            background: rgba(181, 131, 42, 0.08);
            border: 1px solid rgba(181, 131, 42, 0.2);
        }

        .symbol-confirm {
            color: var(--text-secondary);
            background: rgba(102, 102, 102, 0.08);
            border: 1px solid rgba(102, 102, 102, 0.2);
        }

        .symbol-rebuilt {
            color: #b53232;
            background: rgba(181, 50, 50, 0.08);
            border: 1px solid rgba(181, 50, 50, 0.2);
        }

        /* --- Bullet lists --- */
        .talking-points {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: clamp(0.5rem, 1.2vh, 1rem);
            margin-bottom: var(--content-gap);
        }

        .talking-points li {
            font-size: var(--body-size);
            line-height: 1.5;
            color: var(--text-primary);
            padding-left: clamp(1rem, 2vw, 1.5rem);
            position: relative;
        }

        .talking-points li::before {
            content: '';
            position: absolute;
            left: 0;
            top: clamp(6px, 0.8vh, 10px);
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
        }

        /* --- Link buttons --- */
        .slide-links {
            display: flex;
            gap: clamp(6px, 1vw, 12px);
            align-items: center;
            flex-wrap: wrap;
            margin-top: auto;
            padding-top: var(--content-gap);
        }

        .link-article {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: var(--small-size);
            font-weight: 500;
            color: var(--accent-blue);
            text-decoration: none;
            padding: clamp(3px, 0.4vw, 6px) clamp(10px, 1.2vw, 16px);
            background: rgba(50, 106, 181, 0.06);
            border: 2px solid rgba(50, 106, 181, 0.25);
            border-radius: 4px;
            transition: background 0.2s, border-color 0.2s;
        }

        .link-article:hover {
            background: rgba(50, 106, 181, 0.12);
            border-color: var(--accent-blue);
        }

        .link-prompt {
            display: inline-flex;
            align-items: center;
            gap: 3px;
            font-size: var(--small-size);
            font-weight: 600;
            color: var(--accent-green-text);
            background: var(--accent-green-light);
            border: 2px solid var(--accent-green-border);
            border-radius: 3px;
            padding: clamp(3px, 0.4vw, 6px) clamp(8px, 1vw, 14px);
            text-decoration: none;
            cursor: pointer;
            white-space: nowrap;
            transition: background 0.2s, border-color 0.2s;
        }

        .link-prompt:hover {
            background: #edf7ef;
            border-color: var(--accent-green);
        }

        /* --- Footer branding --- */
        .slide-footer {
            position: absolute;
            bottom: clamp(12px, 2vh, 24px);
            left: clamp(16px, 3vw, 32px);
            font-size: var(--small-size);
            font-weight: 400;
            color: var(--text-muted);
        }

        /* --- Time indicator --- */
        .time-indicator {
            position: absolute;
            bottom: clamp(12px, 2vh, 24px);
            right: clamp(16px, 3vw, 32px);
            font-size: var(--small-size);
            font-weight: 500;
            color: var(--text-muted);
            font-variant-numeric: tabular-nums;
        }

        /* --- Two-column layout for deliverable slides --- */
        .two-col {
            display: grid;
            grid-template-columns: 3fr 2fr;
            gap: clamp(1.5rem, 3vw, 3rem);
            align-items: center;
            flex: 1;
        }

        .two-col .col-text {
            display: flex;
            flex-direction: column;
        }

        .two-col .col-image {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .two-col .col-image img {
            max-height: min(45vh, 380px);
            border-radius: 8px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
        }

        @media (max-width: 900px) {
            .two-col {
                grid-template-columns: 1fr;
            }
            .two-col .col-image {
                display: none;
            }
        }

        /* --- Rules of Engagement --- */
        .rules-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: clamp(0.6rem, 1.5vh, 1.2rem);
        }

        .rules-list li {
            font-size: var(--body-size);
            line-height: 1.5;
            color: var(--text-primary);
            display: flex;
            align-items: flex-start;
            gap: clamp(8px, 1vw, 14px);
        }

        .rule-icon {
            flex-shrink: 0;
            width: clamp(18px, 2vw, 24px);
            height: clamp(18px, 2vw, 24px);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 2px;
        }

        .rule-icon svg {
            width: 100%;
            height: 100%;
        }

        /* --- Reading list --- */
        .book-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: clamp(0.6rem, 1.5vh, 1.2rem);
        }

        .book-list li a {
            font-size: var(--body-size);
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 500;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }

        .book-list li a:hover {
            border-bottom-color: var(--accent-blue);
        }

        .book-list li .book-author {
            color: var(--text-secondary);
            font-weight: 400;
        }

        /* --- Homework sections --- */
        .homework-section {
            margin-bottom: clamp(0.8rem, 1.5vh, 1.2rem);
        }

        .homework-section h3 {
            font-size: var(--h3-size);
            font-weight: 600;
            color: #333333;
            margin-bottom: clamp(0.3rem, 0.8vh, 0.6rem);
        }

        .homework-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: clamp(0.3rem, 0.8vh, 0.6rem);
        }

        .homework-list li {
            font-size: var(--body-size);
            line-height: 1.5;
            color: var(--text-primary);
            padding-left: clamp(0.8rem, 1.5vw, 1.2rem);
            position: relative;
        }

        .homework-list li::before {
            content: '';
            position: absolute;
            left: 0;
            top: clamp(5px, 0.7vh, 8px);
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
        }

        .homework-list a {
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 500;
        }

        .homework-list a:hover {
            text-decoration: underline;
        }

        .homework-list .link-prompt {
            font-size: clamp(0.65rem, 1vw, 0.85rem);
            padding: 1px 6px;
            vertical-align: middle;
            margin-left: 4px;
        }

        /* --- Close slide --- */
        .close-question {
            font-size: var(--h2-size);
            font-weight: 400;
            color: var(--text-secondary);
            margin-top: var(--element-gap);
        }

        .close-instruction {
            font-size: var(--h3-size);
            font-weight: 500;
            color: var(--accent-green);
            margin-top: var(--content-gap);
        }

        /* ===========================================
           ANIMATIONS
           =========================================== */
        .reveal {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity var(--duration-normal) var(--ease-out-expo),
                        transform var(--duration-normal) var(--ease-out-expo);
        }

        .slide.visible .reveal {
            opacity: 1;
            transform: translateY(0);
        }

        .reveal:nth-child(1) { transition-delay: 0.05s; }
        .reveal:nth-child(2) { transition-delay: 0.12s; }
        .reveal:nth-child(3) { transition-delay: 0.19s; }
        .reveal:nth-child(4) { transition-delay: 0.26s; }
        .reveal:nth-child(5) { transition-delay: 0.33s; }
        .reveal:nth-child(6) { transition-delay: 0.40s; }
        .reveal:nth-child(7) { transition-delay: 0.47s; }
        .reveal:nth-child(8) { transition-delay: 0.54s; }

        /* --- Progress bar --- */
        .progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: var(--accent-blue);
            z-index: 1000;
            transition: width 0.3s ease;
        }

        /* --- Nav dots --- */
        .nav-dots {
            position: fixed;
            right: clamp(12px, 2vw, 20px);
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 100;
        }

        .nav-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--border-light);
            border: none;
            cursor: pointer;
            transition: background 0.3s, transform 0.3s;
            padding: 0;
        }

        .nav-dot.active {
            background: var(--accent-blue);
            transform: scale(1.3);
        }

        .nav-dot:hover {
            background: var(--accent-green);
        }"""


def build_js():
    """Return the JS block (SlidePresentation class, verbatim from M2)."""
    return """    <script>
        class SlidePresentation {
            constructor() {
                this.slides = document.querySelectorAll('.slide');
                this.currentSlide = 0;
                this.isScrolling = false;

                this.setupIntersectionObserver();
                this.setupKeyboardNav();
                this.setupTouchNav();
                this.setupProgressBar();
                this.setupNavDots();
                this.setupWheelNav();
            }

            setupIntersectionObserver() {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('visible');
                            const idx = Array.from(this.slides).indexOf(entry.target);
                            if (idx !== -1) {
                                this.currentSlide = idx;
                                this.updateNavDots();
                                this.updateProgressBar();
                            }
                        }
                    });
                }, { threshold: 0.5 });

                this.slides.forEach(slide => observer.observe(slide));
            }

            setupKeyboardNav() {
                document.addEventListener('keydown', (e) => {
                    switch(e.key) {
                        case 'ArrowDown':
                        case 'ArrowRight':
                        case ' ':
                        case 'PageDown':
                            e.preventDefault();
                            this.goToSlide(this.currentSlide + 1);
                            break;
                        case 'ArrowUp':
                        case 'ArrowLeft':
                        case 'PageUp':
                            e.preventDefault();
                            this.goToSlide(this.currentSlide - 1);
                            break;
                        case 'Home':
                            e.preventDefault();
                            this.goToSlide(0);
                            break;
                        case 'End':
                            e.preventDefault();
                            this.goToSlide(this.slides.length - 1);
                            break;
                    }
                });
            }

            setupTouchNav() {
                let touchStartY = 0;
                document.addEventListener('touchstart', (e) => {
                    touchStartY = e.touches[0].clientY;
                }, { passive: true });

                document.addEventListener('touchend', (e) => {
                    const diff = touchStartY - e.changedTouches[0].clientY;
                    if (Math.abs(diff) > 50) {
                        if (diff > 0) this.goToSlide(this.currentSlide + 1);
                        else this.goToSlide(this.currentSlide - 1);
                    }
                }, { passive: true });
            }

            setupWheelNav() {
                document.addEventListener('wheel', (e) => {
                    if (this.isScrolling) return;
                    this.isScrolling = true;

                    if (e.deltaY > 0) this.goToSlide(this.currentSlide + 1);
                    else if (e.deltaY < 0) this.goToSlide(this.currentSlide - 1);

                    setTimeout(() => { this.isScrolling = false; }, 800);
                }, { passive: true });
            }

            setupProgressBar() {
                this.progressBar = document.getElementById('progressBar');
                this.updateProgressBar();
            }

            updateProgressBar() {
                if (!this.progressBar) return;
                const progress = ((this.currentSlide + 1) / this.slides.length) * 100;
                this.progressBar.style.width = progress + '%';
            }

            setupNavDots() {
                const nav = document.getElementById('navDots');
                if (!nav) return;

                this.slides.forEach((_, i) => {
                    const dot = document.createElement('button');
                    dot.className = 'nav-dot' + (i === 0 ? ' active' : '');
                    dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
                    dot.addEventListener('click', () => this.goToSlide(i));
                    nav.appendChild(dot);
                });
            }

            updateNavDots() {
                const dots = document.querySelectorAll('.nav-dot');
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active', i === this.currentSlide);
                });
            }

            goToSlide(index) {
                if (index < 0 || index >= this.slides.length) return;
                this.currentSlide = index;
                this.slides[index].scrollIntoView({ behavior: 'smooth' });
                this.updateNavDots();
                this.updateProgressBar();
            }
        }

        new SlidePresentation();
    </script>"""


# ─── Slide builders ──────────────────────────────────────────────────

FOOTER = '        <span class="slide-footer">darlison.com | Metronomics™ Coaching</span>'


def slide_title(meeting):
    n = meeting["num"]
    return f"""    <!-- SLIDE: TITLE -->
    <section class="slide" aria-label="{e(meeting['title'])}">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text" style="gap: clamp(0.75rem, 2vh, 1.5rem);">
                    <h1 class="slide-title reveal" style="font-size: clamp(2.25rem, 5vw, 3.5rem); letter-spacing: -0.03em;">{e(meeting['title'])}</h1>
                    <p class="slide-subtitle reveal">{e(meeting['subtitle'])}</p>
                    <hr class="reveal" style="width: clamp(60px, 10vw, 120px); height: 2px; background: var(--accent-green); border: none;">
                    <img class="reveal" src="../../shared/assets/metronomics-logo.svg" alt="Metronomics" style="max-width: clamp(160px, 20vw, 260px); height: auto;">
                    <span class="reveal" style="font-size: var(--body-size); font-weight: 500; color: var(--text-muted); letter-spacing: 0.02em;">darlison.com</span>
                </div>
                <div class="col-image reveal">
                    <img src="assets/title-m{n}.png" alt="{e(meeting['subtitle'])}">
                </div>
            </div>
        </div>
{FOOTER}
    </section>"""


def slide_good_news(cum):
    return f"""    <!-- SLIDE: GOOD NEWS -->
    <section class="slide" aria-label="Good News">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text" style="align-items: flex-start;">
                    <h1 class="slide-title reveal">Good News</h1>
                    <p class="slide-subtitle reveal" style="font-size: var(--h2-size); font-weight: 400;">
                        Positive. Professional. 5-10 seconds.
                    </p>
                </div>
                <div class="col-image reveal">
                    <img src="../../shared/assets/good-news.png" alt="Good News">
                </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">(5/{cum})</span>
    </section>"""


def slide_rules(cum):
    return f"""    <!-- SLIDE: RULES OF ENGAGEMENT -->
    <section class="slide" aria-label="Rules of Engagement">
        <div class="slide-content">
            <div class="two-col">
            <div class="col-text">
            <h1 class="slide-title reveal">Rules of Engagement</h1>
            <ul class="rules-list">
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M12 2L15 8.5L22 9.5L17 14.5L18 21.5L12 18.5L6 21.5L7 14.5L2 9.5L9 8.5Z"/></svg></span>
                    Challenge yourself. Challenge each other.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span>
                    Discussion and collaboration. Your best contribution.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></span>
                    Be present in the room.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></span>
                    No blame, no shame. No dumb questions.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg></span>
                    Don't ignore the brutal facts. Bring them forward.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></span>
                    Confidentiality. What happens here stays here.
                </li>
            </ul>
            </div>
            <div class="col-image reveal">
                <img src="../../shared/assets/rules-of-engagement.png" alt="Rules of Engagement">
            </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">(5/{cum})</span>
    </section>"""


def slide_reading(month, cum):
    books = reading_for(month)
    items = ""
    for title, author, url in books:
        items += f'                        <li class="reveal"><a href="{e(url)}" target="_blank" rel="noopener">{e(title)}</a> <span class="book-author">&mdash; {e(author)}</span></li>\n'
    return f"""    <!-- SLIDE: READING -->
    <section class="slide" aria-label="Reading">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text">
                    <h1 class="slide-title reveal">Reading</h1>
                    <ul class="book-list">
{items.rstrip()}
                    </ul>
                </div>
                <div class="col-image reveal">
                    <img src="../m1/assets/reading.png" alt="Reading list">
                </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">(2/{cum})</span>
    </section>"""


def badge_label(symbol):
    labels = {"★": "Introduced", "▲": "Evolution", "■": "Rebuilt", "✓": "Confirm"}
    return labels.get(symbol, "")


def slide_deliverable(d):
    """Build a single deliverable slide."""
    sym = d["symbol"]
    badge = d["badge"]
    label = badge_label(sym)
    has_image = d["image_key"] is not None
    img_url = IMG.get(d["image_key"], "") if d["image_key"] else ""

    # Build the text column content
    parts = []
    parts.append(f'                    <span class="symbol-badge {badge} reveal">{sym} {label}</span>')
    parts.append(f'                    <h1 class="slide-title reveal">{e(d["name"])}</h1>')

    if d["subtitle"]:
        parts.append(f'                    <p class="slide-subtitle reveal">{e(d["subtitle"])}</p>')

    # Confirm items: description only, no talking points
    if sym == "✓":
        if d["desc"]:
            parts.append(f'                    <p class="reveal" style="font-size: var(--body-size); color: var(--text-secondary);">')
            parts.append(f'                        {e(d["desc"])}')
            parts.append(f'                    </p>')
    else:
        # Talking points for non-confirm items
        if d["points"]:
            parts.append(f'                    <ul class="talking-points">')
            for pt in d["points"]:
                parts.append(f'                        <li class="reveal">{e(pt)}</li>')
            parts.append(f'                    </ul>')

    # Links
    has_links = d["article"] or d["prompt"]
    if has_links:
        link_parts = []
        if d["article"]:
            link_parts.append(f'                        <a href="{e(d["article"])}" target="_blank" rel="noopener" class="link-article">Article</a>')
        if d["prompt"]:
            link_parts.append(f'                        <a href="{e(d["prompt"])}" target="_blank" rel="noopener" class="link-prompt">&#10022; AI Prompt</a>')
        parts.append(f'                    <div class="slide-links reveal">')
        parts.extend(link_parts)
        parts.append(f'                    </div>')

    col_text = "\n".join(parts)

    if has_image:
        return f"""    <!-- SLIDE: {e(d["name"])} -->
    <section class="slide" aria-label="{e(d["name"])}">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text">
{col_text}
                </div>
                <div class="col-image reveal">
                    <img src="{e(img_url)}" alt="{e(d["name"])}">
                </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">({d["time"]}/{d["cumulative"]})</span>
    </section>"""
    else:
        return f"""    <!-- SLIDE: {e(d["name"])} -->
    <section class="slide" aria-label="{e(d["name"])}">
        <div class="slide-content">
            <div class="col-text">
{col_text}
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">({d["time"]}/{d["cumulative"]})</span>
    </section>"""


def slide_homework(meeting):
    hw_time = meeting["fixed_hw_time"]
    hw_cum = meeting["fixed_hw_cum"]
    sections = []
    for heading, items in meeting["homework"]:
        if items == "books":
            # Books section
            book_list = meeting.get("homework_books", [])
            book_items = ""
            for title, author, url in book_list:
                book_items += f'                    <li><a href="{e(url)}" target="_blank" rel="noopener">{e(title)}</a> <span style="color: var(--text-secondary);">&mdash; {e(author)}</span></li>\n'
            sections.append(f"""            <div class="homework-section reveal">
                <h3>{e(heading)}</h3>
                <ul class="homework-list">
{book_items.rstrip()}
                </ul>
            </div>""")
        else:
            li_items = ""
            for item in items:
                if isinstance(item, tuple):
                    name, article_url, prompt_url = item
                    li_content = ""
                    if article_url:
                        li_content += f'<a href="{e(article_url)}" target="_blank" rel="noopener">{e(name)}</a>'
                    else:
                        li_content += e(name)
                    if prompt_url:
                        li_content += f' <a href="{e(prompt_url)}" target="_blank" rel="noopener" class="link-prompt">&#10022; AI Prompt</a>'
                    li_items += f'                    <li>{li_content}</li>\n'
                else:
                    li_items += f'                    <li>{e(item)}</li>\n'
            sections.append(f"""            <div class="homework-section reveal">
                <h3>{e(heading)}</h3>
                <ul class="homework-list">
{li_items.rstrip()}
                </ul>
            </div>""")

    sections_html = "\n\n".join(sections)

    return f"""    <!-- SLIDE: HOMEWORK -->
    <section class="slide" aria-label="Homework">
        <div class="slide-content">
            <div class="two-col">
            <div class="col-text">
            <h1 class="slide-title reveal">Homework</h1>

{sections_html}
            </div>
            <div class="col-image reveal">
                <img src="../m1/assets/homework.png" alt="Homework and preparation">
            </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">({hw_time}/{hw_cum})</span>
    </section>"""


def slide_cascade(cum):
    return f"""    <!-- SLIDE: CASCADE 3 KEY MESSAGES -->
    <section class="slide" aria-label="Cascade 3 Key Messages">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text">
                    <h1 class="slide-title reveal">Cascade 3 Key Messages</h1>
                    <p class="close-instruction reveal">What are the 3 things your team needs to hear from this meeting?</p>
                    <p class="close-question reveal">Share them in tomorrow's huddle.</p>
                </div>
                <div class="col-image reveal">
                    <img src="../../shared/assets/cascade-3-key-messages.png" alt="Cascade 3 Key Messages">
                </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">(2/{cum})</span>
    </section>"""


def slide_close():
    return f"""    <!-- SLIDE: ONE-PHRASE CLOSE -->
    <section class="slide" aria-label="One-Phrase Close">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text">
                    <h1 class="slide-title reveal">One-Phrase Close</h1>
                    <p class="close-instruction reveal">5 words or less.</p>
                    <p class="close-question reveal">How do you feel right now?</p>
                </div>
                <div class="col-image reveal">
                    <img src="../../shared/assets/one-phrase-close.png" alt="One-Phrase Close">
                </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">(3/120)</span>
    </section>"""


def build_html(meeting):
    n = meeting["num"]
    title_text = f"M{n} &mdash; {e(meeting['title'])}"

    slides = []
    slides.append(slide_title(meeting))
    slides.append(slide_good_news(5))
    slides.append(slide_rules(10))
    slides.append(slide_reading(n, 12))

    for d in meeting["deliverables"]:
        slides.append(slide_deliverable(d))

    slides.append(slide_homework(meeting))
    slides.append(slide_cascade(117))
    slides.append(slide_close())

    slides_html = "\n\n".join(slides)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M{n} &mdash; {e(meeting['title'])}</title>

    <!-- Fonts: IBM Plex Sans from Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700&display=swap" rel="stylesheet">

    <style>
{build_css()}
    </style>
</head>
<body>

    <!-- Progress bar -->
    <div class="progress-bar" id="progressBar"></div>

    <!-- Navigation dots -->
    <nav class="nav-dots" id="navDots" aria-label="Slide navigation"></nav>

{slides_html}

    <!-- ===========================================
       SLIDE PRESENTATION CONTROLLER
       =========================================== -->
{build_js()}
</body>
</html>
"""


def main():
    for month_num in range(3, 14):
        meeting = MEETINGS[month_num]
        out_dir = os.path.join(MONTHLY_DIR, f"m{month_num}")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "index.html")
        content = build_html(meeting)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {out_path}")

    print("\nAll 11 slideshows generated successfully.")


if __name__ == "__main__":
    main()
