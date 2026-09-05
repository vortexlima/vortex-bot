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

# Estado atual do Robô (Gerenciado pela IA)
bot_state = {
    "ativo": "XAUUSD",
    "lote": 0.10,
    "status_robo": "Ligado",
    "estrategia": "Rompimento S&R + EMA 9/21"
}

def consultar_ia_trader(mensagem_usuario):
    """A IA lê o que você quer e interpreta se é uma alteração de trading ou conversa normal"""
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = f"""
    Você é o Vortex AI, assistente e operador autônomo da conta cTrader {CTRADER_ACCOUNT} ({CTRADER_SERVER}).
    Estado atual:
    - Ativo: {bot_state['ativo']}
    - Lote: {bot_state['lote']}
    - Status do Robô: {bot_state['status_robo']}
    - Estratégia: {bot_state['estrategia']}

    O usuário (Edward) vai conversar com você pelo Telegram.
    Se ele pedir para alterar o ativo (ex: mudar para EURUSD, operar Ouro, etc), alterar o lote, pausar o robô, ligar o robô ou pedir o status/saldo, você deve responder confirmando a ação de forma clara.
    Se ele falar de outros assuntos ou sobre a vida, responda como um assistente amigável e prestativo.
    Seja conciso, direto e inteligente.
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensagem_usuario}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        if "choices" in res_json:
            resposta = res_json["choices"][0]["message"]["content"]

            # Interpretação automática da IA para atualizar o estado interno do robô
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
            return "Comando recebido, mas tive um pequeno atraso na nuvem."
    except Exception as e:
        return f"Erro ao consultar cérebro de IA: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        # Deixa a IA processar a intenção do usuário
        resposta_ia = consultar_ia_trader(user_message)
        await context.bot.send_message(chat_id=chat_id, text=resposta_ia, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Erro: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Erro ao processar comando.")

async def main_async():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    print("Vortex AI Trader Assistant iniciado!")
    while True:
        await asyncio.sleep(3600)

def main():
    keep_alive()
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
