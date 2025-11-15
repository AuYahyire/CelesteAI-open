from tools.funciones import consultar_fecha_hora_actual, guardar_recordatorio

class ToolDispatcher:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self._registry = {
            "guardar_recordatorio": self._guardar_recordatorio,
            "consultar_fecha_hora_actual": self._consultar_fecha_hora_actual,
        }

    def execute(self, name, args):
        if name not in self._registry:
            raise ValueError(f"Función {name} no está implementada")
        return self._registry[name](args or {})

    def _guardar_recordatorio(self, args):
        return guardar_recordatorio(
            args["texto"], args["fecha"],
            args.get("rrule"),
            self.chat_id
        )

    def _consultar_fecha_hora_actual(self, args):
        return consultar_fecha_hora_actual(args.get("pregunta"))