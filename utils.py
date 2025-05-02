import logging
import os
from telegram import Update
from telegram.ext import ContextTypes
from config import PANDASCORE_TOKEN

logger = logging.getLogger(__name__)

def get_headers():
    return {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

async def send_message(update: Update, text: str, reply_markup=None):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown", disable_web_page_preview=True)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown", disable_web_page_preview=True)
