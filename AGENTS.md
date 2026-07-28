# For AI agents (Codex, Gemini Spark, etc.)

If the user asked you to **install / set up this automation**, first check your
own capabilities, then open the matching playbook:

- **Can you run a shell (git, python3)?** → `INSTALL.md`. You are the installer
  agent. Default execution backend for Codex users: **Backend B (GitHub Actions
  cron)** — see INSTALL.md Step 2B. Do not attempt to create Claude cloud
  routines.
- **No shell, no git, no script execution** (Gemini Spark and similar Workspace
  assistants) → `INSTALL-SPARK.md`. Its default is **Backend C (Spark-native)**,
  which needs no GitHub account, no mail app password and no LLM API key; that
  file also explains how to reach Backend B through the GitHub web UI if the
  user does want the full scripted version.
