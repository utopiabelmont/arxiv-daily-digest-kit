# arXiv Digest Kit · 每日论文简报自动化 · 論文ダイジェスト自動配信

---

## 中文

每天定时抓取你研究领域的最新 arXiv 论文（可选行业新闻），用你的语言生成摘要
简报和可视化图卡，自动发送到邮箱。运行在云端，电脑关机也照常推送。

**一句话安装** — 对你的编码代理说：

- Claude Code：`安装这个自动化进程 https://github.com/utopiabelmont/arxiv-digest-kit`
- Codex：`Install this automation: https://github.com/utopiabelmont/arxiv-digest-kit`

代理会读取 `INSTALL.md` 向导：先做 3 项前置检查（发信邮箱已开两步验证 /
gh 已登录正确账号 / Claude 路线还需确认 GitHub App 已安装），再用你的语言
问约 11 个问题——简报语言、研究领域（关键词或 Google Scholar/KAKEN/ORCID
链接）、每日篇数偏好、推送时间、**发信邮箱服务商（Gmail/Outlook/QQ/163/
其他均可）**、收件邮箱、是否要行业新闻、仓库名与可见性、邮件标题、
模型/LLM 提供商、图卡深链打开哪家助手——然后自动完成全部配置。
凡有默认值的问题都可以直接回答"默认"。

**两种运行后端**（向导会帮你选）：
- **A · Claude 云端 Routine**：需 Claude Pro/Max，由 Routine 会话写简报；
- **B · GitHub Actions 定时**：Codex 用户默认走这条；需一个 LLM API Key
  （OpenAI 或 Anthropic，日成本约几美分），全程跑在 GitHub 云上。

前提：GitHub 账号 + git；一个支持 SMTP 的发信邮箱（应用专用密码/授权码的
生成路径向导会按服务商分别指导）。

---

## English

Fetches the newest arXiv papers in your field every day (industry news
optional), writes a digest **in your language** plus visual summary cards,
and emails them to you. Runs fully in the cloud — your machine can stay off.

**One-line install** — tell your coding agent:

- Claude Code: `Install this automation: https://github.com/utopiabelmont/arxiv-digest-kit`
- Codex: `Install this automation: https://github.com/utopiabelmont/arxiv-digest-kit`

The agent reads `INSTALL.md`: it runs 3 pre-checks (two-step verification on
your sending mailbox / `gh` logged into the right account / for the Claude
path, the GitHub App actually installed), then interviews you in your
language — about 11 questions covering digest language, research field
(keywords or your Google Scholar / KAKEN / ORCID URL), papers-per-day
preference, push time, **sending-email provider (Gmail / Outlook / QQ /
163 / other)**, recipient address, industry news yes-no, repo name &
visibility, subject line, model / LLM provider, and which assistant the
card deep-links open — then configures everything. Answer "default" to any
question that offers one.

**Two execution backends** (the wizard picks with you):
- **A · Claude cloud Routine** — needs Claude Pro/Max; the Routine session
  writes the digest.
- **B · GitHub Actions cron** — default for Codex users; needs one LLM API
  key (OpenAI or Anthropic, ~a few cents/day); everything runs on GitHub.

Prerequisites: a GitHub account + git; any SMTP-capable sending mailbox
(the wizard gives provider-specific app-password / auth-code steps).

---

## 日本語

毎日決まった時刻に、あなたの研究分野の最新 arXiv 論文（業界ニュースは任意）
を取得し、**指定した言語**でダイジェストとビジュアル要約カードを生成して
メールで届けます。すべてクラウド上で動作し、PC の電源が切れていても配信されます。

**ワンライン・インストール** — コーディングエージェントに次のように伝えてください：

- Claude Code：`このオートメーションをインストールして https://github.com/utopiabelmont/arxiv-digest-kit`
- Codex：`Install this automation: https://github.com/utopiabelmont/arxiv-digest-kit`

エージェントは `INSTALL.md` を読み、まず 3 つの事前チェック（送信メールの
2 段階認証 / gh の正しいアカウントへのログイン / Claude 経路の場合は
GitHub App のインストール確認）を行い、続いてあなたの言語で約 11 の質問
——ダイジェストの言語、研究分野（キーワードまたは Google Scholar・KAKEN・
ORCID の URL）、1 日の論文数の希望、配信時刻、**送信メールプロバイダ
（Gmail / Outlook / QQ / 163 / その他）**、受信アドレス、業界ニュースの
要否、リポジトリ名と公開設定、件名、モデル / LLM プロバイダ、カードの
ディープリンクで開くアシスタント——に答えるだけで、設定は自動で完了します。
デフォルトがある質問には「デフォルトで」と答えられます。

**2 つの実行バックエンド**（ウィザードが一緒に選びます）：
- **A · Claude クラウド Routine** — Claude Pro/Max が必要。
- **B · GitHub Actions cron** — Codex ユーザーはこちらが既定。LLM API キー
  （OpenAI または Anthropic、1 日数セント程度）が必要で、全処理が GitHub 上で
  完結します。

前提条件：GitHub アカウント + git、SMTP 送信可能なメールアカウント
（アプリパスワード / 授権コードの取得手順はプロバイダ別にウィザードが案内します）。

---

### Architecture / 架构 / 構成

fetch (arXiv API + Google News RSS) → LLM digest & cards → commit to your
repo → GitHub Action emails body + HTML card attachment.
Cross-day dedup · timezone-aware dating · multi-provider SMTP · zero pip deps.
