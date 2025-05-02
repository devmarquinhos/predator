from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_menu(options: list[list[tuple[str, str]]]):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in options
    ])

def main_menu():
    return build_menu([
        [("🏟️ - Próximos Jogos", "proximos_jogos"), ("⏮️ - Últimos Jogos", "ultimos_jogos")],
        [("👥 - Elenco Atual", "menu_elenco"), ("📰 - Notícias", "noticias")],
        [("📡 - Partida ao vivo", "aovivo")],
        [("🛒 - Loja da FURIA", "loja_furia")]
    ])

def back_menu(callback="menu_principal"):
    return build_menu([[("🏠 Voltar ao Menu", callback)]])

def elenco_menu():
    return build_menu([
        [("🧔 Elenco Masculino", "elenco_masc")],
        [("👩 Elenco Feminino", "elenco_fem")],
        [("🏠 Voltar ao Menu", "menu_principal")]
    ])
