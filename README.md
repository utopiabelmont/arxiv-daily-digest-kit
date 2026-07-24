# arXiv Digest Kit · 每日论文简报自动化 · 論文ダイジェスト自動配信

---

## 中文

每天定时抓取你研究领域的最新 arXiv 论文（可选行业新闻），用你的语言生成摘要
简报和可视化图卡，自动发送到邮箱。运行在云端，电脑关机也照常推送。

**一句话安装** — 对你的编码代理说：

- Claude Code：`安装这个自动化进程 https://github.com/OWNER/arxiv-digest-kit`
- Codex：`Install this automation: https://github.com/OWNER/arxiv-digest-kit`

代理会读取 `INSTALL.md` 向导，用你的语言问 5 个问题（语言 / 研究领域(可贴
Google Scholar/KAKEN 链接) / 推送时间 / 邮箱 / 是否要行业新闻），然后自动完成配置。

**两种运行后端**（向导会帮你选）：
- **A · Claude 云端 Routine**：需 Claude Pro/Max，由 Routine 会话写简报；
- **B · GitHub Actions 定时**：Codex 用户默认走这条；需一个 LLM API Key
  （OpenAI 或 Anthropic，日成本约几美分），全程跑在 GitHub 云上。

前提：GitHub 账号 + git；一个 Gmail（发信用，向导指导生成应用专用密码）。

---

## English

Fetches the newest arXiv papers in your field every day (industry news
optional), writes a digest **in your language** plus visual summary cards,
and emails them to you. Runs fully in the cloud — your machine can stay off.

**One-line install** — tell your coding agent:

- Claude Code: `Install this automation: https://github.com/OWNER/arxiv-digest-kit`
- Codex: `Install this automation: https://github.com/OWNER/arxiv-digest-kit`

The agent reads `INSTALL.md` and interviews you (language / research field —
keywords or your Google Scholar / KAKEN / ORCID URL / push time / email /
industry news yes-no), then configures everything.

**Two execution backends** (the wizard picks with you):
- **A · Claude cloud Routine** — needs Claude Pro/Max; the Routine session
  writes the digest.
- **B · GitHub Actions cron** — default for Codex users; needs one LLM API
  key (OpenAI or Anthropic, ~a few cents/day); everything runs on GitHub.

Prerequisites: a GitHub account + git; a Gmail account for sending (the
wizard guides you through creating an app password).

---

## 日本語

毎日決まった時刻に、あなたの研究分野の最新 arXiv 論文（業界ニュースは任意）
を取得し、**指定した言語**でダイジェストとビジュアル要約カードを生成して
メールで届けます。すべてクラウド上で動作し、PC の電源が切れていても配信されます。

**ワンライン・インストール** — コーディングエージェントに次のように伝えてください：

- Claude Code：`このオートメーションをインストールして https://github.com/OWNER/arxiv-digest-kit`
- Codex：`Install this automation: https://github.com/OWNER/arxiv-digest-kit`

エージェントが `INSTALL.md` のウィザードを読み、あなたの言語で 5 つの質問
（言語 / 研究分野 — キーワードまたは Google Scholar・KAKEN・ORCID の URL /
配信時刻 / メールアドレス / 業界ニュースの要否）を行い、自動で設定します。

**2 つの実行バックエンド**（ウィザードが一緒に選びます）：
- **A · Claude クラウド Routine** — Claude Pro/Max が必要。Routine セッションが
  ダイジェストを執筆します。
- **B · GitHub Actions cron** — Codex ユーザーはこちらが既定。LLM API キー
  （OpenAI または Anthropic、1 日数セント程度）が必要で、全処理が GitHub 上で
  完結します。

前提条件：GitHub アカウント + git、送信用の Gmail アカウント
（アプリパスワードの作成はウィザードが案内します）。

---

### Architecture / 架构 / 構成

fetch (arXiv API + Google News RSS) → LLM digest & cards → commit to your
private repo → GitHub Action emails body + HTML card attachment.
Cross-day dedup · timezone-aware dating · zero pip dependencies.
