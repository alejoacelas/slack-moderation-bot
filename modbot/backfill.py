"""Classify a channel's past posts and list the ones the bot would flag. Never posts.

Usage: uv run --env-file .env python -m modbot.backfill CHANNEL_ID
The bot must be in the channel. Writes data/backfill-<channel>.json.
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
from slack_sdk import WebClient

from modbot.classifier import classify, violations
from modbot.config import load_config
from modbot.slack_util import is_top_level, load_users


def fetch_history(slack: WebClient, channel_id: str) -> list[dict]:
    msgs, cursor = [], None
    while True:
        r = slack.conversations_history(channel=channel_id, limit=200, cursor=cursor)
        msgs += r["messages"]
        cursor = r.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            return msgs


def main(channel_id: str) -> None:
    slack = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    channel = load_config()["channels"][channel_id]
    channel["purpose"] = slack.conversations_info(channel=channel_id)["channel"]["purpose"]["value"]
    users = load_users(slack)
    msgs = [m for m in fetch_history(slack, channel_id) if is_top_level(m)]
    print(f"{len(msgs)} top-level posts", file=sys.stderr)
    client = anthropic.Anthropic()

    def run(m):
        v = classify(client, m, channel, users)
        return {
            "ts": m["ts"],
            "author": users.get(m.get("user", ""), m.get("user")),
            "permalink": slack.chat_getPermalink(channel=channel_id, message_ts=m["ts"])["permalink"],
            "text": m.get("text", ""),
            "verdict": v.model_dump() if v else None,
            "violations": violations(v) if v else ["refused"],
        }

    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(run, msgs))

    path = Path("data") / f"backfill-{channel['name']}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    flagged = [r for r in results if r["violations"]]
    for r in flagged:
        print(f"{r['author']}: {r['permalink']}")
    print(f"{len(flagged)} flagged of {len(results)}; details in {path}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
