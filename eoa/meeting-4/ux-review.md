# EOA Meeting 4 visual review

Reviewed 30 September 2026. Initial findings appear below, followed by implementation verification.

**Latest scoped verdict:** Slide 13 of the current 16-slide deck passes the two-lane planning-cascade review below. Earlier 24-slide findings are historical, before subsequent owner edits. This is not a physical-device or complete interaction certification.

## Scope and evidence

Reviewed all 24 current desktop slides and all 24 phone viewport captures. Evidence is in `/Users/byron/eoa4-standard-work/ux-current/`.

Desktop evidence: `desktop-01.png` through `desktop-24.png`, plus three overview sheets.
Phone evidence: `phone-01.png` through `phone-24.png`.

The phone captures show the initial viewport. They do not prove that every long slide's bottom remains reachable. Scroll and footer checks remain required after revision. This review does not establish physical-device compatibility.

Read the current presentation brief, HTML, deck CSS, and approved visual standard. The EO Accelerator footer is the owner's explicit series override. Preserve every current audience-facing word, data value, link, and slide order unless Byron approves a content change.

## Recommendation

Improve scale, grouping, and vertical rhythm before adding decoration. Many desktop slides detach the title from a small content group. Several tables occupy only the upper quarter of the stage. This makes the deck feel unfinished despite the consistent shell.

Keep the shared shell unchanged. Apply deck-specific composition and responsive changes in `deck.css` and the corresponding slide markup.

Priorities:

1. Bring content closer to its title, using the standard's 24–37 pixel rhythm. Do not vertically center a small body independently beneath a fixed top title.
2. Increase table row height and supporting text where unused space allows it. Keep the same figures and relationships.
3. Group operational prompts into purposeful panels. Preserve the original wording, including questions and instructions.
4. Add two illustrations, on the barometer and closing slides. Keep data and dense instructions free of illustration.
5. Inspect each long phone slide through its final row and footer after changes.

## Slide-by-slide review

| Slide | Current finding | Recommended visual change | Image |
|---|---|---|---|
| 1 AI Walkthrough | Relevant illustration and balanced split layout. The headline nearly touches its bullets. | Add a clear gap between headline and supporting list. Keep existing illustration and content. | Keep existing |
| 2 Break | Clear, quiet transition with useful contrast. | Keep. Optional slightly larger return time on desktop. | None |
| 3 One Word Barometer | Small question floats far below the title on desktop. Phone has substantial unused space. | Use a story composition. Make the existing question the focal text, with the existing instruction below. | Generate reflective figure |
| 4 Rules of Engagement | Icons help scanning, but all rules sit in a compressed band below a large gap. | Start the two-column list nearer the title. Add consistent row spacing and subtle grouping. Preserve all eight rules. | None |
| 5 Business Updates | Three-card structure now works well. Large gap separates title and cards. | Reduce that gap. Preserve aligned cards, numbered questions, metric labels, and reflection divider. | None |
| 6 Presentations | Six equal bullets hide the distinction between the presenter prompts and subsequent contributions. | Place the four presenter prompts in a clear grid. Separate the two existing sharing/feedback lines below it. | None |
| 7 Sample 3HAG | Data is compressed toward the top. Widgets appears as an incomplete data row. | Increase row spacing. Style Widgets as a full-width section header, preserving its text. Emphasize targets consistently. | None |
| 8 Sample 3HAG capabilities | Two small tables underuse the stage. Phone repeats a long field label beside every capability. | Use four numbered capability items under the existing header. Put the existing customer quotation in a distinct panel. | None |
| 9 Sample 1HAG | Same compressed target table and empty Widgets cells as slide 7. | Match the improved slide 7 structure and spacing. | None |
| 10 Annual company priorities | Three cards provide the right grouping but remain short and crowded at the top. | Increase card padding and text separation. Distinguish owner, action, measure, and connection without changing words. | None |
| 11 Sample QHAG | Six-column table needs more breathing room. Widgets looks like missing data. | Give rows more height, right-align comparable numbers where appropriate, and style Widgets as a section header. | None |
| 12 Quarterly company priorities | Correct three-card structure, same vertical compression as slide 10. | Match slide 10. Keep the connection visually subordinate but readable. | None |
| 13 Sprint lanes, weeks 1–4 | Table occupies a thin strip. Labels and deliverables are harder to scan than necessary. | Increase row height and padding. Distinguish the owner column from week columns. Keep blank-week markers. | None |
| 14 Sprint lanes, weeks 5–9 | Narrow columns and repeated vacation text make the grid busy. | Increase row height. Give vacation cells a quiet shared background. Preserve all text and week associations. | None |
| 15 Sprint lanes, weeks 10–13 | Same thin-grid problem. Quarter-end planning has no visual distinction. | Match the other sprint grids. Give the existing final planning column a subtle shared background. | None |
| 16 Planning Cascade | Three long bullets do not visually express the named progression. | Emphasize the existing 3HAG, 1HAG, and QHAG/sprint terms within the source sentence. Use a simple native-text progression without adding copy. Keep links beneath. | None |
| 17 Personal Review | Deep nested list mixes reflection, action specification, and recording. | Group reflection prompts separately from the OBT details. Place the EOA Prep instruction below. Maintain all original questions. | None |
| 18 Share Your Conclusions | Sharing and email submission have equal bullet weight. | Group the speaking prompts. Give the final email instruction a distinct action strip. | None |
| 19 Homework | Link buttons wrap unevenly. Two tasks read as one long list. | Use two resource panels. Align resource labels and prompt links, stacking them deliberately on phones. Preserve reminder text. | None |
| 20 Send your preparation | Dark treatment provides a clear pause and priority. Long headline remains readable. | Keep all wording. Improve line breaks so the email and deadline form coherent reading groups. | None |
| 21 Reading list | Existing two-panel grouping is useful and consistent. | Keep. Check full phone scroll and final book/footer visibility. Avoid generated book covers. | None |
| 22 Housekeeping | Rating and dates are weakly distinguished. The stage is mostly unused. | Separate the existing Give/Take prompt from two date cards. Use dates as visual anchors without changing their order or wording. | None |
| 23 Feedback | Three questions are legible but visually small and detached from the title. | Use three generously spaced numbered prompt rows. Keep the 30-second instruction subordinate. | None |
| 24 One Phrase Close | Existing emotional question is visually underemphasized. Ending feels like another list slide. | Use a story composition matching slide 3. Make the existing question prominent, retaining the five-word instruction. | Generate closing exchange |

## Image briefs

Generate two images against the approved character reference. Use featureless rounded heads, neutral grey bodies, thin grey outlines, and minimal anatomy. Keep white or transparent backgrounds and restrained blue or green accents. Do not render critical text inside either image.

- Slide 3: One generic figure pausing thoughtfully, with a single empty speech bubble. A quiet reflective pose supports naming a feeling. Do not show a mood scale or facial expressions that suggest a preferred answer.
- Slide 24: Two generic figures in a brief, calm exchange, with one simple empty speech bubble. Match the opening illustration's character family. Avoid applause, trophies, or a celebratory result that the source does not claim.

Do not add an illustration to Business Updates. Its questions and metrics already supply the visual structure. Personal Review also needs its space for the original instructions.

## Content conflicts, flagged without alteration

- Slide 6 visibly assigns five minutes to experience shares and five minutes to coach feedback. Its notes specify a five/three/seven sequence. Resolve with Byron before changing either source.
- Slide 17 visibly says four minutes. Its notes and time chain allocate three minutes. Preserve the displayed source until Byron chooses the intended timing.

These are source discrepancies, not authorization to rewrite the deck.

## Acceptance and follow-up

The current deck needs the visual improvements above. The presentation is not yet a final visual pass.

After implementation, inspect all 24 desktop slides again. Inspect all phone content, including long tables and footers. Confirm controls do not permanently obscure the final content. Confirm preserved content and links against this revision.

## Retrospective

Restoring source copy exposed a composition issue: a shared shell alone does not produce a finished slide. Preserve content, then adapt its grouping and scale. Illustrations should support a specific audience task rather than fill every empty space.

## Image integration follow-up

Reviewed `after-3.png` and `after-24.png` after the two generated illustrations were integrated.

Both desktop compositions pass this visual review. Titles, original questions, and supporting instructions form coherent groups. The images match the approved generic character family. Footer marks remain clear, with no visible clipping or overlap. The barometer feels reflective; the close suggests a brief exchange without inventing an outcome.

This confirmation applies to those two desktop renders only. Their updated phone layouts and the remaining recommendations are still pending.

Reviewed `after-phone-3.png` and `after-phone-24.png`. Both new illustrated slides also pass the captured phone viewport. Questions remain readable, artwork is fully visible, and footer branding stays above the controls. This closes the phone check for slides 3 and 24, not the long reference slides.


## Applied visual revision: final disposition

Byron authorized the remaining layout recommendations. The implemented revision was reviewed from `/Users/byron/eoa4-standard-work/ux-applied/`.

### Evidence personally inspected

- All 24 updated desktop slides through the three overview sheets, with full-size checks of slides 5, 17, 19, and 23.
- All 24 phone scroll strips, including overlapping views of every long slide through its final content and footer.
- The corrected Feedback desktop render, `desktop-23-fixed.png`.
- Current HTML source for the two pre-existing timing discrepancies.

The author separately reports passing geometry checks at all nine standard viewport sizes. Those are supporting technical checks, not a substitute for this visual inspection. This reviewer did not exercise native full screen, touch gestures, or a physical phone.

### Recommendation dispositions

| Slides | Disposition |
|---|---|
| 1 | Headline and supporting list have a clear gap; existing illustration retained. Pass. |
| 2 | Quiet transition retained. Pass. |
| 3, 24 | Illustrated story layouts retain original questions and instructions. Desktop and phone pass. |
| 4 | Rules now sit near the title, with consistent icon rows and separators. All eight retained. Pass. |
| 5 | Cards align beneath the title without the former large gap. No extra illustration. Pass. |
| 6 | Presenter prompts are grouped in cards; sharing and coach feedback are distinct strips. Pass. |
| 7, 9, 11 | Tables have roomier rows and clear Widgets section headers. Phone data remains readable. Pass. |
| 8 | Numbered capabilities use the available width. Customer quotation is distinct. Phone problem resolved. Pass. |
| 10, 12 | Priority cards better separate action, measure, and connection. Pass. |
| 13, 14, 15 | Sprint grids have more vertical space, clear owner columns, and meaningful vacation/planning shading. Pass. |
| 16 | Existing cascade terms are emphasized, with supporting instructions and links clearly grouped. Pass. |
| 17 | Reflection and OBT details form separate panels. Recording instruction is distinct. Pass. |
| 18 | Sharing prompts and email action are visually separate. Pass. |
| 19 | Resource panels and links align cleanly. Phone links deliberately stack. Pass. |
| 20 | Deadline treatment retained and readable. Pass. |
| 21 | Useful two-panel reading structure retained. Final book and footer confirmed on phone. Pass. |
| 22 | Give/Take and upcoming dates have distinct treatments. Original order retained. Pass. |
| 23 | Larger numbered prompt rows improve hierarchy. Initial marker clipping was fixed and visually rechecked. Pass. |

Phone strips confirm final rows and footer branding can be scrolled clear of the fixed controls. No horizontal clipping or unreadable content was found in those captures.

### Preservation and remaining scope

The author reports exact visible-text character/order preservation, ignoring whitespace, and matching link counts. This reviewer independently confirmed that the pre-existing timing discrepancies remain unchanged in source. They still need an owner content decision; they are outside this visual revision.

No blocking visual findings remain in the inspected desktop and phone portrait evidence. The review does not assert publication, audience comprehension, timing rehearsal, or physical-device compatibility.

### Implementation lesson

The initial Feedback marker clipping showed why visual inspection remains necessary after geometry checks. List markers can sit outside measured text boxes. The corrected explicit number column stays inside the available content area.


## Two-lane planning cascade review: current slide 13

Byron requested both financial targets and the capability-to-priority relationship on one slide. The current deck has 16 slides. This follow-up reviews slide 13 only; prior whole-deck findings describe the earlier 24-slide revision.

**Verdict: Pass for the inspected desktop and phone portrait renders.**

Evidence personally inspected:

- `ux-applied/cascade-two-lanes-desktop.png`
- `ux-applied/cascade-two-lanes-1280.png`
- `ux-applied/cascade-phone-strip.jpg`, four overlapping phone views through the footer.
- Current slide 13 HTML and source sample values on slides 7, 9, and 11.

The three common columns identify 3HAG, 1HAG, and QHAG. Two aligned rows distinguish financial targets from capabilities and priorities. Blue and green accents reinforce that distinction. Each horizontal connection clearly says “Fulfilled by.” No cross-row arrow falsely attributes every financial result to the referral example.

The financial values match the existing examples:

| Metric | 3HAG | 1HAG | QHAG |
|---|---:|---:|---:|
| Revenue | $780,000 | $360,000 | $84,000 |
| Profit margin | 18% | 15% | 14% (blended) |
| Cash | $96,000 | $42,000 | $38,000 (end of quarter) |

The 3HAG cash context remains visible: about three months of base cost. The diagram does not call the 3HAG revenue a three-year cumulative total. It preserves distinct horizon dates and the quarterly ratio/balance qualifiers. Speaker notes explicitly avoid adding cash balances or margins across periods.

The referral capability, annual priority, and quarterly priority retain their source wording. The diagram uses native text, making a separate illustration unnecessary.

At 1280 pixels, cards, labels, arrows, and footer remain clear. On the phone, each row becomes a complete vertical sequence. Repeated horizon labels retain orientation. All six cards and final footer can be reached without horizontal clipping. No blocking visual issue was found.

This follow-up does not independently reapprove the other 15 slides after intervening owner edits. No new universal playbook rule emerged: this is a presentation layout using the established cascade relationship.
