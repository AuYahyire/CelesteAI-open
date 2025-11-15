# auth.py
from functools import wraps
from typing import Set
from telegram import Update
from telegram.ext import ContextTypes
from bot.core.logger import get_logger
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

logger = get_logger(__name__)

from bot.core.config import CHAT_IDS_AUTORIZADOS, ADMIN_USER_IDS, ANGLOPARLANTE_USER_IDS

ROLES = {
    "admin": ADMIN_USER_IDS,  # IDs de usuarios con rol de superusuario (admin completo)
    "angloparlante": ANGLOPARLANTE_USER_IDS,  # IDs de usuarios con rol angloparlante
}

def get_roles(user_id: int) -> Set[str]:
    return {role for role, ids in ROLES.items() if user_id in ids}

def rol_requerido(*roles_requeridos):
    roles_requeridos = set(roles_requeridos)
    chats_autorizados = set(CHAT_IDS_AUTORIZADOS) if CHAT_IDS_AUTORIZADOS is not None else None

    def decorator(handler):
        @wraps(handler)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            chat = update.effective_chat

            # 1) Validar chat
            if chats_autorizados is not None:
                if chat is None or chat.id not in chats_autorizados:
                    if update.effective_message:
                        logger.info(f"[rol_requerido] Chat {chat.id if chat else 'None'} no está autorizado.")
                        await update.effective_message.reply_text(
                            "Este bot no está habilitado en este chat."
                        )
                    return

            if user is None:
                logger.warning(f"[rol_requerido] Update {update.update_id} sin usuario asociado.")
                return

            user_roles = get_roles(user.id)
            if "admin" in user_roles or user_roles & roles_requeridos:
                logger.info(f"[rol_requerido] Usuario {user.id} tiene permiso para ejecutar el comando.")
                return await handler(update, context)

            # 2) Permitir a administradores del chat
            if chat and chat.type in ("group", "supergroup"):
                try:
                    member = await context.bot.get_chat_member(chat.id, user.id)
                except TelegramError as exc:
                    logger.warning(f"[rol_requerido] No se pudo obtener miembro {user.id} del chat {chat.id}: {exc}")
                else:
                    if member.status in ("administrator", "creator"):
                        logger.info(f"[rol_requerido] Usuario {user.id} es administrador del chat {chat.id}.")
                        return await handler(update, context)

            if update.effective_message:
                logger.info(f"[rol_requerido] Usuario {user.id} sin permiso para ejecutar el comando.")
                

        return wrapper
    return decorator