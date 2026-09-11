---
name: unity-specs
description: The single home for a project's design specs — one markdown file per feature, mechanic, screen, style rule, or code system, under specs/, each carrying numbered requirement ids, a code map, verification, open questions, and a notes/ideas log. Use whenever the user wants to write, read, update, split, or check a spec or design document; whenever a new feature or mechanic is being designed before any code is written; whenever behaviour gets decided in chat and would otherwise be lost; whenever a legacy monolith design doc needs splitting into specs; and before implementing anything, to find out whether a spec already governs it. Triggers on "spec", "specs/", "design doc", "write up the design", "what is the agreed behaviour for X", "requirement id", "is this specced", and on any request to decide how a mechanic, screen, or style rule should work.
---

# Specs

`specs/` is where the design of the game lives. Code is the implementation, `plans/` are
the execution logs (written with the `unity-plans` skill), any big `docs/` design file is a
legacy monolith on its way in here — but the answer to "how is this *supposed* to work"
comes from a spec, and if a spec and the code disagree, that is a bug in one of them and the
spec says which.

A spec is a **design document**, not a task list and not generated code documentation. It states what the thing is, what it does, and why — at the level a designer argues about, not the level a compiler cares about. Phases and checkboxes belong in `plans/`, which the `unity-plans` skill owns; keep them out of the spec whether or not that skill is loaded.

Nothing below is specific to one project. Read the project's own conventions first — the
`specs/` index if it exists, its legacy design docs, its test and audit entry points — and
use its names, ids and paths in place of the placeholders here.

## Layout

```
specs/
  README.md        the index — one line per spec, with its id prefix and status
  rules/           the rules of play                 (authority over the legacy rules doc)
  mechanics/       systems built on the rules        (abilities, progression, economy, quests)
  ui/              one spec per screen or panel
  style/           cross-cutting UI law              (authority over the legacy style doc)
  code/            architecture and tooling          (assemblies, saves, storefronts, pipelines, audits)
```

That taxonomy is a default for a game project, not a requirement. **Create only the folders you need, when you need them** — a tree of six empty directories is noise. And if the project already keeps its design material somewhere (`Documentation/`, a wiki export, a single `GDD.md`), work inside that location and its conventions rather than opening a second home for the same material. Two homes is how a project ends up with two contradictory answers to the same question.

One file per thing. A spec that needs two headings to describe two unrelated things is two specs. A spec under ~40 lines that only exists to be linked from another is a section of that other one. Past roughly 150 lines, or two clearly separable subjects, split it — otherwise `mechanics/economy.md` becomes the monolith again in a new folder.

Filenames are kebab-case nouns: `dash.md`, `chapter-select.md`, `type-scale.md`. Not `dash-system-v2-final.md`.

## Anatomy

```markdown
---
name: dash
prefix: DASH
status: designed
updated: <date>
---

# Dash

The dash is the player's only way out of a committed attack, so its cost and its
i-frames are what decide whether a fight reads as fair. Make it free and every
other defensive option dies; make it slow and the game stops being about movement.

Related: `specs/rules/stamina.md`, `specs/ui/hud.md`

## Design

DASH-1  A dash consumes one stamina pip at the moment of input, not on landing.
DASH-2  The player is invulnerable for the opening window of a dash
        (`DashConfig.IFrameDuration`), which is tuned to cover an attack wind-up.
DASH-3  A dash cannot be cancelled once it has started.

## Code

| what | where |
|---|---|
| dash resolution | `DashController` — `Player/` |
| stamina cost | `StaminaPool` — `Player/` |
| tuning | `DashConfig` — `Assets/Config/Player/DashConfig.asset` |

## Verification

| id | how |
|---|---|
| DASH-1 | `DashTests.InputConsumesPipImmediately` |
| DASH-2 | `DashTests.IFramesCoverConfiguredWindow` |
| DASH-3 | playtest: test arena, dash then release the button — dash runs to completion |

## Open questions

- [ ] Does a dash off a ledge keep its i-frames through the fall?
- [x] ~~How long are the i-frames~~ → matched to the attack wind-up, authored in
      `DashConfig` (<date>)

## Notes & ideas

- A second dash charge, refilled on a parry, would give late-game builds something
  to spend on. Not designed, not promised.
- `DashController` reaches into the input system directly; worth an interface if
  AI ever dashes.
```

### What each part is for

**Frontmatter** — `status` is one of:

| status | meaning |
|---|---|
| `draft` | still being interviewed; open questions outnumber requirements |
| `designed` | agreed, not built yet |
| `implemented` | built, and every requirement has a passing line in Verification |
| `drifted` | the code and the spec disagree; the spec says which one is wrong |

`drifted` is a real state, not a failure — set it the moment you notice the mismatch, name the mismatch in Notes, and move on. Silently editing the spec to match whatever the code happens to do destroys the only record of what was intended.

`updated` takes its date from the environment or from the last commit touching the file. Never from your own sense of what today is — a confidently wrong date is worse than none.

**The opening paragraph** carries the *why*. Not "this spec describes the dash system" — that is the title's job. Why does the feature exist, and what would be lost without it. This is the part a future session cannot reconstruct from the code.

**Design** — numbered requirements, one per line, each independently checkable. Prose between them is fine when a group needs a frame. State behaviour, not implementation: *what* is true, not which class makes it true. A requirement that cannot be judged true or false is a note, so move it down.

**Tunables live in the asset, not in the requirement.** This is the drift that kills specs fastest: the spec says one stamina pip and 0.15s, a balance pass edits the ScriptableObject, and now the spec is a lie with a version number on it. So a requirement states the *invariant* and names where the number is authored:

> DASH-2  The player is invulnerable for the opening window of a dash (`DashConfig.IFrameDuration`).

not

> DASH-2  The player is invulnerable for the first 0.15s of a dash.

Put the asset path in the Code map, so editing that asset is visibly a design change. Write the literal number into a requirement only when the number *is* the design — a hard cap, a rule of play, a platform limit — and say so, because you have just made the balance team's edit a spec edit.

The same applies to behaviour authored in a prefab or scene rather than in code. If a wired reference, a component's presence, or a layer assignment is load-bearing, the requirement names it and the Code map holds the path. A design that lives only in a prefab and nowhere in the text is invisible in review and invisible in a diff.

**Ids are permanent.** `DASH-2` is quotable from a test name, a code comment, chat, a plan doc. So:

- Append new ids at the end of their group. Never renumber to tidy up.
- A retired requirement stays, struck through, marked `(withdrawn <date>, <reason>)`.
- The prefix is registered in `specs/README.md`. Check it before inventing one — collisions make every citation ambiguous.

**Code** — where to look, not how it works. Two to six rows. Its value is saving a future session a repo-wide sweep, so prefer **the directory plus the type name** (`DashController` — `Player/`) over an exact file path. Type names survive a move, paths do not, and a stale path costs more than the sweep it was meant to save. Use an exact path only where the path *is* the identity: a single authoritative asset, a config file, a build script.

**Verification** — every requirement gets a row: a test name, a project audit that must report zero, or a *repeatable* playtest step naming where to stand and what to press. A requirement with no honest verification gets `unverified` in that column rather than an invented test name — the gap is information. (The `unity-plans` skill states this rule in the same words; if you change one, change the other.)

**Open questions** — unresolved decisions live here instead of being quietly guessed. Answer one by ticking it, striking the question, and appending the answer plus the date; then fold it into Design as a requirement if it changed behaviour.

**Notes & ideas** — the scratch space: future ideas, todos, smells, things worth remembering. Nothing here is a commitment, and nothing here is authority. Keeping it inside the spec is the point — an idea about dashing is findable next to the dash design, and lost anywhere else.

## Writing a spec from a half-formed idea

Research, then ask, then write, in that order.

1. **Find what already exists.** Grep `specs/`, the project's legacy design docs, `plans/`, and the code for the feature's vocabulary. Half of what you were about to ask is already decided somewhere, and asking anyway is how a spec ends up contradicting the shipped game.

   Grep first, read second — use the `narrow-reads` skill. Research is a deliberately wide phase and will exceed that skill's per-answer line budget; keep it cheap by making the sweep return **paths and line numbers**, then window into the two or three places that actually matter. Per artifact: a spec is written to be read whole, so read one whole; `specs/README.md` whole, it is a map and it is cheap; a plan doc **never** whole — outline it with `grep -n "^## \|^- \[ \]"` and window into the one phase. Same for the legacy monolith: grep for the section heading, `sed -n` the section.

2. **Ask one question at a time.** Absorb the answer before choosing the next question, because the answer usually changes what matters next. A batch of four questions written up front is four guesses about which things are load-bearing.

   Ask only what you cannot resolve yourself and what actually changes the design. Good questions are concrete and narrow enough to answer in a word:

   > Does a dash cost stamina on input, or only if it actually moves you?

   Not:

   > What should the dash system do?

   Things to probe, roughly in order of how much they change the rest: the cost, the timing, what it interacts with, what it must *not* do (non-goals are as load-bearing as goals), and the failure cases — what happens when the resource is empty, the animation is interrupted, the input arrives mid-transition.

   Stop when the remaining unknowns no longer change any requirement. Those become open questions in the file, which is where they belong — a spec with three open questions is honest, an interview with thirty answers is exhausting.

3. **Write the file, register it in the index.** Then say in one or two lines what you assumed and what is still open. Do not restate the spec back in chat; the file is the deliverable.

## Updating a spec

A spec earns trust by being current, so it changes with the design and with the code:

- **Design decided in chat** — it lands in the spec, as a numbered requirement, before the conversation moves on. A decision that exists only in a transcript is lost.
- **Code changed** — check the Code map and the Verification rows still hold. If behaviour changed deliberately, edit the requirement and bump `updated`. If it changed accidentally, set `status: drifted` and say so.
- **A tuning asset changed** — normally not a spec edit, which is the whole point of keeping the number out of the requirement. It *is* a spec edit when the new value breaks an invariant the spec states, or when the field itself was renamed or moved.
- **Requirement removed** — strike it, do not delete it. Somebody's test may still cite it.
- **New spec** — add its line to `specs/README.md` and check the prefix is free.

Citing ids from code is welcome where it explains a non-obvious constraint (`// DASH-1: pip is spent on input, not on landing`) — that is a *why* comment. It is not a licence to annotate every method.

## Splitting a legacy design doc

A project that predates `specs/` usually has one or two big markdown files carrying all of it. They are the source material for `rules/` and `style/`, and they shrink into indexes one section at a time. Never in one sweep — a 34 KB rules file rewritten wholesale is unreviewable.

Per section:

1. Copy the section into its spec, then turn its prose into numbered requirements. Preserve the existing authority: the monolith's rule numbers and any `UI-D9`-style ids are already cited from tests, code and chat, so carry them into the Design or Verification line rather than replacing them with fresh ids.
2. Replace the section body in the monolith with a one-line pointer to the spec.
3. Never delete source text before the spec holds it. Diff the two if the section was long.

Migration is opportunistic: split the section you are already working in, not the whole file because you happened to open it.

## Reading a spec

`specs/README.md` first — it is the map, and it is cheap. Then the one spec, read whole. Sweeping six of them to answer one question is not reading, it is dumping; grep for the id if you were given one.

## Anti-patterns

- **A spec that describes the code.** If a paragraph would change when a class gets renamed, it belongs in the Code map as a type name, or nowhere.
- **Numbers copied into requirements.** The asset is the authority; the requirement names it.
- **Renumbering.** Breaks every citation, silently.
- **Inventing verification.** A plausible-looking test name that does not exist is worse than `unverified`.
- **Interviewing for things the repo already answers.** Grep first.
- **Phases and checkboxes in Design.** That is a plan. Link to it.
- **One giant `specs/game.md`.** That is the monolith again, in a new folder.
- **Editing a spec to match surprising code** without recording that it was a surprise.

## When to skip this skill

Bug fixes, refactors, and anything that does not change designed behaviour need no spec — though if the fix reveals that the code never matched the spec, say so and mark it `drifted`. Throwaway experiments do not get specs either; they get a line in the relevant spec's Notes if they taught you something.
