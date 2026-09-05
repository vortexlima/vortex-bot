import os
import logging
import asyncio
from flask import Flask
from threading import Thread
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Configurar Flask para manter o Render acordado
app = Flask('')

@app.route('/')
def home():
    return "Vortex AI Bot está rodando 24/7 na nuvem!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# Configuração de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Credenciais
TELEGRAM_TOKEN = "8032829185:AAGPYud3lah87vnp4EmEW36pe6t8ebpOEsg"
GEMINI_API_KEY = "AQ.Ab8RN6IWZKgpqVIPx0WapAAtkUACqCtKwK4xoe84M6w9l5fnHA"
CTRADER_ACCOUNT = "9732891"
CTRADER_SERVER = "cTrader demo"

# Estado atual do Robô
bot_state = {
    "ativo": "XAUUSD",
    "lote": 0.10,
    "status_robo": "Ligado",
    "estrategia": "Rompimento S&R + EMA 9/21"
}

def consultar_gemini(mensagem_usuario):
    """Consulta direta via requisição HTTP POST para evitar erros do SDK do Google Cloud"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {'Content-Type': 'application/json'}

    prompt = f"""
    Você é o Vortex AI Bot, assistente inteligente de trading forex e ciber-amigo do Edward.
    Conta cTrader: {CTRADER_ACCOUNT} ({CTRADER_SERVER})
    - Ativo: {bot_state['ativo']}
    - Lote: {bot_state['lote']}
    - Status: {bot_state['status_robo']}

    Responda à mensagem do usuário de forma natural, prestativa e inteligente:
    {mensagem_usuario}
    """

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        if "candidates" in res_json:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Erro na resposta da IA: {res_json.get('error', 'Desconhecido')}"
    except Exception as e:
        return f"Erro de conexão com a IA: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        # Consultar Gemini via API direta
        reply_text = consultar_gemini(user_message)

        msg_lower = user_message.lower()
        if "eurusd" in msg_lower:
            bot_state["ativo"] = "EURUSD"
            reply_text += "\n\n⚙️ [Sistema]: Par alterado para EURUSD."
        elif "xauusd" in msg_lower or "ouro" in msg_lower:
            bot_state["ativo"] = "XAUUSD"
            reply_text += "\n\n⚙️ [Sistema]: Par alterado para XAUUSD."
        elif "pausar" in msg_lower:
            bot_state["status_robo"] = "Pausado"
            reply_text += "\n\n⚙️ [Sistema]: Robô pausado."
        elif "ligar" in msg_lower:
            bot_state["status_robo"] = "Ligado"
            reply_text += "\n\n⚙️ [Sistema]: Robô ativado!"

        await context.bot.send_message(chat_id=chat_id, text=reply_text)
    except Exception as e:
        logging.error(f"Erro: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Erro ao processar mensagem.")

async def main_async():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print("Bot Vortex AI iniciado com sucesso!")
    while True:
        await asyncio.sleep(3600)

def main():
    keep_alive()
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
