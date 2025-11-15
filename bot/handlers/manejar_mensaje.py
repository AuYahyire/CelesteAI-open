from telegram import Update
from telegram.ext import ContextTypes
from bot.core.logger import get_logger
from bot.services.OpenAI.responder import ResponderService
from bot.core.config import BOT_USERNAME
from bot.utils.image_utils import extraer_imagenes_base64, file_id_to_resized_base64
import random

logger = get_logger("manejar_mensaje")
responder_service = ResponderService()

BOT_USERNAME_MENCION = f"@{BOT_USERNAME}"
BOT_USERNAME_LOWER = BOT_USERNAME.lower()

async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[manejar_mensajes] Handler ejecutado: {update}")
    mensaje = update.message
    if not mensaje:
        logger.info("[manejar_mensajes] Mensaje sin contenido, se ignora.")
        return

    chat_id = mensaje.chat.id
    user_id = mensaje.from_user.id if mensaje.from_user else None
    username = mensaje.from_user.username if mensaje.from_user else "Unknown"
    texto = mensaje.text or ""
    citado = mensaje.reply_to_message
    imagenes = await extraer_imagenes_base64(mensaje, context) + (await extraer_imagenes_base64(mensaje.reply_to_message, context) if mensaje.reply_to_message else [])
    es_mencion = BOT_USERNAME_MENCION.lower() in texto.lower()
    es_reply_bot = (
        citado and citado.from_user.username and citado.from_user.username.lower() == BOT_USERNAME_LOWER
    )

    logger.info(f"[manejar_mensajes] Mensaje recibido - Chat ID: {chat_id}, User ID: {user_id}, Username: @{username}, Texto: {mensaje.text}")

    # Solo respondemos en mención o reply
    if es_mencion or es_reply_bot:
        texto_completo = texto.strip()
        
        # Si hay mensaje citado, incluir el contenido citado (tanto para mención como reply)
        if citado:
            if citado.text:
                texto_completo += f"\n\nMensaje citado: {citado.text}"
            elif citado.sticker:
                # Verificar si el sticker se pudo convertir a imagen
                sticker_convertido = False
                try:
                    file = await context.bot.get_file(citado.sticker.file_id)
                    base64_str = await file_id_to_resized_base64(file.file_path)
                    if base64_str:
                        sticker_convertido = True
                except Exception:
                    pass
                
                if sticker_convertido:
                    texto_completo += "\n\nSticker citado (incluido como imagen en el contexto)"
                else:
                    sticker_emoji = citado.sticker.emoji or "🤔"
                    texto_completo += f"\n\nSticker citado: {sticker_emoji}"
            elif citado.photo:
                texto_completo += "\n\nImagen citada (incluida en el contexto)"

        logger.info(f"[manejar_mensajes] Procesando respuesta para usuario {user_id} en chat {chat_id}")
        logger.debug(f"[manejar_mensajes] Texto completo enviado a IA: {texto_completo}")
        respuesta = responder_service.responder(texto_completo, imagenes, user_id, chat_id)
        try:
            await mensaje.reply_text(respuesta)
        except Exception as e:
            logger.warning(f"[manejar_mensajes] No se pudo responder al mensaje: {e}")
            await context.bot.send_message(chat_id=chat_id, text=respuesta)
    else:
        # Reaccionar ocasionalmente a mensajes normales (sin mención)
        await reaccionar_ocasionalmente(mensaje, texto)



async def reaccionar_ocasionalmente(mensaje, texto):
    """Reacciona ocasionalmente con emojis a mensajes que no son para el bot"""
    

    if random.random() > 0.05:
        return
    
    # Mapeo de palabras a emojis
    palabras_emojis = {
        'gracias': ['👍', '❤️', '🔥', '✨'],
        'genial': ['👍', '❤️', '🔥', '✨'],
        'excelente': ['👍', '❤️', '🔥', '✨'],
        'perfecto': ['👍', '❤️', '🔥', '✨'],
        'increíble': ['👍', '❤️', '🔥', '✨'],
        'buenísimo': ['👍', '❤️', '🔥', '✨'],
        'jaja': ['😂', '😄', '🤣'],
        'jeje': ['😂', '😄', '🤣'],
        'lol': ['😂', '😄', '🤣'],
        'xd': ['😂', '😄', '🤣'],
        'haha': ['😂', '😄', '🤣'],
        'feliz': ['😊', '😁', '🎉'],
        'contento': ['😊', '😁', '🎉'],
        'alegre': ['😊', '😁', '🎉'],
        'happy': ['😊', '😁', '🎉'],
        'triste': ['😢', '😔'],
        'mal': ['😢', '😔'],
        'horrible': ['😢', '😔'],
        'terrible': ['😢', '😔'],
        'enojado': ['😤', '😠'],
        'molesto': ['😤', '😠'],
        'furioso': ['😤', '😠'],
        'pizza': ['🍕', '🍔', '😋'],
        'hamburguesa': ['🍕', '🍔', '😋'],
        'comida': ['🍕', '🍔', '😋'],
        'comer': ['🍕', '🍔', '😋'],
        'café': ['☕'],
        'coffee': ['☕'],
        'trabajo': ['💪', '📚', '🎯'],
        'estudiar': ['💪', '📚', '🎯'],
        'examen': ['💪', '📚', '🎯'],
        'proyecto': ['💪', '📚', '🎯'],
        'cansado': ['😴', '💤'],
        'agotado': ['😴', '💤'],
        'sueño': ['😴', '💤'],
        'cumpleaños': ['🎂', '🎉', '🥳'],
        'felicidades': ['🎂', '🎉', '🥳'],
        'celebrar': ['🎂', '🎉', '🥳'],
        'código': ['💻', '🐛', '⚡'],
        'programar': ['💻', '🐛', '⚡'],
        'bug': ['💻', '🐛', '⚡'],
        'error': ['💻', '🐛', '⚡'],
        'amén': ['🙏', '✨', '❤️', '🕊️'],
        'amen': ['🙏', '✨', '❤️', '🕊️'],
        'gloria a dios': ['🙏', '✨', '❤️', '🕊️'],
        'dios te bendiga': ['🙏', '✨', '❤️', '🕊️'],
        'bendiciones': ['🙏', '✨', '❤️', '🕊️'],
        'oración': ['🙏', '✨', '🕊️'],
        'oracion': ['🙏', '✨', '🕊️'],
        'rezar': ['🙏', '✨', '🕊️'],
        'orar': ['🙏', '✨', '🕊️'],
        'fe': ['🙏', '✨', '🕊️', '❤️'],
        'esperanza': ['🙏', '✨', '🕊️', '❤️'],
        'milagro': ['🙏', '✨', '🕊️', '❤️'],
        'bendición': ['🙏', '✨', '🕊️', '❤️'],
        'bendicion': ['🙏', '✨', '🕊️', '❤️'],
        'iglesia': ['⛪', '🙏', '✨'],
        'congre': ['⛪', '🙏', '✨'],
        'congregación': ['⛪', '🙏', '✨'],
        'pastor': ['⛪', '🙏', '✨'],
        'aleluya': ['🙏', '✨', '🕊️'],
        'ok': ['👌', '✅'],
        'vale': ['👌', '✅'],
        'bien': ['👌', '✅'],
        'sí': ['👌', '✅'],
        'si': ['👌', '✅'],
        'no': ['❌', '🚫'],
        'nope': ['❌', '🚫'],
        'nah': ['❌', '🚫'],
        'wow': ['🤯', '😱', '🔥'],
        'amazing': ['🤯', '😱', '🔥'],
        'yeshua': ['🔥']
    }
    
    texto_lower = texto.lower()
    emoji_seleccionado = None
    
    # Buscar palabras clave
    for palabra, emojis in palabras_emojis.items():
        if palabra in texto_lower:
            emoji_seleccionado = random.choice(emojis)
            break
    
    # Si no hay palabra clave, reaccionar aleatoriamente (muy ocasional)
    if not emoji_seleccionado and random.random() < 0.05:
        emojis_generales = ['👀', '🤔', '👍']
        emoji_seleccionado = random.choice(emojis_generales)
    
    # Aplicar la reacción
    if emoji_seleccionado:
        try:
            await mensaje.set_reaction(emoji_seleccionado)
            logger.info(f"Reacción {emoji_seleccionado} aplicada al mensaje de {mensaje.from_user.username}")
        except Exception as e:
            logger.error(f"Error aplicando reacción: {e}")