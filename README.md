# Unity Skills

A collection of reusable skills for Unity workflows. Compatible with Claude Code.

## Install

### Claude Code

Install all skills globally (available in every project):

```bash
npx skills add Allasstar/unity-skills -g -a claude-code -y
```

Install into a single project instead (commit `.claude/skills/` to share with your team):

```bash
npx skills add Allasstar/unity-skills -a claude-code -y
```

Pick individual skills:
see what's in the repo
```bash
npx skills add Allasstar/unity-skills --list
```
install only what you need
```bash
npx skills add Allasstar/unity-skills -g -a claude-code \
  --skill unity-cli --skill ui --skill ui-uitk
```

| Scope | Flag | Path |
|---|---|---|
| Global | `-g` | `~/.claude/skills/` |
| Project | (default) | `.claude/skills/` |

By default the CLI installs a canonical copy under `.agents/skills/` and symlinks it into `.claude/skills/`. Pass `--copy` if symlinks are a problem on your setup (Windows without developer mode, some CI images).

### Updating
update every installed skill
```bash
npx skills update -g
```
update specific skills
```bash
npx skills update unity-cli ui-uitk
```

### Verifying

```bash
npx skills ls -g -a claude-code
```

In a Claude Code session, run `/skills` or ask "what skills are available?". Newly added skills are picked up without a restart, unless `~/.claude/skills/` did not exist when the session started. If a skill never appears, run `claude plugin validate ~/.claude/skills` to catch frontmatter errors.

### Removing

```bash
npx skills remove unity-cli -g
```
```bash
npx skills remove --all -g -a claude-code
```

### Manual install

```bash
git clone https://github.com/Allasstar/unity-skills
ln -s "$PWD/unity-skills/skills/unity-cli" ~/.claude/skills/unity-cli
```

Claude Code reads `SKILL.md` through symlinks, so `git pull` keeps the skill current.

### Other agents

```bash
npx skills add Allasstar/unity-skills
```

The CLI auto-detects installed agents and prompts for targets. See [skills.sh](https://skills.sh) for the full list.

## Available skills

| Skill | Description |
|---|---|
