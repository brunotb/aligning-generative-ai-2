import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent import BureaucracyAgent

load_dotenv()

app = FastAPI(title="Amt-Assistent Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
agent = BureaucracyAgent()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    state: dict

@app.get("/")
def read_root():
    return {"status": "running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await agent.process_message(request.message, request.session_id)
        # result is now a dict {"response": ..., "state": ...}
        return ChatResponse(
            response=result["response"],
            state=result["state"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reset")
def reset_session(session_id: str = "default"):
    agent.reset_session(session_id)
    return {"status": "reset"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
