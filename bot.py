import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_TOKEN
from handlers.jogos import proximos_jogos, ultimos_jogos
# (importaremos os demais handlers conforme forem modularizados)
from handlers.start import start
from handlers.elenco import menu_elenco, mostrar_elenco
from handlers.noticias import noticias
from handlers.aovivo import aovivo
from handlers.loja import loja_furia

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


    logger.info("Bot da FURIA está online! 🔥")
    app.run_polling()

if __name__ == "__main__":
    main()
