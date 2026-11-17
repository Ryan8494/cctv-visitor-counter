"""
notifier.py — Kirim notifikasi alert via Telegram.

Token dan chat ID dibaca dari variabel lingkungan yang namanya
dikonfigurasi di config.json (telegram_token_env, telegram_chat_id_env).
Tidak menyimpan kredensial di kode.
"""

from __future__ import annotations

import os
import json
import logging

logger = logging.getLogger(__name__)


def _load_config() -> dict:
    """Muat config.json."""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_credentials() -> tuple[str, str] | None:
    """Ambil token dan chat_id dari variabel lingkungan.

    Returns:
        (token, chat_id) atau None jika tidak dikonfigurasi
    """
    config = _load_config()
    token_env = config.get("telegram_token_env", "TELEGRAM_TOKEN")
    chat_id_env = config.get("telegram_chat_id_env", "TELEGRAM_CHAT_ID")

    token = os.environ.get(token_env)
    chat_id = os.environ.get(chat_id_env)

    if not token or not chat_id:
        logger.warning(
            "Telegram tidak dikonfigurasi. Set variabel lingkungan "
            f"'{token_env}' dan '{chat_id_env}'."
        )
        return None

    return token, chat_id


def send_alert(event: str, detail: str) -> bool:
    """Kirim pesan alert ke Telegram.

    Args:
        event: nama event (misal ALERT_ANTREAN_PANJANG)
        detail: informasi detail tentang alert

    Returns:
        True jika berhasil terkirim, False jika gagal/tidak dikonfigurasi
    """
    creds = _get_credentials()
    if creds is None:
        logger.info(f"Notifikasi dilewati (Telegram belum dikonfigurasi): {event}")
        return False

    token, chat_id = creds

    # Impor requests di sini agar modul bisa diimpor tanpa requests terpasang
    try:
        import requests
    except ImportError:
        logger.error("Package 'requests' belum terpasang. Jalankan: pip install requests")
        return False

    # Format pesan
    emoji_map = {
        "ALERT_ANTREAN_PANJANG": "🚨",
        "ALERT_TUNGGU_LAMA": "⏰",
    }
    emoji = emoji_map.get(event, "ℹ️")

    message = f"{emoji} *{event}*\n{detail}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info(f"Notifikasi terkirim: {event}")
            return True
        else:
            logger.error(f"Gagal kirim notifikasi: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Error kirim notifikasi: {e}")
        return False
