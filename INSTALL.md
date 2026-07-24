# INSTALL.md — AI Setup Wizard (Claude Code & Codex)

> **Human?** Tell your coding agent: "Install this automation: <this repo URL>".
> **Agent?** You are the installer. Follow this playbook exactly.
> 中文/日本語ユーザー向け：向导将以用户在问题1选择的语言交流。

## Rules for the agent

- R1. Conduct the interview in the user's chosen language (Question 1).
- R2. NEVER ask for passwords/API keys in chat. Users enter secrets themselves
  via `gh secret set NAME` (interactive) or the GitHub web UI.
- R3. Confirm derived keywords with the user before writing config.
- R4. State prerequisites first; stop if unmet: GitHub account + git;
  a Gmail account for sending. Backend A additionally needs Claude Pro/Max with
  Claude Code on the web. Backend B additionally needs an LLM API key
  (OpenAI or Anthropic) and bills a few cents/day.

## Step 0 — Pick the execution backend

| | Backend A: Claude cloud Routine | Backend B: GitHub Actions cron |
|---|---|---|
| Runs | Anthropic cloud | GitHub cloud |
| Needs | Claude Pro/Max | LLM API key (secret `LLM_API_KEY`) |
| Summarizer | the Routine's Claude session | `summarize.py` API call |
| Machine off OK | yes | yes |

- Installer is **Codex** → use **Backend B** (Codex has no hosted cloud
  scheduler equivalent to Claude Routines; its App Automations run on the
  user's machine).
- Installer is **Claude Code** → ask the user A or B (A default).

## Step 1 — Interview (both backends)

Ask one at a time:
1. **Language** of the digest (简体中文 / English / 日本語 / ...). Switch now.
2. **Research field**: keyword phrases OR a public profile URL (Google
   Scholar / KAKEN / ORCID). If URL: fetch it, derive 3-6 arXiv categories,
   10-20 `abs:"..."` server terms, 20-40 scoring keywords; confirm (R3).
   Also compose a one-line `field_hint`.
3. **Push time** + UTC offset (e.g. 07:00, UTC+9).
4. **Recipient email** (MAIL_TO).
5. **Industry news** yes/no; if yes, generate 4-8 Google News queries
   (mix English + user-language, correct hl/gl/ceid) and confirm.
6. (Backend B only) **LLM provider** openai|anthropic + verify a current
   cheap model id from the provider's official docs before writing config.
7. Ask which assistant the deep-link cards should open:
   `https://claude.ai/new?q=` or `https://chatgpt.com/?q=` → assistant_url_prefix.

## Step 2 — Build the user's repo (both backends)

1. `git clone <this repo> arxiv-digest && cd arxiv-digest && rm -rf .git && git init -b main`
2. Write `config.json` (structure = config.example.json) from the interview.
3. Backend A → generate `.github/workflows/send-digest.yml` from
   `templates/send-digest.template.yml` ({{SMTP_HOST}} {{SMTP_PORT}} {{SUBJECT_PREFIX}});
   generate `ROUTINE_INSTRUCTIONS.md` from `templates/routine_instructions.template.md`
   ({{LANGUAGE}} {{TZ_SIGN}}{{TZ_HOURS}} {{FIELD_HINT}} {{ASSISTANT_URL_PREFIX}};
   news → splice blocks from `templates/news_blocks.md`, else delete placeholders).
4. Backend B → generate `.github/workflows/daily-digest.yml` from
   `templates/daily-digest-cron.template.yml`:
   - {{CRON_UTC}}: convert the user's local time to UTC yourself
     (e.g. 07:00 UTC+9 → `0 22 * * *`). Tell the user GitHub cron can lag
     minutes to ~an hour at busy times.
   - {{NEWS_RUN}}: `python3 fetch_news.py` if news enabled else `"true"`.
   - {{SMTP_HOST}} {{SMTP_PORT}} {{SUBJECT_PREFIX}} from config.
   Do NOT create send-digest.yml or ROUTINE_INSTRUCTIONS.md for Backend B.
5. Delete installer-only files: INSTALL.md AGENTS.md CLAUDE.md templates/
   config.example.json. Backend A also deletes summarize.py.
6. `gh repo create arxiv-digest --private --source=. --push`
   (no gh → guide web UI + git remote + push).

## Step 3 — Secrets (user-executed; R2 applies)

Guide Gmail app password creation (2-Step Verification → App passwords).
User runs:
```
gh secret set MAIL_USERNAME
gh secret set MAIL_TO
gh secret set MAIL_PASSWORD
```
Backend B additionally: `gh secret set LLM_API_KEY`
(no gh → repo Settings → Secrets and variables → Actions).

## Step 4 — Cloud side

Backend A (user-executed, give exact clicks):
1. github.com/apps/claude → Install → grant the new repo.
2. claude.ai/code env → Network access: Full or Custom incl. export.arxiv.org
   (+ news.google.com if news).
3. claude.ai/code/routines → New routine: repo, Daily at the user's local
   time, paste ROUTINE_INSTRUCTIONS.md.

Backend B: nothing else — the cron workflow is already live after push.

## Step 5 — Verify

Backend A: Routine "Run now" → digests/ + digests_html/ pushed → push-triggered
green "Send daily digest" Action → email with .html attachment.
Backend B: repo → Actions → "Daily digest (cron)" → Run workflow → all steps
green → email arrives. Check: deep links open the chosen assistant with a
prefilled prompt; "Terms" folds work; arXiv links work.

## Troubleshooting

| Symptom | Cause → Fix |
|---|---|
| `Input required and not supplied: from` | Mail secrets missing/typo → Step 3, exact names, Re-run |
| `Invalid login` | App password wrong/spaces or 2FA off → regenerate |
| B: summarize step fails "Missing env LLM_API_KEY" | Secret not set → Step 3 |
| B: "LLM output missing markers" | Retry run; if persistent, switch to a stronger model in config.json |
| B: cron didn't fire on time | GitHub cron lags/queues; also disabled after ~60 days without repo activity (daily commits keep it alive) |
| A: routine pushed but no Action | send-digest.yml wasn't on main before the routine branch existed → put it on main, rerun |
| Digest dated yesterday / overwritten | timezone_utc_offset wrong in config.json |
| Second same-day run nearly empty | cross-day dedup counts today's digest — expected |
| Deep links show raw %XX in the box | model failed URL-encoding → rerun; tighten wording |
| Script network errors (Backend A) | routine env network access → allow export.arxiv.org / news.google.com |
