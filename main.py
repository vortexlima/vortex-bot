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
GROQ_API_KEY = "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"
CTRADER_ACCOUNT = "9732891"
CTRADER_SERVER = "cTrader demo"

# Estado atual do Robô
bot_state = {
    "ativo": "XAUUSD",
    "lote": 0.10,
    "status_robo": "Ligado",
    "estrategia": "Rompimento S&R + EMA 9/21"
}

def perguntar_ia(mensagem_usuario):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt_sistema = f"""
    Você é o Vortex AI, assistente e operador autônomo da conta cTrader {CTRADER_ACCOUNT} ({CTRADER_SERVER}).
    Estado atual:
    - Ativo: {bot_state['ativo']}
    - Lote: {bot_state['lote']}
    - Status do Robô: {bot_state['status_robo']}
    - Estratégia: {bot_state['estrategia']}

    O usuário (Edward) está conversando com você no Telegram. Responda de forma direta, inteligente e amigável.
    """

    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensagem_usuario}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        res_json = response.json()
        if "choices" in res_json:
            resposta = res_json["choices"][0]["message"]["content"]

            # Atualiza estado se necessário via chat
            msg_lower = mensagem_usuario.lower()
            if "eurusd" in msg_lower:
                bot_state["ativo"] = "EURUSD"
            elif "xauusd" in msg_lower or "ouro" in msg_lower:
                bot_state["ativo"] = "XAUUSD"
            elif "pausar" in msg_lower or "desligar" in msg_lower:
                bot_state["status_robo"] = "Pausado"
            elif "ligar" in msg_lower or "ativar" in msg_lower:
                bot_state["status_robo"] = "Ligado"

            return resposta
        else:
            return f"Erro retornado pela Groq: {str(res_json)}"
    except Exception as e:
        return f"Exceção na requisição Groq: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        resposta_ia = perguntar_ia(user_message)
        await context.bot.send_message(chat_id=chat_id, text=resposta_ia)
    except Exception as e:
        logging.error(f"Erro no handler: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"Erro interno: {str(e)}")

async def main_async():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    print("Bot Vortex AI conectado com sucesso!")
    while True:
        await asyncio.sleep(3600)

def main():
    keep_alive()
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
