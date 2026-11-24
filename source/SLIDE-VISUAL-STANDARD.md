# Slide Visual Standard

Approved by Byron on 30 September 2026 after reviewing the Kick Off sample.
This standard governs visual presentation, not approval of example coaching content.
It supersedes the 29 September logo-only title and text-footer rules.

## Source of truth

Use the [shared slideshow shell](shared/README.md), reusable slide libraries, and ordered playlists.
The [library and playlist contract](README.md) defines composition.
The [presentation information design standard](../../style-guides/presentation-information-design.md) governs the communication job.
The [presentation development workflow](../../workflows/presentation-development.md) governs authoring and verification.

## Stage and typography

Center a 16:9 warm neutral slide on a dark surround when desktop space permits.
Use `#1b1f24` for the surround, `#f6f4ef` for the canvas, and white for panels.
Bundle Geist Sans and Geist Mono locally. Do not request online fonts.
Use Geist Sans for titles and body text. Use Geist Mono for compact labels.
Use blue `#326ab6` for structure, green `#54b570` for action, and orange `#a94f1f` for meaningful gaps.
Artwork may use blue `#326ab5` and green `#54b570` sparingly.
Keep headline-to-content spacing about 24 to 37 pixels on desktop.
On the desktop stage, centre the title and its content together as one block between the top of the slide and the footer, so a short slide does not leave the bottom half empty. Slides that fill the page do not move.
Supporting text uses a shared scale across card layouts, reaching 24 pixels at presentation sizes.
Do not shrink dense-card text merely to preserve empty space.
Reference tables that hold a whole framework on one slide may drop to 13 to 18 pixels, provided they still fit at 1280 by 720.

## Opening slide

Every populated opening slide includes a relevant visual image.
Place the headline and green hairline beside the illustration on wide screens.
Stack them on a phone. Preserve readable type and the full illustration.
Keep logos in the footer rather than duplicating them in the title content.
The approved opening example shows generic figures collaborating on a shared plan.

## Footer

Place `darlison.com` at bottom left on every slide.
For Metronomics presentations, place the Metronomics logo at bottom right on every slide.
Use the logo instead of the words “Metronomics Coaching”.
Keep both marks quiet and clear of content and controls.
Use a white logo on the dark closing slide.
Other presentation sources can omit the Metronomics logo through playlist branding.
Do not add a second domain or the old brand-line.
On long mobile slides, the footer follows the content at the bottom of the slide.

## Illustration style

Use the approved [character reference](shared/references/character-style-reference.png).
Characters have rounded, featureless heads, neutral grey bodies, fine grey outlines, and minimal anatomy.
Avoid distinctive clothing, realistic faces, hair, gender cues, and unnecessary detail.
Use simple activity and props to communicate the slide’s point.
Keep backgrounds white or transparent. Use restrained green or blue accents.
Match the character family across all sources in a compiled presentation.
Reuse suitable approved artwork. Generate new artwork against the reference when needed.
The built-in image tool produced the approved September 30 artwork.
Nano Banana is also permitted when requested. The visual reference governs the result.
Preserve prompts, source attribution, alt text, and generated assets with the source slides.
Use native slide text for critical labels when practical.

## Content rules (Byron, 14-Nov-2026)

Learned editing the Metronomics Kick Off. They apply to every deck.

1. **Teach only what this session does.** No lines about later quarters ("confirmed at Q4", "comes later"). No slides for work the board places in a later session.
2. **The Mural board is the reference.** Every exercise slide matches an area on the client board, in its words and order. No board area, no slide.
3. **Byron's teaching wins where he has a rule.** Check his articles, other decks and the board before keeping a source deck's version.
4. **Every exercise slide says what to do.** A bare question confuses. State the action on screen in one short line.
5. **One worked example beats a step-by-step build.** Show the finished thing once, clearly.
6. **One name per idea, everywhere.** Slides, artwork and notes use the same term.
7. **Pictures fit the deck and the slide.** Use only the character style above, checked against the reference. The picture shows what the slide asks people to do. No picture beats the wrong one. When the diagram is the point, use full-width artwork (`art_full`).
8. **Show where we are.** At each new stage, show the cascade with what is done and what is next.
9. **Point at the example; don't redraw it.** To teach one part of a worked example, reuse the exact drawing, dim everything else, and add one callout. Add no boxes or new labels, and use the same words as the drawing's legend.
10. **Animate once, on arrival.** An animated SVG plays once each time its slide is reached and holds its last frame: no loops. Use `fill="freeze"`, never `repeatCount="indefinite"`, and set `"replay": true` on the artwork.
11. **Same subject, same image (Byron, 16-Nov-2026).** When two slides are about the same thing, such as the professional and personal good-news rounds, reuse the same picture. Do not invent a second scene for variety.

Learned building the Metronomics Q1 deck (Byron, 16-Nov-2026):

12. **Open with the session's purpose.** The "What would make today valuable?" slide shows the session's objective on a sticky, such as "Functional clarity with team accountability" at Q1. The close shows the same sticky checked.
13. **One continuing example in every deck.** Use our own subscription company everywhere: the same people, functions and numbers. Shannon's examples are a source to check against, not to copy. A person who holds two functions shows in red. The Kick Off's Function Chart and example pages are the canon for names, owners and numbers: check a later deck's example against them before adding a person or a figure (Byron, 16-Nov-2026: the Q1 Team View had invented a CEO, "Sam", where the Kick Off has Pat).
14. **Teach why, not only what.** Each part of a tool says on screen why it matters, then the question to ask. End each tool by asking what it changes: the 3HAG capabilities, the KFFM, the 1HAG and the QHAG.
15. **Build a picture before the plan it tests.** At Q1, the Market Map comes before the 3HAG pass. Its findings then test the 3HAG, the 1HAG and the QHAG.
16. **One slide per confirm pass.** At a quarterly, a BHAG, 3HAG or 1HAG pass uses its Kick Off test slide. Do not add a separate review slide.
17. **Shared notes say which session they serve.** A note that only one deck needs starts "At the Kick Off," or "At a quarterly,". Never write a slide number in a note. Name the slide instead.
18. **To check something the Kick Off taught, ask on the Kick Off's slide.** Reuse its slide by reference with a playlist `override`: a new title, one ask line (`support` on a card slide) and notes. Do not build a new grid or example. The team recognises what it agreed to, and the ask sits on top of it. The meeting check at Q1 is the model.
19. **A reused slide names its subject (Byron, 17-Nov-2026).** A slide moved out of its home section loses the slides that introduced it. Give it a title that names the thing: "Does your BHAG still hold?", not "Is the ambition clear, connected and exciting?". Use a playlist `override`.
20. **Name every label in a drawing.** A box that holds a priority says "Company priority #1" above it. A finished week says "Complete", never "Done" beside a "Done by" date. One idea keeps one word across every drawing in the deck.
21. **A path map with more than eight stages uses two rows.** One row of ten shrinks the labels below what a projector shows.
22. **A new meeting gets its own agenda slide.** The meeting check holds three cards. A fourth card does not fit: put the added meeting on the next slide.

Learned reviewing the Q3 deck (Byron, 23-Nov-2026):

23. **A check the team does in Metronome says so, the same way everywhere.** Start the slide's instruction line with "In Metronome: open [menu name]", then the ask. Copy the menu name exactly from Metronome's menu. Use it in the quarterly decks only, as a playlist `override`: a Kick Off team has no account yet. Use text, never a screenshot of Metronome. A full-width drawing slide cannot show the line yet.

Learned reviewing the Q3 deck (Byron, 24-Nov-2026):

24. **A later session checks. It does not teach again.** Once the team has the tool, one slide checks it: a title that asks, the ask on screen, and the teaching in the notes. Drop the example slide. The Function Chart check at Q2 and Q3 is the model. The session that first teaches the tool keeps its teaching slides.
25. **The check is on the screen.** A reused slide whose `override` changes only the notes still shows the old teaching. Change the title and the ask as well.
26. **Never assume where the team is.** One team arrives with the work finished, another with a draft, another with nothing. Write each slide so it is true for all three. Keep "draft", "later today" and "once we agree" off the screen.
27. **Every line on screen earns its place.** A person reading it cold must know why it is asked. Test a line before lifting it from the notes.
28. **Trace what each exercise needs.** When an exercise needs something the team must bring, an earlier session sets it as homework and this session checks it before the exercise starts. The A-Player grid needs a scorecard for every direct report, so direct reports have scorecards by Q3.
29. **Fix the pattern, not the slide.** When one slide is wrong, sweep the whole deck and its sister decks for the same fault. Bring Byron the full list before he finds the next one.
30. **A check asks whether the tool is being used, not only whether it is right.** Before removing a slide as a replay, ask what check it carries. The KFFM check walks all six levers every quarter: is each one being pushed, and what moved.

## Layouts

- `title`: opening headline and relevant illustration.
- `comp-story`: one idea with a human scene or simple supporting panel. With `art_full`, add `art_fit` for a short, wide drawing such as a stage map, so its panel hugs the drawing instead of filling the slide.
- `comp-causal`: a connected sequence of panels, with clearly visible blue arrows.
- `comp-decision`: two choices or a bounded set of up to four cards.
- `comp-rule`: a concise closing takeaway on a dark blue background.
- `about-timeline`: a presenter introduction. Name, role and intro on the left; a scrolling list of dated moments on the right. The row in focus grows its photo, logo or illustration under its text. Real mouse movement, wheel, keys and touch move the focus. After 5 seconds idle the list tours itself at 3.5 seconds per row and loops. Wheel and scroll keys inside the list never change slides.
- `comp-attempts`: up to four numbered attempt cards, each with a year, heading, support and outcome. Failed attempts carry an orange top border and outcome. One card may be the win, filled blue.
- `comp-figure`: one inline SVG figure from the library, styled with the shell's `fig-*` classes. Scripts, event handlers, styles and references are refused.

## Sequences, cards, and emphasis

Anything ordered runs green to blue: `#54b570`, `#4ca282`, `#438f93`, `#3b7da5`, `#326ab6`.
Use the full five for the BHAG to sprint lane cascade. For fewer steps, use green first and blue last.
Cards share one shape: white panel, thin border, 4-pixel top border in the sequence colour, and a numbered blue badge before the heading.
Bullets use green markers. Put the key term in bold blue.
Define a term with a hover box on the term itself, never a side panel. Use the source's wording word for word.
Open the hover box downward when the term sits near the top of the slide.
Speaker notes hold the full explanation of the slide, in Byron's words, complete enough to draft an article from (Byron, 22-Nov-2026). Anything that must happen in the room goes on the slide, not in the notes. No sources or credits in the notes; keep them in the source records.
EOA Meeting 4's `deck.css` in coaching-slides is the reference implementation until these patterns move into the shared shell.

Composition badges stay hidden in audience view.
Use `?review=template` to show them during template editing.
Preserve the approved hierarchy and whitespace when adapting content.

## Responsive behaviour and controls

Desktop uses the centered 16:9 stage.
Small or short screens use naturally scrolling slides with readable text.
Stack cards on narrow phones. Keep all content reachable without horizontal scrolling.
Do not compress a desktop slide into an unreadable phone thumbnail.
Vertical touch gestures scroll; horizontal swipes move between slides.
Offer visible previous/next controls and a slide count on small screens.
Keep tap targets at least 44 pixels and the menu clear of slide content.
Use the sidebar as a drawer below 1180 pixels. Keep its selected slide visible.
On small screens, the menu button and the controls share one solid toolbar at the bottom. Nothing floats over the slide.
On a small screen, tapping a drawing opens a zoom view inside the deck, with a Close button. Never open artwork in a new page.
Photos and the deck QR code do not zoom and never stand taller than the screen.
Definition boxes stay inside the screen: on small screens they open as a sheet above the toolbar.
Controls never hide on a touch screen.
Desktop controls stay quiet until approached or focused.
Support arrow keys, Home/End, N for notes, S for sidebar, and F for full screen.
Honor reduced-motion preferences.
In full screen, remove sidebar space and center the content.
On exit, restore the prior sidebar choice and preserve the selected slide.

## Verification before adoption

Check every populated slide for clipping, overlap, readable hierarchy, and artwork loading.
Inspect settled rendered screenshots, including the full content of scrolling phone slides.
Check these nine sizes:

- 1686 × 1267, owner desktop
- 1920 × 1080, full HD
- 1440 × 900, wide desktop
- 1366 × 768, projector
- 1280 × 720, presentation
- 1024 × 768, tablet landscape
- 768 × 1024, tablet portrait
- 390 × 844, phone portrait
- 844 × 390, phone landscape

Exercise navigation, touch-friendly controls, notes, full-screen entry/exit, and resizing.
Compile a playlist that reuses sources from different libraries.
Verify that artwork, notes, ordering, and provenance survive compilation.
A token check alone is not a visual pass.
Browser-sized phone checks do not establish physical-device compatibility.
Check the two phone sizes with device emulation (touch and a mobile viewport), not a narrow desktop window.
Drawings fill their panel. Their smallest type follows the reference-table floor above; the 16-Nov-2026 record lists two that do not yet meet it.
Keep a clear gap, at least 12 pixels, between content and the footer logo.
Test the last text line of every stacked-copy slide against the footer at 1440 × 900 with the sidebar open. A slide can fit the browser pane and still clip there (Q2, 17-Nov-2026).
A hover definition must show in full: hover each underlined term and read the whole box.

## Sharing

Keep editable source in GitHub. Share HTML presentations through the established hosting route.
Source libraries and the compiler live in this repository under `source/`.
Public copies can be published through `coaching-slides` GitHub Pages after separate publication approval.
A saved source change affects future builds; already-published decks change only after rebuilding and publishing.
