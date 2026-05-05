# AskMyNotes

Day 4 of 9 — chunking + embeddings + retrieval.

## Run Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/
```

## Why these chunking parameters
500 chars with 50 overlap fits about one paragraph per chunk; the overlap recovers sentences that get split across boundaries. Smaller chunks = more precise retrieval but more noise; larger = fewer chunks but mushier matches.
