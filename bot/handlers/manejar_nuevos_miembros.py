from telegram import Update
from telegram.ext import ContextTypes
from bot.core.logger import get_logger
from bot.core.config import APP_NAME, CHAT_IDS_AUTORIZADOS

logger = get_logger(APP_NAME)

async def manejar_nuevos_miembros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    if not mensaje or not mensaje.new_chat_members:
        return
    
    chat_id = mensaje.chat.id
    logger.info(f"Nuevos miembros en chat {chat_id}: {len(mensaje.new_chat_members)}")
    
    # Verificar si el chat está autorizado
    if chat_id not in CHAT_IDS_AUTORIZADOS:
        return
    
    # Crear mensaje de bienvenida
    nuevos_usuarios = []
    for usuario in mensaje.new_chat_members:
        if not usuario.is_bot:  # No dar bienvenida a bots
            nombre = usuario.first_name
            if usuario.username:
                nombre += f" (@{usuario.username})"
            nuevos_usuarios.append(nombre)
    
    if nuevos_usuarios:
        if len(nuevos_usuarios) == 1:
            bienvenida = f"¡Bienvenido/a {nuevos_usuarios[0]} al grupo! 👋"
        else:
            usuarios_str = ", ".join(nuevos_usuarios)
            bienvenida = f"¡Bienvenidos {usuarios_str} al grupo! 👋"
        
        try:
            await mensaje.reply_text(bienvenida)
        except Exception as e:
            logger.warning(f"No se pudo enviar bienvenida como reply: {e}")
            await context.bot.send_message(chat_id=chat_id, text=bienvenida)