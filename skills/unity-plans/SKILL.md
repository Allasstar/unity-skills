---
name: unity-plans
description: Plan multi-step or multi-session Unity work as a durable, resumable file under plans/ — a progress table, phases with per-item checkboxes, the scenes/prefabs/assets each phase touches, agent-runnable checks plus repeatable playtest protocols, build and ship steps, and a handoff a future session can resume from with zero prior context. Use whenever the user wants to plan, design, scope or start building a feature, system, screen or milestone, says "plan", asks for phases or a roadmap, or hands over work too big for one sitting; and whenever an existing plans/*.md is being resumed, updated or closed. Reads specs/ first and stops to ask whenever the work has no spec or contradicts one. Not for planning that produces no code or asset change — a meeting agenda, a schedule, a shopping list of ideas — and not for a bug fix or refactor finished in one sitting.
---

# Unity plans

Three artifacts, three jobs. `specs/` says what the game is *supposed* to do and is the
authority on design — see the `unity-specs` skill. `plans/` says how a piece of it gets
built, and becomes the log of it being built. The code is the implementation. When a plan
and a spec disagree, somebody is about to build the wrong thing, which is why the spec
check below comes before anything else.

The plan file — not the conversation — is the source of truth for execution: what to do,
what is done, how it was verified (code *and* feel), and how to ship. A future session
resumes from the file with zero prior context, so anything that lives only in chat is lost.

**Use when** the work may outlive this session: a system, a feature, a screen, a milestone.
**Skip** for a bug fix, a refactor, or anything finished in one sitting — a plan file for a
two-edit job is overhead, and the noise makes the real plans harder to find.

**Unity reality:** most state lives in serialized assets — scenes, prefabs,
ScriptableObjects, addressables, input actions, TMP font assets — that do not diff cleanly,
and "done" usually means *feels right*, not *compiles*. A plan that tracks only C# is blind
to half of what changed.

Nothing below is specific to one project. Read the project's own conventions — its
`specs/` index if it has one, an existing `plans/*.md`, `CLAUDE.md`, the test and audit
entry points — and use its names, ids and tooling in place of the placeholders here.

## The spec check — before you plan anything

If the project keeps specs, read the index (`specs/README.md`) — it is the map, and it is
cheap — then the specs covering this feature's vocabulary. Three outcomes:

**A spec exists and agrees.** Cite its requirement ids in the phase items and Verification
rows. Do not restate the design in the plan: the plan says what to build, the spec says
what it must do, and two copies of a design drift apart within a week. List the governing
specs in the plan's **Context**.

**No spec covers this.** Stop and ask the user which they want:

> Nothing in `specs/` covers the dash ability. Write the spec first with the `unity-specs`
> skill, or plan it now and leave the design as an open question?

Ask rather than choose, because the answer depends on how settled the design is in the
user's head, which the repo cannot tell you. If they choose plan-only, say so in
**Decisions & Open Questions** — a plan that silently invents design is how undiscussed
behaviour ships. In a project with no `specs/` folder at all, say that once and carry the
design in the plan's Context; do not conjure a specs tree nobody asked for.

**A planned item contradicts a spec.** Stop and ask which one is wrong, quoting both:

> `DASH-3` says a dash cannot be cancelled once started, but Phase 2 adds a cancel on
> release. Does `DASH-3` change, or does the phase?

Then apply the answer: if the spec changes, edit it under the `unity-specs` rules before the
plan item goes in. If the plan changes, fix the item and record the conflict in
**Decisions** so nobody relitigates it. Guessing here is the one failure this skill exists
to prevent — the cost of asking is one message, the cost of being wrong is a built feature
that contradicts the law.

**Editing a spec without the `unity-specs` skill loaded** — the non-negotiables, so you do
not have to guess: never renumber; strike a withdrawn requirement rather than deleting it;
bump `updated`; keep tuning numbers in the asset and name the asset in the requirement; and
never edit a requirement to match surprising code without recording that it was a surprise.

## 1. Understand the scope first

An unasked question is a future bug; an interrogation is also a failure mode. Ask what
actually changes the plan's shape, propose a sensible default for the rest, and let the
user correct. Converge in a round or two.

Read before you ask — `ProjectSettings/ProjectVersion.txt`, `Packages/manifest.json`, the
governing specs, the folder structure. A question whose answer is already in the repo
spends the user's patience on nothing. Likewise, anything a spec already decides is not an
interview question; it is a citation. Use the `narrow-reads` skill for the sweep: grep for
line numbers and paths, window into what matters, and never `cat` a scene or prefab.

What to drive out, beyond generic scope and success criteria:

- **Affected assets** — which scenes, prefabs, ScriptableObjects, materials, input actions,
  localization entries. Anything generated or imported?
- **Content vs systems** — code-only, content-only, or both? Who authors the art/audio side?
- **Success criteria** — measurable (a green suite, an audit at zero, a frame-time budget)
  **and** feel ("the dash reads as instant, no input lag"). Both, or the plan cannot say
  when it is done.
- **Non-goals** — scope drift kills more milestones than missing requirements do.
- **Failure cases** — save corruption, an interrupted transition, an empty collection, a
  platform suspend, alt-tab mid-sequence.
- **Render pipeline / perf budget** — when the work touches rendering or hot paths;
  otherwise it is boilerplate the Context does not need.

Every answer worth asking for lands in the plan's **Context**, or the interview was wasted.

## 2. Write the plan

Save to `plans/<descriptive-name>.md` at the repo root, tracked in git. Pick a short local
id prefix for this plan's decisions and open questions — they get quoted in chat and in
later phases, so they are permanent the same way spec ids are. Match the project's existing
plans if they already have a convention. Dates come from the environment or from git, never
from your own sense of the date.

### Two shapes

A **light plan** is Progress, Context, the phases with their Verification Plan and
Verification Results, and Decisions & Open Questions. That is the floor, and it is the right
shape for most two-to-four phase features.

The rest is added when it earns its place:

- **Affected Assets** per phase — the moment a phase touches serialized state. Which, in
  Unity, is most of them; skip it only for genuinely code-only work.
- **Final Recap** and **Build & Ship Plan** — when a build target is actually in scope.
  A feature branch that merges and ships with the next release does not need a ship plan of
  its own.

Start light and promote when the work turns out bigger than it looked. Never the reverse:
deleting sections from a plan mid-flight loses the record.

```markdown
# <Work Title>

<1-2 sentence goal and scope.>

Written <date> against `<branch>` @ `<sha>`. Local ids are `<PREFIX>-n`.

## Progress
| # | Phase | Status | Verified |
|---|-------|--------|----------|
| 1 | <Title> | Not started | — |
| 2 | <Title> | Not started | — |

**Now:** <the single next unchecked item, phase and task>

## Context
- **Specs:** <governing spec paths + their id prefixes — the design lives there, not here.
  "none, design carried below (<PREFIX>-O1)" if the user chose plan-only.>
- **Engine:** Unity <version>, <render pipeline>. Assemblies: <asmdefs, or Assembly-CSharp>
- **Surface:** <the scene / prefab / screen this work lives in, with paths>
- **Success criteria:** <measurable + feel>
- **Non-goals:** <explicitly out of scope>

## For Future Agents
The plan file is the source of truth; the conversation is not.

**Resuming:** read **Progress** and **Now**, then only the current phase. Do not read the
plan whole — completed phase summaries are history, and a finished plan is mostly history.
`grep -n "^## \|^\*\*Now:"` gives you the map; window into the one phase. See the
`narrow-reads` skill.

**Working:** tick `- [x]` items; when a phase completes, set its **Progress** row, update
**Now**, run the **Verification Plan** and record the outcome in **Verification Results**,
then write the **Phase Summary** — what was done, key decisions, **which scenes/prefabs/
assets changed**, and whatever a zero-context session needs to continue. Never rewrite a
completed phase summary; append a correction. Log anything decided or unresolved in
**Decisions & Open Questions**. Keep the governing specs in step (see below). When every
phase is done, fill in **Final Recap** and **Build & Ship Plan** if the plan carries them,
then close the plan out.

## Phase 1: <Title>
Status: Not started   <!-- Not started | In progress | Blocked | Complete -->

- [ ] <concrete code/asset item, citing the requirement it satisfies where one exists>
- [ ] <concrete item — "Disable the input action for the duration of the dash (DASH-3)">

### Affected Assets
- <scene / prefab / SO / localization entry paths this phase touches>
- Revert path: <branch or commit to reset to if this phase is abandoned>

### Verification Plan
**Agent-runnable:**
- <command + expected result — compile, test id, audit that must read zero>

**Playtest (human, repeatable):**
- <where to stand, what to press, the observable pass/fail — not "test it manually">
  e.g. "Load the test arena, dash into a wall → no clip, snaps to the surface, no warnings."

### Verification Results
_(date, what ran it, pass/fail, anything observed)_

### Phase Summary
_(write when the phase completes)_

## Phase 2: <Title>
Status: Not started
Depends on: Phase 1

- [ ] <actionable item>

### Affected Assets
### Verification Plan
### Verification Results
### Phase Summary

## Decisions & Open Questions
- **<PREFIX>-D1 (decided):** <choice + why, so nobody relitigates it>
- **<PREFIX>-O1 (open):** <question + who or what unblocks it>

## Final Recap
_(write when all phases complete)_

## Build & Ship Plan
_(write when all phases complete)_
```

Keep **Progress** at phase granularity. Do not mirror the checkboxes there — two copies of
one list drift, and the phase sections already hold the detail.

**When a phase is superseded** — the design changed mid-build, or the author saw it built
and rejected it — do not delete or rewrite it. Add the replacement as a suffixed phase
(`Phase 4R`), mark the old rows `Superseded by 4R (<PREFIX>-Dn)`, and put a short note near
the top saying what was rejected and why, in the author's own words where you have them.
The record of a wrong turn is worth more than a tidy file: it is what stops the next
session taking the same turn.

## 3. Keep the specs in step

A phase that implements requirements is not done when the code compiles — it is done when
the spec says so too. In the same edit that flips a phase to Complete:

- Fill those requirements' **Verification** rows in the spec with the test, audit or
  playtest step that now covers them, and bump `updated`. A requirement with no honest
  verification gets `unverified` in that column rather than an invented test name — the gap
  is information. (The `unity-specs` skill states this rule in the same words; if you change
  one, change the other.)
- Move the spec's `status` to `implemented` only when *every* requirement has an honest
  verification line — not when most do. If some are still owed, leave it `designed` and say
  what is owed.
- If what got built differs from what the requirement says, that is the contradiction case
  from the spec check, arriving late: set `status: drifted`, name the mismatch in the spec's
  Notes, and ask whether the code or the spec is wrong. Do not quietly edit the requirement
  to match the code — that erases the only record of what was intended.

Design settled in chat while working a plan belongs in the spec, as a numbered requirement,
before the conversation moves on. The plan records that it happened; the spec holds it.

## 4. Closing a plan out

A plan that never closes turns `plans/` into a pile, and **Now** stops meaning anything
because five files all claim to be current.

When every phase is Complete and the work has landed:

- Add `Status: Shipped <date>` (or `Abandoned <date>, <reason>`) under the title.
- Replace **Now** with `— closed`.
- Move the file to `plans/archive/`.

`plans/` holds live work only. Archived plans stay in git and stay greppable, which is all
anybody ever needs from them again.

## Code validation

Confirm the code compiles and the suite is green before leaning on a playtest — a build
check is cheap and catches what a human tester would waste twenty minutes finding.

If the project exposes a live-Editor bridge (a Unity MCP server, a pipeline HTTP endpoint,
`unity-cli`), drive the open Editor through it — recompile, run the edit-mode suite, read
the console. That is the fast path during iterative work, and usually the only way to reach
scene and prefab state at all.

Headless, when no Editor is running — close it first, or the project lock fails the run,
and invoke the exact version from `ProjectSettings/ProjectVersion.txt`:

```
"<UnityHub>/Editor/<version>/Unity" -batchmode -nographics -quit \
  -projectPath . -logFile Logs/compile.log
# the exit code is NOT reliable for script errors — grep the log:
grep -E "error CS|Compilation failed" Logs/compile.log   # expected: no matches
```

For a trustworthy exit code, add a CI method that compiles via `CompilationPipeline` and
calls `EditorApplication.Exit(1)` on error, then run it with `-executeMethod`. The same
hook surfaces IL2CPP and link errors a plain compile misses. Tests run headless via
`-runTests -testPlatform EditMode -testResults <path>`.

Whatever audits the project already has — a UI audit, a localization audit, a naming check
— count as agent-runnable verification. Name them in the Verification Plan with the number
they must report, so a future session can re-run them without hunting.

## Build & Ship Plan

Written when the phases are done, not before, and only when a build target is in scope. Per
target: the `-executeMethod` + `BuildPipeline` entry point, scripting backend and IL2CPP
settings, define symbols, version bump, addressables output if used. For a store target, the
upload command and its configuration — e.g. `steamcmd +run_app_build` with the app's VDF —
and which appid, depot and branch the build goes to.

## Common mistakes

- **Planning past a spec.** No spec, or a contradiction, and the plan gets written anyway on
  a guess. Ask. It is one message.
- **Restating the design in the plan.** Cite the requirement id instead; the copy will drift.
- **Vague items.** Each checkbox is a concrete task ("Cancel the dash on button release"),
  not a theme ("improve movement").
- **Stale Progress table.** The table and **Now** are the first thing read on resume. Update
  them in the same edit that flips a phase to Complete.
- **Reading the whole plan to resume.** Progress, Now, current phase. The rest is history.
- **Interview answers that never land in Context.** The next session asks all over again.
- **Punting to playtest what a compile, test or audit could catch.**
- **Vague playtest steps.** "Test it manually" verifies nothing. Give the scene, the setup,
  the action, the observable pass/fail.
- **Forgetting affected assets.** A C# diff is visible; a rewired prefab reference or a
  tweaked ScriptableObject is not. List them or a future session is blind.
- **Pre-filling summaries.** Phase summaries, verification results, recap and ship plan stay
  placeholders until that work actually happened.
- **Full ceremony for a two-phase feature.** Start light, promote if it grows.
- **Never closing a plan.** Five live plans and five stale **Now** lines is no plan at all.
- **Leaving the spec behind.** A shipped phase whose spec still reads `designed` with empty
  Verification rows means the next session cannot tell what is real.
