from telegram.ext import CommandHandler, MessageHandler, filters
from bot.handlers.start import start
from bot.handlers.help import help
from bot.handlers.manejar_mensaje import manejar_mensaje
from bot.handlers.manejar_sticker import manejar_sticker
from bot.handlers.manejar_nuevos_miembros import manejar_nuevos_miembros
from bot.handlers.manejar_traduccion import manejar_traduccion
from bot.handlers.auth import rol_requerido

def init_handlers(app):
    ##########
    #Comandos#
    ##########
    
    # Comando start con rol admin requerido, este comaando es de testing.
    app.add_handler(CommandHandler("start", rol_requerido("admin")(start)))

    #Comando help sin restricción de roles
    app.add_handler(CommandHandler("help", help))

    #Comandos de traducción
    app.add_handler(CommandHandler("translate", rol_requerido("admin", "angloparlante")(manejar_traduccion))) 
    app.add_handler(CommandHandler("traducir", rol_requerido("admin", "angloparlante")(manejar_traduccion)))


    #################
    #Manejo mensajes#
    #################

    # Stickers: solo usuarios con rol admin
    app.add_handler(MessageHandler(filters.Sticker.ALL, rol_requerido("admin")(manejar_sticker)))

    # Nuevos miembros, mensaje automático de bienvenida, sin restricción de roles
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, manejar_nuevos_miembros))

    #TODO: audios, videos, documentos, etc.

    #Default
    # Mensajes generales (texto libre, imagenes): por ahora, solo admin
    app.add_handler(MessageHandler(filters.ALL, rol_requerido("admin")(manejar_mensaje)))
