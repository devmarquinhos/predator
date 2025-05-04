import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_TOKEN
from handlers.jogos import proximos_jogos, ultimos_jogos
from handlers.start import start
from handlers.elenco import menu_elenco, mostrar_elenco
from handlers.noticias import noticias
from handlers.aovivo import aovivo
from handlers.loja import loja_furia
from handlers.streamers import streamers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aovivo", aovivo))
    app.add_handler(CommandHandler("noticias", noticias))

    app.add_handler(CallbackQueryHandler(start, pattern="menu_principal"))
    app.add_handler(CallbackQueryHandler(proximos_jogos, pattern="proximos_jogos"))
    app.add_handler(CallbackQueryHandler(ultimos_jogos, pattern="ultimos_jogos"))
    app.add_handler(CallbackQueryHandler(menu_elenco, pattern="menu_elenco"))
    app.add_handler(CallbackQueryHandler(mostrar_elenco, pattern="elenco_masc"))
    app.add_handler(CallbackQueryHandler(mostrar_elenco, pattern="elenco_fem"))
    app.add_handler(CallbackQueryHandler(noticias, pattern="noticias"))
    app.add_handler(CallbackQueryHandler(aovivo, pattern="aovivo"))
    app.add_handler(CallbackQueryHandler(loja_furia, pattern="loja_furia"))
    app.add_handler(CallbackQueryHandler(streamers, pattern="streamers"))

    logger.info("Bot da FURIA está online! 🔥")
    # Detecta se estamos no Render ou em ambiente local
    external_url = os.environ.get("RENDER_EXTERNAL_URL")
    port = int(os.environ.get("PORT", 8443))  # Padrão 8443 se não definido

    if external_url:
        logger.info("Executando via webhook.")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=f"{external_url.rstrip('/')}/{TELEGRAM_TOKEN}"
        )
    else:
        logger.info("Executando localmente com polling.")
        app.run_polling()

if __name__ == "__main__":
    main()
