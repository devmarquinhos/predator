import os
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
TWITCH_API_URL = "https://api.twitch.tv/helix/streams"

STREAMERS = {
    "Xarola": "xarola_",
    "Otsuka": "otsukaxd"
}

def get_streamer_status(username):
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}"
    }
    params = {"user_login": username}
    response = requests.get(TWITCH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()["data"]
        return bool(data)
    return False

async def streamers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = "🎥 <b>Streamers parceiros da FURIA:</b>\n\n"
    for name, login in STREAMERS.items():
        is_live = get_streamer_status(login)
        status = "🔴 Ao vivo" if is_live else "⚫️ Offline"
        link = f"https://twitch.tv/{login}"
        message += f"• <a href='{link}'>{name}</a> — {status}\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar ao menu", callback_data="menu_principal")]
    ])

    await query.edit_message_text(
        message,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=keyboard
    )
