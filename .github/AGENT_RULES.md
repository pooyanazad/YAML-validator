# Agent & Contributor Rules

## ⛔ Files That Must NEVER Be Committed or Pushed

| File | Reason |
|------|--------|
| `improvement_suggestions.md` | Local planning doc only. Already in `.gitignore`. Never stage or force-add it. |

### For AI Agents (Antigravity / Copilot / etc.)

- **Do NOT** run `git add improvement_suggestions.md`
- **Do NOT** run `git add -f improvement_suggestions.md` or `git add --force ...`
- **Do NOT** amend any commit to include this file
- When marking tasks done, update the file locally — but **stop there**. It is intentionally git-ignored.
- If you need to reference task status, read the file locally. Never push it.

## ✅ Normal Workflow

1. Make code changes
2. `git add <specific files>` — never use `git add .` blindly
3. Commit with a descriptive message
4. Push to `origin main`
