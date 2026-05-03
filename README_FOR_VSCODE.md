# How to Use These Files with Codex in VS Code

## 1. Copy files into your repo

Copy this folder's contents into your project root.

Expected root:

```txt
terminal-agent-platform/
  PROJECT_PLAN.md
  CODEX_MASTER_PROMPT.md
  CODEX_PHASE_PROMPTS.md
  specs/
```

## 2. Open VS Code

```bash
code terminal-agent-platform
```

## 3. Start Codex

Open Codex in VS Code and paste the contents of `CODEX_MASTER_PROMPT.md`.

## 4. Work phase by phase

After the master prompt, use prompts from `CODEX_PHASE_PROMPTS.md` one at a time.

Do not ask Codex to build everything at once.

## 5. Git workflow

Use branches:

```bash
git checkout -b feature/system-bootstrap
git add .
git commit -m "feat: bootstrap nuxt fastapi docker system"
```

Then continue with:

```bash
git checkout -b feature/chat-foundation
```

## 6. Senior Engineer Rule

Codex is the implementer. You are the tech lead.

Your job:
- keep it scoped
- review diffs
- run tests
- reject unsafe shortcuts
- update specs
