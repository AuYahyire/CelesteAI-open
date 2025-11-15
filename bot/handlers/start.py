from telegram import Update
from telegram.ext import ContextTypes
from bot.core.logger import get_logger
from bot.core.config import APP_NAME

logger = get_logger(APP_NAME)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Comando /start recibido de usuario {update.effective_user.id}")
    await update.message.reply_text("¡Hola! ¡Bot funcionando!")
    logger.info("Respuesta /start enviada")