from telegram import Update
from telegram.ext import ContextTypes
from bot.core.config import BOT_USERNAME

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
🤖 *CelesteAI - Bot de Telegram*

*Comandos disponibles:*
• `/help` - Muestra este mensaje de ayuda
• `/start` - Inicia el bot
• `/translate` - Traduce texto o imágenes
• `/traducir` - Traduce texto o imágenes

*Cómo usar el bot:*
• Menciona al bot: `@{BOT_USERNAME} tu mensaje`
• Responde a un mensaje del bot
• Envía imágenes junto con texto
• Cita mensajes para incluir contexto

*Funciones:*
✨ Respuestas inteligentes con IA
🖼️ Análisis de imágenes
💬 Procesamiento de mensajes citados
🎯 Reacciones automáticas ocasionales

¡Simplemente menciona al bot o responde a sus mensajes para comenzar!
NOTA: Necesitas tener permisos para usar el bot o ciertos comandos.

ENGLISH:

🤖 *CelesteAI - Telegram Bot*

*Available commands:*
• `/help` - Shows this help message
• `/start` - Starts the bot
• `/translate` - Translates text or images
• `/traducir` - Translates text or images

*How to use the bot:*
• Mention the bot: `@{BOT_USERNAME} your message`
• Reply to a bot message
• Send images with text
• Quote messages to include context

*Features:*
✨ Smart AI responses
🖼️ Image analysis
💬 Quoted message processing
🎯 Occasional automatic reactions

Simply mention the bot or reply to its messages to get started!
NOTE: You need to have permissions to use the bot or certain commands.
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')