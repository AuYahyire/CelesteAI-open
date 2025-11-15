import os
import json
from openai import OpenAI
from bot.core.config import OPENAI_BASE_MODEL
from bot.core.logger import get_logger

logger = get_logger(__name__)

class OpenAIResponseService:
    def __init__(self, client=None, model=OPENAI_BASE_MODEL):
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def create_response(self, *, instructions=None, input=None, previous_response_id=None,
                        tools=None, store=True, max_output_tokens=1024,
                        temperature=0.7, parallel_tool_calls=True, truncation="auto"):
        return self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=input,
            previous_response_id=previous_response_id,
            store=store,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            tools=tools,
            parallel_tool_calls=parallel_tool_calls,
            truncation=truncation,
        )