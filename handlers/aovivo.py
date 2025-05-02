import requests
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import FURIA_MASC_ID
from utils import get_headers, send_message
from menus import back_menu

logger = logging.getLogger(__name__)

async def aovivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.pandascore.co/csgo/matches/running"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        await send_message(update, "❌ Erro ao buscar partidas ao vivo.")
        return

    partidas = response.json()

    partida = next((p for p in partidas if any(
        opp.get("opponent", {}).get("id") == FURIA_MASC_ID for opp in p.get("opponents", [])
    )), None)

    if not partida:
        await send_message(update, "📴 A FURIA não está jogando no momento.", reply_markup=back_menu())
        return

    opponents = partida.get("opponents", [])
    time1 = opponents[0]["opponent"]["name"] if opponents else "TBD"
    time2 = opponents[1]["opponent"]["name"] if len(opponents) > 1 else "TBD"
    torneio = partida.get("tournament", {}).get("name", "Torneio desconhecido")
    status = partida.get("status", "Desconhecido").capitalize()

    resposta = (
        f"🔥 A FURIA está jogando agora!\n\n"
        f"🏆 Torneio: {torneio}\n"
        f"🆚 {time1} vs {time2}\n"
        f"🎯 Status: {status}\n"
    )

    await send_message(update, resposta, reply_markup=back_menu())
