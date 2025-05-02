import requests
import time
import logging
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes
from utils import send_message
from menus import back_menu

logger = logging.getLogger(__name__)

# Cache de notícias em memória
noticias_cache = {
    "data": [],
    "timestamp": 0
}

async def noticias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://draft5.gg/arquivo"
    headers = {"User-Agent": "Mozilla/5.0"}

    if time.time() - noticias_cache["timestamp"] < 600:
        noticias = noticias_cache["data"]
    else:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                await send_message(update, "❌ Erro ao buscar as notícias.", reply_markup=back_menu())
                return

            soup = BeautifulSoup(response.text, "html.parser")
            artigos = soup.find_all("a", href=True)

            noticias = []
            vistos = set()

            for link in artigos:
                href = link['href']
                texto = link.get_text(strip=True)

                # Filtra apenas notícias sobre a FURIA
                if "FURIA" in texto.upper() and "/noticia/" in href:
                    titulo = texto.split("Por")[0].strip()
                    url_completo = f"https://draft5.gg{href}" if href.startswith("/") else href
                    if url_completo not in vistos:
                        noticias.append((titulo, url_completo))
                        vistos.add(url_completo)
                if len(noticias) >= 5:
                    break

            noticias_cache["data"] = noticias
            noticias_cache["timestamp"] = time.time()

        except Exception as e:
            logger.error(f"Erro ao processar notícias: {e}")
            await send_message(update, "❌ Ocorreu um erro ao buscar as notícias.", reply_markup=back_menu())
            return

    if noticias:
        resposta = "📰 *Últimas notícias da FURIA*\n"
        for titulo, link in noticias:
            resposta += f"\n→ [{titulo}]({link})\n"
        await send_message(update, resposta, reply_markup=back_menu())
    else:
        await send_message(update, "🦁 Nenhuma notícia recente da FURIA encontrada.", reply_markup=back_menu())
