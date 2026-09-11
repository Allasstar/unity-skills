---
name: unity-narrow-reads
description: Read only the lines you need instead of dumping whole files into context. Use before opening any C# source, Unity scene/prefab/asset YAML, spec or plan doc, CSV, log, or generated file when the goal is to locate, inspect, or verify something rather than rewrite the file wholesale. Triggers on "where is X", "what does Y do", "which prefab/scene references Z", "list the fields/methods of", "check whether the codebase does", and on any read of a file over ~400 lines.
---

# Narrow reads

Context is the budget. A whole-file read costs the same whether you use 6 lines of it or 600.

## The loop

1. **Locate** — find line numbers first, never read to find.
2. **Window** — read only around those numbers.
3. **Widen** — only if the window actually came up short.

```bash
grep -n "PATTERN" path/to/File.cs          # step 1: line numbers
sed -n '120,180p' path/to/File.cs          # step 2: the window
```

Prefer the harness's own grep tool for step 1 where there is one — it integrates with the
permission UI and file links. `sed -n`/`awk` via bash for step 2.

## Budgets

| Situation | Cap |
|---|---|
| Window per hop | ~80 lines |
| Total lines pulled before you answer | ~250 |
| Whole-file read | only under 400 lines, or you are about to rewrite it |

Exceeding a budget is allowed — but say why, don't drift into it.

**The ~250 cap is per answer, not per investigation.** A deliberate research sweep — writing
a spec, scoping a plan, auditing a system — is allowed to go wide. Keep it cheap by making
the sweep return **paths and line numbers**, not content, then window into the two or three
places that turn out to matter. Announce that you are doing a sweep so it reads as a choice
rather than a leak.

## Recipes

Substitute the project's own source root for `<SRC>` below — `Assets/`, `Assets/_Project/`,
`src/`, whatever it uses.

**Locate a symbol across the repo** — paths only, no content:
```bash
grep -rln "SymbolName" <SRC> --include=*.cs
```

**Structural outline of a C# file** (cheap substitute for reading it):
```bash
grep -nE "^\s*(public|private|protected|internal).*(class|struct|enum|interface|\()" File.cs
```

**Serialized surface of a MonoBehaviour/ScriptableObject:**
```bash
grep -n -A1 "SerializeField" File.cs
```

**One method body** — get its start line, then window forward:
```bash
grep -n "void MethodName" File.cs
sed -n '340,395p' File.cs
```

**Call sites with just enough context:**
```bash
grep -rn -B1 -A3 "MethodName(" <SRC> --include=*.cs
```

## Unity YAML — never `cat` a .unity / .prefab / .asset

A busy scene or prefab runs to hundreds of KB, sometimes megabytes. Dumping one is the
single most expensive mistake available.

**Who references this asset** — resolve the guid from the `.meta`, then grep for it:
```bash
grep guid "<SRC>/.../Thing.asset.meta"
grep -rln "GUID_HERE" <SRC> --include=*.prefab --include=*.unity
```

**Does a scene contain object X:**
```bash
grep -n -A2 "m_Name: ObjectName" <SRC>/Scenes/MainMenu.unity
```

**Component/field values** — go through the live editor instead of the file, if the project
exposes a bridge (a Unity MCP server, a pipeline HTTP endpoint, `unity-cli`). Ask it to
evaluate and return a one-line string; that costs tens of tokens where the YAML costs tens
of thousands. With no bridge, grep the component block by `m_Script` guid and window it —
still never the whole file.

**Before deleting anything in a scene:** find the object's `fileID` in its entry, then grep
the scene for that id to turn up every component and reference pointing at it. Delete only
once you have seen the full set. That is a targeted grep, not a read.

## Other file types

- **Specs (`specs/*.md`)** — read one whole; they are written to be read whole and sit under
  the 400-line cap. The index (`specs/README.md`) too: it is a map and it is cheap.
- **Plan docs (`plans/*.md`)** — never whole. `grep -n "^## \|^\*\*Now:\|^- \[ \]"` for the
  outline, then window into the one phase you need. A finished plan is mostly history.
- **CSV** — `head -1` for the header, `awk -F, '$2=="X"'` for rows. Never cat.
- **Test files** — `grep -n "\[Test\]" -A1` gives the case list; read only the failing one.
- **Logs** — grep for the error pattern with `-B2 -A5`. Never tail a whole build log.
- **Generated / `Library/` / `obj/`** — do not read at all; regenerate or query the editor.

## Anti-patterns

- Reading a file "to get oriented" before knowing what you're looking for. Grep orients you.
- Re-reading a file you read or edited **yourself, this session** — trust your own last edit.
  Do re-read when anything else touched it since: another session, another tool, a skill
  that rewrites files, a git operation, a running Editor that reserializes on save.
- Reading a file to confirm an edit landed, where the harness's edit tool errors on a failed
  match. If it doesn't give you that guarantee, verify with a one-line grep, not a read.
- `head -200` as a habit — the answer is rarely in the first 200 lines.
- Widening the window "just in case."

## When to skip this skill

Read the whole file when you are rewriting it, when it is under ~400 lines and you need most
of it, or when structure matters more than any single symbol (a small config, an interface,
a spec, a new-to-you file you're about to restructure).
