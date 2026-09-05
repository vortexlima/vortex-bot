import os
import logging
import asyncio
from flask import Flask
from threading import Thread
import google.generativeai as genai
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

# Credenciais fornecidas
TELEGRAM_TOKEN = "8032829185:AAGPYud3lah87vnp4EmEW36pe6t8ebpOEsg"
GEMINI_API_KEY = "AQ.Ab8RN6IWZKgpqVIPx0WapAAtkUACqCtKwK4xoe84M6w9l5fnHA"
CTRADER_ACCOUNT = "9732891"
CTRADER_SERVER = "cTrader demo"

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Estado atual do Robô
bot_state = {
    "ativo": "XAUUSD",
    "lote": 0.10,
    "status_robo": "Ligado",
    "estrategia": "Rompimento S&R + EMA 9/21"
}

SYSTEM_PROMPT = f"""
Você é o Vortex AI Bot, assistente inteligente de trading forex e ciber-amigo do Edward.
Conta cTrader: {CTRADER_ACCOUNT} ({CTRADER_SERVER})
- Ativo: {bot_state['ativo']}
- Lote: {bot_state['lote']}
- Status: {bot_state['status_robo']}
"""

chat_session = model.start_chat(history=[])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        prompt_completo = f"{SYSTEM_PROMPT}\n\nMensagem do usuário: {user_message}"
        response = chat_session.send_message(prompt_completo)
        reply_text = response.text

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

def main():
    keep_alive()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot Vortex AI iniciado!")
    application.run_polling()

if __name__ == '__main__':
    main()
