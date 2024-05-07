from fastapi import FastAPI

from .DataProcessing import read_input
from .similarity import similarity

app = FastAPI()

#uvicorn api:app --reload
#api to get suggestions
@app.get("/{question}")
async def read_item(question: str):
    question = read_input(question)
    print(question)
    result = similarity({"role": "user", "content": f"{question}"})
    print(result)
    return {"result": result}

