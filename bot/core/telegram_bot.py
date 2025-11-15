from telegram.ext import ApplicationBuilder
import httpx
from bot.core.config import BOT_TOKEN, RAILWAY_DOMAIN
from bot.handlers.handlers import init_handlers
from bot.core.logger import get_logger

logger = get_logger("telegram_bot")

bot_instance = ApplicationBuilder().token(BOT_TOKEN).build()

def init_bot():
    init_handlers(bot_instance)

async def configurar_webhook():
    if not BOT_TOKEN or not RAILWAY_DOMAIN:
        logger.error("[configurar_webhook] Faltan BOT_TOKEN o RAILWAY_DOMAIN para configurar webhook")
        return

    url_webhook = f"https://{RAILWAY_DOMAIN}/webhook"
    async with httpx.AsyncClient() as client:
        response = await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", data={"url": url_webhook})

    if response.status_code == 200:
        logger.info(f"[configurar_webhook] Webhook configurado: {url_webhook}")
    else:
        logger.error(f"[configurar_webhook] Error configurando webhook: {response.status_code} - {response.text}")