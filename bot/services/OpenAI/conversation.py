from datetime import datetime, timezone, timedelta
from bot.db.models import obtener_conversacion, guardar_conversacion, limpiar_conversacion

class ConversationStateManager:
    def __init__(self, ttl=timedelta(hours=1)):
        self.ttl = ttl

    def get_state(self, user_id):
        response_id, created_at = obtener_conversacion(user_id)
        if not response_id or not created_at:
            return None, None

        creation_time = datetime.fromtimestamp(created_at, tz=timezone.utc)
        if datetime.now(timezone.utc) - creation_time > self.ttl:
            limpiar_conversacion(user_id)
            return None, None
        return response_id, created_at

    def save_state(self, user_id, response_id, created_at):
        guardar_conversacion(user_id, response_id, created_at)