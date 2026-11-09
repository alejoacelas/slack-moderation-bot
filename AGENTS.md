# slack-moderation-bot

Scope: the Moderation Bot, which asks authors to delete template messages
(posts not written for the channel) that the channel owner didn't approve in a
DM. [README.md](README.md) is the public setup guide; keep it accurate for
someone who isn't a workspace admin. Alejo's own deployment lives in
[deploy/alejo/](deploy/alejo/).

- Visibility: public repo; Slack history and bot decisions stay in ignored `data/`
- Google account: none
- Still running or billing: `modbot.service` on the agent server, live in
  #too-much-ai (`C0B9PH0TA7J`) and the private #modbot-test (`C0CC9UY80MR`);
  Anthropic API usage per post

Replaces `projects/archive/2026-10-27-slackbots`, whose GitHub repo is archived.

## Alejo's deployment

Slack app `A0CCFRH2CPL` ("Moderation Bot") on the AI Uplift for EA workspace
(`T094GSSSF3M`), Socket Mode. User token scopes are exactly `im:history` and
`im:read`; admin scopes make the install fail on this non-Enterprise workspace.

- [deploy/alejo/config.toml](deploy/alejo/config.toml) lists watched channels.
  Only set a main channel to `live` with Alejo's approval. The bot only receives
  messages from channels it's a member of; invite it first.
- On the agent server it runs as `alejo`'s user service
  ([deploy/alejo/modbot.service](deploy/alejo/modbot.service)) from
  `~/work/slack-moderation-bot`. It runs as `alejo` rather than `agent` because it
  makes single tool-free Claude calls, not agent sessions.
- Deploy: push, then
  `ssh agent-server 'cd ~/work/slack-moderation-bot && git pull && ~/.local/bin/uv sync --frozen && systemctl --user restart modbot'`.
  Logs: `ssh agent-server journalctl --user -u modbot -f`.
- Run locally with
  `~/best/areas/dotfiles/bin/op-agent run --env-file=deploy/alejo/mac.env.tpl -- uv run python -m modbot.bot`
  (or `modbot.backfill CHANNEL_ID`). Stop the server bot first: Slack splits
  events between connections.

## Credentials (personal 1Password)

Server copies are in vault `server-agents`, Mac copies in `mac-agents`.

| Variable | Item | Field |
|---|---|---|
| `SLACK_BOT_TOKEN` | Moderation Bot Slack | `bot_token` |
| `SLACK_APP_TOKEN` | Moderation Bot Slack | `app_token` |
| `SLACK_USER_TOKEN` | Moderation Bot Slack | `user_token` |
| `ANTHROPIC_API_KEY` | ANTHROPIC_API_KEY — personal-apps-2026-10 | `credential` |
