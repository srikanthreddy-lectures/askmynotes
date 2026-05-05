from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from . import store, pdf_utils, rag, llm, classifier

BASE_DIR = Path(__file__).resolve().parent.parent   # → backend/
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AskMyNotes", version="0.2.0")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    used_chunks: list[str]
    question_type: str

class SearchRequest(BaseModel):
    query: str
    k: int = 3

GROUNDING_PROMPT = """You are a professional academic summarizer. Your goal is to synthesize the provided notes into a cohesive, natural language response.

STRICT RULES:
1. DO NOT repeat the same phrases or list items verbatim.
2. DO NOT echo the notes as a list. 
3. DO NOT provide a fragmented response.
4. Synthesize the information into 3-5 full, grammatically correct sentences.
5. If the notes contain a list or syllabus, describe the overall objective of the course/document rather than listing the modules.
6. If the notes do not contain enough information to answer the question, say "I cannot find the answer in the provided notes."
7. Avoid all introductory filler (e.g., "The notes mention..."). Start directly with the answer.

Notes:
{context}

Question: {question}

Final Answer:"""

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if rag.store_size() == 0:
        raise HTTPException(409, "No notes uploaded yet. POST /upload first.")
    
    qtype = classifier.classify(req.question)
    top = rag.retrieve(req.question, k=3)
    chunks = [c for c, _ in top]
    context = "\n---\n".join(chunks)
    try:
        answer = await llm.chat(
            GROUNDING_PROMPT.format(context=context, question=req.question)
        )
    except llm.GroqError as e:
        raise HTTPException(502, f"LLM call failed: {e}")
    return AskResponse(answer=answer, used_chunks=chunks, question_type=qtype)

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
