from telegram import Update
from telegram.ext import ContextTypes
from bot.core.logger import get_logger
from bot.services.OpenAI.responder import ResponderService
from bot.core.config import APP_NAME, CHAT_IDS_AUTORIZADOS, ADMIN_USER_IDS, BOT_USERNAME

logger = get_logger(APP_NAME)
responder_service = ResponderService()

BOT_USERNAME_LOWER = BOT_USERNAME.lower()

async def manejar_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    if not mensaje or not mensaje.sticker:
        return
    
    chat_id = mensaje.chat.id
    user_id = mensaje.from_user.id if mensaje.from_user else None
    username = mensaje.from_user.username if mensaje.from_user else "Unknown"
    
    logger.info(f"Sticker recibido - Chat ID: {chat_id}, User ID: {user_id}, Username: @{username}")
    
    # Verificar si el chat está autorizado
    if chat_id not in CHAT_IDS_AUTORIZADOS:
        return
    
    # Verificar permisos de admin en grupos
    if mensaje.chat.type in ['group', 'supergroup']:
        is_admin = False
        
        if hasattr(mensaje.chat, 'all_members_are_administrators') and mensaje.chat.all_members_are_administrators:
            is_admin = True
        elif user_id in ADMIN_USER_IDS:
            is_admin = True
        else:
            try:
                member = await context.bot.get_chat_member(chat_id, user_id)
                if member.status in ['administrator', 'creator']:
                    is_admin = True
            except Exception:
                pass
        
        if not is_admin:
            return
    
    # Solo responder si es reply al bot
    citado = mensaje.reply_to_message
    es_reply_bot = (
        citado and citado.from_user and citado.from_user.username and citado.from_user.username.lower() == BOT_USERNAME_LOWER
    )
    
    if not es_reply_bot:
        return  # Solo responder a stickers que son reply al bot
    
    # Responder al sticker con OpenAI
    sticker_emoji = mensaje.sticker.emoji or "🤔"
    contexto = f"El usuario envió un sticker con emoji: {sticker_emoji}"
    
    logger.info(f"Procesando sticker para usuario {user_id} en chat {chat_id}")
    respuesta = responder_service.responder(contexto, [], user_id, chat_id)
    try:
        await mensaje.reply_text(respuesta)
    except Exception as e:
        logger.warning(f"No se pudo responder al sticker: {e}")
        await context.bot.send_message(chat_id=chat_id, text=respuesta)