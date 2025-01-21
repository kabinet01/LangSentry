from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LangSentry", description="A FastAPI-based security module for LLMs.")

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    result: str
    score: float

@app.get("/")
def read_root():
    return {"message": "Welcome to LangSentry API!"}

@app.post("/analyze", response_model=PromptResponse)
def analyze(prompt_request: PromptRequest):
    prompt = prompt_request.prompt
    try:
        result, score = 1,1
        return {"result": result, "score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)