# slack-moderation-bot

Scope: a shareable, self-contained version of the Moderation Bot, for other
channel owners to set up. [README.md](README.md) is the setup guide; keep it
accurate for someone who isn't a workspace admin.

- Visibility: public repo; holds no tokens, channel IDs or Slack data
- Google account: none
- Still running or billing: none. Alejo's live copy runs from
  [slackbots](/Users/alejo/best/projects/2026-10-27-slackbots/AGENTS.md);
  port behaviour changes between the two.

Test with a local `config.toml` and `.env` (both ignored). For Alejo's workspace,
the bot token and Anthropic key are in personal 1Password, vault `mac-agents`:
items `Moderation Bot Slack` (`bot_token`, `app_token`) and
`ANTHROPIC_API_KEY — personal-apps-2026-10` (`credential`).
