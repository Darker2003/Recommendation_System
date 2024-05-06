from fastapi import FastAPI

from .similarity import similarity

app = FastAPI()

#uvicorn api:app --reload
#api to get suggestions
@app.get("/{question}")
async def read_item(question: str):
    result = similarity({"role": "user", "content": f"{question}"})
    return {"result": result}

