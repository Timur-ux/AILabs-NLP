import fastapi
import ollama
import os
from pydantic import BaseModel

url = os.getenv("OLLAMA_URL")
if url is None:
    url = "http://localhost:11434"

ollamaClient = ollama.AsyncClient(host=url)

app = fastapi.FastAPI(docs_url="/docs")

class Data(BaseModel):
    message: str

@app.post("/AskOllama")
async def AskOllama(data: Data):
    result = await ollamaClient.chat(model="qwen2.5:0.5b", messages=[{"role": "user", "content": data.message}])
    return result["message"]["content"]

