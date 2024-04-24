

import openai

from chroma_db.chroma_db import ChromaDb


class OpenAIBackend:
    def __init__(self, host: str, port: int, endpoint: str = 'v1', api_key: str = None, system_prompt: str = None):
        self.api_key = api_key
        self.base_url = f"http://{host}:{port}/{endpoint}"

        self.system_prompt = system_prompt
        
        self.client = openai.OpenAI(
            base_url="http://localhost:8080/v1", # "http://<Your api-server IP>:port"
            api_key = "sk-no-key-required"
        )

        


    def query(self, prompt: str):

        rag_data = self.rag.inference(prompt, {}, 0)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            stop="\n\n\n",
            messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": rag_data}
            ]
        )

        return response.choices[0].message.content