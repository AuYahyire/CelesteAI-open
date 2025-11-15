from fastapi import APIRouter, Request
from telegram import Update
from bot.core.telegram_bot import bot_instance
from bot.core.logger import get_logger
from bot.core.config import APP_NAME

router = APIRouter()
logger = get_logger(APP_NAME)

@router.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        logger.info(f"Webhook recibido.")
        
        data = await request.json()
        update = Update.de_json(data, bot_instance.bot)
        logger.info(f"Update procesado: {update}")
        
        await bot_instance.process_update(update)
        logger.info("Update enviado al bot exitosamente")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error en webhook: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}