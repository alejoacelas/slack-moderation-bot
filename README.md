# Slack moderation bot

A Slack bot for channel owners who want a "no template messages without asking me
first" rule. A template message is a post written for many places rather than for
the channel: event announcements, job ads, program calls, newsletter promos.

When someone posts one, the bot replies in the thread and asks them to delete it.
It reads your DMs with the author from the past week first, and stays quiet if you
already approved the post. It never deletes anything, so it works for channel
owners who aren't workspace admins.

Each new top-level post costs one Claude API call, and a flagged post one more for
the DM check. Post text, and for flagged posts your DMs with the author, is sent to
Anthropic's API.

## Setup

You need Python with [uv](https://docs.astral.sh/uv/), an
[Anthropic API key](https://console.anthropic.com/settings/keys), and a computer
that stays on while the bot runs.

1. **Create the app.** Go to [api.slack.com/apps](https://api.slack.com/apps) →
   **Create New App** → **From a manifest**, pick your workspace, and paste
   [manifest.yaml](manifest.yaml). If you don't want the DM approval check, delete
   the `user:` block first.
2. **Install it.** Under **Install App**, click **Install to Workspace** and
   allow. If your workspace requires admin approval, the button reads **Request
   to Install**; send the request and wait for an admin to approve before going on.
3. **Collect the tokens** into a file named `.env`, following
   [.env.example](.env.example):
   - `SLACK_BOT_TOKEN`: **OAuth & Permissions** → Bot User OAuth Token.
   - `SLACK_USER_TOKEN`: same page → User OAuth Token. Leave it out to skip the
     DM check.
   - `SLACK_APP_TOKEN`: **Basic Information** → App-Level Tokens → **Generate
     Token and Scopes**, add the scope `connections:write`.
   - `ANTHROPIC_API_KEY`: your Anthropic key.
4. **Configure channels.** Copy [config.example.toml](config.example.toml) to
   `config.toml`, set `owner_name`, and add a block per channel with mode
   `dry_run`.
5. **Invite the bot** by typing `/invite @Moderation Bot` in each channel. Slack
   only sends the bot messages from channels it's in.
6. **Check it on past posts:**
   `uv run --env-file .env python -m modbot.backfill CHANNEL_ID`. It lists the
   posts it would have flagged and writes its reasoning to `data/`. It never posts.
7. **Run it:** `uv run --env-file .env python -m modbot.bot`. In `dry_run` it only
   logs decisions to `data/decisions.jsonl`. When those look right, set the
   channel to `live` and restart.

Tell your channel about the rule before going live; the bot's replies assume
members know it.

## Keeping it running

The bot only acts while the process runs. On an always-on Linux machine, a
systemd user service keeps it up across crashes and reboots. Save this as
`~/.config/systemd/user/modbot.service`, with your clone's path:

```ini
[Unit]
Description=Slack moderation bot
After=network-online.target

[Service]
WorkingDirectory=/home/you/slack-moderation-bot
ExecStart=/home/you/.local/bin/uv run --env-file .env python -m modbot.bot
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

Then run `systemctl --user enable --now modbot` and `loginctl enable-linger`.
Run only one copy at a time; Slack splits messages between connected copies.

## Adjusting it

- The definition of a template message and the approval rules are prompts in
  [modbot/classifier.py](modbot/classifier.py). When unsure, the bot doesn't flag.
- The reply wording is `reply_text` in [modbot/bot.py](modbot/bot.py).
- Set `MODBOT_MODEL=claude-haiku-5-5` in `.env` to cut cost; the default is
  `claude-opus-5-5`.
