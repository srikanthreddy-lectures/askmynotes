"""Tool router. Two tools today: calculator and search_notes."""
from __future__ import annotations
import re
from . import rag, llm

# Allow only digits, basic operators, parens, dot, whitespace, and the ^ alias.
ARITH_ALLOWED = re.compile(r"^[\s\d\+\-\*\/\(\)\.\^]+$")

GROUNDING_PROMPT = """You are answering a question using ONLY the notes below.
If the notes do not contain enough information, say so honestly — do not invent facts.

Notes:
{context}

Question: {question}

Answer in 3-5 sentences."""

def is_arithmetic(q: str) -> bool:
    """Heuristic: question is pure arithmetic if it's only digits/ops/parens."""
    stripped = q.strip()
    if not stripped:
        return False
    return bool(ARITH_ALLOWED.match(stripped))

def calculator(q: str) -> str:
    expr = q.replace("^", "**")
    try:
        # Restricted eval — guarded by ARITH_ALLOWED above.
        value = eval(expr, {"__builtins__": {}}, {})  # noqa: S307
        return f"= {value}"
    except Exception as e:
        return f"Could not compute: {e}"

async def search_notes(question: str) -> tuple[str, list[str]]:
    """RAG path. Returns (answer, used_chunks)."""
    if rag.store_size() == 0:
        return ("No notes uploaded yet. Upload a PDF first.", [])
    top = rag.retrieve(question, k=3)
    chunks = [c for c, _ in top]
    context = "\n---\n".join(chunks)
    answer = await llm.chat(GROUNDING_PROMPT.format(context=context, question=question))
    return answer, chunks

async def route(question: str) -> tuple[str, str, list[str]]:
    """Returns (tool_used, answer, used_chunks)."""
    if is_arithmetic(question):
        return "calculator", calculator(question), []
    answer, chunks = await search_notes(question)
    return "search_notes", answer, chunks
