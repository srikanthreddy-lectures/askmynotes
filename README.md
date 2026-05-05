# AskMyNotes

Day 6 of 9 — question classifier (stub) + UI tag.

## Run Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/
```

## Get a Groq API key

1. Get a free API key at https://console.groq.com/keys
2. cp backend/.env.example backend/.env
3. Edit backend/.env to set GROQ_API_KEY=<their key>

## Why these chunking parameters
500 chars with 50 overlap fits about one paragraph per chunk; the overlap recovers sentences that get split across boundaries. Smaller chunks = more precise retrieval but more noise; larger = fewer chunks but mushier matches.
