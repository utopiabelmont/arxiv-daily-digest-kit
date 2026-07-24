# arXiv Digest Kit · 每日论文简报自动化套件

每天定时抓取你研究领域的最新 arXiv 论文（可选行业新闻），用你的语言生成
摘要简报和可视化图卡，自动发送到你的邮箱。全程运行在 Claude 云端，
你的电脑关机也照常推送。

## 一句话安装

打开 **Claude Code**（终端 / 桌面版），对它说：

> 安装这个自动化进程 https://github.com/OWNER/arxiv-digest-kit
>
> (English) Install this automation: https://github.com/OWNER/arxiv-digest-kit

Claude 会读取本仓库的 `INSTALL.md` 安装向导，用你的语言问你 5 个问题
（语言 / 研究领域 / 推送时间 / 邮箱 / 是否要行业新闻），然后自动完成配置。

## 前提条件

- Claude Pro / Max（或 Team/Enterprise）订阅，已启用 Claude Code on the web
- GitHub 账号；本机装有 `git`（有 `gh` CLI 更佳）
- 一个 Gmail 账号用于发信（向导会指导你生成应用专用密码）

## 架构

云端 Routine（每日定时）→ `fetch_arxiv.py` 抓论文（可选 `fetch_news.py` 抓新闻）
→ 模型写简报 + 图卡 → 推送到你的 GitHub 仓库 → GitHub Action 发邮件（正文 + HTML 图卡附件）。

安装后所有数据都在你自己的私有仓库和邮箱里，与本模板仓库无关。
