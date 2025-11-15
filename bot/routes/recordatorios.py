import asyncio
from datetime import datetime
import pytz
from bot.core.logger import get_logger
from bot.db.models import actualizar_recordatorio_despues_de_aviso, calcular_siguiente_aviso, obtener_recordatorios_proximos
from bot.core.telegram_bot import bot_instance
from bot.core.config import APP_NAME, CHAT_IDS_AUTORIZADOS

logger = get_logger(APP_NAME)
vzla_tz = pytz.timezone("America/Caracas")

async def enviar_recordatorios_cada_minuto():
    """
    Revisa cada minuto si hay recordatorios pendientes y los envía.
    Maneja tanto recordatorios únicos como repetidos con RRULE.
    """
    while True:
        try:
            hora_venezuela = datetime.now(vzla_tz)
            #logger.info(f"Hora venezuela: {hora_venezuela}")

            # Buscar recordatorios que toca notificar ahora
            recordatorios = obtener_recordatorios_proximos(hora_venezuela)

            if recordatorios:
                # Agrupar recordatorios por chat_id
                recordatorios_por_chat = {}
                for rec in recordatorios:
                    chat_id = rec.get('chat_id', 0)
                    if chat_id == 0 and CHAT_IDS_AUTORIZADOS:
                        chat_id = CHAT_IDS_AUTORIZADOS[0]  # Fallback al primer chat
                    
                    if chat_id not in recordatorios_por_chat:
                        recordatorios_por_chat[chat_id] = []
                    recordatorios_por_chat[chat_id].append(rec)
                
                # Enviar recordatorios a cada chat
                for chat_id, recs in recordatorios_por_chat.items():
                    if chat_id in CHAT_IDS_AUTORIZADOS or chat_id == 0:
                        mensaje = ""
                        for rec in recs:
                            texto = rec['texto']
                            mensaje += f"🔔 {texto} \n"
                        
                        await bot_instance.bot.send_message(chat_id=chat_id, text=mensaje)
                        logger.info(f"Recordatorios enviados a chat {chat_id}")

                # Para cada recordatorio enviamos aviso y actualizamos próximo
                for rec in recordatorios:
                    recordatorio_id = rec['id']
                    rrule = rec['rrule']
                    fecha_inicio = rec['fecha_inicio']
                    proximo_aviso_actual = rec['proximo_aviso']
                    
                    if rrule:
                        # Calcular la siguiente fecha a partir de AHORA (o del último aviso)
                        siguiente_aviso = calcular_siguiente_aviso(rrule, fecha_inicio, proximo_aviso_actual)
                        if siguiente_aviso:
                            # Hay más repeticiones
                            actualizar_recordatorio_despues_de_aviso(
                                recordatorio_id, siguiente_aviso, marcar_notificado=False
                            )
                        else:
                            # No más repeticiones: marcar como notificado
                            actualizar_recordatorio_despues_de_aviso(
                                recordatorio_id, proximo_aviso_actual, marcar_notificado=True
                            )
                    else:
                        # No es repetido, lo marcamos como notificado
                        actualizar_recordatorio_despues_de_aviso(
                            recordatorio_id, proximo_aviso_actual, marcar_notificado=True
                        )

        except Exception as e:
            logger.error(f"Error enviando recordatorios: {e}", exc_info=True)
        
        await asyncio.sleep(60)  # Revisa cada minuto
