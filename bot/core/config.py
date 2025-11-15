import os
import json

# Solo cargar .env en desarrollo local
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # En producción no necesitamos python-dotenv.

APP_NAME = os.getenv("APP_NAME")

BOT_TOKEN = os.getenv("TOKEN_TELEGRAM")
BOT_USERNAME = os.getenv("BOT_USERNAME")
RAILWAY_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN")
PORT = int(os.getenv("PORT", 8000))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_MODEL = os.getenv("OPENAI_BASE_MODEL")


# Múltiples chat IDs autorizados
def parse_ids(env_var):
    ids_str = os.getenv(env_var, "[]")
    try:
        return json.loads(ids_str)
    except json.JSONDecodeError:
        # Fallback para compatibilidad con formato anterior
        try:
            return [int(ids_str)]
        except ValueError:
            return []

CHAT_IDS_AUTORIZADOS = parse_ids("CHAT_IDS_AUTORIZADOS")
ADMIN_USER_IDS = parse_ids("ADMIN_USER_IDS")
ANGLOPARLANTE_USER_IDS = set(parse_ids("ANGLOPARLANTE_USER_IDS"))

# Compatibilidad con variable anterior
if not CHAT_IDS_AUTORIZADOS:
    old_chat_id = os.getenv("CHAT_ID_AUTORIZADO")
    if old_chat_id and old_chat_id != "0":
        try:
            # Si old_chat_id ya es JSON, no convertir
            if old_chat_id.startswith('[') and old_chat_id.endswith(']'):
                CHAT_IDS_AUTORIZADOS = json.loads(old_chat_id)
            else:
                CHAT_IDS_AUTORIZADOS = [int(old_chat_id)]
        except (ValueError, json.JSONDecodeError):
            CHAT_IDS_AUTORIZADOS = []

DB_HOST = os.getenv("MYSQLHOST")
DB_PORT = int(os.getenv("MYSQLPORT", "3306"))
DB_USER = os.getenv("MYSQLUSER")
DB_PASSWORD = os.getenv("MYSQLPASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")