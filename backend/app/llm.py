"""Thin Groq client. OpenAI-compatible /chat/completions endpoint."""
from __future__ import annotations
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"
TIMEOUT_S = 15.0

class GroqError(RuntimeError):
    pass

async def chat(prompt: str, system: str = "You are a helpful study assistant.") -> str:
    if not GROQ_API_KEY:
        raise GroqError("GROQ_API_KEY is not set. See backend/.env.example.")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 512,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
        r = await client.post(GROQ_URL, headers=headers, json=payload)
    if r.status_code != 200:
        raise GroqError(f"Groq HTTP {r.status_code}: {r.text[:200]}")
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()
