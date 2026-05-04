from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from . import store, pdf_utils

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

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(415, "Only application/pdf is accepted.")
    data = await file.read()
    try:
        text, pages = pdf_utils.extract_pdf_text(data)
    except ValueError as e:
        raise HTTPException(422, str(e))
    store.set_document(file.filename or "uploaded.pdf", text)
    return {
        "filename": store.get_filename(),
        "pages": pages,
        "chars": len(text),
        "preview": text[:300],
    }

# IMPORTANT: mount static LAST so /ask and /health win route resolution.
# html=True makes "/" return index.html automatically.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
