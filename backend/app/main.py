from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from . import store, pdf_utils, rag

BASE_DIR = Path(__file__).resolve().parent.parent   # → backend/
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AskMyNotes", version="0.2.0")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

class SearchRequest(BaseModel):
    query: str
    k: int = 3

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    if rag.store_size() == 0:
        return AskResponse(answer="Please upload a PDF first.")
    
    matches = rag.retrieve(req.question, k=3)
    if not matches:
        return AskResponse(answer="No relevant sections found in the notes.")
    
    # Format the retrieved chunks as a temporary answer until Day 5 (LLM)
    formatted_matches = "\n\n".join([
        f"[Score: {round(score, 4)}]\n{chunk}" 
        for chunk, score in matches
    ])
    return AskResponse(answer=f"Retrieved context:\n\n{formatted_matches}")

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
    n = rag.index_text(text)
    return {
        "filename": store.get_filename(),
        "pages": pages,
        "chars": len(text),
        "chunks_indexed": n,
        "preview": text[:300],
    }

@app.post("/search")
def search(req: SearchRequest):
    if rag.store_size() == 0:
        raise HTTPException(409, "No notes uploaded yet. POST /upload first.")
    matches = rag.retrieve(req.query, k=req.k)
    return {
        "matches": [
            {"chunk": chunk, "score": round(score, 4)}
            for chunk, score in matches
        ]
    }

# IMPORTANT: mount static LAST so /ask and /health win route resolution.
# html=True makes "/" return index.html automatically.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
