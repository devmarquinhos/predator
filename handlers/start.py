from telegram import Update
from telegram.ext import ContextTypes
from utils import send_message
from menus import main_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "吼 E aí, torcedor da FURIA!\n"
        "Prepare o coração para rugir com as novidades do nosso time!\n"
        "Selecione uma opção abaixo para ficar por dentro de tudo:"
    )
    await send_message(update, texto, reply_markup=main_menu())
