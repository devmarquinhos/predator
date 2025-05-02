from telegram import Update
from telegram.ext import ContextTypes
from utils import send_message
from menus import main_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "Você acaba de entrar no lado mais selvagem do eSports.\n"
        "Aqui é onde a informação chega primeiro — jogos, bastidores, time e novidades da FURIA.\n"
        "Só os verdadeiros têm acesso.\n"
        "Toque em uma opção e mergulhe no universo FURIA. 🖤💛"
    )
    await send_message(update, texto, reply_markup=main_menu())
