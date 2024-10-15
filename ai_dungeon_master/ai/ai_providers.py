from typing import List

from clientai import ClientAI
from decouple import config

openai_token = config('OPENAI_API_KEY')
replicate_token = config('REPLICATE_API_KEY')

openai_model = "gpt-4o-mini"
replicate_model = "meta/meta-llama-3-8b-instruct"
ollama_model = "llama3"

class AIProviders:
    def __init__(self):
        self.openai = ClientAI('openai', api_key=openai_token)
        self.replicate = ClientAI('replicate', api_key=replicate_token)
        self.ollama = ClientAI('ollama', host="http://localhost:11434")

    def chat(self, messages: List[dict], provider: str = 'openai'):
        if provider == 'openai':
            return self.openai.chat(messages, model=openai_model, stream=True)
        elif provider == 'replicate':
            return self.replicate.chat(messages, model=replicate_model, stream=True)
        elif provider == 'ollama':
            return self.ollama.chat(messages, model=ollama_model, stream=True)
        else:
            raise ValueError(f"Unknown provider: {provider}")
