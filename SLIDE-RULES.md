# Slide-Building Rules

Rules for building monthly Metronomics coaching slideshows.

## Session Structure (three blocks, every session)

1. **Review block** - Standing items confirmed every session. Single slide titled "Standing Review Block" with ✓ badge. Items join this block the month AFTER they are coached and finalized.
2. **Coach block** - Items introduced last month, now being refined and locked in. ▲ badge (green). This is where the real coaching happens.
3. **Introduce block** - New concepts for this month. ★ badge (blue). One group per session, no stacking.

## Slide Order

1. Title (no timing)
2. Good News
3. Standing Review Block (single consolidated slide from M3 onward; M2 has individual ▲ slides since everything is being coached for the first time)
4. ■ Rebuild slides (if applicable: QHAG every 3 months, 3HAG/1HAG annually)
5. ▲ Coach and finalize slides (one per deliverable)
6. ★ Introduce slides (one per deliverable)
7. Homework
8. Cascade 3 Key Messages
9. One-Phrase Close

## Badge System

- **★ Introduced** (blue, `symbol-introduced`) - First time. Teach the concept, gut out a first draft
- **▲ Coach and finalize** (green, inline style on `symbol-introduced`) - Following month. Review homework, refine, lock it in
- **■ Rebuilt** (blue, `symbol-rebuilt`) - Start from scratch (QHAG every 3 months, 3HAG/1HAG annually)
- **✓ Review and confirm** (grey, `symbol-confirm`) - Standing review block. Quick alignment check

## Homework Slide

- **▲ Review and Complete** section: lists this month's introduced items with article links and AI Prompt buttons. "Add finalized artifacts to Mural and Metronome Software" at the end.
- **★ Read Ahead and Complete the AI Prompts for M[next]** section: lists next month's new introductions with article links and AI Prompt buttons. "Add finalized artifacts to Mural" at the end.
- **Books** section (when applicable): reading for upcoming months.
- Symbols go on the section HEADERS only, not repeated on individual items.

## Naming Conventions

- Key Function Flow Map (KFFM)
- Functional Accountability Chart (FAC)
- Functional Organization Chart (FOC)
- American spelling throughout (finalize, artifacts, organization)
- Full name with abbreviation in parentheses on slide titles

## Timing

- Every slide except the title gets a time indicator: (minutes/cumulative)
- Total session: 120 minutes
- Review block: ~10-15 min as sessions mature
- Rebuild slides: ~20 min
- Coach slides: ~8-15 min each
- Introduce slides: ~15-45 min each (main exercises get more time)
- Homework: ~5-10 min
- Cascade + Close: ~10-20 min total

## Cascade Slide

- Text: "Agree on three or less things your team needs to hear from this meeting."
- No "break out as a team" or "come back and present"

## Images

- Title slide: generated via `~/ai-config/scripts/generate_image.py` using the canonical style guide and six reference images
- Title subtitle must match the actual content being covered in that slideshow
- Shared assets referenced from `../../shared/assets/`
- Deliverable images reused from existing assets in `../../shared/assets/deliverables/`

## Footer

- "darlison.com | Metronomics Coaching"

## Recurring Rebuilds

- QHAG + Sprint Lanes: ■ every 3 months (M6, M9, M12, M15, M18, M21)
- 3HAG + 1HAG: ■ annually (M15)
- Owner's Outcome: ✓ quarterly (M4, M7, M10, M13, M16, M19, M22)

## Review Block Growth

Items join the standing review block the month after they are coached:

| From | Items added to review block |
|------|---------------------------|
| M3 | KFFM, FAC, FOC, Profit/X |
| M4 | Core Purpose, BHAG, Meeting Cadence |
| M5 | 3HAG, 1HAG, QHAG + Sprint Lanes |
| M6 | Core Values, A-Player Team Assessment |
| M7 | Function Scorecards |
| M8 | Market Map |
| M9+ | Each finalized deliverable joins the block |
