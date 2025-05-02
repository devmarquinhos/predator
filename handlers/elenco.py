import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import FURIA_MASC_ID, FURIA_FEM_ID
from utils import get_headers, send_message
from menus import elenco_menu, back_menu

async def menu_elenco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, "🎮 Qual elenco da FURIA você quer conhecer?", reply_markup=elenco_menu())

async def mostrar_elenco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    # Define ID e título de acordo com a escolha do usuário
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
