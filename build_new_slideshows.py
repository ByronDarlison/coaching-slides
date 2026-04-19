#!/usr/bin/env python3
"""
Generate M7-M23 monthly coaching slideshows from the introduce-then-coach pacing table.
Uses the CSS/JS template from M6 and the slide-building rules.
"""

import os
from pathlib import Path

BASE = Path(__file__).parent

# Deliverable data: name, article_url, prompt_url, description for coaching, description for introducing, shared_image
DELIVERABLES = {
    "Owner's Outcome": {
        "article": "https://www.darlison.com/are-you-getting-what-you-want/",
        "prompt": "https://www.darlison.com/owners-outcome-prompt/",
        "image": "https://www.darlison.com/content/images/size/w1200/2026/03/Gemini_Generated_Image_c8oxcvc8oxcvc8ox.png",
    },
    "Key Function Flow Map (KFFM)": {
        "article": "https://www.darlison.com/how-your-company-makes-money/",
        "prompt": "https://www.darlison.com/kffm-tools/",
        "image": "https://www.darlison.com/content/images/size/w1920/2026/03/key-function-flow-map-how-company-makes-money.png",
    },
    "Functional Accountability Chart (FAC)": {
        "article": "https://www.darlison.com/how-your-company-makes-money/",
        "prompt": "https://www.darlison.com/kffm-tools/",
        "image": "https://www.darlison.com/content/images/size/w1920/2026/03/key-function-flow-map-how-company-makes-money.png",
    },
    "Functional Organization Chart (FOC)": {
        "article": "https://www.darlison.com/how-your-company-makes-money/",
        "prompt": "https://www.darlison.com/kffm-tools/",
        "image": "https://www.darlison.com/content/images/size/w1920/2026/03/key-function-flow-map-how-company-makes-money.png",
    },
    "Profit/X": {
        "article": "https://www.darlison.com/how-your-company-makes-money/",
        "prompt": "https://www.darlison.com/kffm-tools/",
        "image": "https://www.darlison.com/content/images/size/w1920/2026/03/key-function-flow-map-how-company-makes-money.png",
    },
    "Core Purpose": {
        "article": "https://www.darlison.com/why-does-your-company-exist/",
        "prompt": "https://www.darlison.com/core-purpose-prompt/",
        "image": "../../shared/assets/deliverables/core-customer.png",
    },
    "BHAG": {
        "article": "https://www.darlison.com/why-does-your-company-exist/",
        "prompt": "https://www.darlison.com/core-purpose-prompt/",
        "image": "../../shared/assets/deliverables/core-customer.png",
    },
    "Meeting Cadence": {
        "article": "https://www.darlison.com/the-eight-meetings-that-run-your-company/",
        "prompt": "https://www.darlison.com/meeting-cadence-assessment/",
        "image": "",
    },
    "3HAG": {
        "article": "https://www.darlison.com/where-are-you-going/",
        "prompt": "https://www.darlison.com/planning-cascade-prompt/",
        "image": "https://www.darlison.com/content/images/size/w1200/2026/04/planning-cascade-3hag-weekly-execution.png",
    },
    "1HAG": {
        "article": "https://www.darlison.com/where-are-you-going/",
        "prompt": "https://www.darlison.com/planning-cascade-prompt/",
        "image": "https://www.darlison.com/content/images/size/w1200/2026/04/planning-cascade-3hag-weekly-execution.png",
    },
    "QHAG + 13-Week Sprint Lanes": {
        "article": "https://www.darlison.com/where-are-you-going/",
        "prompt": "https://www.darlison.com/planning-cascade-prompt/",
        "image": "https://www.darlison.com/content/images/size/w1200/2026/04/planning-cascade-3hag-weekly-execution.png",
    },
    "Core Values": {
        "article": "https://www.darlison.com/how-to-discover-your-companys-values-using-ai",
        "prompt": "https://www.darlison.com/values-discovery-prompt/",
        "image": "https://www.darlison.com/content/images/size/w1200/2026/03/How-To-Disover-Company-Values.png",
    },
    "A-Player Team Assessment": {
        "article": "https://www.darlison.com/a-player-team-assessment/",
        "prompt": "https://www.darlison.com/a-player-team-assessment-prompt/",
        "image": "",
    },
    "Market Map": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/market-map.png",
    },
    "Function Scorecards": {
        "article": "https://www.darlison.com/scoreboard-day/",
        "prompt": "",
        "image": "",
    },
    "Core Customer Analysis": {
        "article": "https://www.darlison.com/who-is-your-most-valuable-customer/",
        "prompt": "https://www.darlison.com/core-customer-discovery-prompt/",
        "image": "../../shared/assets/deliverables/core-customer.png",
    },
    "Attribution Map": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/attribution-map.png",
    },
    "Activity Fit Map (Differentiators)": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/activity-fit-map.png",
    },
    "Swimlanes": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/swimlanes.png",
    },
    "12-Month Widget-Based Forecast": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/widget-forecast.png",
    },
    "Quarterly Coaching Reviews": {
        "article": "https://www.darlison.com/coaching-framework/",
        "prompt": "",
        "image": "",
    },
    "Positioning Statement (Moore)": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/positioning-statement.png",
    },
    "Value Proposition (Moore)": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/value-proposition.png",
    },
    "36-Month Rolling Forecast": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/rolling-forecast-36.png",
    },
    "Flywheel": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/flywheel.png",
    },
    "Brand Promise with Guarantee": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/brand-promise.png",
    },
    "Secret Sauce": {
        "article": "",
        "prompt": "",
        "image": "../../shared/assets/deliverables/secret-sauce.png",
    },
    "Skip-Level Reviews": {
        "article": "https://www.darlison.com/skip-level-reviews/",
        "prompt": "",
        "image": "",
    },
    "Business Model Canvas": {
        "article": "",
        "prompt": "",
        "image": "",
    },
    "BrandScript": {
        "article": "",
        "prompt": "",
        "image": "",
    },
    "Porter's Five Forces": {
        "article": "",
        "prompt": "",
        "image": "",
    },
    "Consumption Chain Mapping": {
        "article": "",
        "prompt": "",
        "image": "",
    },
}

# Talking points for coach slides (▲)
COACH_POINTS = {
    "Function Scorecards": [
        "Review the Head of Company scorecard. Does it capture the right accountabilities from the KFFM?",
        "Are critical numbers from the FAC reflected in the scorecard?",
        "Are Core Values built into the behavioral expectations?",
        "Plan the cascade: which leaders get their scorecards next?",
    ],
    "Core Customer Analysis": [
        "Review the profile. Is this truly the ONE customer type who buys at a profit?",
        "Can you name them, describe their life, create a cardboard cutout?",
        "What are their top 3 needs? What benefits do you offer for each?",
        "Does this align with where you're strong on the Market Map?",
    ],
    "Attribution Map": [
        "Review the matrix. Are the 6-8 attributes the right ones for your Core Customer?",
        "Where does your line diverge from competitors? That's your white space.",
        "Does the 3HAG Line show a realistic position in three years?",
        "What strategic trade-offs does this force?",
    ],
    "Activity Fit Map (Differentiators)": [
        "Review the 3-5 differentiating capabilities from the Attribution Map white space",
        "For each differentiator: what supporting activities are required?",
        "Are these things competitors can't or won't do?",
        "Does each differentiator connect to a Core Customer need?",
    ],
    "Swimlanes": [
        "Review the 12-quarter grid. Does each differentiating activity have clear milestones?",
        "Are the quarterly milestones achievable given current capacity?",
        "Does the functional view show each department their piece?",
    ],
    "12-Month Widget-Based Forecast": [
        "Review the forecast. Are widget assumptions owned by function leaders, not finance?",
        "Do the widgets flow from the KFFM?",
        "Is the model built bottom-up from widgets, not top-down from revenue guesses?",
    ],
    "Quarterly Coaching Reviews": [
        "Review the coaching review process. Is it a two-way conversation, not a top-down review?",
        "Is it based on the function scorecard?",
        "Has the CEO completed their own coaching review first?",
    ],
    "Positioning Statement, Value Proposition": [
        "Review both statements together. Does the Positioning Statement say where you play?",
        "Does the Value Proposition say why you win?",
        "Can the team say both confidently in one breath?",
    ],
    "Positioning Statement (Moore)": [
        "Review the statement: For [target customer] who [need], our [product] is a [category] that [key benefit] unlike [alternatives]",
        "Does it feel confident and sayable? Not corporate jargon?",
        "Does it align with the Core Customer and Attribution Map white space?",
    ],
    "Value Proposition (Moore)": [
        "Review the value exchange: what the customer gets and why it's worth what they pay",
        "Does it pair with the Positioning Statement?",
        "Would your Core Customer nod reading this?",
    ],
    "36-Month Rolling Forecast": [
        "Review the 36-month projection. Does it connect the 12-month forecast to the 3HAG?",
        "Are Swimlane assumptions feeding into the forecast?",
        "Does the leadership team own the numbers, not just finance?",
    ],
    "Flywheel": [
        "Review the flywheel map. Does each step feed the next?",
        "Is this genuinely self-reinforcing, or just a list of good things?",
        "Where is the flywheel weakest right now?",
    ],
    "Brand Promise with Guarantee": [
        "Review the promise. Is it based on the Core Customer's top 3 needs?",
        "Is the guarantee specific and credible?",
        "Is the team confident they can deliver before going public?",
    ],
    "Secret Sauce": [
        "Review the discussion. Have you identified a tenfold advantage?",
        "Is it something competitors can't or won't solve?",
        "If not found yet, that's OK. Keep looking at every strategy meeting.",
    ],
    "Skip-Level Reviews": [
        "Review the process. Is the CEO having direct conversations one level below leaders?",
        "One conversation, one improvement, every 90 days?",
        "Is the intent clear: surface how the leader is managing, not bypass them?",
    ],
    "Business Model Canvas": [
        "Review the canvas. Does it accurately map how you create, deliver, and capture value?",
        "Does it align with the Positioning Statement and Value Proposition?",
        "Any surprises in the revenue streams or cost structure?",
    ],
    "BrandScript": [
        "Review the StoryBrand framework. Is the customer the hero, not the company?",
        "Is the company positioned as the guide with a clear plan?",
        "Does the messaging align with the Positioning Statement?",
    ],
    "Porter's Five Forces": [
        "Review the five forces analysis. Which forces are strongest in your industry?",
        "How does this affect your strategy and differentiation?",
        "Any forces you've been underestimating?",
    ],
    "Consumption Chain Mapping": [
        "Review the customer journey map end to end",
        "Where are the friction points in the experience?",
        "Does execution actually serve the Core Customer's needs at every touchpoint?",
    ],
}

# Talking points for introduce slides (★)
INTRO_POINTS = {
    "Core Customer Analysis": [
        "Identify the ONE customer type who buys at a profit, not every customer",
        "Get down to eye level: name them, describe their life, create a cardboard cutout",
        "Often 60% of customers are Core Customers generating profit; the rest may cost more than they're worth",
        "Identify their top 3 needs and the benefits you offer to serve those needs",
    ],
    "Attribution Map": [
        "Identify 6-8 key market attributes. Rank your company and 2-4 competitors 1-5",
        "Plot as lines on a graph: where your line diverges from competitors is your white space",
        "Add a 3HAG Line showing where you want to be in three years",
        "Forces strategic trade-offs: decide what you WILL do and what you WON'T",
    ],
    "Activity Fit Map (Differentiators)": [
        "Michael Porter's framework: the 3-5 capabilities that put your company in a unique position",
        "Built from the white space identified in the Attribution Map",
        "For each differentiator, map the supporting activities required",
        "Shows what you must do differently, not just what you do",
    ],
    "Swimlanes": [
        "A 12-quarter grid with one row per differentiating activity",
        "Each row maps the major milestones needed to build that capability, quarter by quarter",
        "Shows the team exactly what has to happen and when",
        "Functional view added later so each department can see their piece",
    ],
    "12-Month Widget-Based Forecast": [
        "A 12-month P&L forecast built on widgets, not top-down revenue guesses",
        "Finance builds the model. Leaders own the assumptions for their function's widgets",
        "Widgets flow from the KFFM: the things that move through the business",
        "Shifts forecast ownership from finance to the people who control the numbers",
    ],
    "Quarterly Coaching Reviews": [
        "A 90-day two-way conversation based on the function scorecard",
        "Not a top-down annual review. Both sides give and receive feedback",
        "The CEO starts these with leaders once scorecards are in place",
        "Later, leaders run the same reviews with their own team members: the cascade",
    ],
    "Positioning Statement (Moore)": [
        "Geoffrey Moore's Crossing the Chasm framework",
        "For [target customer] who [need], our [product] is a [category] that [key benefit] unlike [alternatives]",
        "Takes all the strategy work and formats it into one confident, sayable statement",
        "If you can't say it in one breath, it's not ready",
    ],
    "Value Proposition (Moore)": [
        "The value exchange: what the customer gets and why it's worth what they pay",
        "Paired with the Positioning Statement: if that says where you play, this says why you win",
        "Must resonate with the Core Customer's top needs",
    ],
    "36-Month Rolling Forecast": [
        "Extends the 12-month widget-based forecast all the way out to the 3HAG",
        "36 months of widget and fiscal projections",
        "Gives the team a line of sight from today's numbers to the 3-year goal",
        "Swimlane assumptions feed directly into the forecast",
    ],
    "Flywheel": [
        "Jim Collins's concept: a self-reinforcing loop where each step feeds the next",
        "The team maps their company's specific flywheel",
        "Not a list of good things. Each action must genuinely compound the next",
        "Once spinning, momentum builds over time",
    ],
    "Brand Promise with Guarantee": [
        "A public commitment to your Core Customer based on their top 3 needs",
        "What you promise to deliver, backed by a specific guarantee if you don't",
        "Brainstorm first. Validate with the market. Lock the guarantee",
        "Not made public until the team is confident they can deliver",
    ],
    "Secret Sauce": [
        "Your unique tenfold advantage: the problem you solve that no one else wants to solve",
        "Most teams take months or years to identify it",
        "Once found, never share it. Never stop looking for the next one",
        "Discussion starts here; it's an ongoing discovery process",
    ],
    "Skip-Level Reviews": [
        "The CEO has a direct conversation with people one level below their leaders",
        "Not to bypass the leader, but to surface how that leader is actually managing",
        "One conversation, one improvement, every 90 days",
        "Builds trust and accountability through the organization",
    ],
    "Business Model Canvas": [
        "Alex Osterwalder's framework mapping how the organization creates, delivers, and captures value",
        "A strategic validation tool: uses the Positioning Statement and Value Proposition as inputs",
        "Examine: key partners, key activities, value propositions, customer relationships, customer segments, channels, cost structure, revenue streams",
    ],
    "BrandScript": [
        "The StoryBrand framework applied to your company's messaging",
        "The customer is the hero, your company is the guide",
        "Clarifies: the problem, the plan, and the success the customer achieves",
        "Every piece of marketing should flow from this script",
    ],
    "Porter's Five Forces": [
        "Michael Porter's industry profitability analysis",
        "Five competitive forces: rivalry, supplier power, buyer power, threat of substitution, threat of new entry",
        "A strategic validation tool: stress-tests your strategy against industry dynamics",
        "Which forces are strongest? How does your differentiation protect you?",
    ],
    "Consumption Chain Mapping": [
        "Maps the Core Customer's complete experience throughout their entire journey with your company",
        "From first awareness through purchase, use, and renewal",
        "Validates strategy by analyzing how well execution serves the customer experience",
        "Surfaces friction points and opportunities the team may have missed",
    ],
}

# Monthly schedule: month_number -> {subtitle, coach_items, introduce_items, rebuild_items, quarterly_oo}
MONTHS = {
    7: {
        "subtitle": "Understanding Your Most Valuable Customer",
        "coach": ["Function Scorecards"],
        "introduce": ["Core Customer Analysis"],
        "rebuild": [],
        "quarterly_oo": True,
    },
    8: {
        "subtitle": "Mapping Your Competitive Position",
        "coach": ["Core Customer Analysis"],
        "introduce": ["Attribution Map"],
        "rebuild": [],
        "quarterly_oo": False,
    },
    9: {
        "subtitle": "Defining What Makes You Different",
        "coach": ["Attribution Map"],
        "introduce": ["Activity Fit Map (Differentiators)"],
        "rebuild": ["QHAG + 13-Week Sprint Lanes"],
        "quarterly_oo": False,
    },
    10: {
        "subtitle": "Operationalizing Strategy into Swimlanes",
        "coach": ["Activity Fit Map (Differentiators)"],
        "introduce": ["Swimlanes"],
        "rebuild": [],
        "quarterly_oo": True,
    },
    11: {
        "subtitle": "Forecasting with Widgets, Not Guesses",
        "coach": ["Swimlanes"],
        "introduce": ["12-Month Widget-Based Forecast"],
        "rebuild": [],
        "quarterly_oo": False,
    },
    12: {
        "subtitle": "Building the Coaching Cascade",
        "coach": ["12-Month Widget-Based Forecast"],
        "introduce": ["Quarterly Coaching Reviews"],
        "rebuild": ["QHAG + 13-Week Sprint Lanes"],
        "quarterly_oo": False,
    },
    13: {
        "subtitle": "Positioning Your Company in the Market",
        "coach": ["Quarterly Coaching Reviews"],
        "introduce": ["Positioning Statement (Moore)", "Value Proposition (Moore)"],
        "rebuild": [],
        "quarterly_oo": True,
    },
    14: {
        "subtitle": "Extending the Forecast to Three Years",
        "coach": ["Positioning Statement (Moore)", "Value Proposition (Moore)"],
        "introduce": ["36-Month Rolling Forecast"],
        "rebuild": [],
        "quarterly_oo": False,
    },
    15: {
        "subtitle": "Annual Rebuild and the Flywheel",
        "coach": ["36-Month Rolling Forecast"],
        "introduce": ["Flywheel"],
        "rebuild": ["3HAG", "1HAG", "QHAG + 13-Week Sprint Lanes"],
        "quarterly_oo": False,
        # Annual rebuild month. Tight, choreographed timing to fit 120 min:
        # 3HAG and 1HAG are re-confirms (10 min each); QHAG + Sprint Lanes
        # gets the full 20 because weekly execution is being rebuilt.
        # Standing Review Block absorbs the remaining slack (27 min) to
        # allow real conversation on any of the 19 items surfaced.
        # Flywheel is an introduce (★): concept + homework pointer only.
        "rebuild_times": [10, 10, 20],
        "standing_review_min": 27,
        "coach_time": 30,
        "introduce_time": 5,
    },
    16: {
        "subtitle": "Making a Promise to Your Customer",
        "coach": ["Flywheel"],
        "introduce": ["Brand Promise with Guarantee"],
        "rebuild": [],
        "quarterly_oo": True,
    },
    17: {
        "subtitle": "Finding Your Unfair Advantage",
        "coach": ["Brand Promise with Guarantee"],
        "introduce": ["Secret Sauce"],
        "rebuild": [],
        "quarterly_oo": False,
    },
    18: {
        "subtitle": "Building Leadership Depth",
        "coach": ["Secret Sauce"],
        "introduce": ["Skip-Level Reviews"],
        "rebuild": ["QHAG + 13-Week Sprint Lanes"],
        "quarterly_oo": False,
    },
    19: {
        "subtitle": "Validating How You Create Value",
        "coach": ["Skip-Level Reviews"],
        "introduce": ["Business Model Canvas"],
        "rebuild": [],
        "quarterly_oo": True,
    },
    20: {
        "subtitle": "Clarifying Your Company's Story",
        "coach": ["Business Model Canvas"],
        "introduce": ["BrandScript"],
        "rebuild": [],
        "quarterly_oo": False,
    },
    21: {
        "subtitle": "Stress-Testing Against Industry Forces",
        "coach": ["BrandScript"],
        "introduce": ["Porter's Five Forces"],
        "rebuild": ["QHAG + 13-Week Sprint Lanes"],
        "quarterly_oo": False,
    },
    22: {
        "subtitle": "Mapping the Customer Experience End to End",
        "coach": ["Porter's Five Forces"],
        "introduce": ["Consumption Chain Mapping"],
        "rebuild": [],
        "quarterly_oo": True,
    },
    23: {
        "subtitle": "Deployment Complete",
        "coach": ["Consumption Chain Mapping"],
        "introduce": [],
        "rebuild": [],
        "quarterly_oo": False,
    },
}

# Review block items grow over time. By M7+ we have all of these:
REVIEW_BLOCK_ITEMS = [
    "Key Function Flow Map (KFFM): Level 1 flow still accurate?",
    "Functional Accountability Chart (FAC): ownership and critical numbers still right?",
    "Functional Organization Chart (FOC): any structural changes?",
    "Profit/X: still the right denominator?",
    "Core Purpose and BHAG: still true?",
    "Meeting Cadence: all standing meetings running? Agendas working?",
    "QHAG + Sprint Lanes: on track this week?",
    "Core Values: being reinforced in meetings and conversations?",
    "A-Player Team Assessment: anyone moved since last month?",
]

# Items added to review block as months progress
REVIEW_ADDITIONS = {
    7: ["Market Map: all players mapped? Positions changing?"],
    8: ["Function Scorecards: Scoreboard Day running weekly?"],
    9: ["Core Customer Analysis: profile still accurate?"],
    10: ["Attribution Map: white space holding?"],
    11: ["Activity Fit Map: differentiators being built?", "Swimlanes: milestones on track?"],
    12: ["12-Month Widget-Based Forecast: actuals vs forecast?"],
    13: ["Quarterly Coaching Reviews: happening every 90 days?"],
    14: ["Positioning Statement and Value Proposition: still confident?"],
    15: ["36-Month Rolling Forecast: connected to 3HAG?"],
    16: ["Flywheel: spinning faster?"],
    17: ["Brand Promise: ready to go public?"],
    18: ["Secret Sauce: any closer to identifying it?"],
    19: ["Skip-Level Reviews: one conversation, one improvement?"],
    20: ["Business Model Canvas: value creation model holding?"],
    21: ["BrandScript: messaging consistent across channels?"],
    22: ["Porter's Five Forces: industry dynamics shifting?"],
}


def number_to_word(n):
    words = {7:"Seven",8:"Eight",9:"Nine",10:"Ten",11:"Eleven",12:"Twelve",
             13:"Thirteen",14:"Fourteen",15:"Fifteen",16:"Sixteen",17:"Seventeen",
             18:"Eighteen",19:"Nineteen",20:"Twenty",21:"Twenty-One",22:"Twenty-Two",23:"Twenty-Three"}
    return words.get(n, str(n))


def make_links(name):
    d = DELIVERABLES.get(name, {})
    parts = []
    if d.get("article"):
        parts.append(f'<a href="{d["article"]}" target="_blank" class="link-article">Article</a>')
    if d.get("prompt"):
        parts.append(f'<a href="{d["prompt"]}" target="_blank" class="link-prompt">&#10022; AI Prompt</a>')
    if parts:
        return f'<div class="slide-links reveal">{"".join(parts)}</div>'
    return ""


def make_image(name):
    d = DELIVERABLES.get(name, {})
    if d.get("image"):
        return f'<div class="col-image reveal"><img src=\'{d["image"]}\' alt="{name}"></div>'
    return ""


def make_homework_link(name):
    d = DELIVERABLES.get(name, {})
    parts = []
    if d.get("article"):
        parts.append(f'<a href="{d["article"]}" target="_blank">{name}</a>')
    else:
        parts.append(name)
    if d.get("prompt"):
        parts.append(f' <a href="{d["prompt"]}" target="_blank" class="link-prompt">&#10022; AI Prompt</a>')
    return "".join(parts)


def build_slideshow(month_num):
    m = MONTHS[month_num]
    word = number_to_word(month_num)

    # Collect review block items
    review_items = list(REVIEW_BLOCK_ITEMS)
    for mn in range(7, month_num):
        review_items.extend(REVIEW_ADDITIONS.get(mn, []))

    # Calculate timing
    slides_content = []
    cumulative = 0

    # Good News
    cumulative += 5
    slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text" style="align-items: flex-start;">
                    <h1 class="slide-title reveal">Good News</h1>
                    <p class="slide-subtitle reveal" style="font-size: var(--h2-size); font-weight: 400;">Positive. Professional. 5-10 seconds.</p>
                </div>
                <div class="col-image reveal"><img src="../../shared/assets/good-news.png" alt="Good News"></div>
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">(5/{cumulative})</span>
    </section>''')

    # Rebuild slides (if any). Per-slide times default to 20 min; an
    # m["rebuild_times"] list overrides (must match len(m["rebuild"])).
    rebuild_times = m.get("rebuild_times", [20] * len(m["rebuild"]))
    for rb, rb_time in zip(m["rebuild"], rebuild_times):
        cumulative += rb_time
        d = DELIVERABLES.get(rb, {})
        slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col"><div class="col-text">
                <span class="symbol-badge symbol-rebuilt reveal">&#9724; Rebuilt</span>
                <h1 class="slide-title reveal">{rb}</h1>
                <p class="slide-subtitle reveal">Quarterly rebuild. Start fresh.</p>
                <ul class="talking-points">
                    <li class="reveal">Review last quarter: what landed, what slipped, what surprised you?</li>
                    <li class="reveal">Set 3-5 new priorities for the next 90 days</li>
                    <li class="reveal">Build fresh Sprint Lanes: one binary deliverable per priority per week, no gaps</li>
                </ul>
                {make_links(rb)}
            </div></div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">({rb_time}/{cumulative})</span>
    </section>''')

    # Owner's Outcome quarterly review
    if m["quarterly_oo"]:
        cumulative += 5
        slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col"><div class="col-text">
                <span class="symbol-badge symbol-confirm reveal">&#10003; Review and confirm</span>
                <h1 class="slide-title reveal">Owner's Outcome</h1>
                <p class="reveal" style="font-size: var(--body-size); color: var(--text-secondary);">Quarterly review. Is the outcome still what you want? Is the business moving you closer?</p>
                {make_links("Owner's Outcome")}
            </div></div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">(5/{cumulative})</span>
    </section>''')

    # Standing Review Block. Default 10 min; m["standing_review_min"]
    # overrides (useful on months with many accumulated items).
    review_time = m.get("standing_review_min", 10)
    cumulative += review_time
    review_lis = "\n".join(f'                <li class="reveal">{item}</li>' for item in review_items)
    slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <span class="symbol-badge symbol-confirm reveal">&#10003; Review and confirm</span>
            <h1 class="slide-title reveal">Standing Review Block</h1>
            <ul class="talking-points">
{review_lis}
            </ul>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">({review_time}/{cumulative})</span>
    </section>''')

    # Coach slides (▲). Formula splits 50 min across coach items with
    # a 10-min floor; m["coach_time"] overrides uniformly.
    coach_time = m.get("coach_time", max(10, 50 // max(len(m["coach"]), 1)))
    for item in m["coach"]:
        cumulative += coach_time
        points = COACH_POINTS.get(item, [f"Review and refine the {item} from last month"])
        points_html = "\n".join(f'                    <li class="reveal">{p}</li>' for p in points)
        img = make_image(item)
        slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col"><div class="col-text">
                <span class="symbol-badge symbol-introduced reveal" style="color: #54B570; background: rgba(84, 181, 112, 0.08); border-color: rgba(84, 181, 112, 0.2);">&#9650; Coach and finalize</span>
                <h1 class="slide-title reveal">{item}</h1>
                <ul class="talking-points">
{points_html}
                </ul>
                {make_links(item)}
            </div>
            {img}
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">({coach_time}/{cumulative})</span>
    </section>''')

    # Introduce slides (★). Formula uses remaining time with a 15-min
    # floor; m["introduce_time"] overrides uniformly.
    if m["introduce"]:
        if "introduce_time" in m:
            intro_time = m["introduce_time"]
        else:
            remaining = 120 - cumulative - 20  # save 20 for homework+cascade+close
            intro_time = max(15, remaining // max(len(m["introduce"]), 1))
        for item in m["introduce"]:
            cumulative += intro_time
            points = INTRO_POINTS.get(item, [f"Introduction to {item}"])
            points_html = "\n".join(f'                    <li class="reveal">{p}</li>' for p in points)
            img = make_image(item)
            mural_tag = '<span class="reveal" style="display: inline-block; background: #f5faf6; border: 1px solid #dceee0; color: #54B570; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; margin-top: 10px; font-weight: 500;">&#8594; Move to Mural for this exercise</span>' if intro_time > 20 else ""
            slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col"><div class="col-text">
                <span class="symbol-badge symbol-introduced reveal">&#9733; Introduced</span>
                <h1 class="slide-title reveal">{item}</h1>
                <ul class="talking-points">
{points_html}
                </ul>
                {make_links(item)}
                {mural_tag}
            </div>
            {img}
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">({intro_time}/{cumulative})</span>
    </section>''')

    # Homework
    cumulative += 5
    hw_review = "\n".join(f'                    <li>{make_homework_link(item)}</li>' for item in m["introduce"])
    next_month = MONTHS.get(month_num + 1)
    hw_ahead = ""
    if next_month and next_month["introduce"]:
        hw_items = "\n".join(f'                    <li>{make_homework_link(item)}</li>' for item in next_month["introduce"])
        hw_ahead = f'''
            <div class="homework-section reveal">
                <h3>&#9733; Read Ahead and Complete the &#10022; AI Prompts for M{month_num + 1}</h3>
                <ul class="homework-list">
{hw_items}
                    <li>Add finalized artifacts to Mural</li>
                </ul>
            </div>'''

    slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col"><div class="col-text">
            <h1 class="slide-title reveal">Homework</h1>
            <p class="slide-subtitle reveal" style="font-size: var(--small-size); color: var(--text-secondary); margin-bottom: 0.4rem;">Add finalized artifacts to Mural and email byron@darlison.com at least two business days before next meeting.</p>
            <div class="homework-section reveal">
                <h3>&#9650; Review and Complete</h3>
                <ul class="homework-list">
{hw_review}
                </ul>
            </div>
{hw_ahead}
            </div>
            <div class="col-image reveal" style="display: flex; flex-direction: column; gap: 1rem; align-items: center;">
                <img src="../m1/assets/homework.png" alt="Homework">
                <p style="margin-top: 0.25rem; padding: 0.55rem 0.8rem; background: rgba(84, 181, 112, 0.08); border-left: 3px solid #54B570; border-radius: 4px; font-style: italic; font-size: var(--small-size); color: var(--text-primary); max-width: 90%;">Reminder: everything on darlison.com updates continuously. Pull the current version each time. Don't work from a saved copy.</p>
            </div>
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">(5/{cumulative})</span>
    </section>''')

    # Cascade (reserve 3 min for Feedback + 3 min for OPC)
    remaining_time = max(0, 120 - cumulative - 6)
    cascade_time = max(2, remaining_time // 2) if remaining_time >= 4 else 2
    cumulative += cascade_time
    slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col"><div class="col-text">
                <h1 class="slide-title reveal">Cascade 3 Key Messages</h1>
                <p class="close-instruction reveal">Agree on three or less things your team needs to hear from this meeting.</p>
            </div>
            <div class="col-image reveal"><img src="../../shared/assets/cascade-3-key-messages.png" alt="Cascade"></div>
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">({cascade_time}/{cumulative})</span>
    </section>''')

    # Feedback (3 min)
    feedback_time = 3
    cumulative += feedback_time
    slides_content.append(f'''
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
                <div class="col-image reveal"><img src="../../shared/assets/feedback.png" alt="Feedback"></div>
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">({feedback_time}/{cumulative})</span>
    </section>''')

    # Close (expands to absorb overflow if the meeting ran long)
    close_time = max(3, 120 - cumulative)
    cumulative += close_time
    slides_content.append(f'''
    <section class="slide">
        <div class="slide-content">
            <div class="two-col"><div class="col-text">
                <h1 class="slide-title reveal">One-Phrase Close</h1>
                <p class="close-instruction reveal">5 words or less.</p>
                <p class="close-question reveal">How do you feel right now?</p>
            </div>
            <div class="col-image reveal"><img src="../../shared/assets/one-phrase-close.png" alt="Close"></div>
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
        <span class="time-indicator">({close_time}/{cumulative})</span>
    </section>''')

    # Read the CSS/JS template from M6
    template_path = BASE / "monthly" / "m6" / "index.html"
    template = template_path.read_text()

    # Extract head section (everything up to </nav>)
    head_end = template.index("</nav>") + len("</nav>")
    head = template[:head_end]
    head = head.replace("M6 &mdash; Monthly Meeting Six", f"M{month_num} &mdash; Monthly Meeting {word}")

    # Extract script section
    script_start = template.index("    <!-- ===========================================\n       SLIDE PRESENTATION CONTROLLER")
    script = template[script_start:]

    # Build title slide
    title_slide = f'''

    <section class="slide">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text" style="gap: clamp(0.75rem, 2vh, 1.5rem);">
                    <h1 class="slide-title reveal" style="font-size: clamp(2.25rem, 5vw, 3.5rem); letter-spacing: -0.03em;">Monthly Meeting {word}</h1>
                    <p class="slide-subtitle reveal">{m["subtitle"]}</p>
                    <hr class="reveal" style="width: clamp(60px, 10vw, 120px); height: 2px; background: var(--accent-green); border: none;">
                    <img class="reveal" src="../../shared/assets/metronomics-logo.svg" alt="Metronomics" style="max-width: clamp(160px, 20vw, 260px); height: auto;">
                    <span class="reveal" style="font-size: var(--body-size); font-weight: 500; color: var(--text-muted);">darlison.com</span>
                </div>
                <div class="col-image reveal">
                    <img src="assets/title-m{month_num}.png" alt="{m["subtitle"]}">
                </div>
            </div>
        </div>
        <span class="slide-footer">darlison.com | Metronomics Coaching</span>
    </section>'''

    # Assemble
    full_html = head + title_slide + "".join(slides_content) + "\n\n" + script

    # Write
    out_dir = BASE / "monthly" / f"m{month_num}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "assets").mkdir(exist_ok=True)
    (out_dir / "index.html").write_text(full_html)
    print(f"  Built M{month_num}: {m['subtitle']}")


if __name__ == "__main__":
    print("Building M7-M23 slideshows...")
    for month in range(7, 24):
        build_slideshow(month)
    print("Done!")
