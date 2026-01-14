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

@app.get("/")
@app.get("/api")
def read_root():
    return {"status": "running"}

@app.post("/chat", response_model=ChatResponse)
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Lazy load agent if not already done
        if agent is None:
             raise HTTPException(status_code=500, detail="Agent failed to initialize. Check logs.")
             
        response_text = await agent.process_message(request.message, request.session_id)
        return ChatResponse(response=response_text)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"CRITICAL ERROR: {error_details}")
        # Return the actual error to the client for debugging
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/reset")
@app.get("/api/reset")
def reset_session(session_id: str = "default"):
    agent.reset_session(session_id)
    return {"status": "reset"}

if __name__ == "__main__":
    uvicorn.run("index:app", host="0.0.0.0", port=8001, reload=True)
