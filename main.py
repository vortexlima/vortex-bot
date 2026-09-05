import os
import logging
import asyncio
from flask import Flask
from threading import Thread
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
CTRADER_ACCOUNT = "9732891"
CTRADER_SERVER = "cTrader demo"

# Estado atual do Robô
bot_state = {
    "ativo": "XAUUSD",
    "lote": 0.10,
    "status_robo": "Ligado",
    "estrategia": "Rompimento S&R + EMA 9/21"
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        msg_lower = user_message.lower()

        # Resposta inteligente simulando a IA com os comandos do robô
        if "eurusd" in msg_lower:
            bot_state["ativo"] = "EURUSD"
            reply_text = "⚙️ [Sistema Vortex]: Par alterado com sucesso para **EURUSD**. Pronto para operar!"
        elif "xauusd" in msg_lower or "ouro" in msg_lower:
            bot_state["ativo"] = "XAUUSD"
            reply_text = "⚙️ [Sistema Vortex]: Par alterado com sucesso para **XAUUSD (Ouro)**."
        elif "pausar" in msg_lower or "desligar" in msg_lower:
            bot_state["status_robo"] = "Pausado"
            reply_text = "⚙️ [Sistema Vortex]: Robô pausado com sucesso. Nenhuma nova ordem será aberta."
        elif "ligar" in msg_lower or "ativar" in msg_lower:
            bot_state["status_robo"] = "Ligado"
            reply_text = "⚙️ [Sistema Vortex]: Robô ativado e operando na estratégia S&R + EMA!"
        elif "status" in msg_lower or "conta" in msg_lower:
            reply_text = f"📊 **Status do Vortex Bot**\n- Conta: {CTRADER_ACCOUNT} ({CTRADER_SERVER})\n- Ativo: {bot_state['ativo']}\n- Lote: {bot_state['lote']}\n- Status: {bot_state['status_robo']}\n- Estratégia: {bot_state['estrategia']}"
        else:
            reply_text = f"🤖 Olá Edward! Recebi sua mensagem: *\"{user_message}\"*\n\nEstou rodando 24/7 na nuvem gerenciando sua conta cTrader ({CTRADER_ACCOUNT}). Como posso ajudar nas operações de Forex hoje?"

        await context.bot.send_message(chat_id=chat_id, text=reply_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Erro: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Erro ao processar comando.")

async def main_async():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    print("Bot Vortex AI iniciado com sucesso!")
    while True:
        await asyncio.sleep(3600)

def main():
    keep_alive()
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
