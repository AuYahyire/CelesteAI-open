# bot/services/responder.py
import json
from bot.core.logger import get_logger
from bot.core.config import APP_NAME
from bot.services.OpenAI.conversation import ConversationStateManager
from bot.services.OpenAI.openai import OpenAIResponseService
from bot.services.OpenAI.tools.registry import ToolDispatcher
from bot.services.OpenAI.utils import load_resource, build_input_block

logger = get_logger(APP_NAME)

class ResponderService:
    def __init__(self, conversation_manager=None, openai_service=None):
        self.conversation_manager = conversation_manager or ConversationStateManager()
        self.openai_service = openai_service or OpenAIResponseService()
        self.tools = load_resource("tools.json")
        self.instructions = None

    def responder(self, contexto_texto, imagenes, user_id, chat_id=0, instructions=None, temperature=0.7):
        logger.info(f"[responder user_id={user_id}, chat_id={chat_id}] {contexto_texto}")
        if instructions:
            self.instructions = load_resource(instructions)
        else:
            self.instructions = load_resource("instrucciones.txt")
        previous_response_id, _ = self.conversation_manager.get_state(user_id)
        input_blocks = build_input_block(contexto_texto, imagenes)

        try:
            response = self.openai_service.create_response(
                instructions=self.instructions,
                input=input_blocks,
                previous_response_id=previous_response_id,
                tools=self.tools,
                temperature=temperature
            )

            self.conversation_manager.save_state(user_id, response.id, response.created_at)

            for output in response.output:
                if output.type == "function_call" and output.status == "completed":
                    return self._handle_function_call(output, input_blocks, user_id, chat_id)

                if output.type == "message":
                    for item in output.content:
                        if item.type == "output_text":
                            return item.text

        except Exception as exc:
            logger.exception("[responder] Error procesando respuesta", exc_info=exc)
            return "⚠️ Ha habido un error, contacte con el administrador del bot."

        return "⚠️ No pude generar respuesta."

    def _handle_function_call(self, tool_call, input_blocks, user_id, chat_id):
        args = json.loads(tool_call.arguments) if tool_call.arguments else {}
        dispatcher = ToolDispatcher(chat_id)

        result = dispatcher.execute(tool_call.name, args)

        input_blocks = input_blocks + [
            {"type": "function_call",
             "call_id": tool_call.call_id,
             "name": tool_call.name,
             "arguments": tool_call.arguments},
            {"type": "function_call_output",
             "call_id": tool_call.call_id,
             "output": str(result)},
        ]

        previous_response_id, _ = self.conversation_manager.get_state(user_id)
        response = self.openai_service.create_response(
            input=input_blocks,
            previous_response_id=previous_response_id,
            tools=self.tools,
            temperature=0.7
        )

        self.conversation_manager.save_state(user_id, response.id, response.created_at)
        logger.info(f"[_handle_function_call] Nueva respuesta tras llamada {tool_call.name}, respuesta: {response.output}")
        for output in response.output:
            if output.type == "function_call" and getattr(output, "status", None) == "completed":
                return self._handle_function_call(output, input_blocks, user_id, chat_id)

            if output.type == "message":
                for item in output.content:
                    if item.type == "output_text":
                        return item.text

        return "⚠️ No pude generar respuesta tras ejecutar la herramienta."