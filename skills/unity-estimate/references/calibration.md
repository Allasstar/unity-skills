# Calibration — reference project

The reference project is a mid-size, single-player PC game in Unity 6. It's turn-based and logic-, UI- and data-heavy, with a 3D board, a run map, meta-progression, localization and store integration. One developer built it with Claude Code on **Opus** with a **Pro** subscription. At measurement time the repo held ~56k lines of C#, ~280 scripts, ~50 prefabs and 4 scenes.

The measurements come from Claude Code transcripts covering 25 weekdays (about 5 weeks). "Active hours" means session time with gaps capped at 15 min, so it includes the developer's prompting, reading and quick checks. That's why AI rows in an estimate already include supervision.

## Capacity (what drives the Schedule sheet)

| Measure | Value |
|---|---|
| Active AI hours per 5 h window, median | 1.95 h (p90 2.9, max 3.6) |
| Hit the window limit | most windows |
| → `pro_window_ai_hours` (100% of a Pro window) | **2.0 h** |
| `budget_share` (plan to use only this much) | **0.8** |
| `windows_per_day` | **2** |
| Pro AI capacity per working day | 2 × 2.0 × 0.8 = **3.2 h** |
| Cross-check: real average | 86.9 AI h over 29 session days (25 weekdays + 7 weekend days) = **3.0 h/day** |
| Output tokens | ~260k per active hour; ~460k per Pro window (median) |
| Developer's own time per day | ~2–3 h, almost all inside AI sessions |

The reference project was built part-time. The per-hour and per-feature rates below don't depend on that. The day length (`dev_hours_per_day`, default 8) only changes the calendar, and on Max tiers it's usually the constraint that binds.

Tier budget multipliers relative to Pro: Max 100 = 5×, Max 200 = 20×. A window never yields more than `window_clock_hours` (5 h) of AI work.

```
ai_per_window = min(5, pro_window_ai_hours × multiplier × budget_share)
ai_per_day    = ai_per_window × windows_per_day
working_days  = ceil(max(AI_hours / ai_per_day, (AI_hours + Dev_hours) / dev_hours_per_day))
```

On Pro, the AI budget is the bottleneck, and the developer has spare hours for Developer rows. On Max, the developer's own day becomes the bottleneck, which is why Max 100 and Max 200 often come out the same. Weekly usage caps, weekends and holidays are ignored.

## Measured AI hours per feature

Sessions were attributed to the next plan-named commit, so treat these as ±20%. A "phase" is one plan phase, sized as one coherent change.

| Feature type | What it delivered | Phases | AI h | h/phase |
|---|---|---|---|---|
| Core rules rework | Removed a board mechanic; new turn resolution order; 3 game modes | 5 | 4.4 | 0.9 |
| Equippable items + modifiers system | Item framework, ~24 content items, HUD strip, offer screen, tooltips, enemy AI using it | ~7 | 9.2 | 1.3 |
| Run map | Node map, seeded runs, node types, drops, persistent HP between nodes | 7 | 8.1 | 1.2 |
| Main menu shell | Two screens, section navigation, currency row, settings, credits | 7 | 7.6 | 1.1 |
| Quests | Stat-tracking layer, quest model, UI, rewards | 5 | 2.1 | 0.4 |
| Meta upgrade tree | Tree UI, ranked nodes, economy nodes, pagination | 8 | 4.9 | 0.6 |
| Crafting / combine screen | Slots, cost rules, crafting UI | 5 | 2.3 | 0.5 |
| UI style pass | UI rules doc, palette, audit tool, restyle of every screen | 8 | 4.1 | 0.5 |
| Localization | Audit rule, static UI → localized components, smart strings/plurals, full 2-language table | 6 | 4.0 | 0.7 |
| Content system + full content | Selectors/filters, 4 reactive triggers, all content for 5 chapters | 10 | 9.9 | 1.0 |
| Gated content packs | 5 unlockable packs + campaign progression | 7 | 2.6 | 0.4 |
| Chapter select screen | Chapter cells, showcase art, cleared state (one layout rejected and rebuilt) | 5 | 2.1 | 0.4 |
| Unattributed | Planning sessions, fixes, tooling, cloud saves, post-processing, misc | — | 15.3 | ~20% of total |

Per-feature hours sum per-session time (76.7 h). `calibrate.py` merges sessions and subagents into windows, which also counts short gaps between sessions, so it reports ~87 h for the same span.

Use this table as **feature budgets** (SKILL.md step 3). Pick the closest row and scale by content count and novelty before splitting into tasks. When backtesting a feature from the reference project, cover its row so the answer isn't copied.

Patterns worth reusing:
- **Phase median ~0.6 h; range 0.4–1.3 h.** Early features that set up new systems (items, run map, main menu) ran at ~1.2 h/phase. Later ones reusing existing seams (quests, content packs, chapter select) ran at ~0.4.
- Content-heavy work (data for 5 chapters) costs about the same per phase as system work. The AI authors assets and data quickly.
- Everything above was built on a codebase that already had conventions, audits and an editor automation bridge. **In a from-scratch project, multiply the first two feature sections after the prototype by 1.5×.**
- A detailed doc is not a big feature. A 690-line design doc for the items system shipped in ~9 AI h, because the detail mostly pins down decisions and doesn't add work.

## Prototype phase (commits only, no hour data)

Before planned feature work, the reference project spent 15 commit days on a prototype: project and asset imports, core entity logic and animation, a turn state machine, drag and drop, VFX/SFX, projectiles, a main menu scene, and a store SDK. There's no hour data, but it shows the shape of a from-scratch start: roughly 2–3 calendar weeks at ~2–3 h/day before planned features begin.

For a new project's **Prototype / core loop** section, budget 15–30 AI h: conventions, input, camera, the core verb, a minimal loop, debug tools and feel iterations. Setup, imports, menus and store work are separate sections, with Developer rows from the table below.

## Developer-only defaults (not measured — adjust to the docs' scope)

| Task | Min–max h |
|---|---|
| Engine project setup (version, packages, render pipeline, input, LFS, folders) | 2–4 |
| Import + configure one asset pack (art / UI / VFX / audio / fonts) | 1–3 per pack |
| Animation setup per character or animated object | 2–6 each |
| Visual layout pass per screen (after AI built structure) | 1–3 per screen |
| VFX / shader / juice tuning per feature | 1–4 per feature |
| Playtest + balance pass per feature | 1–3 per feature |
| Full-game balance pass before release | 8–20 |
| Store page + store assets (capsules, screenshots, trailer cut) | 6–16 |
| Build pipeline, depots, first upload, platform checklist | 3–6 |

## Outside the calibrated areas (judgment, not measured)

The reference project is a single-player, PC, logic- and UI-heavy, data-driven game, so its features measure what the AI does well. The areas below have no reference data. There, the AI writes the code quickly, but the result has to be judged by feel, on a device, or across several clients, so more of the cost lands on the Developer.

For each such section:
1. Scale the AI budget from the closest reference anchor by the multiplier.
2. Add the Developer rows listed.
3. Allow ranges up to 3×.
4. Tag the section `"uncalibrated": "<area>"` so the Schedule sheet flags it.

| Area | AI budget × | Extra Developer rows | Why |
|---|---|---|---|
| 3D character controller, camera, melee/shooting feel | 1.2 | Feel tuning 4–12 h per controller or weapon class | Correct code still feels wrong; tuning is play-and-tweak |
| Physics gameplay (vehicles, ragdolls, destruction) | 1.5 | Tuning 4–10 h per system | Unstable results; the AI can't see jitter or tunnelling |
| Multiplayer / networking (NGO, Mirror, Fish-Net, Photon) | 2.0, plus 1.3× on every feature touching networked state | Multi-client test pass 1–3 h per feature; lag/host-migration pass 6–16 h | Desync and authority bugs only show with real clients |
| Mobile (iOS/Android) | 1.2 | Store consoles, IAP/ads dashboards 4–10 h per store; device test 1–2 h per feature; submission and review cycles 4–8 h per store; device performance pass 6–16 h | Device-only bugs, dashboards behind accounts, review rejections |
| Performance / memory optimization | 1.5 | Profiling on target hardware 4–16 h per platform | Needs the Profiler on real hardware; fixes are verified by measurement |
| VR / XR | 1.5 | Headset test 1–3 h per feature; interaction and comfort tuning 4–12 h | Only testable in the headset |
| Console ports | — | Estimate as Developer: 40–120 h per platform (SDK, certification/TRC, dev-kit builds) | NDA SDKs the AI barely knows; certification is manual |
| Level design, environment building, lighting bakes | 1.0 for tools/procedural | Blockout 4–16 h + dressing 4–20 h per level; lighting bake pass 2–6 h per scene | Built and judged by eye |
| Shader Graph / VFX Graph | 1.5 (only HLSL is AI work) | Graph authoring and look tuning 2–8 h per effect | Graph assets are GUI-edited; the AI edits them poorly |
| Animation-driven gameplay (root motion, IK, blend trees, Timeline) | 1.2 | Setup 4–12 h per character; cutscene 4–10 h per minute | Clip timing and blending are tuned in the editor |
| Live services (UGS Cloud Save/Code, Remote Config, analytics) | 1.2 | Dashboard/environment config 1–3 h per service | Setup lives behind the web dashboard |
| 3D asset pipeline (bought 3D packs, LODs, materials) | — | Import + material/LOD fix 2–6 h per pack | Materials and scale get fixed by eye |

When a project in one of these areas finishes, run `calibrate.py` on it and replace the judgment numbers with measured ones.

## Recalibrating

When the developer changes tier or model, or finishes another project, re-measure:

```bash
python "<skill base dir>/scripts/calibrate.py" "<project dir>"
```

The script prints window capacity and AI hours per weekday from that project's transcripts. Update this file's capacity table with the new numbers and date them.
