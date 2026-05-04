from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent   # → backend/
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AskMyNotes", version="0.2.0")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    return AskResponse(answer=f"echo: {req.question}")

# IMPORTANT: mount static LAST so /ask and /health win route resolution.
# html=True makes "/" return index.html automatically.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
