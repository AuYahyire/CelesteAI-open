from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from bot.core.config import APP_NAME
from bot.core.logger import get_logger
from bot.db.models import init_conversations_table, init_db
from bot.core.telegram_bot import bot_instance, init_bot, configurar_webhook
from bot.routes.recordatorios import enviar_recordatorios_cada_minuto
from bot.routes import webhook

logger = get_logger(APP_NAME)

@asynccontextmanager
async def lifespan(app):
    logger.info(f"Iniciando aplicación {APP_NAME}")
    
    init_db()
    init_conversations_table()
    init_bot()
    await configurar_webhook()
    await bot_instance.initialize()
    await bot_instance.start()
    
    task_recordatorios = asyncio.create_task(enviar_recordatorios_cada_minuto())
    
    yield
    
    task_recordatorios.cancel()
    try:
        await task_recordatorios
    except asyncio.CancelledError:
        pass
    
    logger.info(f"[lifespan] Apagando aplicación {APP_NAME}")
    await bot_instance.stop()

def create_app():
    app = FastAPI(lifespan=lifespan)

    @app.get("/")
    async def health_check():
        return {"status": "ok", "app": APP_NAME}

    @app.middleware("http")
    async def log_requests(request, call_next):
        logger.info(f"[log_requests] → {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"[log_requests] ← {request.method} {request.url} - Status: {response.status_code}")
        return response

    app.include_router(webhook.router)
    return app
