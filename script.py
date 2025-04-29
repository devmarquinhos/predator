import logging
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# TODO -> aonde assistir a FURIA
# TODO -> streamers parceiros
# TODO -> loja da FURIA
# TODO (Opt.) -> integrar um chatbot

# ========== Configuração Inicial ==========

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")

FURIA_TEAM_ID = 124530
FURIA_MASC_ID = FURIA_TEAM_ID
FURIA_FEM_ID = 129384

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== Funções Auxiliares ==========

def get_headers():
    return {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

async def send_message(update: Update, text: str, reply_markup=None):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup)

def build_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("Próximos Jogos", callback_data="proximos_jogos"),
            InlineKeyboardButton("Últimos Jogos", callback_data="ultimos_jogos"),
        ],
        [
            InlineKeyboardButton("Elenco Atual", callback_data="menu_elenco")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_back_menu(callback):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Voltar ao Menu", callback_data=callback)]
    ])

# ========== Comandos ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "吼 E aí, torcedor da FURIA!\n"
        "Prepare o coração para rugir com as novidades do nosso time!\n"
        "Selecione uma opção abaixo para ficar por dentro de tudo:"
    )
    await send_message(update, texto, reply_markup=build_main_menu())

async def proximos_jogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        logger.error(f"Erro {response.status_code}: {response.text}")
        await send_message(update, f"❌ Erro ao buscar jogos: {response.status_code}", reply_markup=build_back_menu("menu_principal"))
        return

    partidas = response.json()
    furia_partidas = [p for p in partidas if any(
        opp['opponent'] and opp['opponent']['id'] == FURIA_TEAM_ID for opp in p.get('opponents', [])
    )]

    if not furia_partidas:
        await send_message(update, "🚫 Nenhuma partida futura encontrada para a FURIA.", reply_markup=build_back_menu("menu_principal"))
        return

    resposta = "🔥 Próximos jogos da FURIA:\n\n"
    for partida in furia_partidas[:5]:
        try:
            time1 = partida['opponents'][0]['opponent']['name']
            time2 = partida['opponents'][1]['opponent']['name']
            data = partida['begin_at'][:10] if partida['begin_at'] else "Data a definir"
            resposta += f"🆚 {time1} vs {time2}\n📅 {data}\n\n"
        except Exception as e:
            logger.error(f"Erro ao formatar partida: {e}")

    await send_message(update, resposta, reply_markup=build_back_menu("menu_principal"))

async def ultimos_jogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.pandascore.co/csgo/matches/past?filter[opponent_id]={FURIA_TEAM_ID}&sort=-begin_at&page[size]=20"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        logger.error(f"Erro {response.status_code}: {response.text}")
        await send_message(update, f"❌ Erro ao buscar jogos: {response.status_code}")
        return

    partidas = response.json()
    hoje = datetime.now(timezone.utc)
    jogos_relevantes = []

    for partida in partidas:
        try:
            opponents = partida.get('opponents', [])
            if len(opponents) < 2:
                continue

            adversario = next((opp['opponent'] for opp in opponents if opp['opponent']['id'] != FURIA_TEAM_ID), None)
            if not adversario:
                continue

            data_inicio_str = partida.get('begin_at')
            if not data_inicio_str:
                continue

            data_inicio = datetime.fromisoformat(data_inicio_str.replace('Z', '+00:00'))

            if data_inicio > hoje:
                continue

            placares = partida.get('results', [])
            placar_furia = next((score.get('score', 0) for score in placares if score.get('team_id') == FURIA_TEAM_ID), 0)
            placar_oponente = next((score.get('score', 0) for score in placares if score.get('team_id') != FURIA_TEAM_ID), 0)

            vencedor = partida.get('winner', {})
            furia_ganhou = vencedor.get('id') == FURIA_TEAM_ID

            jogos_relevantes.append({
                'data': data_inicio.strftime('%d/%m/%Y'),
                'adversario': adversario.get('name', 'Desconhecido'),
                'placar_furia': placar_furia,
                'placar_oponente': placar_oponente,
                'resultado': "✅ Vitória" if furia_ganhou else "❌ Derrota",
                'campeonato': partida.get('league', {}).get('name', 'Campeonato Desconhecido'),
                'timestamp': data_inicio
            })

        except Exception as e:
            logger.error(f"Erro ao processar partida: {e}")

    jogos_relevantes = sorted(jogos_relevantes, key=lambda x: x['timestamp'], reverse=True)[:5]

    if not jogos_relevantes:
        await send_message(update, "🚫 Nenhuma partida recente encontrada para a FURIA.")
        return

    resposta = "📜 Últimos 5 jogos da FURIA:\n\n"
    for i, jogo in enumerate(jogos_relevantes):
        resposta += (
            f"🏆 Jogo {i + 1} - {jogo['campeonato']}\n"
            f"📅 {jogo['data']}\n"
            f"🆚 {jogo['adversario']}\n"
            f"🔢 Placar: {jogo['placar_furia']} x {jogo['placar_oponente']}\n"
            f"🏁 Resultado: {jogo['resultado']}\n\n"
        )

    await send_message(update, resposta)

async def menu_elenco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧔 Elenco Masculino", callback_data="elenco_masc")],
        [InlineKeyboardButton("👩 Elenco Feminino", callback_data="elenco_fem")],
        [InlineKeyboardButton("🏠 Voltar ao Menu", callback_data="menu_principal")]
    ])
    await send_message(update, "🎮 Qual elenco da FURIA você quer conhecer?", reply_markup=keyboard)

async def mostrar_elenco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    team_id = FURIA_MASC_ID if query.data == "elenco_masc" else FURIA_FEM_ID
    titulo = "🧔 Elenco Masculino da FURIA:" if team_id == FURIA_MASC_ID else "👩 Elenco Feminino da FURIA:"

    url = f"https://api.pandascore.co/csgo/players?filter[team_id]={team_id}"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        await query.edit_message_text("❌ Erro ao buscar o elenco.", reply_markup=build_back_menu("menu_elenco"))
        return

    players = response.json()

    if not players:
        await query.edit_message_text("🚫 Nenhum jogador encontrado.", reply_markup=build_back_menu("menu_elenco"))
        return

    resposta = f"{titulo}\n\n"
    for player in players:
        resposta += f"🎮 {player.get('name', 'Nome desconhecido')}\n"

    await query.edit_message_text(resposta, reply_markup=build_back_menu("menu_elenco"))

async def aovivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.pandascore.co/csgo/matches/running"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        await send_message(update, "❌ Erro ao buscar partidas ao vivo.")
        return

    partidas = response.json()

    furia_partida = next((p for p in partidas if any(
        opp['opponent'] and opp['opponent']['id'] == FURIA_TEAM_ID for opp in p.get('opponents', [])
    )), None)

    if not furia_partida:
        await send_message(update, "📴 A FURIA não está jogando no momento.")
        return

    opponents = furia_partida.get('opponents', [])
    time1 = opponents[0]['opponent']['name'] if opponents else "TBD"
    time2 = opponents[1]['opponent']['name'] if len(opponents) > 1 else "TBD"
    torneio = furia_partida.get('tournament', {}).get('name', 'Torneio desconhecido')
    status_partida = furia_partida.get('status', 'Status desconhecido').capitalize()

    resposta = (
        f"🔥 A FURIA está jogando agora!\n\n"
        f"🏆 Torneio: {torneio}\n"
        f"🆚 {time1} vs {time2}\n"
        f"🎯 Status: {status_partida}\n"
    )

    await send_message(update, resposta)

# ========== Inicialização do Bot ==========

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aovivo", aovivo))

    app.add_handler(CallbackQueryHandler(proximos_jogos, pattern="proximos_jogos"))
    app.add_handler(CallbackQueryHandler(ultimos_jogos, pattern="ultimos_jogos"))
    app.add_handler(CallbackQueryHandler(menu_elenco, pattern="menu_elenco"))
    app.add_handler(CallbackQueryHandler(mostrar_elenco, pattern="elenco_masc"))
    app.add_handler(CallbackQueryHandler(mostrar_elenco, pattern="elenco_fem"))
    app.add_handler(CallbackQueryHandler(start, pattern="menu_principal"))

    logger.info("Bot da FURIA está rodando! 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
