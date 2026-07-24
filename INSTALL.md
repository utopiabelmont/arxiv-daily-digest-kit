# INSTALL.md — AI Setup Wizard

> **If you are a human**: just tell Claude Code
> "Install this automation: <this repo URL>" and answer its questions.
> **If you are Claude (or another AI agent)**: you are the installer.
> Follow this playbook exactly. 中文用户提示：向导会以用户选择的语言交流。

## Rules for the agent

- R1. Conduct the whole interview in the user's chosen language (Question 1).
- R2. NEVER ask the user to paste passwords into the chat. Email app passwords
  are entered by the user directly into `gh secret set` (interactive) or the
  GitHub web UI. You may handle non-secret values (email address, keywords).
- R3. Confirm the generated keyword set with the user before writing config.
- R4. This kit requires the user's own Claude Pro/Max plan with Claude Code on
  the web, a GitHub account, and a Gmail account for sending. State this first
  and stop if not met.

## Step 0 — Environment check

Check locally: `git --version`, `python3 --version`, `gh --version`.
`gh` missing -> fall back to manual web-UI instructions where noted.
`gh` present but not logged in -> have the user run `gh auth login`.

## Step 1 — Interview (5 questions)

Ask, one at a time:
1. **Language** for the daily digest emails (e.g. 简体中文 / English / 日本語).
   Switch the conversation to that language now.
2. **Research field**: EITHER a few keyword phrases, OR a public profile URL
   (Google Scholar / KAKEN / ORCID / lab page). If a URL is given, fetch it,
   read titles + interests, and derive:
   - 3-6 arXiv categories (from the official arXiv taxonomy),
   - 10-20 `abs:"..."` server terms (specific phrases),
   - 20-40 scoring keywords (lowercase).
   Show the derived set and iterate until the user approves (R3).
3. **Push time**: local time of day + their UTC offset (e.g. 07:00, UTC+9).
4. **Email address** to receive the digest (MAIL_TO).
5. **Industry news**: yes/no. If yes, generate 4-8 Google News queries from
   the keywords (mix English + the user's language variants with proper
   hl/gl/ceid), show and confirm.

## Step 2 — Create the user's repo

1. `git clone <this template repo> arxiv-digest && cd arxiv-digest`
2. Remove the template git history: `rm -rf .git && git init -b main`
3. Write `config.json` from the interview (copy structure from
   config.example.json; set language, timezone_utc_offset, arxiv.*, news.*,
   email.subject_prefix in the user's language, smtp defaults gmail).
4. Generate `.github/workflows/send-digest.yml` from
   `templates/send-digest.template.yml`, replacing {{SMTP_HOST}} {{SMTP_PORT}}
   {{SUBJECT_PREFIX}}.
5. Generate `ROUTINE_INSTRUCTIONS.md` from
   `templates/routine_instructions.template.md`: fill {{LANGUAGE}},
   {{TZ_SIGN}}{{TZ_HOURS}}, {{FIELD_HINT}} (one-line field summary);
   if news enabled, splice the three blocks from templates/news_blocks.md
   into {{NEWS_STEP}} {{NEWS_SECTION}} {{NEWS_CARD}} and renumber the first
   step to "1/2"; else delete those placeholders.
6. Keep: fetch_arxiv.py fetch_news.py build_html.py card_template.html
   .gitignore README.md. Delete: INSTALL.md templates/ config.example.json.
7. Create the private repo and push:
   `gh repo create arxiv-digest --private --source=. --push`
   (no gh -> guide the user through github.com new-repo + git remote + push).

## Step 3 — Email secrets (user-executed)

1. Guide the user: Google Account -> Security -> 2-Step Verification on ->
   App passwords -> generate 16-char password. They keep it; you never see it.
2. Have the USER run (they type/paste values themselves):
   ```
   gh secret set MAIL_USERNAME   # their gmail address
   gh secret set MAIL_TO         # recipient address from Q4
   gh secret set MAIL_PASSWORD   # the app password (interactive prompt)
   ```
   No gh -> repo Settings -> Secrets and variables -> Actions -> New secret ×3.
   Names must match exactly.

## Step 4 — Claude cloud side (user-executed, give exact clicks)

1. github.com/apps/claude -> Install -> grant access to the new repo
   (this is the App *installation*, distinct from OAuth authorization).
2. claude.ai/code -> environment settings -> Network access: Full, or Custom
   allowing at least `export.arxiv.org` (+ `news.google.com` if news enabled).
3. claude.ai/code/routines -> New routine:
   - repository: the new repo; schedule: Daily at the time from Q3
     (times are entered in the user's local timezone);
   - Instructions: paste the full content of ROUTINE_INSTRUCTIONS.md.

## Step 5 — Verify (walk the user through)

1. Routine "Run now". Expect: digests/DATE.md + digests_html/DATE.html pushed.
2. GitHub Actions: a push-triggered green "Send daily digest" run.
3. Inbox: email with body + .html attachment; blocks deep-link to claude.ai;
   "Terms" folds open; arXiv links work.

## Troubleshooting (battle-tested)

| Symptom | Cause -> Fix |
|---|---|
| Action error `Input required and not supplied: from` | Secrets missing/typo'd -> Step 3, names exact, then Re-run jobs |
| Action `Invalid login` | App password wrong/with spaces, or 2FA off -> regenerate |
| Routine pushed but no Action run | Workflow yml wasn't on main before the routine branch was created -> ensure `.github/workflows/send-digest.yml` on main, rerun routine |
| Manual workflow_dispatch fails "no digests" | Normal before the first routine run pushes to main |
| Repo not selectable in routine | App installed? repo access granted? paste the repo URL directly |
| Digest dated yesterday / same file overwritten | timezone_utc_offset wrong in config.json |
| Second same-day run returns almost empty | Cross-day dedup counts today's digest as "already reported" — expected |
| Script network errors in routine log | Environment network access blocked -> Step 4.2 |
| Deep links show raw %XX text in claude.ai box | Model failed to URL-encode; rerun; if persistent, tighten instruction wording |
