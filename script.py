import logging
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ========== Configs e Tokens ==========

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")

FURIA_MASC_ID = 124530
FURIA_FEM_ID = 129384

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== Funções Utilitárias ==========

def get_headers():
    return {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

async def send_message(update: Update, text: str, reply_markup=None):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup)

def build_menu(options: list[list[tuple[str, str]]]):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in options
    ])

# ========== Menus ==========

def main_menu():
    return build_menu([
        [("Próximos Jogos", "proximos_jogos"), ("Últimos Jogos", "ultimos_jogos")],
        [("Elenco Atual", "menu_elenco")]
    ])

def back_menu(callback="menu_principal"):
    return build_menu([[("🏠 Voltar ao Menu", callback)]])

def elenco_menu():
    return build_menu([
        [("🧔 Elenco Masculino", "elenco_masc")],
        [("👩 Elenco Feminino", "elenco_fem")],
        [("🏠 Voltar ao Menu", "menu_principal")]
    ])

# ========== Comandos ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "吼 E aí, torcedor da FURIA!\n"
        "Prepare o coração para rugir com as novidades do nosso time!\n"
        "Selecione uma opção abaixo para ficar por dentro de tudo:"
    )
    await send_message(update, texto, reply_markup=main_menu())

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
        await send_message(update, "❌ Erro ao buscar jogos passados.")
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
        await send_message(update, "🚫 Nenhuma partida recente encontrada.")
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

    await send_message(update, resposta)

async def menu_elenco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, "🎮 Qual elenco da FURIA você quer conhecer?", reply_markup=elenco_menu())

async def mostrar_elenco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    team_id = FURIA_MASC_ID if query.data == "elenco_masc" else FURIA_FEM_ID
    titulo = "🧔 Elenco Masculino da FURIA:" if team_id == FURIA_MASC_ID else "👩 Elenco Feminino da FURIA:"
    url = f"https://api.pandascore.co/csgo/players?filter[team_id]={team_id}"

    response = requests.get(url, headers=get_headers())
    if response.status_code != 200:
        await query.edit_message_text("❌ Erro ao buscar o elenco.", reply_markup=back_menu("menu_elenco"))
        return

    players = response.json()
    if not players:
        await query.edit_message_text("🚫 Nenhum jogador encontrado.", reply_markup=back_menu("menu_elenco"))
        return

    resposta = f"{titulo}\n\n" + "\n".join(f"🎮 {p.get('name', 'Desconhecido')}" for p in players)
    await query.edit_message_text(resposta, reply_markup=back_menu("menu_elenco"))

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
        await send_message(update, "📴 A FURIA não está jogando no momento.")
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

    await send_message(update, resposta)

# ========== Bot Init ==========

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aovivo", aovivo))

    app.add_handler(CallbackQueryHandler(start, pattern="menu_principal"))
    app.add_handler(CallbackQueryHandler(proximos_jogos, pattern="proximos_jogos"))
    app.add_handler(CallbackQueryHandler(ultimos_jogos, pattern="ultimos_jogos"))
    app.add_handler(CallbackQueryHandler(menu_elenco, pattern="menu_elenco"))
    app.add_handler(CallbackQueryHandler(mostrar_elenco, pattern="elenco_masc"))
    app.add_handler(CallbackQueryHandler(mostrar_elenco, pattern="elenco_fem"))

    logger.info("Bot da FURIA está online! 🔥")
    app.run_polling()

if __name__ == "__main__":
    main()
