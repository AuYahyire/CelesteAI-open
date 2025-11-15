from telegram import Update
from telegram.ext import ContextTypes
from bot.core.logger import get_logger
from bot.services.OpenAI.responder import ResponderService
from bot.utils.image_utils import extraer_imagenes_base64

logger = get_logger("manejar_traduccion")
responder_service = ResponderService()

async def manejar_traduccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message
    if not mensaje:
        return

    chat_id = mensaje.chat.id
    user_id = mensaje.from_user.id if mensaje.from_user else None
    texto = mensaje.text or ""
    citado = mensaje.reply_to_message
    imagenes = await extraer_imagenes_base64(mensaje, context) + (await extraer_imagenes_base64(mensaje.reply_to_message, context) if mensaje.reply_to_message else [])
    
    texto_completo = texto.strip()
    
    if citado:
        if citado.text:
            texto_completo += f"\n\nMensaje citado: {citado.text}"
        elif citado.sticker:
            sticker_convertido = False
            try:
                from bot.utils.image_utils import file_id_to_resized_base64
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

    respuesta = responder_service.responder(texto_completo, imagenes, user_id, chat_id, instructions="traducir.txt", temperature=0.3)
    
    try:
        await mensaje.reply_text(respuesta)
    except Exception as e:
        logger.warning(f"No se pudo responder al mensaje: {e}")
        await context.bot.send_message(chat_id=chat_id, text=respuesta)