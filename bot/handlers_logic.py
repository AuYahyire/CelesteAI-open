import base64
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from bot.core.logger import get_logger
from bot.services.OpenAI import responder
from bot.core.config import APP_NAME, CHAT_IDS_AUTORIZADOS, ADMIN_USER_IDS, BOT_USERNAME
import io
from PIL import Image
import random

logger = get_logger(APP_NAME)

# Cliente HTTP reutilizable para reducir consumo de memoria
_http_client = None

def get_http_client():
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient()
    return _http_client

BOT_USERNAME_MENCION = f"@{BOT_USERNAME}"
BOT_USERNAME_LOWER = BOT_USERNAME.lower()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Comando /start recibido de usuario {update.effective_user.id}")
    await update.message.reply_text("¡Hola! ¡Bot funcionando!")
    logger.info("Respuesta /start enviada")

async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Handler manejar_mensaje ejecutado: {update}")
    mensaje = update.message
    if not mensaje:
        logger.info("Mensaje sin contenido, se ignora.")
        return

    chat_id = mensaje.chat.id
    user_id = mensaje.from_user.id if mensaje.from_user else None
    username = mensaje.from_user.username if mensaje.from_user else "Unknown"
    
    logger.info(f"Mensaje recibido - Chat ID: {chat_id}, User ID: {user_id}, Username: @{username}, Texto: {mensaje.text}")

    # Verificar si el chat está autorizado
    if chat_id not in CHAT_IDS_AUTORIZADOS:
        await mensaje.reply_text("Este chat no está autorizado para usar este bot.")
        logger.info(f"Chat no autorizado: {chat_id}, autorizados: {CHAT_IDS_AUTORIZADOS}")
        return
    
    # Si es un grupo, verificar que el usuario sea admin
    if mensaje.chat.type in ['group', 'supergroup']:
        is_admin = False
        
        # Verificar si todos los miembros son administradores
        if hasattr(mensaje.chat, 'all_members_are_administrators') and mensaje.chat.all_members_are_administrators:
            is_admin = True
            logger.info(f"Usuario {user_id} (@{username}) es admin (todos son admins en el grupo)")
        # Verificar lista manual de admins
        elif user_id in ADMIN_USER_IDS:
            is_admin = True
            logger.info(f"Usuario {user_id} (@{username}) es admin (en lista manual)")
        # Verificar con API de Telegram
        else:
            try:
                member = await context.bot.get_chat_member(chat_id, user_id)
                if member.status in ['administrator', 'creator']:
                    is_admin = True
                    logger.info(f"Usuario {user_id} (@{username}) es admin (verificado con API)")
            except Exception as e:
                logger.error(f"Error verificando admin status: {e}")
        
        if not is_admin:
            logger.info(f"Usuario {user_id} (@{username}) no es admin en grupo {chat_id}")
            return  # Ignorar silenciosamente mensajes de no-admins en grupos

    texto = mensaje.text or ""
    citado = mensaje.reply_to_message
    imagenes = await extraer_imagenes_base64(mensaje, context) + (await extraer_imagenes_base64(mensaje.reply_to_message, context) if mensaje.reply_to_message else [])

    es_mencion = BOT_USERNAME_MENCION.lower() in texto.lower()
    es_reply_bot = (
        citado and citado.from_user and citado.from_user.username and citado.from_user.username.lower() == BOT_USERNAME_LOWER
    )

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
        
        logger.info(f"Procesando respuesta para usuario {user_id} en chat {chat_id}")
        logger.debug(f"Texto completo enviado a IA: {texto_completo}")
        respuesta = responder(texto_completo, imagenes, user_id, chat_id)
        try:
            await mensaje.reply_text(respuesta)
        except Exception as e:
            logger.warning(f"No se pudo responder al mensaje: {e}")
            await context.bot.send_message(chat_id=chat_id, text=respuesta)
    else:
        # Reaccionar ocasionalmente a mensajes normales (sin mención)
        await reaccionar_ocasionalmente(mensaje, texto)

async def file_id_to_resized_base64(file_path: str, size=(512, 512)) -> str:
    # Reutilizar cliente HTTP para reducir overhead de conexiones
    client = get_http_client()
    resp = await client.get(file_path)
    resp.raise_for_status()
    img_bytes = io.BytesIO(resp.content)

    try:
        # Redimensionar con PIL
        with Image.open(img_bytes) as img:
            img = img.convert('RGB')
            img = img.resize(size, Image.LANCZOS)
            out_bytes = io.BytesIO()
            img.save(out_bytes, format="JPEG")
            out_bytes.seek(0)
            b64 = base64.b64encode(out_bytes.read()).decode('utf-8')
            return b64
    except Exception:
        # Si no se puede procesar como imagen, devolver None
        return None

async def extraer_imagenes_base64(mensaje, contexto, size=(512,512)):
    base64_imgs = []
    if not mensaje:
        return base64_imgs

    # Procesar fotos
    if mensaje.photo:
        try:
            file = await contexto.bot.get_file(mensaje.photo[-1].file_id)
            base64_str = await file_id_to_resized_base64(file.file_path, size)
            if base64_str:
                base64_imgs.append(base64_str)
        except Exception as e:
            logger.info(f"Error al extraer imagen: {e}")
    
    # Procesar stickers (solo si se pueden convertir)
    if mensaje.sticker:
        try:
            file = await contexto.bot.get_file(mensaje.sticker.file_id)
            base64_str = await file_id_to_resized_base64(file.file_path, size)
            if base64_str:
                base64_imgs.append(base64_str)
        except Exception:
            # Si no se puede convertir el sticker, se ignora silenciosamente
            pass

    return base64_imgs

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
    respuesta = responder(contexto, [], user_id, chat_id)
    try:
        await mensaje.reply_text(respuesta)
    except Exception as e:
        logger.warning(f"No se pudo responder al sticker: {e}")
        await context.bot.send_message(chat_id=chat_id, text=respuesta)

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