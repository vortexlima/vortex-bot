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
# Usando a chave que você gerou no Google Cloud / Agent Platform
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

def perguntar_gemini(mensagem_usuario):
    """Envia a mensagem para a IA do Google usando o endpoint correto do Agent Platform"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }

    prompt_sistema = f"""
    Você é o Vortex AI Bot, assistente inteligente de trading forex e ciber-amigo do Edward.
    Conta cTrader: {CTRADER_ACCOUNT} ({CTRADER_SERVER})
    - Ativo atual: {bot_state['ativo']}
    - Lote: {bot_state['lote']}
    - Status: {bot_state['status_robo']}
    - Estratégia: {bot_state['estrategia']}

    Responda ao usuário com inteligência, podendo conversar sobre a vida ou ajudar nas operações de forex.
    """

    data = {
        "contents": [{
            "parts": [{"text": f"{prompt_sistema}\n\nUsuário: {mensagem_usuario}"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        if "candidates" in res_json:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # Fallback se a chave GCP precisar do formato de chave de API normal
            url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            resp_fb = requests.post(url_fallback, json=data)
            json_fb = resp_fb.json()
            if "candidates" in json_fb:
                return json_fb["candidates"][0]["content"]["parts"][0]["text"]
            return f"IA indisponível no momento: {str(res_json.get('error', 'Erro desconhecido'))}"
    except Exception as e:
        return f"Erro de conexão com a IA: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        msg_lower = user_message.lower()

        # Comandos de atalho para atualizar o estado interno do robô
        if "eurusd" in msg_lower:
            bot_state["ativo"] = "EURUSD"
        elif "xauusd" in msg_lower or "ouro" in msg_lower:
            bot_state["ativo"] = "XAUUSD"
        elif "pausar" in msg_lower or "desligar" in msg_lower:
            bot_state["status_robo"] = "Pausado"
        elif "ligar" in msg_lower or "ativar" in msg_lower:
            bot_state["status_robo"] = "Ligado"

        # Consulta a IA real
        resposta_ia = perguntar_gemini(user_message)

        await context.bot.send_message(chat_id=chat_id, text=resposta_ia, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Erro: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Erro ao processar mensagem.")

async def main_async():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    print("Bot Vortex AI com IA ativada com sucesso!")
    while True:
        await asyncio.sleep(3600)

def main():
    keep_alive()
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
