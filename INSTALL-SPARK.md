# INSTALL-SPARK.md — AI Setup Wizard for agents without a shell (Gemini Spark)

> **Human?** Tell your assistant: "Install this automation: <this repo URL>".
> **Agent?** You are the installer. Follow this playbook exactly.
> 中文/日本語ユーザー向け：向导将以用户在 Q1 选择的语言交流。

This playbook is for assistants that can browse the web, use Google Workspace
and run on a schedule, but **cannot run a shell, git, or Python** — Gemini Spark
is the reference case. If you *can* run scripts (Claude Code, Codex, …), use
`INSTALL.md` instead.

## Rules for the agent

- R1. Conduct the interview in the user's chosen language (Q1 onward).
- R2. NEVER ask for passwords / API keys in chat. Backend C below needs none at
  all — no app password, no SMTP credential, no LLM API key. Say so; it is the
  main reason this route exists.
- R3. Confirm derived keywords with the user before writing them into the task.
- R4. Ask ONE question at a time. Skip a question when the answer is already
  known from context. Offer the marked defaults so users can just say "default".
- R5. On any tool failure, use the fallback column in "Auto-fallbacks" below —
  do not dead-end the user.
- R6. Do not present unverified behaviour as fact. The items under "Not verified
  yet" must be checked live during Step 5, and the user must be told which ones
  failed.

## Step 0 — Which backend?

Ask first: **"Do you have a GitHub account, or would you mind creating one?"**

- *No / would rather not* → **Backend C (Spark-native)**. This is the default and
  the right answer for most Ultra subscribers. Continue with this file.
- *Yes, happy to use GitHub* → **Backend B (GitHub Actions cron)**, the full
  version: scripted search, exact dedup, HTML attachment, git archive. Follow
  `INSTALL.md` Step 1 onward, with one adjustment — you have no shell, so every
  `gh` command there is unavailable. Do all of it through the GitHub web UI:
  create the repo at github.com/new, upload the kit files (Add file → Upload
  files), and set the Secrets under repo Settings → Secrets and variables →
  Actions. The user still needs a mailbox app password and an LLM API key for
  that route.

Backend table (A and B are described in full in `INSTALL.md`):

| | A: Claude cloud Routine | B: GitHub Actions cron | C: Spark-native |
|---|---|---|---|
| Runs on | Anthropic cloud | GitHub cloud | Google cloud (Spark VM) |
| Needs | Claude Pro/Max | GitHub + LLM API key + mail app password | Google AI Ultra only |
| Searching & ranking | `fetch_arxiv.py` | `fetch_arxiv.py` | the model, by hand |
| Dedup | exact, by arXiv ID | exact, by arXiv ID | Sheets ledger lookup |
| Storage | your repo | your repo | your Google Sheets / Drive |
| Delivery | SMTP via Actions | SMTP via Actions | native Gmail |
| Cards | HTML attachment | HTML attachment | inline HTML in the body |
| Machine off OK | yes | yes | yes |

### What Backend C gives up (tell the user before they choose)

Without script execution the model does the fetching, filtering, dedup and
ranking itself, so it is less reliable than A/B:

- arXiv retrieval is a model-driven search, not a deterministic API query with
  exact-phrase category filters;
- cross-day dedup depends on the model reading the ledger correctly, not on an
  exact ID comparison in code;
- relevance scoring is a judgement call, not the fixed 3-points-in-title /
  1-point-in-abstract formula;
- the HTML cards most likely arrive **inline in the email body**, not as an
  attachment (see "Not verified yet");
- **YouTube research videos are not available on Backend C** — that feature
  needs the YouTube Data API key and `fetch_youtube.py`. Users who want it
  should pick Backend B.

## Step 1 — Prerequisites

- A **Google AI Ultra** subscription with Spark enabled.
- Spark is rolling out by country/region; ask the user to confirm it is
  available for their account. Availability is **not verified** by this kit.
- Gmail, Google Sheets and Google Drive on the same Google account, and the
  willingness to let the scheduled task use them.
- No GitHub account, no app password, no API key, no payment method.

## Step 2 — Interview (7 questions, one at a time)

1. **Language** of the digest (简体中文 / English / 日本語 / ...). Switch now.
2. **Research field**: keyword phrases OR a public profile URL (Google Scholar /
   KAKEN / ORCID). If URL: fetch, derive 3-6 arXiv categories, 10-20 exact
   phrases for `abs:"..."` search terms, 20-40 scoring keywords; show & confirm
   (R3). Compose a one-line field description → `{{FIELD}}`.
3. **Volume preference**: "Is your field narrow or broad? Roughly how many
   papers per day do you want?" → `{{TOP_N}}` (default 12) and
   `{{WINDOW_HOURS}}` (narrow field → 72-96; broad → 48). Explain the tradeoff
   in one sentence.
4. **Push time** + UTC offset (e.g. 07:00, UTC+9) → `{{TZ_SIGN}}{{TZ_HOURS}}`;
   the schedule itself is set in Spark's own UI in local time.
5. **Recipient email** (`{{RECIPIENT}}`; default = the Google account running
   the task).
6. **Industry news** yes/no (default yes); if yes, generate 4-8 news queries
   (mix English + user-language) and confirm; also ask desired volume (default
   top 10 / 7-day window).
7. **Deep-link target** for the cards: default `https://gemini.google.com/`
   (`{{ASSISTANT_URL_PREFIX}}`), or `https://claude.ai/new?q=` /
   `https://chatgpt.com/?q=` if the user prefers another assistant. **The prefill
   URL parameter for Gemini is not verified** — test it in Step 5 and fall back
   to plain, unlinked card blocks if it does nothing.

Also propose an **email subject prefix** in the user's language
(`{{SUBJECT_PREFIX}}`, e.g. 每日论文简报 / Daily paper digest / 論文デイリー) and
confirm it — this is part of Q1's language choice, not a separate question.

## Step 3 — Create the Sheets ledger

The ledger replaces the git archive: it is what makes cross-day dedup possible.

1. In the user's Google Drive, create a new spreadsheet named
   **`arXiv Digest Ledger`** (`{{LEDGER_NAME}}`; any name works as long as the
   task instructions use the same one).
2. Rename the first sheet to `reported`, and put these headers in row 1:
   `arxiv_id` | `title` | `date_reported` | `link`
3. Add a second sheet named `archive` with headers: `date` | `digest_text`
   (optional; it keeps a copy of each day's digest).
4. Leave the rest empty — the scheduled task appends rows itself.

Dedup rule to keep in mind: matching is by `arxiv_id` **ignoring the version
suffix** (`2501.01234v2` = `2501.01234`), so store bare IDs.

## Step 4 — Create the scheduled Spark task

1. Fill in `templates/spark_task_instructions.template.md` from the interview.
   Placeholders: `{{LANGUAGE}}` `{{FIELD}}` `{{TOP_N}}` `{{WINDOW_HOURS}}`
   `{{RECIPIENT}}` `{{LEDGER_NAME}}` `{{ASSISTANT_URL_PREFIX}}`
   `{{SUBJECT_PREFIX}}` `{{TZ_SIGN}}{{TZ_HOURS}}` `{{CATEGORIES}}`
   `{{SERVER_TERMS}}` `{{KEYWORDS}}` `{{ARXIV_API_URL}}`.
   News enabled → splice in the `[NEWS_SECTION]` / `[NEWS_CARD]` blocks from the
   bottom of that file and fill `{{NEWS_QUERIES}}` `{{NEWS_TOP_N}}`
   `{{NEWS_WINDOW_HOURS}}`; news disabled → delete the `{{NEWS_SECTION}}` and
   `{{NEWS_CARD}}` placeholders and the optional-blocks appendix.
2. Build `{{ARXIV_API_URL}}` once, so the task does not have to assemble it
   every morning:
   `http://export.arxiv.org/api/query?search_query=<ENCODED>&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100`
   where `<ENCODED>` is the URL-encoded form of
   `(cat:A OR cat:B) AND (abs:"phrase one" OR abs:"phrase two")`.
   Open it once in a browser to confirm it returns entries; if it returns none,
   the phrases are too narrow — widen them with the user (R3).
3. In the Gemini app → **Agent** tab → create a scheduled task. Set it to run
   **daily at the user's Q4 local time**.
4. Paste the filled instructions as the task's prompt.
5. Grant the task access to Gmail, Google Sheets and Google Drive when prompted.
   Nothing else is needed — no credentials are stored anywhere.

## Step 5 — Verify (walk the user through; ask, don't wait)

Run the task once manually ("Run now" / equivalent in the Agent tab), then check
with the user:

1. an email arrived at `{{RECIPIENT}}` (check spam / promotions too);
2. it is written in `{{LANGUAGE}}` and the paper count looks like `{{TOP_N}}`;
3. arXiv links open the right papers, and the dates are inside the window;
4. the coloured card blocks render — if they arrive as raw HTML source or as an
   unstyled wall of text, the inline-style rule was not followed; tell the task
   to re-check step 6 of its instructions;
5. clicking a card block opens the chosen assistant **with the prompt already
   filled in**. If it opens an empty chat, the prefill parameter does not work:
   switch `{{ASSISTANT_URL_PREFIX}}` to another assistant or drop the links and
   keep the card text (R6);
6. open the ledger — the `reported` sheet gained one row per paper.

Then run it a second time the next day and confirm the second digest does not
repeat yesterday's papers. That single check is the real test of Backend C.

## Not verified yet

Tell the user plainly which of these are untested, and ask for feedback:

| Item | Status |
|---|---|
| Gemini prefill link (`https://gemini.google.com/` + query parameter) | **Not verified.** Test in Step 5; fall back to unlinked card blocks. |
| Whether Spark can send an HTML file as an attachment | **Not verified.** The instructions therefore ask for inline HTML first, Google Doc link second, plain text third. |
| Spark availability per country/region | **Not verified.** Ask the user to confirm on their own account. |

## Auto-fallbacks (R5)

| Failure | Fallback |
|---|---|
| User has no Google AI Ultra | Backend C is unavailable → offer Backend B via `INSTALL.md` (needs GitHub) |
| Profile URL fetch fails / blocked | Ask for keyword phrases instead (Q2 fallback) |
| arXiv API URL returns nothing | Widen categories/phrases with the user; or switch the task to the `https://arxiv.org/search/advanced` page |
| Sheets access denied to the task | Re-grant Drive/Sheets permission; until then the task must not send mail (it would duplicate) |
| Cards arrive broken / stripped | Google Doc link, then plain text — in that order |
| Deep links do not prefill | Drop the links, keep the card text |
| User wants exact dedup / attachments / YouTube | Switch to Backend B (`INSTALL.md`) |

## Troubleshooting

| Symptom | Cause → Fix |
|---|---|
| No email at all | Task did not run (check the Agent tab's run history) or Gmail permission was never granted → re-grant, Run now |
| Email arrived but has no papers | Window too short or phrases too narrow → raise `{{WINDOW_HOURS}}`, widen `{{SERVER_TERMS}}` |
| Same papers as yesterday | Ledger not read or not written → check the `reported` sheet gained rows; confirm the task compares IDs without the `v` suffix |
| Papers unrelated to my field | Scoring keywords too generic → tighten `{{KEYWORDS}}` and `{{FIELD}}` (R3) |
| Cards show as raw `<div ...>` text | Email sent as plain text → the task must send HTML |
| Cards render but colourless | `<style>` block used instead of inline styles → Gmail strips it; enforce `style="..."` attributes |
| Deep links show raw %XX text | Encoding applied twice, or the prompt was encoded after being placed in the href → encode the prompt string once, then concatenate |
| Digest dated a day off | Wrong `{{TZ_SIGN}}{{TZ_HOURS}}` in the instructions |
| Invented papers / broken links | Honesty rules were dropped from the prompt → re-paste them verbatim; report it |

## Disable & uninstall

Delete or pause the task in the Gemini app's Agent tab. To remove everything,
also delete the `arXiv Digest Ledger` spreadsheet and revoke the task's Gmail /
Sheets / Drive access. Nothing else was created — there are no secrets to
revoke.

## Advanced — let Spark do the post-processing

Optional extras, once the daily digest works. They are what Spark can do that a
GitHub cron cannot, but none of them is required and each one is a separate
scheduled or on-demand task:

- **Archive to Google Docs**: append each day's digest to a running Doc
  (one heading per date), so the year's reading is searchable in one place.
- **A "to read" tracker**: reply to the digest email with the papers you want to
  keep; a second task moves them into a Sheets tracking table
  (`arxiv_id` | `title` | `why` | `status`).
- **Calendar reminders**: for papers marked as worth a close read, create a
  30-minute Calendar block later that week, with the arXiv link in the
  description.
- **Weekly roll-up**: a Sunday task that reads the `archive` sheet and mails a
  short summary of the week's themes.

Keep these as separate tasks. Do not bolt them onto the daily instructions —
a longer prompt makes the core digest less reliable.
