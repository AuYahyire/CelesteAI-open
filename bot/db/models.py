from typing import Dict, List
from bot.core.logger import get_logger
import mysql.connector
from mysql.connector import pooling
from bot.core.config import APP_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from datetime import datetime
from dateutil.rrule import rrulestr

logger = get_logger(APP_NAME)

# Connection pool para reutilizar conexiones y reducir memoria
_connection_pool = None

def get_connection_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pooling.MySQLConnectionPool(
            pool_name="celeste_pool",
            pool_size=5,
            pool_reset_session=True,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True
        )
    return _connection_pool

def get_mysql_connection():
    try:
        pool = get_connection_pool()
        return pool.get_connection()
    except mysql.connector.Error as err:
        logger.error(f"Error conectando a la DB: {err}")
        raise

def init_db():
    conn = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recordatorios (
                    id INT(11) AUTO_INCREMENT PRIMARY KEY,
                    texto VARCHAR(255) NOT NULL,
                    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    rrule TEXT,
                    notificado BOOLEAN DEFAULT FALSE,
                    proximo_aviso DATETIME NOT NULL,
                    chat_id BIGINT NOT NULL DEFAULT 0,
                    usuario_id_creacion INT(11),
                    usuario_creacion VARCHAR(255),
                    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    usuario_id_modificacion INT(11),
                    usuario_modificacion VARCHAR(255),
                    fecha_modificacion DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_proximo_aviso (proximo_aviso),
                    INDEX idx_chat_id (chat_id)
                )
        """)
        
        # Agregar columna chat_id si no existe (migración compatible)
        try:
            cursor.execute("ALTER TABLE recordatorios ADD COLUMN chat_id BIGINT NOT NULL DEFAULT 0")
            cursor.execute("ALTER TABLE recordatorios ADD INDEX idx_chat_id (chat_id)")
        except mysql.connector.Error as e:
            if e.errno != 1060:  # Error 1060 = Duplicate column name
                raise
        cursor.close()
        logger.info("Tabla de recordatorios creada o ya existe.")
    except Exception as e:
        logger.error(f"Error inicializando DB: {e}")
        raise
    finally:
        if conn:
            conn.close()


#TODO Mover a una clase
def obtener_recordatorios_proximos(ahora: datetime, chat_id: int = None) -> List[Dict]:
    """
    Devuelve todos los recordatorios a notificar a esta hora (proximo_aviso <= ahora).
    Si se especifica chat_id, solo devuelve recordatorios de ese chat.
    """
    conn = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        if chat_id:
            query = """
                SELECT * FROM recordatorios
                WHERE %s >= proximo_aviso
                  AND notificado = FALSE
                  AND chat_id = %s
                ORDER BY proximo_aviso ASC
            """
            cursor.execute(query, (ahora, chat_id))
        else:
            query = """
                SELECT * FROM recordatorios
                WHERE %s >= proximo_aviso
                  AND notificado = FALSE
                ORDER BY proximo_aviso ASC
            """
            cursor.execute(query, (ahora,))
            
        recordatorios = cursor.fetchall()
        cursor.close()
        return recordatorios
    finally:
        if conn:
            conn.close()

def actualizar_recordatorio_despues_de_aviso(
    recordatorio_id: int, 
    nuevo_proximo_aviso: datetime,
    marcar_notificado: bool = False,
):
    """
    Actualiza el recordatorio después de notificarlo: pone la nueva proxima fecha
    o lo marca como notificado si ya terminó.
    """
    conn = None
    try:
        conn = get_mysql_connection()
        if marcar_notificado:
            query = "UPDATE recordatorios SET proximo_aviso=%s, notificado=TRUE WHERE id=%s"
        else:
            query = "UPDATE recordatorios SET proximo_aviso=%s WHERE id=%s"
        
        cursor = conn.cursor()
        cursor.execute(query, (nuevo_proximo_aviso, recordatorio_id))
        conn.commit()
        cursor.close()
    finally:
        if conn:
            conn.close()

def calcular_siguiente_aviso(rrule_str: str, fecha_inicio: datetime, despues_de: datetime) -> datetime:
    """
    Usa la regla RRULE y regresa la siguiente fecha de aviso después de 'despues_de'.
    Si ya no hay más repeticiones, retorna None.
    """
    regla = rrulestr(rrule_str, dtstart=fecha_inicio)
    proximo = regla.after(despues_de, inc=False)
    return proximo  # datetime o None

def init_conversations_table():
    """
    Inicializa la tabla para conversación por usuario si no existe.
    """
    conn = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                user_id BIGINT PRIMARY KEY,
                previous_response_id VARCHAR(128),
                previous_response_creation_time BIGINT
            )
        """)
        cursor.close()
    finally:
        if conn:
            conn.close()

def obtener_conversacion(user_id: int):
    """
    Consulta el previous_response_id y previous_response_creation_time para un usuario.
    Devuelve (previous_response_id:str, previous_response_creation_time:int) o (None, None)
    """
    conn = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT previous_response_id, previous_response_creation_time FROM conversations WHERE user_id = %s",
            (user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result['previous_response_id'], result['previous_response_creation_time']
        return None, None
    finally:
        if conn:
            conn.close()

def guardar_conversacion(user_id: int, previous_response_id: str, previous_response_creation_time: int):
    """
    Inserta o actualiza la conversación para un usuario.
    """
    conn = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (user_id, previous_response_id, previous_response_creation_time)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                previous_response_id = VALUES(previous_response_id),
                previous_response_creation_time = VALUES(previous_response_creation_time)
        """, (user_id, previous_response_id, previous_response_creation_time))
        conn.commit()
        cursor.close()
    finally:
        if conn:
            conn.close()

def limpiar_conversacion(user_id: int):
    """
    Borra el hilo de conversación de un usuario (usar al vencer la antigüedad).
    """
    conn = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
    finally:
        if conn:
            conn.close()