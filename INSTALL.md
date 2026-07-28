# INSTALL.md — AI Setup Wizard v4 (Claude Code & Codex)

> **Human?** Tell your coding agent: "Install this automation: <this repo URL>".
> **Agent?** You are the installer. Follow this playbook exactly.
> 中文/日本語ユーザー向け：向导将以用户在 Q1 选择的语言交流。

## Rules for the agent

- R1. Conduct the interview in the user's chosen language (Q1 onward).
- R2. NEVER ask for passwords / API keys in chat. Users enter secrets
  themselves via `gh secret set NAME` (interactive) or the GitHub web UI.
- R3. Confirm derived keywords with the user before writing config.
- R4. Ask ONE question at a time. Skip a question when the answer is already
  known from context. Offer the marked defaults so users can just say "default".
- R5. On any tool failure, use the fallback column in "Auto-fallbacks" below —
  do not dead-end the user.

## Step 0 — Backend & pre-checks

Backend table:

| | A: Claude cloud Routine | B: GitHub Actions cron | C: Spark-native |
|---|---|---|---|
| Runs on | Anthropic cloud | GitHub cloud | Google cloud (Spark VM) |
| Needs | Claude Pro/Max | LLM API key (`LLM_API_KEY`) | Google AI Ultra |
| Summarizer | Routine session | `summarize.py` API call | the Spark task itself |
| Storage / dedup | your repo, exact by arXiv ID | your repo, exact by arXiv ID | Google Sheets ledger, model-driven |
| Machine off OK | yes | yes | yes |

Backend C is for assistants that cannot run a shell, git or Python — it drops
the scripts, GitHub and SMTP entirely and is documented separately in
[`INSTALL-SPARK.md`](INSTALL-SPARK.md). This file covers A and B only; the rest
of it assumes you can execute commands.

Optional YouTube search additionally needs `YOUTUBE_API_KEY` in the secure
execution environment. Backend B supports this directly through a GitHub
Actions secret. For Backend A, enable YouTube only if the Routine environment
can expose that secret without committing it; otherwise choose Backend B or
leave YouTube disabled.

- Installer is **Codex** → Backend **B** (Codex App Automations run on the
  user's machine; no hosted scheduler). Installer is **Claude Code** → ask
  A or B (default A). Installer has **no shell** (e.g. Gemini Spark) → stop
  here and follow [`INSTALL-SPARK.md`](INSTALL-SPARK.md) instead.

**Pre-checks (ask/verify explicitly before the interview):**
- P1. `git`, `python3` present; `gh` present AND `gh auth status` shows the
  intended GitHub account (wrong account is a common failure).
- P2. "Does your sending-email account have two-step verification enabled?"
  (needed to create an app password / authorization code). If not, guide
  enabling it first.
- P3. Backend A only: "Have you installed the Claude GitHub App before?"
  (github.com/settings/installations should list "Claude"). OAuth
  authorization alone is NOT installation — this is the #1 stuck point.

## Step 1 — Interview (12 questions, one at a time)

1. **Language** of the digest (简体中文 / English / 日本語 / ...). Switch now.
2. **Research field**: keyword phrases OR a public profile URL (Google
   Scholar / KAKEN / ORCID). If URL: fetch, derive 3-6 arXiv categories,
   10-20 `abs:"..."` server terms, 20-40 scoring keywords; show & confirm
   (R3). Compose a one-line `field_hint`.
3. **Volume preference**: "Is your field narrow or broad? Roughly how many
   papers per day do you want?" → set `top_n` (default 12) and
   `window_hours` (narrow field → 72-96; broad → 48). Explain the tradeoff
   in one sentence.
4. **Push time** + UTC offset (e.g. 07:00, UTC+9) → `timezone_utc_offset`;
   Backend B: convert to `{{CRON_UTC}}` yourself and tell the user GitHub
   cron may lag minutes at busy times.
5. **Sending email provider**: Gmail / Outlook / QQ邮箱 / 163 / other →
   pick SMTP from the table below; "other" → ask for host+port or look up
   the provider's official SMTP docs. Also ask: same account for sending
   and receiving? 
6. **Recipient email** (MAIL_TO; default = sending address).
7. **Industry news** yes/no (default yes); if yes, generate 4-8 Google News
   queries (mix English + user-language, correct hl/gl/ceid) and confirm;
   also ask desired news volume (default top 10 / 7-day window).
8. **YouTube research videos** yes/no (default no). This searches public
   videos; it does not upload videos or access the user's subscriptions. If
   yes, generate and confirm 2-4 search queries from Q2, then ask volume
   (default top 6 / 7-day window), relevance language, and region. Explain
   that the user needs a Google Cloud project with YouTube Data API v3 enabled
   and an API key restricted to that API. Backend A must pass the secure-env
   requirement above before enabling this option.
9. **Repo name / owner / visibility**: default `arxiv-digest`, personal
   account, **private**. Check name collision (`gh repo view`) and re-ask
   if taken. Warn before creating public: digests reveal research interests.
10. **Email subject prefix**: propose one in the user's language
   (e.g. 每日论文简报 / Daily paper digest / 論文デイリー), confirm.
11. Backend A: **Routine model** — recommend the lightweight model to save
    quota; user may pick a stronger one. Backend B: **LLM provider**
    (openai|anthropic) — then VERIFY a current low-cost model id from the
    provider's official docs before writing config; never guess model names.
12. **Deep-link target** for the cards: `https://claude.ai/new?q=` or
    `https://chatgpt.com/?q=` (default = the assistant family the user
    already uses). Note: verify the prefill works during Step 5; if the
    provider changed URL params, adjust `assistant_url_prefix` in config.

### SMTP provider table

| Provider | host | port | Credential to put in MAIL_PASSWORD |
|---|---|---|---|
| Gmail | smtp.gmail.com | 465 | App password (Google Account → Security → App passwords) |
| Outlook/Hotmail | smtp-mail.outlook.com | 587 | App password (Microsoft Account → Security) |
| QQ邮箱 | smtp.qq.com | 465 | 授权码 (设置 → 账户 → POP3/SMTP → 生成授权码) |
| 163邮箱 | smtp.163.com | 465 | 授权码 (设置 → POP3/SMTP/IMAP → 客户端授权密码) |
| Other | ask user / official docs | — | provider-specific app password |

Note for port 587 providers (e.g. Outlook): STARTTLS — set `secure: false`
in the generated workflow's send-mail step (dawidd6 action handles STARTTLS
automatically when secure is false and port is 587).

## Step 2 — Build the user's repo

1. `git clone <this repo> <REPO_NAME> && cd <REPO_NAME> && rm -rf .git && git init -b main`
2. Write `config.json` (structure = config.example.json) from the interview:
   language, timezone_utc_offset, field_hint, assistant_url_prefix, llm
   (Backend B), arxiv (categories/terms/keywords/top_n/window_hours), news,
   youtube (enabled/queries/top_n/window_hours/language/region), and email
   (subject_prefix/smtp_host/smtp_port).
3. Backend A → generate `.github/workflows/send-digest.yml` from
   `templates/send-digest.template.yml` ({{SMTP_HOST}} {{SMTP_PORT}}
   {{SUBJECT_PREFIX}} {{SMTP_SECURE}}: true for port 465, false for 587/STARTTLS); generate
   `ROUTINE_INSTRUCTIONS.md` from `templates/routine_instructions.template.md`
   ({{LANGUAGE}} {{TZ_SIGN}}{{TZ_HOURS}} {{FIELD_HINT}}
   {{ASSISTANT_URL_PREFIX}}; news → splice `templates/news_blocks.md`,
   else delete placeholders; YouTube → splice `templates/youtube_blocks.md`,
   else delete its placeholders).
4. Backend B → generate `.github/workflows/daily-digest.yml` from
   `templates/daily-digest-cron.template.yml` ({{CRON_UTC}} {{NEWS_RUN}}
   {{SMTP_HOST}} {{SMTP_PORT}} {{SUBJECT_PREFIX}} {{SMTP_SECURE}}).
   Do NOT create send-digest.yml / ROUTINE_INSTRUCTIONS.md.
5. Delete installer-only files: INSTALL.md INSTALL-SPARK.md AGENTS.md CLAUDE.md
   templates/ config.example.json; Backend A also deletes summarize.py.
   Verify that `config.example.json` is absent and that `config.json` contains
   only the field, categories, terms, and keywords confirmed in Q2—no demo
   topic or `Demo topic only` marker may remain.
6. Create & push per Q9:
   `gh repo create <OWNER>/<REPO_NAME> --private|--public --source=. --push`

## Step 3 — Secrets (user-executed; R2 applies)

Guide credential creation per the SMTP table (provider-specific path).
User runs:
```
gh secret set MAIL_USERNAME   # sending address
gh secret set MAIL_TO         # recipient (Q6)
gh secret set MAIL_PASSWORD   # app password / 授权码 (interactive)
```
Backend B additionally: `gh secret set LLM_API_KEY`
If YouTube is enabled on Backend B: `gh secret set YOUTUBE_API_KEY`
(no gh → repo Settings → Secrets and variables → Actions; names exact.)
If YouTube is enabled on Backend A, the user must set `YOUTUBE_API_KEY`
through a protected environment-secret mechanism outside the repository.
If that mechanism is unavailable, disable YouTube or use Backend B.

Create the YouTube key without sharing it in chat:
1. Google Cloud Console → create/select a project.
2. APIs & Services → Library → enable **YouTube Data API v3**.
3. Credentials → Create credentials → API key.
4. Restrict the key to **YouTube Data API v3**, then enter it through
   `gh secret set YOUTUBE_API_KEY` or the GitHub Secrets web UI.

Official setup guide:
https://developers.google.com/youtube/v3/getting-started

## Step 4 — Cloud side

Backend A (user-executed, give exact clicks):
1. github.com/apps/claude → Install (or Configure) → grant the new repo
   (verify it now appears under **Installed** GitHub Apps, not only
   Authorized — see P3).
2. claude.ai/code env → Network access: ask the user "Full (simple) or
   Custom (tighter)?"; Custom → allow export.arxiv.org
   (+ news.google.com if news enabled; + www.googleapis.com if YouTube
   enabled).
3. claude.ai/code/routines → New routine: the repo, Daily at the user's
   local time, model per Q11, paste ROUTINE_INSTRUCTIONS.md.

Backend B: nothing else — the cron workflow is live after push.

## Step 5 — Verify (walk the user through; ask, don't wait)

Backend A: Routine "Run now" → digests/ + digests_html/ pushed → green
push-triggered "Send daily digest" Action → ask: "Did the email arrive?
(check spam/promotions too)".
Backend B: repo → Actions → "Daily digest (cron)" → Run workflow → all
steps green → same email check.
Then verify with the user: HTML attachment opens; deep links open the chosen
assistant WITH a readable prefilled prompt (raw %XX → see troubleshooting);
"Terms" folds work; arXiv links work; if enabled, the Research videos section
appears and every Watch link opens the intended YouTube video.

## Auto-fallbacks (R5)

| Failure | Fallback |
|---|---|
| `gh` missing | Web UI path: github.com/new → git remote add → push; secrets via repo Settings |
| `gh` logged into wrong account | `gh auth login` again; re-run pre-check P1 |
| Profile URL fetch fails / blocked | Ask for keyword phrases instead (Q2 fallback) |
| Repo name taken | Re-ask Q9 with a suggested alternative |
| Provider SMTP unknown | Ask user for host/port from their provider's help page |
| YouTube key unavailable on Backend A | Switch to Backend B or disable YouTube; never commit the key |
| YouTube API setup is blocked | Disable YouTube and finish the paper/news installation |

## Troubleshooting

| Symptom | Cause → Fix |
|---|---|
| `Input required and not supplied: from` | Mail secrets missing/typo → Step 3, exact names, Re-run |
| `Invalid login` / auth failed | App password wrong/with spaces, 2FA off, or 587 provider without secure:false → regenerate / fix workflow |
| B: "Missing env LLM_API_KEY" | Secret not set → Step 3 |
| `Missing env YOUTUBE_API_KEY` | YouTube enabled but secret unavailable → set exact secret name or disable `youtube.enabled` |
| YouTube HTTP 403 / quota error | Check API enabled, API restriction, and quota in Google Cloud Console; reduce query count |
| B: "LLM output missing markers" | Retry; if persistent switch to a stronger model in config.json |
| B: cron late / didn't fire | GitHub cron lags & queues; disabled after ~60 days repo inactivity (daily commits keep it alive) |
| A: routine pushed but no Action run | send-digest.yml wasn't on main before the routine branch existed → put on main, rerun |
| A: repo not selectable in routine | App not *installed* or repo not granted (P3) → github.com/apps/claude Configure; paste repo URL directly |
| Digest dated yesterday / file overwritten | timezone_utc_offset wrong in config.json |
| Second same-day run nearly empty | Cross-day dedup counts today's digest — expected |
| Deep links show raw %XX text | Model failed URL-encoding → rerun; tighten wording |
| A: script network errors | Routine env network access → allow export.arxiv.org / news.google.com / www.googleapis.com as enabled |
