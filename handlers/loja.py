from telegram.ext import ContextTypes
from telegram import Update
from utils import send_message
from menus import back_menu

async def loja_furia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "🛍 *Conheça a loja oficial da FURIA!*\n\nClique no link abaixo para ver os produtos:\n\n👉 [furia.gg](https://www.furia.gg/)"
    await send_message(update, texto, reply_markup=back_menu())
