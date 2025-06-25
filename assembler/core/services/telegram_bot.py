"""Module for sending messages via Telegram bot using the Telegram API."""

import requests
from decouple import config


class TelegramBotError(Exception):
    """Custom exception for Telegram bot errors."""

    pass  # noqa: PIE790


TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"


def send_telegram_message(text: str, chat_id: int) -> None:
    """Send a message to a Telegram chat."""
    url = f"{TELEGRAM_API_URL}sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    response = requests.post(url, json=payload, timeout=2)

    if not response.ok:
        msg = f"Failed to send message: {response.text}"
        raise TelegramBotError(msg)
