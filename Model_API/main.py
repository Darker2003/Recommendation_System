import os

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Model.model_predict import predictor

router = APIRouter(prefix="/model", tags=["Model"])

@router.get("/get_question_tags/{question}")
async def get_question_tags(question: str):
    # Get the prediction
    original_sentence, predicted_tags = predictor.predict(question)

    # Print the sentence and its predicted tags
    print("Sentence:", original_sentence)
    print("Predicted Tags:", predicted_tags)
    return {"question_tags": predicted_tags}

app = FastAPI(docs_url="/")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*',]
)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, port=os.environ.get("PORT", 7860))
