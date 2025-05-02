import requests
from datetime import datetime, timezone
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import FURIA_MASC_ID
from utils import get_headers, send_message
from menus import back_menu

logger = logging.getLogger(__name__)

async def proximos_jogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        await send_message(update, "❌ Erro ao buscar jogos futuros.", reply_markup=back_menu())
        return

    partidas = response.json()
    jogos = [
        p for p in partidas if any(
            opp.get("opponent", {}).get("id") == FURIA_MASC_ID for opp in p.get("opponents", [])
        )
    ]

    if not jogos:
        await send_message(update, "🚫 Nenhuma partida futura encontrada para a FURIA.", reply_markup=back_menu())
        return

    resposta = "🔥 Próximos jogos da FURIA:\n\n"
    for partida in jogos[:5]:
        try:
            time1 = partida['opponents'][0]['opponent']['name']
            time2 = partida['opponents'][1]['opponent']['name']
            data = partida['begin_at'][:10] if partida.get('begin_at') else "Data a definir"
            resposta += f"🆚 {time1} vs {time2}\n📅 {data}\n\n"
        except Exception as e:
            logger.error(f"Erro ao formatar partida: {e}")

    await send_message(update, resposta, reply_markup=back_menu())


async def ultimos_jogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.pandascore.co/csgo/matches/past?filter[opponent_id]={FURIA_MASC_ID}&sort=-begin_at&page[size]=20"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        await send_message(update, "❌ Erro ao buscar jogos passados.", reply_markup=back_menu())
        return

    hoje = datetime.now(timezone.utc)
    partidas = response.json()
    jogos = []

    for partida in partidas:
        try:
            opponents = partida.get('opponents', [])
            if len(opponents) < 2:
                continue

            adversario = next((opp['opponent'] for opp in opponents if opp['opponent']['id'] != FURIA_MASC_ID), None)
            if not adversario:
                continue

            inicio_str = partida.get('begin_at')
            if not inicio_str:
                continue
            inicio = datetime.fromisoformat(inicio_str.replace("Z", "+00:00"))
            if inicio > hoje:
                continue

            placares = partida.get('results', [])
            placar_furia = next((s['score'] for s in placares if s['team_id'] == FURIA_MASC_ID), 0)
            placar_adv = next((s['score'] for s in placares if s['team_id'] != FURIA_MASC_ID), 0)

            venceu = partida.get('winner', {}).get('id') == FURIA_MASC_ID
            resultado = "✅ Vitória" if venceu else "❌ Derrota"

            jogos.append({
                "data": inicio.strftime("%d/%m/%Y"),
                "adversario": adversario['name'],
                "placar_furia": placar_furia,
                "placar_oponente": placar_adv,
                "resultado": resultado,
                "campeonato": partida.get('league', {}).get('name', 'Desconhecido'),
                "timestamp": inicio
            })
        except Exception as e:
            logger.error(f"Erro ao processar partida: {e}")

    if not jogos:
        await send_message(update, "🚫 Nenhuma partida recente encontrada.", reply_markup=back_menu())
        return

    resposta = "📜 Últimos 5 jogos da FURIA:\n\n"
    for i, jogo in enumerate(sorted(jogos, key=lambda x: x["timestamp"], reverse=True)[:5]):
        resposta += (
            f"🏆 Jogo {i+1} - {jogo['campeonato']}\n"
            f"📅 {jogo['data']}\n"
            f"🆚 {jogo['adversario']}\n"
            f"🔢 Placar: {jogo['placar_furia']} x {jogo['placar_oponente']}\n"
            f"🏁 Resultado: {jogo['resultado']}\n\n"
        )

    await send_message(update, resposta, reply_markup=back_menu())
