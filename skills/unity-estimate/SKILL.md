---
name: unity-estimate
description: Estimate how long a Unity project — any genre or platform (2D/3D, PC, mobile, multiplayer, VR, console) — or one of its milestones or features will take, from design docs, GDDs, specs or plans, and deliver it as an .xlsx — one row per task with min/max hours, who does it (Developer or AI), sparse comments, totals, and working days per Claude subscription tier (Pro, Max 100, Max 200) under 5-hour usage windows. Use whenever the user says estimate, scope, size, cost out, forecast, "how long will this take", "how many hours/days" about a Unity game or app, or hands over game docs asking for a timeline or estimate spreadsheet — even if they don't say xlsx or Unity. Not for non-Unity projects, writing implementation plans (unity-plans), design specs (unity-specs), or logging time already spent.
---

# Unity estimate

Turn design docs for a Unity project (any genre or platform) into an estimate spreadsheet that a solo developer working with Claude Code can plan by. The only deliverable is the .xlsx, plus a short summary in chat. Don't write plans, specs or code.

The numbers are calibrated against a real reference project: a mid-size, single-player PC game in Unity, built by one developer with Claude Code (Opus) on Pro. Read `references/calibration.md` before sizing anything. It has measured AI hours per shipped feature, Pro window capacity, Developer-only defaults, and the schedule math. Generic industry numbers are far too slow for AI-driven work and far too fast for Pro-limited work.

## 1. Read the docs, then check what exists

Read every doc you were given. For large files, read the section list first, then only the parts you need. Pull out features, screens, content counts (levels, enemies, items, languages), platforms, the art/audio source, and release scope. Also note which parts fall outside what the reference project measured: 3D controllers, physics, multiplayer, mobile, VR, consoles, level building, graph shaders and similar. Those sections are sized differently (step 3).

If the work lands on an existing codebase, look at what is already built before sizing: the repo, `plans/`, `specs/` and recent commits. **Estimate only the remaining work.** Design docs often describe features that are half-built, amended mid-build, or partly cut. Sizing the whole doc as new work is the easiest way to be wrong by 2×.

## 2. Ask what moves the number

Batch the open questions into one AskUserQuestion call. Ask only what the docs and repo leave unclear, in roughly this order of impact:

1. **Scope slice**: the whole doc, or a first slice (MVP, demo, "build order" subset)? Do amendments, stretch sections and "later" ideas count?
2. **Baseline**: from scratch, or on existing code? If some of it is built, what is done?
3. **Release scope**: prototype only, demo, or full store release? Which platforms?
4. **Art/audio source**: bought packs (Developer import time), someone else making them (out of scope, but integration counts), or none yet?
5. **Developer hours per working day**: default 8. The reference project was built at 2–3 h/day, but the hourly rates don't change with day length, only the calendar does.
6. **Model**: Opus (calibration default) or Sonnet. Sonnet burns a Pro window more slowly. Note it in the Schedule sheet instead of silently changing the capacity.

Don't ask for the subscription tier. The Schedule sheet shows Pro, Max 100 and Max 200 side by side. If you can't ask (non-interactive run), pick the most literal reading of the docs, then list every assumption in the chat summary.

## 3. Size top-down: feature budget first, rows second

Summing many small row estimates inflates detailed docs, because each row gets its own padding. In a backtest, a 690-line design doc for an items-and-modifiers system was split bottom-up into 23 AI rows, which came to 2× what the feature actually took (~9 AI h). So:

1. **Budget each feature against the calibration anchors.** Find the closest shipped reference feature and scale it by content count and novelty. New systems with UI ran at ~1.2 h per plan phase. Features that reuse existing seams ran at ~0.4. Most features are 2–10 AI h.
2. **Then split that budget into rows** so the sheet is readable. Aim for 2–8 rows per feature, and keep AI rows at about 0.5 h min or more. Merge anything smaller into its neighbour.
3. **Check the result.** If a feature's rows add up to more than ~1.5× its closest anchor, merge rows or explain the extra in a comment (new tech, a big content count, a known risk).

For a from-scratch project, add a **Prototype / core loop** section first (budget in calibration). Multiply the first two feature sections after it by 1.5×, because conventions and tooling don't exist yet. Keep project setup, asset imports, menus and store work in their own sections, not inside the prototype.

**Sections outside the calibrated areas.** The reference anchors come from a single-player, PC, logic- and UI-heavy game, exactly where the AI is strongest. For multiplayer, mobile, 3D feel, physics, VR, consoles, level building, graph shaders and similar work, use the "Outside the calibrated areas" table in calibration.md:
1. Scale the closest anchor by the area's multiplier.
2. Add the Developer rows it lists.
3. Tag the section with `"uncalibrated": "<area>"`.

Skipping this underestimates exactly the parts where AI help is weakest. The tag makes the Schedule sheet show how much of the estimate rests on judgment rather than measurement.

If the project has checks that every change must pass (localization or UI audits, test suites), fold that cost into each feature's rows. Don't add separate rows for it.

## 4. Who does it

Each row is **AI** or **Developer**. AI rows already include the developer's prompting, review and quick editor checks, since that's how the reference hours were measured. Don't add supervision rows.

Make a row **Developer** when the AI can't do it, does it badly, or it's cheaper by hand:
- Project setup: engine version, packages, render pipeline, source control/LFS, store SDK accounts
- Importing and configuring asset packs (art, UI, VFX, audio, fonts): import settings, broken materials
- Animation setup: animator controllers, clip wiring, rigging, timing
- Visual scene and prefab layout judged by eye
- VFX, shader and "juice" tuning by feel
- Playtesting and balance tuning
- Builds, store pages, store assets, platform submission
- Anything behind an account, payment, legal step or external website

Mixed features get both kinds of row. For example, AI builds the screen logic and prefab structure, and the Developer does the visual layout pass.

## 5. Min and max

- **Min**: the spec is clear, conventions exist, and the first build is accepted.
- **Max**: one rejected iteration or a mid-build redesign. Both happened in the reference project: a screen layout built and thrown away, and a system amended mid-build.

AI rows: keep max/min at 1.5–2.5×. Developer rows and rows in uncalibrated sections can go to 3×, because nobody measured them. Go wider only when the docs are vague, and say why in the comment.

## 6. Comments

Leave the comment cell empty unless it explains *why* a row exists or a non-obvious call: a surprising owner, an unusually wide range, a dependency, a risk, an assumption about unclear scope. Never restate the task name. Most rows should have no comment. Section rows can carry a comment when it applies to the whole feature.

- Good: `Developer: the pack ships Built-in RP materials; converting to URP by eye is faster than prompting.`
- Bad: `Implement the quest system.`

## 7. Build the xlsx

Write the rows to a JSON file in the scratchpad. Run the script with the Bash tool, using the full path from this skill's base directory (PowerShell doesn't expand `~` for python arguments):

```bash
python "<skill base dir>/scripts/build_estimate.py" "<scratchpad>/estimate.json"
```

```json
{
  "project": "MyGame",
  "output": "D:/Games/MyGame/docs/MyGame-estimate.xlsx",
  "assumptions": {"dev_hours_per_day": 8},
  "rows": [
    {"section": "Project setup"},
    {"name": "Unity project, URP, Input System, Git LFS", "min": 2, "max": 4, "owner": "Developer"},
    {"section": "Core loop", "comment": "x1.5: first feature on a new codebase."},
    {"name": "Player turn state machine", "min": 1, "max": 2, "owner": "AI"},
    {"section": "Online co-op", "uncalibrated": "Multiplayer", "comment": "x2.0 AI: desync bugs only show with real clients."},
    {"name": "Netcode for GameObjects session + player spawn", "min": 2, "max": 5, "owner": "AI"},
    {"name": "Two-client test pass", "min": 1, "max": 3, "owner": "Developer"}
  ]
}
```

- **Uncalibrated sections:** tagging a section with `uncalibrated` makes the script add a red warning to the Schedule sheet. It lists the areas and their share of max hours, and says "LOW CONFIDENCE" when they are more than half.
- **Don't write overhead rows.** The script appends an **Overhead** section itself: Planning & specs at 8% and Fixes & integration at 12% of AI feature hours, 20% in total (the reference measurement). They're live formulas, so they follow any edits in Excel. Override with `"overhead": {"planning": 0.08, "fixes": 0.12}`, or turn them off with `"overhead": false`.
- **Assumptions keys** (all optional): `dev_hours_per_day`, `pro_window_ai_hours`, `budget_share`, `windows_per_day`, `window_clock_hours`.
- **Output location:** next to the design docs as `<Project>-estimate.xlsx`, unless the user named a path.
- **Language:** task names and comments follow the language of the docs.

The script writes two sheets. **Estimate** has the task columns, totals and Developer/AI subtotals. **Schedule** has editable assumptions and working days/weeks per tier. It also prints the computed totals, so you can report them without opening Excel.

## 8. Report

Keep the chat reply to a few lines:
- The file path
- Total min–max hours, split Developer / AI
- Working days on Pro / Max 100 / Max 200
- Which constraint binds (AI budget or the developer's day)
- The uncalibrated share, if any, and which areas it covers
- Any assumptions made without asking
