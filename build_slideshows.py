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
def _img(month):
    """Return a function that resolves image keys to paths relative to m{month}/."""
    prefix = "../../shared/assets/deliverables"
    # Article-sourced images (external URLs)
    base = {
        "kffm": "https://www.darlison.com/content/images/size/w1920/2026/03/key-function-flow-map-how-company-makes-money.png",
        "pillar_hr_kffm": "https://www.darlison.com/content/images/size/w1920/2026/04/pillar-hr-kffm-l1.png",
        "pillar_hr_foc": "https://www.darlison.com/content/images/size/w1920/2026/04/pillar-hr-foc.png",
        "pillar_hr_fac": "https://www.darlison.com/content/images/size/w1920/2026/04/pillar-hr-fac.png",
        "purpose": "https://www.darlison.com/content/images/size/w1200/2026/03/core-purpose-discovery-company-why.png",
        "planning": "https://www.darlison.com/content/images/size/w1200/2026/04/planning-cascade-3hag-weekly-execution.png",
        "meetings": "https://www.darlison.com/content/images/size/w1200/2026/03/eight-meetings-company-cadence-2.png",
        "aplayer": "https://www.darlison.com/content/images/size/w1200/2026/03/a-player-team-assessment-values-performance-scatter.png",
        "values": "https://www.darlison.com/content/images/size/w1200/2026/03/How-To-Disover-Company-Values.png",
        "scorecards": "https://www.darlison.com/content/images/size/w1200/2026/05/darlison-featured-scorecards-directive-management-20260503_090605.png",
        "coaching": "https://www.darlison.com/content/images/2026/02/The-Art-of-Mentorship--A-Framework-for-One-on-One-Coaching.png",
        "skiplevel": "https://www.darlison.com/content/images/size/w1200/2026/01/Skip-Level---cropped.png",
        "owner": "https://www.darlison.com/content/images/size/w1200/2026/03/Gemini_Generated_Image_c8oxcvc8oxcvc8ox.png",
        # Generated images for deliverables without articles
        "profit_x": f"{prefix}/profit-x.png",
        "three_hag": f"{prefix}/3hag.png",
        "one_hag": f"{prefix}/1hag.png",
        "q_hag": f"{prefix}/qhag.png",
        "market_map": f"{prefix}/market-map.png",
        "core_customer": f"{prefix}/core-customer.png",
        "attribution_map": f"{prefix}/attribution-map.png",
        "activity_fit": f"{prefix}/activity-fit-map.png",
        "swimlanes": f"{prefix}/swimlanes.png",
        "widget_forecast": f"{prefix}/widget-forecast.png",
        "positioning": f"{prefix}/positioning-statement.png",
        "value_prop": f"{prefix}/value-proposition.png",
        "monthly_forecast": f"{prefix}/monthly-forecast-review.png",
        "strategy_confirm": f"{prefix}/strategy-confirmation.png",
        "rolling_forecast": f"{prefix}/rolling-forecast-36.png",
        "flywheel": f"{prefix}/flywheel.png",
        "brand_promise": f"{prefix}/brand-promise.png",
        "secret_sauce": f"{prefix}/secret-sauce.png",
    }
    return base

IMG = _img(0)  # Same for all months since we use ../../shared/assets/ prefix

# ─── Book data ────────────────────────────────────────────────────────
BOOKS_PREKICKOFF = [
    ("Metronomics", "Shannon Susko", "https://www.amazon.ca/dp/1544521294"),
    ("The Five Dysfunctions of a Team", "Patrick Lencioni", "https://www.amazon.ca/dp/0787960756"),
    ("Start with Why", "Simon Sinek", "https://www.amazon.ca/dp/1591846447"),
]
BOOKS_M3 = [
    ("3HAG WAY", "Shannon Susko", "https://www.amazon.ca/3HAG-WAY-Strategic-Execution-Wild-Ass-Guess/dp/1790131235"),
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


# ─── Auto image key lookup by deliverable name ─────────────────────
_NAME_TO_IMAGE = {
    "Market Map": "market_map",
    "Core Customer Analysis": "core_customer",
    "Attribution Map": "attribution_map",
    "Activity Fit Map": "activity_fit",
    "Swimlanes": "swimlanes",
    "12-Month Widget-Based Forecast": "widget_forecast",
    "Positioning Statement": "positioning",
    "Value Proposition": "value_prop",
    "Monthly Forecast Review": "monthly_forecast",
    "Strategy Confirmation": "strategy_confirm",
    "36-Month Rolling Forecast": "rolling_forecast",
    "Flywheel": "flywheel",
    "Brand Promise with Guarantee": "brand_promise",
    "Secret Sauce": "secret_sauce",
}

# ─── Deliverable helper ──────────────────────────────────────────────
def D(name, symbol, badge, time, cumulative, subtitle=None, desc=None,
      points=None, article=None, prompt=None, image_key=None):
    """Create a deliverable dict. Auto-assigns image_key from name if not provided."""
    if image_key is None:
        image_key = _NAME_TO_IMAGE.get(name)
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
    "subtitle": "From Vision to Execution - Your First Planning Cascade",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 14,
          desc="Standing review: does the Level 1 flow still hold? Any new functions or consolidations since M2?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 3, 17,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 19,
          desc="Quick check: critical numbers still on the right widgets? Any thresholds that need adjusting?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 21,
          desc="Standing review: is the chosen X still the right unit, or is the data telling us something different?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "▲", "symbol-evolution", 8, 29,
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose",
          points=[
              "Read each draft together. What sentence keeps surfacing as 'this is us'?",
              "Test: would this still hold at 10x the size? At a quarter of it?",
              "Lock the working version - we'll confirm at every meeting from now on",
          ]),
        D("BHAG", "▲", "symbol-evolution", 6, 35,
          subtitle="Big Hairy Audacious Goal",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose",
          points=[
              "Compare drafts. Where's the convergence?",
              "Aspirational, not fantasy - 10-30 years out, no numbers",
              "A BHAG that's wrong-but-aligned beats no BHAG every time",
          ]),
        D("Meeting Cadence", "▲", "symbol-evolution", 7, 42,
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings",
          points=[
              "Daily Huddle - is it running? 90 seconds, good news, status only?",
              "Weekly Leadership Tactical - installed, with a real agenda?",
              "Time zones don't exempt anyone. Find the window",
          ]),
        D("3-Year Highly Achievable Goal (3HAG)", "★", "symbol-introduced", 22, 64,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag",
          points=[
              "Fiscal targets, cash, revenue, how many of X of profit/X",
              "What will the company be in 3 years? The statement.",
              "3 to 5 key capabilities",
              "What will you be known for?",
          ]),
        D("1-Year Highly Achievable Goal (1HAG)", "★", "symbol-introduced", 18, 82,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag",
          points=[
              "Fiscal targets, cash, revenue, how many of X of profit/X",
              "3-5 priorities that enable the 3HAG priorities and improve profit/X, 1 owner each",
          ]),
        D("QHAG + 13-Week Sprint Lanes", "★", "symbol-introduced", 23, 105,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag",
          points=[
              "Fiscal targets, cash, revenue, how many of X of profit/X",
              "3-5 priorities that enable the 1HAG priorities and improve profit/X, 1 owner each",
              "Each priority is delivered over a 13 week sprint lane, one binary deliverable per priority per week",
              "No gaps allowed - every week needs a milestone to prevent blind spots",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize 3HAG, 1HAG, QHAG + Sprint Lanes in Mural and Metronome Software",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M4", [
            ("Core Values ★", "https://www.darlison.com/how-to-discover-your-companys-values-using-ai", "https://www.darlison.com/values-discovery-prompt/"),
            ("A-Player Team Assessment ★", "https://www.darlison.com/a-player-team-assessment/", "https://www.darlison.com/a-player-team-assessment-prompt/"),
        ]),
    ],
}

# ── M4 ────────────────────────────────────────────────────────────────
MEETINGS[4] = {
    "num": 4,
    "title": "Monthly Meeting Four",
    "subtitle": "From Plan to People - Coach the Cascade, Build the Team",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 3, 15,
          desc="Anything shifted in what you want from the business?",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 17,
          desc="Any new functions or consolidations since M3?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 19,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 21,
          desc="Any new critical numbers? Thresholds still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 23,
          desc="Still the right unit, or has the data shifted?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 25,
          desc="Still 'this is us'? Any pull to refine?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 27,
          desc="Still feel right? Aspirational but not fantasy?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 29,
          desc="Daily Huddle and Weekly Tactical - still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "▲", "symbol-evolution", 12, 41,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag",
          points=[
              "Read each company's draft 3HAG out loud. Where did the language land?",
              "Are the 3 to 5 key capabilities concrete or fuzzy?",
              "Lock the 'what will you be known for?' answer for the next 90 days",
          ]),
        D("1-Year Highly Achievable Goal (1HAG)", "▲", "symbol-evolution", 10, 51,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag",
          points=[
              "Compare priorities to the 3HAG capabilities. Does each priority enable one?",
              "1 owner per priority. Shared ownership is no ownership",
              "Every priority has a measurable outcome",
          ]),
        D("QHAG + 13-Week Sprint Lanes", "▲", "symbol-evolution", 14, 65,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag",
          points=[
              "Sprint lanes drawn? 5 priorities by 13 weeks?",
              "Every cell has a binary deliverable - no 'in progress' allowed",
              "No gaps allowed - every week needs a milestone to prevent blind spots",
          ]),
        D("A-Player Team Assessment", "★", "symbol-introduced", 18, 83,
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer",
          points=[
              "Plot every direct report on two axes: values alignment by performance",
              "Color code A / B / C - count them, don't perfect them",
              "Gut-feel first version is the right move. Data comes later",
              "The A-players are the bench. Build around them",
          ]),
        D("Core Values", "★", "symbol-introduced", 22, 105,
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values",
          points=[
              "Run the 7-story AI prompt independently first - 60-90 minutes per founder",
              "Compare drafts and merge into a shared list of 5-8 candidates",
              "Pressure-test over the next 6-12 months. Real values reveal in tough decisions",
              "Not aspirational. Descriptive of how your best people already act",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize 3HAG, 1HAG, QHAG + Sprint Lanes drafts in Mural - the M3 introductions are now locked",
            "A-Player Team Assessment in Mural: every direct report plotted on the values × performance grid",
            "Core Values draft list of 5-8 candidates from the 7-story prompt - merged across both founders",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M5", [
            ("Function Scorecards ★", "https://www.darlison.com/scorecards/", "https://www.darlison.com/scorecards-tools/"),
        ]),
    ],
}

# ── M5 ────────────────────────────────────────────────────────────────
MEETINGS[5] = {
    "num": 5,
    "title": "Monthly Meeting Five",
    "subtitle": "Standing Reviews and Scorecards - Sharpening Discipline",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 14,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 18,
          desc="Any new critical numbers? Thresholds still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 20,
          desc="Still the right unit, or has the data shifted?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 22,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 24,
          desc="Still feel right? Aspirational but not fantasy?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 26,
          desc="Daily Huddle and Weekly Tactical - still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 28,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Priorities still on track for the year?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("QHAG + 13-Week Sprint Lanes", "✓", "symbol-confirm", 3, 33,
          desc="Sprint lane status: any cells red? Any blind spots?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag"),
        D("A-Player Team Assessment", "▲", "symbol-evolution", 14, 47,
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer",
          points=[
              "Look at the grid together. Where's the consensus, where's the disagreement?",
              "Plot yourself - the founder is on the grid too",
              "The C corner is the conversation no one wants. Don't skip it",
          ]),
        D("Core Values", "▲", "symbol-evolution", 16, 63,
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values",
          points=[
              "Narrow from 5-8 candidates to 3-5 that pass every test",
              "Each value: would you fire someone for violating it? Hire someone for living it?",
              "Stories beat slogans - keep the language people actually used",
              "These are descriptive, not aspirational. Confirm, don't invent",
          ]),
        D("Function Scorecards", "★", "symbol-introduced", 42, 105,
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards",
          points=[
              "One-page view per function: role purpose, key accountabilities, critical numbers, values expected",
              "CEO creates the first one (Head of Company) as the model",
              "Scoreboard Day: once per week, same day, all critical numbers updated by 10 AM",
              "Every red number triggers a written Situation Report: Situation, Cause, Correction, Follow-up",
              "Causes must be structural (capacity, policies, incentives) - never motivation",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize the A-Player Team Assessment grid in Mural - every direct report plotted, color coded",
            "Lock the Core Values list (3-5 values) with stories that anchor each one",
            "Function Scorecards: CEO drafts the Head-of-Company scorecard as the model for the rest of the leadership team",
        ]),
        ("Read Ahead", [
            "No new framework introductions for M6. M6 introduces Market Map - read the article ahead of time",
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
    "subtitle": "Quarterly Reset - Sprint Rebuild and Mapping the Market",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 14,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 18,
          desc="Critical numbers still right? Any thresholds need adjusting?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 20,
          desc="Half a year of data - does the chosen unit still hold?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 22,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 24,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 26,
          desc="Daily Huddle and Weekly Tactical - still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 28,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Priorities still on track for the year?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 32,
          desc="Anyone shifted between A / B / C since M5?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 34,
          desc="Living up to them? Any violations to name?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "▲", "symbol-evolution", 14, 48,
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards",
          points=[
              "Each leader brings their draft scorecard. Read aloud, group review",
              "Are critical numbers measurable from the KFFM widgets?",
              "The CEO scorecard sets the bar for everyone else's",
              "Scoreboard Day rhythm installed? First red number triggers the first SitRep",
          ]),
        D("QHAG + 13-Week Sprint Lanes", "■", "symbol-rebuilt", 20, 68,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag",
          points=[
              "Rebuilt from scratch - new quarter, fresh 90-day priorities",
              "3-5 priorities aligned to the 1HAG, each with an owner and metric",
              "Every priority enables a 1HAG priority OR improves Profit/X",
              "Sprint Lanes: 13-week grid, one binary deliverable per priority per week",
          ]),
        D("Market Map", "★", "symbol-introduced", 37, 105,
          image_key="market_map",
          points=[
              "Map ALL players: customers/buyers left, your company center, suppliers right",
              "Channels, competitors, trade associations - sticky notes work",
              "Follow the dollar - where does revenue actually flow? Estimate percentages per channel",
              "Red circles = weak position, green = strong. Keep it on the wall, update quarterly",
          ],
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize the rebuilt QHAG + Sprint Lanes for Q2 in Mural and Metronome Software",
            "Function Scorecards: every leadership team member has a scorecard, weekly Scoreboard Day rhythm running",
            "Market Map drawn on Mural - all players, channels, dollar flows, red/yellow/green",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M7", [
            ("Core Customer Analysis ★", "https://www.darlison.com/who-is-your-most-valuable-customer/", "https://www.darlison.com/core-customer-discovery-prompt/"),
        ]),
    ],
}

# ── M7 ────────────────────────────────────────────────────────────────
MEETINGS[7] = {
    "num": 7,
    "title": "Monthly Meeting Seven",
    "subtitle": "Coaching the Market Map and Finding the Core Customer",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 3, 15,
          desc="Quarterly check-in: are you measurably closer to your stated outcome?",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 17,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 19,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 21,
          desc="Critical numbers still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 23,
          desc="Still the right unit?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 25,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 27,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 29,
          desc="Still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 31,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 33,
          desc="Priorities still on track for the year?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("QHAG + 13-Week Sprint Lanes", "✓", "symbol-confirm", 3, 36,
          desc="Sprint lane status: any cells red? Any blind spots?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 38,
          desc="Anyone shifted between A / B / C?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 40,
          desc="Living up to them?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 42,
          desc="Scoreboard Day rhythm running? First red number triggered a SitRep?",
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards"),
        D("Market Map", "▲", "symbol-evolution", 23, 65,
          image_key="market_map",
          points=[
              "Read each section: are buyers / channels / competitors named with the right granularity?",
              "Where's the white space? The line your map draws but no competitor occupies?",
              "Dollar flows: do the percentages add up? Where's the concentration risk?",
              "Update quarterly - the dollar flows shift faster than the boxes do",
          ],
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
        D("Core Customer Analysis", "★", "symbol-introduced", 40, 105,
          article="https://www.darlison.com/who-is-your-most-valuable-customer/",
          prompt="https://www.darlison.com/core-customer-discovery-prompt/",
          image_key="core_customer",
          points=[
              "Identify the ONE customer type who buys at a profit - not every customer",
              "Get down to eye level: name them, describe their life, create a cardboard cutout",
              "60% of customers are often the Core Customers; the rest may cost more than they earn",
              "Identify their top 3 needs and the benefits you offer to serve those needs",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Lock the Market Map after the M7 coaching pass - all players, dollar flows, white space named",
            "Core Customer Analysis: profile complete with the cardboard-cutout level of detail and top 3 needs",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M8", [
            ("Attribution Map ★", None, None),
        ]),
    ],
}

# ── M8 ────────────────────────────────────────────────────────────────
MEETINGS[8] = {
    "num": 8,
    "title": "Monthly Meeting Eight",
    "subtitle": "Coaching the Core Customer and Mapping the Attribution",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 14,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 18,
          desc="Critical numbers still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 20,
          desc="Still the right unit?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 22,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 24,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 26,
          desc="Still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 28,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Priorities still on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("QHAG + 13-Week Sprint Lanes", "✓", "symbol-confirm", 3, 33,
          desc="Sprint lane status: any cells red? Any blind spots?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 35,
          desc="Anyone shifted between A / B / C?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 37,
          desc="Living up to them?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 39,
          desc="Scoreboard Day rhythm running? Red numbers triggering SitReps?",
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards"),
        D("Market Map", "✓", "symbol-confirm", 2, 41,
          desc="Channels and dollar flows still accurate?",
          image_key="market_map",
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
        D("Core Customer Analysis", "▲", "symbol-evolution", 22, 63,
          article="https://www.darlison.com/who-is-your-most-valuable-customer/",
          prompt="https://www.darlison.com/core-customer-discovery-prompt/",
          image_key="core_customer",
          points=[
              "Read the profile aloud. Are the top 3 needs sharp, or still generic?",
              "Test: would a real customer recognize themselves in this description?",
              "What benefits do you offer to serve those needs - one-to-one mapping?",
              "Lock the version - this anchors the Attribution Map you'll start in this same meeting",
          ]),
        D("Attribution Map", "★", "symbol-introduced", 42, 105,
          image_key="attribution_map",
          points=[
              "Identify 6 to 8 key market attributes - the things your Core Customer cares about",
              "Rank your company and 2 to 4 competitors 1-5 on each attribute",
              "Plot as lines on a graph - where your line diverges from competitors is your white space",
              "Add a '3HAG Line' showing where you want to be in three years",
              "Forces strategic trade-offs: decide what you WILL do and what you WON'T",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Lock the Core Customer Analysis after the M8 coaching pass",
            "Attribution Map drafted: attributes identified, competitors ranked, white space named, 3HAG Line added",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M9", [
            ("Activity Fit Map (Differentiators) ★", None, None),
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
    "subtitle": "Q3 Sprint Rebuild, Coach the Attribution Map, Introduce the Activity Fit Map",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 14,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 18,
          desc="Critical numbers still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 20,
          desc="Still the right unit?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 22,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 24,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 26,
          desc="Still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 28,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Priorities still on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 32,
          desc="Anyone shifted between A / B / C?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 34,
          desc="Living up to them?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 36,
          desc="Scoreboard Day rhythm holding?",
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards"),
        D("Market Map", "✓", "symbol-confirm", 2, 38,
          desc="Channels and dollar flows still accurate?",
          image_key="market_map",
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
        D("Core Customer Analysis", "✓", "symbol-confirm", 2, 40,
          desc="Still the right customer profile?",
          article="https://www.darlison.com/who-is-your-most-valuable-customer/",
          prompt="https://www.darlison.com/core-customer-discovery-prompt/",
          image_key="core_customer"),
        D("QHAG + 13-Week Sprint Lanes", "■", "symbol-rebuilt", 18, 58,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag",
          points=[
              "Rebuilt from scratch - Q3 boundary, fresh 90-day priorities",
              "3-5 priorities aligned to the 1HAG, each with an owner and metric",
              "Every priority enables a 1HAG priority OR improves Profit/X",
              "Sprint Lanes: 13-week grid, one binary deliverable per priority per week",
          ]),
        D("Attribution Map", "▲", "symbol-evolution", 14, 72,
          image_key="attribution_map",
          points=[
              "Read each attribute. Are competitors scored from real research, or guesses?",
              "Where does your line genuinely diverge - the white space you can defend?",
              "The 3HAG Line is the strategic commitment. Are you still willing to make it?",
              "Lock the version - this anchors the Activity Fit Map you'll start now",
          ]),
        D("Activity Fit Map (Differentiators)", "★", "symbol-introduced", 33, 105,
          image_key="activity_fit",
          points=[
              "From Attribution Map white space, name 3 to 5 interdependent Differentiating Actions",
              "Use 5 whys on each name. Generic names ('support', 'safety') don't survive contact with strategy",
              "Draw connections showing dependencies (Activity Fit Map Level I) - Porter's framework",
              "If a competitor copies any single action, it shouldn't upend you. Interdependence is the key",
              "Distill into a One-Phrase Strategy that ties all differentiating actions together",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize the rebuilt QHAG + Sprint Lanes for Q3 in Mural and Metronome Software",
            "Lock the Attribution Map after the M9 coaching pass",
            "Activity Fit Map drafted: 3 to 5 differentiating actions named and interconnected",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M10", [
            ("Swimlanes ★", None, None),
        ]),
    ],
}

# ── M10 ───────────────────────────────────────────────────────────────
MEETINGS[10] = {
    "num": 10,
    "title": "Monthly Meeting Ten",
    "subtitle": "Coach the Activity Fit Map, Introduce the Swimlanes",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 2, 14,
          desc="Quarterly check-in.",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 18,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 20,
          desc="Critical numbers still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 22,
          desc="Still the right unit?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 24,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 26,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 28,
          desc="Still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 32,
          desc="Priorities still on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("QHAG + 13-Week Sprint Lanes", "✓", "symbol-confirm", 3, 35,
          desc="Sprint lane status: any cells red? Any blind spots?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 37,
          desc="Anyone shifted between A / B / C?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 39,
          desc="Living up to them?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 41,
          desc="Scoreboard Day rhythm holding?",
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards"),
        D("Market Map", "✓", "symbol-confirm", 2, 43,
          desc="Channels and dollar flows still accurate?",
          image_key="market_map",
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
        D("Core Customer Analysis", "✓", "symbol-confirm", 2, 45,
          desc="Still the right customer profile?",
          article="https://www.darlison.com/who-is-your-most-valuable-customer/",
          prompt="https://www.darlison.com/core-customer-discovery-prompt/",
          image_key="core_customer"),
        D("Attribution Map", "✓", "symbol-confirm", 2, 47,
          desc="White space still real? 3HAG Line still the bet?",
          image_key="attribution_map"),
        D("Activity Fit Map (Differentiators)", "▲", "symbol-evolution", 18, 65,
          image_key="activity_fit",
          points=[
              "Read each differentiating action aloud. Did the names survive contact with the team?",
              "Five whys on every name. 'Support', 'safety', 'compliance' don't tell a story",
              "The interdependencies: if a competitor copies one action, does the whole thing still hold?",
              "Distill to a One-Phrase Strategy that ties everything together",
          ]),
        D("Swimlanes", "★", "symbol-introduced", 40, 105,
          image_key="swimlanes",
          points=[
              "12-quarter grid: one row per differentiating action from the Activity Fit Map",
              "Each cell is the key milestone for that capability in that quarter",
              "Less is more. Three outcomes per lane across 12 quarters - cleaner lanes make decisions easier",
              "Read horizontally (progression over time) and vertically (dependencies across lanes in same quarter)",
              "This is what connects strategy to execution quarter by quarter for 3 years",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Lock the Activity Fit Map after the M10 coaching pass",
            "Swimlanes drafted: 12-quarter grid with one row per differentiator, milestones in every quarter cell",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M11", [
            ("Quarterly Coaching Reviews ★", "https://www.darlison.com/coaching-framework/", None),
            ("12-Month Widget-Based Forecast ★", None, None),
        ]),
    ],
}

# ── M11 ───────────────────────────────────────────────────────────────
MEETINGS[11] = {
    "num": 11,
    "title": "Monthly Meeting Eleven",
    "subtitle": "Coach the Swimlanes, Introduce Coaching Reviews and the 12-Month Widget Forecast",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 14,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 18,
          desc="Critical numbers still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 20,
          desc="Still the right unit?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 22,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 24,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 26,
          desc="Still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 28,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Priorities still on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("QHAG + 13-Week Sprint Lanes", "✓", "symbol-confirm", 3, 33,
          desc="Sprint lane status: any cells red? Any blind spots?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 35,
          desc="Anyone shifted between A / B / C?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 37,
          desc="Living up to them?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 39,
          desc="Scoreboard Day rhythm holding?",
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards"),
        D("Market Map", "✓", "symbol-confirm", 2, 41,
          desc="Channels and dollar flows still accurate?",
          image_key="market_map",
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
        D("Core Customer Analysis", "✓", "symbol-confirm", 2, 43,
          desc="Still the right customer profile?",
          article="https://www.darlison.com/who-is-your-most-valuable-customer/",
          prompt="https://www.darlison.com/core-customer-discovery-prompt/",
          image_key="core_customer"),
        D("Attribution Map", "✓", "symbol-confirm", 2, 45,
          desc="White space still real? 3HAG Line still the bet?",
          image_key="attribution_map"),
        D("Activity Fit Map (Differentiators)", "✓", "symbol-confirm", 2, 47,
          desc="Differentiators still hold? One-Phrase Strategy still survives the room?",
          image_key="activity_fit"),
        D("Swimlanes", "▲", "symbol-evolution", 22, 69,
          image_key="swimlanes",
          points=[
              "Read each lane. Are the milestones binary, or fuzzy?",
              "Vertical view: do quarter-N cells across lanes form a coherent picture?",
              "Less is more - if a lane has more than 3 outcomes per quarter, prune",
              "Lock the version - this is the strategy execution map for the next 3 years",
          ]),
        D("12-Month Widget-Based Forecast", "★", "symbol-introduced", 36, 105,
          image_key="widget_forecast",
          points=[
              "A P&L forecast built on widgets, not top-down revenue guesses",
              "Finance builds the model; leaders own the assumptions for their function's widgets",
              "Forecast widgets first, then layer in fiscal assumptions. Never start with dollars",
              "Shifts forecast ownership from finance to the people who actually control the numbers",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Lock the Swimlanes after the M11 coaching pass",
            "Finance and leaders complete the 12-Month Widget-Based Forecast model",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M12", [
            ("Quarterly Coaching Reviews ★", "https://www.darlison.com/coaching-framework/", None),
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
    "subtitle": "Q4 Sprint Rebuild, Coach the Forecast, Introduce Coaching Reviews",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 14,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 18,
          desc="Critical numbers still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 20,
          desc="Still the right unit?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 22,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 24,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 26,
          desc="Still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 28,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Priorities still on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 32,
          desc="Anyone shifted between A / B / C?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 34,
          desc="Living up to them?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 36,
          desc="Scoreboard Day rhythm holding?",
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards"),
        D("Market Map", "✓", "symbol-confirm", 2, 38,
          desc="Channels and dollar flows still accurate?",
          image_key="market_map",
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
        D("Core Customer Analysis", "✓", "symbol-confirm", 2, 40,
          desc="Still the right customer profile?",
          article="https://www.darlison.com/who-is-your-most-valuable-customer/",
          prompt="https://www.darlison.com/core-customer-discovery-prompt/",
          image_key="core_customer"),
        D("Attribution Map", "✓", "symbol-confirm", 2, 42,
          desc="White space still real? 3HAG Line still the bet?",
          image_key="attribution_map"),
        D("Activity Fit Map (Differentiators)", "✓", "symbol-confirm", 2, 44,
          desc="Differentiators still hold?",
          image_key="activity_fit"),
        D("Swimlanes", "✓", "symbol-confirm", 2, 46,
          desc="Quarterly milestones still tracking?",
          image_key="swimlanes"),
        D("QHAG + 13-Week Sprint Lanes", "■", "symbol-rebuilt", 18, 64,
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag",
          points=[
              "Rebuilt from scratch - Q4 boundary, fresh 90-day priorities",
              "3-5 priorities aligned to the 1HAG, each with an owner and metric",
              "Every priority enables a 1HAG priority OR improves Profit/X",
              "Sprint Lanes: 13-week grid, one binary deliverable per priority per week",
          ]),
        D("12-Month Widget-Based Forecast", "▲", "symbol-evolution", 14, 78,
          image_key="widget_forecast",
          points=[
              "Read the model with the leadership team. Are widget assumptions defensible?",
              "Does the forecast tie cleanly back to the FAC critical numbers?",
              "Where does the forecast disagree with the rolling actuals - and why?",
              "Lock the version - this is the basis for the Monthly Forecast Review rhythm",
          ]),
        D("Quarterly Coaching Reviews", "★", "symbol-introduced", 27, 105,
          article="https://www.darlison.com/coaching-framework/",
          image_key="coaching",
          points=[
              "90-day two-way conversation based on the function scorecard - not a top-down annual review",
              "Both sides give and receive feedback. The leader goes first",
              "W.A.I.T. (Why Am I Talking?) - prioritize listening over telling",
              "Question Funnel: broad exploration through five dimensions, ending in one specific action",
              "Feedback model: What went well? What was tricky? What would you do differently?",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Finalize the rebuilt QHAG + Sprint Lanes for Q4 in Mural and Metronome Software",
            "Lock the 12-Month Widget-Based Forecast after the M12 coaching pass",
            "CEO conducts the first Quarterly Coaching Review with one leader",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M13", [
            ("Positioning Statement (Moore) ★", None, None),
            ("Value Proposition (Moore) ★", None, None),
        ]),
    ],
}

# ── M13 ───────────────────────────────────────────────────────────────
MEETINGS[13] = {
    "num": 13,
    "title": "Monthly Meeting Thirteen",
    "subtitle": "Coach the Coaching Reviews, Introduce Positioning and Value Proposition",
    "fixed_hw_time": 7,
    "fixed_hw_cum": 112,
    "deliverables": [
        D("Owner's Outcome", "✓", "symbol-confirm", 2, 14,
          desc="Quarterly check-in: are you measurably closer to your stated outcome?",
          article="https://www.darlison.com/are-you-getting-what-you-want/",
          prompt="https://www.darlison.com/owners-outcome-prompt/",
          image_key="owner"),
        D("Key Function Flow Map (KFFM)", "✓", "symbol-confirm", 2, 16,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_kffm"),
        D("Functional Organization Chart (FOC)", "✓", "symbol-confirm", 2, 18,
          desc="Any changes.",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_foc"),
        D("Functional Accountability Chart", "✓", "symbol-confirm", 2, 20,
          desc="Critical numbers still right?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="pillar_hr_fac"),
        D("Profit/X", "✓", "symbol-confirm", 2, 22,
          desc="Still the right unit?",
          article="https://www.darlison.com/how-your-company-makes-money/",
          prompt="https://www.darlison.com/kffm-tools/",
          image_key="profit_x"),
        D("Core Purpose", "✓", "symbol-confirm", 2, 24,
          desc="Still 'this is us'?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("BHAG", "✓", "symbol-confirm", 2, 26,
          desc="Still feel right?",
          article="https://www.darlison.com/why-does-your-company-exist/",
          prompt="https://www.darlison.com/core-purpose-prompt/",
          image_key="purpose"),
        D("Meeting Cadence", "✓", "symbol-confirm", 2, 28,
          desc="Still running clean?",
          article="https://www.darlison.com/the-eight-meetings-that-run-your-company/",
          prompt="https://www.darlison.com/meeting-cadence-assessment/",
          image_key="meetings"),
        D("3-Year Highly Achievable Goal (3HAG)", "✓", "symbol-confirm", 2, 30,
          desc="Still feels like the destination?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="three_hag"),
        D("1-Year Highly Achievable Goal (1HAG)", "✓", "symbol-confirm", 2, 32,
          desc="Priorities still on track?",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="one_hag"),
        D("QHAG + 13-Week Sprint Lanes", "✓", "symbol-confirm", 2, 34,
          desc="Sprint status check.",
          article="https://www.darlison.com/where-are-you-going/",
          prompt="https://www.darlison.com/planning-cascade-prompt/",
          image_key="q_hag"),
        D("A-Player Team Assessment", "✓", "symbol-confirm", 2, 36,
          desc="Anyone shifted between A / B / C?",
          article="https://www.darlison.com/a-player-team-assessment/",
          prompt="https://www.darlison.com/a-player-team-assessment-prompt/",
          image_key="aplayer"),
        D("Core Values", "✓", "symbol-confirm", 2, 38,
          desc="Living up to them?",
          article="https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
          prompt="https://www.darlison.com/values-discovery-prompt/",
          image_key="values"),
        D("Function Scorecards", "✓", "symbol-confirm", 2, 40,
          desc="Scoreboard Day rhythm holding?",
          article="https://www.darlison.com/scorecards/",
          prompt="https://www.darlison.com/scorecards-tools/",
          image_key="scorecards"),
        D("Market Map", "✓", "symbol-confirm", 2, 42,
          desc="Channels and dollar flows still accurate?",
          image_key="market_map",
          article="https://www.darlison.com/where-are-you-playing/",
          prompt="https://www.darlison.com/market-map-tools/"),
        D("Core Customer Analysis", "✓", "symbol-confirm", 2, 44,
          desc="Still the right customer profile?",
          article="https://www.darlison.com/who-is-your-most-valuable-customer/",
          prompt="https://www.darlison.com/core-customer-discovery-prompt/",
          image_key="core_customer"),
        D("Attribution Map", "✓", "symbol-confirm", 2, 46,
          desc="White space still real?",
          image_key="attribution_map"),
        D("Activity Fit Map (Differentiators)", "✓", "symbol-confirm", 2, 48,
          desc="Differentiators still hold?",
          image_key="activity_fit"),
        D("Swimlanes", "✓", "symbol-confirm", 2, 50,
          desc="Quarterly milestones still tracking?",
          image_key="swimlanes"),
        D("12-Month Widget-Based Forecast", "✓", "symbol-confirm", 2, 52,
          desc="Tracking to plan?",
          image_key="widget_forecast"),
        D("Quarterly Coaching Reviews", "▲", "symbol-evolution", 14, 66,
          article="https://www.darlison.com/coaching-framework/",
          image_key="coaching",
          points=[
              "First reviews completed - what surfaced from the leader-side feedback?",
              "Did the W.A.I.T. discipline hold, or did the leader fall into telling?",
              "The cascade: leaders now run the same review with their direct reports next quarter",
              "Lock the format. This is the coaching rhythm for the rest of the engagement",
          ]),
        D("Positioning Statement (Moore)", "★", "symbol-introduced", 18, 84,
          image_key="positioning",
          points=[
              "Geoffrey Moore's Crossing the Chasm format: For [target] who [need], our [product] is a [category] that [benefit], unlike [alternatives]",
              "Pulls all the strategic work to date into one confident, repeatable statement",
              "Working through it surfaces gaps in the strategy. That's the point",
              "Introduced now because the team needs a full year of strategic picture-building first",
          ]),
        D("Value Proposition (Moore)", "★", "symbol-introduced", 21, 105,
          image_key="value_prop",
          points=[
              "The value exchange: what the customer gets and why it's worth the price",
              "Paired with Positioning: Positioning says where you play, Value Proposition says why customers buy",
              "A living artifact - revisited as strategy validation continues",
              "Test against the Core Customer's top 3 needs from the Core Customer Analysis",
          ]),
    ],
    "homework": [
        ("Review and Complete", [
            "Lock the Quarterly Coaching Reviews format after the M13 coaching pass",
            "Positioning Statement drafted in Moore's format",
            "Value Proposition drafted and tested against Core Customer top 3 needs",
        ]),
        ("Read Ahead and Complete the ✦ AI Prompts for M14", [
            ("Painted Picture ★", None, None),
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
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>
                    Feedback runs both ways. Tell me what didn't land.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span>
                    Articles and prompts are living. Always pull the latest from darlison.com, not a saved copy.
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
            <p class="slide-subtitle reveal" style="font-size: var(--small-size); color: var(--text-secondary); margin-bottom: 0.4rem;">Add finalized artifacts to Mural and email byron@darlison.com at least five business days before next meeting.</p>

{sections_html}
            </div>
            <div class="col-image reveal" style="display: flex; flex-direction: column; gap: 1rem; align-items: center;">
                <img src="../m1/assets/homework.png" alt="Homework and preparation">
                <p style="margin-top: 0.25rem; padding: 0.55rem 0.8rem; background: rgba(84, 181, 112, 0.08); border-left: 3px solid #54B570; border-radius: 4px; font-style: italic; font-size: var(--small-size); color: var(--text-primary); max-width: 90%;">Reminder: everything on darlison.com updates continuously. Pull the current version each time. Don't work from a saved copy.</p>
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
                    <p class="close-instruction reveal">Break out as a team. Agree on the 3 things your team needs to hear from this meeting.</p>
                    <p class="close-question reveal">Come back and present. Share them in tomorrow's huddle.</p>
                </div>
                <div class="col-image reveal">
                    <img src="../../shared/assets/cascade-3-key-messages.png" alt="Cascade 3 Key Messages">
                </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">(2/{cum})</span>
    </section>"""


def slide_feedback(cum):
    return f"""    <!-- SLIDE: FEEDBACK -->
    <section class="slide" aria-label="Feedback">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text">
                    <h1 class="slide-title reveal">Feedback</h1>
                    <p class="slide-subtitle reveal">30 seconds each.</p>
                    <ol class="reveal" style="padding-left: 1.5rem; display: flex; flex-direction: column; gap: clamp(0.6rem, 1.4vh, 1.1rem); margin-top: var(--content-gap); font-size: var(--body-size); line-height: 1.45; color: var(--text-primary);">
                        <li>What landed today?</li>
                        <li>What confused you, or where did the materials fail you?</li>
                        <li>What would have made this session more useful?</li>
                    </ol>
                </div>
                <div class="col-image reveal">
                    <img src="../../shared/assets/feedback.png" alt="Feedback">
                </div>
            </div>
        </div>
{FOOTER}
        <span class="time-indicator">(3/{cum})</span>
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


def build_deep_link_js():
    """Hash-based deep-link wiring; matches /tmp/add-deep-links.py SNIPPET."""
    return """    <script>
    /* coaching-slides:deep-link v1 */
    (function() {
        const toSlug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
        const slides = document.querySelectorAll('section.slide');
        if (!slides.length) return;

        const seen = new Map();
        slides.forEach(slide => {
            if (slide.id) return;
            const label = slide.getAttribute('aria-label') || 'slide';
            let slug = toSlug(label) || 'slide';
            const n = (seen.get(slug) || 0) + 1;
            seen.set(slug, n);
            slide.id = n > 1 ? `${slug}-${n}` : slug;
        });

        let suppress = false;
        const io = new IntersectionObserver(entries => {
            if (suppress) return;
            for (const e of entries) {
                if (e.isIntersecting && e.intersectionRatio >= 0.5) {
                    const newHash = '#' + e.target.id;
                    if (location.hash !== newHash) {
                        history.replaceState(null, '', newHash);
                    }
                }
            }
        }, { threshold: 0.5 });
        slides.forEach(s => io.observe(s));

        function scrollToHash() {
            const slug = decodeURIComponent(location.hash.slice(1));
            if (!slug) return;
            const target = document.getElementById(slug);
            if (!target) return;
            suppress = true;
            target.scrollIntoView({ behavior: 'auto', block: 'start' });
            setTimeout(() => { suppress = false; }, 700);
        }

        if (location.hash) {
            window.addEventListener('load', () => setTimeout(scrollToHash, 60));
        }
        window.addEventListener('hashchange', scrollToHash);
    })();
    </script>"""


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
    slides.append(slide_cascade(114))
    slides.append(slide_feedback(117))
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
{build_deep_link_js()}
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
