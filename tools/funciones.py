import pytz
import html
from bot.core.config import APP_NAME
from bot.core.logger import get_logger
from bot.db.models import get_mysql_connection
from datetime import datetime

logger = get_logger(APP_NAME)

def parse_fecha(fecha_str: str) -> str:
    """
    Parsea una fecha ISO 8601 a formato MySQL DATETIME (%Y-%m-%d %H:%M:%S)
    """
    logger.debug(f"Parseando fecha: {fecha_str}")
    try:
        dt = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
        parsed = dt.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"Fecha parseada exitosamente: {parsed}")
        return parsed
    except ValueError:
        logger.error(f"Fecha inválida: {fecha_str}")
        raise ValueError("Formato de fecha inválido. Debe ser ISO 8601 como 'YYYY-MM-DDTHH:MM:SS'")

def guardar_recordatorio(texto: str, fecha: str, rrule: str = None, chat_id: int = 0) -> str:
    """
    Guarda un recordatorio simple o repetido en la base de datos.
    Si 'rrule' es None será un único recordatorio. Sino, será repetitivo.
    """
    # Sanitizar entrada para prevenir XSS
    texto = html.escape(texto.strip()) if texto else ""
    if not texto:
        return "⚠️ El texto del recordatorio no puede estar vacío"
    
    logger.info(f"Guardando recordatorio: texto='{texto}', fecha='{fecha}', rrule='{rrule}', chat_id={chat_id}")
    conn = None
    try:
        fecha_mysql = parse_fecha(fecha)
        logger.debug("Conectando a base de datos...")
        conn = get_mysql_connection()
        cursor = conn.cursor()

        if rrule:
            logger.debug("Insertando recordatorio repetitivo")
            sql = """
                INSERT INTO recordatorios
                (texto, fecha_inicio, rrule, proximo_aviso, chat_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (texto, fecha_mysql, rrule, fecha_mysql, chat_id))
        else:
            logger.debug("Insertando recordatorio único")
            # Único
            sql = """
                INSERT INTO recordatorios
                (texto, fecha_inicio, proximo_aviso, chat_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (texto, fecha_mysql, fecha_mysql, chat_id))

        conn.commit()
        cursor.close()
        logger.info(f"Recordatorio guardado exitosamente para fecha {fecha_mysql}")
        return f"✅ Recordatorio guardado: '{texto}' para el {fecha_mysql}{' (repetido)' if rrule else ''}"

    except Exception as e:
        logger.error(f"Error guardando recordatorio: {e}")
        return "⚠️ Error guardando el recordatorio"

    finally:
        if conn:
            logger.debug("Cerrando conexión a base de datos")
            conn.close()

def consultar_fecha_hora_actual(pregunta: str = None):
    logger.debug(f"Consultando fecha/hora actual en zona horaria de Venezuela, pregunta: {pregunta!r}")    
    vzla_tz = pytz.timezone("America/Caracas")
    current_time = datetime.now(vzla_tz)
    logger.debug(f"Fecha/hora actual: {current_time}")
    return current_time
