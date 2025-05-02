# 🦁 FURIA Fan Bot

Um bot do Telegram para fãs da FURIA e-sports! Receba informações sobre jogos, elenco, notícias e acesse diretamente a loja oficial da FURIA — tudo com comandos interativos.

---

## 📦 Funcionalidades

- 🔥 Ver **próximas partidas** e **últimos resultados**
- 🎮 Consultar **elenco atual** (masculino ou feminino)
- 📰 Ver as **últimas 5 notícias** da FURIA no portal draft5.gg
- 📡 Acompanhar **partidas ao vivo**
- 🛍 Acessar a **loja oficial** da FURIA com um clique

---

## 🚀 Como instalar e executar o bot

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/furia-fan-chat.git
cd furia-fan-chat
```

### 2. Crie e ative um ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate         # Linux/macOS
venv\Scripts\activate            # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Crie o arquivo `.env`

Na raiz do projeto (onde está `bot.py`), crie um arquivo chamado `.env` com o seguinte conteúdo:

```env
TELEGRAM_TOKEN=seu_token_do_bot_telegram
PANDASCORE_TOKEN=seu_token_do_pandascore
```

> 🔐 **Atenção:** nunca compartilhe seus tokens publicamente.

---

## ▶️ Executando o bot

Com tudo configurado, basta rodar:

```bash
python bot.py
```

Você verá no terminal:

```
Bot da FURIA está online! 🔥
```

Abra seu bot no Telegram e envie `/start` para ver o menu interativo.

---

## 📁 Estrutura de pastas

```
furia-fan-chat/
├── bot.py               # Arquivo principal que inicia o bot
├── .env                 # Tokens de API
├── config.py            # Variáveis globais
├── utils.py             # Funções auxiliares
├── menus.py             # Geração dos menus inline
├── requirements.txt     # Dependências do projeto
├── handlers/            # Todos os comandos e callbacks
│   ├── __init__.py
│   ├── start.py
│   ├── jogos.py
│   ├── elenco.py
│   ├── noticias.py
│   ├── aovivo.py
```

---

## 💡 Exemplos de uso no Telegram

- `/start` — Mostra o menu inicial
- Toque em "Últimos Jogos" — Ver resultados recentes
- Toque em "Notícias" — Últimas do site draft5.gg relacionadas à FURIA
- Toque em "Loja da FURIA" — Link direto para [furia.gg](https://www.furia.gg/)

---


## 📜 Licença

Distribuído sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

Este bot pode ser livremente copiado, modificado e utilizado por qualquer pessoa conforme os termos da licença MIT.

> **Aviso de direitos autorais:** todo o conteúdo mencionado ou referenciado sobre a FURIA (nomes, marcas, logotipos e notícias) é propriedade intelectual da organização FURIA e de seus respectivos detentores. Este projeto é uma ferramenta de fã, sem afiliação oficial, e não detém qualquer direito sobre o conteúdo citado. 

> Este bot foi desenvolvido como parte de um **desafio técnico**, com fins educacionais e demonstrativos. Seu código-fonte está disponível sob a Licença MIT e pode ser livremente reutilizado ou adaptado por outras pessoas.
