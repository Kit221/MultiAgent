import os
import json
import ollama
from dotenv import load_dotenv
from pydantic import BaseModel

# Загружаем .env файл
load_dotenv()


class LLMAgent:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

        # Создаем клиент с явным указанием хоста
        self.client = ollama.Client(host=self.base_url)

    def ask(self, system_prompt: str, user_prompt: str, response_model: BaseModel) -> dict:
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        try:
            # Используем self.client вместо глобального ollama.chat
            response = self.client.chat(
                model=self.model,
                messages=messages,
                format='json',
                options={
                    'temperature': self.temperature
                }
            )

            raw_json = response['message']['content']
            data = json.loads(raw_json)

            # Валидация схемы Pydantic
            validated_data = response_model(**data)
            return validated_data.model_dump()

        except Exception as e:
            print(f"❌ LLM Error: {e}")
            raise e