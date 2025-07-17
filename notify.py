"""Notification utilities."""

import os
from discord_webhook import DiscordWebhook


def send_discord_notification(message: str):
    """Send a message to Discord webhook.

    Google Voice SMS requires external setup; use Discord by default.
    """
    from signals import load_config

    config = load_config()
    webhook_url = config.get("discord_webhook_url")

    if not webhook_url or "STOCK_SIGNAL_WEBHOOK" in webhook_url:
        webhook_url = os.environ.get("STOCK_SIGNAL_WEBHOOK")

    if not webhook_url or "YOUR_DISCORD_WEBHOOK_URL" in webhook_url:
        print("Discord webhook URL not configured")
        return
    try:
        webhook = DiscordWebhook(url=webhook_url, content=message)
        response = webhook.execute()
        if response.status_code != 200:
            print(f"Failed to send notification: {response.status_code}")
    except Exception as exc:
        print(f"Error sending notification: {exc}")
